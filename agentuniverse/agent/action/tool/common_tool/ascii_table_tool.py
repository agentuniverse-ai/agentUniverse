#!/usr/bin/env python3
"""AsciiTableTool: deterministic monospace table rendering with correct
display-width accounting.

Cell widths follow the ``wcwidth`` model: East Asian Wide/Fullwidth
characters count as two columns, combining marks and zero-width characters
as zero, everything else as one. Control characters are rejected rather
than rendered. The width model is pinned against the real ``wcwidth``
package in the test suite.

Styles: ``ascii`` (``+---+``), ``rounded``, ``unicode`` (box drawing) and
``markdown`` (GFM pipe tables with alignment markers). Ambiguous-width
characters (box drawing, Greek with certain locales) are treated as width
one — the non-CJK ``wcwidth`` default — and the policy is surfaced in every
result.

Modes:
  measure -- display width of one text
  fit     -- minimal column widths for a row set
  render  -- the table itself, with per-line width invariants
"""

import unicodedata
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool

_MODES = ("measure", "fit", "render")
_STYLES = ("ascii", "rounded", "unicode", "markdown")
_ALIGNS = ("left", "center", "right")

_MAX_TEXT_CHARS = 100_000
_MAX_CELLS = 20_000
_MAX_ROWS = 2_000
_MAX_COLS = 200

_ZERO_WIDTH_CF = set("\u200b\u200c\u200d\u2060\ufeff")  # ZWSP ZWNJ ZWJ WJ BOM
_VARIATION_SELECTORS = set("\ufe00\ufe01\ufe02\ufe03\ufe04\ufe05\ufe06\ufe07"
                            "\ufe08\ufe09\ufe0a\ufe0b\ufe0c\ufe0d\ufe0e\ufe0f")


def _char_width(ch: str) -> int:
    """Display width of one character (wcwidth model, ambiguous = 1)."""
    code = ord(ch)
    if unicodedata.combining(ch) or ch in _ZERO_WIDTH_CF or ch in _VARIATION_SELECTORS:
        return 0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    if 0x1F1E6 <= code <= 0x1F1FF:
        return 2  # regional indicators render as emoji flags
    if unicodedata.category(ch) == "Cc":
        raise ValueError("control characters cannot be rendered in tables")
    return 1


def display_width(text: str) -> int:
    return sum(_char_width(ch) for ch in text)


def _truncate(text: str, budget: int) -> str:
    """Cut to ``budget`` display columns, never splitting a wide char."""
    if budget <= 0:
        return ""
    used = 0
    out = []
    for ch in text:
        w = _char_width(ch)
        if used + w > budget:
            break
        out.append(ch)
        used += w
    return "".join(out)


def _pad(text: str, width: int, align: str) -> str:
    fill = width - display_width(text)
    if fill < 0:
        text = _truncate(text, width)
        fill = 0
    if align == "right":
        return " " * fill + text
    if align == "center":
        left = fill // 2
        return " " * left + text + " " * (fill - left)
    return text + " " * fill


