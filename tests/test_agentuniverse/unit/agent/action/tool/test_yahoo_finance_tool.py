# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/06
# @FileName: test_yahoo_finance_tool.py

import sys
import pytest
from unittest.mock import patch, MagicMock

# Mock yfinance before importing the tool
_mock_yf = MagicMock()
sys.modules.setdefault('yfinance', _mock_yf)

from agentuniverse.agent.action.tool.common_tool.yahoo_finance_tool import (
    YahooFinanceTool,
    FinanceMode,
)


def _mock_ticker():
    """Create a mock yfinance.Ticker."""
    ticker = MagicMock()
    ticker.info = {
        "longName": "Test Corp",
        "currentPrice": 150.0,
        "previousClose": 145.0,
        "currency": "USD",
        "marketCap": 2000000000000,
        "trailingPE": 25.5,
        "dayHigh": 152.0,
        "dayLow": 148.0,
        "volume": 50000000,
        "sector": "Technology",
        "industry": "Software",
        "country": "US",
        "website": "https://example.com",
        "fullTimeEmployees": 100000,
        "longBusinessSummary": "A test company.",
        "exchange": "NASDAQ",
    }
    return ticker


def test_yahoo_finance_quote():
    """Test quote mode returns stock price data."""
    ticker = _mock_ticker()
    _mock_yf.Ticker.return_value = ticker

    tool = YahooFinanceTool()
    result = tool.execute(symbol="TEST", mode="quote")

    assert result["symbol"] == "TEST"
    assert result["price"] == 150.0
    assert result["currency"] == "USD"
    assert result["change"] == 5.0
    assert "%" in result["change_percent"]


def test_yahoo_finance_info():
    """Test info mode returns company information."""
    ticker = _mock_ticker()
    _mock_yf.Ticker.return_value = ticker

    tool = YahooFinanceTool()
    result = tool.execute(symbol="TEST", mode="info")

    assert result["name"] == "Test Corp"
    assert result["sector"] == "Technology"
    assert result["industry"] == "Software"


def test_yahoo_finance_invalid_mode():
    """Test that invalid mode raises ValueError."""
    ticker = _mock_ticker()
    _mock_yf.Ticker.return_value = ticker

    tool = YahooFinanceTool()
    with pytest.raises(ValueError):
        tool.execute(symbol="TEST", mode="invalid_mode")


def test_finance_mode_enum():
    """Test FinanceMode enum values."""
    assert FinanceMode.QUOTE.value == "quote"
    assert FinanceMode.HISTORY.value == "history"
    assert FinanceMode.INFO.value == "info"
    assert FinanceMode.FINANCIALS.value == "financials"


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
