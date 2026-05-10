"""
Green Supply Chain Auditor — Agent Definitions
AMD Hackathon 2026
"""

import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

load_dotenv()

# ─────────────────────────────────────────────
# LLM — AMD first, OpenAI fallback
# ─────────────────────────────────────────────
AMD_API_KEY  = os.getenv("AMD_API_KEY")
AMD_API_BASE = os.getenv("AMD_API_BASE_URL")
OPENAI_KEY   = os.getenv("OPENAI_API_KEY")

if AMD_API_KEY and AMD_API_BASE:
    llm = ChatOpenAI(
        model="meta/llama-3-70b-instruct",
        base_url=AMD_API_BASE,
        api_key=AMD_API_KEY,
        temperature=0.2,
        max_tokens=2048,
    )
else:
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",                        # Fast and available on all OpenAI accounts
        api_key=OPENAI_KEY,
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


def lookup_green_suppliers(query: str) -> str:
    """
    Queries supplier database for eco-friendly supplier alternatives.
    Input: a description of the shipment route or product category.
    Returns: list of green supplier suggestions as a JSON string.
    """
    from supplier_db import query_suppliers
    results = query_suppliers(query, n_results=3)
    return json.dumps(results, indent=2)


def estimate_distance_km(origin_destination: str) -> str:
    """
    Estimates shipping distance between two cities/ports in km.
    Input: 'Origin -> Destination' as a string.
    Returns: estimated distance in km as a string.
    """
    # Approximate great-circle distances for common routes
    # In production, call a routing API like Google Distance Matrix
    DISTANCES = {
        # Asia to Middle East
        ("shanghai", "karachi"):    4800,
        ("shanghai", "dubai"):      5900,
        ("shenzhen", "karachi"):    4700,
        # Asia to Europe
        ("mumbai",   "london"):    11000,
        ("mumbai",   "rotterdam"): 10800,
        ("shanghai", "rotterdam"): 19500,
        ("shenzhen", "rotterdam"): 21000,
        ("shanghai", "hamburg"):   19200,
        ("chennai",  "london"):    11200,
        # Intra-Europe
        ("frankfurt","paris"):       480,
        ("amsterdam","madrid"):     1450,
        ("berlin",   "warsaw"):      520,
        ("hamburg",  "dubai"):      5200,
        # Trans-Pacific
        ("los angeles","tokyo"):    8800,
        ("los angeles","shanghai"):11000,
        ("seattle",  "tokyo"):      7700,
        ("seattle",  "lahore"):    11200,
        # Trans-Atlantic
        ("new york",  "london"):    5500,
        ("new york",  "paris"):     5800,
        # Americas
        ("sao paulo", "new york"):  7700,
        ("sao paulo", "new jersey"):7700,
    }
    parts = [p.strip().lower() for p in origin_destination.split("->")]
    if len(parts) == 2:
        key = tuple(parts)
        # Try forward and reverse lookup
        dist = DISTANCES.get(key) or DISTANCES.get((parts[1], parts[0]))
        if dist:
            return str(dist)
        return "7500"  # average long-distance route fallback
    return "5000"  # fallback default


# ─────────────────────────────────────────────
# Agent 1 — Data Extractor (The Librarian)
# ─────────────────────────────────────────────

def agent_extract(raw_data: str) -> list:
    """
    Parse raw shipping documents and extract structured shipment records.
    Uses LLM to handle messy CSVs, invoices, or free-text manifests.
    """
    response = llm.invoke([
        SystemMessage(content=(
            "You are a meticulous logistics data analyst. You have processed thousands "
            "of shipping invoices and know exactly how to spot weights, routes, and "
            "freight modes buried in messy spreadsheets or free-text documents. "
            "Extract every shipment into a JSON array. Each element must have: "
            "origin (str), destination (str), weight_tons (float), "
            "transport_mode (str: air/sea/road/rail), distance_km (float). "
            "Use common sense for missing distances. "
            "Return ONLY the JSON array, no extra text, no markdown fences."
        )),
        HumanMessage(content=(
            f"Here is the raw supply chain data provided by the user:\n\n"
            f"{raw_data}\n\n"
            "Extract every shipment into a JSON array with fields: "
            "origin, destination, weight_tons, transport_mode, distance_km. "
            "Return ONLY the JSON array."
        ))
    ])

    text = response.content.strip()
    # Strip markdown code fences if present
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    shipments = json.loads(text)

    # Fill in distances using our lookup tool for any missing ones
    for s in shipments:
        if not s.get("distance_km"):
            dist_str = estimate_distance_km(f"{s.get('origin','')} -> {s.get('destination','')}")
            s["distance_km"] = float(dist_str)

    return shipments


