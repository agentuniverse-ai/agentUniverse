#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: phonetic_code_tool.py

"""Phonetic coding tool (Soundex + simplified NYSIIS) built on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency phonetic encoder
agents can call for fuzzy name matching: deduplicating customer lists,
matching entity mentions that are spelled differently but pronounced
alike, or pre-clustering names before an exact-match pass.

Phonetic equivalence is an orthogonal axis to string similarity: the
existing TextDistanceTool measures edit distance (how many characters
differ), while this tool measures *how alike two names sound* —
``Robert`` and ``Rupert`` are far apart in edit distance yet share the
Soundex code ``R163``.

Four modes are supported:

* ``soundex`` — the classic American Soundex algorithm (NARA
  publication 55-4, the 4-character ``letter + 3 digits`` form) with
  the standard rules implemented exactly:

  - letter codes: ``B F P V`` → 1, ``C G J K Q S X Z`` → 2,
    ``D T`` → 3, ``L`` → 4, ``M N`` → 5, ``R`` → 6;
    ``A E I O U Y`` are never coded;
  - two adjacent letters with the same code are coded once (this also
    applies when the *first* letter of the word shares its code with
    the second letter, e.g. ``Pfister`` → ``P236``, not ``P123``);
  - the H/W-bridge rule: two letters with the same code separated by
    ``H`` or ``W`` are coded once (e.g. ``Ashcraft`` → ``A261``);
  - the vowel-split rule: two letters with the same code separated by
    a vowel (``A E I O U Y``) are coded twice (e.g. ``Tymczak`` →
    ``T522``);
  - the first letter is retained as-is; the code is zero-padded /
    truncated to exactly four characters (``Lee`` → ``L000``).

* ``nysiis`` — a *simplified* NYSIIS (New York State Identification
  and Intelligence System) following the verifiable core of the 1970
  algorithm. The exact ruleset implemented here, in order:

  1. Prefix rules — the first matching rule (longest first) is
     applied once to the uppercased word:
     ``MAC`` → ``MCC``, ``KN`` → ``NN``, ``SCH`` → ``SS``,
     ``PH`` → ``FF``, ``PF`` → ``FF``, ``K`` → ``N``.
  2. Character pass — the first character is kept unchanged; the
     remaining characters are scanned left to right, applying the
     first matching rule at each position (``PH`` as a pair, then
     singles): ``PH`` → ``FF``, ``Q`` → ``G``, ``Z`` → ``S``,
     ``J`` → ``S``, ``M`` → ``N``, ``K`` → ``C``,
     ``A E I O U`` → ``A``, ``H`` → dropped (``H`` survives only
     inside ``PH``); every other letter passes through unchanged
     (``Y`` counts as a consonant and is kept).
  3. Suffix rules — the first matching rule (longest first) is
     applied once to the end of the key: ``AY`` → ``Y``,
     ``AS`` → ``A``, ``AH`` → ``A``; otherwise a trailing ``S`` is
     dropped.
  4. Collapsing — runs of the same character collapse to a single
     character (``NN`` → ``N``).

  This deliberately omits rules of the full 1970 specification that
  are inconsistently documented across implementations (the ``H``
  context rule, ``EV`` → ``AF``, ``W`` after a vowel, the trailing
  ``EE`` / ``IE`` / ``DT`` / ``NT`` family). Example results of the
  documented ruleset: ``Tymczak`` → ``TYNCSAC``, ``Smith`` →
  ``SNAT``, ``Pfister`` → ``FASTAR``, ``Johnson`` → ``JANSAN``.

* ``compare`` — compares two single words and reports whether they
  share each code, how many of the four Soundex positions differ
  (``soundex_distance``, 0–4), and the Levenshtein edit distance
  between the two Soundex codes (``edit_distance``) and between the
  two NYSIIS keys (``nysiis_edit_distance``).

* ``batch_group`` — groups a list of words by their Soundex code
  (``{code: [words in input order]}``), the building block of
  name-dedup workflows.

Input validation is strict and happens before any computation: words
must be non-empty ASCII alphabetic strings (``[A-Za-z]+`` — split
multi-word input on whitespace yourself and pass each name part
separately; hyphens, apostrophes and digits are rejected), word lists
must be non-empty Python lists of such strings, and per-call limits
are enforced. Every violation raises a ``ValueError``, mirroring the
other common tools. All results are deterministic.
"""

