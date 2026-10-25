#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: collocation_tool.py

"""Word-pair collocation discovery tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency corpus-statistics
utility: agents can discover which word pairs co-occur and how
strongly they are associated. ``TextHistogramTool`` counts unigrams
and ``NgramSuggesterTool`` models next-word likelihood; ranked bigram
discovery with association scores is the gap this tool fills.

Three modes:

* ``bigrams`` — count all adjacent word pairs of ``text``. Pairs are
  formed *within a sentence only*: the text is split on ``.`` ``!``
  ``?`` and their CJK equivalents (``。`` ``！`` ``？``), and no pair
  ever spans two sentences, so ``... end. Start ...`` does not produce
  the pair ``end Start``. Tokens follow the established tokenizer
  family convention: a token is a maximal run of alphanumeric
  characters (Unicode ``str.isalnum``) plus internal apostrophes
  (trimmed at the edges), and every CJK ideograph is emitted as its
  own single-character token — the documented stdlib fallback for
  unspaced Chinese, not real segmentation. Optional ``casefold``
  (default off) folds every token with ``str.casefold()`` before
  counting. The result is a list of ``{pair, count}`` rows — pairs are
  space-joined ``"first second"`` strings — sorted by count descending
  then pair ascending, truncated to ``top_n`` (default 50), plus the
  total pair observation count.
* ``scored`` — the top bigrams with three standard association
  measures computed from the joint frequency ``F(xy)``, the unigram
  frequencies ``F(x)`` / ``F(y)`` and the total token count ``N`` of
  the same text:

  - ``pmi`` — pointwise mutual information,
    ``log2(F(xy) * N / (F(x) * F(y)))``, 3 decimal places;
  - ``dice`` — Dice coefficient, ``2 * F(xy) / (F(x) + F(y))``,
    6 decimal places, always in [0, 1];
  - ``t_score`` — t-score,
    ``(F(xy) - F(x) * F(y) / N) / sqrt(F(xy))``, 3 decimal places.

  Rows are sorted by ``pmi`` descending, then count descending, then
  pair ascending. **Low-frequency PMI explosion**: a pair seen once
  between two otherwise-rare words earns a huge PMI (an F(xy) of 1
  with F(x) = F(y) = 1 already scores log2(N)), so ``min_count``
  (default 3) filters pairs below a joint-frequency floor before
  scoring — the standard mitigation, applied and documented here.
* ``pair_lookup`` — given one ``word``, return its top collocates:
  every pair containing the word in *either order* (queried word
  first or second), with counts and the position of the queried word
  in each pair. When ``casefold`` is on, the queried word is folded
  with the same ``str.casefold()`` before matching.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing/empty text, a ``word``
that is not a single whitespace-free string, ``top_n`` out of range,
``min_count`` below 1, wrong boolean types, oversized inputs) raise a
``ValueError``, mirroring the other common tools. Texts that yield no
pairs at all (a single word, or sentence splits that leave one-token
fragments) are not errors: they return an empty table with zero
totals.
"""

import math
import re
from collections import Counter
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Sentence terminators (ASCII + CJK full-width forms) — the same split
# the n-gram tool uses, so no bigram ever crosses a sentence boundary.
_SENTENCE_SPLIT = re.compile("[.!?。！？]")

# CJK ideograph blocks used by the tokenizer fallback (Ext A, URO,
# compatibility ideographs) — identical to TextHistogramTool. Kana and
# Hangul are intentionally not included: this is a documented
# fallback, not full CJK support.
_CJK_RANGES: Tuple[Tuple[int, int], ...] = (
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
)


