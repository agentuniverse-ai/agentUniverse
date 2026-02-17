# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/5 14:37
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: character_text_splitter.py
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class CharacterTextSplitter(DocProcessor):
    """Character-based text splitter for document processing.

    Splits documents into smaller chunks based on a single character separator,
    with configurable chunk size and overlap parameters.

    Attributes:
        chunk_size: The maximum size of each text chunk (in characters).
        chunk_overlap: The number of characters to overlap between chunks.
        separator: The character sequence used to split text.
    """
    chunk_size: int = 200
    chunk_overlap: int = 20
    separator: str = "\n\n"

    def _split_text(self, text: str) -> List[str]:
        """Split a single text string into chunks.

        Args:
            text: The text to split.

        Returns:
            List of text chunks.
        """
        # Split by separator
        if self.separator:
            splits = text.split(self.separator)
        else:
            splits = list(text)

        # Merge small splits into chunks respecting chunk_size
        chunks = []
        current_chunk: List[str] = []
        current_len = 0

        for split in splits:
            split_len = len(split)
            sep_len = len(self.separator) if self.separator else 0

            # If adding this split would exceed chunk_size, finalize current chunk
            if current_chunk and (current_len + split_len + sep_len) > self.chunk_size:
                chunk_text = self.separator.join(current_chunk) if self.separator else ''.join(current_chunk)
                chunks.append(chunk_text)

                # Keep overlap: drop splits from the front until we're within overlap
                overlap_len = 0
                overlap_start = len(current_chunk)
                for i in range(len(current_chunk) - 1, -1, -1):
                    piece_len = len(current_chunk[i]) + (sep_len if i > 0 else 0)
                    if overlap_len + piece_len > self.chunk_overlap:
                        break
                    overlap_len += piece_len
                    overlap_start = i

                current_chunk = current_chunk[overlap_start:]
                current_len = sum(len(s) for s in current_chunk)
                if current_chunk:
                    current_len += sep_len * (len(current_chunk) - 1)

            current_chunk.append(split)
            current_len += split_len + (sep_len if len(current_chunk) > 1 else 0)

        # Don't forget the last chunk
        if current_chunk:
            chunk_text = self.separator.join(current_chunk) if self.separator else ''.join(current_chunk)
            chunks.append(chunk_text)

        # Filter out empty chunks
        return [c for c in chunks if c.strip()]

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Process documents by splitting them into smaller chunks.

        Args:
            origin_docs: List of original documents to be processed.
            query: Optional query object that may influence the processing.

        Returns:
            List[Document]: List of processed document chunks.
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
        """Initialize the splitter using configuration from a ComponentConfiger.

        Args:
            doc_processor_configer: Configuration object containing splitter parameters.

        Returns:
            DocProcessor: The initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "chunk_size"):
            self.chunk_size = doc_processor_configer.chunk_size
        if hasattr(doc_processor_configer, "chunk_overlap"):
            self.chunk_overlap = doc_processor_configer.chunk_overlap
        if hasattr(doc_processor_configer, "separator"):
            self.separator = doc_processor_configer.separator
        return self
