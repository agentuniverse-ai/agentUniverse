# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/16 17:00
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: arxiv_tool.py
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.annotation.retry import retry


class SearchMode(Enum):
    SEARCH = "search"
    DETAIL = "detail"


@dataclass
class PaperSummary:
    paper_id: str
    title: str
    authors: list[str]
    publish_date: str
    summary: str
    pdf_url: str


class ArxivTool(Tool):
    SORT_CRITERIA: ClassVar[dict[str, str]] = {
        "relevance": "Relevance",
        "submitted_date": "SubmittedDate",
        "last_updated_date": "LastUpdatedDate",
    }
    SORT_ORDERS: ClassVar[dict[str, str]] = {
        "descending": "Descending",
        "ascending": "Ascending",
    }

    sch_engine: Any | None = None
    MAX_QUERY_LENGTH: int = Field(default=300, description="查询字符串最大长度")

    def execute(
        self,
        input: str | ToolInput,
        mode: str | None = None,
        max_results: int = 10,
        sort_by: str = "relevance",
        sort_order: str = "descending",
    ) -> str:
        """Search arXiv papers or retrieve the full text of one paper.

        Args:
          input: Search query in search mode or a paper ID in detail mode.
          mode: Operation mode. Must be ``search`` or ``detail``.
          max_results: Search result limit from 1 to 100. Defaults to 10.
          sort_by: ``relevance``, ``submitted_date``, or ``last_updated_date``. Defaults to ``relevance``.
          sort_order: ``descending`` or ``ascending``. Defaults to ``descending``.

        Returns:
          Formatted search results or the extracted full text of a paper.

        Raises:
          ValueError: If the mode or a search option is invalid.
          ImportError: If the ``arxiv`` or ``pypdf`` package is not installed.
        """
        if isinstance(input, ToolInput):
            params = input.to_dict()
            mode = params.get("mode", mode)
            max_results = params.get("max_results", max_results)
            sort_by = params.get("sort_by", sort_by)
            sort_order = params.get("sort_order", sort_order)
            input = params.get("input")

        if mode not in [m.value for m in SearchMode]:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {[m.value for m in SearchMode]}")

        if mode == SearchMode.SEARCH.value and (
            isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= 100
        ):
            raise ValueError("max_results must be an integer between 1 and 100")

        if mode == SearchMode.SEARCH.value:
            if not isinstance(sort_by, str) or sort_by not in self.SORT_CRITERIA:
                options = ", ".join(self.SORT_CRITERIA)
                raise ValueError(f"sort_by must be one of: {options}")
            if not isinstance(sort_order, str) or sort_order not in self.SORT_ORDERS:
                options = ", ".join(self.SORT_ORDERS)
                raise ValueError(f"sort_order must be one of: {options}")

        try:
            import arxiv
        except ImportError:
            raise ImportError("arxiv is required. Install with: pip install arxiv")

        if self.sch_engine is None:
            self.sch_engine = arxiv.Client()

        query = input
        if mode == SearchMode.SEARCH.value:
            return self.find_papers_by_str(
                query,
                max_results=max_results,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        return self.retrieve_full_paper_text(query)

    def _process_query(self, query: str) -> str:
        if len(query) <= self.MAX_QUERY_LENGTH:
            return query

        words: list[str] = query.split()
        processed_words: list[str] = []
        current_length: int = 0
        for word in words:
            word_length = len(word) + 1
            if current_length + word_length <= self.MAX_QUERY_LENGTH:
                processed_words.append(word)
                current_length += word_length
            else:
                break
        return " ".join(processed_words)

    @retry(3, 1.0)
    def find_papers_by_str(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "relevance",
        sort_order: str = "descending",
    ) -> str:
        """Search arXiv papers and format matching results.

        Args:
          query: Search query passed to the arXiv API.
          max_results: Maximum number of papers to return, from 1 to 100.
          sort_by: ``relevance``, ``submitted_date``, or ``last_updated_date``.
          sort_order: ``descending`` or ``ascending``.

        Returns:
          A formatted list of matching papers, or a no-results message.
        """
        try:
            import arxiv
        except ImportError:
            raise ImportError("arxiv is required. Install with: pip install arxiv")

        search = arxiv.Search(
            query="abs:" + self._process_query(query),
            max_results=max_results,
            sort_by=getattr(arxiv.SortCriterion, self.SORT_CRITERIA[sort_by]),
            sort_order=getattr(arxiv.SortOrder, self.SORT_ORDERS[sort_order]),
        )

        papers: list[PaperSummary] = []
        for result in self.sch_engine.results(search):
            paper = PaperSummary(
                paper_id=result.pdf_url.split("/")[-1],
                title=result.title,
                authors=[str(author) for author in result.authors],
                publish_date=str(result.published).split()[0],
                summary=result.summary.replace("\n", " "),
                pdf_url=result.pdf_url,
            )
            papers.append(paper)
        return self._format_paper_results(papers)

    @retry(3, 1.0)
    def retrieve_full_paper_text(self, paper_id: str) -> str:
        try:
            import arxiv
        except ImportError:
            raise ImportError("arxiv is required. Install with: pip install arxiv")
        search = arxiv.Search(id_list=[paper_id])
        paper = next(self.sch_engine.results(search))
        paper.download_pdf(filename="downloaded-paper.pdf")

        try:
            import pypdf
        except ImportError:
            raise ImportError("pypdf is required to read PDF files: `pip install pypdf`")
        reader = pypdf.PdfReader("downloaded-paper.pdf")
        text_content = [page.extract_text() for page in reader.pages]
        if os.path.exists("downloaded-paper.pdf"):
            os.remove("downloaded-paper.pdf")
        return "\n\n".join(text_content)

    def _format_paper_results(self, papers: list[PaperSummary]) -> str:
        if not papers:
            return "No papers found."

        formatted_results = []
        for i, paper in enumerate(papers, 1):
            paper_info = [
                f"[{i}] {paper.title}",
                f"Authors: {', '.join(paper.authors)}",
                f"Published: {paper.publish_date}",
                f"Paper ID: {paper.paper_id}",
                f"PDF URL: {paper.pdf_url}",
                f"Summary: {paper.summary}",
                "-" * 80,
            ]
            formatted_results.append("\n".join(paper_info))
        return "\n\n".join(formatted_results)
