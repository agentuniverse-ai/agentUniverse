#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: markdown_table_validator_tool.py

"""GFM pipe-table validation / repair tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency table checker agents
can call before pasting generated Markdown into issues, READMEs or
review comments. It complements the other members of the table tool
family: MarkdownTableExtractorTool parses table *content* out of
documents and AsciiTableTool *renders* matrices, while this tool
verifies that a table already written in Markdown has the correct
GitHub-flavoured pipe-table shape — and can repair the common shape
mistakes.

Tables are detected the way GitHub-flavoured Markdown sees them:
maximal groups of consecutive non-blank lines (outside fenced code
blocks) in which at least one line contains an unescaped pipe. Fenced
code (``` or ~~~) is fully immune — pipe-heavy lines inside a fence are
never treated as table rows, and a fence terminates any adjacent table
group. An escaped pipe (``\\|``) is cell *content*, never a separator,
so it does not inflate the cell count.

Three modes are supported:

* ``validate`` — returns one finding list per table. Error-severity
  findings: ``column_count_mismatch`` (a row whose pipe-cell count
  differs from the header count, with the row number and both counts),
  ``missing_alignment_row`` (the header is not followed by a
  ``|---|---|`` delimiter row), ``invalid_alignment_row`` (a delimiter
  row cell using characters or structure other than one dash run with
  optional single colons) and ``ragged_alignment`` (delimiter row cell
  count differs from the header count). Info-severity findings (GFM
  tolerates them, but they are flagged): ``unclosed_edge`` (a row
  missing its leading or trailing pipe) and ``empty_header_cell`` /
  ``empty_body_cell``. Each table gets a verdict of ``valid``,
  ``warnings`` (info findings only) or ``errors``, plus a row/column
  summary.

  A second table row counts as the alignment row when it consists only
  of pipes, dashes, colons and whitespace; a row containing any other
  character is ordinary body content, so ``| 1 | 2 |`` after the header
  yields ``missing_alignment_row`` while ``| --- | :-x |`` yields
  ``invalid_alignment_row``.

* ``fix`` — repairs the markdown and returns it. ``fix_modes`` selects
  the repairs: ``pad_short_rows`` (right-pad short rows with empty
  cells), ``drop_mismatched_rows`` (delete body rows whose cell count
  still differs from the header) and ``add_missing_alignment_row``
  (insert a ``| :--- | :--- |`` delimiter row after a header that lacks
  one). All three are enabled by default; every finding that would
  still stand after the requested repairs is reported as an unfixable
  issue alongside the repaired text. Untouched rows and all non-table
  content pass through byte-exact.
* ``stats`` — table count, per-table shapes (``rows x cols``), the
  maximum column count and the total cell count.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, blank or oversized markdown, an
unknown mode, an unknown / wrongly typed / empty / duplicated
``fix_modes`` entry) raise a ``ValueError``, mirroring the other
common tools. The tool never raises for problems found *in the
document* — those are the findings it reports.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# A valid delimiter-row cell: optional spaces, an optional ':', at
# least one '-', an optional ':' and optional spaces — nothing else.
_ALIGNMENT_CELL = re.compile(r"\A\s*:?-+:?\s*\Z")
# A delimiter row may consist only of pipes, dashes, colons, whitespace
# and the backslashes of escaped pipes.
_ALIGNMENT_CHARS = re.compile(r"\A[-:|\s\\]+\Z")
# Fence opening: three or more backticks or tildes, optionally indented
# (an info string may follow, e.g. ```python).
_FENCE_OPEN = re.compile(r"\A\s*(`{3,}|~{3,})")

ERROR = "error"
INFO = "info"

# Severity of each finding type — errors break the table shape, info
# findings are style issues GFM tolerates.
FINDING_SEVERITY: Dict[str, str] = {
    "column_count_mismatch": ERROR,
    "missing_alignment_row": ERROR,
    "invalid_alignment_row": ERROR,
    "ragged_alignment": ERROR,
    "unclosed_edge": INFO,
    "empty_header_cell": INFO,
    "empty_body_cell": INFO,
}

VALID_MODES = ("validate", "fix", "stats")
FIX_MODES = ("pad_short_rows", "drop_mismatched_rows", "add_missing_alignment_row")


def _split_unescaped_pipes(line: str) -> List[str]:
    """Split ``line`` on pipes, treating ``\\|`` as literal content."""
    parts: List[str] = []
    current: List[str] = []
    index = 0
    while index < len(line):
        char = line[index]
        if char == "\\" and index + 1 < len(line) and line[index + 1] == "|":
            current.append("\\|")
            index += 2
            continue
        if char == "|":
            parts.append("".join(current))
            current = []
            index += 1
            continue
        current.append(char)
        index += 1
    parts.append("".join(current))
    return parts


def _starts_with_pipe(line: str) -> bool:
    """Return True if the first non-space character of ``line`` is ``|``."""
    return line.lstrip().startswith("|")


def _ends_with_unescaped_pipe(line: str) -> bool:
    """Return True if the last non-space char of ``line`` is an unescaped ``|``."""
    stripped = line.rstrip()
    if not stripped.endswith("|"):
        return False
    backslashes = 0
    index = len(stripped) - 2
    while index >= 0 and stripped[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 0


def _has_unescaped_pipe(line: str) -> bool:
    """Return True if ``line`` contains at least one unescaped pipe."""
    index = 0
    while index < len(line):
        if line[index] == "\\":
            index += 2
            continue
        if line[index] == "|":
            return True
        index += 1
    return False


def _row_cells(line: str) -> Tuple[List[str], bool, bool]:
    """Return ``(cells, has_leading_pipe, has_trailing_pipe)`` for a row.

    Cells keep their raw (unstripped) content so fixes can preserve the
    original text; edge pipes are excluded from the returned cell list,
    following the GFM table-row algorithm: the empty fragment before a
    leading pipe and after a trailing pipe is not a cell.
    """
    parts = _split_unescaped_pipes(line)
    has_leading = _starts_with_pipe(line)
    has_trailing = _ends_with_unescaped_pipe(line)
    if has_leading and parts:
        parts = parts[1:]
    if has_trailing and parts:
        parts = parts[:-1]
    return parts, has_leading, has_trailing


class _Row:
    """One physical line acting as a table row candidate."""

    __slots__ = ("line", "line_number", "row_number", "cells", "leading", "trailing")

    def __init__(self, line: str, line_number: int, row_number: int = 0) -> None:
        self.line = line
        self.line_number = line_number
        self.row_number = row_number
        self.cells, self.leading, self.trailing = _row_cells(line)

    @property
    def cell_count(self) -> int:
        return len(self.cells)

    def is_alignment_like(self) -> bool:
        """Return True if the row looks like a delimiter row at all.

        A delimiter-like row consists only of pipes, dashes, colons,
        whitespace and escaped pipes. Whether its cells are *valid*
        delimiter cells is a separate check (``bad_alignment_cells``).
        """
        return bool(_ALIGNMENT_CHARS.match(self.line))

    def bad_alignment_cells(self) -> List[int]:
        """Return the indexes of cells that fail the delimiter syntax."""
        return [
            index
            for index, cell in enumerate(self.cells)
            if not _ALIGNMENT_CELL.match(cell)
        ]


class _Table:
    """A block of consecutive lines detected as a GFM pipe table."""

    __slots__ = ("rows", "start_line", "end_line", "header", "alignment", "body")

    def __init__(self, rows: List[_Row], start_line: Optional[int] = None) -> None:
        self.rows = rows
        self.start_line = rows[0].line_number if start_line is None else start_line
        self.end_line = self.start_line + len(rows) - 1
        self.header = rows[0]
        second = rows[1] if len(rows) > 1 else None
        if second is not None and second.is_alignment_like():
            self.alignment = second
            self.body = rows[2:]
        else:
            self.alignment = None
            self.body = rows[1:]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        return self.header.cell_count


def _find_fenced_regions(lines: List[str]) -> List[bool]:
    """Mark each line that is part of a fenced code block (``` or ~~~)."""
    in_fence = [False] * len(lines)
    fence_char = ""
    fence_length = 0
    is_open = False
    for index, line in enumerate(lines):
        if is_open:
            in_fence[index] = True
            stripped = line.strip()
            if (
                stripped
                and stripped[0] == fence_char
                and set(stripped) == {fence_char}
                and len(stripped) >= fence_length
            ):
                is_open = False
            continue
        match = _FENCE_OPEN.match(line)
        if match:
            fence = match.group(1)
            fence_char = fence[0]
            fence_length = len(fence)
            is_open = True
            in_fence[index] = True
    return in_fence


def _find_tables(markdown: str) -> Tuple[List[_Table], List[_Row]]:
    """Detect pipe tables and return ``(tables, non_table_lines)``.

    ``non_table_lines`` carries every line that is NOT part of a table
    (blank separators, fence content, plain paragraphs) in document
    order, so the fix mode can rebuild the document exactly.
    """
    lines = markdown.split("\n")
    fenced = _find_fenced_regions(lines)
    tables: List[_Table] = []
    others: List[_Row] = []
    block: List[_Row] = []

    def flush() -> None:
        nonlocal block
        if not block:
            return
        if any(_has_unescaped_pipe(row.line) for row in block):
            tables.append(_Table(block))
        else:
            others.extend(block)
        block = []

    for index, line in enumerate(lines):
        line_number = index + 1
        if fenced[index] or not line.strip():
            flush()
            others.append(_Row(line, line_number))
            continue
        block.append(_Row(line, line_number, len(block) + 1))
    flush()
    return tables, others


def _finding(
    finding_type: str, message: str, row: Optional[_Row] = None, **extra: Any
) -> Dict[str, Any]:
    """Build one finding record with its severity and location."""
    record: Dict[str, Any] = {
        "type": finding_type,
        "severity": FINDING_SEVERITY[finding_type],
    }
    if row is not None:
        record["row"] = row.row_number
        record["line"] = row.line_number
    record.update(extra)
    record["message"] = message
    return record


class MarkdownTableValidatorTool(Tool):
    """GFM pipe-table shape validation / repair tool (pure stdlib).

    Attributes:
        max_markdown_chars (int): Upper bound on the ``markdown``
            input length; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "markdown_table_validator_tool"
    description: str = (
        "Markdown GFM pipe-table validator — pure Python stdlib, no "
        "network required. validate mode checks each pipe table for "
        "column count mismatches, missing / invalid / ragged alignment "
        "rows, unclosed edge pipes and empty cells (escaped \\| counts "
        "as content, never as a separator); fix mode repairs short rows "
        "(padding), mismatched rows (dropping) and missing alignment "
        "rows (inserting | :--- |); stats mode reports table count, "
        "shapes, max columns and total cells. Fenced code blocks are "
        "never treated as tables."
    )

    MODES: ClassVar[tuple] = VALID_MODES
    FIX_MODES: ClassVar[tuple] = FIX_MODES

    max_markdown_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        markdown: Any = None,
        fix_modes: Any = None,
    ) -> Dict[str, Any]:
        """Run one table-validation operation.

        Args:
            mode (str): One of ``validate`` / ``fix`` / ``stats``.
            markdown (str): The Markdown document to check. Required
                for every mode.
            fix_modes (list[str]): Fix mode only — a subset of
                ``pad_short_rows`` / ``drop_mismatched_rows`` /
                ``add_missing_alignment_row``; defaults to all three.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the call context): per-table findings for
                ``validate``, the repaired document for ``fix`` and the
                numeric summary for ``stats``.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode is None:
            mode = "validate"
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_markdown = self._validate_markdown(markdown)
        if mode == "stats":
            return self._run_stats(clean_markdown)
        if mode == "fix":
            clean_fix_modes = self._validate_fix_modes(fix_modes)
            return self._run_fix(clean_markdown, clean_fix_modes)
        return self._run_validate(clean_markdown)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"markdown_table_validator_tool: {message}")

    @classmethod
    def _validate_markdown(cls, markdown: Any) -> str:
        """Validate the ``markdown`` document input."""
        if (
            markdown is None
            or isinstance(markdown, bool)
            or not isinstance(markdown, str)
        ):
            cls._invalid(
                f"markdown must be a non-empty string (got {markdown!r})"
            )
        if not markdown.strip():
            cls._invalid("markdown must be a non-empty string (got blank text)")
        if len(markdown) > 100_000:
            cls._invalid(
                f"markdown exceeds the {100_000:,}-character "
                f"limit (got {len(markdown):,} characters)"
            )
        return markdown

    @classmethod
    def _validate_fix_modes(cls, fix_modes: Any) -> Tuple[str, ...]:
        """Validate the fix-mode ``fix_modes`` selector list."""
        if fix_modes is None:
            return FIX_MODES
        if isinstance(fix_modes, (str, bool)) or not isinstance(
            fix_modes, (list, tuple, set)
        ):
            cls._invalid(
                "fix_modes must be a list drawn from: "
                f"{', '.join(FIX_MODES)} (got {fix_modes!r})"
            )
        entries = list(fix_modes)
        if not entries:
            cls._invalid(
                "fix_modes must be a non-empty list drawn from: "
                f"{', '.join(FIX_MODES)} (got [])"
            )
        seen = set()
        for entry in entries:
            if entry not in FIX_MODES:
                cls._invalid(
                    "fix_modes entries must come from: "
                    f"{', '.join(FIX_MODES)} (got {entry!r})"
                )
            if entry in seen:
                cls._invalid(
                    f"fix_modes contains a duplicate entry (got {entry!r})"
                )
            seen.add(entry)
        # Canonical application order, independent of the input order.
        return tuple(entry for entry in FIX_MODES if entry in seen)

    # ------------------------------------------------------------------ #
    # Finding collection (shared by validate and fix)
    # ------------------------------------------------------------------ #

    @classmethod
    def _collect_findings(cls, table: _Table) -> List[Dict[str, Any]]:
        """Return every finding for one table, in scan order."""
        findings: List[Dict[str, Any]] = []
        expected = table.column_count

        # --- alignment row ----------------------------------------------
        if table.alignment is None:
            findings.append(
                _finding(
                    "missing_alignment_row",
                    "table header is not followed by a |---|---| "
                    "alignment row",
                    row=table.header,
                )
            )
        else:
            alignment = table.alignment
            if alignment.cell_count != expected:
                findings.append(
                    _finding(
                        "ragged_alignment",
                        f"alignment row has {alignment.cell_count} cells "
                        f"but the header has {expected}",
                        row=alignment,
                        expected=expected,
                        actual=alignment.cell_count,
                    )
                )
            for index in alignment.bad_alignment_cells():
                findings.append(
                    _finding(
                        "invalid_alignment_row",
                        f"alignment row cell {index + 1} uses invalid "
                        "syntax — only '-', ':' and spaces arranged as an "
                        "optional ':', a dash run and an optional ':' are "
                        "allowed",
                        row=alignment,
                        cell=index + 1,
                    )
                )

        # --- header row --------------------------------------------------
        for index, cell in enumerate(table.header.cells):
            if not cell.strip():
                findings.append(
                    _finding(
                        "empty_header_cell",
                        f"header cell {index + 1} is empty",
                        row=table.header,
                        cell=index + 1,
                    )
                )

        # --- body rows -----------------------------------------------------
        for row in table.body:
            if row.cell_count != expected:
                findings.append(
                    _finding(
                        "column_count_mismatch",
                        f"row {row.row_number} has {row.cell_count} "
                        f"pipe-separated cells but the header has "
                        f"{expected}",
                        row=row,
                        expected=expected,
                        actual=row.cell_count,
                    )
                )
            for index, cell in enumerate(row.cells):
                if not cell.strip():
                    findings.append(
                        _finding(
                            "empty_body_cell",
                            f"row {row.row_number} cell {index + 1} is empty",
                            row=row,
                            cell=index + 1,
                        )
                    )

        # --- edge pipes (every row of the table) ---------------------
        for row in table.rows:
            if not row.leading:
                findings.append(
                    _finding(
                        "unclosed_edge",
                        f"row {row.row_number} is missing its leading pipe "
                        "(GFM tolerates this)",
                        row=row,
                        edge="leading",
                    )
                )
            if not row.trailing:
                findings.append(
                    _finding(
                        "unclosed_edge",
                        f"row {row.row_number} is missing its trailing "
                        "pipe (GFM tolerates this)",
                        row=row,
                        edge="trailing",
                    )
                )
        return findings

    @staticmethod
    def _verdict(findings: List[Dict[str, Any]]) -> str:
        """Collapse findings into the per-table verdict."""
        if any(finding["severity"] == ERROR for finding in findings):
            return "errors"
        if findings:
            return "warnings"
        return "valid"

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(self, markdown: str) -> Dict[str, Any]:
        """Validate every table and report per-table findings."""
        tables, _ = _find_tables(markdown)
        reports = []
        summary = {"valid": 0, "warnings": 0, "errors": 0}
        for index, table in enumerate(tables, start=1):
            findings = self._collect_findings(table)
            verdict = self._verdict(findings)
            summary[verdict] += 1
            reports.append(
                {
                    "table": index,
                    "verdict": verdict,
                    "row_count": table.row_count,
                    "column_count": table.column_count,
                    "line_start": table.start_line,
                    "line_end": table.end_line,
                    "findings": findings,
                }
            )
        error_findings = sum(
            1
            for report in reports
            for finding in report["findings"]
            if finding["severity"] == ERROR
        )
        result = (
            f"validated {len(tables)} table(s): {summary['valid']} valid, "
            f"{summary['warnings']} with warnings, {summary['errors']} with "
            f"errors ({error_findings} error findings)"
        )
        return {
            "mode": "validate",
            "table_count": len(tables),
            "summary": summary,
            "tables": reports,
            "result": result,
        }

    # ------------------------------------------------------------------ #
    # fix mode
    # ------------------------------------------------------------------ #

    def _run_fix(self, markdown: str, fix_modes: Tuple[str, ...]) -> Dict[str, Any]:
        """Repair the requested shape issues and rebuild the document.

        Fixes are applied per table in a fixed order: the missing
        alignment row is inserted first, then short body rows are
        padded, then body rows still mismatching the header column
        count are dropped. Rows are only ever rewritten when a fix
        actually touches them; every other line passes through
        unchanged, so untouched content stays byte-exact.
        """
        tables, _ = _find_tables(markdown)
        # line number -> replacement text; the empty string marks a
        # dropped line, a value containing "\n" an inserted line.
        updates: Dict[int, str] = {}
        applied: List[Dict[str, Any]] = []
        remaining: List[Dict[str, Any]] = []
        line_offset = 0

        for index, table in enumerate(tables, start=1):
            start_line = table.start_line + line_offset

            # 1. Insert the missing alignment row after the header.
            if (
                table.alignment is None
                and "add_missing_alignment_row" in fix_modes
                and table.header.line_number not in updates
            ):
                columns = table.column_count
                delimiter = "| " + " | ".join([":---"] * columns) + " |"
                updates[table.header.line_number] = (
                    table.header.line + "\n" + delimiter
                )
                applied.append(
                    {
                        "table": index,
                        "fix": "add_missing_alignment_row",
                        "line": start_line,
                        "detail": f"inserted a {columns}-cell alignment row",
                    }
                )

            # 2. Pad short body rows up to the header column count.
            if "pad_short_rows" in fix_modes:
                for row in table.body:
                    if (
                        row.cell_count < table.column_count
                        and row.line_number not in updates
                    ):
                        cells = [cell.strip() for cell in row.cells]
                        cells += [""] * (table.column_count - len(cells))
                        updates[row.line_number] = self._rebuild_row(
                            row, cells, ensure_trailing=True
                        )
                        applied.append(
                            {
                                "table": index,
                                "fix": "pad_short_rows",
                                "line": row.line_number + line_offset,
                                "detail": (
                                    f"padded row {row.row_number} from "
                                    f"{row.cell_count} to "
                                    f"{table.column_count} cells"
                                ),
                            }
                        )

            # 3. Drop body rows still mismatching the header count.
            if "drop_mismatched_rows" in fix_modes:
                for row in table.body:
                    if (
                        row.cell_count != table.column_count
                        and row.line_number not in updates
                    ):
                        updates[row.line_number] = ""
                        applied.append(
                            {
                                "table": index,
                                "fix": "drop_mismatched_rows",
                                "line": row.line_number + line_offset,
                                "detail": (
                                    f"dropped row {row.row_number} with "
                                    f"{row.cell_count} cells (header has "
                                    f"{table.column_count})"
                                ),
                            }
                        )

            # 4. Recompute the findings on the post-fix table rows:
            #    whatever still stands is an unfixable issue.
            after_rows = self._rows_after_fix(table, updates, start_line)
            if after_rows:
                after_table = _Table(after_rows)
                for finding in self._collect_findings(after_table):
                    remaining.append({"table": index, **finding})
                line_offset += len(after_rows) - table.row_count

        # Rebuild the document: updated lines are replaced (or removed),
        # everything else passes through untouched.
        lines = markdown.split("\n")
        output_lines: List[str] = []
        for line_number, line in enumerate(lines, start=1):
            replacement = updates.get(line_number)
            if replacement is None:
                output_lines.append(line)
            elif replacement == "":
                continue
            else:
                output_lines.append(replacement)
        repaired_markdown = "\n".join(output_lines)

        result = (
            f"repaired {len(tables)} table(s): {len(applied)} fix(es) "
            f"applied, {len(remaining)} unfixable issue(s) remain"
        )
        return {
            "mode": "fix",
            "fix_modes": list(fix_modes),
            "table_count": len(tables),
            "fixes_applied": applied,
            "unfixable_issues": remaining,
            "result": repaired_markdown,
        }

    @staticmethod
    def _rebuild_row(row: _Row, cells: List[str], ensure_trailing: bool = False) -> str:
        """Rebuild a row from stripped cells, preserving its pipe edges.

        ``ensure_trailing`` forces a trailing pipe: a trailing empty
        padding cell is invisible without one, so padded rows must
        always end with a pipe for the fix to survive re-parsing.
        """
        joined = " | ".join(cells)
        prefix = "| " if row.leading else ""
        suffix = " |" if (row.trailing or ensure_trailing) else ""
        return f"{prefix}{joined}{suffix}"

    @staticmethod
    def _rows_after_fix(
        table: _Table, updates: Dict[int, str], start_line: int
    ) -> List[_Row]:
        """Materialise the table rows after the applied fixes.

        Rows are renumbered sequentially from ``start_line`` so the
        row and line numbers of the remaining findings describe the
        *repaired* document.
        """
        rows: List[_Row] = []
        for row in table.rows:
            replacement = updates.get(row.line_number)
            if replacement == "":
                continue
            pieces = [row.line] if replacement is None else replacement.split("\n")
            for piece in pieces:
                rows.append(_Row(piece, start_line))
                start_line += 1
        for index, row in enumerate(rows, start=1):
            row.row_number = index
        return rows

    # ------------------------------------------------------------------ #
    # stats mode
    # ------------------------------------------------------------------ #

    def _run_stats(self, markdown: str) -> Dict[str, Any]:
        """Summarise the tables found in the document."""
        tables, _ = _find_tables(markdown)
        shapes = [f"{table.row_count}x{table.column_count}" for table in tables]
        max_cols = max((table.column_count for table in tables), default=0)
        total_cells = sum(
            row.cell_count for table in tables for row in table.rows
        )
        result = (
            f"{len(tables)} table(s), max {max_cols} column(s), "
            f"{total_cells} cell(s) total"
        )
        return {
            "mode": "stats",
            "table_count": len(tables),
            "shapes": shapes,
            "max_cols": max_cols,
            "total_cells": total_cells,
            "result": result,
        }
