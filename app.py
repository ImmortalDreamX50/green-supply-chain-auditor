"""
Green Supply Chain Auditor — Agent Definitions
AMD Hackathon 2026

Distance calculation uses OpenStreetMap Nominatim (free, no API key needed).
Works for any city/port in the world automatically.
"""

import os
import time
import requests
from math import radians, sin, cos, sqrt, atan2
from functools import lru_cache
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

# ─────────────────────────────────────────────
# LLM — Llama-3-70B on AMD Developer Cloud
# ─────────────────────────────────────────────
llm = ChatOpenAI(
    model="meta/llama-3-70b-instruct",
    base_url=os.getenv("AMD_API_BASE_URL"),
    api_key=os.getenv("AMD_API_KEY"),
    temperature=0.2,
    max_tokens=2048,
)

# ─────────────────────────────────────────────
# Emission Factors (kg CO₂ per tonne-km)
# Source: International Transport Forum
# ─────────────────────────────────────────────
EMISSION_FACTORS = {
    "air":   0.800,
    "sea":   0.015,
    "road":  0.100,
    "rail":  0.028,
}

# ─────────────────────────────────────────────
# Geocoding + Distance (Nominatim — no key needed)
# ─────────────────────────────────────────────

@lru_cache(maxsize=256)
def geocode_city(city: str) -> tuple[float, float] | None:
    """
    Convert a city name to (lat, lon) using OpenStreetMap Nominatim.
    Results are cached so repeated calls for the same city are instant.
    """
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "GreenChainAuditor/1.0 (hackathon-project)"},
            timeout=5,
        )
        data = response.json()
        if data:
            return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass
    return None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """Great-circle distance between two lat/lon points in km."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return round(R * 2 * atan2(sqrt(a), sqrt(1 - a)))


# ─────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────

@tool("estimate_distance_km")
def estimate_distance_km(origin_destination: str) -> str:
    """
    Calculates the great-circle distance between any two cities in km.
    Uses OpenStreetMap Nominatim for geocoding — works for any city in the world.
    Input: 'City A -> City B'
    Returns: distance in km as a string, or '5000' as a safe fallback.
    """
    parts = [p.strip() for p in origin_destination.split("->")]
    if len(parts) != 2:
        return "5000"

    origin, destination = parts

    # Respect Nominatim's usage policy — 1 request/second max
    origin_coords = geocode_city(origin)
    time.sleep(1)
    dest_coords = geocode_city(destination)

    if not origin_coords or not dest_coords:
        print(f"[distance] Could not geocode: {origin} or {destination}. Using fallback 5000km.")
        return "5000"

    km = haversine_km(*origin_coords, *dest_coords)
    print(f"[distance] {origin} → {destination}: {km} km")
    return str(km)


@tool("calculate_emissions")
def calculate_emissions(shipment_json: str) -> str:
    """
    Calculates CO₂ emissions for a list of shipments.
    Input: JSON string of shipments with fields:
      origin, destination, weight_tons, transport_mode, distance_km
    Returns: JSON string with co2_kg per shipment, total_co2_kg, and hotspot.
    """
    shipments = json.loads(shipment_json)
    results = []
    total_co2 = 0.0

    for s in shipments:
        mode     = s.get("transport_mode", "sea").lower().strip()
        factor   = EMISSION_FACTORS.get(mode, EMISSION_FACTORS["sea"])
        weight   = float(s.get("weight_tons", 1))
        distance = float(s.get("distance_km", 1000))

        co2_kg = round(weight * distance * factor, 2)
        total_co2 += co2_kg
        results.append({**s, "co2_kg": co2_kg, "factor_used": factor})

    hotspot = max(results, key=lambda x: x["co2_kg"])

    return json.dumps({
        "shipments":    results,
        "total_co2_kg": round(total_co2, 2),
        "hotspot":      hotspot,
    }, indent=2)


@tool("lookup_green_suppliers")
def lookup_green_suppliers(query: str) -> str:
    """
    Semantic search over ChromaDB for eco-friendly supplier alternatives.
    Input: description of the route or product category needing a greener option.
    Returns: top 3 matching suppliers as a JSON string.
    """
    from supplier_db import query_suppliers
    results = query_suppliers(query, n_results=3)
    return json.dumps(results, indent=2)


# ─────────────────────────────────────────────
# Agent 1 — Data Extractor (The Librarian)
# ─────────────────────────────────────────────
data_extractor = Agent(
    role="Supply Chain Data Extractor",
    goal=(
        "Parse raw shipping documents (CSV rows, invoice text, manifests) and "
        "extract structured shipment records: origin, destination, weight_tons, "
        "transport_mode, and distance_km for every shipment. "
        "Use the estimate_distance_km tool to get the real distance for every route."
    ),
    backstory=(
        "You are a meticulous logistics data analyst. You have processed thousands "
        "of shipping invoices and know exactly how to spot weights, routes, and "
        "freight modes buried in messy spreadsheets or free-text documents. "
        "You always output clean, valid JSON arrays. You never guess distances — "
        "you always use the estimate_distance_km tool to get accurate figures."
    ),
    tools=[estimate_distance_km],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# ─────────────────────────────────────────────
# Agent 2 — Carbon Calculator (The Engineer)
# ─────────────────────────────────────────────
carbon_calculator = Agent(
    role="Carbon Emissions Engineer",
    goal=(
        "Take structured shipment data and calculate the exact CO₂ emissions "
        "for each route using the calculate_emissions tool. "
        "Identify and clearly flag the single biggest carbon hotspot."
    ),
    backstory=(
        "You are an environmental engineer with deep expertise in lifecycle "
        "carbon accounting for global supply chains. You apply IPCC-aligned "
        "emission factors and always surface the single highest-impact route "
        "as the 'carbon hotspot' for the business to prioritise."
    ),
    tools=[calculate_emissions],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# ─────────────────────────────────────────────
# Agent 3 — Sourcing Strategist (The Consultant)
# ─────────────────────────────────────────────
sourcing_strategist = Agent(
    role="Green Sourcing Strategist",
    goal=(
        "Using the carbon hotspot data, recommend concrete alternatives: "
        "switch Air freight to Sea, find local/regional green suppliers, "
        "and produce a prioritised Sustainability Roadmap with estimated CO₂ savings."
    ),
    backstory=(
        "You are a sustainability consultant who has helped Fortune 500 companies "
        "cut supply chain emissions by 40%. You combine knowledge of global "
        "logistics networks with a database of verified eco-friendly suppliers "
        "to produce actionable, ROI-driven recommendations."
    ),
    tools=[lookup_green_suppliers],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# ─────────────────────────────────────────────
# Tasks
# ─────────────────────────────────────────────

def build_tasks(raw_data: str):
    extract_task = Task(
        description=(
            f"Here is the raw supply chain data provided by the user:\n\n"
            f"{raw_data}\n\n"
            "Extract every shipment into a JSON array. Each element must have: "
            "origin (str), destination (str), weight_tons (float), "
            "transport_mode (str: air/sea/road/rail), distance_km (float). "
            "For EVERY shipment, call the estimate_distance_km tool with format "
            "'Origin -> Destination' to get the real distance. "
            "Return ONLY the JSON array, no extra text."
        ),
        expected_output=(
            "A valid JSON array of shipment objects, each with: "
            "origin, destination, weight_tons, transport_mode, distance_km. "
            "distance_km must come from the estimate_distance_km tool, not guessed."
        ),
        agent=data_extractor,
    )

    calc_task = Task(
        description=(
            "Take the JSON array from the previous task and pass it directly to "
            "the calculate_emissions tool. Return the full JSON result exactly as "
            "the tool returns it — do not modify or summarise."
        ),
        expected_output=(
            "A JSON object with: shipments (array with co2_kg per row), "
            "total_co2_kg (float), and hotspot (the single highest-emission shipment)."
        ),
        agent=carbon_calculator,
        context=[extract_task],
    )

    strategy_task = Task(
        description=(
            "Using the emissions data and hotspot from the previous task, produce a "
            "Sustainability Roadmap. For the top 3 highest-emission routes:\n"
            "1. Recommend switching transport mode where beneficial (e.g. Air → Sea)\n"
            "2. Use lookup_green_suppliers to find a specific eco-friendly supplier for each\n"
            "3. Estimate the CO₂ reduction percentage for each recommendation\n\n"
            "Format the final output as markdown with:\n"
            "- Executive Summary (2-3 sentences)\n"
            "- Top 3 Recommendations (ranked by CO₂ savings, with supplier names)\n"
            "- Summary table of estimated CO₂ reductions\n"
        ),
        expected_output=(
            "A markdown Sustainability Roadmap with executive summary, "
            "top 3 ranked recommendations each with a named green supplier, "
            "and a CO₂ reduction summary table."
        ),
        agent=sourcing_strategist,
        context=[calc_task],
    )

    return [extract_task, calc_task, strategy_task]


# ─────────────────────────────────────────────
# Crew runner — called by Streamlit
# ─────────────────────────────────────────────

def run_audit(raw_data: str) -> dict:
    """
    Run the full 3-agent audit pipeline.
    Returns dict with keys: extraction, emissions, report
    """
    tasks = build_tasks(raw_data)

    crew = Crew(
        agents=[data_extractor, carbon_calculator, sourcing_strategist],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "extraction": tasks[0].output.raw if tasks[0].output else "",
        "emissions":  tasks[1].output.raw if tasks[1].output else "",
        "report":     tasks[2].output.raw if tasks[2].output else str(result),
    }


if __name__ == "__main__":
    # Smoke test — uses live Nominatim geocoding
    sample = """
    origin,destination,weight_tons,transport_mode
    Shanghai,Karachi,5,Air
    Mumbai,London,12,Sea
    Frankfurt,Paris,3,Road
    """
    output = run_audit(sample)
    print("\n===== FINAL REPORT =====\n")
    print(output["report"])
