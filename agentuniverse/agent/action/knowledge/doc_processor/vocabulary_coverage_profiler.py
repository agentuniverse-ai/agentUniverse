# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: vocabulary_coverage_profiler.py

import math
import re
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# --------------------------------------------------------------------------- #
# Built-in stopword inventories — the same compact lists as StopwordRemover.
# --------------------------------------------------------------------------- #

# 120 high-frequency English function words, used here only as a yardstick:
# the share of a document's tokens found in this list is its stopword
# coverage. Content-bearing words are never listed.
_EN_STOPWORDS = frozenset((
    # articles
    'a', 'an', 'the',
    # conjunctions
    'and', 'or', 'but', 'nor', 'so', 'yet', 'if', 'then', 'than', 'that',
    'because', 'while', 'when', 'where', 'although', 'though', 'unless',
    'until', 'since', 'after', 'before',
    # pronouns
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
    'them', 'my', 'your', 'his', 'its', 'our', 'their', 'this', 'these',
    'those', 'who', 'whom', 'whose', 'which', 'what',
    # be / do / have and modal verbs
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'do', 'does',
    'did', 'have', 'has', 'had', 'will', 'would', 'shall', 'should', 'can',
    'could', 'may', 'might', 'must',
    # prepositions
    'of', 'to', 'in', 'on', 'at', 'by', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'above', 'below', 'from', 'up',
    'down', 'out', 'off', 'over', 'under', 'again', 'across', 'near',
    'past',
    # quantifiers / adverbs / negation
    'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'not', 'only', 'own', 'same', 'too',
    'very', 'just', 'as',
))

# 81 single CJK characters (particles, coverbs, pronouns, high-frequency
# adverbs, existential/measure words), matched one character at a time —
# no word segmenter needed.
_ZH_STOPWORDS = frozenset((
    # particles and sentence-final markers
    '的', '了', '着', '过', '地', '得', '是', '之', '者', '也', '乎', '矣',
    '呢', '吧', '吗', '啊', '呀', '哦',
    # conjunctions
    '和', '与', '及', '或', '但', '而', '且', '并', '若', '则', '虽', '因',
    '故',
    # coverbs / prepositions
    '在', '从', '向', '往', '对', '为', '以', '于', '被', '把', '将', '给',
    '让', '比',
    # pronouns and determiners
    '我', '你', '他', '她', '它', '们', '这', '那', '其', '此', '某', '各',
    '每',
    # adverbs, negation, degree
    '不', '没', '就', '还', '才', '只', '再', '又', '更', '最', '很', '太',
    '挺', '极', '稍', '略', '曾', '已', '正', '未',
    # existential and measure
    '有', '个', '些',
))

_ALL_STOPWORDS = _EN_STOPWORDS | _ZH_STOPWORDS

# Unified CJK ideograph ranges: Extension A, the main block, and the
# compatibility ideographs.
_CJK_CLASS = '\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufa6d'

# Tokens counted by the profiler, tried left to right at every position:
#   1. a Latin word — letters plus at most one internal apostrophe, so
#      contractions such as don't stay whole (case is folded afterwards);
#   2. one CJK ideograph, each character acting as its own token unit —
#      the same char-level strategy StopwordRemover uses, no segmenter
#      required.
# Digits, punctuation and other scripts (Cyrillic, Greek, ...) are not
# tokens: vocabulary diversity is measured over word material only.
_TOKEN_RE = re.compile(
    "[A-Za-z]+(?:'[A-Za-z]+)?"
    '|[' + _CJK_CLASS + ']'
)

# Number of most-frequent tokens reported in 'top_5_tokens'.
_TOP_TOKENS = 5


