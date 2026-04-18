"""
Risk Gauge Component — Premium animated Plotly gauge for risk visualization.
"""

import plotly.graph_objects as go


def create_risk_gauge(risk_score: float, title: str = "Dropout Risk Score") -> go.Figure:
    """Create a premium gauge chart with smooth gradient zones."""
    if risk_score >= 0.75:
        bar_color = "#DC2626"
        glow = "rgba(220,38,38,0.3)"
    elif risk_score >= 0.50:
        bar_color = "#F97316"
        glow = "rgba(249,115,22,0.3)"
    elif risk_score >= 0.25:
        bar_color = "#EAB308"
        glow = "rgba(234,179,8,0.3)"
    else:
        bar_color = "#22C55E"
        glow = "rgba(34,197,94,0.3)"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score * 100,
        number=dict(
            suffix="%",
            font=dict(size=52, color="#f1f5f9", family="Inter", weight=800),
        ),
        title=dict(
            text=title,
            font=dict(size=14, color="#64748b", family="Inter"),
        ),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickwidth=1,
                tickcolor="#1e293b",
                tickfont=dict(color="#475569", size=10),
                dtick=25,
            ),
            bar=dict(color=bar_color, thickness=0.7),
            bgcolor="#0f172a",
            borderwidth=0,
            steps=[
                dict(range=[0, 25], color="rgba(34,197,94,0.08)"),
                dict(range=[25, 50], color="rgba(234,179,8,0.08)"),
                dict(range=[50, 75], color="rgba(249,115,22,0.08)"),
                dict(range=[75, 100], color="rgba(220,38,38,0.08)"),
            ],
            threshold=dict(
                line=dict(color="#f1f5f9", width=2),
                thickness=0.75,
                value=risk_score * 100,
            ),
        ),
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        height=300,
        margin=dict(l=25, r=25, t=55, b=15),
    )

    return fig


def create_comparison_gauge(current: float, simulated: float) -> tuple[go.Figure, go.Figure]:
    """Create side-by-side gauges for current vs simulated risk."""
    return create_risk_gauge(current, "Current Risk"), create_risk_gauge(simulated, "Simulated Risk")
