# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/02/16 21:38
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: test_arxiv_tool.py

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

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

    def test_retrieve_full_paper_text_uses_temporary_file(self) -> None:
        downloaded_paths = []
        pdf_url = "https://export.arxiv.org/pdf/1605.08386v1"

        def download_pdf(url, filename):
            self.assertEqual(pdf_url, url)
            pdf_path = Path(filename)
            downloaded_paths.append(pdf_path)
            pdf_path.write_bytes(b"%PDF-1.4")

        paper = SimpleNamespace(pdf_url=pdf_url)
        self.tool.sch_engine = SimpleNamespace(results=lambda _: iter([paper]))
        fake_arxiv = SimpleNamespace(Search=lambda **_: object())
        fake_reader = Mock(
            return_value=SimpleNamespace(
                pages=[
                    SimpleNamespace(extract_text=lambda: "first page"),
                    SimpleNamespace(extract_text=lambda: None),
                ]
            )
        )
        fake_pypdf = SimpleNamespace(PdfReader=fake_reader)

        with (
            patch.dict("sys.modules", {"arxiv": fake_arxiv, "pypdf": fake_pypdf}),
            patch(
                "agentuniverse.agent.action.tool.common_tool.arxiv_tool.urlretrieve",
                side_effect=download_pdf,
            ),
        ):
            result = self.tool.retrieve_full_paper_text("1605.08386v1")
            second_result = self.tool.retrieve_full_paper_text("1605.08386v1")

        self.assertEqual("first page\n\n", result)
        self.assertEqual(result, second_result)
        self.assertEqual(2, len(downloaded_paths))
        self.assertNotEqual(downloaded_paths[0].parent, downloaded_paths[1].parent)
        self.assertTrue(all(path.parent != Path.cwd() for path in downloaded_paths))
        self.assertTrue(all(path.name == "paper.pdf" for path in downloaded_paths))
        self.assertTrue(all(not path.parent.exists() for path in downloaded_paths))
        self.assertEqual(2, fake_reader.call_count)
        fake_reader.assert_has_calls([call(str(path)) for path in downloaded_paths])

    def test_retrieve_full_paper_text_cleans_up_after_parse_failure(self) -> None:
        downloaded_paths = []
        paper = SimpleNamespace(pdf_url="https://export.arxiv.org/pdf/1605.08386v1")
        self.tool.sch_engine = SimpleNamespace(results=lambda _: iter([paper]))
        fake_arxiv = SimpleNamespace(Search=lambda **_: object())
        fake_pypdf = SimpleNamespace(PdfReader=Mock(side_effect=ValueError("invalid PDF")))

        def download_pdf(_, filename):
            pdf_path = Path(filename)
            downloaded_paths.append(pdf_path)
            pdf_path.write_bytes(b"not a PDF")

        with (
            patch.dict("sys.modules", {"arxiv": fake_arxiv, "pypdf": fake_pypdf}),
            patch(
                "agentuniverse.agent.action.tool.common_tool.arxiv_tool.urlretrieve",
                side_effect=download_pdf,
            ),
            self.assertRaisesRegex(ValueError, "invalid PDF"),
        ):
            self.tool.retrieve_full_paper_text.__wrapped__(self.tool, "1605.08386v1")

        self.assertEqual(1, len(downloaded_paths))
        self.assertFalse(downloaded_paths[0].parent.exists())

    def test_retrieve_full_paper_text_rejects_unsafe_pdf_urls(self) -> None:
        fake_arxiv = SimpleNamespace(Search=lambda **_: object())

        for pdf_url in (None, "file:///tmp/paper.pdf"):
            with self.subTest(pdf_url=pdf_url):
                self.tool.sch_engine = SimpleNamespace(
                    results=lambda _: iter([SimpleNamespace(pdf_url=pdf_url)])
                )
                with (
                    patch.dict("sys.modules", {"arxiv": fake_arxiv}),
                    self.assertRaisesRegex(ValueError, "No valid PDF URL found.*1605.08386v1"),
                ):
                    self.tool.retrieve_full_paper_text.__wrapped__(self.tool, "1605.08386v1")

    def test_invalid_mode(self) -> None:
        tool_input = ToolInput({
            'input': 'test',
            'mode': 'invalid_mode'
        })
        with self.assertRaises(ValueError):
            self.tool.execute(tool_input)


if __name__ == '__main__':
    unittest.main()
