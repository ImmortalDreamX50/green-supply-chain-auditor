"""
Green Supply Chain Auditor — Agent Definitions
AMD Hackathon 2025
"""

import os
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
    model="meta/llama-3-70b-instruct",          # AMD Developer Cloud model name
    base_url=os.getenv("AMD_API_BASE_URL"),      # e.g. https://api.amd.com/v1
    api_key=os.getenv("AMD_API_KEY"),
    temperature=0.2,
    max_tokens=2048,
)

# ─────────────────────────────────────────────
# Emission Factors (kg CO₂ per tonne-km)
# Source: International Transport Forum
# ─────────────────────────────────────────────
EMISSION_FACTORS = {
    "air":   0.800,   # Air freight
    "sea":   0.015,   # Ocean shipping
    "road":  0.100,   # Truck / road freight
    "rail":  0.028,   # Rail freight
}

# ─────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────

@tool("calculate_emissions")
def calculate_emissions(shipment_json: str) -> str:
    """
    Calculates CO₂ emissions for a list of shipments.
    Input: JSON string of shipments with fields:
      origin, destination, weight_tons, transport_mode, distance_km
    Returns: JSON string with emissions added per shipment + total + hotspot.
    """
    shipments = json.loads(shipment_json)
    results = []
    total_co2 = 0.0

    for s in shipments:
        mode = s.get("transport_mode", "sea").lower().strip()
        factor = EMISSION_FACTORS.get(mode, EMISSION_FACTORS["sea"])
        weight = float(s.get("weight_tons", 1))
        distance = float(s.get("distance_km", 1000))   # default fallback

        co2_kg = weight * distance * factor
        total_co2 += co2_kg
        results.append({**s, "co2_kg": round(co2_kg, 2), "factor_used": factor})

    # Identify hotspot
    hotspot = max(results, key=lambda x: x["co2_kg"])

    return json.dumps({
        "shipments": results,
        "total_co2_kg": round(total_co2, 2),
        "hotspot": hotspot,
    }, indent=2)


@tool("lookup_green_suppliers")
def lookup_green_suppliers(query: str) -> str:
    """
    Queries ChromaDB vector store for eco-friendly supplier alternatives.
    Input: a description of the shipment route or product category.
    Returns: list of green supplier suggestions as a JSON string.
    """
    from supplier_db import query_suppliers
    results = query_suppliers(query, n_results=3)
    return json.dumps(results, indent=2)


@tool("estimate_distance_km")
def estimate_distance_km(origin_destination: str) -> str:
    """
    Estimates shipping distance between two cities/ports in km.
    Input: 'Origin -> Destination' as a string.
    Returns: estimated distance in km as a string.
    """
    # Approximate great-circle distances for common routes (hackathon hardcodes)
    # In production, call a routing API
    DISTANCES = {
        ("shanghai", "karachi"):   4800,
        ("mumbai",   "london"):   11000,
        ("frankfurt","paris"):      480,
        ("los angeles","tokyo"):   8800,
        ("new york",  "london"):   5500,
        ("shenzhen",  "rotterdam"):21000,
    }
    parts = [p.strip().lower() for p in origin_destination.split("->")]
    if len(parts) == 2:
        key = tuple(parts)
        dist = DISTANCES.get(key) or DISTANCES.get((parts[1], parts[0])) or 5000
        return str(dist)
    return "5000"  # fallback default


# ─────────────────────────────────────────────
# Agent 1 — Data Extractor (The Librarian)
# ─────────────────────────────────────────────
data_extractor = Agent(
    role="Supply Chain Data Extractor",
    goal=(
        "Parse raw shipping documents (CSV rows, invoice text, manifests) and "
        "extract structured shipment records: origin, destination, weight_tons, "
        "transport_mode, and estimated distance_km for every shipment."
    ),
    backstory=(
        "You are a meticulous logistics data analyst. You have processed thousands "
        "of shipping invoices and know exactly how to spot weights, routes, and "
        "freight modes buried in messy spreadsheets or free-text documents. "
        "You always output clean, valid JSON arrays."
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
        "for each route. Identify the single biggest carbon hotspot in the supply chain."
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
            "Use the estimate_distance_km tool for any missing distances. "
            "Return ONLY the JSON array, no extra text."
        ),
        expected_output=(
            "A valid JSON array of shipment objects with fields: "
            "origin, destination, weight_tons, transport_mode, distance_km."
        ),
        agent=data_extractor,
    )

    calc_task = Task(
        description=(
            "Take the JSON array from the previous task and calculate CO₂ emissions "
            "for each shipment using the calculate_emissions tool. "
            "Return the full JSON result including the hotspot."
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
            "Using the hotspot identified by the Carbon Calculator, produce a "
            "Sustainability Roadmap. For each high-emission route:\n"
            "1. Check if switching transport mode (e.g. Air→Sea) would help\n"
            "2. Use lookup_green_suppliers to find alternative eco-friendly suppliers\n"
            "3. Estimate percentage CO₂ reduction for each recommendation\n\n"
            "Format the final output as a clear markdown report with:\n"
            "- Executive Summary (2-3 sentences)\n"
            "- Top 3 Recommendations (ranked by CO₂ savings potential)\n"
            "- Estimated Total Reduction if all recommendations are adopted\n"
        ),
        expected_output=(
            "A markdown-formatted Sustainability Roadmap with executive summary, "
            "top 3 ranked recommendations, and total reduction estimate."
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
    # Quick smoke test with sample data
    sample = """
    origin,destination,weight_tons,transport_mode
    Shanghai,Karachi,5,Air
    Mumbai,London,12,Sea
    Frankfurt,Paris,3,Road
    Los Angeles,Tokyo,8,Air
    """
    output = run_audit(sample)
    print("\n===== FINAL REPORT =====\n")
    print(output["report"])
