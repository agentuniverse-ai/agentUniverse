# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/16 21:38
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: test_arxiv_tool.py

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool.arxiv_tool import ArxivTool, SearchMode
from agentuniverse.agent.action.tool.tool import ToolInput


class FakeArxivClient:
    pass


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
        fake_arxiv = SimpleNamespace(Client=FakeArxivClient)
        with patch.dict("sys.modules", {"arxiv": fake_arxiv}):
            with patch.object(ArxivTool, "find_papers_by_str",
                              autospec=True,
                              return_value="search results") as mock_search:
                result = self.tool.execute(tool_input)
        self.assertTrue(result!= "")
        mock_search.assert_called_once_with(self.tool, "machine learning")

    def test_get_paper_detail(self) -> None:
        tool_input = ToolInput({
            'input': '1605.08386v1',
            'mode': SearchMode.DETAIL.value
        })
        fake_arxiv = SimpleNamespace(Client=FakeArxivClient)
        with patch.dict("sys.modules", {"arxiv": fake_arxiv}):
            with patch.object(ArxivTool, "retrieve_full_paper_text",
                              autospec=True,
                              return_value="paper detail") as mock_detail:
                result = self.tool.execute(tool_input)
        self.assertTrue(result!= "")
        mock_detail.assert_called_once_with(self.tool, "1605.08386v1")

    def test_invalid_mode(self) -> None:
        tool_input = ToolInput({
            'input': 'test',
            'mode': 'invalid_mode'
        })
        with self.assertRaises(ValueError):
            self.tool.execute(tool_input)


if __name__ == '__main__':
    unittest.main()
