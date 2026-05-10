# 🔌 Complete Connection Architecture

## Connection Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                    (Streamlit Browser)                       │
│                   http://localhost:8501                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ User uploads CSV / clicks "Run Audit"
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (app.py)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Line 154: from agents import run_audit              │  │
│  │  Line 159: results = run_audit(raw_data)             │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Function call with CSV data
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (agents.py)                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Line 242: def run_audit(raw_data: str) -> dict     │   │
│  │                                                      │   │
│  │   • Creates 3 agents                                │   │
│  │   • Builds task pipeline                            │   │
│  │   • Executes crew.kickoff()                         │   │
│  │                                                      │   │
│  │   Returns:                                          │   │
│  │   {                                                  │   │
│  │     "extraction": str,   # Agent 1 output          │   │
│  │     "emissions": str,    # Agent 2 JSON            │   │
│  │     "report": str        # Agent 3 markdown        │   │
│  │   }                                                  │   │
│  └────────────┬───────────────────────────────────────┘   │
│               │                                             │
│               │ Each agent needs LLM calls                  │
│               │                                             │
└───────────────┼─────────────────────────────────────────────┘
                │
                │ HTTP API calls
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│               AMD DEVELOPER CLOUD API                        │
│           (or OpenAI as temporary fallback)                  │
│                                                              │
│  Configuration from .env:                                    │
│  • AMD_API_KEY                                              │
│  • AMD_API_BASE_URL                                         │
│                                                              │
│  Model: meta/llama-3-70b-instruct                           │
│  Hardware: AMD Instinct MI300X with ROCm                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📡 Connection Points

### 1️⃣ **Frontend → Backend**
- **File:** app.py line 154
- **Method:** Direct Python import
- **Interface:**
  ```python
  from agents import run_audit
  results = run_audit(raw_data)  # raw_data = CSV string
  ```
- **Status:** ✅ Already connected (no setup needed)

### 2️⃣ **Backend → AMD API**
- **File:** agents.py lines 18-22
- **Method:** HTTP REST API (via langchain-openai)
- **Interface:**
  ```python
  llm = ChatOpenAI(
      model="meta/llama-3-70b-instruct",
      base_url=os.getenv("AMD_API_BASE_URL"),
      api_key=os.getenv("AMD_API_KEY")
  )
  ```
- **Status:** ⚠️ Needs API key configuration

### 3️⃣ **Backend → Database**
- **File:** agents.py line 80 (tool function)
- **Method:** Direct Python import
- **Interface:**
  ```python
  from supplier_db import query_suppliers
  results = query_suppliers(query, n_results=3)
  ```
- **Status:** ✅ Already connected (runs locally)

---

## 🧪 Testing Each Connection

### Test 1: Database Connection
```powershell
python supplier_db.py
```
Expected: `[supplier_db] Seeded 8 supplier profiles into ChromaDB.`

### Test 2: AMD API Connection
```powershell
python test_amd_connection.py
```
Expected: `✅ AMD API Connected Successfully!`

### Test 3: Agent Pipeline (Backend)
```powershell
python agents.py
```
Expected: Full audit report with 3 agent outputs

### Test 4: Full Stack (Frontend + Backend)
```powershell
streamlit run app.py
```
Then upload sample_shipments.csv

---

## 🔧 Troubleshooting Connections

### Issue 1: "Could not import agents.py"
**Cause:** Frontend can't find backend module  
**Solution:** Make sure you're running `streamlit run app.py` from the project root directory

### Issue 2: "AMD_API_KEY not set"
**Cause:** Backend can't connect to AMD  
**Solution:** 
```powershell
notepad .env
# Add your AMD_API_KEY
```

### Issue 3: "ChromaDB import error"
**Cause:** Database package not installed  
**Solution:**
```powershell
pip install chromadb sentence-transformers
```

### Issue 4: API timeout
**Cause:** AMD API slow or unreachable  
**Solution:** Use OpenAI fallback (see OPENAI_FALLBACK_CONFIG.txt)

---

## 📝 Configuration Checklist

- [ ] .env file exists with API keys
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] Database seeded (python supplier_db.py)
- [ ] Backend tested (python agents.py)
- [ ] Frontend launched (streamlit run app.py)

---

## 🚀 Quick Start Commands

```powershell
# 1. Setup (one-time)
notepad .env          # Add your AMD_API_KEY
python supplier_db.py # Seed database

# 2. Test connection
python test_amd_connection.py

# 3. Test backend
python agents.py

# 4. Launch full app
streamlit run app.py
# Visit: http://localhost:8501
```

---

## 🤝 Integration with Person 2

**Person 2 (Frontend) doesn't need to do anything for the connection!**

The connection is already implemented:
- ✅ Import statement: Line 154 of app.py
- ✅ Function call: Line 159 of app.py
- ✅ Result handling: Lines 162-260 of app.py

**What Person 2 should test:**
1. UI displays agent activity correctly
2. Emissions chart renders with data
3. Carbon hotspot card shows correctly
4. Download button works
5. Error messages display properly

**Meeting point:**
When you (Person 1) confirm backend works with `python agents.py`, coordinate with Person 2 to test the full stack together with `streamlit run app.py`.
