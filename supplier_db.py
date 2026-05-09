"""
supplier_db.py — ChromaDB Vector Store for Eco-Friendly Suppliers
AMD Hackathon 2026

Run this file once to seed the database:
    python supplier_db.py

Then import query_suppliers() in agents.py.
"""

import chromadb
from chromadb.utils import embedding_functions
import os

DB_PATH = "./chroma_db"
COLLECTION_NAME = "green_suppliers"

# ─────────────────────────────────────────────
# Seed Data — Eco-Friendly Supplier Profiles
# ─────────────────────────────────────────────
SUPPLIERS = [
    {
        "id": "sup_001",
        "name": "OceanPath Logistics",
        "description": (
            "Sea freight specialist operating carbon-neutral vessels on Asia-Europe "
            "routes. Certified by the Clean Shipping Index. Average 94% lower "
            "emissions than equivalent air freight. Routes: Shanghai, Shenzhen, "
            "Mumbai, Rotterdam, Karachi, London."
        ),
        "region": "Asia-Europe",
        "transport_mode": "sea",
        "co2_rating": "A+",
        "certifications": "Clean Shipping Index, ISO 14001",
    },
    {
        "id": "sup_002",
        "name": "GreenRail Europa",
        "description": (
            "Electric rail freight across the EU and UK. Runs on 100% renewable "
            "energy. 75% lower emissions than road freight for intra-European routes. "
            "Key corridors: Frankfurt-Paris, Amsterdam-Madrid, Berlin-Warsaw."
        ),
        "region": "Europe",
        "transport_mode": "rail",
        "co2_rating": "A+",
        "certifications": "EU EcoLabel, CDP A-List",
    },
    {
        "id": "sup_003",
        "name": "SolarHaul Trucking",
        "description": (
            "Electric truck fleet powered by on-site solar charging hubs. "
            "Zero-emission last-mile and mid-range road freight in Western Europe "
            "and North America. Refrigerated options available."
        ),
        "region": "Europe, North America",
        "transport_mode": "road",
        "co2_rating": "A",
        "certifications": "SmartWay, Science Based Targets",
    },
    {
        "id": "sup_004",
        "name": "PacificGreen Shipping",
        "description": (
            "Slow-steaming LNG-powered container ships on Trans-Pacific routes. "
            "Los Angeles, Long Beach, Tokyo, Yokohama, Shanghai. "
            "40% lower emissions than conventional sea freight."
        ),
        "region": "Asia-Pacific, North America",
        "transport_mode": "sea",
        "co2_rating": "A",
        "certifications": "IMO Tier III, ISO 14001",
    },
    {
        "id": "sup_005",
        "name": "Karachi Green Port Logistics",
        "description": (
            "Local Pakistani sea and road consolidator sourcing from regional "
            "suppliers to reduce long-haul air freight from Asia. "
            "Specialises in textile, electronics, and manufacturing supply chains."
        ),
        "region": "South Asia",
        "transport_mode": "sea",
        "co2_rating": "B+",
        "certifications": "Pakistan Green Business Alliance",
    },
    {
        "id": "sup_006",
        "name": "IndiaShip Direct",
        "description": (
            "Direct sea freight from Mumbai and Chennai to European ports. "
            "Modern eco-vessel fleet with scrubber technology. "
            "Alternative to air freight for time-sensitive but non-perishable goods."
        ),
        "region": "South Asia to Europe",
        "transport_mode": "sea",
        "co2_rating": "A",
        "certifications": "Green Award, BIMCO",
    },
    {
        "id": "sup_007",
        "name": "BioPackage Co.",
        "description": (
            "Regional packaging supplier using 100% recycled and biodegradable "
            "materials. Reduces upstream packaging emissions by up to 60%. "
            "Ships to EU, UK, and North America."
        ),
        "region": "Global",
        "transport_mode": "road",
        "co2_rating": "A+",
        "certifications": "FSC, B-Corp Certified",
    },
    {
        "id": "sup_008",
        "name": "NordGreen Warehousing",
        "description": (
            "Carbon-neutral cold-chain warehousing in Northern Europe. "
            "Powered by wind energy. Reduces temperature-controlled air freight "
            "by enabling regional stocking strategies in Sweden, Norway, Denmark."
        ),
        "region": "Northern Europe",
        "transport_mode": "warehousing",
        "co2_rating": "A+",
        "certifications": "Nordic Swan Ecolabel, ISO 50001",
    },
    {
        "id": "sup_009",
        "name": "AtlanticGreen Cargo",
        "description": (
            "Low-emission sea freight on South America to North America and Europe routes. "
            "Covers Sao Paulo, Buenos Aires, Santos port to New York, New Jersey, Rotterdam. "
            "Specialises in agricultural commodities, raw coffee, and food-grade cargo. "
            "Wind-assisted vessels reduce emissions by 30% vs conventional Atlantic shipping."
        ),
        "region": "South America, North America, Europe",
        "transport_mode": "sea",
        "co2_rating": "A",
        "certifications": "Clean Cargo Working Group, ISO 14001",
    },
    {
        "id": "sup_010",
        "name": "PacificNorth Freight",
        "description": (
            "Eco-certified sea freight connecting US Pacific Northwest ports (Seattle, Portland, "
            "Vancouver) to South Asia including Lahore via Karachi, and Southeast Asia. "
            "LNG-powered fleet. Ideal alternative to air freight for aerospace parts, "
            "industrial equipment, and manufactured goods on high-priority routes."
        ),
        "region": "North America, South Asia",
        "transport_mode": "sea",
        "co2_rating": "A",
        "certifications": "SmartWay, Green Marine",
    },
    {
        "id": "sup_011",
        "name": "BengalSea Logistics",
        "description": (
            "Dhaka and Chittagong-based sea freight consolidator serving North America "
            "and European destinations. Specialises in apparel, garments, and textile exports. "
            "Carbon offset program covers all shipments. "
            "Routes: Dhaka/Chittagong to New York, London, Rotterdam, Hamburg."
        ),
        "region": "South Asia, North America, Europe",
        "transport_mode": "sea",
        "co2_rating": "B+",
        "certifications": "Sustainable Apparel Coalition, WRAP",
    },
    {
        "id": "sup_012",
        "name": "KoreaSea Green",
        "description": (
            "South Korean eco-shipping company operating Busan to Europe and Middle East routes. "
            "Covers Busan to London, Rotterdam, Hamburg, Dubai. "
            "Fleet powered by LNG and hybrid scrubber technology. "
            "Handles heavy equipment, steel, and industrial cargo with low-emission certification."
        ),
        "region": "East Asia, Europe, Middle East",
        "transport_mode": "sea",
        "co2_rating": "A",
        "certifications": "Korean Register Green Ship, IMO Tier III",
    },
    {
        "id": "sup_013",
        "name": "AsiaPacific EcoFreight",
        "description": (
            "Regional sea freight across Southeast Asia and Oceania. "
            "Key routes: Singapore, Hanoi, Ho Chi Minh City to Sydney, Melbourne, Brisbane. "
            "Specialises in electronics, batteries, footwear, and consumer goods. "
            "Solar-assisted vessels with real-time carbon tracking dashboard for clients."
        ),
        "region": "Southeast Asia, Oceania",
        "transport_mode": "sea",
        "co2_rating": "A+",
        "certifications": "Asia Green Freight Network, ISO 14001",
    },
]

