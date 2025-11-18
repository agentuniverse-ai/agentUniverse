# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/18 10:00
# @Author  : yansq
# @Email   : felzyan33@gmail.com
# @FileName: yahoo_finance_tool.py

import yfinance as yf
import json
from enum import Enum
from typing import List, Dict, Any
from pydantic import Field
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.annotation.retry import retry


class YahooFinanceSearchMode(Enum):
    """Yahoo Finance search mode enum"""
    TICKER_INFO = "ticker_info"
    HISTORICAL_DATA = "historical_data"
    TICKER_NEWS = "ticker_news"


class YahooFinanceTool(Tool):
    """Yahoo Finance Tool for fetching stock data."""

    name: str = 'yahoo_finance_tool'
    description: str = 'A tool for fetching financial data from Yahoo Finance, including stock prices, historical data, and news.'

    @retry(3, 1.0)
    def get_ticker_info(self, ticker: str = Field(..., description="The stock ticker symbol, e.g., 'AAPL' for Apple Inc.")) -> Dict[str, Any]:
        """Get comprehensive information for a given stock ticker.

        Args:
            ticker (str): The stock ticker symbol.

        Returns:
            Dict[str, Any]: A dictionary containing the ticker information or an error message.
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            if not info or info.get('trailingPegRatio') is None:
                return {"error": f"Invalid ticker symbol or no data found for '{ticker}'. Please provide a valid ticker."}
            return info
        except Exception as e:
            return {"error": f"An error occurred while fetching ticker info for '{ticker}': {str(e)}"}

    @retry(3, 1.0)
    def get_historical_data(
            self,
            ticker: str = Field(..., description="The stock ticker symbol, e.g., 'MSFT' for Microsoft."),
            period: str = Field(default="1mo",
                                description="The time period for the data. Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max."),
            interval: str = Field(default="1d",
                                  description="The data interval. Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.")
    ) -> List[Dict[str, Any]]:
        """Get historical market data (OHLC) for a given stock ticker.

        Argssymotion-prefix):
            ticker (str): The stock ticker symbol.
            period (str): The time period for the data.
            interval (str): The data interval.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the historical data or an error message.
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period=period, interval=interval)
            if hist.empty:
                return [{"error": f"No historical data found for ticker '{ticker}' with the given parameters (period='{period}', interval='{interval}')."}]
            hist.reset_index(inplace=True)
            for col in hist.select_dtypes(include=['datetime64[ns, UTC]']).columns:
                hist[col] = hist[col].astype(str)
            return json.loads(hist.to_json(orient='records', date_format='iso'))
        except Exception as e:
            return [{"error": f"An error occurred while fetching historical data for '{ticker}': {str(e)}"}]

    @retry(3, 1.0)
    def get_ticker_news(self, ticker: str = Field(..., description="The stock ticker symbol, e.g., 'GOOGL' for Alphabet Inc.")) -> List[Dict[str, Any]]:
        """Get recent news articles for a given stock ticker.

        Args:
            ticker (str): The stock ticker symbol.

        Returns:
            List[Dict[str, Any]]: A list of news articles or an error message.
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            news = ticker_obj.news
            if not news:
                return [{"news": [], "message": f"No news found for ticker '{ticker}'."}]
            return news
        except Exception as e:
            return [{"error": f"An error occurred while fetching news for '{ticker}': {str(e)}"}]

    def execute(self,
                mode: str,
                ticker: str = None,
                period: str = None,
                interval: str = None
                ) -> List[Dict[str, Any]] | Dict[str, Any]:
        if mode == YahooFinanceSearchMode.TICKER_INFO.value:
            if ticker is None:
                raise ValueError("Ticker symbol is required for ticker info mode.")
            return self.get_ticker_info(ticker)
        elif mode == YahooFinanceSearchMode.HISTORICAL_DATA.value:
            if ticker is None:
                raise ValueError("Ticker symbol is required for historical data mode.")
            return self.get_historical_data(ticker, period, interval)
        elif mode == YahooFinanceSearchMode.TICKER_NEWS.value:
            if ticker is None:
                raise ValueError("Ticker symbol is required for ticker news mode.")
            return self.get_ticker_news(ticker)
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {[m.value for m in YahooFinanceSearchMode]}")