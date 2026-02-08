"""
Apple-style Landing Page Components for AlphaDesk.

Minimalist design with clean typography, generous whitespace,
and clear call-to-action elements. Supports both Claude CLI and API key auth.
"""

import streamlit as st
from typing import Callable, Optional
from .auth import (
    AuthStatus,
    AuthMethod,
    get_connection_status_display,
    validate_anthropic_api_key,
    get_api_key_instructions,
    check_claude_installed,
)


def render_landing_page(on_connect: Callable, auth_status: AuthStatus = AuthStatus.UNKNOWN,
                        error_message: str = None, instructions: str = None,
                        on_api_key_submit: Callable = None):
    """
    Render the complete landing page.

    Args:
        on_connect: Callback function when Connect button is clicked
        auth_status: Current authentication status
        error_message: Optional error message to display
        instructions: Optional setup instructions to display
        on_api_key_submit: Callback when API key is submitted
    """
    render_hero_section(on_connect, auth_status, error_message, instructions, on_api_key_submit)
    render_workflow_section()
    render_features_section()
    render_markets_section()
    render_footer_cta(on_connect, auth_status, on_api_key_submit)


def render_hero_section(on_connect: Callable, auth_status: AuthStatus,
                        error_message: str = None, instructions: str = None,
                        on_api_key_submit: Callable = None):
    """Render the hero section with main CTA."""

    # Hero container
    st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(180deg, #fafafa 0%, #f5f5f7 100%); border-radius: 16px; margin-bottom: 3rem;">
            <div style="display: inline-block; padding: 0.4rem 1rem; background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%); color: white; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; border-radius: 100px; margin-bottom: 1.5rem;">
                AI-Powered Investment Research
            </div>
            <h1 style="font-size: 3.5rem; font-weight: 700; color: #1d1d1f; letter-spacing: -2px; margin-bottom: 1rem; line-height: 1.1;">
                <span style="color: #0071e3;">α</span> AlphaDesk
            </h1>
            <p style="font-size: 1.25rem; color: #86868b; max-width: 600px; margin: 0 auto; line-height: 1.6;">
                Professional investment research powered by multi-agent AI.
                Get Wall Street-grade analysis with your Claude account.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Connection options
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        status_display = get_connection_status_display(auth_status)

        if auth_status in [AuthStatus.CONNECTED, AuthStatus.API_KEY_VALID]:
            st.success(f"{status_display['icon']} {status_display['title']}")
        elif auth_status == AuthStatus.CHECKING:
            st.info("⏳ Verifying connection...")
        else:
            # Show auth options in tabs
            cli_available = check_claude_installed()

            if cli_available:
                tab1, tab2 = st.tabs(["🔗 Claude CLI", "🔑 API Key"])
            else:
                tab1, tab2 = st.tabs(["🔑 API Key", "🔗 Claude CLI"])

            # Claude CLI tab
            with (tab1 if cli_available else tab2):
                st.markdown("""
                    <p style="font-size: 0.9rem; color: #86868b; margin-bottom: 1rem;">
                        Use your Claude Pro subscription via Claude CLI (recommended for local use)
                    </p>
                """, unsafe_allow_html=True)

                if cli_available:
                    if st.button("Connect Claude CLI", key="hero_connect_cli",
                                 use_container_width=True, type="primary"):
                        on_connect()
                else:
                    st.warning("Claude CLI not detected on this system")
                    st.markdown("""
                        **Install Claude CLI:**
                        ```bash
                        npm install -g @anthropic-ai/claude-code
                        ```
                        Then run `claude` to authenticate.
                    """)

            # API Key tab
            with (tab2 if cli_available else tab1):
                st.markdown("""
                    <p style="font-size: 0.9rem; color: #86868b; margin-bottom: 1rem;">
                        Use your Anthropic API key (works on Streamlit Cloud)
                    </p>
                """, unsafe_allow_html=True)

                api_key = st.text_input(
                    "Anthropic API Key",
                    type="password",
                    placeholder="sk-ant-...",
                    key="landing_api_key",
                    help="Get your API key from console.anthropic.com"
                )

                if st.button("Connect with API Key", key="hero_connect_api",
                             use_container_width=True,
                             type="primary" if not cli_available else "secondary"):
                    if api_key:
                        if on_api_key_submit:
                            on_api_key_submit(api_key)
                    else:
                        st.error("Please enter your API key")

                with st.expander("How to get an API key"):
                    st.markdown(get_api_key_instructions())

            # Show error if any
            if error_message and auth_status in [AuthStatus.NOT_INSTALLED,
                                                  AuthStatus.NOT_AUTHENTICATED,
                                                  AuthStatus.ERROR,
                                                  AuthStatus.API_KEY_INVALID]:
                st.error(f"{status_display['icon']} **{status_display['title']}**: {error_message}")

                if instructions:
                    with st.expander("📋 Setup Instructions"):
                        st.code(instructions, language=None)


def render_workflow_section():
    """Render the 'How It Works' workflow section."""

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style="font-size: 2rem; font-weight: 600; color: #1d1d1f; margin-bottom: 0.75rem;">
                How It Works
            </h2>
            <p style="font-size: 1.1rem; color: #86868b; margin-bottom: 2rem;">
                Four specialized AI analysts work together to give you comprehensive insights
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Workflow steps using Streamlit columns
    cols = st.columns(4)
    steps = [
        ("📈", "Technical", "Price charts & indicators"),
        ("📰", "News", "Market news & events"),
        ("💬", "Sentiment", "Social media analysis"),
        ("📊", "Fundamentals", "Financial metrics"),
    ]

    for col, (icon, label, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem 1rem; background: white; border: 1px solid #e5e5e5; border-radius: 10px;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                    <div style="font-size: 0.9rem; font-weight: 600; color: #1d1d1f; margin-bottom: 0.25rem;">{label}</div>
                    <div style="font-size: 0.75rem; color: #86868b;">{desc}</div>
                </div>
            """, unsafe_allow_html=True)

    # Debate flow
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; padding: 1rem 1.5rem; background: #f5f5f7; border-radius: 10px; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 100px; background: rgba(52, 199, 89, 0.15); color: #248a3d; font-size: 0.85rem; font-weight: 500;">
                    <span>🐂</span><span>Bull Case</span>
                </div>
                <span style="font-weight: 600; color: #86868b;">vs</span>
                <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 100px; background: rgba(255, 59, 48, 0.15); color: #d70015; font-size: 0.85rem; font-weight: 500;">
                    <span>🐻</span><span>Bear Case</span>
                </div>
                <span style="font-size: 1.25rem; color: #d2d2d7;">→</span>
                <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 100px; background: rgba(0, 113, 227, 0.15); color: #0071e3; font-size: 0.85rem; font-weight: 500;">
                    <span>⚖️</span><span>Final Verdict</span>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_features_section():
    """Render the key features section."""

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1rem;">
            <h2 style="font-size: 2rem; font-weight: 600; color: #1d1d1f; margin-bottom: 1.5rem;">
                Key Features
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Features grid
    col1, col2 = st.columns(2)

    features = [
        ("🤖", "Multi-Agent Analysis", "Four specialized AI agents analyze different aspects of a stock, providing comprehensive coverage like a professional research team."),
        ("⚔️", "Bull vs Bear Debate", "AI agents debate both sides of the investment case, ensuring balanced analysis and surfacing key risks and opportunities."),
        ("🎯", "Risk Assessment", "Three risk perspectives (aggressive, conservative, balanced) help you understand the risk-reward profile."),
        ("🔐", "Flexible Authentication", "Use Claude CLI with your Pro subscription, or connect via API key for cloud deployment."),
    ]

    for i, (icon, title, desc) in enumerate(features):
        with [col1, col2][i % 2]:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e5e5e5; border-radius: 10px; padding: 2rem 1.5rem; text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">{icon}</div>
                    <h3 style="font-size: 1.1rem; font-weight: 600; color: #1d1d1f; margin-bottom: 0.75rem;">{title}</h3>
                    <p style="font-size: 0.9rem; color: #86868b; line-height: 1.6;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)


def render_markets_section():
    """Render the supported markets section."""

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1rem;">
            <h2 style="font-size: 2rem; font-weight: 600; color: #1d1d1f; margin-bottom: 1.5rem;">
                Supported Markets
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Markets grid
    cols = st.columns(4)
    markets = [
        ("🇺🇸", "US Stocks", "AAPL, MSFT, GOOGL"),
        ("🇮🇳", "India NSE", "RELIANCE, TCS"),
        ("🇮🇳", "India BSE", "RELIANCE.BO"),
        ("📈", "Indices", "NIFTY, SENSEX"),
    ]

    for col, (flag, name, examples) in zip(cols, markets):
        with col:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e5e5e5; border-radius: 10px; padding: 1.5rem; text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{flag}</div>
                    <div style="font-size: 0.95rem; font-weight: 600; color: #1d1d1f; margin-bottom: 0.25rem;">{name}</div>
                    <div style="font-size: 0.8rem; color: #86868b; font-family: monospace;">{examples}</div>
                </div>
            """, unsafe_allow_html=True)


def render_footer_cta(on_connect: Callable, auth_status: AuthStatus,
                      on_api_key_submit: Callable = None):
    """Render the footer call-to-action."""

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: #f5f5f7; border-radius: 16px; margin: 2rem 0;">
            <h2 style="font-size: 2rem; font-weight: 600; color: #1d1d1f; margin-bottom: 0.5rem;">
                Ready to Generate Alpha?
            </h2>
            <p style="font-size: 1rem; color: #86868b; margin-bottom: 1.5rem;">
                Connect your Claude account and start getting professional investment research.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if auth_status in [AuthStatus.CONNECTED, AuthStatus.API_KEY_VALID]:
            if st.button("🚀 Start Analyzing", key="footer_start",
                         use_container_width=True, type="primary"):
                st.session_state.show_landing = False
                st.rerun()
        else:
            cli_available = check_claude_installed()
            if cli_available:
                if st.button("🔗 Connect Claude Account", key="footer_connect",
                             use_container_width=True, type="primary"):
                    on_connect()
            else:
                st.info("Enter your API key above to get started")

    # Footer info
    st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; margin-top: 2rem;">
            <p style="font-size: 0.8rem; color: #86868b; max-width: 600px; margin: 0 auto 1rem; line-height: 1.6;">
                AlphaDesk is for informational purposes only. Not financial advice.
                Always do your own research before making investment decisions.
            </p>
            <p style="font-size: 0.75rem; color: #aeaeb2;">
                Powered by Claude · Built with Streamlit
            </p>
        </div>
    """, unsafe_allow_html=True)
