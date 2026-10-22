# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: text_quality_scorer.py

import math
import re
import unicodedata
from typing import Any, Dict, List, Optional

from pydantic import Field

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Default contribution of each sub-score to the composite quality score.
# The values sum to 1.0 so the composite is a plain weighted mean before
# pathology gates are applied.
_DEFAULT_WEIGHTS: Dict[str, float] = {
    'alpha': 0.10,
    'structure': 0.20,
    'punctuation': 0.20,
    'diversity': 0.30,
    'digit': 0.05,
    'whitespace': 0.05,
    'length': 0.10,
}

# Leading / trailing non-word characters, stripped from Latin tokens before
# they become diversity units so "spam." and "spam" count as one word.
_TOKEN_EDGE = re.compile(r'^[\W_]+|[\W_]+$')


class TextQualityScorer(DocProcessor):
    """Score the content quality of each document from lexical statistics.

    RAG pipelines ingest whatever the source hands over: well-edited prose,
    but also keyboard mash pasted into a form field, symbol-heavy spam,
    digit dumps from log scrapes and boilerplate loops repeated by a scraper
    bug. Embedding such junk wastes budget and pollutes recall, yet the
    framework's existing filters decide on metadata that already has to be
    correct. This processor — the content-quality direction of issue #258 —
    looks at the text itself and stamps every document with a deterministic
    ``quality_score`` in [0, 100], so low-quality documents can be routed,
    audited or filtered downstream. It judges the text content; it is
    therefore complementary to components that judge *where* a document came
    from (source-level credibility) and to ``ThresholdFilter``, which applies
    user-supplied rules to metadata this component produces.

    Per-document metrics, all pure-stdlib and computed in one pass:

    - ``length_chars``: total characters of the text;
    - ``non_whitespace_chars``: total characters excluding whitespace —
      the denominator the symbol/digit-soup gate is measured over;
    - ``word_count``: word units — whitespace-separated tokens containing
      Latin letters plus every CJK character (CJK text is not spaced, so
      characters are the natural unit and Chinese documents are not
      misjudged by word statistics designed for Latin scripts);
    - ``mean_word_length``: mean alphanumeric length of the Latin words
      (``None`` for documents without any);
    - ``unique_word_ratio``: distinct word units over all word units, with
      Latin words lowercased and stripped of attached punctuation;
    - ``alpha_ratio`` / ``digit_ratio`` / ``punctuation_ratio``: shares of
      letters (CJK included), digits and Unicode punctuation over non-
      whitespace characters;
    - ``whitespace_irregularity``: share of whitespace characters that
      belong to irregular runs — runs of 2+ spaces, 3+ newlines, any tab,
      carriage return or exotic space, or whitespace touching either end
      of the text;
    - ``cjk_ratio``: share of CJK characters (Han, kana, Hangul) over
      non-whitespace characters. At or above ``cjk_threshold`` the document
      is analysed on the CJK-aware path: CJK characters count as word units
      and mean Latin word length stops contributing.

    The composite score is a weighted mean of seven sub-scores in [0, 1]
    (``weights`` names them): ``alpha`` rewards alphabetic share, ``digit``
    tolerates moderate digit share, ``punctuation`` rewards the band real
    prose sits in, ``structure`` requires enough word units and sane Latin
    word lengths, ``diversity`` penalises both pathological repetition and,
    on longer texts, token-soup uniqueness near 1.0, ``whitespace`` penalises
    irregular whitespace, and ``length`` rewards reaching a useful size. Two
    unambiguous pathologies then gate the result downwards (a document
    exhibiting both sinks fast): long documents whose word units repeat
    almost verbatim (unique ratio < 0.10 over 30+ units — spam loops,
    scraper boilerplate) lose half their score, and long documents that are
    mostly symbols or digits (alpha ratio < 0.20 over 100+ non-whitespace
    characters) lose 60%. Empty, whitespace-only, symbol-only and
    digit-only documents score exactly
    0. Everything is fixed arithmetic: no randomness, no network, no model
    calls — the same text always yields the same score and metrics dict.

    By default every document is kept and only stamped with
    ``metadata[score_key]`` (float score, rounded to 4 decimals) and
    ``metadata[metrics_key]`` (the metrics dict). When ``min_score`` is
    set, documents scoring below it are additionally marked
    ``metadata[rejected_key] = True`` on their original object — so callers
    holding the input list can see why a document vanished — and are dropped
    from the output; the boundary is inclusive (a document scoring exactly
    ``min_score`` is kept). Metadata mappings are copied before mutation and
    text, id and pre-existing metadata entries are never modified.

    Attributes:
        min_score: Optional drop threshold in [0, 100]; ``None`` (default)
            keeps every document and only stamps scores.
        weights: Mapping of sub-score name (one of ``alpha``, ``structure``,
            ``punctuation``, ``diversity``, ``digit``, ``whitespace``,
            ``length``) to a non-negative weight; the composite is the
            weighted mean, so only relative values matter and at least one
            weight must be positive. A provided mapping replaces the
            defaults entirely.
        cjk_threshold: CJK-character share over non-whitespace characters
            at which the CJK-aware path activates, in (0, 1].
        score_key: Metadata key the numeric quality score is written to;
            an empty value disables stamping.
        metrics_key: Metadata key the metrics dict is written to; an empty
            value disables stamping.
        rejected_key: Metadata key set to True on dropped document objects
            when ``min_score`` filtering is active; an empty value disables
            stamping.
    """

    min_score: Optional[float] = None
    weights: Dict[str, float] = Field(
        default_factory=lambda: dict(_DEFAULT_WEIGHTS))
    cjk_threshold: float = 0.30
    score_key: str = 'quality_score'
    metrics_key: str = 'quality_metrics'
    rejected_key: str = 'quality_rejected'

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Score every document and optionally drop low-quality ones.

        Args:
            origin_docs: Documents to score, in batch order.
            query: Query object (unused; quality depends only on the
                documents' own text).

        Returns:
            List[Document]: All input documents when ``min_score`` is None,
            otherwise those scoring at least ``min_score``, in batch order;
            each kept document is stamped with its score and metrics, and
            each dropped document object additionally carries
            ``metadata[rejected_key] = True``.
        """
        kept: List[Document] = []
        for doc in origin_docs:
            metrics = self._analyze(doc.text or "")
            score = round(self._composite_score(metrics), 4)
            if self.score_key:
                self._stamp(doc, self.score_key, score)
            if self.metrics_key:
                self._stamp(doc, self.metrics_key, metrics)
            if self.min_score is not None and score < self.min_score:
                if self.rejected_key:
                    self._stamp(doc, self.rejected_key, True)
                continue
            kept.append(doc)
        return kept

    # ------------------------------------------------------------------ #
    # Metric extraction
    # ------------------------------------------------------------------ #

    def _analyze(self, text: str) -> Dict[str, Any]:
        """Compute the per-document quality metrics.

        Args:
            text: Document text (None treated as empty).

        Returns:
            Dict[str, Any]: The metrics described in the class docstring,
            with ratios rounded to 6 decimals for stable metadata.
        """
        letters = digits = punct = other = cjk = whitespace = 0
        cjk_units: List[str] = []
        for ch in text or "":
            if ch.isspace():
                whitespace += 1
                continue
            if _is_cjk(ch):
                cjk += 1
                cjk_units.append(ch)
            if ch.isalpha():
                letters += 1
            elif ch.isdigit():
                digits += 1
            elif unicodedata.category(ch).startswith('P'):
                punct += 1
            else:
                other += 1
        non_ws = letters + digits + punct + other
        safe_non_ws = max(1, non_ws)

        # Latin words: whitespace tokens with at least one Latin letter and
        # no CJK character (tokens carrying CJK are represented by their
        # characters in cjk_units instead, keeping the two scripts separate).
        latin_words = [token for token in (text or "").split()
                       if _has_latin_letter(token)
                       and not any(_is_cjk(ch) for ch in token)]

        word_count = len(latin_words) + len(cjk_units)
        if latin_words:
            alnum = sum(sum(1 for ch in word if ch.isalnum())
                        for word in latin_words)
            mean_word_length = round(alnum / len(latin_words), 6)
        else:
            mean_word_length = None

        units = [_TOKEN_EDGE.sub('', word).lower() for word in latin_words]
        units.extend(cjk_units)
        unique_ratio = round(len(set(units)) / len(units), 6) if units else 0.0

        cjk_ratio = round(cjk / safe_non_ws, 6)
        script = 'cjk' if cjk_ratio >= self.cjk_threshold else 'latin'

        irregular = self._irregular_whitespace_chars(text or "")
        ws_irregularity = round(irregular / max(1, whitespace), 6)

        return {
            'length_chars': len(text or ""),
            'non_whitespace_chars': non_ws,
            'word_count': word_count,
            'mean_word_length': mean_word_length,
            'unique_word_ratio': unique_ratio,
            'alpha_ratio': round(letters / safe_non_ws, 6),
            'digit_ratio': round(digits / safe_non_ws, 6),
            'punctuation_ratio': round(punct / safe_non_ws, 6),
            'whitespace_irregularity': ws_irregularity,
            'cjk_ratio': cjk_ratio,
            'script': script,
        }

    @staticmethod
    def _irregular_whitespace_chars(text: str) -> int:
        """Count whitespace characters belonging to irregular runs.

        A whitespace run (maximal streak of whitespace characters) is
        irregular when it contains anything but plain single spaces and
        single or paired newlines — i.e. tabs, carriage returns or exotic
        spaces anywhere, three or more consecutive newlines, two or more
        consecutive spaces, a run of three or more characters mixing spaces
        and newlines — or when it touches the start or the end of the text.
        Paragraph breaks (one blank line) stay regular.

        Args:
            text: Raw document text.

        Returns:
            int: Number of whitespace characters inside irregular runs.
        """
        count = 0
        index, length = 0, len(text)
        while index < length:
            if not text[index].isspace():
                index += 1
                continue
            start = index
            while index < length and text[index].isspace():
                index += 1
            run = text[start:index]
            touches_end = start == 0 or index == length
            bad_char = any(ch not in ' \n' for ch in run)
            many_spaces = len(run) >= 2 and all(ch == ' ' for ch in run)
            many_newlines = len(run) >= 3 and all(ch == '\n' for ch in run)
            mixed = (' ' in run and '\n' in run and len(run) >= 3)
            if touches_end or bad_char or many_spaces or many_newlines \
                    or mixed:
                count += len(run)
        return count

    # ------------------------------------------------------------------ #
    # Composite scoring
    # ------------------------------------------------------------------ #

    def _composite_score(self, metrics: Dict[str, Any]) -> float:
        """Combine the metrics into a quality score in [0, 100].

        Args:
            metrics: Dict produced by ``_analyze``.

        Returns:
            float: Weighted-mean score after pathology gates; exactly 0.0
                for documents without measurable content (empty,
                whitespace-only, symbol-only or digit-only texts).
        """
        # word_count == 0 iff the text carries no alphabetic character at
        # all (every CJK char is a unit and every CJK-free token with a
        # letter is a Latin word): empty, whitespace-only, symbol-only and
        # digit-only texts score exactly 0.
        if metrics['word_count'] == 0:
            return 0.0

        words = metrics['word_count']
        unique = metrics['unique_word_ratio']
        mean_length = metrics['mean_word_length']
        # A CJK-path document counts characters, not Latin words, so the
        # Latin word-length heuristic stays neutral there (the same holds
        # for documents without any Latin words at all).
        if mean_length is None or metrics.get('script') == 'cjk':
            length_score = 1.0
        else:
            length_score = _band(mean_length, 2.0, 9.0, 1.2, 15.0)

        sub_scores = {
            'alpha': _ramp(metrics['alpha_ratio'], 0.25, 0.75),
            'structure': min(_ramp(words, 5, 30), length_score),
            'punctuation': _band(metrics['punctuation_ratio'],
                                 0.01, 0.20, 0.0, 0.45),
            'diversity': (
                _ramp(words, 3, 15)
                * _ramp(unique, 0.05, 0.25)
                * (1.0 - _ramp(words, 20, 50) * _ramp(unique, 0.92, 1.0))
            ),
            'digit': 1.0 - _ramp(metrics['digit_ratio'], 0.15, 0.50),
            'whitespace': 1.0 - _ramp(
                metrics['whitespace_irregularity'], 0.10, 0.60),
            'length': _ramp(metrics['length_chars'], 40, 200),
        }

        total = sum(self.weights.get(name, 0.0) for name in sub_scores)
        weighted = sum(self.weights.get(name, 0.0) * value
                       for name, value in sub_scores.items())
        score = 100.0 * weighted / total if total > 0 else 0.0

        # Pathology gates: degenerate repetition and symbol/digit soup are
        # structural failures no weighted average of surface ratios should
        # be able to rescue.
        if words >= 30 and unique < 0.10:
            score *= 0.5
        non_ws_chars = metrics.get('non_whitespace_chars',
                                   metrics['length_chars'])
        if non_ws_chars >= 100 and metrics['alpha_ratio'] < 0.20:
            score *= 0.4
        return score

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
            -> 'TextQualityScorer':
        """Initialize and validate the scorer from component configuration.

        Validation happens eagerly at load time: a misconfigured scorer
        that silently stamped meaningless scores would be far harder to
        notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            TextQualityScorer: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "min_score") and \
                doc_processor_configer.min_score is not None:
            value = doc_processor_configer.min_score
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("min_score must be a number")
            self.min_score = float(value)
            if not 0 <= self.min_score <= 100:
                raise ValueError("min_score must be in [0, 100]")

        if hasattr(doc_processor_configer, "weights") and \
                doc_processor_configer.weights is not None:
            self.weights = self._validated_weights(
                doc_processor_configer.weights)

        if hasattr(doc_processor_configer, "cjk_threshold") and \
                doc_processor_configer.cjk_threshold is not None:
            value = doc_processor_configer.cjk_threshold
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("cjk_threshold must be a number")
            self.cjk_threshold = float(value)
            if not 0 < self.cjk_threshold <= 1:
                raise ValueError("cjk_threshold must be in (0, 1]")

        for attr in ("score_key", "metrics_key", "rejected_key"):
            if hasattr(doc_processor_configer, attr) and \
                    getattr(doc_processor_configer, attr) is not None:
                key = getattr(doc_processor_configer, attr)
                if not isinstance(key, str):
                    raise ValueError(f"{attr} must be a string")
                setattr(self, attr, key)

        return self

    @staticmethod
    def _validated_weights(weights: Any) -> Dict[str, float]:
        """Validate a user-supplied weights mapping.

        Args:
            weights: Candidate mapping of sub-score name to weight.

        Returns:
            Dict[str, float]: A copied mapping with float values.

        Raises:
            ValueError: On a non-mapping input, unknown sub-score names,
                non-numeric or negative or non-finite weights, or an
                all-zero mapping.
        """
        if not isinstance(weights, dict):
            raise ValueError("weights must be a mapping of name to number")
        validated: Dict[str, float] = {}
        for name, value in weights.items():
            if name not in _DEFAULT_WEIGHTS:
                raise ValueError(
                    f"unknown weight {name!r}; expected one of "
                    f"{sorted(_DEFAULT_WEIGHTS)}")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"weight for {name!r} must be a number")
            if not math.isfinite(value):
                raise ValueError(f"weight for {name!r} must be finite")
            if value < 0:
                raise ValueError(f"weight for {name!r} must be >= 0")
            validated[name] = float(value)
        if not validated or sum(validated.values()) <= 0:
            raise ValueError("weights must contain at least one positive "
                             "weight")
        return validated


