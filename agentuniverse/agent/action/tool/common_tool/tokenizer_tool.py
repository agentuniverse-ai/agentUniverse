#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: tokenizer_tool.py

"""Multi-strategy word / character tokenizer built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the missing user-facing tokenization primitive:
several sibling tools consume tokens (``LightStemmerTool`` stems a
word list, ``WordShapeTool`` maps token shapes, ``NgramSuggesterTool``
models word n-grams over its own fixed internal splitter,
``TextHistogramTool`` counts words its own way), but none of them
*produces* a configurable token stream an agent can reuse. This tool
is that primitive — zero network, zero dependencies, and every token
carries exact character offsets into the original text.

Three modes:

* ``tokenize`` — split ``text`` with one of seven strategies and
  return ``[{token, start, end}]`` rows whose spans always slice the
  original text (``text[start:end]`` reconstructs the token exactly;
  with ``lowercase=True`` the ``token`` field holds the lowercased
  form and ``text[start:end].lower()`` reconstructs it — the spans
  never move). Strategies:

  - ``whitespace`` — maximal runs of non-whitespace (``str.split``
    semantics, with offsets).
  - ``word`` — the family word rule: maximal runs of alphanumeric
    characters (Unicode ``str.isalnum``) with internal apostrophes so
    English contractions stay together; leading/trailing apostrophes
    are excluded from the span. Han-character runs stay whole here
    because ``isalnum`` covers ideographs and no dictionary
    segmentation is attempted (documented honestly).
  - ``word_punct`` — NLTK ``wordpunct_tokenize``-style: maximal runs
    of word characters (letters, digits, underscore — regex ``\\w``)
    or maximal runs of punctuation / symbol characters
    (``[^\\w\\s]+``), so punctuation is kept as tokens of its own.
  - ``char`` — every character (Unicode code point) as one token,
    spaces included; astral-plane characters such as emoji are single
    code points and therefore single tokens.
  - ``char_no_space`` — every character except whitespace.
  - ``sentence`` — the family's conservative segmentation with the
    abbreviation guard: terminators are ``.`` ``!`` ``?``, the CJK
    full-width forms ``。`` ``！`` ``？``, the ellipsis ``…`` and runs
    of two or more ``.``; newlines end a segment. A latin ``.`` does
    NOT terminate when followed by an alphanumeric character
    (decimals ``3.14``, domains ``example.com``) or preceded by a
    common abbreviation (``Dr.`` ``e.g.`` ``U.S.`` ...), a single
    letter (initials) or an all-digit token. Segments without any
    word character (bare punctuation) are dropped. The span covers
    the sentence including its terminator, trimmed of surrounding
    whitespace.
  - ``cjk`` — per-ideograph fallback for Chinese text: every Han
    ideograph (Ext A, URO, compatibility blocks) is its own
    single-character token while Latin/alphanumeric runs stay whole
    (``abc中def`` → ``abc``, ``中``, ``def``). Kana and Hangul are
    intentionally not split — this is a fallback, not segmentation.

  Options: ``lowercase`` (default off) lowercases the ``token``
  fields in place; ``drop_stopwords`` (default off) removes tokens
  whose comparison form (lowercased when ``lowercase`` is on, the
  original text otherwise) is in the family built-in English +
    Chinese stopword lists (the Chinese list is single-character,
    matching the ``cjk`` strategy's per-ideograph tokens).

* ``span_check`` — the invariant helper: tokenize ``text`` with the
  raw strategies (``strategy`` omitted = all seven) and verify for
  every token that ``0 <= start < end <= len(text)``, that
  ``text[start:end] == token``, that tokens are non-empty, and that
  spans are ascending and non-overlapping. Returns the number of
  tokens checked and the violation list (empty when the invariant
  holds — which is also asserted by the offline test suite over 500
  seeded random texts including CJK, emoji and combining marks).

* ``count`` — token count and type (unique token) count for one
  strategy (default ``word``) under the same ``lowercase`` /
  ``drop_stopwords`` options, with an optional side-by-side
  ``compare`` table of token and type totals for **all** strategies
  (``compare_strategies=True``).

Input validation is strict and happens before any computation:
malformed parameters (unknown mode or strategy, missing/empty
non-string or oversized ``text``, non-boolean flags) raise a
``ValueError``, mirroring the other common tools. Tokenization itself
cannot fail on content: a text with no tokens under the chosen
strategy (whitespace-only input, bare punctuation) returns an empty
token list, not an error.
"""