# ─────────────────────────────────────────────
# Initialise ChromaDB
# ─────────────────────────────────────────────

def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    ef = embedding_functions.DefaultEmbeddingFunction()   # uses sentence-transformers
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def seed_database():
    """Populate ChromaDB with supplier profiles. Run once."""
    collection = get_collection()

    # Check if already seeded
    if collection.count() >= len(SUPPLIERS):
        print(f"[supplier_db] Already seeded ({collection.count()} records). Skipping.")
        return

    documents = [s["description"] for s in SUPPLIERS]
    ids       = [s["id"] for s in SUPPLIERS]
    metadatas = [
        {
            "name":           s["name"],
            "region":         s["region"],
            "transport_mode": s["transport_mode"],
            "co2_rating":     s["co2_rating"],
            "certifications": s["certifications"],
        }
        for s in SUPPLIERS
    ]

    collection.add(documents=documents, ids=ids, metadatas=metadatas)
    print(f"[supplier_db] Seeded {len(SUPPLIERS)} supplier profiles into ChromaDB.")


def query_suppliers(query: str, n_results: int = 3) -> list[dict]:
    """
    Semantic search over supplier profiles.
    Returns a list of matched supplier dicts with name, description, and metadata.
    """
    collection = get_collection()

    if collection.count() == 0:
        seed_database()

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for i in range(len(results["ids"][0])):
        output.append({
            "supplier_name":    results["metadatas"][0][i]["name"],
            "region":           results["metadatas"][0][i]["region"],
            "transport_mode":   results["metadatas"][0][i]["transport_mode"],
            "co2_rating":       results["metadatas"][0][i]["co2_rating"],
            "certifications":   results["metadatas"][0][i]["certifications"],
            "description":      results["documents"][0][i],
            "relevance_score":  round(1 - results["distances"][0][i], 3),
        })

    return output


# ─────────────────────────────────────────────
# Seed on import / direct run
# ─────────────────────────────────────────────
if __name__ == "__main__":
    seed_database()
    # Quick test query
    queries = [
        "air freight Sao Paulo to New Jersey raw coffee alternative",
        "air freight Seattle to Lahore aerospace parts alternative",
        "sea freight Singapore to Sydney batteries",
    ]
    for q in queries:
        print(f"\nTest query: '{q}'")
        res = query_suppliers(q)
        for r in res:
            print(f"  → {r['supplier_name']} ({r['co2_rating']}) — score: {r['relevance_score']}")
