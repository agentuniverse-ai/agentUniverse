#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: acronym_generator_tool.py

"""Acronym generation from phrases, variants and system names.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency helper agents can
call when they need a short form for a phrase: build the acronym of
"HyperText Markup Language" (HTML), enumerate every reasonable short
form of a longer phrase, or derive a compact system name from a
multi-word identifier.  It is the inverse of the
``AcronymExpanderTool`` (which resolves acronyms back to their
expansions) and is built purely on the standard library.

Three modes are supported:

* ``generate`` — build one acronym from ``phrase`` under the given
  options and report which words were used and which were skipped.
* ``variants`` — enumerate all reasonable acronyms of ``phrase``
  (the full form, the stopword-free form and the first-N-words
  forms) as a labelled list.
* ``from_name`` — derive an acronym suitable for a system name from
  a multi-word ``name``: stopwords are skipped, the result is at
  most 4 letters long, and a documented consonant fallback covers
  names whose initials are too sparse.

Token and letter rules (documented behaviour)
---------------------------------------------

Words are obtained by splitting ``phrase`` on whitespace and
stripping edge punctuation (ASCII punctuation plus typographic
quotes and dashes) from each token.  A token with no alphabetic
character at all ("2024", "--") is skipped with reason
``no_letters``.

Each word is then split into *parts* and every part contributes its
first letter:

* Hyphen rule — a hyphenated word contributes the first letter of
  EACH part: "Cross-Origin Resource Sharing" → ``CORS``.
* Compound rule — a camelCase compound contributes the first letter
  of each hump: "HyperText" → ``H``+``T``, "JavaScript" →
  ``J``+``S`` (so "HyperText Markup Language" → ``HTML`` and
  "JavaScript Object Notation" → ``JSON``).  An all-caps token such
  as ``NASA`` or ``JPEG`` has no hump boundary and contributes only
  its first letter.
* The initial of a part is its first alphabetic character, so "3M"
  contributes ``M``.
* CJK rule — for CJK text (Han, Hiragana, Katakana, Hangul) every
  character is an initial, because Chinese/Japanese short forms are
  built from characters, not first letters: "人工智能" →
  "人工智能" (the full word), "AI驱动" → ``A`` + "驱动".  A Latin
  run inside a mixed part still contributes only its first letter.

Stopwords — when ``skip_stopwords`` is true (the default) a small
built-in English stopword list (``a an and as at but by for from in
into of on onto or the to with``) is matched case-insensitively
against each PART, so hyphen compounds like "state-of-the-art" also
lose their "of"/"the" parts ("State-of-the-art systems" →
``SAS``).  Single-letter words are ordinary words: ``I`` is never a
stopword ("I Robot" → ``IR``) while ``A`` is, so "A Team" → ``T``
with the default options but ``AT`` with ``skip_stopwords=False``.
A phrase made entirely of stopwords yields a structured empty
result (empty acronym, empty ``words_used`` and every word listed
in ``words_skipped``).

``min_word_length`` (default 0) drops whole words shorter than the
given length (length measured on the stripped word).

``max_words`` caps how many eligible words contribute letters.  The
cap itself is capped at 10 — a larger ``max_words`` is clamped to
10 with a note — and words beyond the cap are skipped with reason
``max_words`` plus an explanatory note.  Stopwords never count
towards the cap.  The default (``None``) means "no explicit limit",
i.e. the hard cap of 10.

Styles — ``upper`` (default) upper-cases every initial
("Content management system" → ``CMS``), ``keep_case`` preserves
each word's case ("Content management system" → ``Cms``,
"JavaScript Object Notation" → ``JSON``) and ``first_letters_lower``
lower-cases every initial ("Content management system" → ``cms``).

Variants semantics (documented behaviour)
-----------------------------------------

``variants`` returns the full acronym (all words), the
``no_stopwords`` acronym and one ``first_{n}_words`` acronym for
every n from 2 up to the number of content words, each as
``{"label", "acronym", "word_count"}``.  Exact duplicate acronym
values are collapsed (the first label wins), so a phrase whose
content words are all used, e.g. "Portable Network Graphics", has a
single ``full``/``no_stopwords`` entry rather than repeated ones.

from_name semantics (documented behaviour)
------------------------------------------

``from_name`` collects the initials of the stopword-free words of
``name``, upper-cased and truncated to at most 4 letters
("customer relationship management" → ``CRM``, "HyperText Transfer
Protocol" → ``HTTP``).  When fewer than 2 letters result (a
single-word name such as "Blockchain" gives only ``B``) the tool
falls back to the consonants of the FIRST content word ("y" counts
as a consonant; only ``aeiou`` are vowels), truncated to 4:
"Blockchain" → ``BLCC``, "System" → ``SYST``.  This is a heuristic
and is flagged as such in the result (``fallback_used`` /
``method``).  When neither path yields 2 letters the result is an
empty acronym with ``method`` "none" and an explanatory note.

Input validation is strict and happens before any computation:
unknown mode, missing/empty/non-string/oversized ``phrase`` or
``name``, a phrase with more than 1,000 tokens, non-boolean
``skip_stopwords``, non-integer or negative ``min_word_length``,
non-integer or non-positive ``max_words`` and an unknown ``style``
all raise a ``ValueError``, mirroring the other common tools.
"""

