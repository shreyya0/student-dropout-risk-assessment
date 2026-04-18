"""
Page 2: Batch Cohort Analysis — Upload CSV, analyze an entire class.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import API_BASE_URL, FEATURE_MAP
from dashboard.components.theme import get_custom_css, gradient_divider, page_header, section_header

st.set_page_config(page_title="Batch Cohort Analysis", page_icon=":material/bar_chart:", layout="wide")
st.markdown(get_custom_css(), unsafe_allow_html=True)
st.markdown(page_header("bar_chart", "Batch Cohort Analysis", "Upload a CSV of student data to analyze dropout risk across an entire cohort"), unsafe_allow_html=True)
st.markdown(gradient_divider(), unsafe_allow_html=True)

TIER_COLORS = {"Low": "#22C55E", "Medium": "#EAB308", "High": "#F97316", "Critical": "#DC2626"}
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#e2e8f0", size=12),
    xaxis=dict(gridcolor="rgba(51,65,85,0.3)", zerolinecolor="rgba(51,65,85,0.3)"),
    yaxis=dict(gridcolor="rgba(51,65,85,0.3)", zerolinecolor="rgba(51,65,85,0.3)"),
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(font=dict(size=11)),
)


def map_csv_columns(df: pd.DataFrame) -> list[dict]:
    reverse_map = {v: k for k, v in FEATURE_MAP.items()}
    students = []
    for _, row in df.iterrows():
        student = {}
        for col in df.columns:
            if col in FEATURE_MAP:
                student[col] = row[col]
            elif col in reverse_map:
                student[reverse_map[col]] = row[col]
        students.append(student)
    return students


# ── Upload ──
col_up, col_dl = st.columns([3, 1], gap="large")

with col_up:
    uploaded_file = st.file_uploader("Upload Student Data (CSV)", type=["csv"],
                                     help="CSV with student features matching the model's expected columns.")

with col_dl:
    sample_path = Path(__file__).resolve().parent.parent.parent / "data" / "sample_students.csv"
    if sample_path.exists():
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        csv_data = pd.read_csv(sample_path).to_csv(index=False)
        st.download_button("Download Template", csv_data, "sample_students.csv", "text/csv", icon=":material/download:",
                           use_container_width=True)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin:8px 0 16px 0;">
        <span class="material-symbols-rounded" style="color:#22c55e;font-size:1.2rem;">check_circle</span>
        <span style="color:#e2e8f0;font-weight:600;">{len(df)} students</span>
        <span style="color:#64748b;">•</span>
        <span style="color:#94a3b8;">{len(df.columns)} features</span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Preview Data", icon=":material/visibility:", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)

    if st.button("Analyze Cohort", icon=":material/rocket_launch:", type="primary", use_container_width=True):
        with st.spinner(f"Analyzing {len(df)} students..."):
            try:
                students = map_csv_columns(df)
                res = requests.post(f"{API_BASE_URL}/predict/batch", json={"students": students}, timeout=120)

                if res.status_code == 200:
                    data = res.json()
                    predictions = data["predictions"]
                    summary = data["summary"]

                    results_df = df.copy()
                    results_df["risk_score"] = [p["risk_score"] for p in predictions]
                    results_df["risk_tier"] = [p["risk_tier"]["tier"] for p in predictions]

                    st.markdown(gradient_divider(), unsafe_allow_html=True)

                    # ── Summary Metrics ──
                    st.markdown(section_header("trending_up", "Cohort Summary"), unsafe_allow_html=True)
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("Students", data["total"])
                    m2.metric("Avg Risk", f"{summary['avg_risk']:.1%}")
                    m3.metric("Median Risk", f"{summary['median_risk']:.1%}")
                    m4.metric("High Risk %", f"{summary['pct_high_risk']:.1%}")
                    m5.metric("Std Dev", f"{summary['std_risk']:.3f}")

                    st.markdown(gradient_divider(), unsafe_allow_html=True)

                    # ── Charts ──
                    tab1, tab2, tab3 = st.tabs(["Distribution", "Scatter", "Tiers"])

                    with tab1:
                        fig = px.histogram(results_df, x="risk_score", nbins=30, color="risk_tier",
                                           color_discrete_map=TIER_COLORS, marginal="box",
                                           title="Risk Score Distribution")
                        fig.update_layout(**CHART_LAYOUT, height=420)
                        st.plotly_chart(fig, use_container_width=True)

                    with tab2:
                        grade_col = None
                        for c in ["Curricular units 2nd sem (grade)", "s2_grade", "avg_grade"]:
                            if c in results_df.columns:
                                grade_col = c
                                break
                        if grade_col:
                            fig = px.scatter(results_df, x=grade_col, y="risk_score", color="risk_tier",
                                             color_discrete_map=TIER_COLORS, size="risk_score",
                                             title="Risk vs Academic Performance", opacity=0.7)
                            fig.update_layout(**CHART_LAYOUT, height=420)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No grade column found for scatter plot.")

                    with tab3:
                        tier_dist = summary.get("tier_distribution", {})
                        if tier_dist:
                            fig = px.pie(names=list(tier_dist.keys()), values=list(tier_dist.values()),
                                         color=list(tier_dist.keys()), color_discrete_map=TIER_COLORS,
                                         title="Risk Tier Distribution", hole=0.45)
                            fig.update_layout(**CHART_LAYOUT, height=420)
                            fig.update_traces(textinfo="label+percent", textfont_size=13)
                            st.plotly_chart(fig, use_container_width=True)

                    # ── Table ──
                    st.markdown(gradient_divider(), unsafe_allow_html=True)
                    st.markdown(section_header("list_alt", "Full Results"), unsafe_allow_html=True)
                    display_df = results_df[["risk_score", "risk_tier"]].sort_values("risk_score", ascending=False)
                    st.dataframe(display_df, use_container_width=True, height=350)
                    st.download_button("Download Results", results_df.to_csv(index=False),
                                       "cohort_risk_results.csv", "text/csv", icon=":material/download:", use_container_width=True)
                else:
                    st.error(f"API Error: {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the API. Run: `python -m api.main`")
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.markdown("""
    <div style="text-align:center; padding:80px 20px; color:#475569;">
        <span class="material-symbols-rounded" style="font-size:3.5rem; margin-bottom:16px; opacity:0.6;">bar_chart</span>
        <div style="font-size:1.1rem; font-weight:500; color:#64748b; margin-bottom:6px;">
            Upload a CSV file to analyze your cohort</div>
        <div style="font-size:0.9rem; color:#475569;">Or download the sample template to get started</div>
    </div>
    """, unsafe_allow_html=True)
