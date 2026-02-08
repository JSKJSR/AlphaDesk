import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", "./data"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings - Using Claude Code CLI (your Claude Pro subscription)
    # No API key required! Uses your authenticated Claude Code CLI
    "llm_provider": "claude-code",
    "deep_think_llm": "claude-code",      # Not used - Claude Code uses your subscription model
    "quick_think_llm": "claude-code",     # Not used - Claude Code uses your subscription model
    "backend_url": None,                   # Not used for claude-code
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
    "tool_vendors": {
        "get_fundamentals": "yfinance",       # FREE - Yahoo Finance company info
        "get_global_news": "google",          # FREE - Google News for global news
    },
}
