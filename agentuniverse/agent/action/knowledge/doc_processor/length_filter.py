# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/13
# @FileName: length_filter.py

"""
Length-based document filter.

Drops input :class:`Document` objects whose text length falls outside a
configured ``[min_length, max_length]`` range. This is a *pre-processing*
hygiene step for issue #258: a splitter (character, token, or the
:class:`MarkdownHeaderTextSplitter`) frequently emits near-empty fragments —
a header line whose body was on the next line, a stray blank section — and
those fragments embed to noise and pollute retrieval. Chaining a length filter
right after the splitter removes them before they reach the store.

The existing ``threshold_filter`` filters by *relevance score* after recall;
this filter operates by *content length* before insert, so the two are
complementary and never overlap.

Pure-Python and dependency-free. Length is measured in characters by default;
set ``length_unit: 'token'`` to count whitespace-separated tokens instead.
"""

from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class LengthFilter(DocProcessor):
    """Filter documents by text length, keeping only those within range.

    Attributes:
        min_length (Optional[int]): Minimum inclusive length; shorter documents
            are dropped. Defaults to 1 so empty / whitespace-only documents are
            removed out of the box. Set to ``None`` to disable the lower bound.
        max_length (Optional[int]): Maximum inclusive length; longer documents
            are dropped. Defaults to ``None`` (no upper bound).
        length_unit (str): ``'char'`` (default) counts characters, ``'token'``
            counts whitespace-separated tokens (an approximate, dependency-free
            token count).
        trim (bool): When True (default), leading/trailing whitespace is
            stripped before measuring, so a whitespace-only document is treated
            as length 0.
    """

    min_length: Optional[int] = 1
    max_length: Optional[int] = None
    length_unit: str = "char"
    trim: bool = True

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Return only the documents whose length is within range.

        Documents are passed through unchanged (this is a filter, not a
        transformer), so their ids and metadata are preserved.

        Args:
            origin_docs (List[Document]): Documents to filter.
            query (Query, optional): Unused; kept for interface compatibility.

        Returns:
            List[Document]: The subset of ``origin_docs`` whose measured text
            length satisfies ``min_length <= length <= max_length``.
        """
        kept: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            if self.trim:
                text = text.strip()
            length = self._length(text)
            if self.min_length is not None and length < self.min_length:
                continue
            if self.max_length is not None and length > self.max_length:
                continue
            kept.append(doc)
        return kept

    def _length(self, text: str) -> int:
        """Measure ``text`` according to ``length_unit``."""
        if self.length_unit == "token":
            # Whitespace tokenization: deterministic and dependency-free. Good
            # enough for a coarse length filter; not a model tokenizer.
            return len(text.split())
        return len(text)

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> 'LengthFilter':
        """Initialize the filter from its component config."""
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "min_length"):
            self.min_length = doc_processor_configer.min_length
        if hasattr(doc_processor_configer, "max_length"):
            self.max_length = doc_processor_configer.max_length
        if hasattr(doc_processor_configer, "length_unit"):
            self.length_unit = doc_processor_configer.length_unit
        if hasattr(doc_processor_configer, "trim"):
            self.trim = doc_processor_configer.trim
        return self
