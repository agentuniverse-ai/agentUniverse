#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: character_set_analyzer_tool.py

"""Unicode character-set profiling tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency analyzer that
profiles *which characters* a string is made of — the whole-string
counterpart to ``UnicodeInspectorTool``, which inspects individual
characters. It answers questions such as "which scripts does this
document mix?", "how much of this log line is control characters?"
and "is this payload safe for an ASCII-only downstream system?"

The tool is a strictly-validated façade over the standard library
``unicodedata`` module and supports three modes:

* ``blocks`` — census of Unicode blocks: every character of the text
  is assigned to a named block via a compact, documented block-range
  table (below) and counted. Characters outside every table range —
  notably astral-plane characters such as emoji — fall into an
  ``Other`` bucket. Output rows are sorted by count (descending) then
  block name (ascending) and carry a percentage of the total.
* ``categories`` — census of Unicode general categories: every
  character is classified by ``unicodedata.category`` (``Ll``, ``Lu``,
  ``Lo``, ``Nd``, ``P*`` punctuation, ``S*`` symbols, ``Zs``, ``Cc``,
  ...) with human-readable labels, plus one-letter group subtotals
  (Letter / Mark / Number / Punctuation / Symbol / Separator / Other).
* ``summary`` — quick fingerprint of the text: ``ascii_only`` and
  ``latin1_only`` flags, distinct character count, the five most
  frequent characters, a ``has_emoji`` flag (heuristic: any character
  of general category ``So``) and the control-character count.

Because ``unicodedata`` exposes character properties but *not* block
memberships, the ``blocks`` mode uses a compact block-range table of
34 well-known blocks (inclusive, non-overlapping, sorted by start
code point). It favors the blocks that dominate real-world text over
completeness; characters of the many uncovered blocks are counted
under ``Other`` rather than misattributed:

===========  ============  ==========================================
Start        End           Block
===========  ============  ==========================================
U+0000       U+007F        Basic Latin
U+0080       U+00FF        Latin-1 Supplement
U+0100       U+017F        Latin Extended-A
U+0180       U+024F        Latin Extended-B
U+0250       U+02AF        IPA Extensions
U+02B0       U+02FF        Spacing Modifier Letters
U+0300       U+036F        Combining Diacritical Marks
U+0370       U+03FF        Greek and Coptic
U+0400       U+04FF        Cyrillic
U+0530       U+058F        Armenian
U+0590       U+05FF        Hebrew
U+0600       U+06FF        Arabic
U+0900       U+097F        Devanagari
U+0E00       U+0E7F        Thai
U+2000       U+206F        General Punctuation
U+20A0       U+20CF        Currency Symbols
U+2100       U+214F        Letterlike Symbols
U+2150       U+218F        Number Forms
U+2190       U+21FF        Arrows
U+2200       U+22FF        Mathematical Operators
U+2300       U+23FF        Miscellaneous Technical
U+2500       U+257F        Box Drawing
U+2580       U+259F        Block Elements
U+25A0       U+25FF        Geometric Shapes
U+2600       U+26FF        Miscellaneous Symbols
U+2700       U+27BF        Dingbats
U+3000       U+303F        CJK Symbols and Punctuation
U+3040       U+309F        Hiragana
U+30A0       U+30FF        Katakana
U+3400       U+4DBF        CJK Unified Ideographs Extension A
U+4E00       U+9FFF        CJK Unified Ideographs
U+AC00       U+D7AF        Hangul Syllables
U+E000       U+F8FF        Private Use Area
U+FF00       U+FFEF        Halfwidth and Fullwidth Forms
===========  ============  ==========================================

Input validation is strict and happens before any computation: an
unknown or non-lowercase ``mode``, a missing / empty / non-string
``text``, or text above the 100,000-character cap raises a
``ValueError``, mirroring the other common tools. There are no
content-level failure modes — every well-formed string can be
profiled — so the tool never returns error payloads.

All results are deterministic: counts, percentages (rounded to two
decimals) and sort orders (count descending, then name / category
code / code point ascending) are fully reproducible for the same
input and Python ``unicodedata`` version.
"""

