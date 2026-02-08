"""
Investment Bank Report Styling for TradingAgents.

Professional typography, clear hierarchy, and minimalist layout
inspired by Goldman Sachs, Morgan Stanley, and JP Morgan research reports.
"""

INVESTMENT_REPORT_CSS = """
<style>
/* ========== FONTS ========== */
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ========== CSS VARIABLES ========== */
:root {
    /* Typography */
    --font-heading: 'Merriweather', Georgia, serif;
    --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', monospace;

    /* Type Scale */
    --type-h1: 2.5rem;
    --type-h2: 1.75rem;
    --type-h3: 1.25rem;
    --type-body: 1rem;
    --type-small: 0.875rem;
    --type-tiny: 0.75rem;

    /* Colors - Investment Bank Palette */
    --bg-paper: #fafafa;
    --bg-section: #ffffff;
    --bg-sidebar: #f5f5f7;
    --bg-muted: #f0f0f2;

    /* Borders */
    --border-light: #e5e5e5;
    --border-medium: #d1d1d6;
    --border-dark: #c7c7cc;

    /* Text */
    --text-primary: #1d1d1f;
    --text-secondary: #6e6e73;
    --text-muted: #86868b;
    --text-light: #aeaeb2;

    /* Recommendations - Goldman Sachs style */
    --rec-buy: #007a3d;
    --rec-buy-bg: #e6f4ed;
    --rec-buy-border: #007a3d;
    --rec-sell: #c41e3a;
    --rec-sell-bg: #fce8ec;
    --rec-sell-border: #c41e3a;
    --rec-hold: #b5850b;
    --rec-hold-bg: #fef7e0;
    --rec-hold-border: #b5850b;

    /* Accent */
    --accent-blue: #0066cc;
    --accent-blue-light: #e6f0fa;

    /* Spacing */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    --space-2xl: 3rem;

    /* Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
}

/* ========== GLOBAL STYLES ========== */
.stApp {
    background: var(--bg-paper);
    font-family: var(--font-body);
    color: var(--text-primary);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.main .block-container {
    padding: 2rem 3rem;
    max-width: 1000px;
}

/* ========== REPORT CONTAINER ========== */
.report-container {
    max-width: 900px;
    margin: 0 auto;
    background: var(--bg-paper);
}

/* ========== REPORT COVER ========== */
.report-cover {
    border-bottom: 3px solid var(--border-light);
    padding-bottom: 2rem;
    margin-bottom: 2rem;
}

.report-firm-badge {
    display: inline-block;
    font-family: var(--font-body);
    font-size: var(--type-tiny);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-muted);
    padding: 0.35rem 0.75rem;
    background: var(--bg-muted);
    border-radius: var(--radius-sm);
    margin-bottom: 1.5rem;
}

.report-ticker {
    font-family: var(--font-heading);
    font-size: var(--type-h1);
    font-weight: 900;
    color: var(--text-primary);
    letter-spacing: -1px;
    margin-bottom: 0.25rem;
    line-height: 1.2;
}

.report-company-name {
    font-family: var(--font-body);
    font-size: 1.25rem;
    font-weight: 400;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
}

.report-meta {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.report-date {
    font-size: var(--type-small);
    color: var(--text-muted);
}

.report-exchange {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: var(--type-small);
    color: var(--text-secondary);
    padding: 0.25rem 0.75rem;
    background: var(--bg-muted);
    border-radius: 100px;
}

/* ========== RECOMMENDATION BADGE ========== */
.recommendation-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 2rem;
    font-family: var(--font-heading);
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-radius: var(--radius-sm);
    margin: 1rem 0;
}

.recommendation-badge.buy {
    background: var(--rec-buy-bg);
    color: var(--rec-buy);
    border: 2px solid var(--rec-buy-border);
}

.recommendation-badge.sell {
    background: var(--rec-sell-bg);
    color: var(--rec-sell);
    border: 2px solid var(--rec-sell-border);
}

.recommendation-badge.hold {
    background: var(--rec-hold-bg);
    color: var(--rec-hold);
    border: 2px solid var(--rec-hold-border);
}

.recommendation-icon {
    font-size: 1.25rem;
}

/* ========== SECTION HEADERS ========== */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-family: var(--font-heading);
    font-size: var(--type-h2);
    font-weight: 700;
    color: var(--text-primary);
    border-bottom: 2px solid var(--border-light);
    padding-bottom: 0.75rem;
    margin: 2.5rem 0 1.5rem;
}

.section-header::before {
    content: '';
    display: block;
    width: 4px;
    height: 1.75rem;
    background: var(--accent-blue);
    border-radius: 2px;
}

.section-number {
    font-family: var(--font-mono);
    font-size: var(--type-small);
    color: var(--text-muted);
    margin-right: 0.5rem;
}

/* ========== EXECUTIVE SUMMARY ========== */
.executive-summary {
    background: var(--bg-section);
    border: 1px solid var(--border-light);
    border-left: 4px solid var(--accent-blue);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0 2rem;
}

.executive-summary p {
    font-size: 1.1rem;
    line-height: 1.8;
    color: var(--text-primary);
    margin: 0;
}

.executive-summary .highlight {
    background: var(--accent-blue-light);
    padding: 0.1rem 0.3rem;
    border-radius: 2px;
}

/* ========== THESIS GRID (Bull/Bear) ========== */
.thesis-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin: 1.5rem 0;
}

.thesis-card {
    background: var(--bg-section);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    position: relative;
}

.thesis-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.thesis-card.bull::before {
    background: var(--rec-buy);
}

.thesis-card.bear::before {
    background: var(--rec-sell);
}

.thesis-card-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.thesis-card-icon {
    font-size: 1.5rem;
}

.thesis-card-title {
    font-family: var(--font-heading);
    font-size: 1.1rem;
    font-weight: 700;
}

.thesis-card.bull .thesis-card-title {
    color: var(--rec-buy);
}

.thesis-card.bear .thesis-card-title {
    color: var(--rec-sell);
}

.thesis-card-content {
    font-size: var(--type-body);
    line-height: 1.7;
    color: var(--text-secondary);
    max-height: 250px;
    overflow-y: auto;
}

/* ========== VERDICT CARD ========== */
.verdict-card {
    background: var(--bg-section);
    border: 1px solid var(--border-light);
    border-left: 4px solid var(--accent-blue);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 1.5rem;
    margin: 1rem 0;
}

.verdict-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.verdict-icon {
    font-size: 1.25rem;
}

.verdict-title {
    font-family: var(--font-heading);
    font-size: 1rem;
    font-weight: 700;
    color: var(--accent-blue);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.verdict-content {
    font-size: var(--type-body);
    line-height: 1.7;
    color: var(--text-primary);
}

/* ========== RISK MATRIX ========== */
.risk-matrix {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}

.risk-card {
    background: var(--bg-section);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    position: relative;
}

.risk-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.risk-card.aggressive::before { background: var(--rec-sell); }
.risk-card.conservative::before { background: var(--rec-buy); }
.risk-card.balanced::before { background: var(--rec-hold); }

.risk-label {
    font-size: var(--type-tiny);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

.risk-card.aggressive .risk-label { color: var(--rec-sell); }
.risk-card.conservative .risk-label { color: var(--rec-buy); }
.risk-card.balanced .risk-label { color: var(--rec-hold); }

.risk-content {
    font-size: var(--type-small);
    line-height: 1.6;
    color: var(--text-secondary);
    max-height: 150px;
    overflow-y: auto;
}

/* ========== DATA TABLE ========== */
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--type-small);
    margin: 1rem 0;
}

.data-table th {
    text-align: left;
    font-weight: 600;
    color: var(--text-secondary);
    border-bottom: 2px solid var(--border-light);
    padding: 0.75rem 1rem;
    text-transform: uppercase;
    font-size: var(--type-tiny);
    letter-spacing: 0.5px;
}

.data-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-light);
    color: var(--text-primary);
}

.data-table tr:hover {
    background: var(--bg-muted);
}

.data-table .positive { color: var(--rec-buy); font-weight: 500; }
.data-table .negative { color: var(--rec-sell); font-weight: 500; }

/* ========== APPENDIX ========== */
.appendix-section {
    background: var(--bg-muted);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    margin-top: 2rem;
}

.appendix-title {
    font-family: var(--font-heading);
    font-size: var(--type-small);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

.appendix-content {
    font-size: var(--type-small);
    line-height: 1.6;
    color: var(--text-secondary);
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
}

/* ========== SIDEBAR ========== */
section[data-testid="stSidebar"] {
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border-light);
}

section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1rem;
}

.sidebar-header {
    text-align: center;
    padding-bottom: 1.5rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border-light);
}

.sidebar-logo {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.sidebar-title {
    font-family: var(--font-heading);
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.sidebar-subtitle {
    font-size: var(--type-tiny);
    color: var(--text-muted);
}

/* ========== PROFILE SWITCHER ========== */
.profile-switcher {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-light);
}

.profile-current {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg-section);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
}

.profile-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 1rem;
    flex-shrink: 0;
}

.profile-info {
    flex: 1;
    min-width: 0;
}

.profile-name {
    font-weight: 600;
    font-size: var(--type-small);
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.profile-email {
    font-size: var(--type-tiny);
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ========== SYMBOL RESOLVER FEEDBACK ========== */
.symbol-resolved {
    font-size: var(--type-tiny);
    padding: 0.5rem 0.75rem;
    background: var(--rec-buy-bg);
    border: 1px solid var(--rec-buy);
    border-radius: var(--radius-sm);
    margin-top: 0.5rem;
}

.symbol-resolved-ticker {
    font-family: var(--font-mono);
    font-weight: 600;
    color: var(--rec-buy);
}

.symbol-resolved-name {
    color: var(--text-secondary);
    font-size: var(--type-tiny);
}

.symbol-error {
    font-size: var(--type-tiny);
    padding: 0.5rem 0.75rem;
    background: var(--rec-sell-bg);
    border: 1px solid var(--rec-sell);
    border-radius: var(--radius-sm);
    margin-top: 0.5rem;
    color: var(--rec-sell);
}

/* ========== INPUT LABELS ========== */
.input-label {
    font-size: var(--type-tiny);
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

/* ========== BUTTONS ========== */
.stButton > button {
    width: 100%;
    background: var(--accent-blue);
    color: white;
    font-weight: 600;
    font-size: var(--type-small);
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: var(--radius-md);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #0052a3;
    transform: translateY(-1px);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Secondary button style */
.stButton > button[kind="secondary"] {
    background: var(--bg-section);
    color: var(--text-primary);
    border: 1px solid var(--border-medium);
}

.stButton > button[kind="secondary"]:hover {
    background: var(--bg-muted);
}

/* ========== INPUTS ========== */
.stTextInput input,
.stSelectbox select,
.stDateInput input {
    background: var(--bg-section) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
}

.stTextInput input:focus,
.stSelectbox select:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.2) !important;
}

/* ========== EXPANDERS ========== */
.streamlit-expanderHeader {
    background: var(--bg-muted) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    color: var(--text-primary) !important;
}

.streamlit-expanderContent {
    background: var(--bg-section) !important;
    border: 1px solid var(--border-light) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
}

/* ========== CHECKBOXES ========== */
.stCheckbox label {
    font-size: var(--type-small);
    color: var(--text-primary);
}

/* ========== SCROLLBAR ========== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: var(--bg-muted);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb {
    background: var(--border-medium);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}

/* ========== REPORT FOOTER ========== */
.report-footer {
    text-align: center;
    padding: 2rem 1rem;
    margin-top: 3rem;
    border-top: 2px solid var(--border-light);
}

.report-footer-disclaimer {
    font-size: var(--type-tiny);
    color: var(--text-muted);
    max-width: 600px;
    margin: 0 auto 1rem;
    line-height: 1.6;
}

.report-footer-brand {
    font-size: var(--type-tiny);
    color: var(--text-light);
}

/* ========== LOADING STATE ========== */
.loading-container {
    text-align: center;
    padding: 3rem 2rem;
}

.loading-spinner {
    width: 48px;
    height: 48px;
    border: 3px solid var(--border-light);
    border-top-color: var(--accent-blue);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1.5rem;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-title {
    font-family: var(--font-heading);
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.loading-subtitle {
    font-size: var(--type-small);
    color: var(--text-muted);
}

/* ========== WAITING STATE ========== */
.waiting-container {
    text-align: center;
    padding: 4rem 2rem;
}

.waiting-icon {
    font-size: 3.5rem;
    margin-bottom: 1.5rem;
    opacity: 0.9;
}

.waiting-title {
    font-family: var(--font-heading);
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.waiting-subtitle {
    font-size: var(--type-body);
    color: var(--text-secondary);
    margin-bottom: 2rem;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
}

/* ========== ERROR STATE ========== */
.error-container {
    background: var(--rec-sell-bg);
    border: 1px solid var(--rec-sell);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    margin: 1rem 0;
}

.error-title {
    font-weight: 600;
    color: var(--rec-sell);
    margin-bottom: 0.5rem;
}

.error-message {
    font-size: var(--type-small);
    color: var(--text-secondary);
    font-family: var(--font-mono);
    white-space: pre-wrap;
    max-height: 200px;
    overflow-y: auto;
}

/* ========== RESPONSIVE ========== */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }

    .report-ticker {
        font-size: 2rem;
    }

    .thesis-grid {
        grid-template-columns: 1fr;
    }

    .risk-matrix {
        grid-template-columns: 1fr;
    }

    .recommendation-badge {
        padding: 0.5rem 1.5rem;
        font-size: 1.25rem;
    }
}

/* ========================================== */
/* ========== LANDING PAGE STYLES ========== */
/* ========================================== */

.landing-hero {
    text-align: center;
    padding: 4rem 2rem;
    background: linear-gradient(180deg, #fafafa 0%, #f5f5f7 100%);
    border-radius: var(--radius-lg);
    margin-bottom: 3rem;
}

.landing-hero-badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    background: linear-gradient(135deg, var(--accent-blue) 0%, #42a5f5 100%);
    color: white;
    font-size: var(--type-tiny);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-radius: 100px;
    margin-bottom: 1.5rem;
}

.landing-hero-title {
    font-family: var(--font-heading);
    font-size: 3.5rem;
    font-weight: 900;
    color: var(--text-primary);
    letter-spacing: -2px;
    margin-bottom: 1rem;
    line-height: 1.1;
}

.landing-hero-subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

.landing-section {
    padding: 3rem 1rem;
    margin-bottom: 2rem;
}

.landing-section-title {
    font-family: var(--font-heading);
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    text-align: center;
    margin-bottom: 0.75rem;
}

.landing-section-subtitle {
    font-size: 1.1rem;
    color: var(--text-secondary);
    text-align: center;
    margin-bottom: 2.5rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.landing-footer {
    text-align: center;
    padding: 2rem 1rem;
    margin-top: 2rem;
}

.landing-footer p {
    font-size: var(--type-small);
    color: var(--text-muted);
    max-width: 600px;
    margin: 0 auto 1rem;
    line-height: 1.6;
}

@media (max-width: 768px) {
    .landing-hero {
        padding: 2.5rem 1rem;
    }

    .landing-hero-title {
        font-size: 2.25rem;
    }
}
</style>
"""

# Backward compatibility alias
BLOOMBERG_CSS = INVESTMENT_REPORT_CSS

# Color constants for programmatic use
COLORS = {
    'bg_paper': '#fafafa',
    'bg_section': '#ffffff',
    'bg_sidebar': '#f5f5f7',
    'border_light': '#e5e5e5',
    'text_primary': '#1d1d1f',
    'text_secondary': '#6e6e73',
    'text_muted': '#86868b',
    'accent_blue': '#0066cc',
    'rec_buy': '#007a3d',
    'rec_sell': '#c41e3a',
    'rec_hold': '#b5850b',
}