import re
from typing import Any, ClassVar, Dict, FrozenSet, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# Strategy building blocks
# --------------------------------------------------------------------- #

# whitespace strategy — maximal runs of non-whitespace.
_NON_SPACE_RUN = re.compile(r"\S+")
# word_punct strategy — NLTK wordpunct-style runs: word characters or
# punctuation/symbol runs.
_WORD_PUNCT_RUN = re.compile(r"\w+|[^\w\s]+")

# CJK ideograph blocks used by the cjk strategy (Ext A, URO,
# compatibility ideographs). Kana and Hangul are intentionally not
# included: this is a documented fallback, not full CJK support.
_CJK_RANGES: Tuple[Tuple[int, int], ...] = (
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
)

# --------------------------------------------------------------------- #
# Sentence strategy building blocks (the family rule)
# --------------------------------------------------------------------- #

# Sentence terminators. CJK terminators and the ellipsis always end a
# sentence; the latin period additionally passes through the
# abbreviation guard below. Escaped literals: ideographic full stop
# (U+3002), fullwidth exclamation mark (U+FF01), fullwidth question
# mark (U+FF1F) and ellipsis (U+2026).
_CJK_TERMINATORS = "\u3002\uff01\uff1f\u2026"

# Characters accumulated into the running word used by the guard.
_WORD_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'"
)

# Common English abbreviations whose trailing period must NOT split a
# sentence (matched case-insensitively against the word immediately
# before the period). Single letters (initials such as "J." or the
# "U." and "S." of "U.S.") and all-digit tokens (decimals such as
# "3.14") are guarded separately in _period_ends_sentence.
_ABBREVIATIONS: FrozenSet[str] = frozenset(
    {
        "mr",
        "mrs",
        "ms",
        "dr",
        "prof",
        "sr",
        "jr",
        "st",
        "vs",
        "etc",
        "inc",
        "ltd",
        "co",
        "corp",
        "dept",
        "univ",
        "assn",
        "approx",
        "min",
        "max",
        "no",
        "nos",
        "vol",
        "vols",
        "pp",
        "fig",
        "figs",
        "eq",
        "eqs",
        "al",
        "ca",
        "cf",
        "ed",
        "eds",
        "esq",
        "phd",
        "md",
        "ba",
        "ma",
        "msc",
        "usa",
        "eg",
        "ie",
    }
)

# --------------------------------------------------------------------- #
# Family stopword lists (identical to TextHistogramTool's built-ins)
# --------------------------------------------------------------------- #

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
# cjk strategy's single-CJK-character tokens.
_ZH_STOPWORDS: FrozenSet[str] = frozenset(
    "的了在是我有和就不都一上也很好说到要去你会着这那他她它"
    "们与及或但而被把让从对为以于中吗呢吧啊呀哦嗯之其此该各每"
    "某等种些向往给跟比很再又才只还没"
)

_BUILTIN_STOPWORDS: FrozenSet[str] = _EN_STOPWORDS | _ZH_STOPWORDS


