# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/16 21:38
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: test_arxiv_tool.py

import unittest
from agentuniverse.agent.action.tool.common_tool.arxiv_tool import ArxivTool, SearchMode
from agentuniverse.agent.action.tool.tool import ToolInput


class ArxivToolTest(unittest.TestCase):
    """
    Test cases for ArxivTool class
    """

    def setUp(self) -> None:
        self.tool = ArxivTool()

    def test_search_papers(self) -> None:
        tool_input = ToolInput({
            'input': 'machine learning',
            'mode': SearchMode.SEARCH.value
        })
        result = self.tool.execute(tool_input)
        self.assertIsNotNone(result)
        self.assertGreater(len(result.strip()), 0)

    def test_get_paper_detail(self) -> None:
        tool_input = ToolInput({
            'input': '1605.08386v1',
            'mode': SearchMode.DETAIL.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue(result!= "")

    def test_invalid_mode(self) -> None:
        tool_input = ToolInput({
            'input': 'test',
            'mode': 'invalid_mode'
        })
        with self.assertRaises(ValueError):
            self.tool.execute(tool_input)


if __name__ == '__main__':
    unittest.main()
