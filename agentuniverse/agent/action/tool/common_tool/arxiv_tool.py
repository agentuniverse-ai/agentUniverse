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
    SEARCH = "search"   
    DETAIL = "detail"  


@dataclass
class PaperSummary:
    paper_id: str
    title: str
    authors: List[str]
    publish_date: str
    summary: str
    pdf_url: str


class ArxivTool(Tool):
    """ArXiv paper search and extraction tool.
    
    This tool provides functionality to search for academic papers on ArXiv and extract full text content.
    Supports two modes: search (find papers by query) and detail (extract full paper text by ID).
    """
    
    sch_engine: Optional[Any] = None
    MAX_QUERY_LENGTH: int = Field(default=300, description="Maximum query string length")

    def execute(self, input: str, mode: str):
        """Execute ArXiv search or extraction.
        
        Args:
            input (str): Search query or paper ID depending on mode
            mode (str): Operation mode - 'search' or 'detail'
            
        Returns:
            str: Search results or extracted paper text
        """
        try:
            import arxiv
        except ImportError:
            raise ImportError("arxiv is required. Install with: pip install arxiv")

        if self.sch_engine is None:
            self.sch_engine = arxiv.Client()

        if mode not in [m.value for m in SearchMode]:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {[m.value for m in SearchMode]}")

        query = input
        return (self.find_papers_by_str(query) if mode == SearchMode.SEARCH.value
                else self.retrieve_full_paper_text(query))
        
    def _process_query(self, query: str) -> str:
        """Process and truncate query to fit within MAX_QUERY_LENGTH."""
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
        """Search for papers on ArXiv by query string."""
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
        """Retrieve and extract full text content from a paper by its ID."""
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
        """Format paper search results into a readable string."""
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