"""
Page 3: What-If Simulator — Multi-scenario intervention analysis.
"""

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import API_BASE_URL, SCENARIO_PRESETS
from dashboard.components.theme import get_custom_css, gradient_divider, page_header, section_header, risk_badge_html
from dashboard.components.risk_gauge import create_risk_gauge

st.set_page_config(page_title="What-If Simulator", page_icon=":material/explore:", layout="wide")
st.markdown(get_custom_css(), unsafe_allow_html=True)
st.markdown(page_header("explore", "What-If Simulator", "Explore intervention scenarios to find the best path to student success"), unsafe_allow_html=True)
st.markdown(gradient_divider(), unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### :material/person: Base Profile")
    st.markdown("---")
    s1_approved = st.number_input("S1 Approved", 0, 30, 5, key="ws1a")
    s1_grade = st.slider("S1 Grade", 0.0, 20.0, 12.0, 0.5, key="ws1g")
    s2_approved = st.number_input("S2 Approved", 0, 30, 3, key="ws2a")
    s2_grade = st.slider("S2 Grade", 0.0, 20.0, 9.0, 0.5, key="ws2g")
    st.markdown("---")
    tuition = st.selectbox("Tuition", [0, 1], format_func=lambda x: "Paid" if x else "Unpaid", key="wt")
    scholarship = st.selectbox("Scholarship", [0, 1], format_func=lambda x: "Yes" if x else "No", key="wsc")
    debtor = st.selectbox("Debtor", [0, 1], format_func=lambda x: "Yes" if x else "No", key="wd")
    age = st.slider("Age", 17, 60, 20, key="wa")
    admission_grade = st.slider("Admission Grade", 0.0, 200.0, 127.0, 1.0, key="wadm")

base_payload = {
    "s1_approved": s1_approved, "s1_grade": s1_grade,
    "s2_approved": s2_approved, "s2_grade": s2_grade,
    "tuition_up_to_date": tuition, "scholarship_holder": scholarship,
    "debtor": debtor, "age_at_enrollment": age, "admission_grade": admission_grade,
}

# ── Tabs ──
tab1, tab2, tab3 = st.tabs(["Custom Scenario", "Quick Presets", "Sensitivity Analysis"])

with tab1:
    st.markdown(section_header("tune", "Custom Intervention"), unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("**:material/book: Academic Changes**")
        sim_s2_approved = st.slider("Simulated S2 Approved", 0, 30, min(s2_approved + 2, 30), key="ss2a")
        sim_s2_grade = st.slider("Simulated S2 Grade", 0.0, 20.0, min(s2_grade + 3.0, 20.0), 0.5, key="ss2g")
        sim_s1_approved = st.slider("Simulated S1 Approved", 0, 30, s1_approved, key="ss1a")
        sim_s1_grade = st.slider("Simulated S1 Grade", 0.0, 20.0, s1_grade, 0.5, key="ss1g")

    with col2:
        st.markdown("**:material/payments: Financial Changes**")
        sim_tuition = st.selectbox("Simulated Tuition", [0, 1], index=1,
                                   format_func=lambda x: "Paid" if x else "Unpaid", key="st")
        sim_scholarship = st.selectbox("Simulated Scholarship", [0, 1], index=scholarship,
                                       format_func=lambda x: "Yes" if x else "No", key="ssc")
        sim_debtor = st.selectbox("Simulated Debtor", [0, 1], index=0,
                                  format_func=lambda x: "Yes" if x else "No", key="sd")

    if st.button("Run Simulation", icon=":material/explore:", type="primary", use_container_width=True):
        modifications = {}
        if sim_s2_approved != s2_approved: modifications["s2_approved"] = sim_s2_approved
        if sim_s2_grade != s2_grade: modifications["s2_grade"] = sim_s2_grade
        if sim_s1_approved != s1_approved: modifications["s1_approved"] = sim_s1_approved
        if sim_s1_grade != s1_grade: modifications["s1_grade"] = sim_s1_grade
        if sim_tuition != tuition: modifications["tuition_up_to_date"] = sim_tuition
        if sim_scholarship != scholarship: modifications["scholarship_holder"] = sim_scholarship
        if sim_debtor != debtor: modifications["debtor"] = sim_debtor

        if not modifications:
            st.warning("No changes made — adjust the sliders to simulate an intervention.")
        else:
            with st.spinner("Running simulation..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/simulate/",
                                        json={"student": base_payload, "modifications": modifications}, timeout=15)
                    if res.status_code == 200:
                        data = res.json()
                        current = data["current_risk_score"]
                        simulated = data["simulated_risk_score"]
                        improvement = data["improvement_potential"]

                        st.markdown(gradient_divider(), unsafe_allow_html=True)

                        # Gauges side by side
                        gc1, gc2 = st.columns(2, gap="large")
                        with gc1:
                            st.markdown(section_header("location_on", "Current State"), unsafe_allow_html=True)
                            st.plotly_chart(create_risk_gauge(current, "Current Risk"),
                                           use_container_width=True, config={"displayModeBar": False})
                            st.markdown(f"<div style='text-align:center'>{risk_badge_html(data['current_risk_tier']['tier'], data['current_risk_tier']['emoji'])}</div>",
                                        unsafe_allow_html=True)

                        with gc2:
                            st.markdown(section_header("ads_click", "After Intervention"), unsafe_allow_html=True)
                            st.plotly_chart(create_risk_gauge(simulated, "Simulated Risk"),
                                           use_container_width=True, config={"displayModeBar": False})
                            st.markdown(f"<div style='text-align:center'>{risk_badge_html(data['simulated_risk_tier']['tier'], data['simulated_risk_tier']['emoji'])}</div>",
                                        unsafe_allow_html=True)

                        # Result
                        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                        if improvement > 0:
                            st.success(f"✅ Risk reduced by **{improvement:.1%}** — this intervention is effective!")
                        elif improvement < 0:
                            st.error(f"⚠️ Risk increased by **{abs(improvement):.1%}** — this change is counterproductive.")
                        else:
                            st.info("No change in risk score.")

                        with st.expander("Changes Applied", icon=":material/list_alt:"):
                            for field, change in data["modifications_applied"].items():
                                st.markdown(f"- **{field}**: {change}")
                    else:
                        st.error(f"API Error: {res.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API.")

with tab2:
    st.markdown(section_header("bolt", "Quick Scenario Presets"), unsafe_allow_html=True)

    for preset_name, preset_mods in SCENARIO_PRESETS.items():
        with st.container():
            cp1, cp2 = st.columns([3, 1], gap="medium")
            with cp1:
                st.markdown(f"**{preset_name}**")
                st.caption(f"Changes: {preset_mods}")
            with cp2:
                if st.button("Run ▶", icon=":material/play_arrow:", key=f"p_{preset_name}", use_container_width=True):
                    with st.spinner(f"Running {preset_name}..."):
                        try:
                            res = requests.post(f"{API_BASE_URL}/simulate/",
                                                json={"student": base_payload, "modifications": preset_mods}, timeout=15)
                            if res.status_code == 200:
                                d = res.json()
                                rc1, rc2, rc3 = st.columns(3)
                                rc1.metric("Current", f"{d['current_risk_score']:.1%}")
                                rc2.metric("After", f"{d['simulated_risk_score']:.1%}")
                                rc3.metric("Improvement", f"{d['improvement_potential']:.1%}",
                                           delta=f"-{d['improvement_potential']:.1%}")
                        except Exception as e:
                            st.error(str(e))
            st.markdown("---")

with tab3:
    st.markdown(section_header("bar_chart", "Sensitivity Analysis"), unsafe_allow_html=True)
    st.markdown("<div style='color:#94a3b8;font-size:0.9rem;margin-bottom:16px;'>"
                "Discover which single change would help this student most.</div>", unsafe_allow_html=True)

    if st.button("Run Sensitivity Analysis", icon=":material/science:", type="primary", use_container_width=True, key="sens"):
        with st.spinner("Testing all interventions..."):
            try:
                res = requests.post(f"{API_BASE_URL}/simulate/sensitivity", json=base_payload, timeout=30)
                if res.status_code == 200:
                    data = res.json()
                    results = data["sensitivity_results"]
                    current = data["current_risk"]

                    st.metric("Current Risk Score", f"{current:.1%}")

                    if data["best_single_action"]:
                        best = data["best_single_action"]
                        st.success(f"🏆 **Best action**: {best['label']} ({best['change']}) — "
                                   f"reduces risk by **{best['improvement']:.1%}** "
                                   f"({best['improvement_pct']:.0f}% relative)")

                    positive = [r for r in results if r["improvement"] > 0][:15]
                    if positive:
                        max_imp = max(r["improvement"] for r in positive)
                        fig = go.Figure(go.Bar(
                            y=[r["change"] for r in positive],
                            x=[r["improvement"] for r in positive],
                            orientation="h",
                            marker_color=[f"rgba(99,102,241,{0.3 + 0.7*r['improvement']/max_imp})" for r in positive],
                            text=[f"-{r['improvement']:.1%}" for r in positive],
                            textposition="auto",
                            textfont=dict(color="white", family="Inter", size=11),
                        ))
                        fig.update_layout(
                            title="Risk Reduction by Intervention",
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter", color="#e2e8f0"),
                            xaxis=dict(gridcolor="rgba(51,65,85,0.3)", tickformat=".1%",
                                       title=dict(font=dict(color="#94a3b8"))),
                            yaxis=dict(tickfont=dict(size=11)),
                            height=max(380, len(positive) * 32),
                            margin=dict(l=180, r=40, t=50, b=40),
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"API Error: {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API.")