import re
import string
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Edge punctuation stripped from every token: ASCII punctuation plus
# typographic quotes, guillemets, the ellipsis and the dash family.
_STRIP_CHARS = string.punctuation + (
    "\u2010\u2011\u2012\u2013\u2014\u2015"  # dashes
    "\u2018\u2019\u201c\u201d"  # curly quotes
    "\u00ab\u00bb\u2039\u203a"  # guillemets
    "\u2026"  # ellipsis
)

# Hyphen and dash characters that split a word into parts.
_DASH_RE = re.compile(r"[-\u2010\u2011\u2012\u2013\u2014\u2015]")

# camelCase hump boundaries: lower/digit -> Upper, and UPPER -> Upper+lower
# (the "XMLHttpRequest" pattern).  All-caps runs ("NASA") stay whole.
_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

# Han, Hiragana, Katakana and Hangul syllables — the scripts whose
# short forms are built from characters rather than first letters.
_CJK_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7a3]"
)

# The small built-in English stopword list (matched per part,
# case-insensitively, exact match only — "without" is NOT "with").
_STOPWORDS: frozenset = frozenset(
    (
        "a", "an", "and", "as", "at", "but", "by", "for", "from",
        "in", "into", "of", "on", "onto", "or", "the", "to", "with",
    )
)

# Vowels for the from_name consonant fallback — "y" is a consonant.
_VOWELS = frozenset("aeiou")

# Hard input limits (mirrored as pydantic attributes on the class).
_MAX_PHRASE_CHARS = 10_000
_MAX_TOKENS = 1_000
_MAX_WORDS_CAP = 10
_MAX_NAME_LETTERS = 4


