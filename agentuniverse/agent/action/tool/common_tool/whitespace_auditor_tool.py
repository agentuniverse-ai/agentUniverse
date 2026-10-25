#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: whitespace_auditor_tool.py

"""Report-only whitespace hygiene analysis tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency whitespace auditor
agents can call on arbitrary text before deciding what to do with it.

The tool NEVER modifies the text: every mode only counts, locates and
plans. This complements the ``TextNormalizer`` knowledge doc processor
(PR #3490), which *fixes* whitespace inside the knowledge-store
pipeline — ``WhitespaceAuditorTool`` audits any text a caller hands it
and returns a report, leaving the input byte-for-byte untouched.

Lines are split on ``LF`` (``\\n``), ``CRLF`` (``\\r\\n``) and lone
``CR`` (``\\r``) only; other characters are line content. Line numbers
are 1-based, character offsets are 0-based (a leading BOM occupies
offset 0). Three modes are supported:

* ``audit`` — full counts with the first three positions per category:
  trailing-space lines (line content ending with U+0020 or U+0009),
  leading-space lines (line content starting with U+0020), total tab
  characters anywhere, lines whose leading whitespace mixes tabs and
  spaces, CRLF / LF / CR line-ending counts plus a mixed-endings flag,
  non-breaking space (U+00A0), ideographic space (U+3000) and
  zero-width space (U+200B) character counts, runs of three or more
  consecutive blank lines, a final-newline flag and a BOM flag, plus a
  ``total_issues`` tally and a ``clean`` verdict.
* ``fix_preview`` — the same categories mapped to a change plan: for
  each category, how many lines / characters / endings *would* change
  if the text were normalized (trailing whitespace stripped, leading
  spaces removed, tabs converted, mixed indentation normalized, CR and
  CRLF rewritten to LF, invisible spaces replaced or removed, blank
  runs collapsed to a single blank line, final newline appended, BOM
  stripped). No text is ever returned — only the arithmetic.
* ``locate`` — all positions (capped at 100) of one category, selected
  by its whitelisted name.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text, text over the character
limit, unknown mode, or a ``locate`` category that is not one of the
locatable names — the three flags carry no positions) raise a
``ValueError``, mirroring the other common tools.
"""

from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_TRAILING_CHARS = (" ", "\t")
_LEADING_CHAR = " "


