#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: phonetic_alphabet_tool.py

"""NATO / ICAO spelling-alphabet tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency utility agents can
call for voice-friendly communication: radio / telephone spelling of
identifiers, call signs, one-time codes and serial numbers.

The tool implements the single worldwide-standard spelling alphabet —
the ICAO spelling alphabet (ICAO Annex 10), universally known as the
NATO phonetic alphabet — together with its ICAO digit words, and
supports three modes:

* ``spell`` — convert text to phonetic words, one token per character:
  ``A`` → ``Alfa`` … ``Z`` → ``Zulu`` and ``0`` → ``Zero`` … ``9`` →
  ``Niner``. Case is preserved in the per-character ``entries`` list
  (each entry pairs the phonetic word with the original letter). A
  space becomes a configurable ``space_marker`` token (default
  ``[space]``, e.g. ``·`` also works). Characters outside ``A-Z``,
  ``0-9`` and space — punctuation, symbols, non-ASCII letters — are
  passed through unchanged as their own tokens and reported in the
  ``flagged`` list so nothing is silently dropped or invented.
* ``read`` — convert a sequence of phonetic words back to text.
  Words are matched case-insensitively (``hotel``, ``HOTEL`` and
  ``Hotel`` all map to ``H``), the space marker maps back to a space,
  and single non-alphanumeric pass-through characters (mirroring the
  ``spell`` flagging rule) are kept as-is. Any other token is
  rejected with a structured ``error`` payload that names the
  offending word and its 0-based position.
* ``list`` — return the complete letter and digit tables.

Only the NATO / ICAO alphabet is supported, deliberately. Spelling
alphabets such as the German DIN 5009 or the French "alphabet radio"
exist in several mutually incompatible revisions (for example DIN
5009:1996 vs :2022, or the French ancienne vs nouvelle versions)
with no single canonical table including digit words; rather than
embed a table that may be wrong for a given revision, the tool offers
no ``alphabet`` option at all. The official ICAO spellings are used:
``Alfa`` (not "Alpha"), ``Juliett`` (not "Juliet"), ``X-ray`` and the
digit ``Niner`` (not "Nine").

Input validation is strict and happens before any computation:
malformed parameters (wrong types, missing or empty ``text`` for the
spell/read modes, unknown mode, whitespace inside or other invalid
``space_marker``, non-space whitespace or control characters in spell
or read input, oversized text) raise a ``ValueError``, mirroring the other
common tools. Errors that depend on the *content being processed* —
an unknown word in ``read`` mode — are returned as a structured
``error`` payload so an agent can react without catching exceptions.

Round-trip contract: for text consisting only of ``A-Z``, ``0-9`` and
spaces, ``read(spell(text))`` reproduces the text exactly except that
letters are returned uppercase (the read mapping is case-insensitive,
so letter case cannot be recovered and is canonicalised to upper).
Flagged pass-through characters survive a round trip as themselves.
Caveat: pick a ``space_marker`` that does not occur in the text being
spelled — a literal marker character sequence inside the input would
be indistinguishable from a space after spelling.
"""