def _is_cjk(ch: str) -> bool:
    """Report whether a character belongs to a CJK script block.

    Covers Han (Unified Ideographs, Extensions A and B+, compatibility
    ideographs), kana and Hangul syllables — the scripts written without
    inter-word spaces.

    Args:
        ch: A single character.

    Returns:
        bool: True when the character is CJK.
    """
    code_point = ord(ch)
    return (0x4E00 <= code_point <= 0x9FFF
            or 0x3400 <= code_point <= 0x4DBF
            or 0x20000 <= code_point <= 0x2FA1F
            or 0xF900 <= code_point <= 0xFAFF
            or 0x3040 <= code_point <= 0x30FF
            or 0xAC00 <= code_point <= 0xD7AF
            or 0x31F0 <= code_point <= 0x31FF)


def _has_latin_letter(token: str) -> bool:
    """Report whether a token carries at least one non-CJK letter.

    Args:
        token: A whitespace-delimited token.

    Returns:
        bool: True when the token contains a Latin (or other non-CJK)
        alphabetic character.
    """
    return any(ch.isalpha() and not _is_cjk(ch) for ch in token)


def _ramp(value: float, low: float, high: float) -> float:
    """Linearly map ``value`` from 0 at ``low`` to 1 at ``high``, clamped.

    Args:
        value: Input value.
        low: Value mapping to 0.
        high: Value mapping to 1.

    Returns:
        float: Position in [0, 1].
    """
    if high <= low:
        return 0.0
    return max(0.0, min(1.0, (value - low) / (high - low)))


def _band(value: float, low: float, high: float,
          fall_low: float, fall_high: float) -> float:
    """Score 1 inside [low, high], ramping to 0 outside the fall bounds.

    Args:
        value: Input value.
        low: Start of the full-score band.
        high: End of the full-score band.
        fall_low: Value below the band scoring 0.
        fall_high: Value above the band scoring 0.

    Returns:
        float: Score in [0, 1].
    """
    if value < low:
        return _ramp(value, fall_low, low)
    if value > high:
        return 1.0 - _ramp(value, high, fall_high)
    return 1.0