class TokenizerTool(Tool):
    """Multi-strategy tokenizer with character offsets, pure stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input
            length; longer inputs are rejected before any work.
        max_violations_reported (int): Upper bound on the number of
            violation entries a ``span_check`` call returns (the
            ``violation_count`` total is always exact).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "tokenizer_tool"
    description: str = (
        "Tokenizer tool — pure Python stdlib, no network required. "
        "Split text into tokens with exact character offsets using "
        "one of seven strategies (whitespace, word runs with "
        "apostrophes, NLTK-style word_punct, char, char_no_space, "
        "sentence with abbreviation guards, per-ideograph cjk), with "
        "optional lowercasing and built-in English+Chinese stopword "
        "removal (mode='tokenize'), verify the offset invariant "
        "text[start:end] == token over all strategies "
        "(mode='span_check'), and report token/type counts with an "
        "optional side-by-side comparison of all strategies "
        "(mode='count')."
    )

    MODES: ClassVar[tuple] = ("tokenize", "span_check", "count")
    STRATEGIES: ClassVar[tuple] = (
        "whitespace",
        "word",
        "word_punct",
        "char",
        "char_no_space",
        "sentence",
        "cjk",
    )

    max_text_chars: ClassVar[int] = 100_000
    max_violations_reported: ClassVar[int] = 100

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        strategy: Any = None,
        lowercase: Any = None,
        drop_stopwords: Any = None,
        compare_strategies: Any = None,
    ) -> Dict[str, Any]:
        """Run one tokenization operation.

        Args:
            mode (str): One of ``tokenize`` / ``span_check`` /
                ``count``.
            text (str): The text to tokenize. Required for every
                mode.
            strategy (str): The tokenization strategy. Required for
                ``tokenize``; optional for ``count`` (default
                ``word``) and ``span_check`` (omitted = check all
                seven strategies).
            lowercase (bool): ``tokenize`` / ``count`` — lowercase
                the ``token`` fields / count types case-insensitively
                and match stopwords on the lowercased form (default
                off).
            drop_stopwords (bool): ``tokenize`` / ``count`` — drop
                tokens in the built-in English + Chinese stopword
                lists (default off).
            compare_strategies (bool): ``count`` — add a
                side-by-side table of token and type totals for all
                seven strategies (default off).

        Returns:
            Dict[str, Any]: The tokenization result plus call
                context. Tokenization cannot fail on content, so
                there are no content-level error payloads.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        text = self._validate_text(text)
        lowercase = self._validate_bool(lowercase, "lowercase", False)
        drop_stopwords = self._validate_bool(
            drop_stopwords, "drop_stopwords", False
        )
        compare_strategies = self._validate_bool(
            compare_strategies, "compare_strategies", False
        )

        if mode == "tokenize":
            chosen = self._validate_strategy(strategy, required=True)
            return self._run_tokenize(
                text, chosen, lowercase, drop_stopwords
            )
        if mode == "count":
            chosen = self._validate_strategy(strategy, required=False)
            return self._run_count(
                text, chosen, lowercase, drop_stopwords, compare_strategies
            )
        if strategy is None:
            return self._run_span_check(text, "all")
        return self._run_span_check(
            text, self._validate_strategy(strategy, required=False)
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"tokenizer_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (non-empty string, bounded)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > cls.max_text_chars:
            cls._invalid(
                f"text exceeds the {cls.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_bool(cls, value: Any, label: str, default: bool) -> bool:
        """Validate an optional boolean flag (None means the default)."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        cls._invalid(f"{label} must be a boolean (got {value!r})")

    @classmethod
    def _validate_strategy(cls, strategy: Any, required: bool) -> str:
        """Validate the ``strategy`` option against the known set."""
        if strategy is None:
            if required:
                cls._invalid(
                    "strategy is required for the tokenize mode and must be "
                    f"one of: {', '.join(cls.STRATEGIES)}"
                )
            return "word"
        if isinstance(strategy, bool) or not isinstance(strategy, str):
            cls._invalid(
                f"strategy must be one of: {', '.join(cls.STRATEGIES)} "
                f"(got {strategy!r})"
            )
        if strategy not in cls.STRATEGIES:
            cls._invalid(
                f"strategy must be one of: {', '.join(cls.STRATEGIES)} "
                f"(got {strategy!r})"
            )
        return strategy

    # ------------------------------------------------------------------ #
    # Raw tokenization strategies — every token is the EXACT original
    # slice text[start:end] (the offset invariant).
    # ------------------------------------------------------------------ #

    @staticmethod
    def _tokenize_whitespace(text: str) -> List[Dict[str, Any]]:
        """Maximal runs of non-whitespace characters."""
        return [
            {"token": m.group(), "start": m.start(), "end": m.end()}
            for m in _NON_SPACE_RUN.finditer(text)
        ]

    @classmethod
    def _tokenize_word(cls, text: str) -> List[Dict[str, Any]]:
        """Alphanumeric runs with internal apostrophes (family rule).

        A token is a maximal run of alphanumeric characters (Unicode
        ``str.isalnum``) plus internal apostrophes so English
        contractions stay together; leading/trailing apostrophes are
        excluded from the span. Han runs stay whole (see the module
        docstring for the honest scope).
        """
        return cls._alnum_runs(text, split_cjk=False)

    @staticmethod
    def _tokenize_word_punct(text: str) -> List[Dict[str, Any]]:
        """NLTK wordpunct-style runs: ``\\w+`` or ``[^\\w\\s]+``."""
        return [
            {"token": m.group(), "start": m.start(), "end": m.end()}
            for m in _WORD_PUNCT_RUN.finditer(text)
        ]

    @staticmethod
    def _tokenize_chars(text: str, keep_spaces: bool) -> List[Dict[str, Any]]:
        """Every Unicode code point (optionally without whitespace).

        Astral-plane characters (emoji, rare scripts) are single code
        points in Python strings and therefore single tokens; a
        combining mark is a separate code point and thus a separate
        token (documented honestly — this tool does not fuse
        grapheme clusters).
        """
        tokens: List[Dict[str, Any]] = []
        for index, char in enumerate(text):
            if not keep_spaces and char.isspace():
                continue
            tokens.append(
                {"token": char, "start": index, "end": index + 1}
            )
        return tokens

    @classmethod
    def _tokenize_sentence(cls, text: str) -> List[Dict[str, Any]]:
        """Conservative sentence segmentation with abbreviation guard.

        Mirrors the family rule (see the module docstring). The span
        covers the sentence including its terminator, trimmed of
        surrounding whitespace; offsets refer to the original text
        (dot runs are handled in place, never rewritten).
        """
        tokens: List[Dict[str, Any]] = []
        total = len(text)
        seg_start: int = 0
        open_segment = False
        word: List[str] = []

        def flush(end: int) -> None:
            nonlocal seg_start, open_segment, word
            if open_segment:
                start, stop = seg_start, end
                while start < stop and text[start].isspace():
                    start += 1
                while stop > start and text[stop - 1].isspace():
                    stop -= 1
                if start < stop and any(
                    ch.isalnum() for ch in text[start:stop]
                ):
                    tokens.append(
                        {"token": text[start:stop], "start": start, "end": stop}
                    )
            open_segment = False
            word = []

        index = 0
        while index < total:
            char = text[index]
            if char in "\r\n":
                flush(index)
                index += 1
                continue
            if not open_segment:
                seg_start = index
                open_segment = True
            if char in _CJK_TERMINATORS:
                flush(index + 1)
            elif char in "!?":
                flush(index + 1)
            elif char == ".":
                run_end = index
                while run_end < total and text[run_end] == ".":
                    run_end += 1
                if run_end - index >= 2:
                    # A run of two or more '.' is one ellipsis
                    # terminator ending at the last dot.
                    flush(run_end)
                    index = run_end
                    continue
                if cls._period_ends_sentence(text, index, "".join(word)):
                    flush(index + 1)
                else:
                    word = []
            else:
                if char in _WORD_CHARS:
                    word.append(char)
                else:
                    word = []
            index += 1
        flush(total)
        return tokens

    @staticmethod
    def _period_ends_sentence(
        text: str, index: int, word_run: str
    ) -> bool:
        """Decide whether the latin '.' at ``index`` ends its sentence.

        Returns False (guard applies, no boundary) when the next
        character is alphanumeric — decimals ``3.14``, domains
        ``example.com`` — or the word run before the period is a
        known abbreviation, a single letter (initials, ``U.S.``), or
        all digits.
        """
        if index + 1 < len(text) and text[index + 1].isalnum():
            return False
        token = word_run.rstrip("'").lower()
        if not token:
            return True
        return not (
            token in _ABBREVIATIONS or len(token) == 1 or token.isdigit()
        )

    @classmethod
    def _tokenize_cjk(cls, text: str) -> List[Dict[str, Any]]:
        """Per-ideograph CJK fallback with Latin runs intact.

        Every Han ideograph is its own single-character token;
        alphanumeric runs (with internal apostrophes) stay whole and
        split at the ideograph boundary (``abc中def`` → ``abc``,
        ``中``, ``def``).
        """
        return cls._alnum_runs(text, split_cjk=True)

    @classmethod
    def _alnum_runs(
        cls, text: str, split_cjk: bool
    ) -> List[Dict[str, Any]]:
        """Shared word/cjk scanner with exact, apostrophe-trimmed spans."""
        tokens: List[Dict[str, Any]] = []
        run_start = 0
        run_end = 0  # exclusive
        in_run = False

        def flush() -> None:
            nonlocal in_run
            if in_run:
                # Trim leading/trailing apostrophes from the span so
                # the token is exactly text[start:end].
                start, stop = run_start, run_end
                while start < stop and text[start] == "'":
                    start += 1
                while stop > start and text[stop - 1] == "'":
                    stop -= 1
                if start < stop:
                    tokens.append(
                        {
                            "token": text[start:stop],
                            "start": start,
                            "end": stop,
                        }
                    )
            in_run = False

        for index, char in enumerate(text):
            if split_cjk and cls._is_cjk(char):
                flush()
                tokens.append(
                    {"token": char, "start": index, "end": index + 1}
                )
            elif char.isalnum() or char == "'":
                if not in_run:
                    run_start = index
                    in_run = True
                run_end = index + 1
            else:
                flush()
        flush()
        return tokens

    @staticmethod
    def _is_cjk(char: str) -> bool:
        """Return True for Han ideographs (Ext A, URO, compatibility)."""
        code = ord(char)
        return any(low <= code <= high for low, high in _CJK_RANGES)

    # ------------------------------------------------------------------ #
    # Option pipeline (applied AFTER the raw spans are computed)
    # ------------------------------------------------------------------ #

    @classmethod
    def _apply_options(
        cls,
        tokens: List[Dict[str, Any]],
        lowercase: bool,
        drop_stopwords: bool,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Return the option-adjusted stream and the dropped count.

        Order of operations (documented): the comparison form is the
        lowercased token when ``lowercase`` is on, the original
        otherwise; stopword matching uses that form; ``lowercase``
        then rewrites the surviving ``token`` fields in place (the
        ``start`` / ``end`` offsets never move and keep pointing at
        the original text).
        """
        kept: List[Dict[str, Any]] = []
        dropped = 0
        for entry in tokens:
            form = entry["token"].lower() if lowercase else entry["token"]
            if drop_stopwords and form in _BUILTIN_STOPWORDS:
                dropped += 1
                continue
            if lowercase:
                kept.append(
                    {
                        "token": form,
                        "start": entry["start"],
                        "end": entry["end"],
                    }
                )
            else:
                kept.append(entry)
        return kept, dropped

    # ------------------------------------------------------------------ #
    # Modes
    # ------------------------------------------------------------------ #

    @classmethod
    def _raw_tokens(
        cls, text: str, strategy: str
    ) -> List[Dict[str, Any]]:
        """Dispatch to the raw tokenizer for one strategy."""
        if strategy == "whitespace":
            return cls._tokenize_whitespace(text)
        if strategy == "word":
            return cls._tokenize_word(text)
        if strategy == "word_punct":
            return cls._tokenize_word_punct(text)
        if strategy == "char":
            return cls._tokenize_chars(text, keep_spaces=True)
        if strategy == "char_no_space":
            return cls._tokenize_chars(text, keep_spaces=False)
        if strategy == "sentence":
            return cls._tokenize_sentence(text)
        return cls._tokenize_cjk(text)

    def _run_tokenize(
        self, text: str, strategy: str, lowercase: bool, drop_stopwords: bool
    ) -> Dict[str, Any]:
        """tokenize mode — token stream with offsets and options."""
        raw = self._raw_tokens(text, strategy)
        tokens, dropped = self._apply_options(raw, lowercase, drop_stopwords)
        return {
            "mode": "tokenize",
            "strategy": strategy,
            "lowercase": lowercase,
            "drop_stopwords": drop_stopwords,
            "token_count": len(tokens),
            "dropped_stopword_count": dropped,
            "tokens": tokens,
        }

    def _run_count(
        self,
        text: str,
        strategy: str,
        lowercase: bool,
        drop_stopwords: bool,
        compare_strategies: bool,
    ) -> Dict[str, Any]:
        """count mode — token/type totals, optionally per strategy."""
        result: Dict[str, Any] = {
            "mode": "count",
            "strategy": strategy,
            "lowercase": lowercase,
            "drop_stopwords": drop_stopwords,
        }
        result.update(
            self._count_one(text, strategy, lowercase, drop_stopwords)
        )
        if compare_strategies:
            result["compare"] = {
                each: self._count_one(text, each, lowercase, drop_stopwords)
                for each in self.STRATEGIES
            }
        return result

    @classmethod
    def _count_one(
        cls, text: str, strategy: str, lowercase: bool, drop_stopwords: bool
    ) -> Dict[str, int]:
        """Token and type totals for one strategy under the options."""
        raw = cls._raw_tokens(text, strategy)
        tokens, _ = cls._apply_options(raw, lowercase, drop_stopwords)
        return {
            "token_count": len(tokens),
            "type_count": len({entry["token"] for entry in tokens}),
        }

    def _run_span_check(
        self, text: str, strategy: str
    ) -> Dict[str, Any]:
        """span_check mode — validate the offset invariant.

        ``strategy`` is the literal string ``"all"`` when the caller
        omitted it: every strategy is checked over the raw (un-
        transformed) token streams, which is where every option-
        adjusted output comes from — options rewrite token strings
        and filter, they never move spans.
        """
        strategies = (
            self.STRATEGIES if strategy == "all" else (strategy,)
        )
        violations: List[Dict[str, Any]] = []
        tokens_checked = 0
        for each in strategies:
            previous_end = 0
            for index, entry in enumerate(
                self._raw_tokens(text, each)
            ):
                tokens_checked += 1
                token = entry["token"]
                start = entry["start"]
                end = entry["end"]
                problem = None
                if not isinstance(start, int) or not isinstance(end, int):
                    problem = "non_integer_span"
                elif not (0 <= start < end <= len(text)):
                    problem = "span_out_of_range"
                elif not token:
                    problem = "empty_token"
                elif text[start:end] != token:
                    problem = "slice_mismatch"
                elif start < previous_end:
                    problem = "overlapping_or_unordered_span"
                if problem is not None:
                    violations.append(
                        {
                            "strategy": each,
                            "index": index,
                            "token": token,
                            "start": start,
                            "end": end,
                            "reason": problem,
                        }
                    )
                else:
                    previous_end = end
        reported = violations[: self.max_violations_reported]
        return {
            "mode": "span_check",
            "strategy": strategy,
            "text_length": len(text),
            "strategies_checked": list(strategies),
            "tokens_checked": tokens_checked,
            "violation_count": len(violations),
            "violations": reported,
            "ok": not violations,
        }
