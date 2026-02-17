# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/31 16:19
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: recursive_character_text_splitter.py
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class RecursiveCharacterTextSplitter(DocProcessor):
    """Splits text recursively using a hierarchy of character separators.

    Tries each separator in order.  When a separator produces pieces that
    are still larger than ``chunk_size``, the next separator in the list is
    tried recursively.  Small pieces are merged back together (with overlap)
    to fill chunks up to ``chunk_size``.

    Attributes:
        chunk_size: Maximum size of each text chunk (in characters).
        chunk_overlap: Number of characters to overlap between chunks.
        separators: Ordered list of separator strings to try.
    """
    chunk_size: int = 200
    chunk_overlap: int = 20
    separators: List[str] = ["\n\n", "\n", " ", ""]

    def _split_text(self, text: str, separators: List[str] = None) -> List[str]:
        """Recursively split text using the separator hierarchy.

        Args:
            text: The text to split.
            separators: Remaining separators to try (defaults to self.separators).

        Returns:
            List of text chunks, each within chunk_size.
        """
        if separators is None:
            separators = list(self.separators)

        # Base case: text fits in a single chunk
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        # Find the best separator (first one that actually splits the text)
        separator = ""
        remaining_separators = []
        for i, sep in enumerate(separators):
            if sep == "":
                separator = sep
                remaining_separators = []
                break
            if sep in text:
                separator = sep
                remaining_separators = separators[i + 1:]
                break
        else:
            # No separator found, just return the text as-is
            return [text] if text.strip() else []

        # Split using the chosen separator
        if separator:
            splits = text.split(separator)
        else:
            # Empty separator = split into individual characters
            splits = list(text)

        # Merge splits into chunks, recursing on oversized pieces
        good_splits: List[str] = []
        current_chunk: List[str] = []
        current_len = 0
        sep_len = len(separator)

        def _flush_current():
            """Merge current_chunk into a single string and add to good_splits."""
            nonlocal current_chunk, current_len
            if not current_chunk:
                return
            merged = separator.join(current_chunk) if separator else ''.join(current_chunk)
            if merged.strip():
                good_splits.append(merged)

            # Keep overlap
            overlap_len = 0
            overlap_start = len(current_chunk)
            for idx in range(len(current_chunk) - 1, -1, -1):
                piece_len = len(current_chunk[idx]) + (sep_len if idx > 0 else 0)
                if overlap_len + piece_len > self.chunk_overlap:
                    break
                overlap_len += piece_len
                overlap_start = idx

            current_chunk = current_chunk[overlap_start:]
            current_len = sum(len(s) for s in current_chunk)
            if current_chunk:
                current_len += sep_len * (len(current_chunk) - 1)

        for split in splits:
            split_len = len(split)
            potential_len = current_len + split_len + (sep_len if current_chunk else 0)

            if split_len > self.chunk_size:
                # This split is too large, flush what we have, then recurse
                _flush_current()
                if remaining_separators:
                    sub_chunks = self._split_text(split, remaining_separators)
                    good_splits.extend(sub_chunks)
                else:
                    # Last resort: hard split by characters
                    for start in range(0, len(split), self.chunk_size - self.chunk_overlap):
                        end = min(start + self.chunk_size, len(split))
                        piece = split[start:end]
                        if piece.strip():
                            good_splits.append(piece)
                        if end >= len(split):
                            break
            elif potential_len > self.chunk_size:
                _flush_current()
                current_chunk.append(split)
                current_len = split_len
            else:
                current_chunk.append(split)
                current_len = potential_len

        _flush_current()

        return good_splits

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Split documents recursively using character separators.

        Args:
            origin_docs: List of documents to be split.
            query: Optional query object (not used in this processor).

        Returns:
            List of split document chunks.
        """
        result = []
        for doc in origin_docs:
            chunks = self._split_text(doc.text or "")
            for chunk in chunks:
                result.append(Document(
                    text=chunk,
                    metadata=doc.metadata.copy() if doc.metadata else None
                ))
        return result

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        """Initialize splitter parameters from configuration.

        Args:
            doc_processor_configer: Configuration object containing splitter parameters.

        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "chunk_size"):
            self.chunk_size = doc_processor_configer.chunk_size
        if hasattr(doc_processor_configer, "chunk_overlap"):
            self.chunk_overlap = doc_processor_configer.chunk_overlap
        if hasattr(doc_processor_configer, "separators"):
            self.separators = doc_processor_configer.separators
        return self
