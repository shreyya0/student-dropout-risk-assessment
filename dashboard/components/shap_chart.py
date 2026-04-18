"""
SHAP Chart Components — Waterfall and bar charts for SHAP explanations.
"""

import plotly.graph_objects as go


def create_shap_waterfall(explanation: dict, top_n: int = 10) -> go.Figure:
    """
    Create a SHAP waterfall chart showing feature contributions.

    Args:
        explanation: Dict from RiskExplainer.explain() with all_contributions.
        top_n: Number of top features to show.

    Returns:
        Plotly Figure with horizontal waterfall chart.
    """
    contributions = explanation.get("all_contributions", [])[:top_n]
    contributions.reverse()  # Bottom to top

    names = [c["display_name"] for c in contributions]
    values = [c["shap_value"] for c in contributions]
    colors = ["#DC2626" if v > 0 else "#22C55E" for v in values]

    fig = go.Figure(
        go.Bar(
            y=names,
            x=values,
            orientation="h",
            marker_color=colors,
            marker_line_width=0,
            text=[f"{v:+.3f}" for v in values],
            textposition="auto",
            textfont={"color": "white", "size": 11, "family": "Inter"},
        )
    )

    fig.add_vline(x=0, line_dash="dash", line_color="#475569", line_width=1)

    fig.update_layout(
        title={
            "text": "Feature Impact on Risk (SHAP Values)",
            "font": {"size": 16, "color": "#e2e8f0", "family": "Inter"},
            "x": 0.5,
        },
        xaxis_title="SHAP Value (← Protective | Risk →)",
        xaxis={
            "title": {"font": {"color": "#94a3b8", "size": 12}},
            "tickfont": {"color": "#64748b"},
            "gridcolor": "rgba(51, 65, 85, 0.5)",
            "zerolinecolor": "#475569",
        },
        yaxis={
            "tickfont": {"color": "#e2e8f0", "size": 11, "family": "Inter"},
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=max(350, top_n * 38),
        margin=dict(l=180, r=40, t=60, b=50),
        showlegend=False,
    )

    return fig


def create_global_importance_chart(importance_data: list[dict], top_n: int = 15) -> go.Figure:
    """
    Create a horizontal bar chart of global feature importance.

    Args:
        importance_data: List of {feature, display_name, importance} dicts.
        top_n: Number of top features to show.

    Returns:
        Plotly Figure.
    """
    data = importance_data[:top_n]
    data.reverse()

    names = [d["display_name"] for d in data]
    values = [d["importance"] for d in data]

    # Gradient colors from blue to purple
    n = len(values)
    colors = [
        f"rgb({int(14 + (99-14)*i/max(n-1,1))}, {int(165 - (165-102)*i/max(n-1,1))}, {int(233 + (241-233)*i/max(n-1,1))})"
        for i in range(n)
    ]

    fig = go.Figure(
        go.Bar(
            y=names,
            x=values,
            orientation="h",
            marker_color=colors,
            marker_line_width=0,
            text=[f"{v:.4f}" for v in values],
            textposition="auto",
            textfont={"color": "white", "size": 11, "family": "Inter"},
        )
    )

    fig.update_layout(
        title={
            "text": "Global Feature Importance (SHAP)",
            "font": {"size": 16, "color": "#e2e8f0", "family": "Inter"},
            "x": 0.5,
        },
        xaxis_title="Mean |SHAP Value|",
        xaxis={
            "title": {"font": {"color": "#94a3b8"}},
            "tickfont": {"color": "#64748b"},
            "gridcolor": "rgba(51, 65, 85, 0.5)",
        },
        yaxis={
            "tickfont": {"color": "#e2e8f0", "size": 11, "family": "Inter"},
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=max(400, top_n * 35),
        margin=dict(l=200, r=40, t=60, b=50),
        showlegend=False,
    )

    return fig


def render_risk_factor_cards(risk_factors: list[dict], protective_factors: list[dict]):
    """Render risk and protective factor cards using Streamlit native layout."""
    import streamlit as st

    if risk_factors:
        st.markdown("##### :material/warning: Risk Factors")
        cols = st.columns(min(len(risk_factors[:5]), 3))
        for i, factor in enumerate(risk_factors[:5]):
            with cols[i % 3]:
                st.markdown(
                    f'<div style="background:rgba(220,38,38,0.1);border:1px solid rgba(220,38,38,0.3);'
                    f'border-radius:12px;padding:16px;margin-bottom:8px;">'
                    f'<div style="color:#fca5a5;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;"><span class="material-symbols-rounded" style="font-size:1rem;vertical-align:bottom;margin-right:2px;">warning</span> Risk Factor</div>'
                    f'<div style="color:#f1f5f9;font-weight:600;font-size:0.95rem;">{factor["display_name"]}</div>'
                    f'<div style="color:#dc2626;font-size:0.85rem;margin-top:4px;">Impact: {factor["abs_impact"]:.3f}</div>'
                    f'<div style="color:#94a3b8;font-size:0.8rem;">Value: {factor["feature_value"]:.2f}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    if protective_factors:
        st.markdown("##### :material/security: Protective Factors")
        cols = st.columns(min(len(protective_factors[:5]), 3))
        for i, factor in enumerate(protective_factors[:5]):
            with cols[i % 3]:
                st.markdown(
                    f'<div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);'
                    f'border-radius:12px;padding:16px;margin-bottom:8px;">'
                    f'<div style="color:#86efac;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;"><span class="material-symbols-rounded" style="font-size:1rem;vertical-align:bottom;margin-right:2px;">security</span> Protective</div>'
                    f'<div style="color:#f1f5f9;font-weight:600;font-size:0.95rem;">{factor["display_name"]}</div>'
                    f'<div style="color:#22c55e;font-size:0.85rem;margin-top:4px;">Impact: {factor["abs_impact"]:.3f}</div>'
                    f'<div style="color:#94a3b8;font-size:0.8rem;">Value: {factor["feature_value"]:.2f}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

