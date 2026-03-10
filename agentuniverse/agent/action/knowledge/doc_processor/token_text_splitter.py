# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/5 15:37
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: token_text_splitter.py
from typing import List, Optional, Any

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class TokenTextSplitter(DocProcessor):
    """Splits text into chunks based on token count rather than characters.

    Uses ``tiktoken`` for tokenisation.  You can specify either an
    ``encoding_name`` (e.g. ``"cl100k_base"``) or a ``model_name``
    (e.g. ``"gpt-4"``); when both are given ``model_name`` takes
    precedence.

    Attributes:
        chunk_size: Maximum number of tokens per chunk.
        chunk_overlap: Number of tokens to overlap between consecutive chunks.
        encoding_name: The tiktoken encoding name (default ``"cl100k_base"``).
        model_name: Optional model name; if given, the encoding is derived
            from it automatically.
    """
    chunk_size: int = 200
    chunk_overlap: int = 20
    encoding_name: str = 'cl100k_base'
    model_name: Optional[str] = None
    _encoding: Optional[Any] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def encoding(self):
        if self._encoding is None:
            try:
                import tiktoken
            except ImportError:
                raise ImportError(
                    "tiktoken is required for TokenTextSplitter. "
                    "Install it with: pip install tiktoken"
                )
            if self.model_name:
                self._encoding = tiktoken.encoding_for_model(self.model_name)
            else:
                self._encoding = tiktoken.get_encoding(self.encoding_name)
        return self._encoding

    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks based on token count.

        Args:
            text: The text to split.

        Returns:
            List of text chunks, each containing at most ``chunk_size`` tokens.
        """
        tokens = self.encoding.encode(text)

        if len(tokens) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            if chunk_text.strip():
                chunks.append(chunk_text)
            if end >= len(tokens):
                break
            # Move forward by (chunk_size - chunk_overlap) tokens
            start += max(1, self.chunk_size - self.chunk_overlap)

        return chunks

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Split documents based on token count using the specified tokenizer.

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
        if hasattr(doc_processor_configer, "encoding_name"):
            self.encoding_name = doc_processor_configer.encoding_name
        if hasattr(doc_processor_configer, "model_name"):
            self.model_name = doc_processor_configer.model_name
        return self
