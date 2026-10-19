#!/usr/bin/env python3
# ruff: noqa: TRY003

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: case_converter_tool.py

"""Text case / style conversion tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency case converter agents
can call for identifier plumbing: normalizing user-typed identifiers to
``snake_case`` before a lookup, building URL slugs from arbitrary
titles, or re-casing prose for display.

The tool supports ten modes, all implemented with plain ``str``
methods and two small regular expressions (plus ``unicodedata`` for the
slug fold):

* ``upper`` / ``lower`` — whole-text Unicode-aware casing via
  ``str.upper()`` / ``str.lower()``. Every character is preserved;
  only its case changes. CJK ideographs and other caseless scripts
  pass through untouched.
* ``title`` — Title Case with small-word handling: every word is
  capitalized except the English small words ``a`` / ``an`` / ``the`` /
  ``of`` / ``and``, which stay lowercase *unless* they are the first or
  the last word of the text. Whitespace and punctuation are preserved
  exactly; only the case of word characters changes.
* ``sentence`` — sentence case: the first cased character of the text
  is uppercased and every other cased character is lowercased. All
  separators and caseless characters are preserved.
* ``snake`` / ``kebab`` / ``camel`` / ``pascal`` / ``constant`` —
  identifier styles built from a common word tokenizer: lowercase
  ``snake_case``, lowercase ``kebab-case``, lower-``camelCase``,
  ``PascalCase`` and upper ``CONSTANT_CASE``. Multi-word input is
  split on runs of whitespace, underscores, dashes and *any other
  non-alphanumeric characters*, plus camel-hump boundaries detected
  with the classic two-rule split — a lowercase-to-uppercase
  transition (``getHTTP`` → ``get`` + ``HTTP``) and the last letter of
  an uppercase run followed by a lowercase letter (``HTTPServer`` →
  ``HTTP`` + ``Server``), so acronyms survive the split. Digits never
  create a boundary (``model2vec`` and ``sha256Sum`` stay single
  words). Words are
  re-cased with Unicode-aware ``str`` methods; acronyms are normalized
  to the target style (``HTTPServer`` → ``http_server`` in snake mode,
  ``httpServer`` in camel mode).
* ``slug`` — URL slug: the text is NFKD-normalized, combining marks
  are stripped (so ``José`` folds to ``jose``), the remainder is
  lowercased, and every run of non-alphanumeric characters becomes a
  single ``-`` with no leading or trailing dash. CJK and other
  caseless scripts survive the fold because they have no diacritics
  to strip.

Input validation is strict and happens before any computation: an
unknown mode, a missing / empty / non-string text, or text longer than
100,000 characters raises a ``ValueError``, mirroring the other common
tools. All conversions are deterministic and never touch the network.
"""

