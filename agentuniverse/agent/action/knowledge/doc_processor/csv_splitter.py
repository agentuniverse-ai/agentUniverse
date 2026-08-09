# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: csv_splitter.py

"""
CSV/TSV splitter — a knowledge pre-processing DocProcessor.

Splits CSV or TSV text into one chunk per row group, where each chunk
contains a configurable number of rows plus the header. The header is
preserved on every chunk so that each is self-contained and retrievable
in context.

Pure Python with the built-in ``csv`` module — no third-party dependency.
Sibling of the merged ``MarkdownHeaderTextSplitter`` (#625) and the new
``HtmlHeaderTextSplitter`` (#737), ``JsonSplitter`` (#738), etc.
Addresses #258.
"""

import csv
import io
import logging
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class CsvSplitter(DocProcessor):
    """Split CSV/TSV text into row-grouped chunks with header preserved.

    Attributes:
        rows_per_chunk: Number of data rows per chunk (default 50). The
            header row is prepended to every chunk.
        delimiter: Column delimiter. ``","`` for CSV (default), ``"\\t"``
            for TSV, or any other single character.
        max_cell_chars: Maximum characters per cell in the output text;
            longer cells are truncated (default 1000).
    """

    rows_per_chunk: int = 50
    delimiter: str = ","
    max_cell_chars: int = 1000

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        if not origin_docs:
            return []
        result: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            for chunk_text in self._split_csv(text):
                meta = dict(doc.metadata or {})
                meta["chunk_method"] = "csv"
                result.append(Document(text=chunk_text, metadata=meta))
        return result

    def _split_csv(self, text: str) -> List[str]:
        """Parse CSV text and return chunk strings."""
        reader = csv.reader(io.StringIO(text), delimiter=self.delimiter)
        rows = list(reader)
        if not rows:
            return []

        header = rows[0]
        data_rows = rows[1:]
        if not data_rows:
            return [self._format_csv([header])]

        chunks: List[str] = []
        for i in range(0, len(data_rows), self.rows_per_chunk):
            batch = data_rows[i:i + self.rows_per_chunk]
            chunk_rows = [header] + batch
            chunks.append(self._format_csv(chunk_rows))
        return chunks

    def _format_csv(self, rows: List[List[str]]) -> str:
        """Format rows back to CSV text, truncating oversized cells."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=self.delimiter)
        for row in rows:
            truncated_row = []
            for cell in row:
                if len(cell) > self.max_cell_chars:
                    truncated_row.append(
                        cell[:max(0, self.max_cell_chars - 1)] + "…")
                else:
                    truncated_row.append(cell)
            writer.writerow(truncated_row)
        return output.getvalue().strip()

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "CsvSplitter":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "rows_per_chunk"):
            self.rows_per_chunk = doc_processor_configer.rows_per_chunk
        if hasattr(doc_processor_configer, "delimiter"):
            self.delimiter = doc_processor_configer.delimiter
        if hasattr(doc_processor_configer, "max_cell_chars"):
            self.max_cell_chars = doc_processor_configer.max_cell_chars
        return self
