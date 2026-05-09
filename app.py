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
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0f1117; }
  [data-testid="stSidebar"] { background: #161a24; }
  .metric-card {
    background: #1c2130;
    border: 1px solid #2d3555;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
  }
  .metric-card .label { color: #8892b0; font-size: 13px; margin-bottom: 6px; }
  .metric-card .value { color: #e2e8f0; font-size: 28px; font-weight: 600; }
  .hotspot-card {
    background: #2a1a1a;
    border: 1px solid #c0392b;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
  }
  .agent-step {
    background: #161a24;
    border-left: 3px solid #2ecc71;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 13px;
    color: #a8b2d8;
  }
  .agent-step .agent-name { color: #64ffda; font-weight: 600; }
  .report-box {
    background: #161a24;
    border: 1px solid #2d3555;
    border-radius: 12px;
    padding: 24px;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/AMD_Logo.svg/320px-AMD_Logo.svg.png", width=100)
    st.markdown("## 🌿 Green Supply Chain Auditor")
    st.markdown("Powered by **Llama-3-70B** on **AMD Instinct MI300X** via ROCm")
    st.divider()
    st.markdown("### How it works")
    st.markdown("""
1. 📂 **Upload** your shipping CSV
2. 🤖 **3 AI Agents** analyse your data
3. 📊 **Carbon hotspots** are identified
4. 🌱 **Green alternatives** are recommended
    """)
    st.divider()
    st.markdown("### Sample CSV format")
    st.code("""origin,destination,weight_tons,transport_mode
Shanghai,Karachi,5,Air
Mumbai,London,12,Sea
Frankfurt,Paris,3,Road""", language="csv")

    # Download sample CSV
    sample_csv = "origin,destination,weight_tons,transport_mode\nShanghai,Karachi,5,Air\nMumbai,London,12,Sea\nFrankfurt,Paris,3,Road\nLos Angeles,Tokyo,8,Air\nShenzhen,Rotterdam,20,Sea\n"
    st.download_button("⬇️ Download sample CSV", sample_csv, "sample_shipments.csv", "text/csv")

# ─────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────
st.title("🌿 Green Supply Chain Auditor")
st.markdown("*Upload your shipping data and our AMD-powered AI agents will audit your carbon footprint in seconds.*")

# File upload
uploaded_file = st.file_uploader(
    "Upload shipping data (CSV or paste text below)",
    type=["csv", "txt"],
    help="CSV with columns: origin, destination, weight_tons, transport_mode"
)

# Text fallback
raw_text_input = st.text_area(
    "Or paste shipping data directly:",
    placeholder="origin,destination,weight_tons,transport_mode\nShanghai,Karachi,5,Air\n...",
    height=120,
)

run_col, _ = st.columns([1, 3])
with run_col:
    run_button = st.button("🚀 Run Audit", type="primary", use_container_width=True)

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
    st.subheader("📋 Uploaded Data Preview")
    try:
        df_preview = pd.read_csv(io.StringIO(raw_data))
        st.dataframe(df_preview, use_container_width=True)
    except Exception:
        st.text(raw_data[:500])

    st.divider()
    st.subheader("🤖 Agent Activity")

    # Agent progress display
    agent_log = st.container()

    with agent_log:
        step1 = st.empty()
        step2 = st.empty()
        step3 = st.empty()

    step1.markdown('<div class="agent-step"><span class="agent-name">Agent 1 — Data Extractor</span> &nbsp; Parsing shipment records...</div>', unsafe_allow_html=True)

    # ── Import and run agents ──────────────────
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
    step3.markdown('<div class="agent-step"><span class="agent-name">Agent 3 — Sourcing Strategist</span> &nbsp; ✅ Sustainability roadmap generated</div>', unsafe_allow_html=True)

    # ── Parse emissions JSON ───────────────────
    st.divider()
    st.subheader("📊 Emissions Breakdown")

    try:
        emissions_data = json.loads(results["emissions"])
        shipments = emissions_data.get("shipments", [])
        total_co2  = emissions_data.get("total_co2_kg", 0)
        hotspot    = emissions_data.get("hotspot", {})

        # Metric cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="metric-card">
              <div class="label">Total CO₂ Emissions</div>
              <div class="value">{total_co2:,.0f} kg</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card">
              <div class="label">Shipments Audited</div>
              <div class="value">{len(shipments)}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            air_count = sum(1 for s in shipments if s.get("transport_mode","").lower() == "air")
            st.markdown(f"""<div class="metric-card">
              <div class="label">High-Emission Air Routes</div>
              <div class="value">{air_count}</div>
            </div>""", unsafe_allow_html=True)

        # Hotspot
        if hotspot:
            st.markdown(f"""<div class="hotspot-card">
              🔥 <strong>Carbon Hotspot:</strong> &nbsp;
              {hotspot.get('origin','?')} → {hotspot.get('destination','?')} &nbsp;|&nbsp;
              {hotspot.get('transport_mode','?').upper()} &nbsp;|&nbsp;
              <strong>{hotspot.get('co2_kg',0):,.0f} kg CO₂</strong> &nbsp;
              ({round(hotspot.get('co2_kg',0)/total_co2*100) if total_co2 else 0}% of total)
            </div>""", unsafe_allow_html=True)

        # Emissions bar chart
        df_em = pd.DataFrame(shipments)
        if not df_em.empty and "co2_kg" in df_em.columns:
            df_em["route"] = df_em["origin"] + " → " + df_em["destination"]
            df_em = df_em.sort_values("co2_kg", ascending=False)
            st.bar_chart(df_em.set_index("route")["co2_kg"])

        # Detailed table
        st.markdown("**Shipment Details**")
        cols_to_show = ["origin", "destination", "weight_tons", "transport_mode", "distance_km", "co2_kg"]
        cols_available = [c for c in cols_to_show if c in df_em.columns]
        st.dataframe(df_em[cols_available], use_container_width=True)

    except (json.JSONDecodeError, KeyError):
        st.info("Emissions data (raw):")
        st.text(results.get("emissions", ""))

    # ── Sustainability Roadmap ─────────────────
    st.divider()
    st.subheader("🌱 Sustainability Roadmap")
    st.markdown('<div class="report-box">', unsafe_allow_html=True)
    st.markdown(results.get("report", "No report generated."))
    st.markdown('</div>', unsafe_allow_html=True)

    # Download report
    report_text = results.get("report", "")
    st.download_button(
        "⬇️ Download Full Report",
        report_text,
        file_name="carbon_audit_report.md",
        mime="text/markdown",
    )

    # ── Raw extraction (expandable) ────────────
    with st.expander("🔍 Raw Extraction Output (Agent 1)"):
        st.text(results.get("extraction", ""))

    st.success("✅ Audit complete! Powered by AMD Instinct MI300X + Llama-3-70B via ROCm")
