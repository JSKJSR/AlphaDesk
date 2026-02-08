"""
AlphaDesk - AI-Powered Investment Research

Professional investment bank-style research reports powered by multi-agent AI.
Features symbol resolution, profile management, and comprehensive analysis.

Run: streamlit run tradingagents/ui/app.py
"""

import streamlit as st
import sys
from datetime import datetime, date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.ui.styles import INVESTMENT_REPORT_CSS
from tradingagents.ui.auth import (
    AuthStatus,
    AuthMethod,
    verify_claude_connection,
    validate_anthropic_api_key,
    get_best_auth_method,
    check_claude_installed,
)
import os
from tradingagents.ui.landing import render_landing_page
from tradingagents.ui.components import (
    render_report_cover,
    render_section_header,
    render_executive_summary,
    render_investment_thesis,
    render_risk_matrix,
    render_appendix,
    render_report_footer,
    render_sidebar_header,
    render_profile_switcher,
    render_symbol_feedback,
    render_waiting_state,
    render_loading_state,
    render_error_state,
    render_footer,
    generate_share_text,
    escape_html,
)
from tradingagents.dataflows.symbol_resolver import resolve_symbol

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="AlphaDesk - AI Investment Research",
    page_icon="α",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom styling
st.markdown(INVESTMENT_REPORT_CSS, unsafe_allow_html=True)

# ========== SESSION STATE ==========
# Auth states
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = AuthStatus.UNKNOWN
if 'claude_verified' not in st.session_state:
    st.session_state.claude_verified = False
if 'show_landing' not in st.session_state:
    st.session_state.show_landing = True
if 'auth_error' not in st.session_state:
    st.session_state.auth_error = None
if 'auth_instructions' not in st.session_state:
    st.session_state.auth_instructions = None
if 'startup_check_done' not in st.session_state:
    st.session_state.startup_check_done = False
if 'auth_method' not in st.session_state:
    st.session_state.auth_method = AuthMethod.NONE
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# ========== AUTO-VERIFY ON STARTUP ==========
# Automatically check for available auth methods on first load
if not st.session_state.startup_check_done:
    st.session_state.startup_check_done = True

    # Check for API key in environment first (for Streamlit Cloud)
    env_api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if env_api_key:
        validation = validate_anthropic_api_key(env_api_key)
        if validation['valid']:
            st.session_state.auth_status = AuthStatus.API_KEY_VALID
            st.session_state.auth_method = AuthMethod.ANTHROPIC_API
            st.session_state.api_key = env_api_key
            st.session_state.claude_verified = True
            st.session_state.show_landing = False

    # Otherwise check CLI
    if not st.session_state.claude_verified:
        result = verify_claude_connection()
        if result['status'] == AuthStatus.CONNECTED:
            st.session_state.auth_status = AuthStatus.CONNECTED
            st.session_state.auth_method = AuthMethod.CLAUDE_CLI
            st.session_state.claude_verified = True
            st.session_state.show_landing = False

# Analysis states
if 'result' not in st.session_state:
    st.session_state.result = None
if 'decision' not in st.session_state:
    st.session_state.decision = None
if 'running' not in st.session_state:
    st.session_state.running = False
if 'error' not in st.session_state:
    st.session_state.error = None
if 'force_fresh' not in st.session_state:
    st.session_state.force_fresh = False

# Symbol states
if 'raw_ticker' not in st.session_state:
    st.session_state.raw_ticker = "AAPL"
if 'resolved_ticker' not in st.session_state:
    st.session_state.resolved_ticker = "AAPL"
if 'ticker_metadata' not in st.session_state:
    st.session_state.ticker_metadata = {}
if 'date_str' not in st.session_state:
    st.session_state.date_str = date.today().strftime("%Y-%m-%d")


# ========== AUTH CALLBACKS ==========
def handle_connect():
    """Handle the Connect button click for Claude CLI."""
    st.session_state.auth_status = AuthStatus.CHECKING
    st.session_state.auth_error = None
    st.session_state.auth_instructions = None

    # Verify connection
    result = verify_claude_connection()

    st.session_state.auth_status = result['status']

    if result['status'] == AuthStatus.CONNECTED:
        st.session_state.auth_method = AuthMethod.CLAUDE_CLI
        st.session_state.claude_verified = True
        st.session_state.show_landing = False
    else:
        st.session_state.auth_error = result.get('details', result.get('message'))
        st.session_state.auth_instructions = result.get('instructions')

    st.rerun()


