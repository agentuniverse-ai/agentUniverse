#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/19 19:16
# @Author  : beikai
# @Email   : beikai.yzw@antgroup.com
# @FileName: test_yahoo_finance.py

import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.yahoo_finance import YahooFinanceTool


class YahooFinanceToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = YahooFinanceTool()
        self.tool.name = "yahoo_finance_tool"
        self.tool.description = "Retrieve financial data from Yahoo Finance"

    @patch('agentuniverse.agent.action.tool.common_tool.yahoo_finance.yf')
    def test_execute_successful(self, mock_yf):
        # 创建模拟的返回数据
        mock_history_data = MagicMock()
        mock_history_data.to_dict.return_value = {
            'Open': {0: 150.0},
            'Close': {0: 155.0}
        }

        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_history_data
        mock_yf.Ticker.return_value = mock_ticker

        # 执行工具
        tool_input = ToolInput({
            'ticker': 'AAPL',
            'period': '1mo',
            'interval': '1d'
        })

        result = self.tool.execute(tool_input)
        print(result)

        # 验证结果
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['period'], '1mo')
        self.assertEqual(result['interval'], '1d')
        self.assertIn('history', result)

        # 验证mock被正确调用
        mock_yf.Ticker.assert_called_once_with('AAPL')
        mock_ticker.history.assert_called_once_with(period='1mo', interval='1d')

    def test_execute_missing_ticker(self):
        # 测试缺少ticker参数的情况
        tool_input = ToolInput({
            'period': '1mo',
            'interval': '1d'
        })

        with self.assertRaises(ValueError) as context:
            self.tool.execute(tool_input)

        self.assertIn("Ticker symbol is required", str(context.exception))

    @patch('agentuniverse.agent.action.tool.common_tool.yahoo_finance.yf')
    def test_execute_with_defaults(self, mock_yf):
        # 测试使用默认参数
        mock_history_data = MagicMock()
        mock_history_data.to_dict.return_value = {
            'Open': {0: 150.0},
            'Close': {0: 155.0}
        }

        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_history_data
        mock_yf.Ticker.return_value = mock_ticker

        # 不提供period和interval，使用默认值
        tool_input = ToolInput({
            'ticker': 'GOOGL'
        })

        result = self.tool.execute(tool_input)

        # 验证默认值被正确使用
        self.assertEqual(result['symbol'], 'GOOGL')
        self.assertEqual(result['period'], '1mo')  # 默认值
        self.assertEqual(result['interval'], '1d')  # 默认值

        # 验证mock被正确调用
        mock_yf.Ticker.assert_called_once_with('GOOGL')
        mock_ticker.history.assert_called_once_with(period='1mo', interval='1d')

    @patch('agentuniverse.agent.action.tool.common_tool.yahoo_finance.yf')
    def test_execute_yfinance_exception(self, mock_yf):
        # 模拟yfinance抛出异常
        mock_yf.Ticker.side_effect = Exception("Network error")

        tool_input = ToolInput({
            'ticker': 'MSFT',
            'period': '1mo',
            'interval': '1d'
        })

        with self.assertRaises(Exception) as context:
            self.tool.execute(tool_input)

        self.assertIn("Network error", str(context.exception))


if __name__ == '__main__':
    unittest.main()