"""
Dashboard Theme — Industry-grade dark mode styling for Streamlit.

Premium glassmorphism design with gradient accents, smooth animations,
and professional typography using Inter font family.
"""


def get_custom_css() -> str:
    """Return premium dark theme CSS for injection into Streamlit."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0');

        .material-symbols-rounded {
          font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
          vertical-align: middle;
        }

        /* ═══════════════════════════════════════════
           GLOBAL RESET & TYPOGRAPHY
           ═══════════════════════════════════════════ */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background: #0a0f1a !important;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.02em !important;
        }

        /* ═══════════════════════════════════════════
           SIDEBAR — Sleek dark panel
           ═══════════════════════════════════════════ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #070b14 0%, #0d1321 50%, #111827 100%) !important;
            border-right: 1px solid rgba(99, 102, 241, 0.08) !important;
        }

        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {
            background: linear-gradient(135deg, #60a5fa, #a78bfa) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            font-weight: 700 !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(99, 102, 241, 0.1) !important;
            margin: 12px 0 !important;
        }

        section[data-testid="stSidebar"] label {
            color: #94a3b8 !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
        }

        /* Sidebar inputs */
        section[data-testid="stSidebar"] .stNumberInput input,
        section[data-testid="stSidebar"] .stSelectbox > div > div {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(99, 102, 241, 0.15) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
        }

        /* ═══════════════════════════════════════════
           METRIC CARDS — Glassmorphism
           ═══════════════════════════════════════════ */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.7), rgba(30, 41, 59, 0.5)) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(99, 102, 241, 0.12) !important;
            border-radius: 16px !important;
            padding: 20px 24px !important;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255,255,255,0.03) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px) !important;
            border-color: rgba(99, 102, 241, 0.25) !important;
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.12), inset 0 1px 0 rgba(255,255,255,0.05) !important;
        }

        div[data-testid="stMetric"] label {
            color: #64748b !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            font-size: 0.7rem !important;
            letter-spacing: 0.08em !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-weight: 800 !important;
            font-size: 1.8rem !important;
            color: #f1f5f9 !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            font-weight: 600 !important;
            font-size: 0.8rem !important;
        }

        /* ═══════════════════════════════════════════
           BUTTONS — Gradient with glow
           ═══════════════════════════════════════════ */
        .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            padding: 12px 28px !important;
            font-size: 0.9rem !important;
            letter-spacing: 0.01em !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 28px rgba(99, 102, 241, 0.45) !important;
            filter: brightness(1.1) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
        }

        /* Primary button variant */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%) !important;
        }

        /* ═══════════════════════════════════════════
           TABS — Pill style
           ═══════════════════════════════════════════ */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            background: rgba(15, 23, 42, 0.5) !important;
            border-radius: 14px !important;
            padding: 4px !important;
            border: 1px solid rgba(99, 102, 241, 0.08) !important;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border-radius: 10px !important;
            color: #64748b !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            padding: 8px 20px !important;
            transition: all 0.2s ease !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #cbd5e1 !important;
            background: rgba(99, 102, 241, 0.08) !important;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
            color: white !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 12px rgba(99, 102, 241, 0.3) !important;
        }

        .stTabs [data-baseweb="tab-highlight"] {
            display: none !important;
        }

        .stTabs [data-baseweb="tab-border"] {
            display: none !important;
        }

        /* ═══════════════════════════════════════════
           EXPANDERS — Glass cards
           ═══════════════════════════════════════════ */
        div[data-testid="stExpander"] {
            border: 1px solid rgba(99, 102, 241, 0.1) !important;
            border-radius: 16px !important;
            background: rgba(15, 23, 42, 0.4) !important;
            backdrop-filter: blur(10px) !important;
            overflow: hidden !important;
        }

        div[data-testid="stExpander"] summary {
            font-weight: 600 !important;
            color: #e2e8f0 !important;
        }

        /* ═══════════════════════════════════════════
           ALERTS — Refined
           ═══════════════════════════════════════════ */
        .stAlert {
            border-radius: 14px !important;
            border: none !important;
            backdrop-filter: blur(10px) !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 14px !important;
        }

        /* ═══════════════════════════════════════════
           FILE UPLOADER
           ═══════════════════════════════════════════ */
        div[data-testid="stFileUploader"] {
            border: 2px dashed rgba(99, 102, 241, 0.2) !important;
            border-radius: 16px !important;
            background: rgba(15, 23, 42, 0.3) !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stFileUploader"]:hover {
            border-color: rgba(99, 102, 241, 0.4) !important;
            background: rgba(15, 23, 42, 0.5) !important;
        }

        /* ═══════════════════════════════════════════
           DATAFRAMES
           ═══════════════════════════════════════════ */
        .stDataFrame {
            border-radius: 14px !important;
            overflow: hidden !important;
            border: 1px solid rgba(99, 102, 241, 0.1) !important;
        }

        /* ═══════════════════════════════════════════
           SELECTBOX & NUMBER INPUT
           ═══════════════════════════════════════════ */
        .stSelectbox > div > div,
        .stNumberInput input {
            border-radius: 10px !important;
        }

        /* ═══════════════════════════════════════════
           PLOTLY CHARTS — remove bg
           ═══════════════════════════════════════════ */
        .js-plotly-plot .plotly .main-svg {
            background: transparent !important;
        }

        /* ═══════════════════════════════════════════
           CUSTOM COMPONENTS
           ═══════════════════════════════════════════ */

        /* Risk Badge */
        .risk-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 20px;
            border-radius: 100px;
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-family: 'Inter', sans-serif;
        }
        .risk-critical {
            background: rgba(220, 38, 38, 0.15);
            color: #fca5a5;
            border: 1px solid rgba(220, 38, 38, 0.3);
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.1);
        }
        .risk-high {
            background: rgba(249, 115, 22, 0.15);
            color: #fdba74;
            border: 1px solid rgba(249, 115, 22, 0.3);
            box-shadow: 0 0 20px rgba(249, 115, 22, 0.1);
        }
        .risk-medium {
            background: rgba(234, 179, 8, 0.15);
            color: #fde047;
            border: 1px solid rgba(234, 179, 8, 0.3);
            box-shadow: 0 0 20px rgba(234, 179, 8, 0.1);
        }
        .risk-low {
            background: rgba(34, 197, 94, 0.15);
            color: #86efac;
            border: 1px solid rgba(34, 197, 94, 0.3);
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.1);
        }

        /* Gradient Divider */
        .gradient-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, rgba(99,102,241,0.3) 30%, rgba(139,92,246,0.3) 70%, transparent 100%);
            margin: 28px 0;
            border: none;
        }

        /* Glass Card */
        .glass-card {
            background: linear-gradient(135deg, rgba(15,23,42,0.6), rgba(30,41,59,0.3));
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(99, 102, 241, 0.1);
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.03);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.2);
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.2), 0 0 30px rgba(99,102,241,0.06);
        }

        .glass-card .card-icon {
            font-size: 2rem;
            margin-bottom: 14px;
            display: block;
        }

        .glass-card .card-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 8px;
            letter-spacing: -0.01em;
        }

        .glass-card .card-desc {
            color: #94a3b8;
            font-size: 0.88rem;
            line-height: 1.55;
        }

        /* Stat Pill */
        .stat-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(99, 102, 241, 0.1);
            border-radius: 100px;
            padding: 6px 16px;
            font-size: 0.82rem;
            color: #94a3b8;
            font-weight: 500;
        }

        .stat-pill .stat-value {
            color: #e2e8f0;
            font-weight: 700;
        }

        /* Section Header */
        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }

        .section-header .section-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2));
            border: 1px solid rgba(99,102,241,0.15);
        }

        .section-header .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #e2e8f0;
            letter-spacing: -0.01em;
        }

        /* Page header */
        .page-header {
            padding: 8px 0 4px 0;
        }

        .page-header .page-title {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
            margin-bottom: 6px;
            line-height: 1.2;
        }

        .page-header .page-subtitle {
            color: #64748b;
            font-size: 0.95rem;
            font-weight: 400;
            line-height: 1.4;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {
            background: rgba(10, 15, 26, 0.8) !important;
            backdrop-filter: blur(12px) !important;
        }

        /* Smooth scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.2);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.4);
        }
    </style>
    """