class AsciiTableTool(Tool):
    """Deterministic monospace tables with wcwidth-verified alignment."""

    name: str = "ascii_table_tool"
    description: str = (
        "Render monospace tables (ascii/rounded/unicode/markdown styles) "
        "with correct wcwidth display accounting for East Asian wide "
        "characters, combining marks and zero-width joiners."
    )
    tool_type: str = "api"

    def execute(self, mode: str = "render", text: str = "",
                rows: Any = None, headers: Any = None,
                style: str = "ascii", align: Any = "left",
                max_col_width: int = 0, **kwargs: Any) -> Any:
        """Run one table operation.

        - measure: text -> display width breakdown
        - fit:     rows (+ headers) -> minimal column widths
        - render:  rows (+ headers) -> table text with per-line invariants
        """
        if mode not in _MODES:
            raise ValueError(f"mode must be one of {_MODES}; got {mode!r:.64}")
        if mode == "measure":
            return self._measure(text)
        if rows is None and headers is None:
            raise ValueError("rows (or headers) are required for fit/render")
        grid = self._grid(rows, headers)
        has_header = headers is not None
        if mode == "fit":
            return self._fit(grid)
        return self._render(grid, style, align, max_col_width, has_header)

    # ------------------------------------------------------------------ #

    @staticmethod
    def _check_text(text: str, what: str) -> str:
        if not isinstance(text, str):
            raise ValueError(f"{what} must be a string, got {type(text).__name__}")
        if len(text) > _MAX_TEXT_CHARS:
            raise ValueError(f"{what} exceeds {_MAX_TEXT_CHARS} characters")
        return text

    def _measure(self, text: str) -> dict:
        text = self._check_text(text, "text")
        width = display_width(text)
        per_char = []
        for i, ch in enumerate(text[:40]):
            per_char.append({"index": i, "char": ch, "width": _char_width(ch)})
        return {
            "mode": "measure", "chars": len(text), "display_width": width,
            "per_char_preview": per_char,
            "policy": "ambiguous-width characters count as one column "
                      "(non-CJK wcwidth default)",
        }

    def _grid(self, rows, headers) -> list:
        def as_cells(value, what):
            if isinstance(value, str):
                raise ValueError(f"{what} must be a list of rows, not a string")
            if not isinstance(value, list):
                raise ValueError(f"{what} must be a list, got {type(value).__name__}")
            out = []
            for row in value[:_MAX_ROWS]:
                if isinstance(row, (list, tuple)):
                    cells = [self._check_text(c, "cell") for c in row]
                else:
                    raise ValueError("each row must be a list of cell strings")
                out.append(cells)
            return out

        body = as_cells(rows, "rows") if rows is not None else []
        head = None
        if headers is not None:
            if isinstance(headers, str) or not isinstance(headers, list):
                raise ValueError("headers must be a list of cell strings")
            head = [self._check_text(c, "header cell") for c in headers[:_MAX_COLS]]
        grid = ([head] if head else []) + body
        if not grid:
            raise ValueError("at least one row or header is required")
        ncols = max(len(r) for r in grid)
        if ncols > _MAX_COLS:
            raise ValueError(f"more than {_MAX_COLS} columns")
        total = sum(len(r) for r in grid)
        if total > _MAX_CELLS:
            raise ValueError(f"more than {_MAX_CELLS} cells total")
        for r in grid:  # ragged rows are padded with empty cells (documented)
            while len(r) < ncols:
                r.append("")
        return grid

    @staticmethod
    def _fit(grid: list) -> dict:
        ncols = len(grid[0])
        widths = [0] * ncols
        for row in grid:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], display_width(cell))
        return {
            "mode": "fit", "rows": len(grid), "columns": ncols,
            "column_widths": widths,
        }

    def _render(self, grid: list, style: str, align, max_col_width: int, has_header: bool) -> dict:
        if style not in _STYLES:
            raise ValueError(f"style must be one of {_STYLES}; got {style!r:.64}")
        if isinstance(align, str):
            if align not in _ALIGNS:
                raise ValueError(f"align must be one of {_ALIGNS}; got {align!r:.64}")
            aligns = [align] * len(grid[0])
        elif isinstance(align, list):
            aligns = []
            for a in align:
                if a not in _ALIGNS:
                    raise ValueError(f"align entry must be one of {_ALIGNS}")
                aligns.append(a)
            while len(aligns) < len(grid[0]):
                aligns.append("left")
            aligns = aligns[: len(grid[0])]
        else:
            raise ValueError("align must be a string or list of strings")
        if not isinstance(max_col_width, int) or max_col_width < 0:
            raise ValueError("max_col_width must be a non-negative integer")
        notes = []
        if max_col_width and max_col_width > 1:
            notes.append(f"cells truncated to {max_col_width} display columns")
            budget = max_col_width - 1  # leave room for the ellipsis
            grid = [
                [(_truncate(c, budget) + "…") if display_width(c) > max_col_width else c
                 for c in row]
                for row in grid
            ]
        widths = [max(display_width(c) for c in col) for col in zip(*grid)]
        if style == "markdown":
            # GFM alignment markers need three columns minimum; raising the
            # width keeps every line (separator included) one display width.
            widths = [max(w, 3) for w in widths]
        lines = []
        if style == "markdown":
            for row in grid:
                lines.append(self._md_row(row, widths, aligns))
            if has_header:
                lines.insert(1, self._md_sep(widths, aligns))
            else:
                lines.insert(1, self._md_sep(widths, ["left"] * len(widths)))
                notes.append("markdown tables use the first row as the header row")
        else:
            tl, tr, bl, br, h, v = {
                "ascii": ("+", "+", "+", "+", "-", "|"),
                "rounded": ("\u256d", "\u256e", "\u2570", "\u256f", "\u2500", "\u2502"),
                "unicode": ("\u250c", "\u2510", "\u2514", "\u2518", "\u2500", "\u2502"),
            }[style]
            mid = "+" if style == "ascii" else "\u253c"
            top_j = "+" if style == "ascii" else "\u252c"
            bot_j = "+" if style == "ascii" else "\u2534"
            top = tl + top_j.join(h * (w + 2) for w in widths) + tr
            bot = bl + bot_j.join(h * (w + 2) for w in widths) + br
            sep = mid + mid.join(h * (w + 2) for w in widths) + mid
            lines.append(top)
            for idx, row in enumerate(grid):
                lines.append(self._box_row(row, widths, aligns, v))
                if has_header and idx == 0 and len(grid) > 1:
                    lines.append(sep)
            lines.append(bot)
        return {
            "mode": "render", "style": style,
            "table": "\n".join(lines), "line_count": len(lines),
            "column_widths": widths, "aligns": aligns,
            "notes": notes,
            "policy": "ambiguous-width characters count as one column; "
                      "combining marks and zero-width joiners count as zero",
        }

    @staticmethod
    def _md_row(row, widths, aligns):
        return "| " + " | ".join(
            _pad(c, w, a) for c, w, a in zip(row, widths, aligns)
        ) + " |"

    @staticmethod
    def _md_sep(widths, aligns):
        cells = []
        for w, a in zip(widths, aligns):
            if a == "left":
                cells.append(":" + "-" * (w - 1))
            elif a == "right":
                cells.append("-" * (w - 1) + ":")
            else:
                cells.append(":" + "-" * (w - 2) + ":")
        return "| " + " | ".join(cells) + " |"

    @staticmethod
    def _box_row(row, widths, aligns, v):
        return v + " " + (" " + v + " ").join(
            _pad(c, w, a) for c, w, a in zip(row, widths, aligns)
        ) + " " + v