# ─────────────────────────────────────────────
# Agent 2 — Carbon Calculator (The Engineer)
# ─────────────────────────────────────────────

def agent_calculate(shipments: list) -> dict:
    """
    Take structured shipment data and calculate the exact CO₂ emissions
    for each route. Identifies the single biggest carbon hotspot.
    """
    emissions_json = calculate_emissions(json.dumps(shipments))
    return json.loads(emissions_json)


# ─────────────────────────────────────────────
# Agent 3 — Sourcing Strategist (The Consultant)
# ─────────────────────────────────────────────

def agent_strategise(emissions_data: dict) -> str:
    """
    Using the carbon hotspot data, recommend concrete alternatives:
    switch Air freight to Sea, find local/regional green suppliers,
    and produce a prioritised Sustainability Roadmap with estimated CO₂ savings.
    """
    hotspot   = emissions_data.get("hotspot", {})
    total_co2 = emissions_data.get("total_co2_kg", 0)
    shipments = emissions_data.get("shipments", [])

    # Look up green suppliers for top 3 highest-emission routes
    top3 = sorted(shipments, key=lambda x: -x.get("co2_kg", 0))[:3]
    supplier_context = ""
    for route in top3:
        query = (
            f"{route.get('transport_mode','')} freight "
            f"{route.get('origin','')} to {route.get('destination','')} "
            "green alternative"
        )
        supplier_context += f"\n{route.get('origin','')} → {route.get('destination','')}: "
        supplier_context += lookup_green_suppliers(query)

    response = llm.invoke([
        SystemMessage(content=(
            "You are a sustainability consultant who has helped Fortune 500 companies "
            "cut supply chain emissions by 40%. You combine knowledge of global "
            "logistics networks with a database of verified eco-friendly suppliers "
            "to produce actionable, ROI-driven recommendations. "
            "Format your response as a clear markdown report."
        )),
        HumanMessage(content=(
            f"Using the hotspot identified below, produce a Sustainability Roadmap.\n\n"
            f"Total CO₂: {total_co2:,.0f} kg\n"
            f"Carbon Hotspot: {hotspot.get('origin','?')} → {hotspot.get('destination','?')} "
            f"({hotspot.get('transport_mode','?')}, {hotspot.get('co2_kg',0):,.0f} kg CO₂)\n\n"
            f"All shipments:\n{json.dumps(shipments, indent=2)}\n\n"
            f"Available green suppliers per route:\n{supplier_context}\n\n"
            "Format the final output as a clear markdown report with:\n"
            "- Executive Summary (2-3 sentences)\n"
            "- Top 3 Recommendations (ranked by CO₂ savings potential)\n"
            "- Estimated Total Reduction if all recommendations are adopted\n"
        ))
    ])

    return response.content


# ─────────────────────────────────────────────
# Crew runner — called by Streamlit
# ─────────────────────────────────────────────

def run_audit(raw_data: str) -> dict:
    """
    Run the full 3-agent audit pipeline.
    Returns dict with keys: extraction, emissions, report
    """
    try:
        # Agent 1 — Extract shipments
        shipments = agent_extract(raw_data)
        extraction_str = json.dumps(shipments, indent=2)

        # Agent 2 — Calculate emissions + find hotspot
        emissions_data = agent_calculate(shipments)
        emissions_str  = json.dumps(emissions_data, indent=2)

        # Agent 3 — Generate sustainability roadmap
        report = agent_strategise(emissions_data)

        return {
            "extraction": extraction_str,
            "emissions":  emissions_str,
            "report":     report,
        }

    except Exception as e:
        # Return error in a format the UI can handle
        error_msg = f"Error during audit: {str(e)}"
        return {
            "extraction": f"[Error] {error_msg}",
            "emissions":  '{"shipments": [], "total_co2_kg": 0, "hotspot": {}}',
            "report":     f"# Error\n\n{error_msg}\n\nPlease check your API credentials and try again.",
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
