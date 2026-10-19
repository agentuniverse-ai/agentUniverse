#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: wordplay_tool.py

"""Wordplay utility tool (anagrams, palindromes, letter scores) built
purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency wordplay helper
agents can call for language checks and puzzle-style analysis.

The tool supports four modes:

* ``check`` — test one text (or a pair of texts) for the classic
  wordplay properties. ``check='is_palindrome'`` compares the text
  against itself: by default the letters-only reduction (Unicode
  ``casefold`` + every non-letter character stripped) is compared with
  its reverse, so ``"A man, a plan, a canal: Panama"`` and the CJK
  classic ``"上海自来水来自海上"`` are both palindromes; the optional
  ``strict`` flag instead compares the raw characters exactly, with no
  case folding and nothing stripped. ``check='is_anagram'`` compares
  two texts: the canonical verdict uses the letters-only multiset
  (case-insensitive, non-letters stripped), and the result also
  reports on which comparison basis (letters-only and/or raw
  characters) the anagram property holds, plus letter-count summaries
  and the letters whose counts differ. ``check='both'`` runs both
  checks. Palindrome checking works on any alphabetic script (CJK
  characters count as letters and are compared naturally); if a text
  has no letters at all after the strip (e.g. ``"!!!"``), a
  structured ``empty_after_strip`` error payload is returned instead
  of a meaningless verdict.
* ``anagrams_of`` — given one input word, generate every permutation
  of its letters and keep those that appear in a small built-in
  common-English word list, returning the matches other than the
  input word itself. The embedded list is a hand-curated *demo* list
  of 499 frequent English words (3-6 letters, chosen so that it
  contains dozens of classic anagram groups such as *listen / silent
  / enlist / tinsel / inlets*); it is intentionally small and is NOT
  a dictionary, so the tool reports the list size alongside the
  matches. To stay deterministic and cheap, the input is capped at
  ``MAX_ANAGRAM_INPUT`` (8) letters after the same letters-only
  reduction and the output is capped at ``MAX_ANAGRAM_RESULTS`` (50)
  alphabetically-sorted matches. This mode is English-only: the
  embedded list contains no non-English words, so non-Latin input
  simply yields no matches.
* ``palindrome_parts`` — find the longest palindromic substring of
  the letters-only reduction of the text (first occurrence on ties)
  and every distinct palindromic substring of length >= 3, capped at
  ``MAX_PALINDROMES`` (50) entries sorted by decreasing length then
  alphabetically, with a ``truncated`` flag when the cap hits. Works
  on CJK input naturally.
* ``letter_score`` — score a word with the standard English
  Scrabble tile values (a e i o u l n s t r = 1, d g = 2, b c m p =
  3, f h v w y = 4, k = 5, j x = 8, q z = 10). Only ASCII letters
  carry values; every other character (spaces, digits, punctuation,
  non-Latin letters) is reported in ``unscored`` counts, and a text
  with no ASCII letters at all returns a structured
  ``no_scoreable_letters`` error payload.

Everything is deterministic: no randomness anywhere (anagram
candidates come from itertools.permutations), so identical inputs
always produce identical outputs. Input validation is strict and
happens before any computation: malformed parameters (wrong types,
empty text, unknown mode / check value, a non-bool ``strict``, a
missing or malformed ``second_text``, text over ``max_text_chars``
characters, an ``anagrams_of`` input longer than 8 letters after the
reduction) raise a ``ValueError``, mirroring the other common tools.
Errors that depend on the *content being processed* — a text that
reduces to zero letters, or a letter_score text with nothing
scoreable — are returned as structured ``error`` payloads so an
agent can react without catching exceptions.
"""

