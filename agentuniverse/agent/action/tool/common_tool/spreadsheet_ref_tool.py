#!/usr/bin/env python3
"""Spreadsheet cell/range reference algebra for agents.

Deterministic, stdlib-only conversions between A1 and R1C1 reference
styles, range parsing and expansion under Excel hard limits (16,384
columns = XFD, 1,048,576 rows), absolute/relative ``$`` semantics,
sheet-qualified references with quoted names, and rectangle set
operations (intersection, union, subtract, shift, resize).

``$`` markers may only prefix the column letters or the row digits
(never in between), relative R1C1 parts are resolved against an anchor
cell (default ``A1``), and every input style is checked against the
sheet bounds before any result is returned.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

MAX_ROW = 1_048_576
MAX_COL = 16_384  # column XFD

_A1_CELL_RE = re.compile(r"^(\$?)([A-Za-z]{1,3})(\$?)([0-9]+)$")
_R1C1_CELL_RE = re.compile(
    r"^R([0-9]*|\[-?[0-9]+\])?C([0-9]*|\[-?[0-9]+\])?$", re.IGNORECASE
)
_PLAIN_SHEET_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
_R1C1_SHAPE_RE = re.compile(r"^[Rr][0-9\[]?.*[Cc]")
_QUOTED_SPAN_RE = re.compile(r'"(?:[^"]|"")*"')
# One addressable corner: optional $, 1-3 letters, optional $, digits.
_CELL_PART = r"\$?[A-Za-z]{1,3}\$?[0-9]+"
# A token tail that never backtracks: either consume ":cell2" (and then the
# next character must not extend an identifier or open a call) or stop after
# the first cell (and then the next character must not be ':' either, so a
# malformed range can never fall back to a partial match).
_TOKEN_TAIL = (
    r"(?::(?P<c2abs>\$?)(?P<c2col>[A-Za-z]{1,3})(?P<c2rowabs>\$?)(?P<c2row>[0-9]+)"
    r"(?![A-Za-z0-9_(])"
    r"|(?![\:A-Za-z0-9_(]))"
)
# Quoted-sheet references are extracted first and blanked out, so cell-like
# text inside a sheet name (e.g. the Q3 in 'Q3 Data') can never leak through.
_QUOTED_SHEET_REF_RE = re.compile(
    r"'(?P<qsheet>(?:[^']|'')+)'!"
    r"(?P<c1abs>\$?)(?P<c1col>[A-Za-z]{1,3})(?P<c1rowabs>\$?)(?P<c1row>[0-9]+)"
    + _TOKEN_TAIL
)
# Any leftover quoted sheet prefix (one whose reference part did not parse)
# is blanked too, so cell-like text inside the name can never leak.
_QUOTED_SHEET_PREFIX_RE = re.compile(r"'(?:[^']|'')+'!")
# A range whose second corner repeats a sheet prefix, e.g.
# Sheet1!A1:Sheet1!B2 or 'Q 3'!B2:'Q 3'!C4. Excel accepts these; before
# reference extraction the repeated prefix is collapsed onto the first
# corner when (and only when) it names the same sheet.
_REPEATED_SHEET_RANGE_RE = re.compile(
    r"(?<![A-Za-z0-9_$])"
    r"(?P<lead>[A-Za-z_][A-Za-z0-9_.]*!|'(?:[^']|'')+'!)"
    r"(?P<first>\$?[A-Za-z]{1,3}\$?[0-9]+)"
    r":"
    r"(?P<mid>[A-Za-z_][A-Za-z0-9_.]*!|'(?:[^']|'')+'!)"
    r"(?P<second>\$?[A-Za-z]{1,3}\$?[0-9]+)"
    r"(?![A-Za-z0-9_(])"
)
_EXTRACT_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_$])"
    r"(?:(?P<psheet>[A-Za-z_][A-Za-z0-9_.]*)!)?"
    r"(?P<c1abs>\$?)(?P<c1col>[A-Za-z]{1,3})(?P<c1rowabs>\$?)(?P<c1row>[0-9]+)"
    + _TOKEN_TAIL
)
_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")


def col_letters_to_index(letters: str) -> int:
    """Convert column letters to a 1-based index via bijective base-26."""
    index = 0
    for char in letters.upper():
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index


def col_index_to_letters(index: int) -> str:
    """Convert a 1-based column index to letters via bijective base-26."""
    if index < 1:
        raise ValueError(f"column index must be >= 1, got {index}")
    letters = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def _needs_quoting(sheet: str) -> bool:
    return not bool(_PLAIN_SHEET_RE.match(sheet))


def _quote_sheet(sheet: str) -> str:
    if _needs_quoting(sheet):
        return "'" + sheet.replace("'", "''") + "'"
    return sheet


def _sheet_of_prefix(prefix: str) -> str:
    """Return the bare sheet name behind a 'Sheet!' / ''quoted!'' prefix."""
    body = prefix[:-1]  # drop the bang
    if body.startswith("'"):
        body = body[1:-1].replace("''", "'")
    return body


def _normalize_repeated_sheet(text: str) -> str:
    """Collapse identical repeated sheet prefixes inside one range token.

    ``Sheet1!A1:Sheet1!B2`` becomes ``Sheet1!A1:B2``; a second corner that
    names a *different* sheet is left untouched (3-D references are out of
    scope and must not be silently re-qualified).
    """

    def rewrite(match: re.Match) -> str:
        lead, mid = match.group("lead"), match.group("mid")
        if _sheet_of_prefix(lead) != _sheet_of_prefix(mid):
            return match.group(0)
        return lead + match.group("first") + ":" + match.group("second")

    return _REPEATED_SHEET_RANGE_RE.sub(rewrite, text)


class _RefError(ValueError):
    """Validation failure carrying a character position inside the input."""

    def __init__(self, message: str, position: int) -> None:
        super().__init__(message)
        self.position = position


class _Cell:
    """Resolved cell coordinates plus $ / R1C1 addressing semantics."""

    __slots__ = ("row", "col", "abs_row", "abs_col", "rel_row", "rel_col")

    def __init__(
        self,
        row: int,
        col: int,
        abs_row: bool,
        abs_col: bool,
        rel_row: int | None = None,
        rel_col: int | None = None,
    ) -> None:
        self.row = row
        self.col = col
        self.abs_row = abs_row
        self.abs_col = abs_col
        self.rel_row = rel_row  # R1C1 relative row offset; None when absolute
        self.rel_col = rel_col  # R1C1 relative col offset; None when absolute

    def a1(self) -> str:
        return (
            ("$" if self.abs_col else "")
            + col_index_to_letters(self.col)
            + ("$" if self.abs_row else "")
            + str(self.row)
        )

    def r1c1(self) -> str:
        row_part = f"R[{self.rel_row}]" if self.rel_row is not None else f"R{self.row}"
        col_part = f"C[{self.rel_col}]" if self.rel_col is not None else f"C{self.col}"
        return row_part + col_part


def _check_bounds(row: int | None, col: int | None, position: int) -> None:
    if col is not None and col > MAX_COL:
        raise _RefError(
            f"column {col_index_to_letters(col)} is beyond the Excel limit "
            f"XFD (16384)",
            position,
        )
    if row is not None and row > MAX_ROW:
        raise _RefError(f"row {row} is beyond the Excel limit 1048576", position)


def _parse_a1_cell(token: str, position: int) -> _Cell:
    """Parse one A1-style token (``$A$1``, ``B$2``, ``A1``) at ``position``."""
    match = _A1_CELL_RE.match(token)
    if not match:
        raise _RefError(
            f"invalid cell reference {token!r}: expected column letters then "
            "row digits, with optional $ directly before the letters and/or "
            "directly before the digits (never in between)",
            position,
        )
    abs_col = match.group(1) == "$"
    letters = match.group(2)
    abs_row = match.group(3) == "$"
    digits = match.group(4)
    col = col_letters_to_index(letters)
    row = int(digits)
    if row < 1:
        raise _RefError("row numbers start at 1", position + len(token) - len(digits))
    if col > MAX_COL:
        _check_bounds(None, col, position + (1 if abs_col else 0))
    if row > MAX_ROW:
        _check_bounds(row, None, position + len(token) - len(digits))
    return _Cell(row, col, abs_row, abs_col)


def _parse_r1c1_cell(token: str, position: int) -> _Cell:
    """Parse one R1C1 token (``R1C1``, ``R[1]C[-2]``, ``R1C[2]``, ``RC``)."""
    match = _R1C1_CELL_RE.match(token)
    if not match:
        raise _RefError(
            f"invalid R1C1 reference {token!r}: expected forms like R1C1, "
            "R[1]C[-2], R1C[2] or RC",
            position,
        )
    row_part, col_part = match.group(1), match.group(2)
    rel_row = rel_col = None
    if row_part is None or row_part == "":
        rel_row = 0  # bare R means the anchor's row
    elif row_part.startswith("["):
        rel_row = int(row_part[1:-1])
    if col_part is None or col_part == "":
        rel_col = 0  # bare C means the anchor's column
    elif col_part.startswith("["):
        rel_col = int(col_part[1:-1])
    if rel_row is None:
        row = int(row_part)
        if row < 1:
            raise _RefError(f"R1C1 row must be >= 1, got {row}", position)
        _check_bounds(row, None, position)
        abs_row = True
    else:
        row = 1 + rel_row  # placeholder; resolved against the anchor later
        abs_row = False
    if rel_col is None:
        col = int(col_part)
        if col < 1:
            raise _RefError(f"R1C1 column must be >= 1, got {col}", position)
        _check_bounds(None, col, position)
        abs_col = True
    else:
        col = 1 + rel_col
        abs_col = False
    return _Cell(row, col, abs_row, abs_col, rel_row, rel_col)


def _looks_like_r1c1(token: str) -> bool:
    """True for tokens shaped like R1C1 (R-part then C-part, no letters)."""
    return bool(_R1C1_SHAPE_RE.match(token)) and bool(
        re.fullmatch(r"[Rr][0-9\[\]-]*[Cc][0-9\[\]-]*", token)
    )


def _resolve_relative(cell: _Cell, anchor: tuple[int, int]) -> _Cell:
    """Resolve R1C1 relative parts against ``anchor`` (row, col)."""
    row = anchor[0] + cell.rel_row if cell.rel_row is not None else cell.row
    col = anchor[1] + cell.rel_col if cell.rel_col is not None else cell.col
    if row < 1:
        raise _RefError(
            f"relative row offset resolves to row {row} (< 1) at the anchor",
            0,
        )
    if col < 1:
        raise _RefError(
            f"relative column offset resolves to column {col} (< 1) at the anchor",
            0,
        )
    _check_bounds(row, col, 0)
    return _Cell(row, col, cell.abs_row, cell.abs_col, cell.rel_row, cell.rel_col)


def _split_sheet_prefix(ref: str) -> tuple[str | None, int]:
    """Return (sheet, body_start) after stripping an optional sheet prefix."""
    if ref.startswith("'"):
        index = 1
        while index < len(ref):
            if ref[index] != "'":
                index += 1
                continue
            if index + 1 < len(ref) and ref[index + 1] == "'":
                index += 2  # doubled quote inside the sheet name
                continue
            if index + 1 < len(ref) and ref[index + 1] == "!":
                sheet = ref[1:index].replace("''", "'")
                if not sheet:
                    raise _RefError("empty quoted sheet name", 0)
                return sheet, index + 2
            raise _RefError(
                "quoted sheet name must be followed by '!'", index + 1
            )
        raise _RefError("unterminated quoted sheet name", 0)
    bang = ref.find("!")
    if bang == 0:
        raise _RefError("empty sheet name before '!'", 0)
    if bang > 0:
        sheet = ref[:bang]
        if not _PLAIN_SHEET_RE.match(sheet):
            raise _RefError(
                f"invalid sheet name {sheet!r}: quote names containing spaces "
                "or special characters, e.g. 'My Sheet'!A1",
                0,
            )
        return sheet, bang + 1
    return None, 0


class _ParsedRef:
    """Parsed single cell or rectangular range."""

    __slots__ = ("kind", "sheet", "start", "end", "notes", "full_row", "full_col")

    def __init__(
        self,
        kind: str,
        sheet: str | None,
        start: _Cell,
        end: _Cell,
        notes: list[str] | None = None,
        full_row: bool = False,
        full_col: bool = False,
    ) -> None:
        self.kind = kind
        self.sheet = sheet
        self.start = start
        self.end = end
        self.notes = notes or []
        self.full_row = full_row
        self.full_col = full_col

    @property
    def rows(self) -> int:
        return self.end.row - self.start.row + 1

    @property
    def cols(self) -> int:
        return self.end.col - self.start.col + 1

    @property
    def cell_count(self) -> int:
        return self.rows * self.cols

    def prefix(self) -> str:
        return f"{_quote_sheet(self.sheet)}!" if self.sheet is not None else ""

    def normalized(self) -> str:
        if self.kind == "cell":
            return self.prefix() + self.start.a1()
        if self.full_col:
            left = ("$" if self.start.abs_col else "") + col_index_to_letters(self.start.col)
            right = ("$" if self.end.abs_col else "") + col_index_to_letters(self.end.col)
            return self.prefix() + f"{left}:{right}"
        if self.full_row:
            left = ("$" if self.start.abs_row else "") + str(self.start.row)
            right = ("$" if self.end.abs_row else "") + str(self.end.row)
            return self.prefix() + f"{left}:{right}"
        return self.prefix() + self.start.a1() + ":" + self.end.a1()


def _classify_corner(token: str) -> str:
    """Classify a range corner token: 'column', 'row', 'cell' or 'invalid'."""
    if not token:
        return "invalid"
    stripped = token.replace("$", "")
    if not stripped:
        return "invalid"
    if stripped.isalpha():
        return "cell" if _looks_like_r1c1(token) else "column"
    if stripped.isdigit():
        return "row"
    if _A1_CELL_RE.match(token) or _R1C1_CELL_RE.match(stripped):
        return "cell"
    return "invalid"


def _parse_cell_token(token: str, position: int, anchor: tuple[int, int]) -> _Cell:
    """Parse one corner token; A1 wins over R1C1 on ambiguity (e.g. RC1)."""
    if _R1C1_CELL_RE.match(token) and not _A1_CELL_RE.match(token):
        cell = _parse_r1c1_cell(token, position)
        if cell.rel_row is not None or cell.rel_col is not None:
            cell = _resolve_relative(cell, anchor)
        return cell
    return _parse_a1_cell(token, position)


def parse_ref(ref: str, anchor: tuple[int, int] = (1, 1)) -> _ParsedRef:
    """Parse a sheet-qualified cell/range reference in A1 or R1C1 style.

    The sheet prefix may also be repeated on the second range corner
    (``Sheet1!A1:Sheet1!B2``) as long as it names the same sheet; the
    normalized form writes the sheet once.
    """
    if not isinstance(ref, str) or not ref.strip():
        raise _RefError("empty reference", 0)
    if len(ref) > 500:
        raise _RefError("reference longer than 500 characters", 0)
    sheet, body_start = _split_sheet_prefix(ref)
    body = ref[body_start:]
    if not body:
        raise _RefError("missing cell or range after the sheet name", len(ref))
    offset = body_start
    parts = body.split(":")
    if len(parts) > 2:
        second_colon = body.index(":", body.index(":") + 1)
        raise _RefError("a range may contain at most one ':'", offset + second_colon)
    positions = [
        offset + sum(len(part) + 1 for part in parts[:index])
        for index in range(len(parts))
    ]
    if len(parts) == 2 and ("!" in parts[1] or parts[1].startswith("'")):
        # Excel also accepts the sheet repeated on the second corner
        # (Sheet1!A1:Sheet1!B2); accept it when it names the same sheet.
        sheet2, second_start = _split_sheet_prefix(parts[1])
        if sheet != sheet2:
            raise _RefError(
                "a range's corners must carry the same sheet prefix: write "
                "the sheet once (Sheet1!A1:B2) or repeat the same sheet on "
                "both corners",
                positions[1],
            )
        parts[1] = parts[1][second_start:]
    kinds = [_classify_corner(token) for token in parts]

    if len(parts) == 1:
        if kinds[0] == "column":
            raise _RefError(
                "column reference needs a ':' range separator, e.g. A:A",
                positions[0],
            )
        if kinds[0] == "row":
            raise _RefError(
                "row reference needs a ':' range separator, e.g. 1:1",
                positions[0],
            )
        cell = _parse_cell_token(parts[0], positions[0], anchor)
        return _ParsedRef("cell", sheet, cell, cell)

    kind_a, kind_b = kinds
    if kind_a != kind_b or "invalid" in kinds:
        raise _RefError(
            f"range corners must be the same kind (cell, column or row), got "
            f"{parts[0]!r} ({kind_a}) and {parts[1]!r} ({kind_b})",
            positions[0],
        )
    notes: list[str] = []
    if kind_a == "column":
        cells = []
        for token, position in zip(parts, positions):
            stripped = token.replace("$", "")
            if len(token) != len(stripped) + token.count("$", 0, 1) or "$" in stripped:
                raise _RefError(
                    f"invalid full-column bound {token!r}: expected 1-3 letters "
                    "with an optional leading $ only",
                    position,
                )
            col = col_letters_to_index(stripped)
            _check_bounds(None, col, position)
            cells.append(_Cell(1, col, True, token.startswith("$")))
        if cells[0].col > cells[1].col:
            cells.reverse()
            notes.append("corners re-ordered into canonical left:right order")
        result = _ParsedRef(
            "range", sheet, cells[0],
            _Cell(MAX_ROW, cells[1].col, True, cells[1].abs_col),
            notes, full_col=True,
        )
        return result
    if kind_a == "row":
        cells = []
        for token, position in zip(parts, positions):
            stripped = token.lstrip("$")
            if token.count("$") > 1 or not stripped.isdigit():
                raise _RefError(
                    f"invalid full-row bound {token!r}: expected digits with an "
                    "optional leading $ only",
                    position,
                )
            row = int(stripped)
            if row < 1:
                raise _RefError("row numbers start at 1", position)
            _check_bounds(row, None, position)
            cells.append(_Cell(row, 1, token.startswith("$"), True))
        if cells[0].row > cells[1].row:
            cells.reverse()
            notes.append("corners re-ordered into canonical top:bottom order")
        return _ParsedRef(
            "range", sheet, cells[0],
            _Cell(cells[1].row, MAX_COL, cells[1].abs_row, True),
            notes, full_row=True,
        )
    start = _parse_cell_token(parts[0], positions[0], anchor)
    end = _parse_cell_token(parts[1], positions[1], anchor)
    if start.row > end.row or start.col > end.col:
        start, end = end, start
        notes.append("corners re-ordered into canonical top-left:bottom-right order")
    return _ParsedRef("range", sheet, start, end, notes)


def _parse_anchor(anchor: Any) -> tuple[int, int]:
    if anchor is None:
        return (1, 1)
    if not isinstance(anchor, str) or not anchor.strip():
        raise ValueError("anchor must be a non-empty A1-style cell such as 'C5'")
    parsed = parse_ref(anchor)
    if parsed.kind != "cell":
        raise ValueError(f"anchor must be a single cell, got range {anchor!r}")
    return (parsed.start.row, parsed.start.col)


def _parse_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def _make_area(
    sheet: str | None,
    r1: int, c1: int, r2: int, c2: int,
    abs_row: bool, abs_col: bool,
) -> _ParsedRef:
    """Build a result range, collapsing 1x1 boxes to cell kind and
    full-width/height boxes to full-row/full-column form."""
    full_col = r1 == 1 and r2 == MAX_ROW
    full_row = not full_col and c1 == 1 and c2 == MAX_COL
    if not full_col and not full_row and r1 == r2 and c1 == c2:
        return _ParsedRef("cell", sheet, _Cell(r1, c1, abs_row, abs_col), _Cell(r1, c1, abs_row, abs_col))
    return _ParsedRef(
        "range", sheet,
        _Cell(r1, c1, abs_row, abs_col),
        _Cell(r2, c2, abs_row, abs_col),
        full_row=full_row, full_col=full_col,
    )


def _area_ref(r1: int, c1: int, r2: int, c2: int) -> str:
    """Render a rectangle, collapsing 1x1 boxes to a single cell ref."""
    if r1 == r2 and c1 == c2:
        return f"{col_index_to_letters(c1)}{r1}"
    return f"{col_index_to_letters(c1)}{r1}:{col_index_to_letters(c2)}{r2}"


def _mask_quoted(text: str) -> tuple[str, int]:
    """Blank out double-quoted spans (Excel escapes "" inside strings)."""
    spans = list(_QUOTED_SPAN_RE.finditer(text))
    masked = text
    for span in spans:
        replacement = " " * (span.end() - span.start())
        masked = masked[: span.start()] + replacement + masked[span.end():]
    return masked, len(spans)


def _cell_payload(cell: _Cell) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "a1": cell.a1(),
        "row": cell.row,
        "col": cell.col,
        "col_letters": col_index_to_letters(cell.col),
        "abs_row": cell.abs_row,
        "abs_col": cell.abs_col,
    }
    if cell.rel_row is not None or cell.rel_col is not None:
        payload["r1c1"] = cell.r1c1()
        if cell.rel_row is not None:
            payload["rel_row_offset"] = cell.rel_row
        if cell.rel_col is not None:
            payload["rel_col_offset"] = cell.rel_col
    return payload


def _convert_cell(cell: _Cell, anchor: tuple[int, int], to: str, steps: list[str]) -> str:
    """Render one cell in the target style, recording explanation steps."""
    if to == "r1c1":
        if cell.rel_row is not None or cell.rel_col is not None:
            steps.append(f"{cell.r1c1()} kept in relative R1C1 form")
            return cell.r1c1()
        if cell.abs_row and cell.abs_col:
            steps.append(
                f"{cell.a1()} -> row {cell.row}, column {cell.col} "
                f"({col_index_to_letters(cell.col)}) -> {cell.r1c1()}"
            )
            return cell.r1c1()
        # relative / mixed A1 addresses keep their semantics as R[d]C[d]
        # offsets against the anchor, exactly like Excel's R1C1 display mode
        rel_row = None if cell.abs_row else cell.row - anchor[0]
        rel_col = None if cell.abs_col else cell.col - anchor[1]
        rendered = _Cell(
            cell.row, cell.col, cell.abs_row, cell.abs_col, rel_row, rel_col
        )
        parts = []
        if rel_row is not None:
            parts.append(f"relative row {anchor[0]}{rel_row:+d}={cell.row}")
        else:
            parts.append(f"absolute row {cell.row}")
        if rel_col is not None:
            parts.append(f"relative column {anchor[1]}{rel_col:+d}={cell.col}")
        else:
            parts.append(f"absolute column {cell.col}")
        steps.append(
            f"{cell.a1()} at anchor {col_index_to_letters(anchor[1])}{anchor[0]} "
            f"converts with {', '.join(parts)} -> {rendered.r1c1()}"
        )
        return rendered.r1c1()
    if cell.rel_row is None and cell.rel_col is None:
        steps.append(f"{cell.r1c1()} -> {cell.a1()} (absolute parts map directly)")
        return cell.a1()
    resolved = _resolve_relative(cell, anchor)
    parts = []
    if cell.rel_row is not None:
        parts.append(f"row {anchor[0]}{cell.rel_row:+d}={resolved.row}")
    if cell.rel_col is not None:
        parts.append(
            f"column {anchor[1]}{cell.rel_col:+d}={resolved.col} "
            f"({col_index_to_letters(resolved.col)})"
        )
    steps.append(
        f"{cell.r1c1()} at anchor {col_index_to_letters(anchor[1])}{anchor[0]} "
        f"resolves via {', '.join(parts)} -> {resolved.a1()}"
    )
    return resolved.a1()


def _disjoint_areas(a: _ParsedRef, b: _ParsedRef) -> list[str]:
    """Decompose the union of two rectangles into disjoint rectangles.

    Greedy maximal-rectangle cover over the cell set: always emit the
    rectangle rooted at the smallest remaining (row, col). Deterministic.
    """
    cells: set[tuple[int, int]] = set()
    for ref in (a, b):
        for row in range(ref.start.row, ref.end.row + 1):
            for col in range(ref.start.col, ref.end.col + 1):
                cells.add((row, col))
    areas: list[str] = []
    while cells:
        row_top = min(row for row, _ in cells)
        col_left = min(col for row, col in cells if row == row_top)
        col_right = col_left
        while (row_top, col_right + 1) in cells:
            col_right += 1
        row_bottom = row_top
        while all(
            (row_bottom + 1, col) in cells for col in range(col_left, col_right + 1)
        ):
            row_bottom += 1
        for row in range(row_top, row_bottom + 1):
            for col in range(col_left, col_right + 1):
                cells.discard((row, col))
        areas.append(_area_ref(row_top, col_left, row_bottom, col_right))
    return areas


class SpreadsheetRefTool(Tool):
    """Spreadsheet cell/range reference algebra.

    Modes: parse, convert, expand, algebra, extract_refs.
    """

    max_input_length: int = 10_000
    max_expand_cells: int = 10_000
    max_formula_refs: int = 10_000
    max_algebra_cells: int = 1_000_000
    max_notes: int = 20

    _MODES: ClassVar[tuple[str, ...]] = (
        "parse", "convert", "expand", "algebra", "extract_refs",
    )
    _OPS: ClassVar[tuple[str, ...]] = (
        "intersection", "union", "subtract", "shift", "resize",
    )

    def execute(
        self,
        mode: str,
        ref: str | None = None,
        to: str | None = None,
        anchor: str | None = None,
        range_a: str | None = None,
        range_b: str | None = None,
        op: str | None = None,
        shift_rows: int | None = None,
        shift_cols: int | None = None,
        resize_rows: int | None = None,
        resize_cols: int | None = None,
        formula: str | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            if operation == "parse":
                return self._parse_mode(ref)
            if operation == "convert":
                return self._convert_mode(ref, to, anchor)
            if operation == "expand":
                return self._expand_mode(ref)
            if operation == "algebra":
                return self._algebra_mode(
                    range_a, range_b, op, shift_rows, shift_cols,
                    resize_rows, resize_cols,
                )
            return self._extract_refs_mode(formula)
        except _RefError as exc:
            return self._error(mode, "reference_error", str(exc), position=exc.position)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(mode, "operation_error", f"Reference operation failed: {exc}")

    # -- shared helpers ---------------------------------------------------
    def _validate_config(self) -> None:
        for name in (
            "max_input_length", "max_expand_cells", "max_formula_refs",
            "max_algebra_cells", "max_notes",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    def _mode(self, mode: Any) -> str:
        if mode not in self._MODES:
            raise ValueError(
                f"mode must be one of {', '.join(self._MODES)}, got {mode!r}"
            )
        return str(mode)

    def _error(
        self, ref: Any, kind: str, message: str, position: int | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": "error", "error_type": kind, "error": message, "ref": ref
        }
        if position is not None:
            payload["position"] = position
        return payload

    def _input_ref(self, ref: Any, name: str = "ref") -> str:
        if not isinstance(ref, str) or not ref.strip():
            raise ValueError(f"{name} must be a non-empty reference string")
        if len(ref) > self.max_input_length:
            raise ValueError(
                f"{name} exceeds max_input_length={self.max_input_length} characters"
            )
        return ref

    # -- parse --------------------------------------------------------------
    def _parse_mode(self, ref: Any) -> dict[str, Any]:
        text = self._input_ref(ref)
        parsed = parse_ref(text)
        notes = list(parsed.notes)
        if parsed.full_col:
            notes.append("full-column range: rows span the sheet rows 1..1048576")
        if parsed.full_row:
            notes.append("full-row range: columns span the sheet columns 1..16384")
        return {
            "status": "ok",
            "kind": parsed.kind,
            "sheet": parsed.sheet,
            "sheet_quoted": parsed.sheet is not None and _needs_quoting(parsed.sheet),
            "start": _cell_payload(parsed.start),
            "end": _cell_payload(parsed.end),
            "size": {"rows": parsed.rows, "cols": parsed.cols},
            "cell_count": parsed.cell_count,
            "normalized": parsed.normalized(),
            "notes": notes[: self.max_notes],
        }

    # -- convert --------------------------------------------------------------
    def _convert_mode(self, ref: Any, to: Any, anchor: Any) -> dict[str, Any]:
        text = self._input_ref(ref)
        if to not in ("r1c1", "a1"):
            raise ValueError("to must be 'r1c1' or 'a1'")
        anchor_rc = _parse_anchor(anchor)
        parsed = parse_ref(text, anchor=anchor_rc)
        steps: list[str] = []
        if parsed.kind == "cell":
            converted = _convert_cell(parsed.start, anchor_rc, to, steps)
        else:
            converted = (
                _convert_cell(parsed.start, anchor_rc, to, steps)
                + ":"
                + _convert_cell(parsed.end, anchor_rc, to, steps)
            )
        return {
            "status": "ok",
            "kind": parsed.kind,
            "to": to,
            "anchor": f"{col_index_to_letters(anchor_rc[1])}{anchor_rc[0]}",
            "original": text,
            "normalized": parsed.normalized(),
            "converted": parsed.prefix() + converted,
            "explanation": " ".join(steps),
        }

    # -- expand -----------------------------------------------------------------
    def _expand_mode(self, ref: Any) -> dict[str, Any]:
        text = self._input_ref(ref)
        parsed = parse_ref(text)
        count = parsed.cell_count
        payload: dict[str, Any] = {
            "status": "ok",
            "kind": parsed.kind,
            "sheet": parsed.sheet,
            "normalized": parsed.normalized(),
            "size": {"rows": parsed.rows, "cols": parsed.cols},
            "cell_count": count,
        }
        if parsed.full_col:
            payload["full_column"] = True
        if parsed.full_row:
            payload["full_row"] = True
        if count > self.max_expand_cells:
            payload["enumerated"] = False
            payload["refused"] = True
            payload["reason"] = (
                f"cell_count {count} exceeds max_expand_cells="
                f"{self.max_expand_cells}; size-only mode, use parse or "
                "algebra arithmetic instead of enumeration"
            )
            return payload
        cells: list[str] = []
        prefix = parsed.prefix()
        for row in range(parsed.start.row, parsed.end.row + 1):
            for col in range(parsed.start.col, parsed.end.col + 1):
                cells.append(f"{prefix}{col_index_to_letters(col)}{row}")
        payload["enumerated"] = True
        payload["cells"] = cells
        payload["order"] = "row-major"
        return payload

    # -- algebra ------------------------------------------------------------------
    def _algebra_mode(
        self,
        range_a: Any,
        range_b: Any,
        op: Any,
        shift_rows: Any,
        shift_cols: Any,
        resize_rows: Any,
        resize_cols: Any,
    ) -> dict[str, Any]:
        if op not in self._OPS:
            raise ValueError(
                "op must be one of intersection, union, subtract, shift, resize"
            )
        if op in ("shift", "resize"):
            return self._transform(
                range_a, op, shift_rows, shift_cols, resize_rows, resize_cols
            )
        a = parse_ref(self._input_ref(range_a, "range_a"))
        b = parse_ref(self._input_ref(range_b, "range_b"))
        if (a.sheet or "") != (b.sheet or ""):
            raise ValueError(
                "range algebra requires both ranges on the same sheet "
                f"(got {a.sheet!r} and {b.sheet!r})"
            )
        if op == "intersection":
            return self._intersect(a, b)
        if op == "union":
            return self._union(a, b)
        return self._subtract(a, b)

    def _intersect(self, a: _ParsedRef, b: _ParsedRef) -> dict[str, Any]:
        r1, r2 = max(a.start.row, b.start.row), min(a.end.row, b.end.row)
        c1, c2 = max(a.start.col, b.start.col), min(a.end.col, b.end.col)
        if r1 > r2 or c1 > c2:
            return {
                "status": "ok", "op": "intersection",
                "range_a": a.normalized(), "range_b": b.normalized(),
                "result": None, "areas": [], "cell_count": 0,
                "explanation": "the ranges do not overlap, so the intersection is empty",
            }
        area = _make_area(a.sheet, r1, c1, r2, c2, False, False)
        return {
            "status": "ok", "op": "intersection",
            "range_a": a.normalized(), "range_b": b.normalized(),
            "result": area.normalized(), "areas": [area.normalized()],
            "cell_count": area.cell_count,
            "explanation": (
                f"row overlap {r1}..{r2} and column overlap {c1}..{c2} give "
                f"{area.normalized()} ({area.rows}x{area.cols} = "
                f"{area.cell_count} cells)"
            ),
        }

    def _union(self, a: _ParsedRef, b: _ParsedRef) -> dict[str, Any]:
        r1, r2 = min(a.start.row, b.start.row), max(a.end.row, b.end.row)
        c1, c2 = min(a.start.col, b.start.col), max(a.end.col, b.end.col)
        box_count = (r2 - r1 + 1) * (c2 - c1 + 1)
        overlap_rows = max(0, min(a.end.row, b.end.row) - max(a.start.row, b.start.row) + 1)
        overlap_cols = max(0, min(a.end.col, b.end.col) - max(a.start.col, b.start.col) + 1)
        union_count = a.cell_count + b.cell_count - overlap_rows * overlap_cols
        if box_count == union_count:
            area = _make_area(a.sheet, r1, c1, r2, c2, False, False)
            return {
                "status": "ok", "op": "union",
                "range_a": a.normalized(), "range_b": b.normalized(),
                "result": area.normalized(), "areas": [area.normalized()],
                "cell_count": area.cell_count, "contiguous": True,
                "explanation": (
                    f"the ranges are rectangular-contiguous: their union fills "
                    f"the bounding box {area.normalized()} ({area.rows}x"
                    f"{area.cols} = {area.cell_count} cells)"
                ),
            }
        areas: list[str] = []
        decomposition_note = ""
        if union_count <= self.max_algebra_cells:
            areas = [a.prefix() + ref for ref in _disjoint_areas(a, b)]
        else:
            decomposition_note = (
                f"; area decomposition skipped because the union holds "
                f"{union_count} cells (> max_algebra_cells={self.max_algebra_cells})"
            )
        return {
            "status": "ok", "op": "union",
            "range_a": a.normalized(), "range_b": b.normalized(),
            "result": None, "areas": areas,
            "cell_count": union_count, "contiguous": False,
            "explanation": (
                f"the ranges are not rectangular-contiguous (the bounding box "
                f"would hold {box_count} cells but the union holds "
                f"{union_count}), so the union is a multi-area range with "
                f"{len(areas)} disjoint area(s){decomposition_note}"
            ),
        }

    def _subtract(self, a: _ParsedRef, b: _ParsedRef) -> dict[str, Any]:
        overlap_rows = min(a.end.row, b.end.row) - max(a.start.row, b.start.row) + 1
        overlap_cols = min(a.end.col, b.end.col) - max(a.start.col, b.start.col) + 1
        if overlap_rows <= 0 or overlap_cols <= 0:
            return {
                "status": "ok", "op": "subtract",
                "range_a": a.normalized(), "range_b": b.normalized(),
                "result": a.normalized(), "areas": [a.normalized()],
                "cell_count": a.cell_count,
                "explanation": "b does not overlap a, so a minus b is a itself",
            }
        br1, br2 = max(a.start.row, b.start.row), min(a.end.row, b.end.row)
        bc1, bc2 = max(a.start.col, b.start.col), min(a.end.col, b.end.col)
        areas: list[tuple[int, int, int, int]] = []
        if a.start.row < br1:
            areas.append((a.start.row, a.start.col, br1 - 1, a.end.col))
        if br2 < a.end.row:
            areas.append((br2 + 1, a.start.col, a.end.row, a.end.col))
        if bc1 > a.start.col:
            areas.append((br1, a.start.col, br2, bc1 - 1))
        if bc2 < a.end.col:
            areas.append((br1, bc2 + 1, br2, a.end.col))
        area_refs = [
            _area_ref(r1, c1, r2, c2) for (r1, c1, r2, c2) in areas
        ]
        cell_count = sum(
            (r2 - r1 + 1) * (c2 - c1 + 1) for (r1, c1, r2, c2) in areas
        )
        if not area_refs:
            return {
                "status": "ok", "op": "subtract",
                "range_a": a.normalized(), "range_b": b.normalized(),
                "result": None, "areas": [], "cell_count": 0,
                "explanation": (
                    "b covers a entirely, so a minus b is the empty range"
                ),
            }
        result = a.prefix() + area_refs[0] if len(area_refs) == 1 else None
        return {
            "status": "ok", "op": "subtract",
            "range_a": a.normalized(), "range_b": b.normalized(),
            "result": result, "areas": [a.prefix() + ref for ref in area_refs],
            "cell_count": cell_count,
            "explanation": (
                f"removing the {overlap_rows}x{overlap_cols}="
                f"{overlap_rows * overlap_cols} cell overlap from "
                f"{a.cell_count} cells leaves {cell_count} cell(s) in "
                f"{len(area_refs)} area(s)"
            ),
        }

    def _transform(
        self,
        range_a: Any,
        op: str,
        shift_rows: Any,
        shift_cols: Any,
        resize_rows: Any,
        resize_cols: Any,
    ) -> dict[str, Any]:
        a = parse_ref(self._input_ref(range_a, "range_a"))
        r1, r2 = a.start.row, a.end.row
        c1, c2 = a.start.col, a.end.col
        if op == "shift":
            dr = _parse_int(shift_rows if shift_rows is not None else 0, "shift_rows")
            dc = _parse_int(shift_cols if shift_cols is not None else 0, "shift_cols")
            nr1, nr2, nc1, nc2 = r1 + dr, r2 + dr, c1 + dc, c2 + dc
            if nr1 < 1 or nc1 < 1 or nr2 > MAX_ROW or nc2 > MAX_COL:
                raise ValueError(
                    f"shift by (rows={dr}, cols={dc}) would move the range "
                    f"outside the sheet bounds (rows 1..{MAX_ROW}, columns "
                    f"1..{MAX_COL})"
                )
            explanation = (
                f"shifting {a.normalized()} by rows={dr}, cols={dc} keeps the "
                f"size {a.rows}x{a.cols}"
            )
        else:
            rows = _parse_int(resize_rows, "resize_rows")
            cols = _parse_int(resize_cols, "resize_cols")
            if rows < 1 or cols < 1:
                raise ValueError("resize_rows and resize_cols must be >= 1")
            nr1, nc1 = r1, c1
            nr2, nc2 = r1 + rows - 1, c1 + cols - 1
            if nr2 > MAX_ROW or nc2 > MAX_COL:
                raise ValueError(
                    f"the resized range would exceed the sheet bounds (it "
                    f"needs rows up to {nr2} and columns up to {nc2})"
                )
            explanation = (
                f"resizing {a.normalized()} from {a.rows}x{a.cols} to "
                f"{rows}x{cols} anchored at its top-left corner"
            )
        area = _make_area(a.sheet, nr1, nc1, nr2, nc2, a.start.abs_row, a.start.abs_col)
        return {
            "status": "ok", "op": op,
            "range_a": a.normalized(),
            "result": area.normalized(), "areas": [area.normalized()],
            "cell_count": area.cell_count,
            "explanation": explanation,
        }

    # -- extract_refs ---------------------------------------------------------
    def _extract_refs_mode(self, formula: Any) -> dict[str, Any]:
        if not isinstance(formula, str) or not formula.strip():
            raise ValueError("formula must be a non-empty formula string")
        if len(formula) > self.max_input_length:
            raise ValueError(
                f"formula exceeds max_input_length={self.max_input_length} characters"
            )
        masked, quoted_count = _mask_quoted(formula)
        # collapse identical repeated sheet prefixes inside ranges
        # (Sheet1!A1:Sheet1!B2 -> Sheet1!A1:B2) before any scanning pass
        masked = _normalize_repeated_sheet(masked)
        matches: list[re.Match] = []
        # pass 1: quoted-sheet references, blanked so their interiors can
        # never leak cell-like tokens into pass 2
        for match in _QUOTED_SHEET_REF_RE.finditer(masked):
            matches.append(match)
            masked = (
                masked[: match.start()]
                + " " * (match.end() - match.start())
                + masked[match.end():]
            )
        # pass 2: blank leftover quoted sheet prefixes (their reference part
        # did not parse), again preventing interior leaks
        masked = _QUOTED_SHEET_PREFIX_RE.sub(
            lambda span: " " * len(span.group(0)), masked
        )
        # pass 3: plain and plain-sheet-qualified references; each match is
        # blanked afterwards so identifier fragments of an extracted
        # reference (the C in C$3) can never leak into the name scan below
        plain_matches = list(_EXTRACT_REF_RE.finditer(masked))
        for probe in plain_matches:
            masked = (
                masked[: probe.start()]
                + " " * (probe.end() - probe.start())
                + masked[probe.end():]
            )
        matches.extend(plain_matches)
        refs: list[dict[str, Any]] = []
        seen: set[str] = set()
        for probe in matches:
            groups = probe.groupdict()
            if groups.get("qsheet") is not None:
                sheet = groups["qsheet"].replace("''", "'")
            else:
                sheet = groups.get("psheet")
            col1 = col_letters_to_index(probe.group("c1col"))
            row1 = int(probe.group("c1row"))
            if col1 > MAX_COL or row1 > MAX_ROW:
                continue  # e.g. XFE1 inside an identifier: not a real reference
            start = {
                "a1": col_index_to_letters(col1) + str(row1),
                "row": row1,
                "col": col1,
                "col_letters": col_index_to_letters(col1),
                "abs_col": probe.group("c1abs") == "$",
                "abs_row": probe.group("c1rowabs") == "$",
            }
            entry: dict[str, Any] = {
                "ref": probe.group(0),
                "kind": "cell",
                "sheet": sheet,
                "cross_sheet": sheet is not None,
                "start": start,
            }
            if probe.group("c2col") is not None:
                col2 = col_letters_to_index(probe.group("c2col"))
                row2 = int(probe.group("c2row"))
                if col2 > MAX_COL or row2 > MAX_ROW:
                    continue
                entry["kind"] = "range"
                entry["end"] = {
                    "a1": col_index_to_letters(col2) + str(row2),
                    "row": row2,
                    "col": col2,
                    "col_letters": col_index_to_letters(col2),
                    "abs_col": probe.group("c2abs") == "$",
                    "abs_row": probe.group("c2rowabs") == "$",
                }
                entry["size"] = {
                    "rows": abs(row2 - row1) + 1,
                    "cols": abs(col2 - col1) + 1,
                }
            if start["abs_row"] and start["abs_col"]:
                entry["addressing"] = "absolute"
            elif start["abs_row"] or start["abs_col"]:
                entry["addressing"] = "mixed"
            else:
                entry["addressing"] = "relative"
            if entry["ref"] not in seen:
                seen.add(entry["ref"])
                refs.append(entry)
            if len(refs) >= self.max_formula_refs:
                break
        names: list[str] = []
        for token in _IDENTIFIER_RE.finditer(masked):
            name = token.group(0)
            after = masked[token.end(): token.end() + 1]
            before = masked[max(0, token.start() - 1): token.start()]
            if after == "(" or after == "!" or before in ("!", "'", "$"):
                # function call, sheet-name part of a reference, or an Excel
                # error literal like #REF!: never a defined-name candidate
                continue
            if _EXTRACT_REF_RE.fullmatch(name) or _R1C1_CELL_RE.match(name):
                continue  # plain cell references are already reported
            if name.upper() in ("TRUE", "FALSE"):
                continue
            if name not in names:
                names.append(name)
            if len(names) >= self.max_formula_refs:
                break
        return {
            "status": "ok",
            "formula_length": len(formula),
            "quoted_strings": quoted_count,
            "refs": refs,
            "ref_count": len(refs),
            "defined_name_candidates": names,
            "note": (
                "references are A1-style tokens found outside double-quoted "
                "strings; identifiers not followed by '(' are reported as "
                "defined-name candidates for information only"
            ),
        }
