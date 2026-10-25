#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: unicode_inspector_tool.py

"""Unicode character / string inspection tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency "what is this
character" helper for agents that have to handle exotic text — mojibake
debugging, mixed-script detection or normalization checks — using only
the standard library ``unicodedata`` module.

The tool supports three modes:

* ``inspect`` — describe every character of a string (capped at the
  first 100 characters, the full count is always reported). Each
  per-character record contains the character itself, its codepoint as
  ``U+XXXX``, its hexadecimal value, its Unicode name (from
  ``unicodedata.name`` or ``<unnamed>`` for unassigned code points),
  its general category with a human-readable label, its bidirectional
  class, its East Asian width with the meaning of the ``W`` / ``F`` /
  ``H`` / ``Na`` / ``A`` / ``N`` classes documented, its NFD
  decomposition mapping (or ``None`` when there is none) and an
  ``is_emoji_ish`` flag that is true when the category is ``So``
  (Symbol, other — where the plain-text emoji live).
* ``string_stats`` — summarize the script mix of a string with a
  category / codepoint-range heuristic (counts for Latin, CJK,
  Hangul, Kana, Cyrillic, Greek, Arabic, Hebrew, digits, punctuation,
  symbols, whitespace and a catch-all ``other`` bucket so the counts
  always sum to the total), plus the NFKC-normalized form and the
  length of the string in all three metrics that matter: code points,
  UTF-8 bytes and UTF-16 code units.
* ``normalize`` — apply one of the four Unicode normalization forms
  ``NFC`` / ``NFD`` / ``NFKC`` / ``NFKD`` and report the normalized
  string, whether anything changed and the positions of the original
  string that changed (capped at 100 positions).

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text, unknown mode or form,
oversized text) raise a ``ValueError``, mirroring the other common
tools. All outputs are deterministic for a given Python ``unicodedata``
database version; nothing in the tool is random and nothing touches
the network.
"""