def handle_api_key_submit(api_key: str):
    """Handle API key submission."""
    st.session_state.auth_status = AuthStatus.CHECKING
    st.session_state.auth_error = None

    # Validate API key
    validation = validate_anthropic_api_key(api_key)

    if validation['valid']:
        st.session_state.auth_status = AuthStatus.API_KEY_VALID
        st.session_state.auth_method = AuthMethod.ANTHROPIC_API
        st.session_state.api_key = api_key
        st.session_state.claude_verified = True
        st.session_state.show_landing = False
        # Also set environment variable for the session
        os.environ['ANTHROPIC_API_KEY'] = api_key
    else:
        st.session_state.auth_status = AuthStatus.API_KEY_INVALID
        st.session_state.auth_error = validation['message']

    st.rerun()


# ========== LANDING PAGE ==========
if st.session_state.show_landing and not st.session_state.claude_verified:
    # Hide sidebar on landing page
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none; }
        .main .block-container { max-width: 1200px; }
    </style>
    """, unsafe_allow_html=True)

    render_landing_page(
        on_connect=handle_connect,
        auth_status=st.session_state.auth_status,
        error_message=st.session_state.auth_error,
        instructions=st.session_state.auth_instructions,
        on_api_key_submit=handle_api_key_submit
    )

else:
    # ========== MAIN DASHBOARD ==========

    # ========== SIDEBAR ==========
    with st.sidebar:
        render_sidebar_header()

        # Profile switcher
        render_profile_switcher()

        # Connection status indicator
        if st.session_state.claude_verified:
            auth_method = st.session_state.auth_method
            if auth_method == AuthMethod.ANTHROPIC_API:
                method_label = "API Key"
                method_icon = "🔑"
            else:
                method_label = "Claude CLI"
                method_icon = "🔗"

            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.5rem;
                        padding: 0.5rem 0.75rem; background: var(--rec-buy-bg);
                        border: 1px solid var(--rec-buy); border-radius: 8px;
                        margin-bottom: 1rem; font-size: 0.8rem;">
                <span>{method_icon}</span>
                <span style="color: var(--rec-buy); font-weight: 500;">Connected via {method_label}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ========== SYMBOL INPUT ==========
        st.markdown('<div class="input-label">Stock Symbol</div>', unsafe_allow_html=True)
        raw_ticker = st.text_input(
            "ticker",
            value=st.session_state.raw_ticker,
            placeholder="e.g., RELIANCE, AAPL, TCS",
            label_visibility="collapsed",
            help="Enter stock symbol. Exchange suffix optional - we'll resolve it automatically."
        )

        # Symbol resolution with feedback
        if raw_ticker and raw_ticker.strip():
            resolved, metadata = resolve_symbol(raw_ticker)
            if resolved:
                st.session_state.resolved_ticker = resolved
                st.session_state.ticker_metadata = metadata
                # Show resolution feedback if different from input
                if raw_ticker.upper() != resolved.upper():
                    render_symbol_feedback(resolved, metadata)
            else:
                st.session_state.resolved_ticker = None
                st.session_state.ticker_metadata = metadata
                render_symbol_feedback(None, metadata)
        else:
            st.session_state.resolved_ticker = None

        st.markdown("<br>", unsafe_allow_html=True)

        # ========== DATE INPUT ==========
        st.markdown('<div class="input-label">Analysis Date</div>', unsafe_allow_html=True)
        analysis_date = st.date_input(
            "date",
            value=date.today(),
            label_visibility="collapsed",
        )
        date_str = analysis_date.strftime("%Y-%m-%d")

        st.markdown("<br>", unsafe_allow_html=True)

        # ========== ANALYST SELECTION ==========
        st.markdown('<div class="input-label">AI Analysts</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            market = st.checkbox("Technical", value=True, help="Price charts & indicators")
            social = st.checkbox("Sentiment", value=True, help="Social media analysis")
        with col2:
            news = st.checkbox("News", value=True, help="News & events")
            fundamentals = st.checkbox("Fundamentals", value=True, help="Financial data")

        analysts = {
            "market": market,
            "social": social,
            "news": news,
            "fundamentals": fundamentals,
        }
        selected_analysts = [k for k, v in analysts.items() if v]

        st.markdown("<br>", unsafe_allow_html=True)

        # ========== CACHE OPTIONS ==========
        force_fresh = st.checkbox("Force fresh analysis", value=False,
                                  help="Bypass cache and run new analysis")

        st.markdown("<br>", unsafe_allow_html=True)

        # ========== ACTION BUTTONS ==========
        run_disabled = not selected_analysts or st.session_state.running or not st.session_state.resolved_ticker
        if st.button("Run Analysis", use_container_width=True, disabled=run_disabled, type="primary"):
            st.session_state.raw_ticker = raw_ticker
            st.session_state.date_str = date_str
            st.session_state.running = True
            st.session_state.force_fresh = force_fresh
            st.session_state.error = None
            st.rerun()

        # Show warning if symbol not resolved
        if raw_ticker and not st.session_state.resolved_ticker:
            st.markdown("""
            <div style="font-size: 0.75rem; color: var(--rec-sell); margin-top: 0.5rem;">
                Please enter a valid stock symbol
            </div>
            """, unsafe_allow_html=True)

        # Clear results button
        if st.session_state.result:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Clear Results", use_container_width=True):
                st.session_state.result = None
                st.session_state.decision = None
                st.session_state.error = None
                st.rerun()

        # Back to home button
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Back to Home", use_container_width=True):
            st.session_state.show_landing = True
            st.rerun()

        # Info box
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: var(--bg-section); border: 1px solid var(--border-light);
                    border-radius: 8px; padding: 1rem; font-size: 0.75rem; color: var(--text-muted);">
            <strong style="color: var(--text-secondary);">Supported Markets</strong><br><br>
            US: AAPL, MSFT, GOOGL<br>
            India NSE: RELIANCE, TCS<br>
            India BSE: Add .BO suffix<br>
            Indices: NIFTY, SENSEX
        </div>
        """, unsafe_allow_html=True)


    # ========== ANALYSIS CACHE ==========
    import os
    import json
    import hashlib

    CACHE_DIR = os.path.expanduser('~/.tradingagents/cache')

    def get_cache_key(ticker: str, date_str: str, analysts: list) -> str:
        """Generate cache key from analysis parameters."""
        key_str = f"{ticker}_{date_str}_{'_'.join(sorted(analysts))}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def load_from_cache(ticker: str, date_str: str, analysts: list):
        """Load cached analysis results if available."""
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_key = get_cache_key(ticker, date_str, analysts)
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

        if os.path.exists(cache_file):
            try:
                # Check if cache is less than 24 hours old
                import time
                if time.time() - os.path.getmtime(cache_file) < 86400:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        return data.get('result'), data.get('decision')
            except (json.JSONDecodeError, IOError):
                pass
        return None, None

    def save_to_cache(ticker: str, date_str: str, analysts: list, result: dict, decision: str):
        """Save analysis results to cache."""
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_key = get_cache_key(ticker, date_str, analysts)
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

        try:
            with open(cache_file, 'w') as f:
                json.dump({'result': result, 'decision': decision}, f)
        except IOError:
            pass

    # ========== ANALYSIS FUNCTION ==========
    def run_analysis(ticker: str, date_str: str, selected_analysts: list, use_cache: bool = True):
        """Run the TradingAgents analysis with caching and progress."""
        try:
            # Check cache first
            if use_cache:
                cached_result, cached_decision = load_from_cache(ticker, date_str, selected_analysts)
                if cached_result and cached_decision:
                    return cached_result, cached_decision, None, True  # True = from cache

            from tradingagents.graph.trading_graph import TradingAgentsGraph
            from tradingagents.default_config import DEFAULT_CONFIG

            config = DEFAULT_CONFIG.copy()

            # Set LLM provider based on auth method
            if st.session_state.auth_method == AuthMethod.ANTHROPIC_API:
                config['llm_provider'] = 'anthropic-api'
                # Ensure API key is in environment
                if st.session_state.api_key:
                    os.environ['ANTHROPIC_API_KEY'] = st.session_state.api_key
            else:
                config['llm_provider'] = 'claude-code'

            graph = TradingAgentsGraph(
                selected_analysts=selected_analysts,
                debug=False,
                config=config
            )

            final_state, decision = graph.propagate(ticker, date_str)

            # Save to cache
            if final_state and decision:
                save_to_cache(ticker, date_str, selected_analysts, final_state, decision)

            return final_state, decision, None, False  # False = fresh analysis

        except Exception as e:
            import traceback
            return None, None, f"{str(e)}\n\n{traceback.format_exc()}", False


    # ========== MAIN CONTENT ==========
    if st.session_state.running:
        # Running state
        ticker = st.session_state.resolved_ticker or st.session_state.raw_ticker

        # Show progress with status updates
        with st.status(f"Analyzing {ticker}...", expanded=True) as status:
            st.write("Checking cache...")

            # Run analysis (will check cache first unless force_fresh)
            use_cache = not st.session_state.force_fresh
            result, decision, error, from_cache = run_analysis(
                ticker,
                st.session_state.date_str,
                selected_analysts,
                use_cache=use_cache
            )

            if from_cache:
                st.write("Loaded from cache (less than 24h old)")
                status.update(label="Analysis loaded from cache!", state="complete")
            elif error:
                status.update(label="Analysis failed", state="error")
            else:
                st.write("Analysis complete!")
                status.update(label="Analysis complete!", state="complete")

        st.session_state.running = False

        if error:
            st.session_state.error = error
        else:
            st.session_state.result = result
            st.session_state.decision = decision

        st.rerun()

    elif st.session_state.error:
        # Error state
        ticker = st.session_state.resolved_ticker or st.session_state.raw_ticker
        render_report_cover(ticker, ticker, "HOLD", st.session_state.date_str)
        render_error_state(st.session_state.error)

    elif st.session_state.result:
        # ========== RESULTS - INVESTMENT BANK REPORT LAYOUT ==========
        result = st.session_state.result
        decision = st.session_state.decision
        ticker = result.get('company_of_interest', st.session_state.resolved_ticker)
        date_str = result.get('trade_date', st.session_state.date_str)

        # Get company info from metadata
        company_name = st.session_state.ticker_metadata.get('company_name', ticker)
        exchange = st.session_state.ticker_metadata.get('exchange', '')

        # 1. REPORT COVER
        render_report_cover(ticker, company_name, decision, date_str, exchange)

        # 2. EXECUTIVE SUMMARY
        render_section_header("Executive Summary", "01")
        render_executive_summary(result, decision)

        # 3. INVESTMENT THESIS
        render_section_header("Investment Thesis", "02")
        invest_debate = result.get('investment_debate_state', {})
        render_investment_thesis(
            invest_debate.get('bull_history', ''),
            invest_debate.get('bear_history', ''),
            invest_debate.get('judge_decision', '')
        )

        # 4. RISK ASSESSMENT
        render_section_header("Risk Assessment", "03")
        risk_debate = result.get('risk_debate_state', {})
        render_risk_matrix(
            risk_debate.get('risky_history', ''),
            risk_debate.get('safe_history', ''),
            risk_debate.get('neutral_history', ''),
            risk_debate.get('judge_decision', '')
        )

        # 5. TECHNICAL ANALYSIS (if available)
        if result.get('market_report'):
            render_section_header("Technical Analysis", "04")
            market_content = escape_html(result.get('market_report', '')[:2000])
            st.markdown(f"""
                <div style="background: var(--bg-section); border: 1px solid var(--border-light);
                            border-radius: 8px; padding: 1.5rem; margin: 1rem 0;
                            font-size: 0.95rem; line-height: 1.7; color: var(--text-secondary);">
                    {market_content}
                </div>
            """, unsafe_allow_html=True)

        # 6. APPENDIX
        render_section_header("Appendix", "05")
        render_appendix(result)

        # 7. SHARE SECTION
        st.markdown("<br>", unsafe_allow_html=True)
        share_text = generate_share_text(ticker, decision, date_str)
        with st.expander("Share This Report"):
            st.code(share_text, language=None)
            st.markdown("""
            <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.5rem;">
                Copy the text above to share on social media.
            </div>
            """, unsafe_allow_html=True)

        # 8. REPORT FOOTER
        render_report_footer(ticker, date_str)

    else:
        # Waiting state
        render_waiting_state()

    # Simple footer
    render_footer()
