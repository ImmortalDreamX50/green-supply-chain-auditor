"""
app.py — Streamlit UI for Green Supply Chain Auditor
AMD Hackathon 2025

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
import io
import time

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Green Supply Chain Auditor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS - Professional Light Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
  /* Main container - Clean white background */
  [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }
  
  /* Professional sidebar with subtle gradient */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-right: 2px solid #e2e8f0;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  }
  
  [data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
  }
  
  /* Sidebar headings */
  [data-testid="stSidebar"] h1, 
  [data-testid="stSidebar"] h2, 
  [data-testid="stSidebar"] h3 {
    color: #1e293b !important;
    font-weight: 700 !important;
  }
  
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] .stMarkdown {
    color: #475569 !important;
  }
  
  [data-testid="stSidebar"] .stCaption {
    color: #64748b !important;
  }
  
  /* Hide default Streamlit branding */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  
  /* Professional header */
  .hero-header {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    padding: 2.5rem 3rem;
    border-radius: 20px;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 40px rgba(16, 185, 129, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  .hero-title {
    color: #ffffff;
    font-size: 2.75rem;
    font-weight: 800;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    letter-spacing: -0.5px;
  }
  
  .hero-subtitle {
    color: #d1fae5;
    font-size: 1.15rem;
    margin-top: 0.75rem;
    font-weight: 400;
    line-height: 1.6;
  }
  
  /* Enhanced metric cards - Light theme */
  .metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.75rem;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
  
  .metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(16, 185, 129, 0.15);
    border-color: #10b981;
  }
  
  .metric-card .label {
    color: #64748b;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 0.5rem;
    font-weight: 700;
  }
  
  .metric-card .value {
    color: #10b981;
    font-size: 2.75rem;
    font-weight: 800;
    line-height: 1;
  }
  
  /* Professional hotspot card - Light theme */
  .hotspot-card {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    border: 3px solid #ef4444;
    border-radius: 16px;
    padding: 1.75rem 2.25rem;
    margin: 1.5rem 0;
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.15);
  }
  
  .hotspot-title {
    color: #b91c1c;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.75rem;
    font-weight: 800;
  }
  
  .hotspot-route {
    color: #1e293b;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
  }
  
  .hotspot-value {
    color: #dc2626;
    font-size: 1.125rem;
    font-weight: 600;
  }
  
  /* Modern agent steps - Light theme */
  .agent-step {
    background: linear-gradient(90deg, rgba(16, 185, 129, 0.08) 0%, transparent 100%);
    border-left: 4px solid #10b981;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.5rem;
    margin: 0.75rem 0;
    font-size: 0.95rem;
    color: #475569;
    transition: all 0.3s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    border-right: 1px solid #e2e8f0;
    border-top: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .agent-step:hover {
    background: linear-gradient(90deg, rgba(16, 185, 129, 0.12) 0%, transparent 100%);
    transform: translateX(6px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
  }
  
  .agent-step .agent-name {
    color: #059669;
    font-weight: 800;
    font-size: 1rem;
  }
  
  /* Enhanced report box - Light theme */
  .report-box {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 2.5rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    color: #1e293b;
  }
  
  .report-box h1, .report-box h2, .report-box h3 {
    color: #1e293b !important;
  }
  
  .report-box p, .report-box li {
    color: #475569 !important;
  }
  
  /* Professional data table styling */
  .stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    border: 1px solid #e2e8f0;
  }
  
  /* Enhanced buttons */
  .stButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
  }
  
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4) !important;
  }
  
  /* File uploader enhancement - Light theme */
  [data-testid="stFileUploader"] {
    border: 3px dashed #cbd5e1 !important;
    border-radius: 20px !important;
    padding: 2.5rem !important;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
    transition: all 0.3s ease !important;
  }
  
  [data-testid="stFileUploader"]:hover {
    border-color: #10b981 !important;
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.1) !important;
  }
  
  /* Sidebar enhancements - Professional light design */
  .sidebar-section {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border-radius: 16px;
    padding: 1.25rem;
    margin: 1rem 0;
    border: 2px solid #a7f3d0;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.08);
  }
  
  .sidebar-logo {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
  }
  
  /* Info box styling - Light theme */
  .stAlert {
    border-radius: 14px !important;
    border-left: 5px solid #10b981 !important;
    background: #f0fdf4 !important;
    color: #065f46 !important;
  }
  
  /* Download button - Professional style */
  .stDownloadButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.75rem !important;
    font-weight: 700 !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
  }
  
  .stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
  }
  
  /* Divider styling */
  hr {
    border-color: #e2e8f0 !important;
    opacity: 0.8 !important;
    margin: 2rem 0 !important;
  }
  
  /* Text color fixes for light theme */
  h1, h2, h3, h4, h5, h6 {
    color: #1e293b !important;
  }
  
  p, div, span {
    color: #475569;
  }
  
  .stMarkdown {
    color: #475569;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar - Executive Professional Layout
# ─────────────────────────────────────────────
with st.sidebar:
    # Professional logo section
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🌿</div>
        <div style="color: white; font-size: 1.3rem; font-weight: 800; letter-spacing: 0.5px;">
            GREEN SUPPLY CHAIN
        </div>
        <div style="color: #d1fae5; font-size: 0.85rem; margin-top: 0.25rem; font-weight: 500;">
            ESG Carbon Auditor
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Technology badge
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center;">
        <div style="color: #059669; font-weight: 800; font-size: 0.95rem; margin-bottom: 0.5rem;">
            ⚡ POWERED BY AMD
        </div>
        <div style="color: #64748b; font-size: 0.85rem; line-height: 1.6;">
            <b>AMD Instinct MI300X</b><br>
            Llama-3-70B LLM<br>
            ROCm AI Acceleration
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # How it works - Professional format
    st.markdown("### 📋 How It Works")
    st.markdown("")
    
    st.markdown("""
    <div style="line-height: 2.2; color: #475569;">
        <div style="margin-bottom: 0.75rem;">
            <span style="display: inline-block; width: 28px; height: 28px; background: linear-gradient(135deg, #10b981, #059669); 
                         border-radius: 50%; color: white; text-align: center; line-height: 28px; 
                         font-weight: 700; font-size: 0.85rem; margin-right: 0.75rem;">1</span>
            <span style="font-weight: 600; color: #1e293b;">Upload CSV Data</span>
        </div>
        <div style="margin-bottom: 0.75rem;">
            <span style="display: inline-block; width: 28px; height: 28px; background: linear-gradient(135deg, #10b981, #059669); 
                         border-radius: 50%; color: white; text-align: center; line-height: 28px; 
                         font-weight: 700; font-size: 0.85rem; margin-right: 0.75rem;">2</span>
            <span style="font-weight: 600; color: #1e293b;">AI Agents Analyze</span>
        </div>
        <div style="margin-bottom: 0.75rem;">
            <span style="display: inline-block; width: 28px; height: 28px; background: linear-gradient(135deg, #10b981, #059669); 
                         border-radius: 50%; color: white; text-align: center; line-height: 28px; 
                         font-weight: 700; font-size: 0.85rem; margin-right: 0.75rem;">3</span>
            <span style="font-weight: 600; color: #1e293b;">Identify Hotspots</span>
        </div>
        <div style="margin-bottom: 0.75rem;">
            <span style="display: inline-block; width: 28px; height: 28px; background: linear-gradient(135deg, #10b981, #059669); 
                         border-radius: 50%; color: white; text-align: center; line-height: 28px; 
                         font-weight: 700; font-size: 0.85rem; margin-right: 0.75rem;">4</span>
            <span style="font-weight: 600; color: #1e293b;">Get Recommendations</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # CSV Format - Cleaner design
    st.markdown("### 📝 Required Format")
    st.markdown("")
    st.code("""origin,destination,weight_tons,transport_mode
Shanghai,Karachi,5,Air
Mumbai,London,12,Sea""", language="csv")
    
    # Download button
    sample_csv = "origin,destination,weight_tons,transport_mode\nShanghai,Karachi,5,Air\nMumbai,London,12,Sea\nFrankfurt,Paris,3,Road\nLos Angeles,Tokyo,8,Air\nShenzhen,Rotterdam,20,Sea\n"
    st.download_button(
        "⬇️ Download Sample",
        sample_csv,
        "sample_shipments.csv",
        "text/csv",
        use_container_width=True
    )
    
    st.divider()
    
    # Professional stats section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center;">
        <div style="color: #059669; font-weight: 800; font-size: 0.95rem; margin-bottom: 1rem;">
            📊 PLATFORM CAPABILITIES
        </div>
        <div style="display: flex; justify-content: space-around; margin-top: 1rem;">
            <div>
                <div style="color: #10b981; font-size: 1.75rem; font-weight: 800;">20+</div>
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 600;">Routes</div>
            </div>
            <div>
                <div style="color: #10b981; font-size: 1.75rem; font-weight: 800;">8</div>
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 600;">Suppliers</div>
            </div>
            <div>
                <div style="color: #10b981; font-size: 1.75rem; font-weight: 800;">3</div>
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 600;">AI Agents</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    # Footer badge
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 0.75rem; 
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); 
                border-radius: 10px; border: 1px solid #a7f3d0;">
        <div style="color: #059669; font-size: 0.8rem; font-weight: 700;">
            ✓ Real-time Processing
        </div>
        <div style="color: #64748b; font-size: 0.75rem; margin-top: 0.25rem;">
            Instant carbon insights
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Main UI - Professional Header
# ─────────────────────────────────────────────
# Hero header
st.markdown("""
<div class="hero-header">
    <h1 class="hero-title">🌿 Green Supply Chain Auditor</h1>
    <p class="hero-subtitle">AI-powered carbon footprint analysis for sustainable logistics | Powered by AMD Instinct MI300X</p>
</div>
""", unsafe_allow_html=True)

