# 🚀 Quick Start Guide

## Prerequisites
- Python 3.9+ installed
- AMD Developer Cloud API access (or OpenAI for testing)

## Setup (5 minutes)

### 1️⃣ Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2️⃣ Configure API Keys
```powershell
# .env file is already created, just edit it:
notepad .env
```

Add your AMD API credentials:
```
AMD_API_KEY=your_actual_key_here
AMD_API_BASE_URL=https://api.amd.com/v1
```

**Don't have AMD access?** Use OpenAI for testing:
```
# Comment out AMD lines, add:
OPENAI_API_KEY=your_openai_key_here
```

Then modify `agents.py` line 15-20 to use OpenAI model.

### 3️⃣ Seed Database
```powershell
python supplier_db.py
```

### 4️⃣ Test System
```powershell
python test_system.py
```

### 5️⃣ Launch App
```powershell
streamlit run app.py
```

---

## 🧪 Quick Test Without LLM

Test the database and tools without API keys:

```powershell
python -c "from supplier_db import seed_database, query_suppliers; seed_database(); print(query_suppliers('sea freight'))"
```

---

## 📊 Using the App

1. **Upload CSV** - Use `sample_shipments.csv` or create your own
2. **Click "Run Audit"** - 3 AI agents analyze your supply chain
3. **View Results** - Carbon emissions, hotspots, and recommendations
4. **Download Report** - Get markdown sustainability roadmap

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `AMD_API_KEY not set` | Edit `.env` file with your credentials |
| `ChromaDB error` | Delete `chroma_db/` folder and run `python supplier_db.py` |
| `LLM timeout` | Check internet connection, verify API endpoint |

---

## 🎯 For Hackathon Demo

**Best demo flow:**
1. Show `sample_shipments.csv` in editor (10 shipments)
2. Upload to Streamlit app
3. Click "Run Audit" - show agent activity in real-time
4. Highlight the Carbon Hotspot (usually air freight routes)
5. Show Top 3 Recommendations from Agent 3
6. Download the report

**Key talking points:**
- "3 specialized AI agents working together"
- "Powered by AMD Instinct MI300X with Llama-3-70B"
- "Reduces audit time from months to seconds"
- "ChromaDB stores 8 verified green suppliers"

---

## 📁 Project Structure

```
green-supply-chain-auditor/
├── agents.py              # 3 CrewAI agents + tools
├── supplier_db.py         # ChromaDB vector store
├── app.py                 # Streamlit UI
├── test_system.py         # Automated testing
├── sample_shipments.csv   # Demo data
├── requirements.txt       # Python dependencies
├── .env                   # API credentials (don't commit!)
└── README.md             # Full documentation
```

---

## 👥 Team Roles (Reference)

- **Person 1** (You): Backend - agents.py, supplier_db.py, AMD integration
- **Person 2**: Frontend - app.py, UI polish, CSV parsing
- **Person 3**: Pitch - Demo script, README, presentation

---

Need help? Check `README.md` for full documentation.
