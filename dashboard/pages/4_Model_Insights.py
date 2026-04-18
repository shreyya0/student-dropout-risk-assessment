"""
Page 4: Model Insights — Performance metrics, feature importance, and comparison.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import API_BASE_URL, TRAINING_METRICS_PATH, MODEL_COMPARISON_PATH
from dashboard.components.theme import get_custom_css, gradient_divider, page_header, section_header
from dashboard.components.shap_chart import create_global_importance_chart

st.set_page_config(page_title="Model Insights", page_icon=":material/science:", layout="wide")
st.markdown(get_custom_css(), unsafe_allow_html=True)
st.markdown(page_header("science", "Model Insights", "Performance metrics, feature importance, and training analytics"), unsafe_allow_html=True)
st.markdown(gradient_divider(), unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#e2e8f0", size=12),
    margin=dict(l=40, r=40, t=50, b=40),
)

MODEL_COLORS = {"RandomForest": "#3b82f6", "XGBoost": "#8b5cf6", "GradientBoosting": "#f97316"}

# ── Load metrics ──
training_metrics, model_comparison = None, None
if TRAINING_METRICS_PATH.exists():
    with open(TRAINING_METRICS_PATH) as f:
        training_metrics = json.load(f)
if MODEL_COMPARISON_PATH.exists():
    with open(MODEL_COMPARISON_PATH) as f:
        model_comparison = json.load(f)

# ── Tabs ──
tab1, tab2, tab3, tab4 = st.tabs(["Model Comparison", "Feature Importance", "Confusion Matrix", "History"])

with tab1:
    st.markdown(section_header("emoji_events", "Model Comparison"), unsafe_allow_html=True)

    if model_comparison:
        # Table
        comp_data = []
        for name, m in model_comparison.items():
            comp_data.append({
                "Model": name,
                "Accuracy": f"{m['accuracy']:.4f}",
                "F1": f"{m['f1_score']:.4f}",
                "Precision": f"{m['precision']:.4f}",
                "Recall": f"{m['recall']:.4f}",
                "AUC": f"{m['roc_auc']:.4f}",
                "CV F1": f"{m['cv_f1_mean']:.4f} ± {m['cv_f1_std']:.4f}",
                "Time (s)": f"{m['train_time_seconds']:.0f}",
            })
        st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

        # Bar chart
        metrics_list = ["accuracy", "f1_score", "precision", "recall", "roc_auc"]
        fig = go.Figure()
        for name, m in model_comparison.items():
            fig.add_trace(go.Bar(
                name=name, x=[x.replace("_", " ").title() for x in metrics_list],
                y=[m[k] for k in metrics_list],
                marker_color=MODEL_COLORS.get(name, "#64748b"),
                text=[f"{m[k]:.3f}" for k in metrics_list],
                textposition="auto", textfont=dict(color="white", size=11, family="Inter"),
            ))
        fig.update_layout(**CHART_LAYOUT, barmode="group", height=420,
                          yaxis=dict(range=[0, 1], gridcolor="rgba(51,65,85,0.3)"),
                          legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

        if training_metrics and "best_model" in training_metrics:
            st.success(f"**Best Model**: {training_metrics['best_model']} — selected by F1 score", icon=":material/emoji_events:")

        # CV box plot
        st.markdown(gradient_divider(), unsafe_allow_html=True)
        st.markdown(section_header("inventory_2", "Cross-Validation Scores"), unsafe_allow_html=True)
        cv_data = []
        for name in model_comparison:
            if training_metrics and name in training_metrics:
                for score in training_metrics[name].get("cv_scores", []):
                    cv_data.append({"Model": name, "F1 Score": score})
        if cv_data:
            fig_cv = px.box(pd.DataFrame(cv_data), x="Model", y="F1 Score", color="Model",
                            color_discrete_map=MODEL_COLORS)
            fig_cv.update_layout(**CHART_LAYOUT, height=380, showlegend=False,
                                 yaxis=dict(gridcolor="rgba(51,65,85,0.3)"))
            st.plotly_chart(fig_cv, use_container_width=True)
    else:
        st.warning("No training metrics found. Run: `python -m models.train_pipeline`")

    # Model info from API
    st.markdown(gradient_divider(), unsafe_allow_html=True)
    st.markdown(section_header("build", "Active Model"), unsafe_allow_html=True)
    try:
        res = requests.get(f"{API_BASE_URL}/analytics/model-info", timeout=10)
        if res.status_code == 200:
            info = res.json()
            m1, m2, m3 = st.columns(3)
            m1.metric("Type", info["model_type"])
            m2.metric("Features", info["n_features"])
            m3.metric("Trained", (info.get("trained_at") or "Unknown")[:10])
    except Exception:
        st.caption("Start the API to see live model info.")


with tab2:
    st.markdown(section_header("star", "Global Feature Importance (SHAP)"), unsafe_allow_html=True)
    try:
        res = requests.get(f"{API_BASE_URL}/explain/global-importance", timeout=15)
        if res.status_code == 200:
            importance = res.json()["feature_importance"]
            fig_imp = create_global_importance_chart(importance, top_n=20)
            st.plotly_chart(fig_imp, use_container_width=True)
            with st.expander("Full Table", icon=":material/list_alt:"):
                imp_df = pd.DataFrame(importance).rename(columns={"display_name": "Feature", "importance": "Importance"})
                st.dataframe(imp_df[["Feature", "Importance"]], use_container_width=True, hide_index=True)
        else:
            st.warning("Could not load feature importance.")
    except requests.exceptions.ConnectionError:
        st.warning("Start the API to see SHAP feature importance.")


with tab3:
    st.markdown(section_header("trending_up", "Confusion Matrix"), unsafe_allow_html=True)
    if training_metrics and "best_model" in training_metrics:
        best = training_metrics["best_model"]
        if best in training_metrics:
            cm = training_metrics[best].get("confusion_matrix")
            if cm:
                fig_cm = px.imshow(
                    np.array(cm), labels=dict(x="Predicted", y="Actual", color="Count"),
                    x=["Safe (0)", "At Risk (1)"], y=["Safe (0)", "At Risk (1)"],
                    color_continuous_scale=[[0, "#0a0f1a"], [0.5, "#6366f1"], [1, "#c084fc"]],
                    text_auto=True, title=f"Confusion Matrix — {best}")
                fig_cm.update_layout(**CHART_LAYOUT, height=400)
                st.plotly_chart(fig_cm, use_container_width=True)

            report = training_metrics[best].get("classification_report", {})
            if report:
                st.markdown(gradient_divider(), unsafe_allow_html=True)
                st.markdown(section_header("list_alt", "Classification Report"), unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(report).transpose().round(4), use_container_width=True)
    else:
        st.warning("Run the training pipeline to see confusion matrix.")


with tab4:
    st.markdown(section_header("history", "Prediction History"), unsafe_allow_html=True)
    try:
        cf1, cf2, cf3 = st.columns(3)
        with cf1:
            hist_limit = st.number_input("Limit", 10, 500, 50, key="hl")
        with cf2:
            hist_tier = st.selectbox("Tier", [None, "Critical", "High", "Medium", "Low"], key="ht")
        with cf3:
            hist_type = st.selectbox("Type", [None, "single", "batch", "simulation"], key="hty")

        params = {"limit": hist_limit}
        if hist_tier: params["risk_tier"] = hist_tier
        if hist_type: params["prediction_type"] = hist_type

        res = requests.get(f"{API_BASE_URL}/analytics/history", params=params, timeout=10)
        if res.status_code == 200:
            history = res.json()
            if history["predictions"]:
                hist_df = pd.DataFrame(history["predictions"])
                cols = [c for c in ["id", "timestamp", "risk_score", "risk_tier", "prediction_type"] if c in hist_df.columns]
                st.dataframe(hist_df[cols], use_container_width=True, height=350)

                res_sum = requests.get(f"{API_BASE_URL}/analytics/summary", timeout=10)
                if res_sum.status_code == 200:
                    s = res_sum.json()
                    s1, s2, s3 = st.columns(3)
                    s1.metric("Total Predictions", s["total_predictions"])
                    s2.metric("Avg Risk", f"{s['avg_risk_score']:.1%}")
                    s3.metric("Recent Avg", f"{s.get('recent_avg_risk', 0):.1%}")
            else:
                st.info("No predictions logged yet.")
    except requests.exceptions.ConnectionError:
        st.warning("Start the API to see prediction history.")