import itertools
from collections import Counter
from typing import Any, ClassVar, Dict

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Standard English Scrabble tile values (1 point: e a i o u l n s t r,
# 2: d g, 3: b c m p, 4: f h v w y, 5: k, 8: j x, 10: q z).
SCRABBLE_VALUES: Dict[str, int] = {
    **{letter: 1 for letter in "aeioulnstr"},
    **{letter: 2 for letter in "dg"},
    **{letter: 3 for letter in "bcmp"},
    **{letter: 4 for letter in "fhvwy"},
    "k": 5,
    "j": 8,
    "x": 8,
    "q": 10,
    "z": 10,
}

# Hand-curated demo list of 499 common English words. It is
# deliberately small (a demo, not a dictionary) and biased towards
# classic anagram groups (listen/silent/enlist/tinsel/inlets,
# stone/tones/notes/onset, earth/heart, angel/angle/glean, ...) so the
# anagrams_of mode returns interesting results offline. English only.
_DEMO_WORDS: frozenset = frozenset("""
    able act agree air alert alter among and angel angle arm art
    ate back bag baker ball band bank bar base bat bath battle
    bear beat bed bee been begin being below best bird bit blue
    board boat body book born both bowl boy break brief broad bus
    busy buy came can car card care case cat center chain charm
    cheat china cider come course credit cried cup cut dark data date
    day deal dear deep desk diet direct dog done door down draw
    drop dry dusty eager ear early earth east easy eat egg elbow
    else end enlist even ever evil eye face fact fail fair fall
    far farm fast feed feel feet felt few fiber find fine fire
    fish five fly food foot for form former four fox free from
    full fun gain game gas gate gave get gift girl give glad
    glean goal god gold gone good grow grown gun had hair half
    hall hand hard hat hate have head heart heat held help her
    here hero high hill him hint his hold home hope host hot
    hour huge ice idea inlets into item job just keep key kind
    king knew know lake lamp land lane last late later law lay
    layer leak lean left leg less let lift like lime line lion
    lip list listen live load loan long look lose loss lot loud
    love low mail main make man mango many map march marine mark
    master may mean meat meet men mile milk mill mind mine miss
    mode mood moon more most move much must name near need net
    new news next nice night nine note notes now oil old once
    one only onset open ought our out over own pace pack page
    pain pair pale palm panel park part pass past path pay peak
    pen pet phase pie pig plan plane play plus poem pool port
    post pure push put quiet quite race rain ran rank rate read
    real recent red reform remain rescue rest rip road rock roof room
    root rule run sad safe said sail sale salt sand sat save
    saw say seal seat secure see seem seen send serve shape she
    sheet ship shop shot show side sign silent sing sit site six
    size skin sky slow soft sole son song soon sort source spot
    star state stay step stone stop stream study such sun sure tablet
    tail take tale talk tall task taste tax tea teach team tell
    ten test text than that the them then there these they thin
    thing this three throw tide time tinsel tired toe told tone tones
    tool top tough tower town toy trap tree tried trim trip true
    try turn two unit upon use user verse very view wait wake
    walk wall want warm warn was wash wave way weak wear web
    week well went were west wet what when who why wide wife
    wild win wind wing wise wish won word wore work worth wrong
    wrote yard year yes yet you zero
""".split())


class WordplayTool(Tool):
    """Wordplay tool — anagrams, palindromes and letter scores, pure stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` /
            ``second_text`` input length; longer inputs are rejected
            before any work (palindrome_parts runs an O(n^2) scan, so
            the bound is much tighter than text-heavy tools).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "wordplay_tool"
    description: str = (
        "Wordplay tool — anagram, palindrome and letter-score utilities, "
        "pure Python stdlib, no network required. Check whether one text "
        "is a palindrome (letters-only basis, or exact raw characters "
        "with strict=True) or whether two texts are anagrams "
        "(mode='check'), list anagram candidates of a word from a small "
        "built-in common-English demo word list (mode='anagrams_of'), "
        "find the longest palindromic substring plus all palindromic "
        "substrings of length >= 3 (mode='palindrome_parts'), and score "
        "a word with standard English Scrabble tile values "
        "(mode='letter_score')."
    )

    MODES: ClassVar[tuple] = (
        "check", "anagrams_of", "palindrome_parts", "letter_score",
    )
    CHECKS: ClassVar[tuple] = ("is_anagram", "is_palindrome", "both")
    MAX_ANAGRAM_INPUT: ClassVar[int] = 8
    MAX_ANAGRAM_RESULTS: ClassVar[int] = 50
    MAX_PALINDROMES: ClassVar[int] = 50
    MIN_PART_LENGTH: ClassVar[int] = 3

    max_text_chars: int = 2_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        second_text: Any = None,
        check: Any = None,
        strict: Any = None,
    ) -> Dict[str, Any]:
        """Run one wordplay operation.

        Args:
            mode (str): One of ``check`` / ``anagrams_of`` /
                ``palindrome_parts`` / ``letter_score``.
            text (str): The text to analyse. Required for every mode.
            second_text (str): ``check`` mode with anagram — the text
                to compare against (anagram checking is a two-text
                operation).
            check (str): ``check`` mode only — ``is_anagram``,
                ``is_palindrome`` or ``both``.
            strict (str): ``check`` mode palindrome only — when True
                the palindrome verdict compares the raw characters
                exactly (no case folding, nothing stripped); the
                default (False / None) uses the letters-only
                reduction.

        Returns:
            Dict[str, Any]: The operation result (verdict plus details
                and the call context) or a structured ``error`` payload
                for content-level failures (a text that reduces to
                zero letters, or nothing scoreable for
                ``letter_score``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "check":
            return self._run_check(clean_text, second_text, check, strict)
        if mode == "anagrams_of":
            return self._run_anagrams_of(clean_text)
        if mode == "palindrome_parts":
            return self._run_palindrome_parts(clean_text)
        return self._run_letter_score(clean_text)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"wordplay_tool: {message}")

    def _validate_text(self, text: Any) -> str:
        """Validate the ``text`` / ``second_text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            self._invalid("text must be a non-empty string (got '')")
        if len(text) > self.max_text_chars:
            self._invalid(
                f"text exceeds the {self.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @staticmethod
    def _letters(text: str) -> str:
        """Reduce a text to its letters: casefold, drop non-letters.

        Uses Unicode ``str.isalpha`` per character, so CJK ideographs
        (and any other alphabetic script) count as letters.
        """
        return "".join(ch for ch in text.casefold() if ch.isalpha())

    # ------------------------------------------------------------------ #
    # check mode
    # ------------------------------------------------------------------ #

    def _run_check(
        self, text: str, second_text: Any, check: Any, strict: Any
    ) -> Dict[str, Any]:
        """Dispatch the is_anagram / is_palindrome / both checks."""
        if check not in self.CHECKS:
            self._invalid(
                "check must be one of: "
                f"{', '.join(self.CHECKS)} (got {check!r})"
            )
        if strict is None:
            strict = False
        if not isinstance(strict, bool):
            self._invalid(f"strict must be a boolean or None (got {strict!r})")

        result: Dict[str, Any] = {"mode": "check", "check": check}
        if check in ("is_anagram", "both"):
            if second_text is None:
                self._invalid(
                    "second_text is required when check is 'is_anagram' "
                    f"or 'both' (got {second_text!r})"
                )
            clean_second = self._validate_text(second_text)
            result["anagram"] = self._check_anagram(text, clean_second)
        if check in ("is_palindrome", "both"):
            result["palindrome"] = self._check_palindrome(text, strict)
        return result

    def _check_anagram(self, text: str, second_text: str) -> Dict[str, Any]:
        """Compare two texts as anagrams on two bases."""
        context = {"text": text, "second_text": second_text}
        letters_a = self._letters(text)
        letters_b = self._letters(second_text)
        if not letters_a or not letters_b:
            return self._error_result(
                context,
                error_type="empty_after_strip",
                message=(
                    "anagram checking needs at least one letter on both "
                    "sides after casefolding and removing non-letters "
                    f"(text reduces to {letters_a!r}, second_text to "
                    f"{letters_b!r})"
                ),
            )
        counts_a = Counter(letters_a)
        counts_b = Counter(letters_b)
        letters_only = counts_a == counts_b
        raw = sorted(text.casefold()) == sorted(second_text.casefold())
        differing = {
            letter: [counts_a.get(letter, 0), counts_b.get(letter, 0)]
            for letter in sorted(counts_a.keys() | counts_b.keys())
            if counts_a.get(letter, 0) != counts_b.get(letter, 0)
        }
        if letters_only and raw:
            verdict = "anagrams on both the letters-only and raw bases"
        elif letters_only:
            verdict = "anagrams on the letters-only basis (raw characters differ)"
        else:
            verdict = "not anagrams"
        return {
            **context,
            "is_anagram": letters_only,
            "basis": {"letters_only": letters_only, "raw": raw},
            "verdict": verdict,
            "details": {
                "text_letters": letters_a,
                "second_text_letters": letters_b,
                "letter_counts": {
                    "text": dict(sorted(counts_a.items())),
                    "second_text": dict(sorted(counts_b.items())),
                },
                "differing_letters": differing,
            },
        }

    def _check_palindrome(self, text: str, strict: bool) -> Dict[str, Any]:
        """Check a text for palindrome-ness on two bases."""
        context = {"text": text, "strict": strict}
        letters = self._letters(text)
        if not letters:
            return self._error_result(
                context,
                error_type="empty_after_strip",
                message=(
                    "palindrome checking needs at least one letter after "
                    "casefolding and removing non-letters "
                    f"(text {text!r} reduces to '')"
                ),
            )
        letters_pal = letters == letters[::-1]
        raw_pal = text == text[::-1]
        is_palindrome = raw_pal if strict else letters_pal
        first_mismatch = None
        basis_text = text if strict else letters
        if not is_palindrome:
            length = len(basis_text)
            for i in range(length // 2):
                if basis_text[i] != basis_text[length - 1 - i]:
                    first_mismatch = {
                        "position": i,
                        "left": basis_text[i],
                        "right": basis_text[length - 1 - i],
                    }
                    break
        if is_palindrome and strict:
            verdict = "palindrome on the strict raw-character basis"
        elif is_palindrome:
            verdict = "palindrome on the letters-only basis"
        else:
            verdict = "not a palindrome"
        return {
            **context,
            "is_palindrome": is_palindrome,
            "basis": {"letters_only": letters_pal, "raw": raw_pal},
            "verdict": verdict,
            "details": {
                "cleaned_text": letters,
                "cleaned_length": len(letters),
                "first_mismatch": first_mismatch,
            },
        }

    # ------------------------------------------------------------------ #
    # anagrams_of mode
    # ------------------------------------------------------------------ #

    def _run_anagrams_of(self, text: str) -> Dict[str, Any]:
        """Permute the input's letters and match the demo word list."""
        context = {"mode": "anagrams_of", "text": text}
        word = self._letters(text)
        if not word:
            return self._error_result(
                context,
                error_type="empty_after_strip",
                message=(
                    "anagrams_of needs at least one letter after casefolding "
                    f"and removing non-letters (text {text!r} reduces to '')"
                ),
            )
        if len(word) > self.MAX_ANAGRAM_INPUT:
            self._invalid(
                "anagrams_of input exceeds the "
                f"{self.MAX_ANAGRAM_INPUT}-letter limit after casefolding "
                f"and removing non-letters (got {len(word)} letters) — "
                "permutation matching is capped to stay deterministic "
                "and cheap"
            )
        candidates = {
            "".join(permutation)
            for permutation in itertools.permutations(word)
        }
        matches = sorted(
            candidate
            for candidate in candidates
            if candidate in _DEMO_WORDS and candidate != word
        )
        total = len(matches)
        truncated = total > self.MAX_ANAGRAM_RESULTS
        return {
            **context,
            "word": word,
            "letters": len(word),
            "anagrams": matches[: self.MAX_ANAGRAM_RESULTS],
            "count": min(total, self.MAX_ANAGRAM_RESULTS),
            "total_found": total,
            "truncated": truncated,
            "excluded_input": word in _DEMO_WORDS,
            "word_list_size": len(_DEMO_WORDS),
            "note": (
                "matched against the embedded common-English demo word "
                "list (English only, not a dictionary)"
            ),
        }

    # ------------------------------------------------------------------ #
    # palindrome_parts mode
    # ------------------------------------------------------------------ #

    def _run_palindrome_parts(self, text: str) -> Dict[str, Any]:
        """Find the longest and all >=3-letter palindromic substrings."""
        context = {"mode": "palindrome_parts", "text": text}
        cleaned = self._letters(text)
        if not cleaned:
            return self._error_result(
                context,
                error_type="empty_after_strip",
                message=(
                    "palindrome_parts needs at least one letter after "
                    f"casefolding and removing non-letters (text {text!r} "
                    "reduces to '')"
                ),
            )
        length = len(cleaned)
        palindromes = set()
        best = ""
        for center in range(length):
            for left, right in ((center, center), (center, center + 1)):
                while (
                    left >= 0
                    and right < length
                    and cleaned[left] == cleaned[right]
                ):
                    substring = cleaned[left : right + 1]
                    if len(substring) > len(best):
                        best = substring
                    if len(substring) >= self.MIN_PART_LENGTH:
                        palindromes.add(substring)
                    left -= 1
                    right += 1
        ordered = sorted(palindromes, key=lambda s: (-len(s), s))
        total = len(ordered)
        truncated = total > self.MAX_PALINDROMES
        return {
            **context,
            "cleaned_text": cleaned,
            "cleaned_length": length,
            "longest": best,
            "longest_length": len(best),
            "palindromes": ordered[: self.MAX_PALINDROMES],
            "count": min(total, self.MAX_PALINDROMES),
            "total_found": total,
            "truncated": truncated,
        }

    # ------------------------------------------------------------------ #
    # letter_score mode
    # ------------------------------------------------------------------ #

    def _run_letter_score(self, text: str) -> Dict[str, Any]:
        """Score the text with standard English Scrabble tile values."""
        context = {"mode": "letter_score", "text": text}
        folded = text.casefold()
        counts = Counter(
            ch for ch in folded if ch in SCRABBLE_VALUES
        )
        if not counts:
            return self._error_result(
                context,
                error_type="no_scoreable_letters",
                message=(
                    "letter_score needs at least one ASCII letter (a-z) "
                    "to score — every Scrabble tile value is defined for "
                    f"English letters only (text {text[:64]!r} has none)"
                ),
            )
        unscored = Counter(
            ch for ch in folded if ch not in SCRABBLE_VALUES
        )
        breakdown = [
            {
                "letter": letter,
                "count": count,
                "value": SCRABBLE_VALUES[letter],
                "points": count * SCRABBLE_VALUES[letter],
            }
            for letter, count in sorted(counts.items())
        ]
        result: Dict[str, Any] = {
            **context,
            "word": "".join(ch for ch in folded if ch in SCRABBLE_VALUES),
            "score": sum(entry["points"] for entry in breakdown),
            "breakdown": breakdown,
        }
        if unscored:
            result["unscored"] = {
                "counts": dict(sorted(unscored.items())),
                "total": sum(unscored.values()),
            }
        return result

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
