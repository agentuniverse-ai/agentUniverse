#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: text_histogram_tool.py

"""Text frequency-analysis (histogram) tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency text histogram agents
can call to answer "what does this text consist of?": which characters,
words or word n-grams dominate, how uniform the character distribution
is, and how large the text is.

The tool supports four modes, all deterministic and all returning
counts plus percentages:

* ``chars`` — character frequency table. Optional ``case_insensitive``
  folding and an ``ignore_whitespace`` switch (default ``True`` —
  spaces and newlines usually dominate raw counts and hide the
  interesting characters).
* ``words`` — word frequency table with a ``min_length`` filter and
  optional stopword removal (``stopwords='builtin'`` applies a small
  built-in English + Chinese list, ``'en'`` / ``'zh'`` apply the
  language halves, or pass a custom list of strings).
* ``ngrams`` — word n-gram frequency table for ``n`` between 2 and 5.
  N-grams are built over the *unfiltered* token sequence so that
  adjacency is preserved (``min_length`` / ``stopwords`` are words-mode
  options and are not applied here).
* ``summary`` — total characters / words / lines, unique counts, the
  top-5 characters and words, and the Shannon entropy in bits of the
  raw character distribution.

Determinism: every table is ordered by count descending, then by
lexicographic (code-point) order of the value for equal counts, and is
truncated to ``top_n`` (default 20, at most 500). Percentages are
rounded to four decimals and are relative to the tokens actually
counted in the mode (e.g. after whitespace removal or stopword
filtering).

CJK heuristic (documented honestly): the word/n-gram tokenizer splits
on non-alphanumeric characters and treats every CJK ideograph as its
own single-character token, because Chinese text carries no spaces and
proper segmentation needs a dictionary the stdlib does not ship. A
run of Han characters therefore yields one token per character; the
built-in Chinese stopword list is single-character for the same
reason. Mixed runs such as ``abc中def`` split at the CJK boundary
into ``abc``, ``中``, ``def``. This is a fallback, not segmentation.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty or oversized text, ``top_n``
outside 1..500, ``min_length`` outside 1..50, ``n`` outside 2..5,
unknown mode / stopword selector, non-string entries in a custom
stopword list) raise a ``ValueError``, mirroring the other common
tools. Texts that contain no countable tokens at all (for example a
whitespace-only input with ``ignore_whitespace=True``) are not errors:
they yield an empty histogram with a zero denominator.
"""

import math
from collections import Counter
from typing import Any, ClassVar, Dict, FrozenSet, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# CJK ideograph blocks used by the tokenizer fallback (Ext A, URO,
# compatibility ideographs). Kana and Hangul are intentionally not
# included: this is a documented fallback, not full CJK support.
_CJK_RANGES: Tuple[Tuple[int, int], ...] = (
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
)

# Small English stopword list (kept lowercase).
_EN_STOPWORDS: FrozenSet[str] = frozenset(
    """
    a an the and or but if then else when while because as of at by for
    with about into through during before after to from up down in out
    on off over under again is am are was were be been being have has
    had do does did will would can could should shall may might must
    i you he she it we they me him her us them my your his its our
    their this that these those what which who whom whose why how not
    no nor so than too very just there here all any both each few more
    most other some such only own same s t don now
    """.split()
)

# Small Chinese stopword list — single characters only, matching the
# single-CJK-character token fallback described in the module docstring.
_ZH_STOPWORDS: FrozenSet[str] = frozenset(
    "的了在是我有和就不都一上也很好说到要去你会着这那他她它"
    "们与及或但而被把让从对为以于中吗呢吧啊呀哦嗯之其此该各每"
    "某等种些向往给跟比很再又才只还没"
)


