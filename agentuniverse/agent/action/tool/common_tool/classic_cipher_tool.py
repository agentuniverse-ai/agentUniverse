#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: classic_cipher_tool.py

"""Classical cipher utility tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency cipher toolbox agents
can call for puzzle / CTF-style tasks: encoding clues, checking
candidate decryptions, or brute-forcing shift ciphers.

The tool implements five classical schemes and always keeps the output
readable and reversible:

* ``rot13`` — the self-inverse ROT13 transform. Applying it twice
  restores the input, so no ``operation`` selector is needed.
* ``caesar`` — the Caesar shift cipher with a ``shift`` of 1-25 and an
  explicit ``encode`` / ``decode`` operation (decoding with the same
  shift reverses an encoding).
* ``atbash`` — the Atbash mirror mapping ``A`` <-> ``Z``, ``B`` <-> ``Y``,
  ... Like ROT13 it is self-inverse, so no ``operation`` is needed.
* ``vigenere`` — the Vigenère polyalphabetic cipher with a ``key`` of
  ASCII letters only. Key letters are case-insensitive; the key stream
  advances only over the letters of the text (the standard convention),
  so digits and punctuation do not consume key material. Encoding and
  decoding with the same key round-trip exactly.
* ``crack`` — brute-force cryptanalysis of any Caesar / ROT13 shifted
  text: all 26 candidate shifts are tried and ranked by the
  chi-squared distance between the candidate's letter histogram and
  standard English letter frequencies (lower score = more
  English-like). The top-3 candidates are returned with their shift,
  score and plaintext.

Every mode transforms only the 26 ASCII letters ``A``-``Z`` / ``a``-``z``
and preserves the case of each letter. Any other character — digits,
punctuation, whitespace, accented Latin letters, and non-Latin scripts
such as CJK — passes through the transform completely unchanged.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode / operation, wrong ``text`` type,
empty text, oversized text, a Caesar ``shift`` outside 1-25, a
Vigenère ``key`` that is not a non-empty string of ASCII letters)
raise a ``ValueError``, mirroring the other common tools. One failure
depends on the *content being processed* instead: ``crack`` on a text
that contains no ASCII letters at all (letter-frequency ranking would
be meaningless) returns a structured ``error`` payload so an agent can
react without catching exceptions.
"""

import re
import string
from typing import Any, ClassVar, Dict, List

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_LETTERS_ONLY = re.compile(r"\A[A-Za-z]+\Z")
_INTEGER = re.compile(r"\A[+-]?[0-9]+\Z")
_LOWER = string.ascii_lowercase
_UPPER = string.ascii_uppercase

# Standard English relative letter frequencies (percent), as published
# in the well-known "Letter frequency" table (Wikipedia / Lewand's
# _Cryptological Mathematics_). Used by the chi-squared ranker of the
# crack mode.
_ENGLISH_FREQ: Dict[str, float] = {
    "a": 8.167, "b": 1.492, "c": 2.782, "d": 4.253, "e": 12.702,
    "f": 2.228, "g": 2.015, "h": 6.094, "i": 6.966, "j": 0.153,
    "k": 0.772, "l": 4.025, "m": 2.406, "n": 6.749, "o": 7.507,
    "p": 1.929, "q": 0.095, "r": 5.987, "s": 6.327, "t": 9.056,
    "u": 2.758, "v": 0.978, "w": 2.360, "x": 0.150, "y": 1.974,
    "z": 0.074,
}


