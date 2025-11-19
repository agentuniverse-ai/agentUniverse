#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Yahoo Finance Tool for agentUniverse framework.
"""

import yfinance as yf
from typing import Optional
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.logging.logging_util import LOGGER


class YahooFinanceTool(Tool):
    """Yahoo Finance Tool for retrieving financial data."""

    def execute(self, tool_input: ToolInput):
        """Execute the Yahoo Finance tool.

        Args:
            tool_input (ToolInput): The input parameters for the tool.

        Returns:
            dict: The financial data retrieved from Yahoo Finance.
        """
        try:
            # Get the ticker symbol from input
            ticker = tool_input.get_data('ticker')
            if not ticker:
                raise ValueError("Ticker symbol is required")

            # Get additional parameters
            period = tool_input.get_data('period', '1mo')  # Default to 1 month
            interval = tool_input.get_data('interval', '1d')  # Default to daily

            # Create Yahoo Finance ticker object
            ticker_obj = yf.Ticker(ticker)

            # Get historical data
            hist_data = ticker_obj.history(period=period, interval=interval)

            # Convert to dict for serialization
            result = {
                'symbol': ticker,
                'period': period,
                'interval': interval,
                'history': hist_data.to_dict()
            }

            return result

        except Exception as e:
            LOGGER.error(f"Error retrieving data from Yahoo Finance: {str(e)}")
            raise e