class CollocationTool(Tool):
    """Word-pair collocation discovery tool.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input
            length; longer inputs are rejected before any work.
        max_word_chars (int): Upper bound on the ``word`` input
            length for the ``pair_lookup`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "collocation_tool"
    description: str = (
        "Collocation tool — pure Python stdlib, no network required. "
        "Discover word pairs that co-occur: count sentence-internal "
        "adjacent word pairs with optional casefolding (mode='bigrams', "
        "EN words + CJK chars as tokens, {pair, count} rows sorted by "
        "count desc then pair asc, top_n default 50), score the top "
        "bigrams with PMI, Dice and t-score association measures "
        "(mode='scored', sorted by PMI desc, min_count default 3 to "
        "defuse the low-frequency PMI explosion), or look up the top "
        "collocates of one specific word in both orders "
        "(mode='pair_lookup')."
    )

    MODES: ClassVar[tuple] = ("bigrams", "scored", "pair_lookup")
    TOP_N_RANGE: ClassVar[tuple] = (1, 1000)
    MIN_COUNT_RANGE: ClassVar[tuple] = (1, 1_000_000)

    max_text_chars: int = 100_000
    max_word_chars: int = 1_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        word: Any = None,
        top_n: Any = None,
        casefold: Any = None,
        min_count: Any = None,
    ) -> Dict[str, Any]:
        """Run one collocation-discovery operation.

        Args:
            mode (str): One of ``bigrams`` / ``scored`` /
                ``pair_lookup``.
            text (str): The corpus text; required by every mode.
            word (str): The ``pair_lookup`` mode target — a single
                word without whitespace; not used by the other modes.
            top_n (int): Rows kept in the result table; 1 to 1000,
                default 50.
            casefold (bool): Fold every token (and the ``word``) with
                ``str.casefold()`` before counting/matching
                (default off).
            min_count (int): ``scored`` mode only — minimum joint
                frequency for a pair to be scored; 1 to 1,000,000,
                default 3.

        Returns:
            Dict[str, Any]: The operation result plus call context.
                Texts with no formable pairs return empty tables with
                zero totals rather than errors.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        clean_casefold = self._validate_bool(casefold, "casefold", False)
        clean_top_n = self._validate_int_option(
            top_n, "top_n", 50, *self.TOP_N_RANGE
        )
        if mode == "pair_lookup":
            clean_word = self._validate_word(word)
            return self._run_pair_lookup(
                clean_text, clean_word, clean_casefold, clean_top_n
            )
        clean_min_count = self._validate_int_option(
            min_count, "min_count", 3, *self.MIN_COUNT_RANGE
        )
        if mode == "bigrams":
            return self._run_bigrams(
                clean_text, clean_casefold, clean_top_n
            )
        return self._run_scored(
            clean_text, clean_casefold, clean_top_n, clean_min_count
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"collocation_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (non-empty, bounded)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_word(cls, word: Any) -> str:
        """Validate the ``pair_lookup`` word (single, whitespace-free)."""
        if word is None or isinstance(word, bool) or not isinstance(word, str):
            cls._invalid(
                "word is required for the pair_lookup mode and must be a "
                f"single word without whitespace (got {word!r})"
            )
        if not word.strip():
            cls._invalid(
                "word must be a single word without whitespace "
                "(got an empty or blank string)"
            )
        if len(word) > 1_000:
            cls._invalid(
                f"word exceeds the {1_000:,}-character limit "
                f"(got {len(word):,} characters)"
            )
        if any(char.isspace() for char in word):
            cls._invalid(
                "word must be a single word without whitespace (got "
                f"{word!r}); query each word of a phrase separately"
            )
        return word

    @classmethod
    def _validate_bool(cls, value: Any, label: str, default: bool) -> bool:
        """Validate an optional boolean flag (None means the default)."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        cls._invalid(f"{label} must be a boolean (got {value!r})")

    @classmethod
    def _validate_int_option(
        cls, value: Any, label: str, default: int, low: int, high: int
    ) -> int:
        """Validate an optional integer option within an inclusive range."""
        if value is None:
            return default
        if isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(
                f"{label} must be an integer between {low} and {high} (got {value!r})"
            )
        if value < low or value > high:
            cls._invalid(f"{label} must be an integer between {low} and {high} (got {value})")
        return value

    # ------------------------------------------------------------------ #
    # Tokenizer (the established family convention)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _is_cjk(char: str) -> bool:
        """Return True for Han ideographs (Ext A, URO, compatibility)."""
        code = ord(char)
        return any(low <= code <= high for low, high in _CJK_RANGES)

    @classmethod
    def _tokenize(cls, text: str) -> List[str]:
        """Split text into word tokens with the CJK char fallback.

        A token is a maximal run of alphanumeric characters (Unicode
        ``str.isalnum``) plus internal apostrophes so English
        contractions stay together; leading/trailing apostrophes are
        trimmed. Every CJK ideograph is emitted as its own
        single-character token (see the module docstring for the
        honest scope of that heuristic).
        """
        tokens: List[str] = []
        run: List[str] = []

        def flush() -> None:
            if run:
                word = "".join(run).strip("'")
                if word:
                    tokens.append(word)
                run.clear()

        for char in text:
            if cls._is_cjk(char):
                flush()
                tokens.append(char)
            elif char.isalnum() or char == "'":
                run.append(char)
            else:
                flush()
        flush()
        return tokens

    @classmethod
    def _sentence_tokens(cls, text: str, casefold: bool) -> List[List[str]]:
        """Tokenize each sentence separately (no cross-sentence pairs)."""
        sentences: List[List[str]] = []
        for segment in _SENTENCE_SPLIT.split(text):
            tokens = cls._tokenize(segment)
            if casefold:
                tokens = [token.casefold() for token in tokens]
            if tokens:
                sentences.append(tokens)
        return sentences

    # ------------------------------------------------------------------ #
    # Counting helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _count(
        cls, text: str, casefold: bool
    ) -> Tuple[Counter, Counter, int]:
        """Return (bigram counts, unigram counts, total tokens).

        Bigrams are sentence-internal only. Unigrams and the total
        token count N are taken over the same token stream, so the
        association formulas stay internally consistent.
        """
        bigrams: Counter = Counter()
        unigrams: Counter = Counter()
        total_tokens = 0
        for tokens in cls._sentence_tokens(text, casefold):
            total_tokens += len(tokens)
            for token in tokens:
                unigrams[token] += 1
            for first, second in zip(tokens, tokens[1:]):
                bigrams[(first, second)] += 1
        return bigrams, unigrams, total_tokens

    @staticmethod
    def _ordered_pairs(counts: Counter) -> List[Tuple[Tuple[str, str], int]]:
        """Order (pair, count) rows by count desc then pair ascending."""
        return sorted(
            counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1])
        )

    # ------------------------------------------------------------------ #
    # bigrams mode
    # ------------------------------------------------------------------ #

    def _run_bigrams(
        self, text: str, casefold: bool, top_n: int
    ) -> Dict[str, Any]:
        """Count all sentence-internal adjacent word pairs."""
        bigram_counts, _, _ = self._count(text, casefold)
        ordered = self._ordered_pairs(bigram_counts)
        return {
            "mode": "bigrams",
            "casefold": casefold,
            "top_n": top_n,
            "total_bigrams": sum(bigram_counts.values()),
            "distinct_pairs": len(bigram_counts),
            "bigrams": [
                {"pair": f"{first} {second}", "count": count}
                for (first, second), count in ordered[:top_n]
            ],
        }

    # ------------------------------------------------------------------ #
    # scored mode
    # ------------------------------------------------------------------ #

    def _run_scored(
        self, text: str, casefold: bool, top_n: int, min_count: int
    ) -> Dict[str, Any]:
        """Score top bigrams with PMI, Dice and t-score."""
        bigram_counts, unigram_counts, total_tokens = self._count(
            text, casefold
        )

        scored: List[Dict[str, Any]] = []
        for (first, second), joint in bigram_counts.items():
            if joint < min_count:
                continue
            f_first = unigram_counts[first]
            f_second = unigram_counts[second]
            pmi = round(
                math.log2(joint * total_tokens / (f_first * f_second)), 3
            )
            dice = round(2.0 * joint / (f_first + f_second), 6)
            t_score = round(
                (joint - f_first * f_second / total_tokens)
                / math.sqrt(joint),
                3,
            )
            scored.append(
                {
                    "pair": f"{first} {second}",
                    "count": joint,
                    "pmi": pmi,
                    "dice": dice,
                    "t_score": t_score,
                }
            )

        # Sorted by pmi desc, then count desc, then pair ascending.
        scored.sort(key=lambda row: (-row["pmi"], -row["count"], row["pair"]))
        return {
            "mode": "scored",
            "casefold": casefold,
            "min_count": min_count,
            "top_n": top_n,
            "total_tokens": total_tokens,
            "distinct_pairs": len(bigram_counts),
            "qualifying_pairs": len(scored),
            "collocations": scored[:top_n],
            "note": {
                "type": "low_frequency_pmi",
                "message": (
                    "PMI explodes for rare pairs (a joint frequency of 1 "
                    "between two hapax words already scores log2(N)), so "
                    f"pairs below min_count={min_count} joint occurrences "
                    "are filtered out before scoring; raise min_count for "
                    "a stricter corpus-statistics guarantee or set it to 1 "
                    "to score everything."
                ),
            },
        }

    # ------------------------------------------------------------------ #
    # pair_lookup mode
    # ------------------------------------------------------------------ #

    def _run_pair_lookup(
        self, text: str, word: str, casefold: bool, top_n: int
    ) -> Dict[str, Any]:
        """List the top collocates of one word, in both orders."""
        if casefold:
            word = word.casefold()
        bigram_counts, _, _ = self._count(text, casefold)

        matches: List[Dict[str, Any]] = []
        for (first, second), count in bigram_counts.items():
            at_first = first == word
            at_second = second == word
            if not (at_first or at_second):
                continue
            if at_first and at_second:
                position = "both"
            elif at_first:
                position = "first"
            else:
                position = "second"
            matches.append(
                {
                    "pair": f"{first} {second}",
                    "count": count,
                    "position": position,
                }
            )

        matches.sort(key=lambda row: (-row["count"], row["pair"]))
        return {
            "mode": "pair_lookup",
            "word": word,
            "casefold": casefold,
            "top_n": top_n,
            "total_pairs_with_word": len(matches),
            "collocates": matches[:top_n],
        }
