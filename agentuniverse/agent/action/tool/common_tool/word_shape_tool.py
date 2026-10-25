#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: word_shape_tool.py

"""Word shape / digit-normalization / token-feature utility built on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency implementation of the
classic NER-style word-shape features: shape patterns, collapsed
shapes, digit normalization, per-word feature analysis and vocabulary
shape profiling.

Character-to-symbol mapping
---------------------------

Every character of a word maps to exactly one symbol.  The rules are
evaluated in the order below and the **first match wins**, so the table
is exact and deterministic for any input:

===  =============================  ======  ===========================
 #    Character test                Symbol  Examples
===  =============================  ======  ===========================
 1   ``str.isupper()`` — cased         X    ``A``, ``É``, ``Ⅷ``
     uppercase letter
 2   ``str.islower()`` — cased         x    ``a``, ``é``, ``ß``
     lowercase letter
 3   ``str.isdigit()`` — decimal       d    ``0``–``9``, ``²``, ``٣``
     or superscript digit
 4   Unicode name starts with          C    ``一`` (CJK UNIFIED
     ``"CJK"`` — CJK ideograph,              IDEOGRAPH-4E00), ``㐀``,
     compatibility ideograph,               ``豈`` (compatibility),
     radical or stroke                       ``⺆`` (CJK RADICAL)
 5   category ``P*`` — punctuation     p    ``'`` ``-`` ``!`` ``.``,
                                            ``、`` ``「``
 6   category ``S*`` — symbol          s    ``+``, ``$``, ``€``,
                                            ``©``, ``°``
 7   category ``L*`` but neither       L    ``あ``, ``ァ``, ``가``,
     upper nor lower — other               ``々``, ``ǅ``
     letter (kana, hangul, marks,
     titlecase)
 8   anything else — marks ``M*``,     o    space, ``½`` (No), U+0301
     separators ``Z*`` (incl.              combining acute, ``\n``,
     space), numerics ``Nl``/``No``        control characters
     not caught above, control
     ``Cc``, format ``Cf``, unassigned
     ``Cn``
===  =============================  ======  ===========================

Notes on the table:

* Rule 3 uses ``str.isdigit()``, so the superscript ``²`` (category
  ``No``) is a ``d``, while the fraction ``½`` (also ``No`` but not a
  digit) falls through to rule 8 and is an ``o``.
* Rule 4 is name-based, not block-based: the ideographic comma ``、``
  and corner bracket ``「`` are punctuation (rule 5) even though they
  live in CJK-adjacent blocks, while kana and hangul letters fall to
  rule 7 (``L``) because their Unicode names start with ``HIRAGANA`` /
  ``KATAKANA`` / ``HANGUL``, not ``CJK``.

Canonical examples (``shape`` mode, full and collapsed)::

    "Apple"        ->  "Xxxxx"      (collapsed "Xx")
    "APPLE"        ->  "XXXXX"      (collapsed "X")
    "123"          ->  "ddd"        (collapsed "d")
    "McDonald's"   ->  "XxXxxxxxpx" (collapsed "XxXxpx")
    "USA1"         ->  "XXXd"       (collapsed "Xd")
    "hello-world"  ->  "xxxxxpxxxxx" (collapsed "xpx")
    "CAFÉ"         ->  "XXXX"       (collapsed "X")
    "naïve"        ->  "xxxxx"      (collapsed "x")
    "北京2026"       ->  "CCdddd"     (collapsed "Cd")
    "こんにちは"       ->  "LLLLL"      (collapsed "L")
    "€20"          ->  "sdd"        (collapsed "sd")

The *collapsed* shape replaces every run of consecutive identical
symbols with a single symbol (``"Apple" -> "Xx"``, ``"USA1" -> "Xd"``).

Modes
-----

* ``shape`` — map one word (``word``) or a list of words (``words``)
  to the per-word shape string; ``collapsed=True`` switches the output
  to the collapsed variant.  ``len(shape) == len(word)`` always holds
  for the full shape.
* ``normalize_digits`` — replace every maximal run of digits
  (characters with ``str.isdigit()`` true) in ``text`` with a single
  ``"0"`` — the classic number normalization, e.g.
  ``"iPhone 15 Pro" -> "iPhone 0 Pro"``, ``"2026-10-20" -> "0-0-0"``.
* ``analyze`` — compute the full feature dictionary of one word:
  ``shape``, ``collapsed``, ``is_capitalized`` (first character
  ``isupper()``), ``is_all_caps`` (``str.isupper()``, i.e. at least one
  cased character and every cased character uppercase), ``digit_ratio``
  and ``alpha_ratio`` (digit / alphabetic character counts divided by
  the word length), ``has_hyphen``, ``length`` and a ``script`` guess
  (``latin`` / ``cjk`` / ``mixed`` — letters only; ``unknown`` when the
  word contains no letters at all).
* ``batch_shapes`` — tokenize ``text`` on whitespace, map every token
  to its full shape and count shape frequencies; the result is sorted
  by descending count with ties broken by ascending shape string, and
  can be truncated with ``top_n`` (vocabulary shape profiling).

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, both or neither of ``word`` /
``words``, wrong types, empty strings / lists, non-bool ``collapsed``,
invalid ``top_n``, oversized inputs) raise a ``ValueError``, mirroring
the other common tools.
"""