import re
import unicodedata
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Maximal runs of Unicode alphanumeric characters (word chars without
# the underscore — the underscore acts as a separator instead).
_ALNUM_RUN = re.compile(r"[^\W_]+")
# Title-mode tokenizer: word runs and everything else, both kept.
_TITLE_TOKENS = re.compile(r"([^\W_]+)|([\W_]+)")
# Camel-hump boundaries (ASCII letters only; other scripts have no humps).
_LOWER_TO_UPPER = re.compile(r"([a-z])([A-Z])")
_ACRONYM_TO_WORD = re.compile(r"([A-Z]+)([A-Z][a-z])")
# English small words kept lowercase in title mode (except first/last).
_SMALL_WORDS = frozenset({"a", "an", "the", "of", "and"})

# Sentinel inserted at hump boundaries; a word run can never contain NUL.
_HUMP = "\x00"


class CaseConverterTool(Tool):
    """Text case / style conversion tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "case_converter_tool"
    description: str = (
        "Case converter tool — pure Python stdlib, no network required. "
        "Unicode-aware case modes upper/lower/title (title keeps the "
        "small words a/an/the/of/and lowercase unless first or last) "
        "and sentence, plus identifier modes snake_case, kebab-case, "
        "camelCase, PascalCase, CONSTANT_CASE and URL slug "
        "(NFKD ascii-fold: Jose with an acute becomes jose). "
        "Multi-word input is split on spaces, underscores, dashes and "
        "camel humps, with acronym-safe splitting (HTTPServer -> "
        "http_server)."
    )

    MODES: ClassVar[tuple] = (
        "upper",
        "lower",
        "title",
        "sentence",
        "snake",
        "kebab",
        "camel",
        "pascal",
        "constant",
        "slug",
    )

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(self, mode: Any, text: Any = None) -> dict[str, Any]:
        """Convert ``text`` to the case / style selected by ``mode``.

        Args:
            mode (str): One of ``upper``, ``lower``, ``title``,
                ``sentence``, ``snake``, ``kebab``, ``camel``,
                ``pascal``, ``constant``, ``slug``.
            text (str): The non-empty text to convert (at most 100,000
                characters).

        Returns:
            dict[str, Any]: ``{"mode": <mode>, "result": <converted>}``.
                The identifier and slug modes return an empty string
                when the input contains no alphanumeric characters at
                all.

        Raises:
            ValueError: If ``mode`` is unknown or ``text`` is missing,
                empty, not a string, or over the length limit.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        return {"mode": mode, "result": self._convert(mode, clean_text)}

    # ------------------------------------------------------------------ #
    # Mode dispatch
    # ------------------------------------------------------------------ #

    @classmethod
    def _convert(cls, mode: str, text: str) -> str:
        """Dispatch to the implementation of one mode."""
        if mode in ("snake", "kebab", "camel", "pascal", "constant"):
            return cls._identifier(mode, cls._words(text))
        if mode == "title":
            return cls._title_case(text)
        if mode == "sentence":
            return cls._sentence_case(text)
        if mode == "slug":
            return cls._slug(text)
        return text.upper() if mode == "upper" else text.lower()

    @staticmethod
    def _identifier(mode: str, words: list[str]) -> str:
        """Join already-tokenized words into one identifier style."""
        if mode == "snake":
            return "_".join(word.lower() for word in words)
        if mode == "kebab":
            return "-".join(word.lower() for word in words)
        if mode == "constant":
            return "_".join(word.upper() for word in words)
        if mode == "camel":
            if not words:
                return ""
            return words[0].lower() + "".join(word.capitalize() for word in words[1:])
        return "".join(word.capitalize() for word in words)  # pascal

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"case_converter_tool: {message}")

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

    # ------------------------------------------------------------------ #
    # Word tokenization for the identifier modes
    # ------------------------------------------------------------------ #

    @classmethod
    def _words(cls, text: str) -> list[str]:
        """Split text into words for the identifier modes.

        The text is cut at every run of non-alphanumeric characters
        (whitespace, underscores, dashes, punctuation), and each
        remaining run is additionally split at camel-hump boundaries:
        a lowercase-to-uppercase transition, and the boundary between
        an uppercase run and the last uppercase letter that starts a
        cased word (acronym handling, ``HTTPServer`` → ``HTTP`` +
        ``Server``). Digits never create a boundary, so ``model2vec``
        and ``sha256Sum`` stay single words.
        """
        words: list[str] = []
        for run in _ALNUM_RUN.findall(text):
            marked = _LOWER_TO_UPPER.sub(r"\1" + _HUMP + r"\2", run)
            marked = _ACRONYM_TO_WORD.sub(r"\1" + _HUMP + r"\2", marked)
            words.extend(part for part in marked.split(_HUMP) if part)
        return words

    # ------------------------------------------------------------------ #
    # Prose case modes
    # ------------------------------------------------------------------ #

    @classmethod
    def _title_case(cls, text: str) -> str:
        """Title Case with the small-word rule.

        Whitespace and punctuation are preserved exactly. Words found
        in the small-word set (compared case-insensitively) stay
        lowercase unless they are the first or the last word of the
        text; every other word is capitalized (first character upper,
        rest lower).
        """
        tokens = list(_TITLE_TOKENS.findall(text))
        word_positions = [i for i, token in enumerate(tokens) if token[0]]
        for index in word_positions:
            word = tokens[index][0]
            is_first = index == word_positions[0]
            is_last = index == word_positions[-1]
            if word.lower() in _SMALL_WORDS and not (is_first or is_last):
                tokens[index] = (word.lower(), tokens[index][1])
            else:
                tokens[index] = (word.capitalize(), tokens[index][1])
        return "".join(word if word else separator for word, separator in tokens)

    @staticmethod
    def _sentence_case(text: str) -> str:
        """Sentence case: first cased character upper, the rest lower.

        Caseless characters (digits, CJK, punctuation, whitespace) are
        untouched; the leading run of caseless characters simply passes
        through before the first cased character is uppercased.
        """
        for index, char in enumerate(text):
            if char != char.lower() or char != char.upper():
                return text[:index] + char.upper() + text[index + 1 :].lower()
        return text

    # ------------------------------------------------------------------ #
    # slug mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _slug(text: str) -> str:
        """URL slug: NFKD fold, strip diacritics, lowercase, dash-join.

        ``José`` becomes ``jose``: NFKD decomposes the ``é`` into ``e``
        plus a combining acute accent, the combining mark (a non-spacing
        character) is dropped, and only then is the text lowercased and
        every non-alphanumeric run collapsed into a single ``-``.
        """
        folded = unicodedata.normalize("NFKD", text)
        stripped = "".join(
            ch
            for ch in folded
            if not unicodedata.combining(ch)
        )
        dashed = "".join(
            ch if ch.isalnum() else "-" for ch in stripped.lower()
        )
        return re.sub(r"-+", "-", dashed).strip("-")
