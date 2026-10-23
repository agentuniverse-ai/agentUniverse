# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/16 21:38
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: test_arxiv_tool.py

import unittest
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, patch

from agentuniverse.agent.action.tool.common_tool.arxiv_tool import ArxivTool, SearchMode
from agentuniverse.agent.action.tool.tool import ToolInput


class FakeArxivClient:
    """Minimal arXiv client used by the focused unit tests."""

    def results(self, search: Any) -> Iterator[Any]:
        return iter([])


class ArxivToolTest(unittest.TestCase):
    """
    Test cases for ArxivTool class
    """

    def setUp(self) -> None:
        """Set up a fresh tool for each test."""
        self.tool = ArxivTool()

    def test_search_uses_default_options(self) -> None:
        search_constructor = Mock(return_value=object())
        fake_arxiv = SimpleNamespace(
            Client=FakeArxivClient,
            Search=search_constructor,
            SortCriterion=SimpleNamespace(
                Relevance="relevance",
                SubmittedDate="submittedDate",
                LastUpdatedDate="lastUpdatedDate",
            ),
            SortOrder=SimpleNamespace(Descending="descending", Ascending="ascending"),
        )
        with patch.dict("sys.modules", {"arxiv": fake_arxiv}):
            result = self.tool.execute(input="machine learning", mode=SearchMode.SEARCH.value)

        self.assertEqual(result, "No papers found.")
        search_constructor.assert_called_once_with(
            query="abs:machine learning",
            max_results=10,
            sort_by="relevance",
            sort_order="descending",
        )

    def test_langchain_json_passes_custom_search_options(self) -> None:
        self.tool.input_keys = ["input", "mode"]
        search_constructor = Mock(return_value=object())
        fake_arxiv = SimpleNamespace(
            Client=FakeArxivClient,
            Search=search_constructor,
            SortCriterion=SimpleNamespace(
                Relevance="relevance",
                SubmittedDate="submittedDate",
                LastUpdatedDate="lastUpdatedDate",
            ),
            SortOrder=SimpleNamespace(Descending="descending", Ascending="ascending"),
        )
        with patch.dict("sys.modules", {"arxiv": fake_arxiv}):
            with patch(
                "agentuniverse.base.annotation.trace._tool_wrapper_sync",
                new=lambda func, *args, **kwargs: func(*args, **kwargs),
            ):
                result = self.tool.langchain_run(
                    '{"input": "machine learning", "mode": "search", "max_results": 3, '
                    '"sort_by": "submitted_date", "sort_order": "ascending"}'
                )

        self.assertEqual(result, "No papers found.")
        search_constructor.assert_called_once_with(
            query="abs:machine learning",
            max_results=3,
            sort_by="submittedDate",
            sort_order="ascending",
        )

    def test_last_updated_sort(self) -> None:
        search_constructor = Mock(return_value=object())
        fake_arxiv = SimpleNamespace(
            Client=FakeArxivClient,
            Search=search_constructor,
            SortCriterion=SimpleNamespace(
                Relevance="relevance",
                SubmittedDate="submittedDate",
                LastUpdatedDate="lastUpdatedDate",
            ),
            SortOrder=SimpleNamespace(Descending="descending", Ascending="ascending"),
        )
        with patch.dict("sys.modules", {"arxiv": fake_arxiv}):
            result = self.tool.execute(
                input="machine learning",
                mode=SearchMode.SEARCH.value,
                sort_by="last_updated_date",
            )

        self.assertEqual(result, "No papers found.")
        search_constructor.assert_called_once_with(
            query="abs:machine learning",
            max_results=10,
            sort_by="lastUpdatedDate",
            sort_order="descending",
        )

    def test_query_is_passed_through_and_max_results_can_be_100(self) -> None:
        search_constructor = Mock(return_value=object())
        fake_arxiv = SimpleNamespace(
            Client=FakeArxivClient,
            Search=search_constructor,
            SortCriterion=SimpleNamespace(
                Relevance="relevance",
                SubmittedDate="submittedDate",
                LastUpdatedDate="lastUpdatedDate",
            ),
            SortOrder=SimpleNamespace(Descending="descending", Ascending="ascending"),
        )
        with patch.dict("sys.modules", {"arxiv": fake_arxiv}):
            result = self.tool.execute(
                input='"quantum criticality" machine',
                mode=SearchMode.SEARCH.value,
                max_results=100,
            )

        self.assertEqual(result, "No papers found.")
        search_constructor.assert_called_once_with(
            query='abs:"quantum criticality" machine',
            max_results=100,
            sort_by="relevance",
            sort_order="descending",
        )

    def test_invalid_max_results(self) -> None:
        for max_results in (0, 101, True, "3"):
            with self.subTest(max_results=max_results):
                with self.assertRaises(ValueError) as context:
                    self.tool.execute(
                        input="machine learning",
                        mode="search",
                        max_results=max_results,
                    )
                self.assertIn(repr(max_results), str(context.exception))

    def test_invalid_sort_options(self) -> None:
        invalid_options = (
            ("sort_by", "date"),
            ("sort_order", "newest"),
        )
        for option, value in invalid_options:
            with self.subTest(option=option, value=value):
                with self.assertRaises(ValueError) as context:
                    self.tool.execute(
                        input="machine learning",
                        mode=SearchMode.SEARCH.value,
                        **{option: value},
                    )
                self.assertIn(repr(value), str(context.exception))

    def test_empty_or_non_string_input(self) -> None:
        for input_value in ("", "  ", None):
            with self.subTest(input_value=input_value):
                with self.assertRaisesRegex(ValueError, "input must be a non-empty string"):
                    self.tool.execute(input=input_value, mode=SearchMode.SEARCH.value)

    def test_get_paper_detail(self) -> None:
        """Test that detail mode delegates to the paper text retriever."""
        tool_input = ToolInput({"input": "1605.08386v1", "mode": SearchMode.DETAIL.value})
        fake_arxiv = SimpleNamespace(Client=FakeArxivClient)
        with patch.dict("sys.modules", {"arxiv": fake_arxiv}):
            with patch.object(
                ArxivTool, "retrieve_full_paper_text", autospec=True, return_value="paper detail"
            ) as mock_detail:
                result = self.tool.execute(tool_input)
        self.assertTrue(result != "")
        mock_detail.assert_called_once_with(self.tool, "1605.08386v1")

    def test_invalid_mode(self) -> None:
        """Test that an invalid mode is rejected with its value shown."""
        tool_input = ToolInput({"input": "test", "mode": "invalid_mode"})
        with self.assertRaises(ValueError) as context:
            self.tool.execute(tool_input)
        self.assertIn(repr("invalid_mode"), str(context.exception))


if __name__ == "__main__":
    unittest.main()