from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class PhoneticAlphabetTool(Tool):
    """NATO / ICAO spelling-alphabet tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "phonetic_alphabet_tool"
    description: str = (
        "NATO / ICAO spelling-alphabet tool — pure Python stdlib, no "
        "network required. Spells text into phonetic words per "
        "character (mode='spell': A→Alfa … Z→Zulu, 0→Zero … 9→Niner, "
        "spaces become a configurable marker, punctuation passed "
        "through flagged), reads phonetic words back to text "
        "case-insensitively with unknown words rejected by name and "
        "position (mode='read'), and lists the full letter and digit "
        "tables (mode='list')."
    )

    MODES: ClassVar[tuple] = ("spell", "read", "list")
    # ICAO spelling alphabet (ICAO Annex 10), aka the NATO phonetic
    # alphabet. Official spellings: Alfa, Juliett, X-ray.
    LETTERS: ClassVar[dict[str, str]] = {
        "A": "Alfa",
        "B": "Bravo",
        "C": "Charlie",
        "D": "Delta",
        "E": "Echo",
        "F": "Foxtrot",
        "G": "Golf",
        "H": "Hotel",
        "I": "India",
        "J": "Juliett",
        "K": "Kilo",
        "L": "Lima",
        "M": "Mike",
        "N": "November",
        "O": "Oscar",
        "P": "Papa",
        "Q": "Quebec",
        "R": "Romeo",
        "S": "Sierra",
        "T": "Tango",
        "U": "Uniform",
        "V": "Victor",
        "W": "Whiskey",
        "X": "X-ray",
        "Y": "Yankee",
        "Z": "Zulu",
    }
    # ICAO phonetic digit words ("Niner", not "Nine").
    DIGITS: ClassVar[dict[str, str]] = {
        "0": "Zero",
        "1": "One",
        "2": "Two",
        "3": "Three",
        "4": "Four",
        "5": "Five",
        "6": "Six",
        "7": "Seven",
        "8": "Eight",
        "9": "Niner",
    }
    DEFAULT_SPACE_MARKER: ClassVar[str] = "[space]"

    max_text_chars: int = 10_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any,
        text: Any = None,
        space_marker: Any = None,
    ) -> dict[str, Any]:
        """Run one spelling-alphabet operation.

        Args:
            mode (str): One of ``spell`` / ``read`` / ``list``.
            text (str): The text to spell (spell mode) or the phonetic
                words to read back (read mode). Required — a non-empty
                string — for spell and read; not used by ``list``.
            space_marker (str): Token that represents a space
                character. Defaults to ``[space]``; ``·`` is a common
                compact alternative. Must be a non-empty string without
                whitespace, must not collide (case-insensitively) with
                any phonetic word, and must not be a single alphanumeric
                character, so that read mode stays unambiguous.

        Returns:
            Dict[str, Any]: The operation result (a ``result`` string
                plus the call context; spell mode additionally returns
                the per-character ``entries`` and the ``flagged``
                pass-through list, list mode the full ``letters`` and
                ``digits`` tables) or a structured ``error`` payload for
                content-level failures (unknown word in read mode).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "list":
            return self._run_list()
        clean_text = self._validate_text(text)
        clean_marker = self._validate_space_marker(space_marker)
        if mode == "spell":
            return self._run_spell(clean_text, clean_marker)
        return self._run_read(clean_text, clean_marker)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"phonetic_alphabet_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input for the spell / read modes."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 10_000:
            cls._invalid(
                f"text exceeds the {10_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        for position, char in enumerate(text):
            # The alphabet is for speakable text: the plain space is
            # spelled via the marker; any other whitespace or control
            # character (tab, newline, NBSP, ...) is rejected.
            if char != " " and (char.isspace() or ord(char) < 0x20 or char == "\x7f"):
                cls._invalid(
                    "text must only contain printable characters with "
                    "plain spaces (control characters and other "
                    f"whitespace are not speakable; got {char!r} at "
                    f"position {position})"
                )
        return text

    @classmethod
    def _validate_space_marker(cls, space_marker: Any) -> str:
        """Validate the ``space_marker`` option.

        Accepts ``None`` (the ``[space]`` default). The marker must be
        a non-empty string without any whitespace, it must not collide
        (case-insensitively) with a phonetic word, and it must not be a
        single alphanumeric character, so that read mode cannot
        misinterpret a legitimate token as a space.
        """
        if space_marker is None:
            return cls.DEFAULT_SPACE_MARKER
        if isinstance(space_marker, bool) or not isinstance(space_marker, str):
            cls._invalid(
                f"space_marker must be a non-empty string or None (got {space_marker!r})"
            )
        if not space_marker:
            cls._invalid("space_marker must be a non-empty string or None (got '')")
        if len(space_marker) > 16:
            cls._invalid(
                "space_marker must be at most 16 characters long "
                f"(got {len(space_marker)})"
            )
        for char in space_marker:
            if char.isspace():
                cls._invalid(
                    "space_marker must not contain whitespace "
                    f"(got {space_marker!r})"
                )
        if space_marker.lower() in cls._reverse_map():
            cls._invalid(
                "space_marker must not collide with a phonetic word "
                f"(got {space_marker!r})"
            )
        if len(space_marker) == 1 and space_marker.isalnum():
            cls._invalid(
                "space_marker must not be a single alphanumeric "
                f"character, which read mode could not distinguish "
                f"from a pass-through character (got {space_marker!r})"
            )
        return space_marker

    # ------------------------------------------------------------------ #
    # Table helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _reverse_map(cls) -> dict[str, str]:
        """Lowercased phonetic word → canonical character."""
        table = {word.lower(): letter for letter, word in cls.LETTERS.items()}
        table.update(
            {word.lower(): digit for digit, word in cls.DIGITS.items()}
        )
        return table

    # ------------------------------------------------------------------ #
    # spell mode
    # ------------------------------------------------------------------ #

    def _run_spell(self, text: str, space_marker: str) -> dict[str, Any]:
        """Spell text into phonetic words, one token per character."""
        entries: list[dict[str, str]] = []
        flagged: list[dict[str, Any]] = []
        tokens: list[str] = []
        for index, char in enumerate(text):
            if char == " ":
                word = space_marker
            elif char.isascii() and char.isalpha():
                word = self.LETTERS[char.upper()]
            elif char.isdigit() and char in self.DIGITS:
                word = self.DIGITS[char]
            else:
                # Punctuation, symbols and non-ASCII characters pass
                # through unchanged as their own token, flagged.
                word = char
                flagged.append({"char": char, "index": index})
            entries.append({"char": char, "word": word})
            tokens.append(word)
        return {
            "mode": "spell",
            "result": " ".join(tokens),
            "entries": entries,
            "flagged": flagged,
            "space_marker": space_marker,
        }

    # ------------------------------------------------------------------ #
    # read mode
    # ------------------------------------------------------------------ #

    def _run_read(self, text: str, space_marker: str) -> dict[str, Any]:
        """Read phonetic words back to text, case-insensitively."""
        reverse = self._reverse_map()
        tokens = text.split()
        context = {"mode": "read", "space_marker": space_marker}
        characters: list[str] = []
        for index, token in enumerate(tokens):
            lowered = token.lower()
            if lowered == space_marker.lower():
                characters.append(" ")
            elif lowered in reverse:
                characters.append(reverse[lowered])
            elif len(token) == 1 and not token.isalnum():
                # Single pass-through character, mirroring the spell
                # flagging rule for punctuation and symbols.
                characters.append(token)
            else:
                return self._error_result(
                    context,
                    error_type="unknown_word",
                    message=(
                        f"unknown phonetic word {token!r} at position "
                        f"{index} (word {index + 1} of {len(tokens)}) — "
                        "expected a NATO/ICAO letter word (Alfa…Zulu), a "
                        "digit word (Zero…Niner), the space marker, or a "
                        "single non-alphanumeric pass-through character"
                    ),
                )
        return {**context, "result": "".join(characters)}

    # ------------------------------------------------------------------ #
    # list mode
    # ------------------------------------------------------------------ #

    def _run_list(self) -> dict[str, Any]:
        """Return the complete NATO / ICAO letter and digit tables."""
        return {
            "mode": "list",
            "alphabet": "nato",
            "letters": dict(self.LETTERS),
            "digits": dict(self.DIGITS),
            "default_space_marker": self.DEFAULT_SPACE_MARKER,
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
