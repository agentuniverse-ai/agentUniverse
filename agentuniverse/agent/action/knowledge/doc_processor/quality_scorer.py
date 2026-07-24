# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: quality_scorer.py

"""
Quality scorer — a knowledge post-processing DocProcessor.

Scores each recalled document on overall text quality and optionally drops
low-quality documents. The score is a weighted average of several
independent, dependency-free heuristics, each normalised to ``[0.0, 1.0]``:

- **length**          — rewards documents of a useful size. Too-short text is
                         nearly content-free; too-long text tends to be noise.
                         Peaks around ``ideal_length``.
- **sentence_completeness** — fraction of sentence-ending punctuation that is
                         a real sentence terminator (``. ! ?``) versus other
                         punctuation, plus a penalty for fragments with no
                         terminator at all. Detects well-formed prose vs.
                         keyword soup.
- **special_char_ratio** — penalises a high proportion of non-alphanumeric,
                         non-whitespace symbols (``@ # % ^ * ~`` …), a strong
                         signal of boilerplate / log spam.
- **repetition**      — penalises repeated content. Measured via the share of
                         duplicated n-grams (default 8-char shingles) and the
                         share of the most frequent repeated word.
- **information_density** — ratio of distinct word tokens to total tokens,
                         a coarse lexical-diversity signal. Dense, varied
                         text scores higher than filler.

The final score is ``sum(weight_i * score_i) / sum(weight_i)``. Weights and
sub-scores are stamped into metadata under ``score_key`` (default
``quality_score``) so downstream stages (e.g. ``ThresholdFilter``) can use
them. Documents scoring below ``min_score`` are dropped when ``min_score`` is
set (``None`` disables dropping — the scorer then only annotates).

Addresses #248 (knowledge post-processing components). It complements
``ThresholdFilter`` (which filters on an externally-supplied score field):
this component *produces* a score from text alone, no external signals or
models required.
"""

import logging
import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# Default weights for each sub-score. Keys must match the dimension names.
DEFAULT_WEIGHTS: Dict[str, float] = {
    "length": 0.15,
    "sentence_completeness": 0.25,
    "special_char_ratio": 0.15,
    "repetition": 0.20,
    "information_density": 0.25,
}

# Token / sentence regexes (compiled once).
_WORD_RE = re.compile(r"[A-Za-z0-9']+")
_SENTENCE_END_RE = re.compile(r"[.!?]+")
_ALL_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_SPECIAL_CHAR_RE = re.compile(r"[^\w\s]", re.UNICODE)
# Punctuation that is NOT a sentence terminator (commas, semicolons, etc.).
_NON_TERMINATOR_PUNCT_RE = re.compile(r"[,;:()\[\]\"'`/\\|<>{}`~@#$%^&*_+=]")