class AcronymGeneratorTool(Tool):
    """Acronym generation from phrases, variants and system names.

    Attributes:
        max_phrase_chars (int): Upper bound on the ``phrase`` and
            ``name`` input length; longer inputs are rejected.
        max_tokens (int): Upper bound on the number of whitespace
            tokens accepted in one phrase.
        max_words_cap (int): Hard cap on ``max_words``; larger
            values are clamped down to it.
        max_name_letters (int): Maximum length of a ``from_name``
            acronym.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "acronym_generator_tool"
    description: str = (
        "Acronym generator tool — pure Python stdlib, no network "
        "required. Build an acronym from a phrase with stopword "
        "skipping, length and word-count options and three letter "
        "styles (mode='generate', 'HyperText Markup Language' -> "
        "HTML), enumerate all reasonable acronym variants of a "
        "phrase as a labelled list (mode='variants'), or derive a "
        "compact system-name acronym from a multi-word name with a "
        "documented consonant fallback (mode='from_name')."
    )

    MODES: ClassVar[tuple] = ("generate", "variants", "from_name")
    STYLES: ClassVar[tuple] = ("upper", "keep_case", "first_letters_lower")

    max_phrase_chars: int = 10_000
    max_tokens: int = 1_000
    max_words_cap: int = 10
    max_name_letters: int = 4

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        phrase: Any = None,
        skip_stopwords: bool = True,
        min_word_length: int = 0,
        max_words: Any = None,
        style: str = "upper",
        name: Any = None,
    ) -> dict[str, Any]:
        """Run one acronym generation operation.

        Args:
            mode (str): One of ``generate`` / ``variants`` /
                ``from_name``.
            phrase (str): The source phrase; required for the
                ``generate`` and ``variants`` modes.
            skip_stopwords (bool): Skip the built-in English
                stopword parts (generate mode, default True).
            min_word_length (int): Drop words shorter than this
                length (generate mode, default 0).
            max_words (int | None): Cap on the number of eligible
                words that contribute letters; at most 10, larger
                values are clamped with a note (generate mode,
                default None = the hard cap of 10).
            style (str): Letter style — ``upper`` (default),
                ``keep_case`` or ``first_letters_lower``.
            name (str): The multi-word name to shorten; required
                for the ``from_name`` mode.

        Returns:
            Dict[str, Any]: The operation result (a ``result`` key
                plus the call context) — see the mode docstrings
                for the exact payload shapes.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if style not in self.STYLES:
            self._invalid(
                f"style must be one of: {', '.join(self.STYLES)} "
                f"(got {style!r})"
            )
        if mode == "from_name":
            return self._run_from_name(self._validate_phrase(name, "name"))
        words = self._validate_phrase(phrase, "phrase")
        if mode == "generate":
            return self._run_generate(
                words,
                skip_stopwords=skip_stopwords,
                min_word_length=min_word_length,
                max_words=max_words,
                style=style,
            )
        return self._run_variants(words, style=style)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"acronym_generator_tool: {message}")

    @classmethod
    def _validate_phrase(cls, value: Any, label: str) -> list[str]:
        """Validate ``phrase``/``name`` and return the raw tokens.

        Returns the whitespace-split tokens with edge punctuation
        still attached (stripping happens during processing so that
        the skip reports can echo the cleaned word).
        """
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be a non-empty string (got {value!r})")
        if not value.strip():
            cls._invalid(f"{label} must be a non-empty string (got {value!r})")
        if len(value) > _MAX_PHRASE_CHARS:
            cls._invalid(
                f"{label} exceeds the {_MAX_PHRASE_CHARS:,}-character limit "
                f"(got {len(value):,} characters)"
            )
        tokens = value.split()
        if len(tokens) > _MAX_TOKENS:
            cls._invalid(
                f"{label} exceeds the {_MAX_TOKENS:,}-token limit "
                f"(got {len(tokens):,} tokens)"
            )
        return tokens

    @classmethod
    def _validate_bool(cls, value: Any, label: str) -> bool:
        """Validate a boolean option."""
        if not isinstance(value, bool):
            cls._invalid(f"{label} must be a boolean (got {value!r})")
        return value

    @classmethod
    def _validate_int(cls, value: Any, label: str, minimum: int) -> int:
        """Validate an integer option (bools are rejected)."""
        if value is None or isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(f"{label} must be an integer (got {value!r})")
        if value < minimum:
            cls._invalid(f"{label} must be >= {minimum} (got {value!r})")
        return value

    # ------------------------------------------------------------------ #
    # Word / part / letter helpers (pure)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _clean_word(token: str) -> str:
        """Strip edge punctuation from one whitespace token."""
        return token.strip(_STRIP_CHARS)

    @staticmethod
    def _split_word_parts(word: str) -> list[str]:
        """Split a word into parts on dashes and camelCase humps."""
        parts: list[str] = []
        for segment in _DASH_RE.split(word):
            parts.extend(part for part in _CAMEL_RE.split(segment) if part)
        return parts

    @staticmethod
    def _part_letters(part: str) -> list[str]:
        """Return the initial(s) contributed by one word part.

        CJK characters each contribute themselves; every non-CJK
        run contributes its first alphabetic character.
        """
        letters: list[str] = []
        buffer: list[str] = []

        def flush() -> None:
            for char in buffer:
                if char.isalpha():
                    letters.append(char)
                    break

        for char in part:
            if _CJK_RE.match(char):
                flush()
                buffer = []
                letters.append(char)
            else:
                buffer.append(char)
        flush()
        return letters

    @staticmethod
    def _apply_style(letters: list[str], style: str) -> str:
        """Join the collected initials under one letter style."""
        if style == "keep_case":
            return "".join(letters)
        if style == "first_letters_lower":
            return "".join(letter.lower() for letter in letters)
        return "".join(letter.upper() for letter in letters)

    @classmethod
    def _word_letters(
        cls, word: str, skip_stopwords: bool
    ) -> list[str]:
        """Letters a cleaned word contributes (stopwords applied per part)."""
        letters: list[str] = []
        for part in cls._split_word_parts(word):
            if skip_stopwords and part.lower() in _STOPWORDS:
                continue
            letters.extend(cls._part_letters(part))
        return letters

    # ------------------------------------------------------------------ #
    # generate mode
    # ------------------------------------------------------------------ #

    def _run_generate(
        self,
        tokens: list[str],
        skip_stopwords: Any,
        min_word_length: Any,
        max_words: Any,
        style: str,
    ) -> dict[str, Any]:
        """Build one acronym from the phrase under the options."""
        skip = self._validate_bool(skip_stopwords, "skip_stopwords")
        min_len = self._validate_int(min_word_length, "min_word_length", 0)
        notes: list[str] = []
        effective_cap = _MAX_WORDS_CAP
        if max_words is not None:
            requested = self._validate_int(max_words, "max_words", 1)
            effective_cap = min(requested, _MAX_WORDS_CAP)
            if requested > _MAX_WORDS_CAP:
                notes.append(
                    f"max_words={requested} exceeds the "
                    f"{_MAX_WORDS_CAP}-word cap; using {_MAX_WORDS_CAP}"
                )

        letters: list[str] = []
        words_used: list[str] = []
        words_skipped: list[dict[str, str]] = []
        eligible = 0
        for token in tokens:
            word = self._clean_word(token)
            if not word or not any(char.isalpha() for char in word):
                words_skipped.append(
                    {"word": word or token, "reason": "no_letters"}
                )
                continue
            if len(word) < min_len:
                words_skipped.append(
                    {"word": word, "reason": "min_word_length"}
                )
                continue
            word_letters = self._word_letters(word, skip)
            if not word_letters:
                words_skipped.append({"word": word, "reason": "stopword"})
                continue
            if eligible >= effective_cap:
                words_skipped.append({"word": word, "reason": "max_words"})
                continue
            eligible += 1
            letters.extend(word_letters)
            words_used.append(word)

        beyond_cap = sum(
            1 for entry in words_skipped if entry["reason"] == "max_words"
        )
        if beyond_cap:
            notes.append(
                f"{beyond_cap} word(s) beyond the {effective_cap}-word cap "
                "were ignored"
            )
        acronym = self._apply_style(letters, style)
        if not acronym:
            notes.append(
                "no words contributed letters — the acronym is empty"
            )
        return {
            "mode": "generate",
            "result": acronym,
            "acronym": acronym,
            "letters": letters,
            "words_used": words_used,
            "words_skipped": words_skipped,
            "word_count": len(words_used),
            "options": {
                "skip_stopwords": skip,
                "min_word_length": min_len,
                "max_words": effective_cap,
                "style": style,
            },
            "notes": notes,
        }

    # ------------------------------------------------------------------ #
    # variants mode
    # ------------------------------------------------------------------ #

    def _run_variants(
        self, tokens: list[str], style: str
    ) -> dict[str, Any]:
        """Enumerate all reasonable acronyms of the phrase."""
        all_words: list[str] = []
        content_letters: list[list[str]] = []
        for token in tokens:
            word = self._clean_word(token)
            if not word or not any(char.isalpha() for char in word):
                continue
            all_words.append(word)
            word_letters = self._word_letters(word, True)
            if word_letters:
                content_letters.append(word_letters)

        variants: list[dict[str, Any]] = []
        seen: set[str] = set()

        def emit(label: str, letters: list[str], count: int) -> None:
            acronym = self._apply_style(letters, style)
            if acronym in seen:
                return
            seen.add(acronym)
            variants.append(
                {"label": label, "acronym": acronym, "word_count": count}
            )

        emit(
            "full",
            [
                letter
                for word in all_words
                for letter in self._word_letters(word, False)
            ],
            len(all_words),
        )
        emit(
            "no_stopwords",
            [letter for wl in content_letters for letter in wl],
            len(content_letters),
        )
        for n in range(2, len(content_letters) + 1):
            emit(
                f"first_{n}_words",
                [letter for wl in content_letters[:n] for letter in wl],
                n,
            )
        return {
            "mode": "variants",
            "result": variants,
            "variant_count": len(variants),
            "word_count": len(all_words),
            "content_word_count": len(content_letters),
            "style": style,
        }

    # ------------------------------------------------------------------ #
    # from_name mode
    # ------------------------------------------------------------------ #

    def _run_from_name(self, tokens: list[str]) -> dict[str, Any]:
        """Derive a compact system-name acronym from a name."""
        notes: list[str] = []
        content_words: list[str] = []
        letters: list[str] = []
        for token in tokens:
            word = self._clean_word(token)
            if not word or not any(char.isalpha() for char in word):
                continue
            word_letters = self._word_letters(word, True)
            if not word_letters:
                continue
            content_words.append(word)
            letters.extend(word_letters)

        acronym = ""
        method = "none"
        used_letters: list[str] = []
        if len(letters) >= 2:
            used_letters = letters[: _MAX_NAME_LETTERS]
            acronym = "".join(letter.upper() for letter in used_letters)
            method = "initials"
        elif content_words:
            first = content_words[0]
            consonants = [
                char.upper()
                for char in first
                if char.isalpha() and char.lower() not in _VOWELS
            ]
            if len(consonants) >= 2:
                used_letters = consonants[: _MAX_NAME_LETTERS]
                acronym = "".join(used_letters)
                method = "consonant_fallback"
                notes.append(
                    f"initials produced fewer than 2 letters; fell back to "
                    f"the consonants of the first content word {first!r}"
                )
        if method == "none":
            notes.append(
                "neither the initials nor the consonant fallback produced "
                "at least 2 letters"
            )
        return {
            "mode": "from_name",
            "result": acronym,
            "acronym": acronym,
            "method": method,
            "fallback_used": method == "consonant_fallback",
            "letters": used_letters,
            "name_words": content_words,
            "notes": notes,
        }
