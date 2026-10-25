#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: ascii_table_tool.py

"""Table rendering tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency table renderer agents
can call to turn structured results into readable text. It pairs
naturally with the query/parse side of the tool family: CSVQueryTool
queries delimited data and MarkdownTableExtractorTool parses tables out
of documents, while this tool renders tabular data back into aligned
plain-text or Markdown tables.

The tool supports four modes:

* ``render`` — a list-of-list ``rows`` matrix (plus an optional
  ``header`` list) is rendered as a table.
* ``transpose`` — the same matrix is transposed (rows become columns,
  the header becomes the first column) and rendered headerless.
* ``from_csv`` / ``from_tsv`` — delimited text is parsed with the
  standard library ``csv`` module (strict quoting, blank lines skipped,
  ``delimiter`` overridable) and the parsed rows are rendered. By
  default the first parsed row is used as the header (``has_header``).

Four output styles are available:

* ``markdown`` (default) — a GitHub-flavoured pipe table; alignment is
  encoded in the separator row (``:--`` / ``:-:`` / ``--:``) whenever
  an explicit ``align`` is given, plain dashes otherwise.
* ``ascii`` — ``+``/``-``/``|`` box borders around the table.
* ``grid`` — the same box drawing plus a separator line between every
  row.
* ``simple`` — borderless aligned columns (two-space gutter) with a
  dash underline beneath the header.

Layout is CJK-aware: cell display width is measured with
``unicodedata.east_asian_width`` so east-asian wide (``W``) and
fullwidth (``F``) characters occupy two columns, keeping the rendered
borders aligned when CJK text is mixed with ASCII.

Options: ``align`` (global or per-column left/center/right),
``max_col_width`` (truncate overflowing cells with a trailing ``…``
ellipsis, CJK-aware) and ``ragged`` (``error`` — the default — rejects
rows of inconsistent length; ``pad`` right-pads short rows with empty
cells).

Input validation is strict and happens before any rendering: wrong
parameter types, unknown mode/style/alignment/ragged policy, a
non-integer or non-positive ``max_col_width``, an empty table, cells
that are not scalars (str/int/float/bool/None), cells containing
newline, carriage-return or tab characters, a multi-character or
quote-clashing ``delimiter``, and oversized inputs all raise a
``ValueError``, mirroring the other common tools. Content-level
failures of the delimited parsers (malformed quoting detected by the
strict ``csv`` reader) are returned as a structured ``error`` payload
so an agent can react without catching exceptions.
"""

import csv
import io
import unicodedata
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# East-asian width classes that occupy two terminal columns.
_WIDE_WIDTHS = ("W", "F")
_ELLIPSIS = "…"


def _display_width(text: str) -> int:
    """Return the terminal display width of ``text``.

    East-asian wide (``W``) and fullwidth (``F``) characters count as
    two columns, everything else (including ambiguous-width characters
    such as ``…``) as one.
    """
    return sum(
        2 if unicodedata.east_asian_width(char) in _WIDE_WIDTHS else 1
        for char in text
    )


def _pad_cell(text: str, width: int, alignment: str) -> str:
    """Pad ``text`` with spaces to ``width`` display columns."""
    pad = width - _display_width(text)
    if pad <= 0:
        return text
    if alignment == "right":
        return " " * pad + text
    if alignment == "center":
        left = pad // 2
        return " " * left + text + " " * (pad - left)
    return text + " " * pad


def _truncate_cell(text: str, limit: int) -> str:
    """Truncate ``text`` to ``limit`` display columns using a ``…`` marker."""
    if _display_width(text) <= limit:
        return text
    budget = limit - _display_width(_ELLIPSIS)
    kept: List[str] = []
    used = 0
    for char in text:
        char_width = 2 if unicodedata.east_asian_width(char) in _WIDE_WIDTHS else 1
        if used + char_width > budget:
            break
        kept.append(char)
        used += char_width
    return "".join(kept) + _ELLIPSIS