# Demo mode toggle
col1, col2 = st.columns([3, 1])
with col1:
    demo_mode = st.checkbox(
        "🎨 Demo Mode (No API Required)", 
        help="Preview the platform with sample data - no API credits needed"
    )
with col2:
    if demo_mode:
        st.success("✓ Demo Active")

if demo_mode:
    st.info("💡 **Demo Mode Active** - Using realistic mock data to showcase the platform. Add OpenAI/AMD API credentials to process real shipments.")

st.markdown("<br>", unsafe_allow_html=True)

# Upload section with better styling
st.markdown("### 📂 Upload Shipping Data")

# File upload
uploaded_file = st.file_uploader(
    "Drag and drop your CSV file here or click to browse",
    type=["csv", "txt"],
    help="CSV format: origin, destination, weight_tons, transport_mode",
    label_visibility="collapsed"
)

# Text fallback with better UX
with st.expander("✍️ Or paste shipping data directly", expanded=False):
    raw_text_input = st.text_area(
        "Paste CSV data here:",
        placeholder="origin,destination,weight_tons,transport_mode\nShanghai,Karachi,5,Air\nMumbai,London,12,Sea\n...",
        height=150,
        label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Action button with better spacing
col1, col2, col3 = st.columns([2, 2, 2])
with col2:
    run_button = st.button("🚀 Run Carbon Audit", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# Run pipeline
# ─────────────────────────────────────────────
if run_button:
    # Determine input data
    raw_data = ""
    if uploaded_file:
        raw_data = uploaded_file.read().decode("utf-8")
    elif raw_text_input.strip():
        raw_data = raw_text_input.strip()
    else:
        st.warning("Please upload a CSV file or paste shipping data first.")
        st.stop()

    # Show preview of uploaded data
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Data Preview")
    st.caption("Verify your uploaded shipment data before processing")
    
    try:
        df_preview = pd.read_csv(io.StringIO(raw_data))
        st.dataframe(df_preview, use_container_width=True, height=200)
        st.caption(f"✓ {len(df_preview)} shipments detected | {len(df_preview.columns)} columns")
    except Exception:
        with st.expander("📄 Raw Data View"):
            st.code(raw_data[:500], language="csv")

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    
    # Agent activity section with professional styling
    st.markdown("### 🤖 AI Agent Pipeline")
    st.caption("Multi-agent system processing your data in real-time")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Agent progress display
    agent_log = st.container()

    with agent_log:
        step1 = st.empty()
        step2 = st.empty()
        step3 = st.empty()

    step1.markdown('<div class="agent-step"><span class="agent-name">Agent 1 — Data Extractor</span> &nbsp; 🔄 Parsing shipment records...</div>', unsafe_allow_html=True)

    # ── Import and run agents ──────────────────
    if demo_mode:
        # Demo mode: return mock results
        time.sleep(1)  # Simulate processing
        results = {
            "extraction": "Extracted 5 shipment records from the uploaded data.",
            "emissions": json.dumps({
                "shipments": [
                    {"route": "Shanghai → Karachi", "mode": "Air", "distance_km": 4200, "weight_tons": 5, "co2_kg": 16800, "esg_rating": "C"},
                    {"route": "Mumbai → London", "mode": "Sea", "distance_km": 7200, "weight_tons": 12, "co2_kg": 1296, "esg_rating": "A"},
                    {"route": "Frankfurt → Paris", "mode": "Road", "distance_km": 450, "weight_tons": 3, "co2_kg": 135, "esg_rating": "B+"},
                    {"route": "Los Angeles → Tokyo", "mode": "Air", "distance_km": 8800, "weight_tons": 8, "co2_kg": 56320, "esg_rating": "D"},
                    {"route": "Shenzhen → Rotterdam", "mode": "Sea", "distance_km": 9500, "weight_tons": 20, "co2_kg": 2850, "esg_rating": "A+"}
                ],
                "total_co2_kg": 77401,
                "hotspot": {
                    "route": "Los Angeles → Tokyo (Air)",
                    "co2_kg": 56320,
                    "recommendation": "Switch from air to sea freight using OceanPath Logistics (ESG Rating: A+). This change will reduce emissions by 98% and save 55 tonnes of CO₂."
                }
            }),
            "report": """# 🌿 Carbon Audit Report (Demo)

## Executive Summary
**Total Emissions:** 77.4 tonnes CO₂  
**Hotspot Identified:** Los Angeles → Tokyo air freight (73% of total emissions)

## Key Findings
1. **Air freight dominates emissions** - LA→Tokyo route alone contributes 56.3 tonnes CO₂
2. **Sea freight is optimal** - Mumbai→London and Shenzhen→Rotterdam show excellent performance (A/A+ ratings)
3. **Immediate action available** - Switching LA→Tokyo to sea freight saves 55 tonnes CO₂ (98% reduction)

## Recommendations

### 🚨 Priority 1: Los Angeles → Tokyo
- **Current:** Air freight, 56.3 tonnes CO₂
- **Recommended:** OceanPath Logistics (Sea freight, A+ rating)
- **Savings:** 55 tonnes CO₂ (98% reduction)
- **Trade-off:** +12 days transit time

### ⚡ Priority 2: Shanghai → Karachi  
- **Current:** Air freight, 16.8 tonnes CO₂
- **Recommended:** Karachi Green Port Logistics (B+ rating)
- **Savings:** 14 tonnes CO₂ (83% reduction)

### ✅ Maintain Best Practices
- Continue using sea freight for EU-Asia routes
- Current Mumbai→London and Shenzhen→Rotterdam are optimal

## Impact Summary
Implementing all recommendations would reduce annual emissions by **69.8 tonnes CO₂** (90% reduction), equivalent to taking 15 cars off the road for a year.

---
*Generated in Demo Mode - Add API credits to process your actual data*
"""
        }
    else:
        try:
            from agents import run_audit
        except ImportError as e:
            st.error(f"Could not import agents.py: {e}\nMake sure your AMD API keys are set in .env")
            st.stop()

        with st.spinner("Running 3-agent pipeline on AMD Instinct MI300X..."):
            try:
                results = run_audit(raw_data)
            except Exception as e:
                st.error(f"Agent pipeline error: {e}")
                st.stop()

    step1.markdown('<div class="agent-step"><span class="agent-name">Agent 1 — Data Extractor</span> &nbsp; ✅ Shipment records extracted</div>', unsafe_allow_html=True)
    step2.markdown('<div class="agent-step"><span class="agent-name">Agent 2 — Carbon Calculator</span> &nbsp; ✅ Emissions calculated, hotspot identified</div>', unsafe_allow_html=True)
    
    if demo_mode:
        step3.markdown('<div class="agent-step"><span class="agent-name">Agent 3 — Sourcing Strategist</span> &nbsp; ✅ Demo report generated (using mock data)</div>', unsafe_allow_html=True)
    else:
        step3.markdown('<div class="agent-step"><span class="agent-name">Agent 3 — Sourcing Strategist</span> &nbsp; ✅ Sustainability roadmap generated</div>', unsafe_allow_html=True)

    # ── Parse emissions JSON ───────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📊 Carbon Emissions Analysis")
    st.caption("Comprehensive breakdown of your supply chain's carbon footprint")
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        emissions_data = json.loads(results["emissions"])
        shipments = emissions_data.get("shipments", [])
        total_co2  = emissions_data.get("total_co2_kg", 0)
        hotspot    = emissions_data.get("hotspot", {})

        # Professional metric cards with better formatting
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="metric-card">
              <div class="label">💨 Total CO₂ Emissions</div>
              <div class="value">{total_co2/1000:,.1f}</div>
              <div class="label" style="color: #64748b; margin-top: 0.5rem;">tonnes CO₂</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card">
              <div class="label">📦 Shipments Audited</div>
              <div class="value">{len(shipments)}</div>
              <div class="label" style="color: #64748b; margin-top: 0.5rem;">routes analyzed</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            air_count = sum(1 for s in shipments if s.get("mode","").lower() == "air" or s.get("transport_mode","").lower() == "air")
            st.markdown(f"""<div class="metric-card">
              <div class="label">✈️ High-Risk Routes</div>
              <div class="value">{air_count}</div>
              <div class="label" style="color: #64748b; margin-top: 0.5rem;">air freight shipments</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Enhanced hotspot display with improved clarity
        if hotspot:
            hotspot_route = hotspot.get('route', f"{hotspot.get('origin','?')} → {hotspot.get('destination','?')}")
            hotspot_co2 = hotspot.get('co2_kg', 0)
            hotspot_pct = round(hotspot_co2/total_co2*100) if total_co2 else 0
            hotspot_recommendation = hotspot.get('recommendation', 'Switch to greener transport mode for significant savings')
            
            # Build HTML as a single line to avoid rendering issues
            hotspot_html = f"""
            <div class="hotspot-card">
                <div class="hotspot-title">🔥 HIGHEST IMPACT ROUTE</div>
                <div class="hotspot-route">{hotspot_route}</div>
                <div style="margin-top: 1rem;">
                    <div style="font-size: 1.75rem; font-weight: 800; color: #dc2626; margin-bottom: 0.5rem;">{hotspot_co2:,.0f} kg CO₂</div>
                    <div style="font-size: 1rem; color: #991b1b; font-weight: 600;">{hotspot_pct}% of your total carbon footprint</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.6); border-radius: 10px; padding: 1rem; margin-top: 1.25rem; border-left: 4px solid #059669;">
                    <div style="color: #065f46; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">💡 RECOMMENDED ACTION</div>
                    <div style="color: #047857; font-size: 1rem; font-weight: 600; line-height: 1.6;">{hotspot_recommendation}</div>
                </div>
            </div>
            """
            st.markdown(hotspot_html, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

        # Professional emissions visualization
        st.markdown("#### 📈 Carbon Footprint by Route")
        st.caption("Compare emissions across all your shipping routes")
        df_em = pd.DataFrame(shipments)
        if not df_em.empty and "co2_kg" in df_em.columns:
            # Create better route labels
            if "route" in df_em.columns:
                df_em["route_label"] = df_em["route"]
            else:
                df_em["route_label"] = df_em.get("origin", "?") + " → " + df_em.get("destination", "?")
            
            df_em = df_em.sort_values("co2_kg", ascending=False)
            
            # Convert to tonnes for better readability
            df_em["co2_tonnes"] = df_em["co2_kg"] / 1000
            
            st.bar_chart(df_em.set_index("route_label")["co2_tonnes"], color="#10b981")
            st.caption("💡 Chart shows emissions in tonnes of CO₂ — Higher bars indicate priority routes for optimization")

        st.markdown("<br>", unsafe_allow_html=True)

        # Enhanced detailed table
        st.markdown("#### 📋 Complete Route Details")
        st.caption("Full breakdown of each shipment's environmental impact")
        if not df_em.empty:
            # Prepare display columns
            display_df = df_em.copy()
            
            # Format columns for better display
            if "co2_kg" in display_df.columns:
                display_df["CO₂ (kg)"] = display_df["co2_kg"].apply(lambda x: f"{x:,.0f}")
            if "distance_km" in display_df.columns:
                display_df["Distance (km)"] = display_df["distance_km"].apply(lambda x: f"{x:,.0f}")
            if "weight_tons" in display_df.columns or "weight_tonnes" in display_df.columns:
                weight_col = "weight_tons" if "weight_tons" in display_df.columns else "weight_tonnes"
                display_df["Weight (t)"] = display_df[weight_col]
            
            # Select columns to show
            show_cols = []
            if "route_label" in display_df.columns:
                show_cols.append("route_label")
                display_df = display_df.rename(columns={"route_label": "Route"})
            elif "origin" in display_df.columns and "destination" in display_df.columns:
                show_cols.extend(["origin", "destination"])
                
            if "mode" in display_df.columns:
                show_cols.append("mode")
                display_df = display_df.rename(columns={"mode": "Mode"})
            elif "transport_mode" in display_df.columns:
                show_cols.append("transport_mode")
                display_df = display_df.rename(columns={"transport_mode": "Mode"})
                
            for col in ["Weight (t)", "Distance (km)", "CO₂ (kg)"]:
                if col in display_df.columns:
                    show_cols.append(col)
            
            if "esg_rating" in display_df.columns:
                show_cols.append("esg_rating")
                display_df = display_df.rename(columns={"esg_rating": "ESG Rating"})
            
            st.dataframe(
                display_df[[c for c in show_cols if c in display_df.columns]],
                use_container_width=True,
                height=300
            )

    except (json.JSONDecodeError, KeyError):
        st.warning("⚠️ Unable to parse emissions data")
        with st.expander("📄 View Raw Data"):
            st.code(results.get("emissions", ""), language="json")

    # ── Sustainability Roadmap ─────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 🌱 AI-Generated Sustainability Roadmap")
    st.caption("Strategic recommendations to reduce your carbon footprint")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="report-box">', unsafe_allow_html=True)
    st.markdown(results.get("report", "No report generated."))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Enhanced download section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        report_text = results.get("report", "")
        st.download_button(
            "⬇️ Download Complete Report",
            report_text,
            file_name=f"carbon_audit_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Raw extraction (expandable) ────────────
    with st.expander("🔍 View Raw Agent Outputs (Technical Details)"):
        st.markdown("**Agent 1 - Data Extraction:**")
        st.text(results.get("extraction", "No data")[:500])
        st.markdown("**Agent 2 - Emissions JSON:**")
        st.code(results.get("emissions", "{}"), language="json")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Success message with better styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                padding: 1.5rem; border-radius: 12px; text-align: center; 
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
        <h3 style="color: white; margin: 0;">✅ Audit Complete!</h3>
        <p style="color: #d1fae5; margin: 0.5rem 0 0 0;">
            Powered by AMD Instinct MI300X • AI-driven insights in seconds
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Professional Footer (always shown)
# ─────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="text-align: center; color: #64748b;">
        <h4 style="color: #10b981;">🌍 Our Impact</h4>
        <p style="font-size: 0.9rem;">
            Helping businesses reduce<br>
            carbon emissions through<br>
            AI-powered insights
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="text-align: center; color: #64748b;">
        <h4 style="color: #10b981;">⚡ Technology</h4>
        <p style="font-size: 0.9rem;">
            AMD Instinct MI300X<br>
            Llama-3-70B via ROCm<br>
            Multi-Agent AI System
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="text-align: center; color: #64748b;">
        <h4 style="color: #10b981;">📊 Features</h4>
        <p style="font-size: 0.9rem;">
            Real-time carbon tracking<br>
            20+ trade route coverage<br>
            Green supplier database
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Copyright/credit
st.markdown("""
<div style="text-align: center; color: #475569; padding: 2rem 0 1rem 0; font-size: 0.875rem;">
    🌿 <b>Green Supply Chain Auditor</b> | Built for AMD Hackathon 2025<br>
    <span style="color: #64748b;">Empowering sustainable logistics through AI</span>
</div>
""", unsafe_allow_html=True)