def risk_badge_html(tier: str, icon: str = "") -> str:
    """Generate HTML for a styled risk tier badge."""
    css_class = f"risk-{tier.lower()}"
    icon_html = f'<span class="material-symbols-rounded" style="font-size:1.1em; margin-right:4px;">{icon}</span>' if icon else ""
    return f'<span class="risk-badge {css_class}">{icon_html}{tier}</span>'


def gradient_divider() -> str:
    """Generate a gradient divider HTML element."""
    return '<div class="gradient-divider"></div>'


def page_header(icon: str, title: str, subtitle: str) -> str:
    """Generate a page header with gradient title and material icon."""
    return f"""
    <div class="page-header">
        <div class="page-title"><span class="material-symbols-rounded" style="font-size:inherit; vertical-align:middle; margin-right:8px;">{icon}</span>{title}</div>
        <div class="page-subtitle">{subtitle}</div>
    </div>
    """


def section_header(icon: str, title: str) -> str:
    """Generate a section header with icon."""
    return f"""
    <div class="section-header">
        <div class="section-icon"><span class="material-symbols-rounded">{icon}</span></div>
        <div class="section-title">{title}</div>
    </div>
    """


def glass_card(icon: str, title: str, description: str, accent_color: str = "99,102,241") -> str:
    """Generate a glassmorphism card."""
    return f"""
    <div class="glass-card" style="border-color: rgba({accent_color},0.12);">
        <span class="card-icon"><span class="material-symbols-rounded">{icon}</span></span>
        <div class="card-title">{title}</div>
        <div class="card-desc">{description}</div>
    </div>
    """


def stat_pill(label: str, value: str) -> str:
    """Generate an inline stat pill."""
    return f'<span class="stat-pill">{label} <span class="stat-value">{value}</span></span>'