class TextHistogramTool(Tool):
    """Deterministic character / word / n-gram frequency analysis tool.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_histogram_tool"
    description: str = (
        "Text histogram tool — pure Python stdlib, no network required. "
        "Character frequency with optional case folding and whitespace "
        "filtering (mode='chars'), word frequency with min_length and "
        "builtin EN/ZH or custom stopwords (mode='words'), word n-gram "
        "frequency for n=2..5 (mode='ngrams'), and a summary with "
        "total chars/words/lines, unique counts, top-5 chars/words and "
        "the Shannon entropy in bits of the character distribution "
        "(mode='summary'). All tables: counts, percentages, top_n "
        "(default 20) and a deterministic count-desc / lexicographic "
        "tie-break order."
    )

    MODES: ClassVar[tuple] = ("chars", "words", "ngrams", "summary")
    STOPWORD_LABELS: ClassVar[Tuple[str, ...]] = ("none", "builtin", "en", "zh")
    STOPWORD_SETS: ClassVar[Dict[str, FrozenSet[str]]] = {
        "none": frozenset(),
        "en": _EN_STOPWORDS,
        "zh": _ZH_STOPWORDS,
        "builtin": _EN_STOPWORDS | _ZH_STOPWORDS,
    }

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        top_n: Any = None,
        case_insensitive: Any = None,
        ignore_whitespace: Any = None,
        min_length: Any = None,
        stopwords: Any = None,
        n: Any = None,
    ) -> Dict[str, Any]:
        """Run one frequency analysis.

        Args:
            mode (str): One of ``chars`` / ``words`` / ``ngrams`` /
                ``summary``.
            text (str): The text to analyse. Required in every mode — a
                non-empty string of at most 100,000 characters.
            top_n (int): Number of table rows to return, 1..500,
                default 20. Applies to the ``chars`` / ``words`` /
                ``ngrams`` tables; the ``summary`` mode always reports
                exactly five rows and ignores ``top_n`` (the value is
                still validated when provided).
            case_insensitive (bool): Fold characters / words to
                lowercase before counting (Unicode ``str.lower``).
                Default ``False``. Applies to the ``chars`` / ``words``
                / ``ngrams`` modes; the ``summary`` mode always uses
                the raw, case-sensitive distribution and ignores this
                flag.
            ignore_whitespace (bool): ``chars`` mode only — skip
                whitespace characters entirely (default ``True``). When
                ``False``, spaces, tabs and newlines are counted like
                any other character. Ignored by the other modes (the
                ``summary`` entropy and unique-character counts always
                use the raw text).
            min_length (int): ``words`` mode only — drop word tokens
                shorter than this many characters, 1..50, default 1.
                Ignored by the other modes (n-grams need the unfiltered
                token sequence to preserve adjacency).
            stopwords (Any): ``words`` mode only — ``None`` / ``"none"``
                (no filtering, the default), ``"builtin"`` (small
                built-in EN+ZH list), ``"en"`` / ``"zh"`` (language
                halves, case-insensitive labels), or a list / tuple /
                set of non-empty strings used as a custom stopword
                list. Ignored by the other modes.
            n (int): ``ngrams`` mode only — the n-gram size, an integer
                between 2 and 5 (there is no default; the parameter is
                required for the ``ngrams`` mode).

        Returns:
            Dict[str, Any]: The analysis result. The table modes return
                ``mode``, the echoed options, ``total_counted`` (the
                percentage denominator), ``unique_count``, ``top_n``
                and a ``histogram`` list of
                ``{"value", "count", "percent"}`` rows ordered by count
                descending then lexicographic value. The ``summary``
                mode returns ``total_chars`` / ``total_words`` /
                ``total_lines``, ``unique_chars`` / ``unique_words``,
                ``top_5_chars`` / ``top_5_words`` (same row shape) and
                ``entropy_bits``.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        clean_top_n = self._validate_top_n(top_n)
        fold = self._validate_flag(
            case_insensitive, "case_insensitive", default=False
        )
        if mode == "summary":
            return self._run_summary(clean_text)
        if mode == "chars":
            skip_ws = self._validate_flag(
                ignore_whitespace, "ignore_whitespace", default=True
            )
            return self._run_chars(clean_text, clean_top_n, fold, skip_ws)
        if mode == "words":
            return self._run_words(
                clean_text, clean_top_n, fold, min_length, stopwords
            )
        return self._run_ngrams(clean_text, clean_top_n, fold, n)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_histogram_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input."""
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
    def _validate_top_n(cls, top_n: Any) -> int:
        """Validate the ``top_n`` row limit (1..500, default 20)."""
        if top_n is None:
            return 20
        if isinstance(top_n, bool) or not isinstance(top_n, int):
            cls._invalid(f"top_n must be an integer between 1 and 500 (got {top_n!r})")
        if not 1 <= top_n <= 500:
            cls._invalid(
                f"top_n must be between 1 and 500 (got {top_n})"
            )
        return top_n

    @classmethod
    def _validate_flag(cls, value: Any, name: str, default: bool) -> bool:
        """Validate a boolean option such as ``case_insensitive``."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        cls._invalid(f"{name} must be a boolean or None (got {value!r})")

    @classmethod
    def _validate_min_length(cls, min_length: Any) -> int:
        """Validate the ``words``-mode ``min_length`` (1..50, default 1)."""
        if min_length is None:
            return 1
        if isinstance(min_length, bool) or not isinstance(min_length, int):
            cls._invalid(
                f"min_length must be an integer between 1 and 50 (got {min_length!r})"
            )
        if not 1 <= min_length <= 50:
            cls._invalid(f"min_length must be between 1 and 50 (got {min_length})")
        return min_length

    @classmethod
    def _validate_stopwords(
        cls, stopwords: Any
    ) -> Tuple[str, FrozenSet[str]]:
        """Validate the ``words``-mode ``stopwords`` selector.

        Returns a ``(label, word_set)`` pair; the label is ``"none"``,
        ``"builtin"``, ``"en"``, ``"zh"`` or ``"custom"``.
        """
        if stopwords is None:
            return "none", frozenset()
        if isinstance(stopwords, str):
            label = stopwords.strip().lower()
            if label in cls.STOPWORD_SETS:
                return label, cls.STOPWORD_SETS[label]
            cls._invalid(
                "stopwords must be one of: "
                f"{', '.join(cls.STOPWORD_LABELS)} (case-insensitive) "
                "or a list of non-empty strings "
                f"(got {stopwords!r})"
            )
        if isinstance(stopwords, (list, tuple, set, frozenset)):
            cleaned: List[str] = []
            for item in stopwords:
                if (
                    item is None
                    or isinstance(item, bool)
                    or not isinstance(item, str)
                    or not item
                ):
                    cls._invalid(
                        "custom stopwords must be a list of non-empty "
                        f"strings (got entry {item!r})"
                    )
                cleaned.append(item)
            return "custom", frozenset(cleaned)
        cls._invalid(
            "stopwords must be one of: "
            f"{', '.join(cls.STOPWORD_LABELS)} (case-insensitive) "
            "or a list of non-empty strings "
            f"(got {stopwords!r})"
        )

    @classmethod
    def _validate_n(cls, n: Any) -> int:
        """Validate the ``ngrams``-mode n-gram size (2..5, no default)."""
        if n is None:
            cls._invalid("n is required for the ngrams mode (got None)")
        if isinstance(n, bool) or not isinstance(n, int):
            cls._invalid(f"n must be an integer between 2 and 5 (got {n!r})")
        if not 2 <= n <= 5:
            cls._invalid(f"n must be between 2 and 5 (got {n})")
        return n

    # ------------------------------------------------------------------ #
    # Tokenizer (shared by words / ngrams / summary)
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

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _build_table(counter: Dict[str, int], top_n: int) -> List[Dict[str, Any]]:
        """Order by count desc then lexicographic value, cut to top_n."""
        total = sum(counter.values())
        ordered = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
        return [
            {
                "value": value,
                "count": count,
                "percent": round(count * 100.0 / total, 4) if total else 0.0,
            }
            for value, count in ordered[:top_n]
        ]

    @staticmethod
    def _entropy_bits(counter: Dict[str, int]) -> float:
        """Shannon entropy in bits over a character distribution."""
        total = sum(counter.values())
        if total <= 0 or len(counter) <= 1:
            return 0.0
        entropy = 0.0
        for count in counter.values():
            probability = count / total
            entropy -= probability * math.log2(probability)
        return round(entropy, 6)

    # ------------------------------------------------------------------ #
    # chars mode
    # ------------------------------------------------------------------ #

    def _run_chars(
        self, text: str, top_n: int, fold: bool, skip_ws: bool
    ) -> Dict[str, Any]:
        """Character frequency table."""
        cleaned = text.lower() if fold else text
        counter = Counter(
            char for char in cleaned if not (skip_ws and char.isspace())
        )
        return {
            "mode": "chars",
            "case_insensitive": fold,
            "ignore_whitespace": skip_ws,
            "total_counted": sum(counter.values()),
            "unique_count": len(counter),
            "top_n": top_n,
            "histogram": self._build_table(counter, top_n),
        }

    # ------------------------------------------------------------------ #
    # words mode
    # ------------------------------------------------------------------ #

    def _run_words(
        self,
        text: str,
        top_n: int,
        fold: bool,
        min_length: Any,
        stopwords: Any,
    ) -> Dict[str, Any]:
        """Word frequency table with min_length and stopword filters."""
        clean_min_length = self._validate_min_length(min_length)
        label, word_set = self._validate_stopwords(stopwords)
        if fold:
            word_set = frozenset(word.lower() for word in word_set)

        tokens = self._tokenize(text)
        if fold:
            tokens = [token.lower() for token in tokens]
        kept = [
            token
            for token in tokens
            if len(token) >= clean_min_length and token not in word_set
        ]
        counter = Counter(kept)
        echo = label if label != "custom" else f"custom({len(word_set)})"
        return {
            "mode": "words",
            "case_insensitive": fold,
            "min_length": clean_min_length,
            "stopwords": echo,
            "total_counted": len(kept),
            "unique_count": len(counter),
            "filtered_out": len(tokens) - len(kept),
            "top_n": top_n,
            "histogram": self._build_table(counter, top_n),
        }

    # ------------------------------------------------------------------ #
    # ngrams mode
    # ------------------------------------------------------------------ #

    def _run_ngrams(
        self, text: str, top_n: int, fold: bool, n: Any
    ) -> Dict[str, Any]:
        """Word n-gram frequency table (n = 2..5)."""
        clean_n = self._validate_n(n)
        tokens = self._tokenize(text)
        if fold:
            tokens = [token.lower() for token in tokens]
        values = [
            " ".join(tokens[index : index + clean_n])
            for index in range(len(tokens) - clean_n + 1)
        ]
        counter = Counter(values)
        return {
            "mode": "ngrams",
            "n": clean_n,
            "case_insensitive": fold,
            "total_counted": len(values),
            "unique_count": len(counter),
            "top_n": top_n,
            "histogram": self._build_table(counter, top_n),
        }

    # ------------------------------------------------------------------ #
    # summary mode
    # ------------------------------------------------------------------ #

    def _run_summary(self, text: str) -> Dict[str, Any]:
        """Overview: totals, uniques, top-5 lists and char entropy.

        Everything here is computed on the raw input: case-sensitive,
        whitespace included for the totals, unique counts and entropy.
        The ``top_5_chars`` list skips whitespace characters (a space
        is not an informative "top character") with percentages
        relative to the non-whitespace character count; the
        ``top_5_words`` list uses the unfiltered CJK-aware tokenizer.
        """
        tokens = self._tokenize(text)
        char_counts = Counter(text)
        non_ws_chars = Counter(
            char for char in text if not char.isspace()
        )
        return {
            "mode": "summary",
            "total_chars": len(text),
            "total_words": len(tokens),
            "total_lines": len(text.splitlines()),
            "unique_chars": len(char_counts),
            "unique_words": len(set(tokens)),
            "top_5_chars": self._build_table(non_ws_chars, 5),
            "top_5_words": self._build_table(Counter(tokens), 5),
            "entropy_bits": self._entropy_bits(char_counts),
        }
