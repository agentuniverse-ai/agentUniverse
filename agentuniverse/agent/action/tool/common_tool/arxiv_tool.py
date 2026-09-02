# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/16 17:00
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: arxiv_tool.py
from typing import Optional, Any, List
import os
from dataclasses import dataclass
from enum import Enum
from pydantic import Field
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.annotation.retry import retry


class SearchMode(Enum):
    """Search modes supported by ArxivTool.

    SEARCH: keyword search over arXiv; DETAIL: fetch the full text of a paper by id.
    """
    SEARCH = "search"   
    DETAIL = "detail"  


@dataclass
class PaperSummary:
    """Data class summarizing a single arXiv paper.

    Attributes:
    paper_id: arXiv identifier; title: paper title; authors: author name list;
    publish_date: publication date string; summary: paper abstract;
    pdf_url: URL of the paper PDF.
    """
    paper_id: str
    title: str
    authors: List[str]
    publish_date: str
    summary: str
    pdf_url: str


class ArxivTool(Tool):
    
    """Tool for searching arXiv papers and reading their full text.

    Runs in two modes: SEARCH returns formatted paper summaries for a keyword
    query, while DETAIL downloads a paper PDF and extracts its text.

    Requires the optional arxiv and pypdf packages.
    """
    sch_engine: Optional[Any] = None
    MAX_QUERY_LENGTH: int = Field(default=300, description="查询字符串最大长度")

    def execute(self, input: str | ToolInput, mode: str = None):
        """Dispatch the request according to the requested search mode.

        Args:
        input: keyword string or paper id, or a ToolInput holding input and mode;
        mode: one of SearchMode values (from ToolInput when input is a ToolInput).

        Returns:
        str: formatted paper summaries (SEARCH) or full paper text (DETAIL).
        """
        if isinstance(input, ToolInput):
            params = input.to_dict()
            mode = params.get("mode", mode)
            input = params.get("input")

        if mode not in [m.value for m in SearchMode]:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {[m.value for m in SearchMode]}")

        try:
            import arxiv
        except ImportError:
            raise ImportError("arxiv is required. Install with: pip install arxiv")

        if self.sch_engine is None:
            self.sch_engine = arxiv.Client()

        query = input
        return (self.find_papers_by_str(query) if mode == SearchMode.SEARCH.value
                else self.retrieve_full_paper_text(query))
        
    def _process_query(self, query: str) -> str:
        """Truncate a query to the maximum query length without splitting words.

        Args:
        query: the query string to process.

        Returns:
        str: the query when short enough, otherwise a prefix of whole words.
        """
        if len(query) <= self.MAX_QUERY_LENGTH:
            return query
        
        words: List[str] = query.split()
        processed_words: List[str] = []
        current_length: int = 0
        for word in words:
            word_length = len(word) + 1 
            if current_length + word_length <= self.MAX_QUERY_LENGTH:
                processed_words.append(word)
                current_length += word_length
            else:
                break
        return ' '.join(processed_words)

    @retry(3, 1.0)
    def find_papers_by_str(self, query) -> str:
        """Search arXiv by relevance and return formatted results for the query.

        Args:
        query: keyword string to search for.

        Returns:
        str: formatted paper results, or 'No papers found.' when none match.
        """
        processed_query = self._process_query(query)
        result_num:int = 10   
        try:
            import arxiv
        except ImportError:
            raise ImportError("arxiv is required. Install with: pip install arxiv")
    
        search = arxiv.Search(
            query="abs:" + processed_query,
            max_results=result_num,
            sort_by=arxiv.SortCriterion.Relevance)

        papers: List[PaperSummary] = []
        for result in self.sch_engine.results(search):
            paper = PaperSummary(
                paper_id=result.pdf_url.split("/")[-1],
                title=result.title,
                authors=[str(author) for author in result.authors],
                publish_date=str(result.published).split()[0],
                summary=result.summary.replace('\n', ' '),
                pdf_url=result.pdf_url
            )
            papers.append(paper)
        return self._format_paper_results(papers)

    @retry(3, 1.0)
    def retrieve_full_paper_text(self, paper_id: str) -> str:
        """Download a paper PDF and extract its full text page by page.

        Args:
        paper_id: arXiv identifier of the paper to fetch.

        Returns:
        str: extracted text of all pages joined by blank lines.
        """
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
            raise ImportError(
                "pypdf is required to read PDF files: `pip install pypdf`"
            )
        reader = pypdf.PdfReader('downloaded-paper.pdf')
        text_content = [page.extract_text() for page in reader.pages]
        if os.path.exists("downloaded-paper.pdf"):
            os.remove("downloaded-paper.pdf")
        return "\n\n".join(text_content)

    def _format_paper_results(self, papers: List[PaperSummary]) -> str:
        """Render paper summaries into a numbered, human-readable block.

        Args:
        papers: list of PaperSummary objects to format.

        Returns:
        str: formatted text, or 'No papers found.' for an empty list.
        """
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
                "-" * 80
            ]
            formatted_results.append("\n".join(paper_info))
        return "\n\n".join(formatted_results)
