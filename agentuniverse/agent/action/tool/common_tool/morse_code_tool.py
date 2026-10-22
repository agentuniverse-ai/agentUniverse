#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: morse_code_tool.py

"""International Morse code tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency Morse codec agents
can call for signalling, puzzle, CTF and educational workflows.

The tool implements the International Morse code of ITU-R M.1677-1:
the 26 letters, the 10 digits and the standard punctuation set
``. , ? ' ! / ( ) & : ; = + - _ " $ @``. Three modes are supported:

* ``encode`` — text to Morse. Input is case-insensitive; letters are
  separated by a single space and words by ``" / "`` (any run of
  whitespace separates words). Characters outside the table (including
  CJK and emoji) are flagged per character — after case folding — in
  ``unknown_chars`` / ``skipped_count`` and skipped, so the encodable
  characters are still converted.
* ``decode`` — Morse to text. The input is split into space-separated
  tokens; a ``/`` token (i.e. the ``" / "`` word separator) starts a
  new word, every other token must be a code from the International
  Morse table. Invalid tokens are rejected with a structured
  ``error`` payload that lists the offending token(s). Prosigns are
  handled as normal letters: ``SOS`` must be sent as ``... --- ...``,
  and the concatenated form ``...---...`` is reported as an invalid
  token. The decoded text is uppercase.
* ``table`` — the full character-to-code mapping (54 entries).

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty or whitespace-only text in
the encode/decode modes, unknown mode, oversized text) raise a
``ValueError``, mirroring the other common tools. Errors that depend
on the *content being processed* — a decode token that is not valid
International Morse — are returned as a structured ``error`` payload
so an agent can react without catching exceptions.
"""

from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class MorseCodeTool(Tool):
    """International Morse code encode / decode / table tool.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "morse_code_tool"
    description: str = (
        "Morse code tool — International Morse (ITU-R M.1677-1), pure "
        "Python stdlib, no network required. Encode text to Morse with "
        "letters separated by single spaces and words by ' / ' "
        "(mode='encode', case-insensitive, unknown characters flagged "
        "and skipped), decode Morse back to uppercase text rejecting "
        "invalid tokens with the token listed (mode='decode', '/' is "
        "the word separator, prosigns handled as normal letters), or "
        "return the full character-to-code table (mode='table')."
    )

    MODES: ClassVar[tuple] = ("encode", "decode", "table")
    # International Morse code, ITU-R M.1677-1: letters, digits, then
    # the standard punctuation set in a fixed order. Insertion order is
    # part of the deterministic `table` mode output.
    MORSE_CODE: ClassVar[dict[str, str]] = {
        "A": ".-", "B": "-...", "C": "-.-.", "D": "-..",
        "E": ".", "F": "..-.", "G": "--.", "H": "....",
        "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
        "M": "--", "N": "-.", "O": "---", "P": ".--.",
        "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
        "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
        "Y": "-.--", "Z": "--..",
        "0": "-----", "1": ".----", "2": "..---", "3": "...--",
        "4": "....-", "5": ".....", "6": "-....", "7": "--...",
        "8": "---..", "9": "----.",
        ".": ".-.-.-", ",": "--..--", "?": "..--..", "'": ".----.",
        "!": "-.-.--", "/": "-..-.", "(": "-.--.", ")": "-.--.-",
        "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-",
        "+": ".-.-.", "-": "-....-", "_": "..--.-", '"': ".-..-.",
        "$": "...-..-", "@": ".--.-.",
    }
    # Reverse lookup shared by the decode mode (codes are unique).
    MORSE_TO_CHAR: ClassVar[dict[str, str]] = {
        code: char for char, code in MORSE_CODE.items()
    }

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(self, mode: Any = None, text: Any = None) -> dict[str, Any]:
        """Run one Morse code operation.

        Args:
            mode (str): One of ``encode`` / ``decode`` / ``table``.
            text (str): The text to encode (case-insensitive; letters,
                digits and the punctuation set ``.,?'!/()&:;=+-_"$@``
                are supported, any whitespace run separates words) or
                the Morse string to decode (space-separated tokens,
                ``/`` as the word separator). Required for the
                ``encode`` and ``decode`` modes; not used by ``table``.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string or mapping plus the call context), with
                ``unknown_chars`` / ``skipped_count`` in encode mode;
                or a structured ``error`` payload for content-level
                failures (invalid decode tokens).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "table":
            return self._run_table()
        clean_text = self._validate_text(text)
        if mode == "encode":
            return self._run_encode(clean_text)
        return self._run_decode(clean_text)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"morse_code_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input of the encode/decode modes."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if not text.strip():
            cls._invalid(
                "text must contain at least one non-whitespace character "
                "(got whitespace only)"
            )
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    # ------------------------------------------------------------------ #
    # encode / decode / table modes
    # ------------------------------------------------------------------ #

    def _run_encode(self, text: str) -> dict[str, Any]:
        """Encode text to Morse, flagging unknown characters."""
        unknown: list[str] = []
        encoded_words: list[str] = []
        for word in text.upper().split():
            codes: list[str] = []
            for char in word:
                code = self.MORSE_CODE.get(char)
                if code is None:
                    unknown.append(char)
                else:
                    codes.append(code)
            # A word made entirely of unknown characters contributes
            # no Morse output (its characters are counted as skipped).
            if codes:
                encoded_words.append(" ".join(codes))
        return {
            "mode": "encode",
            "result": " / ".join(encoded_words),
            "unknown_chars": unknown[:100],
            "skipped_count": len(unknown),
        }

    def _run_decode(self, text: str) -> dict[str, Any]:
        """Decode Morse to uppercase text, rejecting invalid tokens."""
        words: list[list[str]] = [[]]
        invalid: list[str] = []
        for token in text.split():
            if token == "/":
                words.append([])
                continue
            char = self.MORSE_TO_CHAR.get(token)
            if char is None:
                invalid.append(token)
            else:
                words[-1].append(char)
        if invalid:
            shown = ", ".join(repr(token) for token in invalid[:5])
            more = (
                f" (+{len(invalid) - 5} more)"
                if len(invalid) > 5
                else ""
            )
            return self._error_result(
                {"mode": "decode"},
                error_type="invalid_morse_token",
                message=(
                    "input contains token(s) that are not International "
                    f"Morse code: {shown}{more}. Decode expects letters "
                    "separated by single spaces and words by ' / '; "
                    "prosigns are handled as normal letters, e.g. SOS "
                    "must be sent as '... --- ...' rather than the "
                    "concatenated '...---...'"
                ),
            )
        return {
            "mode": "decode",
            "result": " ".join(
                "".join(word) for word in words if word
            ),
        }

    def _run_table(self) -> dict[str, Any]:
        """Return the full character-to-code mapping."""
        return {
            "mode": "table",
            "result": dict(self.MORSE_CODE),
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any], error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
