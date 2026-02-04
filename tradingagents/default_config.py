import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", "./data"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings - Using Anthropic Claude
    "llm_provider": "anthropic",
    "deep_think_llm": "claude-sonnet-4-20250514",      # Deep thinking tasks (analysis, debates)
    "quick_think_llm": "claude-sonnet-4-20250514",     # Quick tasks (summaries, simple responses)
    "backend_url": "https://api.anthropic.com",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration - Prioritize FREE sources (yfinance, google)
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",        # FREE - Yahoo Finance
        "technical_indicators": "yfinance",   # FREE - Yahoo Finance
        "fundamental_data": "yfinance",       # FREE - Yahoo Finance (balance sheet, cashflow, income)
        "news_data": "google",                # FREE - Google News
    },
    # Tool-level configuration (takes precedence over category-level)
    # Only get_fundamentals requires Alpha Vantage (optional - will fail gracefully if no key)
    "tool_vendors": {
        "get_fundamentals": "alpha_vantage",  # Requires ALPHA_VANTAGE_API_KEY (free tier available)
    },
}
