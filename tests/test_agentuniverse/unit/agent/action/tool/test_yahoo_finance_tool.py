# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/18 10:00
# @Author  : yansq
# @Email   : felzyan33@gmail.com
# @FileName: yahoo_finance_tool.py

import unittest
from agentuniverse.agent.action.tool.common_tool.yahoo_finance_tool import YahooFinanceTool, YahooFinanceSearchMode

class YahooFinanceToolTest(unittest.TestCase):
    """
    Test cases for YahooFinanceTool class
    """
    def setUp(self) -> None:
        self.tool = YahooFinanceTool()

    def test_get_ticker_info(self) -> None:
        tool_input = {
            'mode': YahooFinanceSearchMode.TICKER_INFO.value,
            'ticker': 'AAPL'
        }
        result = self.tool.execute(**tool_input)
        self.assertIsInstance(result, dict)
        self.assertNotIn('error', result)
        self.assertEqual(result.get('symbol'), 'AAPL')

    def test_get_historical_data(self) -> None:
        tool_input = {
            'mode': YahooFinanceSearchMode.HISTORICAL_DATA.value,
            'ticker': 'MSFT',
            'period': '1mo',
            'interval': '1d'
        }
        result = self.tool.execute(**tool_input)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], dict)
        self.assertNotIn('error', result[0])

    def test_get_ticker_news(self) -> None:
        tool_input = {
            'mode': YahooFinanceSearchMode.TICKER_NEWS.value,
            'ticker': 'META',
        }
        result = self.tool.execute(**tool_input)
        self.assertIsInstance(result, list)
        # News can be empty, so we just check if it's a list
        if len(result) > 0:
            self.assertIsInstance(result[0], dict)
            self.assertNotIn('error', result[0])

if __name__ == '__main__':
    unittest.main()