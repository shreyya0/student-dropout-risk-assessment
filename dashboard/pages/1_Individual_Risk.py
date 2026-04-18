"""
Page 1: Individual Risk Assessment — Deep dive per student.
"""

import sys
from pathlib import Path

import streamlit as st
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import API_BASE_URL
from dashboard.components.theme import get_custom_css, risk_badge_html, gradient_divider, page_header, section_header
from dashboard.components.risk_gauge import create_risk_gauge
from dashboard.components.shap_chart import create_shap_waterfall, render_risk_factor_cards

st.set_page_config(page_title="Individual Risk Assessment", page_icon=":material/search:", layout="wide")
st.markdown(get_custom_css(), unsafe_allow_html=True)
st.markdown(page_header("search", "Individual Risk Assessment", "Deep-dive analysis with SHAP explainability for a single student"), unsafe_allow_html=True)
st.markdown(gradient_divider(), unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### :material/person: Student Profile")
    st.markdown("---")

    st.markdown("**:material/book: Semester 1**")
    s1_enrolled = st.number_input("S1 Enrolled", 0, 30, 6, key="s1e")
    s1_approved = st.number_input("S1 Approved", 0, 30, 5, key="s1a")
    s1_grade = st.slider("S1 Grade", 0.0, 20.0, 12.0, 0.5, key="s1g")
    s1_evaluations = st.number_input("S1 Evaluations", 0, 50, 6, key="s1ev")

    st.markdown("**:material/book: Semester 2**")
    s2_enrolled = st.number_input("S2 Enrolled", 0, 30, 6, key="s2e")
    s2_approved = st.number_input("S2 Approved", 0, 30, 5, key="s2a")
    s2_grade = st.slider("S2 Grade", 0.0, 20.0, 12.0, 0.5, key="s2g")
    s2_evaluations = st.number_input("S2 Evaluations", 0, 50, 6, key="s2ev")

    st.markdown("---")
    st.markdown("**:material/payments: Financial**")
    tuition = st.selectbox("Tuition", [1, 0], format_func=lambda x: "Paid" if x else "Unpaid", key="tui")
    scholarship = st.selectbox("Scholarship", [0, 1], format_func=lambda x: "Yes" if x else "No", key="sch")
    debtor = st.selectbox("Debtor", [0, 1], format_func=lambda x: "Yes" if x else "No", key="dbt")

    st.markdown("---")
    st.markdown("**:material/badge: Profile**")
    age = st.slider("Age", 17, 60, 20, key="age")
    gender = st.selectbox("Gender", [1, 0], format_func=lambda x: "Male" if x else "Female", key="gen")
    displaced = st.selectbox("Displaced", [0, 1], format_func=lambda x: "Yes" if x else "No", key="dsp")
    international = st.selectbox("International", [0, 1], format_func=lambda x: "Yes" if x else "No", key="intl")
    admission_grade = st.slider("Admission Grade", 0.0, 200.0, 127.0, 1.0, key="adm")
    prev_qual_grade = st.slider("Prev. Qualification Grade", 0.0, 200.0, 130.0, 1.0, key="pvg")

# ── Main ──
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    run_predict = st.button("Predict Risk", icon=":material/rocket_launch:", use_container_width=True, type="primary")
with c2:
    run_explain = st.button("SHAP Explain", icon=":material/science:", use_container_width=True)

if run_predict or run_explain:
    payload = {
        "tuition_up_to_date": tuition, "scholarship_holder": scholarship,
        "age_at_enrollment": age, "gender": gender, "displaced": displaced,
        "international": international, "debtor": debtor,
        "admission_grade": admission_grade, "prev_qualification_grade": prev_qual_grade,
        "s1_enrolled": s1_enrolled, "s1_approved": s1_approved,
        "s1_grade": s1_grade, "s1_evaluations": s1_evaluations,
        "s2_enrolled": s2_enrolled, "s2_approved": s2_approved,
        "s2_grade": s2_grade, "s2_evaluations": s2_evaluations,
    }

    with st.spinner("Analyzing..."):
        try:
            endpoint = "/explain/" if run_explain else "/predict/"
            res = requests.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=30)

            if res.status_code == 200:
                data = res.json()
                risk_score = data["risk_score"]
                tier = data["risk_tier"]

                st.markdown(gradient_divider(), unsafe_allow_html=True)

                # ── Gauge + Summary ──
                col_gauge, col_info = st.columns([1, 1], gap="large")

                with col_gauge:
                    fig = create_risk_gauge(risk_score)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                with col_info:
                    st.markdown(risk_badge_html(tier["tier"], tier["emoji"]), unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:2rem;font-weight:800;color:#f1f5f9;margin:8px 0 4px 0;'>{risk_score:.1%}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color:#94a3b8;font-size:0.9rem;margin-bottom:16px;'>{tier['action']}</div>", unsafe_allow_html=True)

                    # Academic summary cards
                    grade_trend = s2_grade - s1_grade
                    m1, m2, m3 = st.columns(3)
                    m1.metric("S1 Grade", f"{s1_grade:.1f}")
                    m2.metric("S2 Grade", f"{s2_grade:.1f}")
                    m3.metric("Trend", f"{grade_trend:+.1f}", delta=f"{grade_trend:+.1f}")

                    m4, m5, m6 = st.columns(3)
                    m4.metric("S1 Pass", f"{s1_approved}/{s1_enrolled}")
                    m5.metric("S2 Pass", f"{s2_approved}/{s2_enrolled}")
                    m6.metric("Tuition", "Paid" if tuition else "Due")

                # ── SHAP (if explain) ──
                if run_explain and "risk_factors" in data:
                    st.markdown(gradient_divider(), unsafe_allow_html=True)
                    st.markdown(section_header("psychology", "AI Explanation (SHAP)"), unsafe_allow_html=True)

                    # Natural language
                    st.info(f"**Insights**: {data['natural_language_summary']}")

                    # Waterfall
                    fig_shap = create_shap_waterfall(data, top_n=10)
                    st.plotly_chart(fig_shap, use_container_width=True, config={"displayModeBar": False})

                    # Factor cards
                    st.markdown(gradient_divider(), unsafe_allow_html=True)
                    render_risk_factor_cards(
                        data.get("risk_factors", []),
                        data.get("protective_factors", []),
                    )

            else:
                st.error(f"API Error ({res.status_code}): {res.text}")

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the API. Run: `python -m api.main`")
        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.markdown("""
    <div style="text-align:center; padding:80px 20px; color:#475569;">
        <span class="material-symbols-rounded" style="font-size:3.5rem; margin-bottom:16px; opacity:0.6;">school</span>
        <div style="font-size:1.1rem; font-weight:500; color:#64748b; margin-bottom:6px;">
            Configure a student profile in the sidebar</div>
        <div style="font-size:0.9rem; color:#475569;">
            Then click <strong style="color:#818cf8;">Predict Risk</strong> or
            <strong style="color:#a78bfa;">SHAP Explain</strong></div>
    </div>
    """, unsafe_allow_html=True)