import difflib
import unicodedata
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Human-readable labels for the Unicode general categories (Unicode
# chapter 4, general category values).
_CATEGORY_LABELS: dict[str, str] = {
    "Lu": "Uppercase Letter",
    "Ll": "Lowercase Letter",
    "Lt": "Titlecase Letter",
    "Lm": "Modifier Letter",
    "Lo": "Other Letter",
    "Mn": "Nonspacing Mark",
    "Mc": "Spacing Combining Mark",
    "Me": "Enclosing Mark",
    "Nd": "Decimal Digit",
    "Nl": "Letter Number",
    "No": "Other Number",
    "Pc": "Connector Punctuation",
    "Pd": "Dash Punctuation",
    "Ps": "Open Punctuation",
    "Pe": "Close Punctuation",
    "Pi": "Initial Punctuation",
    "Pf": "Final Punctuation",
    "Po": "Other Punctuation",
    "Sm": "Math Symbol",
    "Sc": "Currency Symbol",
    "Sk": "Modifier Symbol",
    "So": "Other Symbol",
    "Zs": "Space Separator",
    "Zl": "Line Separator",
    "Zp": "Paragraph Separator",
    "Cc": "Control",
    "Cf": "Format",
    "Cs": "Surrogate",
    "Co": "Private Use",
    "Cn": "Unassigned",
}

# Meaning of the East Asian width classes (Unicode UAX #11).
_EAW_LABELS: dict[str, str] = {
    "F": "fullwidth — wide form, two columns in East Asian context",
    "H": "halfwidth — narrow form, one column",
    "W": "wide — East Asian wide, two columns",
    "Na": "narrow — one column",
    "A": "ambiguous — one or two columns depending on context",
    "N": "neutral — not East Asian, one column",
}

# Codepoint ranges for the script buckets of the string_stats heuristic.
# Checked in this order; script buckets win over the category buckets,
# so e.g. Arabic-Indic digits count as arabic while ASCII digits count
# as digits (they are not part of the Latin ranges below).
_SCRIPT_RANGES: dict[str, list[tuple[int, int]]] = {
    "latin": [
        (0x0041, 0x005A), (0x0061, 0x007A), (0x00AA, 0x00AA),
        (0x00BA, 0x00BA), (0x00C0, 0x024F), (0x1E00, 0x1EFF),
        (0x2C60, 0x2C7F), (0xA720, 0xA7FF), (0xFB00, 0xFB06),
        (0xFF21, 0xFF3A), (0xFF41, 0xFF5A),
    ],
    "greek": [(0x0370, 0x03FF), (0x1F00, 0x1FFF)],
    "cyrillic": [(0x0400, 0x052F), (0x2DE0, 0x2DFF), (0xA640, 0xA69F)],
    "hebrew": [(0x0590, 0x05FF), (0xFB1D, 0xFB4F)],
    "arabic": [
        (0x0600, 0x06FF), (0x0750, 0x077F),
        (0xFB50, 0xFDFF), (0xFE70, 0xFEFF),
    ],
    "kana": [
        (0x3041, 0x309F), (0x30A0, 0x30FF),
        (0x31F0, 0x31FF), (0xFF66, 0xFF9D),
    ],
    "hangul": [
        (0x1100, 0x11FF), (0x3130, 0x318F),
        (0xA960, 0xA97F), (0xAC00, 0xD7FF),
    ],
    "cjk": [
        (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF),
        (0x20000, 0x2FA1F), (0x30000, 0x3134F),
    ],
}

# Buckets reported by the string_stats mode, in reporting order.
_STAT_BUCKETS: tuple[str, ...] = (
    "latin", "cjk", "hangul", "kana", "cyrillic", "greek",
    "arabic", "hebrew", "digits", "punctuation", "symbols",
    "whitespace", "other",
)


class UnicodeInspectorTool(Tool):
    """Unicode character / string inspection tool, pure stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
        max_inspect_chars (int): Cap on the per-character records
            returned by the ``inspect`` mode.
        max_changed_positions (int): Cap on the changed-position list
            returned by the ``normalize`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "unicode_inspector_tool"
    description: str = (
        "Unicode inspector tool — pure Python stdlib unicodedata, no "
        "network required. 'What is this character' inspection "
        "(mode='inspect'): per-character records with codepoint U+XXXX, "
        "hex, Unicode name, category with human-readable label, "
        "bidirectional class, East Asian width (W/F/H/Na/A/N meaning "
        "documented), NFD decomposition and an is-emoji-ish (category "
        "So) flag, capped at 100 characters with the total count. "
        "Script-mix summary (mode='string_stats'): counts of "
        "Latin/CJK/Hangul/Kana/Cyrillic/Greek/Arabic/Hebrew/digits/"
        "punctuation/symbols/whitespace plus the NFKC form and the "
        "length in code points, UTF-8 bytes and UTF-16 units. Unicode "
        "normalization (mode='normalize'): NFC/NFD/NFKC/NFKD with a "
        "changed flag and the changed positions."
    )

    MODES: ClassVar[tuple] = ("inspect", "string_stats", "normalize")
    FORMS: ClassVar[tuple] = ("NFC", "NFD", "NFKC", "NFKD")

    max_text_chars: int = 100_000
    max_inspect_chars: int = 100
    max_changed_positions: int = 100

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self, mode: Any = None, text: Any = None, form: Any = None
    ) -> dict[str, Any]:
        """Run one Unicode inspection operation.

        Args:
            mode (str): One of ``inspect`` / ``string_stats`` /
                ``normalize``.
            text (str): The text to inspect. Must be a non-empty string
                of at most 100,000 characters.
            form (str): Normalize mode only — one of ``NFC`` / ``NFD`` /
                ``NFKC`` / ``NFKD`` (exact uppercase spelling).

        Returns:
            Dict[str, Any]: The inspection result; see the module
                docstring for the payload of each mode.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "inspect":
            return self._run_inspect(clean_text)
        if mode == "string_stats":
            return self._run_string_stats(clean_text)
        return self._run_normalize(clean_text, form)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"unicode_inspector_tool: {message}")

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
    # inspect mode
    # ------------------------------------------------------------------ #

    def _run_inspect(self, text: str) -> dict[str, Any]:
        """Describe every character of the text (capped at 100 records)."""
        total = len(text)
        capped = text[: self.max_inspect_chars]
        records = [
            self._inspect_char(index, char) for index, char in enumerate(capped)
        ]
        return {
            "mode": "inspect",
            "total_chars": total,
            "returned_chars": len(records),
            "truncated": total > len(records),
            "characters": records,
        }

    @classmethod
    def _inspect_char(cls, index: int, char: str) -> dict[str, Any]:
        """Build the per-character record for the inspect mode."""
        code = ord(char)
        try:
            name = unicodedata.name(char)
        except ValueError:
            # Unassigned code point (or a lone surrogate) has no name.
            name = "<unnamed>"
        category = unicodedata.category(char)
        category_label = _CATEGORY_LABELS.get(category, "Unknown")
        eaw = unicodedata.east_asian_width(char)
        eaw_label = _EAW_LABELS.get(eaw, "unknown width class")
        decomposition = unicodedata.decomposition(char)
        return {
            "index": index,
            "char": char,
            "codepoint": f"U+{code:04X}",
            "hex": format(code, "x"),
            "name": name,
            "category": f"{category} ({category_label})",
            "bidi_class": unicodedata.bidirectional(char),
            "east_asian_width": f"{eaw} ({eaw_label})",
            "decomposition": decomposition if decomposition else None,
            "is_emoji_ish": category == "So",
        }

    # ------------------------------------------------------------------ #
    # string_stats mode
    # ------------------------------------------------------------------ #

    def _run_string_stats(self, text: str) -> dict[str, Any]:
        """Summarize the script mix, NFKC form and the three lengths."""
        counts = {bucket: 0 for bucket in _STAT_BUCKETS}
        for char in text:
            counts[self._classify_char(char)] += 1
        return {
            "mode": "string_stats",
            "total_chars": len(text),
            "script_counts": counts,
            "nfkc": unicodedata.normalize("NFKC", text),
            "lengths": {
                "code_points": len(text),
                "utf8_bytes": len(text.encode("utf-8")),
                "utf16_units": len(text.encode("utf-16-le")) // 2,
            },
        }

    @staticmethod
    def _classify_char(char: str) -> str:
        """Classify one character into a string_stats bucket.

        The order defines the heuristic: whitespace wins over everything
        (``str.isspace`` also covers tab/newline control characters),
        then the script codepoint ranges, then the general-category
        buckets (digits ``Nd``, punctuation ``P*``, symbols ``S*``);
        everything else — marks, control and format characters,
        unassigned code points — lands in the ``other`` bucket so the
        counts always sum to the total number of characters.
        """
        if char.isspace():
            return "whitespace"
        code = ord(char)
        for script, ranges in _SCRIPT_RANGES.items():
            for low, high in ranges:
                if low <= code <= high:
                    return script
        category = unicodedata.category(char)
        if category == "Nd":
            return "digits"
        if category.startswith("P"):
            return "punctuation"
        if category.startswith("S"):
            return "symbols"
        return "other"

    # ------------------------------------------------------------------ #
    # normalize mode
    # ------------------------------------------------------------------ #

    def _run_normalize(self, text: str, form: Any) -> dict[str, Any]:
        """Normalize the text and report the changed positions."""
        if isinstance(form, bool) or form not in self.FORMS:
            self._invalid(
                "form must be one of: "
                f"{', '.join(self.FORMS)} (got {form!r})"
            )
        normalized = unicodedata.normalize(form, text)
        changed = self._changed_positions(text, normalized)
        capped = changed[: self.max_changed_positions]
        return {
            "mode": "normalize",
            "form": form,
            "result": normalized,
            "changed": normalized != text,
            "changed_count": len(changed),
            "changed_positions": capped,
            "changed_positions_truncated": len(changed) > len(capped),
        }

    @staticmethod
    def _changed_positions(original: str, normalized: str) -> list[int]:
        """Positions of the original string affected by normalization.

        Uses ``difflib.SequenceMatcher`` over the two strings: every
        original index covered by a non-``equal`` opcode is reported, so
        a replaced character position and a deleted character position
        both count as changed. The result is sorted ascending.
        """
        matcher = difflib.SequenceMatcher(a=original, b=normalized, autojunk=False)
        positions: list[int] = []
        for tag, i1, i2, _j1, _j2 in matcher.get_opcodes():
            if tag != "equal":
                positions.extend(range(i1, i2))
        return sorted(positions)