import unicodedata
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


def _char_symbol(ch: str) -> str:
    """Map a single character to its shape symbol (table in module docstring)."""
    if ch.isupper():
        return "X"
    if ch.islower():
        return "x"
    if ch.isdigit():
        return "d"
    try:
        name = unicodedata.name(ch)
    except ValueError:
        # Surrogates / unassigned characters have no name.
        name = ""
    if name.startswith("CJK"):
        return "C"
    category = unicodedata.category(ch)
    if category.startswith("P"):
        return "p"
    if category.startswith("S"):
        return "s"
    if category.startswith("L"):
        return "L"
    return "o"


def word_shape(word: str) -> str:
    """Return the full shape of ``word`` (one symbol per character)."""
    return "".join(_char_symbol(ch) for ch in word)


def collapsed_shape(shape: str) -> str:
    """Collapse consecutive runs of identical symbols to a single symbol."""
    return "".join(
        symbol
        for index, symbol in enumerate(shape)
        if index == 0 or shape[index - 1] != symbol
    )


def digit_runs_to_zero(text: str) -> Tuple[str, int]:
    """Replace every maximal digit run with a single ``"0"``.

    A digit is a character for which ``str.isdigit()`` is true, so the
    replacement covers ASCII ``0-9`` as well as Unicode decimal and
    superscript digits.

    Returns the normalized text and the number of replaced runs.
    """
    parts: List[str] = []
    runs = 0
    index = 0
    length = len(text)
    while index < length:
        if text[index].isdigit():
            runs += 1
            while index < length and text[index].isdigit():
                index += 1
            parts.append("0")
        else:
            parts.append(text[index])
            index += 1
    return "".join(parts), runs


def script_guess(word: str) -> str:
    """Guess the script of ``word`` from its letters.

    CJK characters (symbol ``C``) count toward ``cjk``; every other
    alphabetic character counts toward ``latin`` (an approximation that
    also lumps Cyrillic, Greek, kana and hangul under ``latin``).
    Digits, punctuation, symbols and whitespace are script-neutral.
    """
    has_cjk = False
    has_latin = False
    for ch in word:
        if not ch.isalpha():
            continue
        if _char_symbol(ch) == "C":
            has_cjk = True
        else:
            has_latin = True
    if has_cjk and has_latin:
        return "mixed"
    if has_cjk:
        return "cjk"
    if has_latin:
        return "latin"
    return "unknown"


