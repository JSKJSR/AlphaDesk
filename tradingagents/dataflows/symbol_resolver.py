"""
Stock Symbol Resolution Module.

Automatically resolves simplified stock symbols to their full exchange-qualified form.
Supports NSE (.NS), BSE (.BO), and US exchanges.

Example:
    >>> from tradingagents.dataflows.symbol_resolver import resolve_symbol
    >>> resolved, meta = resolve_symbol("RELIANCE")
    >>> print(resolved)  # "RELIANCE.NS"
    >>> print(meta['exchange'])  # "NSE"
"""

import yfinance as yf
from typing import Optional, Dict, Tuple
from functools import lru_cache
import json
import os


# Exchange priority for Indian stocks (NSE first, then BSE)
INDIAN_EXCHANGE_PRIORITY = ['.NS', '.BO']

# Known symbol mappings for common stocks (instant resolution)
KNOWN_MAPPINGS = {
    # Top Indian stocks (Nifty 50)
    'RELIANCE': 'RELIANCE.NS',
    'TCS': 'TCS.NS',
    'INFY': 'INFY.NS',
    'HDFCBANK': 'HDFCBANK.NS',
    'HDFC': 'HDFCBANK.NS',
    'ICICIBANK': 'ICICIBANK.NS',
    'SBIN': 'SBIN.NS',
    'BHARTIARTL': 'BHARTIARTL.NS',
    'AIRTEL': 'BHARTIARTL.NS',
    'ITC': 'ITC.NS',
    'KOTAKBANK': 'KOTAKBANK.NS',
    'LT': 'LT.NS',
    'AXISBANK': 'AXISBANK.NS',
    'WIPRO': 'WIPRO.NS',
    'HCLTECH': 'HCLTECH.NS',
    'MARUTI': 'MARUTI.NS',
    'TATAMOTORS': 'TATAMOTORS.NS',
    'TATASTEEL': 'TATASTEEL.NS',
    'SUNPHARMA': 'SUNPHARMA.NS',
    'BAJFINANCE': 'BAJFINANCE.NS',
    'ASIANPAINT': 'ASIANPAINT.NS',
    'HINDALCO': 'HINDALCO.NS',
    'JSWSTEEL': 'JSWSTEEL.NS',
    'NTPC': 'NTPC.NS',
    'POWERGRID': 'POWERGRID.NS',
    'ONGC': 'ONGC.NS',
    'COALINDIA': 'COALINDIA.NS',
    'INDUSINDBK': 'INDUSINDBK.NS',
    'ULTRACEMCO': 'ULTRACEMCO.NS',
    'TITAN': 'TITAN.NS',
    'TECHM': 'TECHM.NS',
    'BAJAJFINSV': 'BAJAJFINSV.NS',
    'ADANIENT': 'ADANIENT.NS',
    'ADANIPORTS': 'ADANIPORTS.NS',
    'DRREDDY': 'DRREDDY.NS',
    'CIPLA': 'CIPLA.NS',
    'BRITANNIA': 'BRITANNIA.NS',
    'DIVISLAB': 'DIVISLAB.NS',
    'EICHERMOT': 'EICHERMOT.NS',
    'HEROMOTOCO': 'HEROMOTOCO.NS',
    'BAJAJ-AUTO': 'BAJAJ-AUTO.NS',
    'GRASIM': 'GRASIM.NS',
    'NESTLEIND': 'NESTLEIND.NS',
    'APOLLOHOSP': 'APOLLOHOSP.NS',
    'TATACONSUM': 'TATACONSUM.NS',
    'HINDUNILVR': 'HINDUNILVR.NS',
    'HUL': 'HINDUNILVR.NS',
    'BPCL': 'BPCL.NS',
    'UPL': 'UPL.NS',
    'SHREECEM': 'SHREECEM.NS',

    # Top US stocks (no suffix needed)
    'AAPL': 'AAPL',
    'APPLE': 'AAPL',
    'MSFT': 'MSFT',
    'MICROSOFT': 'MSFT',
    'GOOGL': 'GOOGL',
    'GOOG': 'GOOG',
    'GOOGLE': 'GOOGL',
    'AMZN': 'AMZN',
    'AMAZON': 'AMZN',
    'TSLA': 'TSLA',
    'TESLA': 'TSLA',
    'META': 'META',
    'FACEBOOK': 'META',
    'NVDA': 'NVDA',
    'NVIDIA': 'NVDA',
    'JPM': 'JPM',
    'V': 'V',
    'VISA': 'V',
    'JNJ': 'JNJ',
    'WMT': 'WMT',
    'WALMART': 'WMT',
    'PG': 'PG',
    'MA': 'MA',
    'MASTERCARD': 'MA',
    'UNH': 'UNH',
    'HD': 'HD',
    'DIS': 'DIS',
    'DISNEY': 'DIS',
    'PYPL': 'PYPL',
    'PAYPAL': 'PYPL',
    'BAC': 'BAC',
    'NFLX': 'NFLX',
    'NETFLIX': 'NFLX',
    'ADBE': 'ADBE',
    'ADOBE': 'ADBE',
    'CRM': 'CRM',
    'SALESFORCE': 'CRM',
    'INTC': 'INTC',
    'INTEL': 'INTC',
    'AMD': 'AMD',
    'CSCO': 'CSCO',
    'CISCO': 'CSCO',
    'ORCL': 'ORCL',
    'ORACLE': 'ORCL',

    # Indices
    'NIFTY': '^NSEI',
    'NIFTY50': '^NSEI',
    'SENSEX': '^BSESN',
    'SPX': '^GSPC',
    'SP500': '^GSPC',
    'DOWJONES': '^DJI',
    'DOW': '^DJI',
    'NASDAQ': '^IXIC',
}