def _separator_segment(width: int, alignment: str, explicit: bool) -> str:
    """Build one Markdown separator segment for a column.

    GitHub-flavoured Markdown encodes column alignment with colons in
    the separator row. Colons are emitted only when an explicit
    ``align`` was requested; the default renders plain dashes. The
    segment spans the same ``width + 2`` display columns a rendered
    cell occupies (at least three dashes) so the pipes stay visually
    aligned with the data rows.
    """
    length = max(width + 2, 3)
    if not explicit:
        return "-" * length
    if alignment == "left":
        return ":" + "-" * (length - 1)
    if alignment == "right":
        return "-" * (length - 1) + ":"
    return ":" + "-" * (length - 2) + ":"


class AsciiTableTool(Tool):
    """Render tabular data as aligned Markdown / ASCII tables.

    Attributes:
        MAX_ROWS (int): Upper bound on the number of data rows.
        MAX_COLUMNS (int): Upper bound on the number of columns.
        MAX_CELLS (int): Upper bound on the total number of cells
            (header included).
        MAX_CELL_CHARS (int): Upper bound on the length of a single
            cell, in characters, before truncation.
        MAX_TEXT_CHARS (int): Upper bound on the length of delimited
            input text for the ``from_csv`` / ``from_tsv`` modes.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "ascii_table_tool"
    description: str = (
        "ASCII table tool — render tabular data as aligned tables, pure "
        "Python stdlib, no network required. Modes: render (list-of-list "
        "rows plus optional header), transpose (swap rows and columns), "
        "from_csv / from_tsv (parse delimited text with the stdlib csv "
        "module, delimiter option). Styles: markdown pipe table (default), "
        "ascii with +-+ borders, grid with row separators, simple aligned "
        "columns. CJK east-asian width aware (wide characters count as "
        "two columns); global or per-column left/center/right alignment "
        "and max_col_width truncation with a trailing ellipsis."
    )

    MODES: ClassVar[tuple] = ("render", "transpose", "from_tsv", "from_csv")
    STYLES: ClassVar[tuple] = ("markdown", "ascii", "grid", "simple")
    ALIGNMENTS: ClassVar[tuple] = ("left", "center", "right")
    RAGGED_POLICIES: ClassVar[tuple] = ("error", "pad")

    MAX_ROWS: ClassVar[int] = 10_000
    MAX_COLUMNS: ClassVar[int] = 1_000
    MAX_CELLS: ClassVar[int] = 100_000
    MAX_CELL_CHARS: ClassVar[int] = 10_000
    MAX_TEXT_CHARS: ClassVar[int] = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        rows: Any = None,
        header: Any = None,
        text: Any = None,
        style: Any = None,
        align: Any = None,
        max_col_width: Any = None,
        ragged: Any = None,
        delimiter: Any = None,
        has_header: Any = None,
    ) -> Dict[str, Any]:
        """Render one table.

        Args:
            mode (str): One of ``render`` / ``transpose`` / ``from_tsv`` /
                ``from_csv``.
            rows (list[list]): The row matrix (each cell a scalar:
                str / int / float / bool / None). Required for the
                ``render`` and ``transpose`` modes; not used by the
                delimited modes.
            header (list): Optional header row (same cell rules). For
                ``transpose`` it becomes the first column of the result.
            text (str): The delimited text to parse. Required for the
                ``from_csv`` / ``from_tsv`` modes.
            style (str): ``markdown`` (default), ``ascii``, ``grid`` or
                ``simple``.
            align (str | list[str]): ``left`` / ``center`` / ``right``
                globally, or one entry per column. ``None`` defaults to
                left alignment everywhere.
            max_col_width (int): Truncate cells whose display width
                exceeds this many columns, marking the cut with ``…``.
            ragged (str): ``error`` (default) rejects rows of
                inconsistent length; ``pad`` right-pads short rows with
                empty cells.
            delimiter (str): One-character field delimiter for the
                delimited modes (default ``\\t`` for ``from_tsv``, ``,``
                for ``from_csv``); must not clash with the ``"`` quote
                character.
            has_header (bool): Delimited modes only — treat the first
                parsed row as the header (default ``True``).

        Returns:
            Dict[str, Any]: The rendered table under ``result`` plus the
                call context (``mode``, ``style``, ``header``, ``rows``,
                ``columns``, and ``delimiter`` for the delimited modes),
                or a structured ``error`` payload when the delimited
                text cannot be parsed.

        Raises:
            ValueError: If any parameter or the table shape is invalid
                (before any rendering happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_style = self._validate_style(style)
        clean_align = self._validate_align(align)
        clean_max_col_width = self._validate_max_col_width(max_col_width)
        clean_ragged = self._validate_ragged(ragged)

        if mode in ("from_tsv", "from_csv"):
            default_delimiter = "\t" if mode == "from_tsv" else ","
            clean_text = self._validate_text(text)
            clean_delimiter = self._validate_delimiter(delimiter, default_delimiter)
            clean_has_header = self._validate_has_header(has_header)
            parsed = self._parse_delimited(mode, clean_text, clean_delimiter)
            if isinstance(parsed, dict):
                return parsed
            if clean_has_header:
                if len(parsed) < 2:
                    self._invalid(
                        "delimited text must contain a header row and at "
                        f"least one data row (got {len(parsed)} row(s))"
                    )
                header_cells, body_rows = parsed[0], parsed[1:]
            else:
                header_cells, body_rows = None, parsed
        else:
            header_cells, body_rows = self._validate_rows_and_header(rows, header)

        if mode == "transpose":
            matrix = ([header_cells] if header_cells is not None else []) + body_rows
            # The ragged policy must be applied before the swap, otherwise
            # zip would silently truncate ragged rows.
            matrix = self._rectangularize(matrix, clean_ragged)
            if not matrix[0]:
                self._invalid("table must have at least one column")
            header_cells, body_rows = None, [list(column) for column in zip(*matrix)]

        header_cells, body_rows, columns = self._normalize(
            header_cells, body_rows, clean_ragged
        )
        if clean_max_col_width is not None:
            header_cells, body_rows = self._truncate_cells(
                header_cells, body_rows, clean_max_col_width
            )
        table = self._render(header_cells, body_rows, columns, clean_style, clean_align)

        result: Dict[str, Any] = {
            "mode": mode,
            "style": clean_style,
            "header": header_cells is not None,
            "rows": len(body_rows),
            "columns": columns,
            "result": table,
        }
        if mode in ("from_tsv", "from_csv"):
            result["delimiter"] = clean_delimiter
        return result

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any rendering)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"ascii_table_tool: {message}")

    @classmethod
    def _validate_style(cls, style: Any) -> str:
        """Validate the ``style`` selector (default ``markdown``)."""
        if style is None:
            return "markdown"
        if style not in cls.STYLES:
            cls._invalid(
                f"style must be one of: {', '.join(cls.STYLES)} (got {style!r})"
            )
        return style

    @classmethod
    def _validate_align(cls, align: Any) -> Any:
        """Validate the ``align`` option.

        Returns ``None`` (default left everywhere), a global alignment
        string, or a non-empty list of per-column alignment strings. The
        per-column length is checked against the column count later,
        once the table shape is known.
        """
        if align is None:
            return None
        if isinstance(align, str):
            if align not in cls.ALIGNMENTS:
                cls._invalid(
                    "align must be one of: "
                    f"{', '.join(cls.ALIGNMENTS)} (got {align!r})"
                )
            return align
        if isinstance(align, (list, tuple)):
            if not align:
                cls._invalid("align list must contain at least one entry")
            for entry in align:
                if entry not in cls.ALIGNMENTS:
                    cls._invalid(
                        "each align entry must be one of: "
                        f"{', '.join(cls.ALIGNMENTS)} (got {entry!r})"
                    )
            return list(align)
        cls._invalid(
            "align must be 'left', 'center', 'right' or a list of those "
            f"(got {align!r})"
        )

    @classmethod
    def _validate_max_col_width(cls, max_col_width: Any) -> Optional[int]:
        """Validate the ``max_col_width`` truncation limit."""
        if max_col_width is None:
            return None
        if isinstance(max_col_width, bool) or not isinstance(max_col_width, int):
            cls._invalid(
                "max_col_width must be a positive integer or None "
                f"(got {max_col_width!r})"
            )
        if max_col_width < 1:
            cls._invalid(
                f"max_col_width must be a positive integer (got {max_col_width})"
            )
        return max_col_width

    @classmethod
    def _validate_ragged(cls, ragged: Any) -> str:
        """Validate the ``ragged`` row policy (default ``error``)."""
        if ragged is None:
            return "error"
        if ragged not in cls.RAGGED_POLICIES:
            cls._invalid(
                "ragged must be one of: "
                f"{', '.join(cls.RAGGED_POLICIES)} (got {ragged!r})"
            )
        return ragged

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the delimited ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > cls.MAX_TEXT_CHARS:
            cls._invalid(
                f"text exceeds the {cls.MAX_TEXT_CHARS:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_delimiter(cls, delimiter: Any, default: str) -> str:
        """Validate the one-character ``delimiter`` for delimited modes."""
        if delimiter is None:
            return default
        if isinstance(delimiter, bool) or not isinstance(delimiter, str):
            cls._invalid(
                f"delimiter must be a single character string (got {delimiter!r})"
            )
        if len(delimiter) != 1:
            cls._invalid(
                "delimiter must be a single character string "
                f"(got {delimiter!r} with length {len(delimiter)})"
            )
        if delimiter in ('"', "'", "\n", "\r"):
            cls._invalid(
                f"delimiter must not clash with the quote character or a "
                f"line break (got {delimiter!r})"
            )
        return delimiter

    @classmethod
    def _validate_has_header(cls, has_header: Any) -> bool:
        """Validate the delimited-mode ``has_header`` flag (default True)."""
        if has_header is None:
            return True
        if isinstance(has_header, bool):
            return has_header
        cls._invalid(f"has_header must be a boolean or None (got {has_header!r})")

    @classmethod
    def _coerce_cell(cls, cell: Any) -> str:
        """Coerce one scalar cell to its string representation."""
        if cell is None:
            return ""
        if isinstance(cell, bool):
            return str(cell)
        if isinstance(cell, (int, float)):
            return str(cell)
        if isinstance(cell, str):
            return cell
        cls._invalid(
            "cells must be str, int, float, bool or None "
            f"(got {type(cell).__name__}: {cell!r})"
        )

    @classmethod
    def _validate_rows_and_header(
        cls, rows: Any, header: Any
    ) -> Tuple[Optional[List[str]], List[List[str]]]:
        """Validate and coerce the ``rows`` matrix and optional ``header``."""
        if rows is None or isinstance(rows, (str, bool)) or not isinstance(
            rows, (list, tuple)
        ):
            cls._invalid(f"rows must be a list of row lists (got {rows!r})")
        if not rows:
            cls._invalid("rows must contain at least one row (got [])")
        body_rows: List[List[str]] = []
        for index, row in enumerate(rows):
            if row is None or isinstance(row, (str, bool)) or not isinstance(
                row, (list, tuple)
            ):
                cls._invalid(
                    f"rows[{index}] must be a list of cells (got {row!r})"
                )
            body_rows.append([cls._coerce_cell(cell) for cell in row])
        header_cells: Optional[List[str]] = None
        if header is not None:
            if isinstance(header, (str, bool)) or not isinstance(header, (list, tuple)):
                cls._invalid(f"header must be a list of cells (got {header!r})")
            if not header:
                cls._invalid("header must contain at least one cell (got [])")
            header_cells = [cls._coerce_cell(cell) for cell in header]
        return header_cells, body_rows

    # ------------------------------------------------------------------ #
    # Delimited text parsing (from_csv / from_tsv)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_delimited(
        cls, mode: str, text: str, delimiter: str
    ) -> Any:
        """Parse delimited text with the strict stdlib csv reader.

        Blank lines are skipped. Quoted fields may contain the
        delimiter and escaped quotes; a quoted field containing a line
        break is parsed by the reader but later rejected by the
        single-line cell check in :meth:`_normalize`. Malformed quoting
        (extra characters after a closing quote under the strict
        reader) yields a structured error payload instead of an
        exception.
        """
        context = {"mode": mode}
        try:
            parsed = [
                row
                for row in csv.reader(
                    io.StringIO(text, newline=""), delimiter=delimiter, strict=True
                )
                if row
            ]
        except csv.Error as exc:
            return cls._error_result(
                context,
                error_type="invalid_delimited_text",
                message=(
                    "text cannot be parsed as delimited data: "
                    f"{exc} (delimiter {delimiter!r}; strict RFC 4180 "
                    "quoting is required — a quoted field must be closed "
                    "and followed by the delimiter or the end of the line)"
                ),
            )
        return parsed

    # ------------------------------------------------------------------ #
    # Normalization (shape checks, ragged policy, limits)
    # ------------------------------------------------------------------ #

    @classmethod
    def _normalize(
        cls, header: Optional[List[str]], body: List[List[str]], ragged: str
    ) -> Tuple[Optional[List[str]], List[List[str]], int]:
        """Apply the ragged policy and the table-size limits.

        Returns the (possibly padded) header and body plus the column
        count. Every cell is checked for single-line, bounded content.
        """
        if not body:
            cls._invalid("table must contain at least one data row")
        if header is not None and not header:
            cls._invalid("header must contain at least one cell (got [])")
        combined = ([header] if header is not None else []) + body
        combined = cls._rectangularize(combined, ragged)
        width = len(combined[0])
        if width == 0:
            cls._invalid("table must have at least one column")
        if header is not None:
            header, body = combined[0], combined[1:]
        else:
            body = combined
        if len(body) > cls.MAX_ROWS:
            cls._invalid(
                f"table exceeds the {cls.MAX_ROWS:,}-row limit "
                f"(got {len(body):,} rows)"
            )
        if width > cls.MAX_COLUMNS:
            cls._invalid(
                f"table exceeds the {cls.MAX_COLUMNS:,}-column limit "
                f"(got {width:,} columns)"
            )
        total_cells = (len(body) + (1 if header is not None else 0)) * width
        if total_cells > cls.MAX_CELLS:
            cls._invalid(
                f"table exceeds the {cls.MAX_CELLS:,}-cell limit "
                f"(got {total_cells:,} cells)"
            )
        for row in combined:
            for cell in row:
                cls._check_cell_content(cell)
        return header, body, width

    @classmethod
    def _rectangularize(
        cls, rows: List[List[str]], ragged: str
    ) -> List[List[str]]:
        """Enforce a rectangular row matrix per the ``ragged`` policy.

        ``error`` (the default) rejects rows of inconsistent length;
        ``pad`` right-pads short rows with empty cells up to the widest
        row. Rows that are already rectangular are returned unchanged.
        """
        lengths = [len(row) for row in rows]
        width = max(lengths)
        if any(length != width for length in lengths):
            if ragged == "error":
                observed = sorted(set(lengths))
                cls._invalid(
                    "rows have inconsistent lengths "
                    f"(observed {observed}); pass ragged='pad' to pad "
                    "short rows with empty cells"
                )
            return [row + [""] * (width - len(row)) for row in rows]
        return rows

    @classmethod
    def _check_cell_content(cls, cell: str) -> None:
        """Reject cells that would break single-line table rendering."""
        if len(cell) > cls.MAX_CELL_CHARS:
            cls._invalid(
                f"cell exceeds the {cls.MAX_CELL_CHARS:,}-character limit "
                f"(got {len(cell):,} characters)"
            )
        for bad_char, label in (("\n", "newline"), ("\r", "carriage return"), ("\t", "tab")):
            if bad_char in cell:
                cls._invalid(
                    f"cells must not contain a {label} character "
                    f"(got {cell[:64]!r})"
                )

    @classmethod
    def _truncate_cells(
        cls, header: Optional[List[str]], body: List[List[str]], limit: int
    ) -> Tuple[Optional[List[str]], List[List[str]]]:
        """Apply ``max_col_width`` truncation to every cell."""
        truncated_body = [
            [_truncate_cell(cell, limit) for cell in row] for row in body
        ]
        truncated_header = (
            [_truncate_cell(cell, limit) for cell in header]
            if header is not None
            else None
        )
        return truncated_header, truncated_body

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #

    @classmethod
    def _resolve_alignments(
        cls, align: Any, columns: int
    ) -> Tuple[List[str], bool]:
        """Resolve the ``align`` option into per-column alignments."""
        if align is None:
            return ["left"] * columns, False
        if isinstance(align, str):
            return [align] * columns, True
        if len(align) != columns:
            cls._invalid(
                "align must have one entry per column "
                f"({columns} expected, got {len(align)})"
            )
        return list(align), True

    @classmethod
    def _render(
        cls,
        header: Optional[List[str]],
        body: List[List[str]],
        columns: int,
        style: str,
        align: Any,
    ) -> str:
        """Render the normalized table in the requested style."""
        aligns, explicit = cls._resolve_alignments(align, columns)
        cells = ([header] if header is not None else []) + body
        widths = [
            max(_display_width(row[index]) for row in cells) for index in range(columns)
        ]
        if style == "markdown":
            return cls._render_markdown(header, widths, aligns, explicit, body)
        if style in ("ascii", "grid"):
            return cls._render_boxed(
                header, body, widths, aligns, style == "grid"
            )
        return cls._render_simple(header, body, widths, aligns)

    @staticmethod
    def _row_line_markdown(
        cells: List[str], widths: List[int], aligns: List[str]
    ) -> str:
        """Render one Markdown pipe row."""
        padded = [
            _pad_cell(cell, width, alignment)
            for cell, width, alignment in zip(cells, widths, aligns)
        ]
        return "| " + " | ".join(padded) + " |"

    @classmethod
    def _render_markdown(
        cls,
        header: Optional[List[str]],
        widths: List[int],
        aligns: List[str],
        explicit: bool,
        body: List[List[str]],
    ) -> str:
        """Render a GitHub-flavoured Markdown pipe table.

        A missing header renders as a row of empty cells so the output
        stays valid GFM, which requires a header row.
        """
        header_cells = header if header is not None else [""] * len(widths)
        separator = "|" + "|".join(
            _separator_segment(width, alignment, explicit)
            for width, alignment in zip(widths, aligns)
        ) + "|"
        lines = [
            cls._row_line_markdown(header_cells, widths, aligns),
            separator,
        ]
        lines.extend(cls._row_line_markdown(row, widths, aligns) for row in body)
        return "\n".join(lines)

    @staticmethod
    def _row_line_boxed(
        cells: List[str], widths: List[int], aligns: List[str]
    ) -> str:
        """Render one boxed (ascii / grid) row."""
        padded = [
            _pad_cell(cell, width, alignment)
            for cell, width, alignment in zip(cells, widths, aligns)
        ]
        return "| " + " | ".join(padded) + " |"

    @classmethod
    def _render_boxed(
        cls,
        header: Optional[List[str]],
        body: List[List[str]],
        widths: List[int],
        aligns: List[str],
        row_separators: bool,
    ) -> str:
        """Render a +-+ bordered table (``ascii`` or ``grid`` style)."""
        border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
        lines = [border]
        if header is not None:
            lines.append(cls._row_line_boxed(header, widths, aligns))
            lines.append(border)
        for row in body:
            lines.append(cls._row_line_boxed(row, widths, aligns))
            if row_separators:
                lines.append(border)
        if not row_separators:
            lines.append(border)
        return "\n".join(lines)

    @staticmethod
    def _render_simple(
        header: Optional[List[str]],
        body: List[List[str]],
        widths: List[int],
        aligns: List[str],
    ) -> str:
        """Render borderless aligned columns with a two-space gutter."""
        gutter = "  "
        lines: List[str] = []
        if header is not None:
            padded = [
                _pad_cell(cell, width, alignment)
                for cell, width, alignment in zip(header, widths, aligns)
            ]
            lines.append(gutter.join(padded))
            lines.append(gutter.join("-" * width for width in widths))
        for row in body:
            padded = [
                _pad_cell(cell, width, alignment)
                for cell, width, alignment in zip(row, widths, aligns)
            ]
            lines.append(gutter.join(padded))
        return "\n".join(lines)

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