class WhitespaceAuditorTool(Tool):
    """Report-only whitespace hygiene analysis for arbitrary text.

    The tool never modifies its input; ``audit`` counts whitespace
    issues, ``fix_preview`` computes what a normalization *would*
    change, and ``locate`` lists the positions of one category.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "whitespace_auditor_tool"
    description: str = (
        "Whitespace auditor tool — pure Python stdlib, no network "
        "required, and strictly report-only (the input text is never "
        "modified or returned). mode='audit' counts whitespace hygiene "
        "issues with the first three positions per category (trailing-"
        "space lines, leading-space lines, tab characters, mixed "
        "tab+space indentation lines, CRLF/LF/CR line-ending counts "
        "with a mixed-endings flag, non-breaking space U+00A0, "
        "ideographic space U+3000 and zero-width space U+200B counts, "
        "runs of 3+ consecutive blank lines, final-newline flag, BOM "
        "flag), mode='fix_preview' returns the same categories as a "
        "change plan of what normalization WOULD alter (no text "
        "returned), and mode='locate' lists all positions (capped at "
        "100) of one whitelisted category."
    )

    MODES: ClassVar[tuple] = ("audit", "fix_preview", "locate")
    # Line-ending kinds tracked by the ending categories.
    ENDINGS: ClassVar[tuple] = ("crlf", "lf", "cr")
    # The three boolean flags carry no positions and are not locatable.
    FLAG_CATEGORIES: ClassVar[tuple] = (
        "mixed_line_endings",
        "final_newline",
        "bom",
    )
    # Category name -> position semantics ("line" = 1-based line
    # number, "offset" = 0-based character offset).
    CATEGORY_KINDS: ClassVar[dict] = {
        "trailing_space": "line",
        "leading_space": "line",
        "tabs": "offset",
        "mixed_indent": "line",
        "crlf": "line",
        "lf": "line",
        "cr": "line",
        "nbsp": "offset",
        "ideographic_space": "offset",
        "zero_width_space": "offset",
        "blank_run": "line",
    }
    LOCATE_CATEGORIES: ClassVar[tuple] = tuple(CATEGORY_KINDS)
    # Number of positions shown per category in the audit report.
    AUDIT_PREVIEW: ClassVar[int] = 3
    # Upper bound on the positions returned by locate mode.
    LOCATE_CAP: ClassVar[int] = 100
    # A blank-line run only counts once it reaches this length.
    BLANK_RUN_MIN: ClassVar[int] = 3

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        category: Any = None,
    ) -> dict[str, Any]:
        """Run one whitespace audit operation.

        Args:
            mode (str): One of ``audit`` / ``fix_preview`` / ``locate``.
            text (str): The text to analyse. Required by every mode and
                never modified, never returned.
            category (str): ``locate`` mode only — one of the
                locatable category names (the count categories; the
                ``mixed_line_endings`` / ``final_newline`` / ``bom``
                flags carry no positions and are rejected).

        Returns:
            Dict[str, Any]: The audit report, the fix-preview change
                plan, or the locate position list (see the module
                docstring for the exact shapes).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "locate":
            clean_category = self._validate_category(category)
            return self._run_locate(clean_text, clean_category)
        analysis = self._analyze(clean_text)
        if mode == "audit":
            return self._build_audit(clean_text, analysis)
        return self._build_fix_preview(clean_text, analysis)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"whitespace_auditor_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (the tool never alters it)."""
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
    def _validate_category(cls, category: Any) -> str:
        """Validate the ``locate`` category against the whitelist."""
        if (
            category is None
            or isinstance(category, bool)
            or not isinstance(category, str)
        ):
            cls._invalid(
                "category must be one of: "
                f"{', '.join(cls.LOCATE_CATEGORIES)} (got {category!r})"
            )
        if category in cls.FLAG_CATEGORIES:
            cls._invalid(
                f"category {category!r} is a boolean flag without "
                "positions; locatable categories are: "
                f"{', '.join(cls.LOCATE_CATEGORIES)}"
            )
        if category not in cls.CATEGORY_KINDS:
            cls._invalid(
                "category must be one of: "
                f"{', '.join(cls.LOCATE_CATEGORIES)} (got {category!r})"
            )
        return category

    # ------------------------------------------------------------------ #
    # Analysis (single deterministic scan — the text is only read)
    # ------------------------------------------------------------------ #

    @classmethod
    def _split_lines(cls, text: str) -> list[tuple[str, str]]:
        """Split text into ``(content, ending)`` pairs.

        Lines are terminated by ``\\n``, ``\\r\\n`` or a lone ``\\r``;
        the ending is ``""`` for a final unterminated line.
        """
        lines: list[tuple[str, str]] = []
        start = 0
        index = 0
        length = len(text)
        while index < length:
            char = text[index]
            if char == "\n":
                lines.append((text[start:index], "\n"))
                index += 1
                start = index
            elif char == "\r":
                if index + 1 < length and text[index + 1] == "\n":
                    lines.append((text[start:index], "\r\n"))
                    index += 2
                else:
                    lines.append((text[start:index], "\r"))
                    index += 1
                start = index
            else:
                index += 1
        if start < length:
            lines.append((text[start:], ""))
        return lines

    @classmethod
    def _analyze(cls, text: str) -> dict[str, Any]:
        """Count every category in one deterministic scan."""
        lines = cls._split_lines(text)

        trailing_lines: list[int] = []
        leading_lines: list[int] = []
        mixed_lines: list[int] = []
        ending_lines: dict[str, list[int]] = {
            "crlf": [],
            "lf": [],
            "cr": [],
        }
        blank_run_starts: list[int] = []
        blank_run_lengths: list[int] = []
        blank_run: int = 0

        for number, (content, ending) in enumerate(lines, start=1):
            if content.endswith(_TRAILING_CHARS):
                trailing_lines.append(number)
            if content.startswith(_LEADING_CHAR):
                leading_lines.append(number)
            stripped = content.lstrip(" \t")
            indent = content[: len(content) - len(stripped)]
            if " " in indent and "\t" in indent:
                mixed_lines.append(number)
            if ending:
                kind = "crlf" if ending == "\r\n" else "lf" if ending == "\n" else "cr"
                ending_lines[kind].append(number)
            if not content.strip():
                blank_run += 1
            else:
                if blank_run >= cls.BLANK_RUN_MIN:
                    blank_run_starts.append(number - blank_run)
                    blank_run_lengths.append(blank_run)
                blank_run = 0
        # A blank run that reaches the end of the text counts too.
        if blank_run >= cls.BLANK_RUN_MIN:
            blank_run_starts.append(len(lines) - blank_run + 1)
            blank_run_lengths.append(blank_run)

        tab_offsets = [i for i, char in enumerate(text) if char == "\t"]
        nbsp_offsets = [i for i, char in enumerate(text) if char == "\u00a0"]
        ideographic_offsets = [i for i, char in enumerate(text) if char == "\u3000"]
        zero_width_offsets = [i for i, char in enumerate(text) if char == "\u200b"]

        ending_counts = {kind: len(ending_lines[kind]) for kind in cls.ENDINGS}
        distinct_endings = sum(1 for kind in cls.ENDINGS if ending_counts[kind])

        return {
            "line_count": len(lines),
            "positions": {
                "trailing_space": trailing_lines,
                "leading_space": leading_lines,
                "tabs": tab_offsets,
                "mixed_indent": mixed_lines,
                "crlf": ending_lines["crlf"],
                "lf": ending_lines["lf"],
                "cr": ending_lines["cr"],
                "nbsp": nbsp_offsets,
                "ideographic_space": ideographic_offsets,
                "zero_width_space": zero_width_offsets,
                "blank_run": blank_run_starts,
            },
            "blank_run_lengths": blank_run_lengths,
            "distinct_endings": distinct_endings,
            "flags": {
                "mixed_line_endings": distinct_endings >= 2,
                "final_newline": text.endswith(("\n", "\r")),
                "bom": text.startswith("\ufeff"),
            },
        }

    # ------------------------------------------------------------------ #
    # Result builders (read-only views over the analysis)
    # ------------------------------------------------------------------ #

    @classmethod
    def _build_counts(cls, analysis: dict[str, Any]) -> dict[str, int]:
        """Per-category totals derived from the position lists."""
        return {
            category: len(analysis["positions"][category])
            for category in cls.LOCATE_CATEGORIES
        }

    @classmethod
    def _build_audit(cls, text: str, analysis: dict[str, Any]) -> dict[str, Any]:
        """Build the full audit report with first-3 position previews."""
        counts = cls._build_counts(analysis)
        flags = analysis["flags"]
        preview = {
            category: {
                "kind": cls.CATEGORY_KINDS[category],
                "first": analysis["positions"][category][: cls.AUDIT_PREVIEW],
            }
            for category in cls.LOCATE_CATEGORIES
        }
        total_issues = (
            counts["trailing_space"]
            + counts["leading_space"]
            + counts["mixed_indent"]
            + counts["nbsp"]
            + counts["ideographic_space"]
            + counts["zero_width_space"]
            + counts["blank_run"]
            + (1 if flags["mixed_line_endings"] else 0)
            + (0 if flags["final_newline"] else 1)
            + (1 if flags["bom"] else 0)
        )
        return {
            "mode": "audit",
            "text_length": len(text),
            "line_count": analysis["line_count"],
            "counts": counts,
            "flags": flags,
            "positions": preview,
            "total_issues": total_issues,
            "clean": total_issues == 0,
        }

    @classmethod
    def _build_fix_preview(
        cls, text: str, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Build the change plan of what normalization WOULD alter.

        The assumed normalization policy is documented in the module
        docstring: LF is the target line ending, runs of 3+ blank lines
        collapse to a single blank line, and every tab / invisible
        space is converted or removed. Only the arithmetic is returned
        — never any text.
        """
        counts = cls._build_counts(analysis)
        flags = analysis["flags"]
        changes = {
            "trailing_space": counts["trailing_space"],
            "leading_space": counts["leading_space"],
            "tabs": counts["tabs"],
            "mixed_indent": counts["mixed_indent"],
            "crlf": counts["crlf"],
            "lf": 0,
            "cr": counts["cr"],
            "mixed_line_endings": 1 if flags["mixed_line_endings"] else 0,
            "nbsp": counts["nbsp"],
            "ideographic_space": counts["ideographic_space"],
            "zero_width_space": counts["zero_width_space"],
            "blank_run": sum(
                length - 1 for length in analysis["blank_run_lengths"]
            ),
            "final_newline": 0 if flags["final_newline"] else 1,
            "bom": 1 if flags["bom"] else 0,
        }
        total_changes = sum(changes.values())
        return {
            "mode": "fix_preview",
            "text_length": len(text),
            "line_count": analysis["line_count"],
            "changes": changes,
            "total_changes": total_changes,
            "would_change": total_changes > 0,
        }

    @classmethod
    def _run_locate(cls, text: str, category: str) -> dict[str, Any]:
        """List every position of one category, capped at LOCATE_CAP."""
        analysis = cls._analyze(text)
        positions = analysis["positions"][category]
        shown = positions[: cls.LOCATE_CAP]
        return {
            "mode": "locate",
            "category": category,
            "kind": cls.CATEGORY_KINDS[category],
            "count": len(positions),
            "returned": len(shown),
            "truncated": len(positions) > len(shown),
            "positions": shown,
        }