# Cache file name
CACHE_FILE = 'symbol_cache.json'


class SymbolResolver:
    """
    Resolves simplified stock symbols to exchange-qualified forms.

    Features:
    - Known mappings for instant resolution of common stocks
    - Dynamic resolution via yfinance validation
    - Caching of successful resolutions
    - Metadata extraction (company name, exchange, sector)
    """

    def __init__(self, cache_dir: str = None):
        """
        Initialize the symbol resolver.

        Args:
            cache_dir: Directory for cache file. Defaults to dataflows/data_cache/
        """
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(__file__), 'data_cache'
        )
        self.cache_path = os.path.join(self.cache_dir, CACHE_FILE)
        self._load_cache()

    def _load_cache(self):
        """Load cached resolutions from disk."""
        self.cache = {}
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r') as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.cache = {}

    def _save_cache(self):
        """Save resolutions to disk cache."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except IOError:
            pass  # Silently fail cache writes

    def _validate_symbol(self, symbol: str) -> bool:
        """
        Check if a symbol is valid on Yahoo Finance.

        Args:
            symbol: Full symbol to validate (e.g., "RELIANCE.NS")

        Returns:
            True if valid and has market data
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            # Check for meaningful data
            return (
                info.get('regularMarketPrice') is not None or
                info.get('previousClose') is not None or
                info.get('symbol') is not None
            )
        except Exception:
            return False

    def _is_likely_indian(self, symbol: str) -> bool:
        """
        Heuristic to detect if symbol is likely an Indian stock.

        Args:
            symbol: Raw symbol input

        Returns:
            True if likely Indian stock
        """
        symbol_upper = symbol.upper()

        # Already has exchange suffix
        if symbol_upper.endswith('.NS') or symbol_upper.endswith('.BO'):
            return True

        # Check known Indian mappings
        if symbol_upper in KNOWN_MAPPINGS:
            resolved = KNOWN_MAPPINGS[symbol_upper]
            return resolved.endswith('.NS') or resolved.endswith('.BO')

        # Common Indian stock patterns
        indian_patterns = ['BANK', 'PHARMA', 'STEEL', 'MOTORS', 'FINANCE', 'CEMENT', 'POWER']
        for pattern in indian_patterns:
            if pattern in symbol_upper:
                return True

        # Check if it's a longer name (Indian tickers tend to be longer)
        if len(symbol_upper) > 6 and not symbol_upper.startswith('^'):
            return True

        return False

    def resolve(self, symbol: str) -> Tuple[Optional[str], Dict]:
        """
        Resolve a symbol to its full exchange-qualified form.

        Args:
            symbol: User-entered symbol (e.g., "RELIANCE" or "RELIANCE.NS")

        Returns:
            Tuple of (resolved_symbol, metadata)
            - resolved_symbol: Full symbol or None if not found
            - metadata: Dict with original, resolved, exchange, company_name, etc.
        """
        if not symbol or not symbol.strip():
            return None, {'error': 'Empty symbol'}

        symbol_upper = symbol.upper().strip()

        # Already has exchange suffix or is an index - validate and return
        if '.' in symbol_upper or symbol_upper.startswith('^'):
            if self._validate_symbol(symbol_upper):
                return self._get_metadata(symbol_upper, symbol)
            else:
                return None, {
                    'error': f"Symbol '{symbol}' not found",
                    'original': symbol
                }

        # Check known mappings first (instant resolution)
        if symbol_upper in KNOWN_MAPPINGS:
            resolved = KNOWN_MAPPINGS[symbol_upper]
            return self._get_metadata(resolved, symbol)

        # Check cache
        if symbol_upper in self.cache:
            cached = self.cache[symbol_upper]
            return cached['resolved'], {**cached, 'is_cached': True}

        # Dynamic resolution
        resolved = self._dynamic_resolve(symbol_upper)
        if resolved:
            metadata = self._get_metadata(resolved, symbol)
            # Cache the resolution
            self.cache[symbol_upper] = {
                'resolved': resolved,
                'original': symbol,
                **metadata[1]
            }
            self._save_cache()
            return resolved, metadata[1]

        return None, {
            'error': f"Could not resolve symbol '{symbol}'",
            'original': symbol,
            'suggestions': self._get_suggestions(symbol_upper)
        }

    def _dynamic_resolve(self, symbol: str) -> Optional[str]:
        """
        Try to resolve symbol by testing exchanges.

        Args:
            symbol: Uppercase symbol without suffix

        Returns:
            Resolved symbol or None
        """
        # If looks like Indian stock, try Indian exchanges first
        if self._is_likely_indian(symbol):
            for suffix in INDIAN_EXCHANGE_PRIORITY:
                candidate = symbol + suffix
                if self._validate_symbol(candidate):
                    return candidate

        # Try US (no suffix) first for other stocks
        if self._validate_symbol(symbol):
            return symbol

        # Try all major exchanges as fallback
        for suffix in ['.NS', '.BO', '.L', '.DE', '.PA', '.TO']:
            candidate = symbol + suffix
            if self._validate_symbol(candidate):
                return candidate

        return None

    def _get_metadata(self, resolved: str, original: str) -> Tuple[str, Dict]:
        """
        Get metadata for a resolved symbol.

        Args:
            resolved: Full resolved symbol
            original: Original user input

        Returns:
            Tuple of (resolved_symbol, metadata_dict)
        """
        try:
            ticker = yf.Ticker(resolved)
            info = ticker.info

            # Determine exchange
            exchange = 'US'
            exchange_name = 'US Stock'
            if resolved.endswith('.NS'):
                exchange = 'NSE'
                exchange_name = 'National Stock Exchange (India)'
            elif resolved.endswith('.BO'):
                exchange = 'BSE'
                exchange_name = 'Bombay Stock Exchange (India)'
            elif resolved.endswith('.L'):
                exchange = 'LSE'
                exchange_name = 'London Stock Exchange'
            elif resolved.startswith('^'):
                exchange = 'INDEX'
                exchange_name = 'Market Index'

            return resolved, {
                'original': original,
                'resolved': resolved,
                'exchange': exchange,
                'exchange_name': exchange_name,
                'company_name': info.get('longName') or info.get('shortName') or resolved,
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'currency': info.get('currency', 'USD'),
                'is_cached': False
            }
        except Exception as e:
            return resolved, {
                'original': original,
                'resolved': resolved,
                'exchange': 'Unknown',
                'exchange_name': 'Unknown',
                'company_name': resolved,
                'error': str(e),
                'is_cached': False
            }

    def _get_suggestions(self, symbol: str) -> list:
        """
        Get suggestions for similar symbols.

        Args:
            symbol: Symbol that couldn't be resolved

        Returns:
            List of similar known symbols
        """
        suggestions = []
        symbol_lower = symbol.lower()

        for known in KNOWN_MAPPINGS.keys():
            # Simple similarity check
            if (symbol_lower in known.lower() or
                known.lower() in symbol_lower or
                symbol_lower[:3] == known.lower()[:3]):
                suggestions.append(known)

        return suggestions[:5]  # Return top 5 suggestions


# Singleton instance
_resolver = None


def get_resolver() -> SymbolResolver:
    """Get the singleton symbol resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = SymbolResolver()
    return _resolver


def resolve_symbol(symbol: str) -> Tuple[Optional[str], Dict]:
    """
    Convenience function to resolve a symbol.

    Args:
        symbol: User-entered stock symbol

    Returns:
        Tuple of (resolved_symbol, metadata)

    Example:
        >>> resolved, meta = resolve_symbol("RELIANCE")
        >>> print(resolved)  # "RELIANCE.NS"
        >>> print(meta['company_name'])  # "Reliance Industries Limited"
    """
    return get_resolver().resolve(symbol)
