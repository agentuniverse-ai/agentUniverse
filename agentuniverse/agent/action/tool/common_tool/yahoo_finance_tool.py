# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/06
# @FileName: yahoo_finance_tool.py

from typing import Optional, Any, Dict, List, Union
from enum import Enum
from dataclasses import dataclass

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.annotation.retry import retry


class FinanceMode(Enum):
    QUOTE = "quote"
    HISTORY = "history"
    INFO = "info"
    FINANCIALS = "financials"


@dataclass
class StockQuote:
    symbol: str
    name: str
    price: float
    currency: str
    market_cap: str
    pe_ratio: float
    day_high: float
    day_low: float
    volume: int
    change: float
    change_percent: float


class YahooFinanceTool(Tool):
    """Yahoo Finance tool for retrieving stock market data.

    Uses the yfinance library to fetch real-time and historical
    financial data from Yahoo Finance.

    Modes:
        quote: Get current stock quote (price, market cap, P/E, etc.)
        history: Get historical price data
        info: Get company information (sector, industry, description)
        financials: Get financial statements (income, balance sheet, cash flow)
    """

    max_results: int = Field(default=30, description="Max number of historical data points")

    def execute(
        self,
        symbol: str,
        mode: str,
        period: str = "1mo",
        interval: str = "1d",
        statement: str = "income",
    ) -> Union[Dict, str]:
        """Execute the Yahoo Finance tool.

        Args:
            symbol: Stock ticker symbol (e.g. AAPL, GOOGL, MSFT).
            mode: One of quote, history, info, financials.
            period: Time period for historical data (1d,5d,1mo,3mo,6mo,1y,2y,5y,max).
            interval: Data interval for historical data (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo).
            statement: Financial statement type for financials mode (income, balance, cashflow).
        """
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError(
                "yfinance is required. Install with: pip install yfinance"
            )

        if mode not in [m.value for m in FinanceMode]:
            raise ValueError(
                f"Invalid mode: {mode}. Must be one of {[m.value for m in FinanceMode]}"
            )

        ticker = yf.Ticker(symbol)

        if mode == FinanceMode.QUOTE.value:
            return self._get_quote(ticker, symbol)
        elif mode == FinanceMode.HISTORY.value:
            return self._get_history(ticker, period, interval)
        elif mode == FinanceMode.INFO.value:
            return self._get_info(ticker)
        elif mode == FinanceMode.FINANCIALS.value:
            return self._get_financials(ticker, statement)

    @retry(3, 1.0)
    def _get_quote(self, ticker, symbol: str) -> Dict:
        """Get current stock quote."""
        info = ticker.info or {}
        quote = StockQuote(
            symbol=symbol,
            name=info.get("longName", info.get("shortName", symbol)),
            price=round(info.get("currentPrice", info.get("regularMarketPrice", 0)), 2),
            currency=info.get("currency", "USD"),
            market_cap=self._format_large_number(info.get("marketCap", 0)),
            pe_ratio=round(info.get("trailingPE", 0), 2),
            day_high=round(info.get("dayHigh", 0), 2),
            day_low=round(info.get("dayLow", 0), 2),
            volume=info.get("volume", 0),
            change=round(
                info.get("currentPrice", 0) - info.get("previousClose", 0), 2
            ),
            change_percent=round(
                (
                    (info.get("currentPrice", 0) - info.get("previousClose", 0))
                    / max(info.get("previousClose", 1), 1)
                )
                * 100,
                2,
            ),
        )
        return {
            "symbol": quote.symbol,
            "name": quote.name,
            "price": quote.price,
            "currency": quote.currency,
            "market_cap": quote.market_cap,
            "pe_ratio": quote.pe_ratio,
            "day_high": quote.day_high,
            "day_low": quote.day_low,
            "volume": quote.volume,
            "change": quote.change,
            "change_percent": f"{quote.change_percent}%",
        }

    @retry(3, 1.0)
    def _get_history(self, ticker, period: str, interval: str) -> List[Dict]:
        """Get historical price data."""
        hist = ticker.history(period=period, interval=interval)
        if hist.empty:
            return {"error": "No historical data found for the given parameters."}
        results = []
        for idx, row in hist.head(self.max_results).iterrows():
            results.append(
                {
                    "date": str(idx),
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                }
            )
        return results

    @retry(3, 1.0)
    def _get_info(self, ticker) -> Dict:
        """Get company information."""
        info = ticker.info or {}
        return {
            "name": info.get("longName", info.get("shortName", "N/A")),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "country": info.get("country", "N/A"),
            "website": info.get("website", "N/A"),
            "employees": info.get("fullTimeEmployees", "N/A"),
            "description": info.get("longBusinessSummary", "N/A"),
            "currency": info.get("currency", "N/A"),
            "exchange": info.get("exchange", "N/A"),
        }

    @retry(3, 1.0)
    def _get_financials(self, ticker, statement: str) -> Dict:
        """Get financial statements."""
        if statement == "income":
            df = ticker.financials
            label = "Income Statement"
        elif statement == "balance":
            df = ticker.balance_sheet
            label = "Balance Sheet"
        elif statement == "cashflow":
            df = ticker.cashflow
            label = "Cash Flow Statement"
        else:
            return {"error": f"Invalid statement type: {statement}. Use income, balance, or cashflow."}

        if df is None or df.empty:
            return {"error": f"No {label} data available."}

        result = {"statement_type": label, "periods": {}}
        for col in df.columns:
            period_key = str(col).split(" ")[0]
            result["periods"][period_key] = {
                str(row): self._safe_value(row_val)
                for row, row_val in df[col].items()
            }
        return result

    @staticmethod
    def _format_large_number(num: int | float) -> str:
        """Format large numbers to human-readable form."""
        if num == 0:
            return "N/A"
        for unit in ["", "K", "M", "B", "T"]:
            if abs(num) < 1000:
                return f"{num:.2f}{unit}"
            num /= 1000.0
        return f"{num:.2f}T"

    @staticmethod
    def _safe_value(val: Any) -> Any:
        """Safely convert a value for JSON serialization."""
        if hasattr(val, "item"):
            return val.item()
        try:
            return float(val)
        except (TypeError, ValueError):
            return str(val)
