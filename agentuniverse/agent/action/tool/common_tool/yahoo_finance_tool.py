# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/10
# @Author  : contributor
# @FileName: yahoo_finance_tool.py

"""
Yahoo Finance market-data tool.

Provides stock / ETF / index quotes, historical OHLCV bars, and company
information sourced from Yahoo Finance, addressing the *Yahoo Finance* item of
issue #252 (tool plug-in integration).

The tool is built on top of the ``yfinance`` library (the de-facto Python
client for Yahoo Finance data). ``yfinance`` is imported lazily inside the
methods that need it, so importing this module never requires the dependency —
an agent that never calls the tool pays no install cost, and a missing
``yfinance`` surfaces a clear, actionable error only when the tool is actually
used.

Three operating modes are supported:

* ``quote``   — the latest price, change, and a handful of headline metrics.
* ``history`` — historical OHLCV bars for a configurable period / interval.
* ``info``    — a curated company profile (a stable subset of the Yahoo
  Finance profile; the full ``ticker.info`` payload is intentionally not
  dumped, to keep the agent context compact).

All output is a human-readable string so it can be dropped directly into an
agent's context. The data-fetching helpers are isolated from the formatting
helpers, which keeps the component fully unit-testable without a network
connection: tests stub :meth:`_get_ticker` and feed fixed dicts to the pure
formatters.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.annotation.retry import retry


class YahooFinanceTool(Tool):
    """Yahoo Finance market-data tool.

    Attributes:
        max_history_rows (int): Upper bound on the number of history rows
            returned, to keep the agent context compact.
        quote_fields (List[str]): Keys surfaced in ``quote`` mode, in display
            order.
        info_fields (List[str]): Curated keys surfaced in ``info`` mode, in
            display order. Only these keys are emitted, so the agent context
            is not flooded by the large, unstable ``ticker.info`` payload.
    """

    name: str = "yahoo_finance_tool"
    description: str = (
        "Yahoo Finance market-data tool. Fetches the latest quote, historical "
        "OHLCV bars, or the company profile for a stock / ETF / index symbol "
        "(e.g. 'AAPL', '600519.SS')."
    )
    max_history_rows: int = Field(30, description="Max number of history rows returned.")
    quote_fields: List[str] = [
        "regularMarketPrice", "regularMarketChange", "regularMarketChangePercent",
        "regularMarketVolume", "regularMarketPreviousClose", "marketCap",
        "fiftyTwoWeekLow", "fiftyTwoWeekHigh", "currency",
    ]
    info_fields: List[str] = [
        "longName", "symbol", "quoteType", "currency", "exchange",
        "sector", "industry", "country", "city",
        "marketCap", "enterpriseValue", "enterpriseToRevenue",
        "enterpriseToEbitda", "trailingPE", "forwardPE",
        "dividendYield", "payoutRatio", "beta",
        "profitMargins", "grossMargins", "operatingMargins",
        "returnOnEquity", "returnOnAssets",
        "totalRevenue", "revenueGrowth", "earningsGrowth",
        "totalCash", "totalDebt",
        "fiftyTwoWeekLow", "fiftyTwoWeekHigh",
        "regularMarketPrice", "regularMarketVolume",
        "fullTimeEmployees", "website", "longBusinessSummary",
    ]
    max_business_summary_chars: int = Field(
        400,
        description="Cap on the longBusinessSummary length emitted in info "
                    "mode. The raw field is an unbounded company description, "
                    "so even within the curated info_fields list it is "
                    "truncated to keep the agent context compact.",
    )

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(self,
                mode: str,
                symbol: str,
                period: str = "1mo",
                interval: str = "1d") -> str:
        """Run a Yahoo Finance query.

        Args:
            mode (str): One of ``quote`` / ``history`` / ``info``.
            symbol (str): Ticker symbol, e.g. ``AAPL`` or ``600519.SS``.
            period (str): History period, e.g. ``1mo``, ``3mo``, ``1y``,
                ``max``. Ignored outside ``history`` mode.
            interval (str): History bar interval, e.g. ``1d``, ``1wk``,
                ``1mo``. Ignored outside ``history`` mode.

        Returns:
            str: Human-readable result (or a clear error message).
        """
        symbol = self._normalize_symbol(symbol)
        if not symbol:
            return "Error: 'symbol' is required."
        if mode not in ("quote", "history", "info"):
            return (f"Error: invalid mode '{mode}'. "
                    "Must be one of: quote, history, info.")

        try:
            ticker = self._get_ticker(symbol)
            if mode == "quote":
                return self._format_quote(symbol, self._fetch_quote(ticker))
            if mode == "info":
                return self._format_info(symbol, self._fetch_info(ticker))
            return self._format_history(
                symbol, self._fetch_history(ticker, period=period, interval=interval))
        except ImportError:
            return ("Error: yfinance is required. "
                    "Install it with: pip install yfinance")
        except Exception as exc:  # noqa: BLE001 - surface any fetch error to the agent
            return f"Error fetching data for symbol '{symbol}': {exc}"

    # ------------------------------------------------------------------ #
    # Data fetching (network) — lazy yfinance import, isolated for testing
    # ------------------------------------------------------------------ #

    def _get_ticker(self, symbol: str):
        """Return a ``yfinance.Ticker`` for the symbol (lazy import)."""
        import yfinance  # noqa: WPS433 - lazy on purpose
        return yfinance.Ticker(symbol)

    @retry(3, 1.0)
    def _fetch_quote(self, ticker) -> Dict[str, Any]:
        """Pull the headline quote metrics for the ticker."""
        info = self._safe_info(ticker)
        return {field: info.get(field) for field in self.quote_fields}

    @retry(3, 1.0)
    def _fetch_history(self, ticker, period: str, interval: str) -> List[Dict[str, Any]]:
        """Pull historical OHLCV bars as a list of row dicts (newest first)."""
        df = ticker.history(period=period, interval=interval)
        if df is None or getattr(df, "empty", True):
            return []
        # Reset the date index into a column, then take the most recent rows.
        rows = df.reset_index().rename(columns=str.lower).to_dict(orient="records")
        return rows[::-1][:self.max_history_rows]

    @retry(3, 1.0)
    def _fetch_info(self, ticker) -> Dict[str, Any]:
        """Pull the full company profile for the ticker."""
        return self._safe_info(ticker)

    # ------------------------------------------------------------------ #
    # Formatting (pure) — fully testable without a network
    # ------------------------------------------------------------------ #

    def _format_quote(self, symbol: str, quote: Dict[str, Any]) -> str:
        """Render the quote metrics as a readable block."""
        lines = [f"{symbol} — latest quote"]
        for field in self.quote_fields:
            value = quote.get(field)
            if value is None:
                continue
            lines.append(f"  {field}: {self._humanize(field, value)}")
        if len(lines) == 1:
            return f"{symbol} — no quote data available."
        return "\n".join(lines)

    def _format_history(self, symbol: str, rows: List[Dict[str, Any]]) -> str:
        """Render historical bars as a compact, aligned table."""
        if not rows:
            return f"{symbol} — no historical data available."
        columns = ["date", "open", "high", "low", "close", "volume"]
        header = " | ".join(col.ljust(8) for col in columns)
        body = []
        for row in rows:
            date = self._row_value(row, "date", "index")
            cells = [
                str(date)[:10].ljust(8) if date is not None else "-".ljust(8),
                self._fmt_num(self._row_value(row, "open")),
                self._fmt_num(self._row_value(row, "high")),
                self._fmt_num(self._row_value(row, "low")),
                self._fmt_num(self._row_value(row, "close")),
                self._fmt_int(self._row_value(row, "volume")),
            ]
            body.append(" | ".join(cell.ljust(8) for cell in cells))
        return "\n".join([f"{symbol} — history (newest first)", header] + body)

    def _format_info(self, symbol: str, info: Dict[str, Any]) -> str:
        """Render a curated slice of the company profile.

        Only the keys in :attr:`info_fields` are emitted (those that are
        actually present and non-empty). Unknown ``ticker.info`` keys are
        deliberately dropped, because the raw payload is large and varies
        between symbols / yfinance releases — emitting it verbatim would flood
        the agent context with an unstable, hard-to-consume blob.
        """
        if not info:
            return f"{symbol} — no company info available."
        lines = [f"{symbol} — company profile"]
        for key in self.info_fields:
            value = info.get(key)
            if value in (None, ""):
                continue
            if key == "longBusinessSummary" and isinstance(value, str):
                value = self._truncate(value, self.max_business_summary_chars)
            lines.append(f"  {key}: {self._humanize(key, value)}")
        if len(lines) == 1:
            return f"{symbol} — no company info available."
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Small helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_symbol(symbol: Optional[str]) -> str:
        """Uppercase and trim the symbol; return '' for blank input."""
        if not symbol or not str(symbol).strip():
            return ""
        return str(symbol).strip().upper()

    @staticmethod
    def _safe_info(ticker) -> Dict[str, Any]:
        """Best-effort ``ticker.info``; tolerates yfinance returning None."""
        try:
            info = ticker.info
        except Exception:  # noqa: BLE001
            return {}
        return info or {}

    @staticmethod
    def _row_value(row: Dict[str, Any], *keys: str) -> Any:
        """Return the first present key from ``keys`` in ``row``."""
        for key in keys:
            if key in row and row[key] is not None:
                return row[key]
        return None

    @staticmethod
    def _fmt_num(value: Any) -> str:
        """Format a price-like number to a concise string."""
        if value is None:
            return "-"
        try:
            return f"{float(value):.2f}"
        except (TypeError, ValueError):
            return str(value)

    @staticmethod
    def _fmt_int(value: Any) -> str:
        """Format a volume-like number with thousands separators."""
        if value is None:
            return "-"
        try:
            return f"{int(float(value)):,}"
        except (TypeError, ValueError):
            return str(value)

    def _humanize(self, key: str, value: Any) -> str:
        """Render large monetary values compactly for human readability."""
        if key in ("marketCap",) and isinstance(value, (int, float)):
            return self._compact_number(value)
        if key in ("regularMarketVolume",) and isinstance(value, (int, float)):
            return self._fmt_int(value)
        if isinstance(value, float):
            return self._fmt_num(value)
        return str(value)

    @staticmethod
    def _compact_number(value: float) -> str:
        """Abbreviate a large number using T / B / M / K suffixes."""
        for unit, factor in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
            if abs(value) >= factor:
                return f"{value / factor:.2f}{unit}"
        return f"{value:.2f}"

    @staticmethod
    def _truncate(value: str, limit: int) -> str:
        """Truncate a long string to ``limit`` chars with an ellipsis.

        ``longBusinessSummary`` (and any other free-text profile field) can run
        to thousands of characters; capping it keeps the agent context compact.
        """
        if limit <= 0 or len(value) <= limit:
            return value
        return value[:limit].rstrip() + "…"
