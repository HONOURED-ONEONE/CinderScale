import streamlit as st
import requests
import time

st.set_page_config(page_title="RCA Copilot CEF Dashboard", layout="wide")

st.title("RCA Copilot — Continuous Epistemic Falsifier")

# Sidebar Configuration
st.sidebar.header("Backend Settings")
backend_url = st.sidebar.text_input("Control Plane API URL", "http://localhost:5000")
refresh_rate = st.sidebar.slider("Refresh Interval (s)", 2, 30, 5)
auto_refresh = st.sidebar.toggle("Auto Refresh", value=True)

def get_data(endpoint):
    try:
        r = requests.get(f"{backend_url}/api/{endpoint}", timeout=2)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return None

# State management for auto-refresh
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()

# Fetch Data
analysis = get_data("Cef/latest-analysis")
claims = get_data("Cef/claims")
contradictions = get_data("Cef/contradictions")
ledger = get_data("Cef/ledger")

if not analysis:
    st.warning("Could not connect to Control Plane or no analysis available yet.")
    st.stop()

# Header Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest Run", analysis["final"]["run_id"])
c2.metric("TSS", f"{analysis['final']['tss']:.3f}")
c3.metric("Claims", len(claims) if claims else 0)
c4.metric("Contradictions", len(contradictions) if contradictions else 0)

tabs = st.tabs(["CEF Overview", "RCA Results", "Falsification Ledger", "Telemetry Preview"])

with tabs[0]:
    st.subheader("Continuous Epistemic State")
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("### Health Claims")
        if claims:
            st.table(claims[-10:]) # Show last 10
        else:
            st.info("No claims recorded.")
            
    with col_r:
        st.write("### Active Contradictions")
        if contradictions:
            for ct in contradictions[-5:]:
                st.error(f"**[{ct['severity']}] {ct['service']}**: {ct['description']}")
        else:
            st.success("No active contradictions detected.")

    st.write("### Recommended Probes")
    if analysis.get("probes"):
        for p in analysis["probes"]:
            st.info(f"**{p['action_id']}** on `{p['target']}` — {p['rationale']}")

with tabs[1]:
    final = analysis["final"]
    left, right = st.columns([2, 3])
    with left:
        st.subheader("Top-3 Hypotheses")
        for i, h in enumerate(final["top3"], 1):
            st.write(f"**{i}. {h['name']}** — `{h['confidence']:.2f}`")
        
        st.subheader("Forecasting")
        if analysis.get("forecasting"):
            f = analysis["forecasting"]
            st.metric("Verifiability Risk", f"{f.get('risk_score', 0.0)*100:.0f}%", 
                      delta=f.get("trend"), delta_color="inverse")
            st.caption(f"Horizon: {f.get('horizon')} (v{f.get('version')})")

    with right:
        st.subheader("MEPPs")
        for pack in final.get("mepp", []):
            with st.expander(f"{pack['hypothesis']} ({pack['confidence']:.2f})"):
                st.json(pack["minimal_evidence"])

with tabs[2]:
    st.subheader("Falsification Ledger")
    if ledger:
        st.dataframe(ledger, use_container_width=True)
    else:
        st.info("Ledger is empty.")

with tabs[3]:
    st.subheader("Telemetry Inventory")
    inv = final.get("inventory", {})
    st.json(inv)
