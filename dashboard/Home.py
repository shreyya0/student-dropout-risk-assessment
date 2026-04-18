"""
Student Dropout Risk Assessment Dashboard — Main Application.

Premium multi-page Streamlit dashboard with glassmorphism design.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dashboard.components.theme import get_custom_css, gradient_divider, glass_card, page_header

st.set_page_config(
    page_title="Student Dropout Risk Assessment",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Hero ──
st.markdown("""
<div style="text-align:center; padding:50px 20px 30px 20px;">
    <div style="font-size:3.2rem; font-weight:900;
                background:linear-gradient(135deg, #60a5fa 0%, #818cf8 40%, #c084fc 70%, #e879f9 100%);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                letter-spacing:-0.04em; line-height:1.15; margin-bottom:12px;">
        Student Dropout Risk Assessment
    </div>
    <div style="color:#64748b; font-size:1.05rem; font-weight:400; max-width:700px; margin:0 auto 20px auto; line-height:1.6;">
        An advanced predictive analytics platform leveraging machine learning to proactively identify student risk profiles and prescribe targeted interventions for academic retention.
    </div>
    <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
        <span style="display:inline-flex;align-items:center;gap:6px;background:rgba(99,102,241,0.1);
                     border:1px solid rgba(99,102,241,0.15);border-radius:100px;padding:6px 16px;
                     font-size:0.78rem;color:#a5b4fc;font-weight:500;">
            <span style="width:6px;height:6px;border-radius:50%;background:#6366f1;"></span> 4,424 Students Trained
        </span>
        <span style="display:inline-flex;align-items:center;gap:6px;background:rgba(139,92,246,0.1);
                     border:1px solid rgba(139,92,246,0.15);border-radius:100px;padding:6px 16px;
                     font-size:0.78rem;color:#c4b5fd;font-weight:500;">
            <span style="width:6px;height:6px;border-radius:50%;background:#8b5cf6;"></span> 43 Features
        </span>
        <span style="display:inline-flex;align-items:center;gap:6px;background:rgba(192,132,252,0.1);
                     border:1px solid rgba(192,132,252,0.15);border-radius:100px;padding:6px 16px;
                     font-size:0.78rem;color:#d8b4fe;font-weight:500;">
            <span style="width:6px;height:6px;border-radius:50%;background:#c084fc;"></span> 93.8% ROC AUC
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(gradient_divider(), unsafe_allow_html=True)

# ── Navigation Cards ──
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown(glass_card(
        "search", "Individual Risk Assessment",
        "Deep-dive analysis for a single student with SHAP explainability. "
        "Understand exactly why a student is at risk and what factors are protective.",
        "96,165,250"
    ), unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(glass_card(
        "explore", "What-If Simulator",
        "Explore intervention scenarios and find the optimal path to student success. "
        "Test tuition payments, scholarships, and academic improvements.",
        "139,92,246"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(glass_card(
        "bar_chart", "Batch Cohort Analysis",
        "Upload a CSV of student data and analyze an entire class at once. "
        "Get risk distributions, scatter plots, and downloadable results.",
        "34,197,94"
    ), unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(glass_card(
        "science", "Model Insights",
        "Explore model performance, cross-validation results, confusion matrix, "
        "feature importance rankings, and prediction history.",
        "249,115,22"
    ), unsafe_allow_html=True)

st.markdown(gradient_divider(), unsafe_allow_html=True)

# ── Tech Stack ──
st.markdown("""
<div style="text-align:center; padding:10px 0 30px 0;">
    <div style="display:flex; justify-content:center; gap:20px; flex-wrap:wrap; margin-bottom:16px;">
        <span style="color:#475569; font-size:0.8rem; font-weight:500; display:flex; align-items:center; gap:6px;">
            <span style="color:#818cf8;">●</span> Python
        </span>
        <span style="color:#475569; font-size:0.8rem; font-weight:500; display:flex; align-items:center; gap:6px;">
            <span style="color:#818cf8;">●</span> FastAPI
        </span>
        <span style="color:#475569; font-size:0.8rem; font-weight:500; display:flex; align-items:center; gap:6px;">
            <span style="color:#a78bfa;">●</span> XGBoost
        </span>
        <span style="color:#475569; font-size:0.8rem; font-weight:500; display:flex; align-items:center; gap:6px;">
            <span style="color:#a78bfa;">●</span> SHAP
        </span>
        <span style="color:#475569; font-size:0.8rem; font-weight:500; display:flex; align-items:center; gap:6px;">
            <span style="color:#c084fc;">●</span> Streamlit
        </span>
        <span style="color:#475569; font-size:0.8rem; font-weight:500; display:flex; align-items:center; gap:6px;">
            <span style="color:#c084fc;">●</span> Plotly
        </span>
        <span style="color:#475569; font-size:0.8rem; font-weight:500; display:flex; align-items:center; gap:6px;">
            <span style="color:#e879f9;">●</span> Docker
        </span>
    </div>
    <div style="color:#334155; font-size:0.78rem; font-weight:400;">
        Dataset: UCI ML Repository — Predict Students' Dropout and Academic Success (ID 697)
    </div>
    <div style="color:#334155; font-size:0.78rem; margin-top:8px;">
        Navigate to pages using the sidebar ←
    </div>
</div>
""", unsafe_allow_html=True)