import unicodedata
from bisect import bisect_right
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Compact Unicode block table: (first, last, name) inclusive ranges,
# sorted by first code point and non-overlapping. Characters outside
# every range are reported under the "Other" bucket.
_BLOCK_RANGES: Tuple[Tuple[int, int, str], ...] = (
    (0x0000, 0x007F, "Basic Latin"),
    (0x0080, 0x00FF, "Latin-1 Supplement"),
    (0x0100, 0x017F, "Latin Extended-A"),
    (0x0180, 0x024F, "Latin Extended-B"),
    (0x0250, 0x02AF, "IPA Extensions"),
    (0x02B0, 0x02FF, "Spacing Modifier Letters"),
    (0x0300, 0x036F, "Combining Diacritical Marks"),
    (0x0370, 0x03FF, "Greek and Coptic"),
    (0x0400, 0x04FF, "Cyrillic"),
    (0x0530, 0x058F, "Armenian"),
    (0x0590, 0x05FF, "Hebrew"),
    (0x0600, 0x06FF, "Arabic"),
    (0x0900, 0x097F, "Devanagari"),
    (0x0E00, 0x0E7F, "Thai"),
    (0x2000, 0x206F, "General Punctuation"),
    (0x20A0, 0x20CF, "Currency Symbols"),
    (0x2100, 0x214F, "Letterlike Symbols"),
    (0x2150, 0x218F, "Number Forms"),
    (0x2190, 0x21FF, "Arrows"),
    (0x2200, 0x22FF, "Mathematical Operators"),
    (0x2300, 0x23FF, "Miscellaneous Technical"),
    (0x2500, 0x257F, "Box Drawing"),
    (0x2580, 0x259F, "Block Elements"),
    (0x25A0, 0x25FF, "Geometric Shapes"),
    (0x2600, 0x26FF, "Miscellaneous Symbols"),
    (0x2700, 0x27BF, "Dingbats"),
    (0x3000, 0x303F, "CJK Symbols and Punctuation"),
    (0x3040, 0x309F, "Hiragana"),
    (0x30A0, 0x30FF, "Katakana"),
    (0x3400, 0x4DBF, "CJK Unified Ideographs Extension A"),
    (0x4E00, 0x9FFF, "CJK Unified Ideographs"),
    (0xAC00, 0xD7AF, "Hangul Syllables"),
    (0xE000, 0xF8FF, "Private Use Area"),
    (0xFF00, 0xFFEF, "Halfwidth and Fullwidth Forms"),
)

# Block start code points, kept in a parallel tuple for bisect lookup.
_BLOCK_STARTS: Tuple[int, ...] = tuple(
    first for first, _last, _name in _BLOCK_RANGES
)

# The bucket reported for characters outside every table range.
OTHER_BLOCK = "Other"


def lookup_block(code_point: int) -> str:
    """Return the block name for ``code_point`` (or ``"Other"``).

    Uses a binary search over the sorted, non-overlapping
    ``_BLOCK_RANGES`` table; characters not covered by any range —
    including astral-plane characters such as emoji — are attributed
    to the ``Other`` bucket instead of the nearest block.
    """
    index = bisect_right(_BLOCK_STARTS, code_point) - 1
    if index >= 0 and code_point <= _BLOCK_RANGES[index][1]:
        return _BLOCK_RANGES[index][2]
    return OTHER_BLOCK


