"""
Investment Bank Report Components for TradingAgents.

Professional typography, clear hierarchy, and structured layout
inspired by Goldman Sachs, Morgan Stanley, and JP Morgan research reports.
"""

import streamlit as st
import html
from datetime import datetime
from typing import Dict, Optional


def escape_html(content: str) -> str:
    """Escape HTML tags in content to prevent rendering issues."""
    if not content:
        return ""
    # Escape HTML entities
    escaped = html.escape(content)
    # Convert newlines to <br> for proper display
    escaped = escaped.replace('\n', '<br>')
    return escaped


# ============================================================================
# REPORT COMPONENTS
# ============================================================================

def render_report_cover(ticker: str, company_name: str, decision: str, date: str, exchange: str = ""):
    """
    Render the report cover with ticker, company name, and recommendation.
    Investment bank style header.
    """
    decision_upper = decision.upper().strip()

    if "BUY" in decision_upper:
        badge_class = "buy"
        badge_icon = "+"
        badge_text = "BUY"
    elif "SELL" in decision_upper:
        badge_class = "sell"
        badge_icon = "-"
        badge_text = "SELL"
    else:
        badge_class = "hold"
        badge_icon = "="
        badge_text = "HOLD"

    exchange_display = f'<span class="report-exchange">{exchange}</span>' if exchange else ""

    st.markdown(f"""
        <div class="report-cover">
            <div class="report-firm-badge">TradingAgents Research</div>
            <div class="report-ticker">{ticker}</div>
            <div class="report-company-name">{company_name or ticker}</div>
            <div class="recommendation-badge {badge_class}">
                <span class="recommendation-icon">{badge_icon}</span>
                {badge_text}
            </div>
            <div class="report-meta">
                <span class="report-date">Analysis Date: {date}</span>
                {exchange_display}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, section_number: str = ""):
    """Render a professional section header with blue accent bar."""
    number_html = f'<span class="section-number">{section_number}</span>' if section_number else ""
    st.markdown(f"""
        <div class="section-header">
            {number_html}{title}
        </div>
    """, unsafe_allow_html=True)


def render_executive_summary(result: dict, decision: str):
    """Render the executive summary from analysis results."""
    decision_upper = decision.upper().strip()

    if "BUY" in decision_upper:
        stance = "bullish"
        action = "buying"
    elif "SELL" in decision_upper:
        stance = "bearish"
        action = "selling"
    else:
        stance = "neutral"
        action = "holding"

    # Extract key insight from final decision - escape HTML
    final_decision = result.get('final_trade_decision', '')
    summary = escape_html(final_decision[:500]) if final_decision else f"Our multi-agent AI analysis has concluded with a {stance} outlook, recommending {action} this position."

    st.markdown(f"""
        <div class="executive-summary">
            <p>{summary}</p>
        </div>
    """, unsafe_allow_html=True)


def render_investment_thesis(bull_history: str, bear_history: str, judge_decision: str):
    """Render investment thesis with bull/bear cards."""

    # Bull case - escape HTML to prevent rendering issues
    bull_content = escape_html(bull_history[:600]) if bull_history else "Bull case analysis pending..."

    # Bear case - escape HTML to prevent rendering issues
    bear_content = escape_html(bear_history[:600]) if bear_history else "Bear case analysis pending..."

    st.markdown(f"""
        <div class="thesis-grid">
            <div class="thesis-card bull">
                <div class="thesis-card-header">
                    <span class="thesis-card-icon">+</span>
                    <span class="thesis-card-title">Bull Case</span>
                </div>
                <div class="thesis-card-content">{bull_content}</div>
            </div>
            <div class="thesis-card bear">
                <div class="thesis-card-header">
                    <span class="thesis-card-icon">-</span>
                    <span class="thesis-card-title">Bear Case</span>
                </div>
                <div class="thesis-card-content">{bear_content}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Verdict - escape HTML
    verdict_content = escape_html(judge_decision[:800]) if judge_decision else "Research manager verdict pending..."
    st.markdown(f"""
        <div class="verdict-card">
            <div class="verdict-header">
                <span class="verdict-icon">||</span>
                <span class="verdict-title">Research Manager Verdict</span>
            </div>
            <div class="verdict-content">{verdict_content}</div>
        </div>
    """, unsafe_allow_html=True)


def render_risk_matrix(risky: str, safe: str, neutral: str, judge: str):
    """Render risk assessment as a professional matrix."""

    # Escape HTML in all content
    risky_content = escape_html(risky[:400]) if risky else "Aggressive perspective pending..."
    safe_content = escape_html(safe[:400]) if safe else "Conservative perspective pending..."
    neutral_content = escape_html(neutral[:400]) if neutral else "Balanced perspective pending..."

    st.markdown(f"""
        <div class="risk-matrix">
            <div class="risk-card aggressive">
                <div class="risk-label">Aggressive View</div>
                <div class="risk-content">{risky_content}</div>
            </div>
            <div class="risk-card conservative">
                <div class="risk-label">Conservative View</div>
                <div class="risk-content">{safe_content}</div>
            </div>
            <div class="risk-card balanced">
                <div class="risk-label">Balanced View</div>
                <div class="risk-content">{neutral_content}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Risk verdict - escape HTML
    judge_content = escape_html(judge[:800]) if judge else "Risk manager verdict pending..."
    st.markdown(f"""
        <div class="verdict-card">
            <div class="verdict-header">
                <span class="verdict-icon">!</span>
                <span class="verdict-title">Risk Manager Verdict</span>
            </div>
            <div class="verdict-content">{judge_content}</div>
        </div>
    """, unsafe_allow_html=True)


def render_analysis_section(title: str, content: str, icon: str = ""):
    """Render an analysis section with content."""
    if not content or not content.strip():
        st.markdown(f"""
            <div style="color: var(--text-muted); padding: 1rem; text-align: center;
                        background: var(--bg-muted); border-radius: 8px; margin: 1rem 0;">
                No {title.lower()} data available
            </div>
        """, unsafe_allow_html=True)
        return

    # Truncate for display
    display_content = content[:2000]
    if len(content) > 2000:
        display_content += "..."

    st.markdown(f"""
        <div style="background: var(--bg-section); border: 1px solid var(--border-light);
                    border-radius: 8px; padding: 1.5rem; margin: 1rem 0;
                    font-size: 0.95rem; line-height: 1.7; color: var(--text-secondary);">
            {display_content}
        </div>
    """, unsafe_allow_html=True)


def render_appendix(result: dict):
    """Render raw reports in collapsible appendix sections."""
    st.markdown("""
        <div class="appendix-section">
            <div class="appendix-title">Appendix - Raw Analysis Reports</div>
        </div>
    """, unsafe_allow_html=True)

    reports = [
        ("Technical Analysis", result.get('market_report', '')),
        ("Sentiment Analysis", result.get('sentiment_report', '')),
        ("News Analysis", result.get('news_report', '')),
        ("Fundamental Analysis", result.get('fundamentals_report', '')),
        ("Trading Strategy", result.get('trader_investment_plan', '')),
    ]

    for title, content in reports:
        if content and content.strip():
            with st.expander(title, expanded=False):
                escaped_content = escape_html(content[:3000])
                st.markdown(f"""
                    <div class="appendix-content">{escaped_content}</div>
                """, unsafe_allow_html=True)


def render_report_footer(ticker: str, date: str):
    """Render professional disclaimer footer."""
    st.markdown(f"""
        <div class="report-footer">
            <div class="report-footer-disclaimer">
                This report was generated by AlphaDesk AI and is for informational purposes only.
                It does not constitute financial advice, investment recommendations, or an offer to buy or sell securities.
                Past performance is not indicative of future results. Always conduct your own research and consult
                with a qualified financial advisor before making investment decisions.
            </div>
            <div class="report-footer-brand">
                AlphaDesk Research | {ticker} | {date} | Powered by Claude AI
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# SIDEBAR COMPONENTS
# ============================================================================

def render_sidebar_header():
    """Render the sidebar header."""
    st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-logo">α</div>
            <div class="sidebar-title">AlphaDesk</div>
            <div class="sidebar-subtitle">AI Investment Research</div>
        </div>
    """, unsafe_allow_html=True)


def render_profile_switcher():
    """Render Google/AWS-style profile switcher in sidebar."""
    try:
        from tradingagents.ui.profiles import get_profile_manager
        manager = get_profile_manager()
        active = manager.get_active_profile()
        all_profiles = manager.get_all_profiles()
    except Exception:
        # Fallback if profiles not available
        active = None
        all_profiles = []

    if active:
        st.markdown(f"""
            <div class="profile-switcher">
                <div class="profile-current">
                    <div class="profile-avatar" style="background: {active.color};">
                        {active.avatar_initial}
                    </div>
                    <div class="profile-info">
                        <div class="profile-name">{active.name}</div>
                        <div class="profile-email">{active.email or 'Claude Account'}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Profile management expander
        with st.expander("Manage Profiles", expanded=False):
            # List all profiles
            for profile in all_profiles:
                col1, col2 = st.columns([4, 1])
                with col1:
                    marker = " (active)" if profile.is_active else ""
                    if st.button(
                        f"{profile.avatar_initial} {profile.name}{marker}",
                        key=f"switch_profile_{profile.id}",
                        use_container_width=True
                    ):
                        if not profile.is_active:
                            manager.switch_profile(profile.id)
                            st.info("Profile switched. Re-authenticate if using different Claude account.")
                            st.rerun()
                with col2:
                    if not profile.is_active and len(all_profiles) > 1:
                        if st.button("X", key=f"del_profile_{profile.id}"):
                            manager.delete_profile(profile.id)
                            st.rerun()

            st.markdown("---")

            # Add new profile form
            new_name = st.text_input("New profile name", key="new_profile_name")
            if st.button("Add Profile", key="add_profile_btn"):
                if new_name and new_name.strip():
                    manager.add_profile(new_name.strip())
                    st.success(f"Profile '{new_name}' added!")
                    st.rerun()

            # Auth instructions
            st.markdown("""
                <div style="background: #fef7e0; border: 1px solid #b5850b; border-radius: 8px;
                            padding: 0.75rem; margin-top: 1rem; font-size: 0.75rem; color: #6e6e73;">
                    <strong style="color: #b5850b;">To switch Claude accounts:</strong><br>
                    1. Run <code>claude logout</code><br>
                    2. Run <code>claude</code> and login<br>
                    3. Click Connect again
                </div>
            """, unsafe_allow_html=True)


def render_symbol_feedback(resolved: str, metadata: dict):
    """Render symbol resolution feedback."""
    if resolved:
        company = metadata.get('company_name', resolved)
        exchange = metadata.get('exchange', '')
        st.markdown(f"""
            <div class="symbol-resolved">
                <span class="symbol-resolved-ticker">{resolved}</span>
                <span style="color: var(--text-muted); margin: 0 0.5rem;">|</span>
                <span style="color: var(--text-secondary);">{exchange}</span>
                <br>
                <span class="symbol-resolved-name">{company}</span>
            </div>
        """, unsafe_allow_html=True)
    elif 'error' in metadata:
        st.markdown(f"""
            <div class="symbol-error">
                {metadata['error']}
            </div>
        """, unsafe_allow_html=True)


# ============================================================================
# STATE COMPONENTS
# ============================================================================

def render_waiting_state():
    """Render an elegant waiting state."""
    st.markdown("""
        <div class="waiting-container">
            <div class="waiting-icon">||</div>
            <div class="waiting-title">TradingAgents Research</div>
            <div class="waiting-subtitle">
                AI-powered multi-agent analysis for professional trading insights.
                Enter a stock symbol in the sidebar and click Run Analysis.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Quick start guide
    st.markdown("""
        <div style="max-width: 400px; margin: 0 auto; text-align: left;">
            <div style="background: var(--bg-section); border: 1px solid var(--border-light);
                        border-radius: 8px; padding: 1.5rem;">
                <div style="font-weight: 600; margin-bottom: 1rem; color: var(--text-primary);">Quick Start</div>
                <div style="display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="background: var(--accent-blue); color: white; width: 24px; height: 24px;
                                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                font-size: 0.75rem; flex-shrink: 0;">1</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">Enter a stock symbol (e.g., AAPL, RELIANCE)</span>
                </div>
                <div style="display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="background: var(--accent-blue); color: white; width: 24px; height: 24px;
                                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                font-size: 0.75rem; flex-shrink: 0;">2</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">Select analysis date</span>
                </div>
                <div style="display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="background: var(--accent-blue); color: white; width: 24px; height: 24px;
                                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                font-size: 0.75rem; flex-shrink: 0;">3</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">Choose AI analysts</span>
                </div>
                <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                    <span style="background: var(--accent-blue); color: white; width: 24px; height: 24px;
                                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                font-size: 0.75rem; flex-shrink: 0;">4</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem;">Click "Run Analysis"</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_loading_state(message: str = "Generating Report"):
    """Render a loading state."""
    st.markdown(f"""
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-title">{message}</div>
            <div class="loading-subtitle">
                Our AI analysts are evaluating market data, news, and sentiment.
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_error_state(error: str):
    """Render an error state."""
    st.markdown(f"""
        <div class="error-container">
            <div class="error-title">Analysis Error</div>
            <div class="error-message">{error[:1500]}</div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_share_text(ticker: str, decision: str, date: str) -> str:
    """Generate shareable text for social media."""
    decision_upper = decision.upper().strip()

    if "BUY" in decision_upper:
        signal = "BULLISH"
    elif "SELL" in decision_upper:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"

    return f"""
{ticker} Research Report - {signal}

Multi-agent AI analysis complete:
- 4 specialized analysts evaluated
- Investment thesis debated
- Risk assessment performed

Generated by AlphaDesk
Analysis date: {date}

#AlphaDesk #Trading #AI #Research #{ticker}
    """.strip()


def render_footer():
    """Render a simple page footer (for backward compatibility)."""
    st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; margin-top: 2rem;
                    border-top: 1px solid var(--border-light); color: var(--text-muted); font-size: 0.75rem;">
            AlphaDesk | Powered by Claude AI | Not financial advice
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

def render_hero_header(ticker: str, date: str, company_name: str = None):
    """Render header (redirects to report cover for backward compatibility)."""
    render_report_cover(ticker, company_name or ticker, "HOLD", date)


def render_decision_card(decision: str, confidence: str = None):
    """Render decision card (backward compatibility - now part of report cover)."""
    pass  # Decision is now shown in report cover


def render_summary_card(ticker: str, decision: str, key_insight: str = None):
    """Render summary (backward compatibility - now executive summary)."""
    pass  # Summary is now executive summary


def render_pipeline_progress(stages: Dict[str, str]):
    """Render pipeline progress (simplified for new design)."""
    complete_count = sum(1 for s in stages.values() if s == "complete")
    total = len(stages)

    st.markdown(f"""
        <div style="background: var(--bg-muted); padding: 0.75rem 1rem; border-radius: 8px;
                    margin-bottom: 1.5rem; font-size: 0.85rem; color: var(--text-secondary);">
            Analysis Progress: {complete_count}/{total} stages complete
        </div>
    """, unsafe_allow_html=True)


def render_section_card(title: str, content: str, icon: str = ""):
    """Render section card (backward compatibility)."""
    render_analysis_section(title, content, icon)


def render_investment_debate(bull_history: str, bear_history: str, judge_decision: str):
    """Render investment debate (backward compatibility)."""
    render_investment_thesis(bull_history, bear_history, judge_decision)


def render_risk_debate(risky: str, safe: str, neutral: str, judge: str):
    """Render risk debate (backward compatibility)."""
    render_risk_matrix(risky, safe, neutral, judge)


def render_analyst_reports(result: dict):
    """Render analyst reports (now part of appendix)."""
    pass  # Now handled by render_appendix


def render_trader_analysis(plan: str):
    """Render trader analysis (now part of appendix)."""
    pass  # Now handled by render_appendix