class QualityScorer(DocProcessor):
    """Score and optionally filter documents by text quality.

    Attributes:
        min_score: Minimum final score in ``[0.0, 1.0]`` required to keep a
            document. Documents below this are dropped. Set to ``None`` to
            disable dropping (the scorer then only annotates metadata).
            Default ``None``.
        score_key: Metadata key under which the final score is written.
            Default ``"quality_score"``.
        detail_key: Metadata key under which the per-dimension breakdown
            ``{dim: {score, weight}, ...}`` is written. Set to ``None`` / empty
            to omit the breakdown. Default ``"quality_detail"``.
        weights: Per-dimension weights. Keys must be a subset of
            ``{length, sentence_completeness, special_char_ratio, repetition,
            information_density}``. Missing dimensions default to
            ``DEFAULT_WEIGHTS``. Dimensions with weight ``0`` are skipped.
        ideal_length: Character count at which the ``length`` dimension scores
            1.0. Below or above this, the score falls off (quadratic within
            ``[0, 2*ideal]``, then linear decay beyond). Default 500.
        min_length: Texts shorter than this (in characters) get a ``length``
            score of 0. Default 20.
        repetition_shingle_size: Character n-gram size used to measure
            repetition. Default 8.
        repetition_word_window: Number of most-common words considered when
            measuring word repetition. Default 10.
    """

    min_score: Optional[float] = None
    score_key: str = "quality_score"
    detail_key: str = "quality_detail"
    weights: Dict[str, float] = dict(DEFAULT_WEIGHTS)
    ideal_length: int = 500
    min_length: int = 20
    repetition_shingle_size: int = 8
    repetition_word_window: int = 10

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Score each document; drop those below ``min_score`` when set."""
        if not origin_docs:
            return []

        self._validate_min_score()
        weights = self._normalised_weights()

        result: List[Document] = []
        dropped = 0
        for doc in origin_docs:
            text = doc.text or ""
            breakdown = self._score_all(text, weights)
            final = self._weighted_average(breakdown, weights)

            kept = True
            if self.min_score is not None and final < self.min_score:
                dropped += 1
                kept = False

            if not kept:
                continue

            meta = dict(doc.metadata or {})
            meta[self.score_key] = round(final, 6)
            if self.detail_key:
                meta[self.detail_key] = {
                    dim: {
                        "score": round(info["score"], 6),
                        "weight": info["weight"],
                    }
                    for dim, info in breakdown.items()
                }
            result.append(Document(text=doc.text, metadata=meta))

        if dropped > 0:
            logger.debug("QualityScorer: dropped %d/%d documents "
                         "(min_score=%s)", dropped, len(origin_docs),
                         self.min_score)
        return result

    # ------------------------------------------------------------------ #
    # Orchestration
    # ------------------------------------------------------------------ #
    def _score_all(self, text: str,
                   weights: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Compute every active dimension's sub-score.

        Args:
            text: The document text.
            weights: Normalised, active dimension weights.

        Returns:
            Mapping ``dim -> {"score": float, "weight": float}`` for each
            active dimension.
        """
        tokens = _WORD_RE.findall(text.lower())
        breakdown: Dict[str, Dict[str, float]] = {}
        for dim in weights:
            if dim == "length":
                breakdown[dim] = self._score_length(text)
            elif dim == "sentence_completeness":
                breakdown[dim] = self._score_sentence_completeness(text)
            elif dim == "special_char_ratio":
                breakdown[dim] = self._score_special_char_ratio(text)
            elif dim == "repetition":
                breakdown[dim] = self._score_repetition(text, tokens)
            elif dim == "information_density":
                breakdown[dim] = self._score_information_density(tokens)
            else:
                # Unknown dimension — skip (already filtered out upstream).
                continue
        return breakdown

    def _validate_min_score(self) -> None:
        """Validate ``min_score`` is None or in ``[0.0, 1.0]``.

        Called from ``_process_docs`` so an invalid value is caught regardless
        of how the instance was built (configer vs. direct construction).
        """
        if self.min_score is None:
            return
        try:
            ms = float(self.min_score)
        except (TypeError, ValueError):
            raise ValueError(
                f"min_score must be numeric or null, got {self.min_score!r}."
            )
        if not 0.0 <= ms <= 1.0:
            raise ValueError(
                f"min_score must be in [0.0, 1.0] or null, got {ms}."
            )

    def _normalised_weights(self) -> Dict[str, float]:
        """Return the active (non-zero) weights, validated.

        Raises ``ValueError`` for unknown dimensions. Empty after filtering
        means the config was all-zeros, which is invalid.
        """
        valid = set(DEFAULT_WEIGHTS)
        active: Dict[str, float] = {}
        for dim, w in self.weights.items():
            if dim not in valid:
                raise ValueError(
                    f"Unknown quality dimension: {dim!r}. "
                    f"Valid dimensions: {sorted(valid)}."
                )
            try:
                w = float(w)
            except (TypeError, ValueError):
                raise ValueError(
                    f"Weight for {dim!r} must be numeric, got {w!r}."
                )
            if w < 0:
                raise ValueError(
                    f"Weight for {dim!r} must be >= 0, got {w}."
                )
            if w > 0:
                active[dim] = w
        if not active:
            raise ValueError(
                "All quality weights are zero; at least one dimension must "
                "have a positive weight."
            )
        return active

    @staticmethod
    def _weighted_average(breakdown: Dict[str, Dict[str, float]],
                          weights: Dict[str, float]) -> float:
        """Return the weight-normalised average of the active sub-scores."""
        total_w = sum(weights[dim] for dim in breakdown)
        if total_w <= 0:
            return 0.0
        acc = 0.0
        for dim, info in breakdown.items():
            acc += weights[dim] * info["score"]
        return acc / total_w

    # ------------------------------------------------------------------ #
    # Dimension scorers — each returns {"score", "weight"} with score in [0,1]
    # ------------------------------------------------------------------ #
    def _score_length(self, text: str) -> Dict[str, float]:
        """Reward documents near ``ideal_length``; penalise very short/long."""
        n = len(text)
        if n == 0:
            return {"score": 0.0, "weight": self.weights["length"]}
        if n <= self.min_length:
            return {"score": 0.0, "weight": self.weights["length"]}
        ideal = max(1, self.ideal_length)
        if n <= 2 * ideal:
            # Quadratic peak at ideal_length within [min, 2*ideal].
            ratio = (n - self.min_length) / max(1, ideal - self.min_length)
            # Bell shape centred at ratio=1, value 1 at peak.
            score = 1.0 - (ratio - 1.0) ** 2
        else:
            # Beyond 2*ideal, decay linearly toward 0 (never negative).
            excess = n - 2 * ideal
            score = max(0.0, 1.0 - excess / (2.0 * ideal))
        return {"score": self._clamp01(score), "weight": self.weights["length"]}

    def _score_sentence_completeness(self, text: str) -> Dict[str, float]:
        """Reward proper sentence terminators; penalise fragments / run-ons.

        Combines two signals:
        - the fraction of punctuation that is a real terminator (``. ! ?``);
        - a penalty when there are words but no terminator at all.
        """
        terminators = _SENTENCE_END_RE.findall(text)
        non_term_punct = _NON_TERMINATOR_PUNCT_RE.findall(text)
        word_count = len(_WORD_RE.findall(text))

        if word_count == 0:
            return {"score": 0.0,
                    "weight": self.weights["sentence_completeness"]}

        total_punct = len(terminators) + len(non_term_punct)
        if total_punct == 0:
            # Words but zero punctuation — likely a fragment / keyword list.
            return {"score": 0.1,
                    "weight": self.weights["sentence_completeness"]}

        term_fraction = len(terminators) / total_punct
        # A document should have roughly one terminator per ~10-25 words.
        # Too few terminators => run-on; too many => choppy. Both reduce score.
        if terminators:
            words_per_sentence = word_count / len(terminators)
            # Ideal around 15; penalise outside [5, 40].
            if 5 <= words_per_sentence <= 40:
                cadence = 1.0
            else:
                cadence = max(0.0, 1.0 - abs(words_per_sentence - 15) / 60.0)
        else:
            cadence = 0.0

        score = 0.5 * term_fraction + 0.5 * cadence
        return {"score": self._clamp01(score),
                "weight": self.weights["sentence_completeness"]}

    def _score_special_char_ratio(self, text: str) -> Dict[str, float]:
        """Penalise a high ratio of special (non-word, non-space) characters."""
        if not text:
            return {"score": 0.0,
                    "weight": self.weights["special_char_ratio"]}
        special = len(_SPECIAL_CHAR_RE.findall(text))
        ratio = special / len(text)
        # 0 special chars -> 1.0; >= 0.3 special -> 0.0; linear between.
        score = 1.0 - min(1.0, ratio / 0.3)
        return {"score": self._clamp01(score),
                "weight": self.weights["special_char_ratio"]}

    def _score_repetition(self, text: str,
                          tokens: List[str]) -> Dict[str, float]:
        """Penalise repeated shingles and dominant repeated words.

        ``repetition_score = 1 - max(shingle_dup_rate, word_dup_rate)``.
        """
        weight = self.weights["repetition"]

        # --- shingle (character n-gram) duplication ---
        shingle_dup = 0.0
        size = max(1, self.repetition_shingle_size)
        if len(text) >= size:
            shingles = [text[i:i + size] for i in range(len(text) - size + 1)]
            if shingles:
                counts = Counter(shingles)
                # Words repeated more than once count as duplicated.
                dup_count = sum(c for c in counts.values() if c > 1) - sum(
                    1 for c in counts.values() if c > 1)
                shingle_dup = max(0.0, dup_count) / len(shingles)

        # --- dominant-word repetition ---
        word_dup = 0.0
        if tokens:
            top = Counter(tokens).most_common(self.repetition_word_window)
            # Share of tokens taken by the single most frequent word beyond
            # its first occurrence.
            if top:
                freq_word, freq_count = top[0]
                if freq_count > 1:
                    word_dup = (freq_count - 1) / len(tokens)

        score = 1.0 - self._clamp01(max(shingle_dup, word_dup))
        return {"score": score, "weight": weight}

    def _score_information_density(self,
                                   tokens: List[str]) -> Dict[str, float]:
        """Reward lexical diversity (distinct tokens / total tokens)."""
        weight = self.weights["information_density"]
        if not tokens:
            return {"score": 0.0, "weight": weight}
        diversity = len(set(tokens)) / len(tokens)
        return {"score": self._clamp01(diversity), "weight": weight}

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #
    @staticmethod
    def _clamp01(value: float) -> float:
        """Clamp ``value`` to the ``[0.0, 1.0]`` range."""
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value

    # ------------------------------------------------------------------ #
    # Config initialisation
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) -> "QualityScorer":
        """Initialise the scorer from its component configuration.

        Validates weights/dimensions and clamps numeric thresholds.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "min_score"):
            ms = doc_processor_configer.min_score
            if ms is None:
                self.min_score = None
            else:
                ms = float(ms)
                if not 0.0 <= ms <= 1.0:
                    raise ValueError(
                        f"min_score must be in [0.0, 1.0] or null, got {ms}."
                    )
                self.min_score = ms

        if hasattr(doc_processor_configer, "score_key"):
            self.score_key = doc_processor_configer.score_key

        if hasattr(doc_processor_configer, "detail_key"):
            self.detail_key = doc_processor_configer.detail_key

        if hasattr(doc_processor_configer, "weights"):
            w = doc_processor_configer.weights
            if not isinstance(w, dict):
                raise ValueError("weights must be a mapping of dim -> number.")
            # Validate eagerly via _normalised_weights.
            self.weights = dict(w)
            self._normalised_weights()

        if hasattr(doc_processor_configer, "ideal_length"):
            self.ideal_length = int(doc_processor_configer.ideal_length)
            if self.ideal_length <= 0:
                raise ValueError("ideal_length must be a positive integer.")

        if hasattr(doc_processor_configer, "min_length"):
            self.min_length = max(0, int(doc_processor_configer.min_length))

        if hasattr(doc_processor_configer, "repetition_shingle_size"):
            self.repetition_shingle_size = max(
                1, int(doc_processor_configer.repetition_shingle_size))

        if hasattr(doc_processor_configer, "repetition_word_window"):
            self.repetition_word_window = max(
                1, int(doc_processor_configer.repetition_word_window))

        return self
