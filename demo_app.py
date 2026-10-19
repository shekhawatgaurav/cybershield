"""CyberShield demo-only frontend, safe to publish. Start: streamlit run demo_app.py"""
from __future__ import annotations

import streamlit as st
from cybershield.scanner import demo_result
from cybershield.reports import to_html, to_json

st.set_page_config(page_title="CyberShield | Live Portfolio Demo", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: #090f1c; color: #e9f0fb;}
[data-testid="stHeader"] {background: #090f1c;}
[data-testid="stSidebar"] {background: #101b2c; border-right: 1px solid #26384f;}
h1,h2,h3 {letter-spacing: -.035em;}
.hero-title {font-size: 42px; font-weight: 800; letter-spacing: -.05em; margin-bottom: 3px;}
.eyebrow {color:#65dfc7;letter-spacing:.15em;font-size:12px;font-weight:800;margin-top:22px;}
.subtitle {color: #9db0c6; margin: 0 0 30px;}
.tile {background:#142137; border:1px solid #2a4059; border-radius:14px; padding:19px; min-height:110px;}
.tile-label {color:#a0b6cc; font-size:12px; text-transform:uppercase; letter-spacing:.08em;}
.tile-value {color:#edf5ff; font-weight:850; font-size:31px; line-height:1.5;}
.notice {background:#2e2715; border:1px solid #6d5427; border-radius:10px; color:#f6d28b; padding:13px; margin-bottom:20px;}
[data-testid="stForm"] {border:1px solid #284157; background:#101b2c; border-radius:16px; padding:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">◈ CYBERSHIELD / SECURITY INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Website Security Auditor</div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Interactive portfolio demo using simulated web security findings. No website is contacted.</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("🛡️ CyberShield")
    st.caption("Version 1.0 · Educational security project")
    st.divider()
    st.markdown("**Audit scope**")
    st.write("✅ Passive HTTP response checks")
    st.write("✅ One optional benign Origin probe")
    st.write("✅ Local JSON/HTML report exports")
    st.write("⛔ No exploitation, fuzzing, login attempts or crawling")
    st.divider()
    st.caption("Public demo only: no scanning, outgoing requests, user URLs, or real vulnerabilities verified.")


st.warning("LIVE PORTFOLIO DEMO — This public dashboard uses simulated data only. No website scanning or network requests are available here.")
if st.button("↻ Reload simulated findings", type="primary") or "result" not in st.session_state:
    st.session_state["result"] = demo_result()

result = st.session_state.get("result")
if result:
    st.divider()
    if result.demo:
        st.markdown('<div class="notice">DEMO MODE — All findings below are simulated for demonstration. No real website was scanned.</div>', unsafe_allow_html=True)
    st.subheader("Audit overview")
    metrics = [("Configuration score", f"{result.score} / 100"),
        ("Indicative grade", result.grade),
        ("Review needed", str(sum(f.status == "WARN" for f in result.findings))),
        ("Checks completed", str(len(result.findings)))]
    cols = st.columns(4)
    for col, (caption, value) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="tile"><div class="tile-label">{caption}</div><div class="tile-value">{value}</div></div>', unsafe_allow_html=True)
    st.caption(f"URL: {result.final_url}  ·  HTTP: {result.http_status}  ·  {result.elapsed_ms} ms  ·  {result.scanned_at}")
    st.progress(result.score / 100)

    st.subheader("Observations")
    status_filter = st.segmented_control("Display", options=["All", "Warnings", "Passed", "Informational"], default="All")
    active = {"All": None, "Warnings": "WARN", "Passed": "PASS", "Informational": "INFO"}.get(status_filter)
    for item in result.findings:
        if active and item.status != active:
            continue
        symbol = {"WARN": "🟠", "PASS": "🟢", "INFO": "🔵"}[item.status]
        with st.expander(f"{symbol} {item.title}   ·   {item.status}{' / '+item.severity if item.status == 'WARN' else ''}", expanded=item.status == "WARN"):
            st.write(item.detail)
            st.markdown(f"**Recommendation:** {item.recommendation}")
            if item.evidence:
                st.caption(item.evidence)

    st.subheader("Export your results")
    dl_json, dl_html = st.columns(2)
    with dl_json:
        st.download_button("⬇ Download JSON report", to_json(result), file_name="cybershield-audit.json",
            mime="application/json", use_container_width=True)
    with dl_html:
        st.download_button("⬇ Download HTML report", to_html(result), file_name="cybershield-audit.html",
            mime="text/html", use_container_width=True)
    st.info("This checks a single observed page's response configuration. A high score does not guarantee security.")
else:
    st.info("Start with **Explore offline demo** to view the dashboard without contacting any external website.")
