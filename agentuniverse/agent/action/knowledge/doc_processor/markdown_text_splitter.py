# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: markdown_text_splitter.py

"""
Markdown text splitter — a knowledge pre-processing DocProcessor.

Splits Markdown documents into chunks along structural boundaries (code
fences, list blocks, blockquotes, table blocks, and paragraph breaks),
while respecting ``max_chunk_size``. Unlike ``MarkdownHeaderTextSplitter``
(#625) which splits by header hierarchy, this splitter focuses on keeping
structurally cohesive blocks together and only splitting when a chunk
exceeds the size budget.

Pure Python, zero third-party dependency. Addresses #258.
"""

import logging
import re
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# Block-level patterns that should not be split mid-block.
_CODE_FENCE_START = re.compile(r"^(`{3,}|~{3,})", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\|.*\|$")
_HR = re.compile(r"^(-{3,}|\*{3,}|_{3,})\s*$")
_BLOCKQUOTE = re.compile(r"^>\s")
_LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+\.)\s")
_HEADING = re.compile(r"^#{1,6}\s")


class MarkdownTextSplitter(DocProcessor):
    """Split Markdown by structural blocks with size-bounded chunking.

    Attributes:
        max_chunk_size: Maximum characters per chunk (default 1500).
        min_chunk_size: Minimum characters; smaller chunks are merged into
            the next one (default 200).
        chunk_overlap: Number of characters of overlap between adjacent
            chunks when a hard split is needed (default 100).
    """

    max_chunk_size: int = 1500
    min_chunk_size: int = 200
    chunk_overlap: int = 100

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        if not origin_docs:
            return []
        result: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            for chunk_text in self._split(text):
                meta = dict(doc.metadata or {})
                meta["chunk_method"] = "markdown_text"
                result.append(Document(text=chunk_text, metadata=meta))
        return result

    def _split(self, text: str) -> List[str]:
        blocks = self._identify_blocks(text)
        chunks = self._assemble_chunks(blocks)
        return chunks

    @staticmethod
    def _identify_blocks(text: str) -> List[str]:
        """Split text into structural blocks (code, table, list, paragraph)."""
        lines = text.split("\n")
        blocks: List[str] = []
        current: List[str] = []
        in_code_fence = False
        fence_marker = None

        def _flush():
            if current:
                blocks.append("\n".join(current).strip())
                current.clear()

        for line in lines:
            stripped = line.strip()

            # Code fence handling.
            fence_match = _CODE_FENCE_START.match(stripped)
            if fence_match:
                if not in_code_fence:
                    _flush()
                    in_code_fence = True
                    fence_marker = fence_match.group(1)[0]
                    current.append(line)
                elif in_code_fence and stripped.startswith(fence_marker * 3):
                    current.append(line)
                    in_code_fence = False
                    fence_marker = None
                    _flush()
                else:
                    current.append(line)
                continue

            if in_code_fence:
                current.append(line)
                continue

            # Structural boundaries that flush the current block.
            is_heading = bool(_HEADING.match(stripped))
            is_hr = bool(_HR.match(stripped))
            is_table = bool(_TABLE_ROW.match(stripped))
            is_blockquote = bool(_BLOCKQUOTE.match(stripped))
            is_list = bool(_LIST_ITEM.match(stripped))
            is_blank = stripped == ""

            # Transition between block types — flush.
            prev_stripped = current[-1].strip() if current else ""
            prev_is_table = bool(_TABLE_ROW.match(prev_stripped))
            prev_is_list = bool(_LIST_ITEM.match(prev_stripped))
            prev_is_blockquote = bool(_BLOCKQUOTE.match(prev_stripped))

            if (is_heading or is_hr) and current:
                _flush()
            elif is_table and current and not prev_is_table:
                _flush()
            elif is_list and current and not prev_is_list and not is_blank:
                _flush()
            elif is_blockquote and current and not prev_is_blockquote:
                _flush()
            elif is_blank and current and prev_stripped:
                _flush()

            current.append(line)

        _flush()
        return [b for b in blocks if b]

    def _assemble_chunks(self, blocks: List[str]) -> List[str]:
        """Group blocks into chunks respecting max/min chunk size."""
        if not blocks:
            return []

        chunks: List[str] = []
        current_parts: List[str] = []
        current_size = 0

        for block in blocks:
            block_size = len(block)

            if block_size > self.max_chunk_size:
                # Flush current chunk first.
                if current_parts:
                    chunks.append("\n\n".join(current_parts))
                    current_parts = []
                    current_size = 0
                # Hard-split the oversized block.
                chunks.extend(self._hard_split_block(block))
                continue

            if current_size + block_size + 2 > self.max_chunk_size:
                # Flush current, start new chunk.
                if current_parts and current_size >= self.min_chunk_size:
                    chunks.append("\n\n".join(current_parts))
                    current_parts = []
                    current_size = 0
                elif current_parts:
                    # Merge because current is below min_chunk_size.
                    pass

            current_parts.append(block)
            current_size += block_size + 2  # +2 for "\n\n"

        if current_parts:
            chunks.append("\n\n".join(current_parts))

        return [c.strip() for c in chunks if c.strip()]

    def _hard_split_block(self, block: str) -> List[str]:
        """Split a block that exceeds max_chunk_size at line boundaries."""
        lines = block.split("\n")
        parts: List[str] = []
        current: List[str] = []
        current_size = 0

        for line in lines:
            if current_size + len(line) + 1 > self.max_chunk_size and current:
                parts.append("\n".join(current))
                # Overlap: carry last few lines.
                overlap_lines = self._overlap_lines(current)
                current = overlap_lines + [line]
                current_size = sum(len(l) + 1 for l in current)
            else:
                current.append(line)
                current_size += len(line) + 1

        if current:
            parts.append("\n".join(current))

        return [p.strip() for p in parts if p.strip()]

    def _overlap_lines(self, lines: List[str]) -> List[str]:
        """Return the trailing lines fitting within chunk_overlap."""
        overlap: List[str] = []
        size = 0
        for line in reversed(lines):
            size += len(line) + 1
            if size > self.chunk_overlap:
                break
            overlap.insert(0, line)
        return overlap

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "MarkdownTextSplitter":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "max_chunk_size"):
            self.max_chunk_size = doc_processor_configer.max_chunk_size
        if hasattr(doc_processor_configer, "min_chunk_size"):
            self.min_chunk_size = doc_processor_configer.min_chunk_size
        if hasattr(doc_processor_configer, "chunk_overlap"):
            self.chunk_overlap = doc_processor_configer.chunk_overlap
        return self
