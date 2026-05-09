# 🌿 Green Supply Chain Auditor
**AMD Hackathon 2025** — Multi-Agent ESG Carbon Auditing System

> *"Companies are failing their climate goals because they can't track their tier-2 suppliers. Our AMD-powered agentic system audits entire supply chains in seconds — not months."*

---

## Architecture

```
CSV Upload → Agent 1 (Data Extractor)
                  ↓
           Agent 2 (Carbon Calculator) ← ChromaDB Supplier Memory
                  ↓
           Agent 3 (Sourcing Strategist)
                  ↓
         Carbon Audit Report (Markdown)
```

## Why AMD?

- **Model:** Llama-3-70B running on AMD Developer Cloud via **ROCm**
- **Hardware:** AMD Instinct MI300X — high memory bandwidth enables faster processing of large, complex supply chain datasets vs traditional GPUs
- **Framework:** CrewAI for multi-agent orchestration

---

## Setup

```bash
# 1. Clone and enter project
cd green_supply_chain

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your AMD API credentials
cp .env.example .env
# Edit .env and add your AMD_API_KEY and AMD_API_BASE_URL

# 4. Seed the supplier database (run once)
python supplier_db.py

# 5. Launch the app
streamlit run app.py
```

---

## Files

| File | Purpose |
|------|---------|
| `agents.py` | CrewAI agent definitions + task pipeline |
| `supplier_db.py` | ChromaDB vector store — eco-friendly supplier profiles |
| `app.py` | Streamlit UI |
| `requirements.txt` | Python dependencies |
| `.env.example` | API key template |

---

## Sample Input CSV

```csv
origin,destination,weight_tons,transport_mode
Shanghai,Karachi,5,Air
Mumbai,London,12,Sea
Frankfurt,Paris,3,Road
Los Angeles,Tokyo,8,Air
```

---

## Team

- **Architect:** Agent design, CrewAI config, pitch
- **Dev 1:** Streamlit UI, ChromaDB, file parsing
- **Dev 2:** AMD API integration, emission factors, output formatting
