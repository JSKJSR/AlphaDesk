"""
TradingAgents UI - Elegant, responsive Streamlit interface.

Features:
- Apple-style landing page with Claude account connection
- Dark theme dashboard for analysis results
- Responsive design for all screen sizes
"""

from .styles import BLOOMBERG_CSS, COLORS
from .auth import (
    AuthStatus,
    check_claude_installed,
    check_claude_authenticated,
    verify_claude_connection,
    get_connection_status_display,
)
from .landing import (
    render_landing_page,
    render_hero_section,
    render_workflow_section,
    render_features_section,
    render_markets_section,
    render_footer_cta,
)
from .components import (
    render_hero_header,
    render_decision_card,
    render_summary_card,
    render_pipeline_progress,
    render_section_card,
    render_investment_debate,
    render_risk_debate,
    render_waiting_state,
    render_loading_state,
    render_error_state,
    render_sidebar_header,
    render_footer,
    render_analyst_reports,
    render_trader_analysis,
    generate_share_text,
)

__all__ = [
    # Styles
    'BLOOMBERG_CSS',
    'COLORS',
    # Auth
    'AuthStatus',
    'check_claude_installed',
    'check_claude_authenticated',
    'verify_claude_connection',
    'get_connection_status_display',
    # Landing page
    'render_landing_page',
    'render_hero_section',
    'render_workflow_section',
    'render_features_section',
    'render_markets_section',
    'render_footer_cta',
    # Dashboard components
    'render_hero_header',
    'render_decision_card',
    'render_summary_card',
    'render_pipeline_progress',
    'render_section_card',
    'render_investment_debate',
    'render_risk_debate',
    'render_waiting_state',
    'render_loading_state',
    'render_error_state',
    'render_sidebar_header',
    'render_footer',
    'render_analyst_reports',
    'render_trader_analysis',
    'generate_share_text',
]
