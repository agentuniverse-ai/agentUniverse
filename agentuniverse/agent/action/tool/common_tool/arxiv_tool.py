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

    sch_engine: Optional[Any] = None
    MAX_QUERY_LENGTH: int = Field(default=300, description="查询字符串最大长度")
    max_pdf_size_bytes: int = Field(
        default=50 * 1024 * 1024,
        description="Maximum PDF size in bytes for retrieve_full_paper_text")

    def execute(self, input: str | ToolInput, mode: str = None):
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
        try:
            import arxiv
        except ImportError:
            raise ImportError("arxiv is required. Install with: pip install arxiv")
        search = arxiv.Search(id_list=[paper_id])
        paper = next(self.sch_engine.results(search))

        import tempfile
        # Use a unique temp file per call instead of a fixed CWD filename,
        # so concurrent calls do not overwrite each other and the temp file
        # is cleaned up even when pypdf raises on a corrupt/encrypted PDF.
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".pdf", delete=False
            ) as tmp:
                tmp_path = tmp.name
            paper.download_pdf(filename=tmp_path)

            # Reject unreasonably large PDFs before loading them.
            if os.path.getsize(tmp_path) > self.max_pdf_size_bytes:
                raise ValueError(
                    f"Downloaded PDF for {paper_id} is "
                    f"{os.path.getsize(tmp_path)} bytes, exceeding "
                    f"max_pdf_size_bytes ({self.max_pdf_size_bytes}).")

            try:
                import pypdf
            except ImportError:
                raise ImportError(
                    "pypdf is required to read PDF files: `pip install pypdf`"
                )
            reader = pypdf.PdfReader(tmp_path)
            text_content = []
            for page in reader.pages:
                try:
                    text_content.append(page.extract_text() or "")
                except Exception:
                    text_content.append("")
            return "\n\n".join(text_content)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def _format_paper_results(self, papers: List[PaperSummary]) -> str:
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