class ClassicCipherTool(Tool):
    """Classical cipher utility tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any computation.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "classic_cipher_tool"
    description: str = (
        "Classical cipher tool — pure Python stdlib, no network "
        "required. ROT13 self-inverse transform (mode='rot13'), Caesar "
        "encode/decode with shift 1-25 (mode='caesar'), Atbash mirror "
        "mapping (mode='atbash'), Vigenère encode/decode with a "
        "letters-only key (mode='vigenere'), and brute-force "
        "Caesar/ROT13 cracking that ranks all 26 shifts by English "
        "letter-frequency chi-squared score and returns the top-3 "
        "candidates (mode='crack'). Case is preserved and non-ASCII "
        "letters, digits, punctuation and CJK pass through unchanged."
    )

    MODES: ClassVar[tuple] = ("rot13", "caesar", "atbash", "vigenere", "crack")
    OPERATIONS: ClassVar[tuple] = ("encode", "decode")

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        operation: Any = None,
        shift: Any = None,
        key: Any = None,
    ) -> Dict[str, Any]:
        """Run one classical cipher operation.

        Args:
            mode (str): One of ``rot13`` / ``caesar`` / ``atbash`` /
                ``vigenere`` / ``crack``.
            text (str): The text to transform (non-empty string, at
                most 100,000 characters).
            operation (str): ``encode`` or ``decode`` — required for
                the ``caesar`` and ``vigenere`` modes; the self-inverse
                ``rot13`` / ``atbash`` modes and ``crack`` do not use
                it.
            shift (int | str): Caesar shift, an integer between 1 and
                25 (a plain digit string like ``"3"`` is also
                accepted). Caesar mode only.
            key (str): Vigenère key — a non-empty string of ASCII
                letters only (case-insensitive). Vigenère mode only.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the call context; ``crack`` returns a
                ``candidates`` list of the three best shifts with
                ``shift`` / ``score`` / ``result``), or a structured
                ``error`` payload when ``crack`` receives a text
                without any ASCII letter to rank.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "rot13":
            return {"mode": "rot13", "result": self._caesar_text(clean_text, 13)}
        if mode == "atbash":
            return {"mode": "atbash", "result": self._atbash_text(clean_text)}
        if mode == "crack":
            return self._run_crack(clean_text)

        clean_operation = self._validate_operation(operation)
        if mode == "caesar":
            clean_shift = self._validate_shift(shift)
            delta = clean_shift if clean_operation == "encode" else -clean_shift
            return {
                "mode": "caesar",
                "operation": clean_operation,
                "shift": clean_shift,
                "result": self._caesar_text(clean_text, delta),
            }
        return self._run_vigenere(clean_operation, clean_text, key)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"classic_cipher_tool: {message}")

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
    def _validate_operation(cls, operation: Any) -> str:
        """Validate the encode/decode ``operation`` selector."""
        if operation not in cls.OPERATIONS:
            cls._invalid(
                "operation must be one of: "
                f"{', '.join(cls.OPERATIONS)} (got {operation!r})"
            )
        return operation

    @classmethod
    def _validate_shift(cls, shift: Any) -> int:
        """Validate the Caesar ``shift`` (integer 1-25 or digit string)."""
        value: Any = shift
        if isinstance(shift, str) and _INTEGER.match(shift.strip()):
            value = int(shift.strip())
        if isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(
                f"shift must be an integer between 1 and 25 (got {shift!r})"
            )
        if not 1 <= value <= 25:
            cls._invalid(
                f"shift must be an integer between 1 and 25 (got {shift!r})"
            )
        return value

    @classmethod
    def _validate_key(cls, key: Any) -> str:
        """Validate the Vigenère ``key`` (non-empty ASCII letters only)."""
        if key is None or isinstance(key, bool) or not isinstance(key, str):
            cls._invalid(
                "key must be a non-empty string of letters A-Z/a-z only "
                f"(got {key!r})"
            )
        if not key:
            cls._invalid("key must be a non-empty string of letters A-Z/a-z only (got '')")
        if not _LETTERS_ONLY.match(key):
            cls._invalid(
                "key must be a non-empty string of letters A-Z/a-z only "
                f"(got {key[:64]!r})"
            )
        return key

    # ------------------------------------------------------------------ #
    # Character-level primitives (ASCII letters only, case preserved)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _caesar_text(text: str, delta: int) -> str:
        """Shift every ASCII letter of ``text`` by ``delta`` positions."""
        out: List[str] = []
        for char in text:
            if "a" <= char <= "z":
                out.append(_LOWER[(ord(char) - 97 + delta) % 26])
            elif "A" <= char <= "Z":
                out.append(_UPPER[(ord(char) - 65 + delta) % 26])
            else:
                out.append(char)
        return "".join(out)

    @staticmethod
    def _atbash_text(text: str) -> str:
        """Mirror every ASCII letter (A<->Z, B<->Y, ...)."""
        out: List[str] = []
        for char in text:
            if "a" <= char <= "z":
                out.append(_LOWER[25 - (ord(char) - 97)])
            elif "A" <= char <= "Z":
                out.append(_UPPER[25 - (ord(char) - 65)])
            else:
                out.append(char)
        return "".join(out)

    # ------------------------------------------------------------------ #
    # vigenere mode
    # ------------------------------------------------------------------ #

    def _run_vigenere(
        self, operation: str, text: str, key: Any
    ) -> Dict[str, Any]:
        """Encode / decode Vigenère with a letters-only key.

        Key letters are case-insensitive and the key stream advances
        only over the letters of the text, so non-letters pass through
        without consuming key material — the standard convention that
        makes the classic published vectors reproducible.
        """
        clean_key = self._validate_key(key)
        shifts = [ord(char.lower()) - 97 for char in clean_key]
        sign = 1 if operation == "encode" else -1
        out: List[str] = []
        key_index = 0
        for char in text:
            if "a" <= char <= "z":
                out.append(
                    _LOWER[(ord(char) - 97 + sign * shifts[key_index % len(shifts)]) % 26]
                )
                key_index += 1
            elif "A" <= char <= "Z":
                out.append(
                    _UPPER[(ord(char) - 65 + sign * shifts[key_index % len(shifts)]) % 26]
                )
                key_index += 1
            else:
                out.append(char)
        return {
            "mode": "vigenere",
            "operation": operation,
            "key": clean_key,
            "result": "".join(out),
        }

    # ------------------------------------------------------------------ #
    # crack mode
    # ------------------------------------------------------------------ #

    def _run_crack(self, text: str) -> Dict[str, Any]:
        """Brute-force all 26 Caesar shifts and rank them by chi-squared.

        The score of a candidate is the chi-squared distance between
        its letter histogram and the expected English letter
        histogram: ``sum((observed - expected)^2 / expected)`` over the
        26 letters, where ``expected = english_frequency * n_letters``.
        Lower scores mean the candidate looks more like English; ties
        are broken by the lower shift so the ranking is deterministic.
        """
        counts = {letter: 0 for letter in _LOWER}
        for char in text:
            if "a" <= char <= "z":
                counts[char] += 1
            elif "A" <= char <= "Z":
                counts[char.lower()] += 1
        total = sum(counts.values())
        context: Dict[str, Any] = {"mode": "crack"}
        if total == 0:
            return self._error_result(
                context,
                error_type="no_alphabetic_characters",
                message=(
                    "text contains no ASCII letters, so English "
                    "letter-frequency ranking has nothing to score "
                    f"(got {text[:64]!r})"
                ),
            )

        # Shifting text maps letters to letters bijectively, so the
        # histogram of the candidate decrypted with shift s is the
        # ciphertext histogram rotated by s: candidate_count[p] =
        # counts[(p + s) mod 26].
        scored = []
        for shift in range(26):
            score = 0.0
            for index, letter in enumerate(_LOWER):
                expected = _ENGLISH_FREQ[letter] / 100.0 * total
                observed = counts[_LOWER[(index + shift) % 26]]
                score += (observed - expected) ** 2 / expected
            scored.append((score, shift))
        scored.sort(key=lambda item: (item[0], item[1]))
        candidates = [
            {
                "shift": shift,
                "score": score,
                "result": self._caesar_text(text, -shift),
            }
            for score, shift in scored[:3]
        ]
        return {"mode": "crack", "candidates": candidates}

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
