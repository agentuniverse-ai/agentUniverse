# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: keyword_extractor.py

"""
Keyword extractor — a knowledge post-processing DocProcessor.

Extracts keywords from recalled documents using a dependency-free YAKE-like
algorithm: scores candidate terms by frequency, position, capitalisation,
and term length, then stamps the top-N keywords into each document's
metadata. This is distinct from the existing ``JiebaKeywordExtractor``
(which requires the ``jieba`` package and targets Chinese text only).

Pure Python, zero third-party dependency. Addresses #248.
"""

import logging
import math
import re
from collections import Counter
from typing import List, Optional, Set, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# Stopwords for English + common Chinese function words.
_STOPWORDS: Set[str] = {
    # English
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "up", "down", "out", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how",
    "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "just", "also", "but", "and", "or", "if",
    "while", "about", "against", "between", "this", "that", "these",
    "those", "it", "its", "i", "me", "my", "we", "our", "you", "your",
    "he", "him", "his", "she", "her", "they", "them", "their", "what",
    "which", "who", "whom", "whose",
}

# Candidate term pattern: sequences of word characters (incl. CJK), hyphens.
_TERM_PATTERN = re.compile(r"[\w][-–\w]*", re.UNICODE)

_MIN_TERM_LEN = 2
_MAX_TERM_LEN = 40


class KeywordExtractor(DocProcessor):
    """Extract top-N keywords from each document using a YAKE-like scoring.

    Attributes:
        top_k: Number of keywords to extract per document (default 10).
        ngram_size: Maximum n-gram length for candidate terms (default 3).
        keywords_key: Metadata key under which the keywords list is stored.
        min_term_freq: Minimum frequency for a term to be considered
            (default 1).
    """

    top_k: int = 10
    ngram_size: int = 3
    keywords_key: str = "keywords"
    min_term_freq: int = 1

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        if not origin_docs:
            return []
        result: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            keywords = self._extract(text)
            meta = dict(doc.metadata or {})
            meta[self.keywords_key] = keywords
            result.append(Document(
                text=doc.text, metadata=meta, embedding=doc.embedding))
        return result

    def _extract(self, text: str) -> List[str]:
        """Extract top-k keywords from text using YAKE-like scoring."""
        if not text or not text.strip():
            return []

        sentences = self._split_sentences(text)
        if not sentences:
            return []

        # Build candidate terms (1 to ngram_size).
        term_scores: dict[str, float] = {}
        term_freq = Counter()
        term_positions: dict[str, list] = {}
        term_caps: dict[str, int] = {}
        total_sentences = len(sentences)

        for sent_idx, sentence in enumerate(sentences):
            tokens = self._tokenize(sentence)
            for n in range(1, min(self.ngram_size, len(tokens)) + 1):
                for i in range(len(tokens) - n + 1):
                    term_tokens = tokens[i:i + n]
                    term = " ".join(t.lower() for t in term_tokens)

                    # Skip if any token is a stopword (for n>1, skip if first
                    # or last token is a stopword).
                    if n == 1 and term in _STOPWORDS:
                        continue
                    if n > 1 and (term_tokens[0].lower() in _STOPWORDS
                                   or term_tokens[-1].lower() in _STOPWORDS):
                        continue

                    if len(term) < _MIN_TERM_LEN or len(term) > _MAX_TERM_LEN:
                        continue

                    term_freq[term] += 1
                    term_positions.setdefault(term, []).append(sent_idx)
                    # Capitalisation bonus.
                    if any(t[0].isupper() for t in term_tokens if t):
                        term_caps[term] = term_caps.get(term, 0) + 1

        # Score terms.
        for term, freq in term_freq.items():
            if freq < self.min_term_freq:
                continue

            # Frequency score (normalised).
            max_freq = max(term_freq.values()) if term_freq else 1
            freq_score = freq / max_freq

            # Position score (earlier = better).
            positions = term_positions[term]
            pos_score = math.log(1 + (total_sentences - positions[0])
                                 / max(1, total_sentences))

            # Capitalisation bonus.
            caps_ratio = term_caps.get(term, 0) / freq
            caps_score = caps_ratio * 0.5

            # Combined YAKE-like score (higher = more important).
            score = freq_score + pos_score + caps_score
            term_scores[term] = score

        # Sort by score descending, return top_k.
        sorted_terms = sorted(term_scores.items(), key=lambda x: -x[1])
        return [term for term, _ in sorted_terms[:self.top_k]]

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        parts = re.split(r"(?<=[.!?。！？])\s+|\n+", text.strip())
        return [s.strip() for s in parts if len(s.strip()) >= 3]

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [m.group() for m in _TERM_PATTERN.finditer(text)
                if len(m.group()) >= 1]

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "KeywordExtractor":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "top_k"):
            self.top_k = doc_processor_configer.top_k
        if hasattr(doc_processor_configer, "ngram_size"):
            self.ngram_size = doc_processor_configer.ngram_size
        if hasattr(doc_processor_configer, "keywords_key"):
            self.keywords_key = doc_processor_configer.keywords_key
        if hasattr(doc_processor_configer, "min_term_freq"):
            self.min_term_freq = doc_processor_configer.min_term_freq
        return self
