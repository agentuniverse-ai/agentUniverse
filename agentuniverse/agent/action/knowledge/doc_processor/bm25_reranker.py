"""Offline lexical reranking over a recalled candidate list."""

import math
import re
import unicodedata
from collections import Counter
from typing import List, Optional

from pydantic import StrictFloat, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


def _tokens(text: str) -> List[str]:
    """Case-fold NFC words, retaining internal hyphens/dots in identifiers."""
    return re.findall(r"\w+(?:[-.]\w+)*", unicodedata.normalize("NFC", text).casefold())


class BM25Reranker(DocProcessor):
    """Rank candidate occurrences by positive-IDF BM25 without a model or API.

    Statistics describe this candidate list, not the store's full corpus.
    Repeated query terms contribute once; equal scores preserve input order.
    Documents are shallow copies with new metadata dictionaries. Other nested
    values remain shared and are never modified by this processor.

    Attributes:
        k1: Finite positive term-frequency saturation parameter.
        b: Finite length-normalization weight in [0, 1].
        top_n: Nonnegative result limit, or None to return every occurrence.
        score_field: Metadata destination; existing values at this key are
            replaced on the returned copies only.
    """

    k1: StrictFloat = 1.2
    b: StrictFloat = 0.75
    top_n: Optional[StrictInt] = None
    score_field: StrictStr = "bm25_score"

    def __init__(self, **data):
        super().__init__(**data)
        self._validate_options()

    def _validate_options(self) -> None:
        for name in ("k1", "b"):
            value = getattr(self, name)
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"{name} must be a finite number")
        if self.k1 <= 0:
            raise ValueError("k1 must be positive")
        if not 0 <= self.b <= 1:
            raise ValueError("b must be between 0 and 1")
        if self.top_n is not None and (type(self.top_n) is not int or self.top_n < 0):
            raise ValueError("top_n must be a nonnegative integer or None")
        if not isinstance(self.score_field, str) or not self.score_field.strip():
            raise ValueError("score_field must be a nonblank string")

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Score and sort candidates without modifying input documents.

        Empty input and a zero result limit return [] without needing a query.
        None/empty document text has zero length and receives a zero score.

        Raises:
            ValueError: Options are invalid, or a nonempty operation has no
                query containing at least one token.
        """
        self._validate_options()
        if not origin_docs or self.top_n == 0:
            return []
        if query is None or not isinstance(query.query_str, str):
            raise ValueError("query.query_str must contain at least one token")
        terms = list(dict.fromkeys(_tokens(query.query_str)))
        if not terms:
            raise ValueError("query.query_str must contain at least one token")

        frequencies = [Counter(_tokens(doc.text or "")) for doc in origin_docs]
        lengths = [sum(counts.values()) for counts in frequencies]
        count = len(origin_docs)
        average_length = sum(lengths) / count
        document_frequency = Counter()
        for counts in frequencies:
            document_frequency.update(counts.keys())
        idf = {term: math.log1p((count - document_frequency[term] + 0.5) /
                              (document_frequency[term] + 0.5)) for term in terms}
        scored = []
        for doc, counts, length in zip(origin_docs, frequencies, lengths):
            score = 0.0
            if length:
                normalization = 1 - self.b + self.b * length / average_length
                for term in terms:
                    frequency = counts[term]
                    if frequency:
                        # Algebraically BM25's tf*(k1+1)/(tf+k1*norm), but
                        # avoids overflow of k1*norm for large finite k1.
                        denominator = (frequency / (self.k1 + 1) +
                                       (self.k1 / (self.k1 + 1)) * normalization)
                        score += idf[term] * frequency / denominator
            metadata = dict(doc.metadata or {})
            metadata[self.score_field] = score
            scored.append(doc.model_copy(update={"metadata": metadata}))
        scored.sort(key=lambda doc: doc.metadata[self.score_field], reverse=True)
        return scored if self.top_n is None else scored[:self.top_n]

    def _initialize_by_component_configer(self, config: ComponentConfiger) -> 'BM25Reranker':
        """Validate YAML options before changing the active configuration."""
        names = ("k1", "b", "top_n", "score_field")
        values = {name: getattr(config, name, getattr(self, name)) for name in names}
        validated = BM25Reranker(**values)
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        return self