class WordShapeTool(Tool):
    """Token shape / normalization pattern tool built purely on the stdlib.

    Attributes:
        max_input_chars (int): Upper bound for any single string input;
            longer inputs are rejected before any work.
        max_words (int): Upper bound for the ``words`` list of the
            ``shape`` mode and for ``top_n``.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "word_shape_tool"
    description: str = (
        "Word shape tool — classic NER-style token shape patterns, pure "
        "Python stdlib, no network required. Map a word or word list to "
        "per-word shape strings (uppercase->X, lowercase->x, digit->d, "
        "punctuation->p, CJK ideograph->C, other letter->L, symbol->s, "
        "other->o) with a collapsed variant (mode='shape'), replace every "
        "digit run with a single '0' (mode='normalize_digits'), compute "
        "per-word features — shape, collapsed shape, capitalization, "
        "ratios, hyphen, length, script guess (mode='analyze'), and "
        "profile shape frequencies over whitespace-separated tokens with "
        "an optional top-N (mode='batch_shapes')."
    )

    MODES: ClassVar[tuple] = ("shape", "normalize_digits", "analyze", "batch_shapes")
    SCRIPTS: ClassVar[tuple] = ("latin", "cjk", "mixed", "unknown")

    max_input_chars: int = 100_000
    max_words: int = 10_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        word: Any = None,
        words: Any = None,
        text: Any = None,
        collapsed: Any = None,
        top_n: Any = None,
    ) -> Dict[str, Any]:
        """Run one word-shape operation.

        Args:
            mode (str): One of ``shape`` / ``normalize_digits`` /
                ``analyze`` / ``batch_shapes``.
            word (str): The word to map — required by ``shape`` (unless
                ``words`` is given) and ``analyze``; not used by the
                other modes.
            words (list[str]): A list of words to map — required by
                ``shape`` (unless ``word`` is given); not used by the
                other modes.  Mutually exclusive with ``word``.
            text (str): The input text — required by ``normalize_digits``
                and ``batch_shapes``; not used by the other modes.
            collapsed (bool): ``shape`` mode only — return the collapsed
                variant (consecutive identical symbols merged into one);
                defaults to the full shape.
            top_n (int): ``batch_shapes`` mode only — return only the
                first N shapes of the frequency-sorted list.

        Returns:
            Dict[str, Any]: The operation result under ``result`` plus
                the call context (mode and the validated options).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "shape":
            return self._run_shape(word, words, collapsed)
        if mode == "normalize_digits":
            return self._run_normalize_digits(text)
        if mode == "analyze":
            return self._run_analyze(word)
        return self._run_batch_shapes(text, top_n)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"word_shape_tool: {message}")

    @classmethod
    def _validate_string(cls, value: Any, label: str) -> str:
        """Validate a generic non-empty string input."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{label} must be a non-empty string (got '')")
        if len(value) > 100_000:
            cls._invalid(
                f"{label} exceeds the {100_000:,}-character limit "
                f"(got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _validate_collapsed(cls, collapsed: Any) -> bool:
        """Validate the ``collapsed`` flag of the ``shape`` mode."""
        if collapsed is None:
            return False
        if isinstance(collapsed, bool):
            return collapsed
        cls._invalid(f"collapsed must be a boolean or None (got {collapsed!r})")

    @classmethod
    def _validate_word(cls, word: Any) -> str:
        """Validate the single ``word`` input (``shape`` / ``analyze``)."""
        return cls._validate_string(word, "word")

    @classmethod
    def _validate_words(cls, words: Any) -> List[str]:
        """Validate the ``words`` list input of the ``shape`` mode."""
        if words is None or isinstance(words, (str, bool)) or not isinstance(words, list):
            cls._invalid(f"words must be a non-empty list of non-empty strings (got {words!r})")
        if not words:
            cls._invalid("words must be a non-empty list of non-empty strings (got [])")
        if len(words) > 10_000:
            cls._invalid(
                f"words exceeds the {10_000:,}-item limit (got {len(words):,} items)"
            )
        for item in words:
            if item is None or isinstance(item, bool) or not isinstance(item, str):
                cls._invalid(
                    "every item of words must be a non-empty string "
                    f"(got {item!r})"
                )
            if not item:
                cls._invalid("every item of words must be a non-empty string (got '')")
            if len(item) > 100_000:
                cls._invalid(
                    f"a words item exceeds the {100_000:,}-character limit "
                    f"(got {len(item):,} characters)"
                )
        return words

    @classmethod
    def _validate_top_n(cls, top_n: Any) -> Any:
        """Validate the ``top_n`` option of the ``batch_shapes`` mode."""
        if top_n is None:
            return None
        if isinstance(top_n, bool) or not isinstance(top_n, int):
            cls._invalid(f"top_n must be a positive integer or None (got {top_n!r})")
        if top_n < 1:
            cls._invalid(f"top_n must be a positive integer or None (got {top_n!r})")
        if top_n > 10_000:
            cls._invalid(
                f"top_n exceeds the {10_000:,} limit (got {top_n:,})"
            )
        return top_n

    # ------------------------------------------------------------------ #
    # shape mode
    # ------------------------------------------------------------------ #

    def _run_shape(
        self, word: Any, words: Any, collapsed: Any
    ) -> Dict[str, Any]:
        """Map one word or a list of words to shape strings."""
        clean_collapsed = self._validate_collapsed(collapsed)
        if (word is None) == (words is None):
            self._invalid(
                "shape mode requires exactly one of word or words "
                f"(got word={word!r}, words={words!r})"
            )
        if word is not None:
            clean_word = self._validate_word(word)
            shape = word_shape(clean_word)
            result = collapsed_shape(shape) if clean_collapsed else shape
            return {
                "mode": "shape",
                "collapsed": clean_collapsed,
                "word": clean_word,
                "result": result,
            }
        clean_words = self._validate_words(words)
        shapes = [word_shape(item) for item in clean_words]
        if clean_collapsed:
            shapes = [collapsed_shape(shape) for shape in shapes]
        return {
            "mode": "shape",
            "collapsed": clean_collapsed,
            "count": len(shapes),
            "result": shapes,
        }

    # ------------------------------------------------------------------ #
    # normalize_digits mode
    # ------------------------------------------------------------------ #

    def _run_normalize_digits(self, text: Any) -> Dict[str, Any]:
        """Replace every digit run of the text with a single zero."""
        clean_text = self._validate_string(text, "text")
        normalized, runs = digit_runs_to_zero(clean_text)
        return {
            "mode": "normalize_digits",
            "digit_runs": runs,
            "result": normalized,
        }

    # ------------------------------------------------------------------ #
    # analyze mode
    # ------------------------------------------------------------------ #

    def _run_analyze(self, word: Any) -> Dict[str, Any]:
        """Compute the full feature dictionary of one word."""
        clean_word = self._validate_word(word)
        shape = word_shape(clean_word)
        digits = sum(1 for ch in clean_word if ch.isdigit())
        alphas = sum(1 for ch in clean_word if ch.isalpha())
        length = len(clean_word)
        return {
            "mode": "analyze",
            "word": clean_word,
            "result": {
                "shape": shape,
                "collapsed": collapsed_shape(shape),
                "is_capitalized": clean_word[0].isupper(),
                "is_all_caps": clean_word.isupper(),
                "digit_ratio": digits / length,
                "alpha_ratio": alphas / length,
                "has_hyphen": "-" in clean_word,
                "length": length,
                "script": script_guess(clean_word),
            },
        }

    # ------------------------------------------------------------------ #
    # batch_shapes mode
    # ------------------------------------------------------------------ #

    def _run_batch_shapes(self, text: Any, top_n: Any) -> Dict[str, Any]:
        """Count shape frequencies over the whitespace-split tokens of text."""
        clean_text = self._validate_string(text, "text")
        clean_top_n = self._validate_top_n(top_n)
        tokens = clean_text.split()
        if not tokens:
            self._invalid(
                "text must contain at least one whitespace-separated token"
            )
        counts: Dict[str, int] = {}
        for token in tokens:
            shape = word_shape(token)
            counts[shape] = counts.get(shape, 0) + 1
        ranked = [
            {"shape": shape, "count": count}
            for shape, count in sorted(
                counts.items(), key=lambda item: (-item[1], item[0])
            )
        ]
        if clean_top_n is not None:
            ranked = ranked[:clean_top_n]
        return {
            "mode": "batch_shapes",
            "token_count": len(tokens),
            "unique_count": len(counts),
            "top_n": clean_top_n,
            "result": ranked,
        }