class VocabularyCoverageProfiler(DocProcessor):
    """Profile each document's lexical diversity into metadata.

    Splitters and embedding models downstream of ingestion behave very
    differently on a vocabulary-rich essay and on a page that repeats one
    phrase two hundred times — yet both look like "a document" until
    someone measures them. This processor, addressing the pre-processing
    direction of issue #258, computes a compact set of lexical-diversity
    statistics for every document and stamps them into
    ``metadata[vocabulary_key]`` so pipelines can pick chunk sizes,
    choose embedding strategies, or route low-information documents aside
    before any model runs. It is deliberately distinct from its
    neighbours: ``TextQualityScorer`` fuses several signals into
    composite quality gates, and ``ReadingLevelScorer`` applies
    readability formulas (syllables, sentence length) — neither reports
    the vocabulary-shape numbers below, and this component computes
    nothing else.

    Tokenization follows the ``StopwordRemover`` family, pure stdlib and
    deterministic: Latin word runs (letters plus at most one internal
    apostrophe, lowercased, so *Apple* and *apple* are one type) plus
    individual CJK ideographs as char-sized units. Digits, punctuation
    and other scripts contribute nothing, so a phone-number column or a
    wall of punctuation never inflates diversity. Over the
    case-folded token stream the component computes:

    * ``token_count`` — total tokens;
    * ``type_count`` — distinct tokens (the "types" of corpus linguistics);
    * ``type_token_ratio`` — ``type_count / token_count``: the classic
      TTR, which falls as a document gets longer even for rich prose;
    * ``root_ttr`` — ``type_count / sqrt(token_count)``: Guiraud's index,
      computed alongside because its square-root denominator makes it
      far less length-dependent — the two are reported together so
      consumers can see both the familiar and the length-fairer figure;
    * ``hapax_count`` / ``hapax_ratio`` — tokens occurring exactly once,
      in absolute terms and as ``hapax_count / token_count``; a large
      hapax share with a small type count signals noise (ids, typos)
      rather than rich vocabulary;
    * ``avg_word_length`` / ``longest_word`` — mean token length in
      characters (first-encountered token wins length ties) and the
      longest token itself;
    * ``stopword_coverage`` — percentage of tokens found in the built-in
      compact EN+ZH function-word inventories (the same lists as
      ``StopwordRemover``): boilerplate and filler pages score high,
      dense technical prose low;
    * ``top_5_tokens`` — the five most frequent tokens with counts,
      ties broken alphabetically (ascending) so output is reproducible.

    A document with no tokens at all (empty, whitespace, digits or
    punctuation only) receives ``token_count`` 0 and ``type_count`` 0
    with every ratio and average set to ``None`` — never a division
    error — and an empty ``top_5_tokens`` list.

    Optionally the processor flags monotony: when a document's
    ``root_ttr`` is strictly below ``low_diversity_threshold`` (default
    5.0, roughly the floor for healthy prose) the string ``low_diversity``
    is stamped into ``metadata[flag_key]``. Tokenless documents are never
    flagged — their diversity is unmeasured, not low. Documents are
    neither dropped, reordered nor rewritten: the output list maps 1:1
    onto the input, text and id stay untouched, and metadata mappings
    are copied before mutation. The whole pass is offline and
    deterministic — same input, same numbers, every run.

    Attributes:
        low_diversity_threshold: Root TTR strictly below this value flags
            a document as ``low_diversity``; must be a positive number.
        vocabulary_key: Metadata key the statistics dict is written to;
            an empty value disables stamping the statistics.
        flag_key: Metadata key the ``low_diversity`` marker is written
            to on flagged documents; an empty value disables flagging.
    """

    low_diversity_threshold: float = 5.0
    vocabulary_key: str = 'vocabulary'
    flag_key: str = 'vocabulary_flag'

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp lexical-diversity statistics into every document.

        Args:
            origin_docs: Documents to profile, in batch order.
            query: Query object (unused; profiling depends only on the
                documents' own text).

        Returns:
            List[Document]: The same document objects, in the same order,
            with vocabulary statistics (and, for low-diversity documents,
            the flag) stamped into their metadata.
        """
        if not origin_docs:
            return []

        for doc in origin_docs:
            stats = self._profile(doc.text or '')
            if self.vocabulary_key:
                self._stamp(doc, self.vocabulary_key, stats)
            if self.flag_key and stats['root_ttr'] is not None and \
                    stats['root_ttr'] < self.low_diversity_threshold:
                self._stamp(doc, self.flag_key, 'low_diversity')

        return list(origin_docs)

    # ------------------------------------------------------------------ #
    # Statistics
    # ------------------------------------------------------------------ #

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Split text into lowercased Latin word and CJK char tokens.

        Args:
            text: Raw document text.

        Returns:
            List[str]: Token list in order of occurrence; empty for text
            without word material.
        """
        return [token.lower() for token in _TOKEN_RE.findall(text)]

    @staticmethod
    def _profile(text: str) -> dict:
        """Compute the full statistics dict for one text.

        Args:
            text: Raw document text (None treated as empty).

        Returns:
            dict: Keys token_count, type_count, type_token_ratio,
            root_ttr, hapax_count, hapax_ratio, avg_word_length,
            longest_word, stopword_coverage and top_5_tokens. Ratios and
            averages are None for a tokenless document; top_5_tokens is
            a list of [token, count] pairs, most frequent first, ties
            broken alphabetically ascending.
        """
        tokens = VocabularyCoverageProfiler._tokenize(text)
        token_count = len(tokens)
        if token_count == 0:
            return {
                'token_count': 0,
                'type_count': 0,
                'type_token_ratio': None,
                'root_ttr': None,
                'hapax_count': 0,
                'hapax_ratio': None,
                'avg_word_length': None,
                'longest_word': None,
                'stopword_coverage': None,
                'top_5_tokens': [],
            }

        counts: dict = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1

        type_count = len(counts)
        hapax_count = sum(1 for c in counts.values() if c == 1)
        stopword_hits = sum(c for token, c in counts.items()
                            if token in _ALL_STOPWORDS)
        ranked = sorted(counts.items(), key=lambda item: (-item[1],
                                                           item[0]))

        return {
            'token_count': token_count,
            'type_count': type_count,
            'type_token_ratio': type_count / token_count,
            'root_ttr': type_count / math.sqrt(token_count),
            'hapax_count': hapax_count,
            'hapax_ratio': hapax_count / token_count,
            'avg_word_length': sum(len(t) for t in tokens) / token_count,
            'longest_word': max(tokens, key=len),
            'stopword_coverage': stopword_hits / token_count * 100.0,
            'top_5_tokens': [[token, count]
                             for token, count in ranked[:_TOP_TOKENS]],
        }

    @staticmethod
    def _stamp(doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place edits.

        Args:
            doc: Document to stamp.
            key: Metadata key.
            value: Metadata value.
        """
        meta = dict(doc.metadata or {})
        meta[key] = value
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'VocabularyCoverageProfiler':
        """Initialize and validate the profiler from component configuration.

        Validation happens eagerly at load time: a silently misread
        threshold that flagged every document (or none) would be far
        harder to notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            VocabularyCoverageProfiler: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "low_diversity_threshold") and \
                doc_processor_configer.low_diversity_threshold is not None:
            threshold = doc_processor_configer.low_diversity_threshold
            if isinstance(threshold, bool) or \
                    not isinstance(threshold, (int, float)):
                raise ValueError(
                    "low_diversity_threshold must be a number")
            self.low_diversity_threshold = float(threshold)
            if self.low_diversity_threshold <= 0:
                raise ValueError(
                    "low_diversity_threshold must be > 0, got "
                    f"{self.low_diversity_threshold}")

        if hasattr(doc_processor_configer, "vocabulary_key") and \
                doc_processor_configer.vocabulary_key is not None:
            key = doc_processor_configer.vocabulary_key
            if not isinstance(key, str):
                raise ValueError("vocabulary_key must be a string")
            self.vocabulary_key = key

        if hasattr(doc_processor_configer, "flag_key") and \
                doc_processor_configer.flag_key is not None:
            key = doc_processor_configer.flag_key
            if not isinstance(key, str):
                raise ValueError("flag_key must be a string")
            self.flag_key = key

        return self