import re
from typing import Any, ClassVar, Dict, List

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Full-match guard for a single word: ASCII letters only.
_ALPHA_WORD = re.compile(r"\A[A-Za-z]+\Z")

# Standard American Soundex letter -> digit table.
_SOUNDEX_CODES: Dict[str, str] = {}
for _chars, _code in (
    ("BFPV", "1"),
    ("CGJKQSXZ", "2"),
    ("DT", "3"),
    ("L", "4"),
    ("MN", "5"),
    ("R", "6"),
):
    for _char in _chars:
        _SOUNDEX_CODES[_char] = _code

# Letters that act as separators in Soundex (vowel-like: reset the
# "previous code" so a repeated code after them is coded again).
_SOUNDEX_SEPARATORS = frozenset("AEIOUY")


class PhoneticCodeTool(Tool):
    """Phonetic coding tool — Soundex and simplified NYSIIS, pure stdlib.

    Attributes:
        max_word_chars (int): Upper bound on a single word's length.
        max_words_per_text (int): Upper bound on the word count accepted
            by the ``soundex`` / ``nysiis`` modes.
        max_batch_words (int): Upper bound on the word count accepted
            by the ``batch_group`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "phonetic_code_tool"
    description: str = (
        "Phonetic code tool — pure Python stdlib, no network required. "
        "Classic American Soundex codes for one or more words "
        "(mode='soundex', e.g. Robert->R163), simplified NYSIIS keys "
        "(mode='nysiis', e.g. Smith->SNAT), a two-word comparison with "
        "same-code flags and code distances (mode='compare'), and "
        "Soundex-based grouping of a word list for name dedup "
        "(mode='batch_group'). Use it for fuzzy name matching: names "
        "that sound alike share codes even when spelled differently."
    )

    MODES: ClassVar[tuple] = ("soundex", "nysiis", "compare", "batch_group")

    max_word_chars: int = 100
    max_words_per_text: int = 100
    max_batch_words: int = 1_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        word1: Any = None,
        word2: Any = None,
        words: Any = None,
    ) -> Dict[str, Any]:
        """Run one phonetic coding operation.

        Args:
            mode (str): One of ``soundex`` / ``nysiis`` / ``compare`` /
                ``batch_group``.
            text (str): The word(s) to encode — a single word or several
                whitespace-separated words, each fully alphabetic.
                Required for the ``soundex`` and ``nysiis`` modes.
            word1 (str): The first word for the ``compare`` mode (a
                single alphabetic word).
            word2 (str): The second word for the ``compare`` mode (a
                single alphabetic word).
            words (List[str]): The word list for the ``batch_group``
                mode — a non-empty list of alphabetic words.

        Returns:
            Dict[str, Any]: The operation result. ``soundex`` /
            ``nysiis`` return ``result`` as a code string for a single
            word and a list of code strings for several words;
            ``compare`` returns both codes plus ``same_soundex``,
            ``same_nysiis``, ``soundex_distance`` (0-4 Soundex
            positions that differ), ``edit_distance`` (Levenshtein
            distance between the two Soundex codes) and
            ``nysiis_edit_distance``; ``batch_group`` returns
            ``groups`` (Soundex code -> words in input order) plus
            word / group counts.

        Raises:
            ValueError: If any parameter is malformed (unknown mode,
                missing or non-alphabetic words, wrong types, empty
                lists, words or lists over the size limits).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "compare":
            return self._run_compare(word1, word2)
        if mode == "batch_group":
            return self._run_batch_group(words)
        clean_words = self._validate_text_words(text)
        if mode == "soundex":
            codes = [self.soundex(word) for word in clean_words]
        else:
            codes = [self.nysiis(word) for word in clean_words]
        result: Any = codes[0] if len(codes) == 1 else codes
        return {
            "mode": mode,
            "result": result,
            "codes": codes,
        }

    # ------------------------------------------------------------------ #
    # Public algorithms (plain functions over validated words)
    # ------------------------------------------------------------------ #

    @staticmethod
    def soundex(word: str) -> str:
        """Return the classic 4-character American Soundex code.

        Implements the standard NARA rules: the first letter is kept;
        ``B F P V`` -> 1, ``C G J K Q S X Z`` -> 2, ``D T`` -> 3,
        ``L`` -> 4, ``M N`` -> 5, ``R`` -> 6; adjacent same-code
        letters (including across an ``H`` / ``W`` bridge, and
        including the first letter versus the second letter) are coded
        once; a vowel (``A E I O U Y``) between same-code letters lets
        the second one be coded again; the result is zero-padded or
        truncated to letter + three digits.
        """
        word = word.upper()
        first = word[0]
        digits: List[str] = []
        prev = _SOUNDEX_CODES.get(first)
        for char in word[1:]:
            if char in ("H", "W"):
                # H/W bridge: skipped without resetting the previous
                # code, so S-H-C style pairs still collapse.
                continue
            code = _SOUNDEX_CODES.get(char)
            if code is None:
                # Vowel separator (A E I O U Y): resets the previous
                # code so a following same-code letter is coded again.
                prev = None
                continue
            if code != prev:
                digits.append(code)
            prev = code
        return first + ("".join(digits) + "000")[:3]

    @staticmethod
    def nysiis(word: str) -> str:
        """Return the simplified NYSIIS key for ``word``.

        Implements exactly the documented ruleset: prefix rules
        (``MAC``->``MCC``, ``KN``->``NN``, ``SCH``->``SS``,
        ``PH``->``FF``, ``PF``->``FF``, ``K``->``N``), a character
        pass that keeps the first character and maps ``PH``->``FF``,
        ``Q``->``G``, ``Z``/``J``->``S``, ``M``->``N``, ``K``->``C``,
        vowels->``A`` and drops ``H``, suffix rules (``AY``->``Y``,
        ``AS``/``AH``->``A``, trailing ``S`` dropped), then collapsing
        of repeated characters.
        """
        word = word.upper()
        for prefix, replacement in (
            ("MAC", "MCC"),
            ("KN", "NN"),
            ("SCH", "SS"),
            ("PH", "FF"),
            ("PF", "FF"),
            ("K", "N"),
        ):
            if word.startswith(prefix):
                word = replacement + word[len(prefix):]
                break

        singles = {
            "Q": "G", "Z": "S", "J": "S", "M": "N", "K": "C",
            "A": "A", "E": "A", "I": "A", "O": "A", "U": "A", "H": "",
        }
        out = [word[0]]
        index = 1
        while index < len(word):
            if word[index : index + 2] == "PH":
                out.append("FF")
                index += 2
                continue
            char = word[index]
            out.append(singles.get(char, char))
            index += 1
        key = "".join(out)

        for suffix, replacement in (("AY", "Y"), ("AS", "A"), ("AH", "A")):
            if key.endswith(suffix):
                key = key[: -len(suffix)] + replacement
                break
        else:
            if key.endswith("S"):
                key = key[:-1]

        collapsed: List[str] = []
        for char in key:
            if not collapsed or collapsed[-1] != char:
                collapsed.append(char)
        return "".join(collapsed)

    # ------------------------------------------------------------------ #
    # compare / batch_group modes
    # ------------------------------------------------------------------ #

    def _run_compare(self, word1: Any, word2: Any) -> Dict[str, Any]:
        """Compare two single words across both phonetic algorithms."""
        clean_word1 = self._validate_single_word("word1", word1)
        clean_word2 = self._validate_single_word("word2", word2)
        soundex1 = self.soundex(clean_word1)
        soundex2 = self.soundex(clean_word2)
        nysiis1 = self.nysiis(clean_word1)
        nysiis2 = self.nysiis(clean_word2)
        # Positions among the four code characters that differ (0-4).
        differing = sum(1 for a, b in zip(soundex1, soundex2) if a != b)
        return {
            "mode": "compare",
            "word1": clean_word1,
            "word2": clean_word2,
            "soundex1": soundex1,
            "soundex2": soundex2,
            "nysiis1": nysiis1,
            "nysiis2": nysiis2,
            "same_soundex": soundex1 == soundex2,
            "same_nysiis": nysiis1 == nysiis2,
            "soundex_distance": differing,
            "edit_distance": self._levenshtein(soundex1, soundex2),
            "nysiis_edit_distance": self._levenshtein(nysiis1, nysiis2),
        }

    def _run_batch_group(self, words: Any) -> Dict[str, Any]:
        """Group a validated word list by Soundex code."""
        clean_words = self._validate_word_list(words)
        groups: Dict[str, List[str]] = {}
        for word in clean_words:
            groups.setdefault(self.soundex(word), []).append(word)
        return {
            "mode": "batch_group",
            "groups": groups,
            "word_count": len(clean_words),
            "group_count": len(groups),
        }

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"phonetic_code_tool: {message}")

    @classmethod
    def _validate_single_word(cls, label: str, word: Any) -> str:
        """Validate one strictly single alphabetic word."""
        if word is None or isinstance(word, bool) or not isinstance(word, str):
            cls._invalid(f"{label} must be a non-empty alphabetic word (got {word!r})")
        if not _ALPHA_WORD.match(word):
            cls._invalid(
                f"{label} must contain only ASCII letters A-Z / a-z with no "
                f"spaces, digits, hyphens or apostrophes (got {word[:64]!r})"
            )
        if len(word) > 100:
            cls._invalid(
                f"{label} exceeds the {100}-character limit (got {len(word)} characters)"
            )
        return word

    @classmethod
    def _validate_text_words(cls, text: Any) -> List[str]:
        """Validate the ``text`` input of the soundex / nysiis modes."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty alphabetic word or words (got {text!r})")
        words = text.split()
        if not words:
            cls._invalid("text must contain at least one word (got whitespace only)")
        if len(words) > 100:
            cls._invalid(
                f"text exceeds the {100}-word limit (got {len(words)} words)"
            )
        for word in words:
            if not _ALPHA_WORD.match(word):
                cls._invalid(
                    "every word in text must contain only ASCII letters A-Z / a-z "
                    f"with no digits, hyphens or apostrophes (got {word[:64]!r})"
                )
            if len(word) > 100:
                cls._invalid(
                    f"a word in text exceeds the {100}-character limit "
                    f"(got {len(word)} characters in {word[:64]!r})"
                )
        return words

    @classmethod
    def _validate_word_list(cls, words: Any) -> List[str]:
        """Validate the ``words`` list of the batch_group mode."""
        if words is None or isinstance(words, (bool, str)) or not isinstance(words, list):
            cls._invalid(f"words must be a non-empty list of alphabetic words (got {words!r})")
        if not words:
            cls._invalid("words must be a non-empty list of alphabetic words (got [])")
        if len(words) > 1_000:
            cls._invalid(
                f"words exceeds the {1_000:,}-entry limit (got {len(words):,} entries)"
            )
        for word in words:
            if word is None or isinstance(word, bool) or not isinstance(word, str):
                cls._invalid(f"every entry of words must be an alphabetic word (got {word!r})")
            if not _ALPHA_WORD.match(word):
                cls._invalid(
                    "every entry of words must contain only ASCII letters A-Z / a-z "
                    f"with no spaces, digits, hyphens or apostrophes (got {word[:64]!r})"
                )
            if len(word) > 100:
                cls._invalid(
                    f"an entry of words exceeds the {100}-character limit "
                    f"(got {len(word)} characters in {word[:64]!r})"
                )
        return list(words)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _levenshtein(left: str, right: str) -> int:
        """Plain Levenshtein edit distance between two code strings."""
        if left == right:
            return 0
        previous = list(range(len(right) + 1))
        for i, left_char in enumerate(left, start=1):
            current = [i]
            for j, right_char in enumerate(right, start=1):
                cost = 0 if left_char == right_char else 1
                current.append(
                    min(
                        previous[j] + 1,      # deletion
                        current[j - 1] + 1,   # insertion
                        previous[j - 1] + cost,  # substitution
                    )
                )
            previous = current
        return previous[-1]