class CharacterSetAnalyzerTool(Tool):
    """Unicode block / general-category profiling tool, pure stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input
            length; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "character_set_analyzer_tool"
    description: str = (
        "Character set analyzer tool — pure Python stdlib, no network "
        "required. Profiles which characters a string is made of: "
        "mode='blocks' counts characters per Unicode block via a "
        "compact 34-block range table (unknown and astral characters "
        "fall into an 'Other' bucket), mode='categories' counts "
        "unicodedata general categories (Ll, Lu, Lo, Nd, punctuation, "
        "symbols, Zs, Cc, ...) with human labels and one-letter group "
        "subtotals, and mode='summary' returns ascii_only / latin1_only "
        "flags, distinct character count, top-5 most frequent "
        "characters, a category-So has_emoji heuristic flag and the "
        "control-character count."
    )

    MODES: ClassVar[tuple] = ("blocks", "categories", "summary")
    TOP_CHARS: ClassVar[int] = 5

    # Human-readable labels for the Unicode general categories.
    CATEGORY_LABELS: ClassVar[Dict[str, str]] = {
        "Lu": "Uppercase Letter",
        "Ll": "Lowercase Letter",
        "Lt": "Titlecase Letter",
        "Lm": "Modifier Letter",
        "Lo": "Other Letter",
        "Mn": "Nonspacing Mark",
        "Mc": "Spacing Combining Mark",
        "Me": "Enclosing Mark",
        "Nd": "Decimal Number",
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

    # Human-readable labels for the one-letter category groups.
    GROUP_LABELS: ClassVar[Dict[str, str]] = {
        "L": "Letter",
        "M": "Mark",
        "N": "Number",
        "P": "Punctuation",
        "S": "Symbol",
        "Z": "Separator",
        "C": "Other",
    }

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(self, mode: Any = None, text: Any = None) -> Dict[str, Any]:
        """Run one character-set analysis.

        Args:
            mode (str): One of ``blocks`` / ``categories`` / ``summary``
                (lowercase only — the mode selector is matched
                strictly, so ``"BLOCKS"`` is rejected with a clear
                error listing the valid values).
            text (str): The text to profile. Required — a non-empty
                string of at most ``max_text_chars`` characters.
                Profiling an empty string is a caller error by
                convention with the other text tools.

        Returns:
            Dict[str, Any]: The profiling result. ``blocks`` returns
            ``total_chars``, ``distinct_blocks`` and ``blocks`` rows
            (``block`` / ``count`` / ``percent``, sorted by count
            descending then name ascending); ``categories`` returns
            ``total_chars``, ``categories`` rows (``category`` /
            ``label`` / ``count`` / ``percent``, sorted by count
            descending then category code ascending) and ``groups``
            one-letter subtotals; ``summary`` returns ``total_chars``,
            ``ascii_only``, ``latin1_only``, ``distinct_chars``,
            ``top_chars`` (up to five rows sorted by count descending
            then code point ascending), ``has_emoji`` and
            ``control_char_count``.

        Raises:
            ValueError: If any parameter is malformed (before any
            computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} "
                f"(lowercase only, got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "blocks":
            return self._run_blocks(clean_text)
        if mode == "categories":
            return self._run_categories(clean_text)
        return self._run_summary(clean_text)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"character_set_analyzer_tool: {message}")

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
    # blocks mode
    # ------------------------------------------------------------------ #

    def _run_blocks(self, text: str) -> Dict[str, Any]:
        """Count characters per Unicode block (compact table lookup)."""
        tally: Dict[str, int] = {}
        for char in text:
            block = lookup_block(ord(char))
            tally[block] = tally.get(block, 0) + 1
        total = len(text)
        rows = self._sorted_rows(
            tally, total, key_name="block", tie_break=lambda name: name
        )
        return {
            "mode": "blocks",
            "total_chars": total,
            "distinct_blocks": len(rows),
            "blocks": rows,
        }

    # ------------------------------------------------------------------ #
    # categories mode
    # ------------------------------------------------------------------ #

    def _run_categories(self, text: str) -> Dict[str, Any]:
        """Count characters per Unicode general category + groups."""
        tally: Dict[str, int] = {}
        for char in text:
            category = unicodedata.category(char)
            tally[category] = tally.get(category, 0) + 1
        total = len(text)
        rows = [
            {
                "category": category,
                "label": self.CATEGORY_LABELS.get(category, "Unknown"),
                "count": count,
                "percent": round(count * 100.0 / total, 2),
            }
            for category, count in tally.items()
        ]
        rows.sort(key=lambda row: (-row["count"], row["category"]))

        groups: Dict[str, int] = {}
        for category, count in tally.items():
            group = category[0]
            groups[group] = groups.get(group, 0) + count
        group_rows = [
            {
                "group": group,
                "label": self.GROUP_LABELS.get(group, "Unknown"),
                "count": count,
                "percent": round(count * 100.0 / total, 2),
            }
            for group, count in groups.items()
        ]
        group_rows.sort(key=lambda row: (-row["count"], row["group"]))
        return {
            "mode": "categories",
            "total_chars": total,
            "categories": rows,
            "groups": group_rows,
        }

    # ------------------------------------------------------------------ #
    # summary mode
    # ------------------------------------------------------------------ #

    def _run_summary(self, text: str) -> Dict[str, Any]:
        """Compute the quick fingerprint flags of the text."""
        frequency: Dict[str, int] = {}
        control_count = 0
        has_emoji = False
        max_code = 0
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
            code = ord(char)
            if code > max_code:
                max_code = code
            category = unicodedata.category(char)
            if category == "Cc":
                control_count += 1
            elif category == "So":
                # Heuristic: most pictographic emoji carry category So.
                has_emoji = True
        top = sorted(frequency.items(), key=lambda item: (-item[1], ord(item[0])))
        return {
            "mode": "summary",
            "total_chars": len(text),
            "ascii_only": max_code < 0x80,
            "latin1_only": max_code <= 0xFF,
            "distinct_chars": len(frequency),
            "top_chars": [
                {"char": char, "codepoint": ord(char), "count": count}
                for char, count in top[: self.TOP_CHARS]
            ],
            "has_emoji": has_emoji,
            "control_char_count": control_count,
        }

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _sorted_rows(
        tally: Dict[str, int],
        total: int,
        key_name: str,
        tie_break,
    ) -> List[Dict[str, Any]]:
        """Build ``{key, count, percent}`` rows sorted count desc."""
        rows = [
            {
                key_name: name,
                "count": count,
                "percent": round(count * 100.0 / total, 2),
            }
            for name, count in tally.items()
        ]
        rows.sort(key=lambda row: (-row["count"], tie_break(row[key_name])))
        return rows
