#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: csv_lint_tool.py

"""RFC 4180 compliance and data-quality linter for CSV text, built
purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency review/QA layer for
agents that *emit or receive* CSV. Existing common tools consume CSV
but none of them examines its structure: CsvJsonTool converts parsed
CSV to JSON, CSVQueryTool runs SQL-like queries over parsed CSV, and
the knowledge-side readers load files for ingestion — a CSV with
ragged rows, duplicate headers, mixed line terminators or locale
ambiguous numbers currently reaches all of them silently damaged.
CsvLintTool sits in front of them: lint the structure, profile the
columns, or apply safe text-level fixes.

Everything runs offline on the ``csv_text`` string via the standard
``csv`` module in ``strict=True`` mode; no file I/O, no network, no
pandas. Delimiter auto-sniffing reuses the CsvJsonTool (#3738)
counting rule: count ``;`` ``\\t`` ``|`` and ``,`` candidates outside
double-quoted sections, highest count wins, ties prefer the earlier
candidate in that comma-first order, and a text with no outside-quote
candidate at all sniffs to comma.

Row and column numbers are 1-based over *physical records* — the
header is record 1, the first data row record 2 — exactly as the text
is read; a blank line is a record too (reported by CSV009 and then
excluded from the table). ``col`` is the 1-based field index; it is
``None`` for file- or row-level findings. ``value_preview`` shows the
offending cell escaped (``\\r`` ``\\n`` ``\\t``) and capped at 40
characters in its escaped form; cells under a secret-named header
(column names matching password / passwd / pwd / secret / token /
api key / private key / credential, case-insensitive) are masked to
``***`` in previews and in profile top values.

Supported modes
---------------
* ``lint`` — run the rule table below over ``csv_text`` and return
  ``ok`` plus ``findings``. Each finding is ``{code, severity, row,
  col, message, value_preview, hint}``. ``ok`` is True only when no
  finding of severity error or warning was raised (info-only stays
  ok). Findings are sorted by (row, col, code) with ``col=None``
  sorting first, capped at 200 entries (``finding_count`` keeps the
  true total and ``findings_truncated`` flags the cut). When the
  strict reader raises, CSV011 reports the failure at the record
  where it stopped and the remaining rules run over the records
  parsed before the failure.
* ``profile`` — per-column descriptive statistics over the data
  rows: inferred dominant ``type`` (``int`` / ``float`` / ``bool`` /
  ``date`` / ``datetime`` / ``string``, or ``empty`` when a column
  has no non-empty cell), ``nullable``, ``fill_rate`` (non-empty
  cells / rows that have the column, rounded to 4 decimals — short
  rows count as missing), ``distinct_count`` and ``top_values``
  (top 5 by count then value, values masked to ``***`` under
  secret-named headers, counts kept) over non-empty cells, and
  ``min`` / ``max`` over the numerically parseable cells (``None``
  when there are none; int-only columns report ints). Headerless
  input names columns ``col_1..col_N``; ragged long rows contribute
  their extra cells. Type shapes: bool is ``true``/``false``
  case-insensitively; int/float follow the CsvJsonTool family
  patterns (decimal or scientific, finite, and *no* leading zero —
  ``007`` stays a string); dates are ``YYYY-MM-DD`` and datetimes
  ``YYYY-MM-DD[T ]HH:MM[:SS[.f]][Z|±HH[:MM]|±HHMM]`` with
  range-checked month/day/hour/minute/second (a shape match, not a
  calendar check for the year).
* ``fix`` — re-emit the parsed table with safe text-level repairs:
  strip the UTF-8 BOM, drop empty rows, pad short rows to the
  expected width with empty cells, strip leading/trailing whitespace
  from every cell, and normalize the line terminator (``lf`` or
  ``crlf``; quoted multi-line cells keep their embedded newlines).
  Each repair is individually toggleable and only transformations
  that actually changed something are listed in ``applied``.
  ``remaining`` re-lints the fixed text with the same options, so
  what is left is exactly what fixing cannot heal (long rows,
  duplicate or empty header cells, mixed locales, header-only
  files...). Fixing requires a strictly parseable input — malformed
  quoting raises ``ValueError`` instead of being silently re-quoted;
  unnecessary quotes around plain cells are dropped by
  re-serialization (values are preserved).

Expected width and ragged rows
------------------------------
The expected width is the header's field count when ``has_header`` is
True, otherwise the modal (most common) width over the data rows with
ties resolved to the *smaller* width. Data rows narrower than the
expected width fire ``ragged_short``; wider rows fire ``ragged_long``
(which most often means an unquoted delimiter inside a field).
``inconsistent_count`` is the once-per-file summary of the
same problem: it fires when the header plus data rows do not all
share one width, reporting the width breakdown.

Rule table (mode ``lint``)
--------------------------
=========================  ======  =====================================  =========================================================
Code                       Sev.    Trigger (exact)                        Hint
=========================  ======  =====================================  =========================================================
CSV001 bom                 info    the text starts with a UTF-8 BOM       decode with utf-8-sig or strip the BOM before
                                  (``\\ufeff``); it is stripped before   feeding parsers that treat it as part of the first
                                  any parsing, so it pollutes only       header cell
                                  consumers that do not
CSV002 mixed_terminators   warn.   records end with at least two         normalize to one terminator (fix mode with
                                  distinct styles among ``\\r\\n``,       ``terminator='lf'`` or ``'crlf'``); terminators
                                  ``\\n`` and ``\\r`` counted outside     inside quoted cells never count
                                  quotes; reported on the first record
                                  ended by a non-dominant style
                                  (dominant = most frequent, ties by
                                  crlf > lf > cr)
CSV003 ragged_short        warn.   a data row has fewer fields than the   add the missing trailing fields or fix the export
                                  expected width                          (fix mode can pad with empty cells)
CSV004 ragged_long         error   a data row has more fields than the    most often an unquoted delimiter inside a field —
                                  expected width                          quote fields containing the delimiter
CSV005 inconsistent_count  warn.   file-level summary: the header plus    see the per-row ragged findings; align the widths
                                  data rows do not all share one
                                  width (fires once alongside them)
CSV006 empty_header_cell   warn.   a header cell is empty or              give every column a name
                                  whitespace-only
CSV007 duplicate_headers   error   the same header cell text appears      rename the later columns (exact, case-sensitive
                                  more than once (exact text, case-      match)
                                  sensitive)
CSV008 cell_whitespace     info    a cell value has leading or           trim cells (fix mode) — quoted intentional
                                  trailing whitespace, quoted or not     spaces should be excluded from stripping
CSV009 empty_rows          info    one or more records are blank (no      drop them (fix mode) — they usually mean
                                  fields, or a single whitespace-only     trailing newlines or spreadsheet noise
                                  field); reported once, count in the
                                  message, excluded from the table
CSV010 header_only         warn.   ``has_header`` is True and no data    the file carries structure but zero rows
                                  record remains after removing empty
                                  rows
CSV011 unclosed_quote      error   the ``csv`` strict reader raised:      repair the quoting — an unterminated ``"``
                                  an unterminated quote (``unexpected    swallows the rest of the file, a stray quote
                                  end of data``) or a stray quote in     after a closing one splits the field
                                  an unquoted field (``',' expected
                                  after '"'``); row is the record where
                                  the reader stopped, col unavailable
CSV012 mixed_number_locale warn.   a majority-numeric column contains    pick one number format for the export — the two
                                  both dot-decimal cells (``1.5`` /      shapes read as different values under different
                                  ``1.234``) and comma-grouped cells     locales (heuristic, documented: ``1.234`` is
                                  (``1,234`` / ``1,5``) — the two are    itself ambiguous between 1.234 and 1,234)
                                  indistinguishable thousands vs
                                  decimal separators
CSV013 field_over_max_len  warn.   a cell longer than the                 raise max_field_len or fix the source — runaway
                                  ``max_field_len`` option (opt-in,      fields are usually serialization bugs
                                  default off; 1..1000000)
CSV014 over_max_columns    warn.   the expected width exceeds the        split the file or raise the limit — wide CSVs
                                  ``max_columns`` option (opt-in,        are usually export accidents
                                  default off; 1..1000)
=========================  ======  =====================================  =========================================================

Options and error matrix
------------------------
``delimiter`` is None (auto-sniff) or exactly one of ``,`` ``;``
``\\t`` ``|``. ``has_header`` (bool, default True) — with False the
expected width falls back to the modal data width and profile columns
are named ``col_1..col_N``. ``max_field_len`` / ``max_columns``
(integers within their ranges above, default None = rule off) gate
CSV013 / CSV014. ``rules`` maps any implemented rule code to False to
disable that single rule for the call. Fix mode replaces the lint
options with ``strip_whitespace`` / ``drop_empty_rows`` /
``pad_short_rows`` (bools, default True) and ``terminator``
(``lf`` / ``crlf``, default ``lf``). Options are validated per mode —
a lint-only option in profile mode is an error, and vice versa.

``ValueError`` is raised for: an unknown mode; a non-string, empty or
oversized ``csv_text`` (over ``max_input_chars`` = 100,000
characters); more than ``max_rows`` = 10,000 records or a row wider
than ``max_columns`` = 1,000 fields; a text with no non-empty record
at all; malformed options of any kind; and, in fix mode only, input
the strict reader cannot parse. All findings and statistics are exact
and the run is fully deterministic.
"""

import csv
import io
import re
from typing import Any, ClassVar, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Static vocabulary
# ---------------------------------------------------------------------------

# Candidate delimiters for auto-sniffing, in tie-break priority order
# (same rule as CsvJsonTool).
_DELIMITER_CANDIDATES: tuple = (",", ";", "\t", "|")

# Canonical numeric shapes (CsvJsonTool family): decimal or scientific,
# finite, and no leading zero ("007" stays a string).
_INT_PATTERN = re.compile(r"\A[+-]?[0-9]+\Z")
_FLOAT_PATTERN = re.compile(r"\A[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
_LEADING_ZERO = re.compile(r"\A[+-]?0[0-9]")

# Locale ambiguity shapes for CSV012.
_DOT_DECIMAL = re.compile(r"\A[+-]?[0-9]+\.[0-9]+\Z")
_COMMA_DECIMAL = re.compile(r"\A[+-]?[0-9]+,[0-9]+\Z")
_GROUPED_NUMBER = re.compile(r"\A[+-]?[0-9]{1,3}(?:[.,][0-9]{3})+(?:[.,][0-9]+)?\Z")

# Calendar-range-checked date / datetime shapes.
_DATE_PATTERN = re.compile(
    r"\A[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])\Z"
)
_DATETIME_PATTERN = re.compile(
    r"\A[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])"
    r"[T ](?:[01][0-9]|2[0-3]):[0-5][0-9]"
    r"(?::(?:[0-5][0-9]|60)(?:\.[0-9]+)?)?"
    r"(?:Z|[+-](?:[01][0-9]|2[0-3])(?::?[0-5][0-9])?)?\Z"
)

_BOOL_TOKENS = frozenset({"true", "false"})

# Secret-looking header names: values are masked in previews and
# profile top values.
_SECRET_NAME = re.compile(
    r"password|passwd|pwd|secret|token|api[_-]?key|private[_-]?key|credential",
    re.IGNORECASE,
)

# Rule codes -> (slug, severity, hint). Severity is one of the three
# lint severities; ``ok`` is False when any error or warning fires.
_RULES: dict = {
    "CSV001": ("bom", "info",
               "decode with utf-8-sig or strip the BOM before parsing"),
    "CSV002": ("mixed_terminators", "warning",
               "normalize to one terminator (fix mode, terminator option)"),
    "CSV003": ("ragged_short", "warning",
               "add the missing trailing fields or pad them (fix mode)"),
    "CSV004": ("ragged_long", "error",
               "quote fields that contain the delimiter"),
    "CSV005": ("inconsistent_count", "warning",
               "align all rows (and the header) to one field count"),
    "CSV006": ("empty_header_cell", "warning",
               "give every column a name"),
    "CSV007": ("duplicate_headers", "error",
               "rename later duplicate columns"),
    "CSV008": ("cell_whitespace", "info",
               "trim cells (fix mode) or quote intentional spaces"),
    "CSV009": ("empty_rows", "info",
               "drop blank records (fix mode)"),
    "CSV010": ("header_only", "warning",
               "the file has structure but zero data rows"),
    "CSV011": ("unclosed_quote", "error",
               "repair the quoting around the reported record"),
    "CSV012": ("mixed_number_locale", "warning",
               "export numbers in one locale-consistent format"),
    "CSV013": ("field_over_max_len", "warning",
               "raise max_field_len or fix the runaway field"),
    "CSV014": ("over_max_columns", "warning",
               "split the file or raise the max_columns option"),
}
_RULE_CODES: tuple = tuple(_RULES)

# Per-mode option gates for the error matrix.
_LINT_OPTIONS = frozenset(
    {"delimiter", "has_header", "max_field_len", "max_columns", "rules"}
)
_PROFILE_OPTIONS = frozenset({"delimiter", "has_header"})
_FIX_OPTIONS = frozenset(
    {"delimiter", "has_header", "strip_whitespace", "drop_empty_rows",
     "pad_short_rows", "terminator"}
)
_MODE_OPTIONS = {"lint": _LINT_OPTIONS, "profile": _PROFILE_OPTIONS,
                 "fix": _FIX_OPTIONS}

_TYPE_PRIORITY: tuple = ("int", "float", "bool", "date", "datetime", "string")

_TERMINATOR_STYLES: tuple = ("crlf", "lf", "cr")


def _err(message: str) -> ValueError:
    """Return the ValueError every validation branch raises."""
    return ValueError(message)


def _preview(value: str, cap: int = 40) -> str:
    """Escape and cap a cell for a finding's ``value_preview``."""
    text = value.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    if len(text) > cap:
        text = text[: cap - 3] + "..."
    return text


def _sniff_delimiter(text: str) -> str:
    """Count candidate delimiters outside double-quoted sections.

    CsvJsonTool (#3738) counting rule: a state machine toggles the
    in-quote state on every double quote (doubled ``""`` escapes net
    out); the candidate with the highest outside-quote count wins,
    ties prefer the earlier candidate in ``_DELIMITER_CANDIDATES``
    (comma first), and a text with no outside-quote delimiter at all
    sniffs to comma.
    """
    counts = dict.fromkeys(_DELIMITER_CANDIDATES, 0)
    in_quotes = False
    for char in text:
        if char == '"':
            in_quotes = not in_quotes
            continue
        if not in_quotes and char in counts:
            counts[char] += 1
    return max(
        _DELIMITER_CANDIDATES,
        key=lambda candidate: (
            counts[candidate],
            -_DELIMITER_CANDIDATES.index(candidate),
        ),
    )


def _scan_terminators(text: str) -> tuple:
    """Count line terminator styles outside double-quoted sections.

    Returns ``(counts, events)`` where ``counts`` maps ``crlf`` /
    ``lf`` / ``cr`` to occurrence counts and ``events`` lists
    ``(style, ordinal)`` in scan order, the ordinal being the 1-based
    index of the record the terminator ends. Terminators inside
    quoted cells never count.
    """
    counts = {"crlf": 0, "lf": 0, "cr": 0}
    events: list = []
    in_quotes = False
    ordinal = 0
    i = 0
    size = len(text)
    while i < size:
        char = text[i]
        if char == '"':
            in_quotes = not in_quotes
            i += 1
            continue
        if not in_quotes and char == "\r":
            ordinal += 1
            if i + 1 < size and text[i + 1] == "\n":
                counts["crlf"] += 1
                events.append(("crlf", ordinal))
                i += 2
                continue
            counts["cr"] += 1
            events.append(("cr", ordinal))
            i += 1
            continue
        if not in_quotes and char == "\n":
            ordinal += 1
            counts["lf"] += 1
            events.append(("lf", ordinal))
        i += 1
    return counts, events


def _parse_records(text: str, delimiter: str) -> tuple:
    """Strictly parse ``text`` into records, surviving csv errors.

    Returns ``(records, error)``: ``records`` is the list of field
    lists parsed before any failure and ``error`` is
    ``(row, message)`` for the record the strict reader stopped on
    (``len(records) + 1`` — the csv module exposes no finer position),
    or ``None`` when the whole text parsed.
    """
    records: list = []
    reader = csv.reader(
        io.StringIO(text, newline=""), delimiter=delimiter, strict=True
    )
    try:
        for fields in reader:
            records.append(fields)
    except csv.Error as exc:
        return records, (len(records) + 1, str(exc))
    return records, None


def _is_empty_record(fields: list) -> bool:
    """A blank record: no fields, or one whitespace-only field."""
    return not fields or (len(fields) == 1 and not fields[0].strip())


def _build_table(tool: Any, records: list, has_header: bool) -> dict:
    """Split parsed records into header / data / empty and widths.

    Returns ``{"header", "data", "empty_rows", "expected_width",
    "width_counts"}`` where header and data entries are
    ``(row_number, fields)`` with 1-based physical row numbers.
    Raises ValueError when nothing remains or a row exceeds the hard
    column cap.
    """
    empty_rows: list = []
    non_empty: list = []
    for row_no, fields in enumerate(records, 1):
        if _is_empty_record(fields):
            empty_rows.append(row_no)
        else:
            non_empty.append((row_no, fields))
    if not non_empty:
        raise _err("csv_text contains no non-empty record to analyze")

    widest = max(len(fields) for _, fields in non_empty)
    if widest > tool.max_columns:
        raise _err(
            f"input exceeds the {tool.max_columns:,}-column limit "
            f"(got {widest:,} columns)"
        )

    if has_header:
        header = non_empty[0]
        data = non_empty[1:]
        expected_width = len(header[1])
    else:
        header = None
        data = non_empty
        counts: dict = {}
        for _, fields in data:
            width = len(fields)
            counts[width] = counts.get(width, 0) + 1
        # Most common width; ties resolve to the smaller width.
        expected_width = max(counts, key=lambda w: (counts[w], -w))

    width_counts: dict = {}
    for _, fields in ([header] if header is not None else []) + data:
        width = len(fields)
        width_counts[width] = width_counts.get(width, 0) + 1
    return {
        "header": header,
        "data": data,
        "empty_rows": empty_rows,
        "expected_width": expected_width,
        "width_counts": width_counts,
    }


def _classify_cell(value: str) -> str:
    """Classify a non-empty cell into the profile type vocabulary."""
    if value.lower() in _BOOL_TOKENS:
        return "bool"
    if _INT_PATTERN.match(value) and not _LEADING_ZERO.match(value):
        return "int"
    if _FLOAT_PATTERN.match(value) and not _LEADING_ZERO.match(value):
        return "float"
    if _DATE_PATTERN.match(value):
        return "date"
    if _DATETIME_PATTERN.match(value):
        return "datetime"
    return "string"


def _numeric_value(value: str) -> Optional[float]:
    """Parse a canonically numeric cell, else None ("007" is not)."""
    if _INT_PATTERN.match(value) and not _LEADING_ZERO.match(value):
        return int(value)
    if _FLOAT_PATTERN.match(value) and not _LEADING_ZERO.match(value):
        return float(value)
    return None


def _secret_columns(header: Optional[tuple], expected_width: int) -> set:
    """Indices (0-based) of secret-named header columns."""
    if header is None:
        return set()
    return {
        j
        for j in range(min(len(header[1]), expected_width))
        if _SECRET_NAME.search(header[1][j])
    }


def _column_name(header: Optional[tuple], index: int) -> str:
    """Display name for column ``index`` (0-based)."""
    if header is not None and index < len(header[1]) and header[1][index].strip():
        return header[1][index]
    return f"col_{index + 1}"


# ---------------------------------------------------------------------------
# lint mode
# ---------------------------------------------------------------------------

def _run_lint(tool: Any, text: str, delimiter: str, delimiter_sniffed: bool,
              has_header: bool, max_field_len: Optional[int],
              max_columns: Optional[int], disabled: set) -> dict:
    """Run the full rule table; returns the lint result dict."""
    had_bom = text.startswith("\ufeff")
    work_text = text[1:] if had_bom else text

    records, parse_error = _parse_records(work_text, delimiter)
    if len(records) > tool.max_rows:
        raise _err(
            f"input exceeds the {tool.max_rows:,}-record limit "
            f"(got {len(records):,} records)"
        )
    if not records:
        if parse_error is None:
            raise _err(
                "csv_text contains no non-empty record to analyze"
            )
        # The strict reader failed before yielding anything: report
        # the quoting failure itself, there is no table to analyze.
        row, message = parse_error
        return {
            "mode": "lint",
            "ok": False,
            "delimiter": delimiter,
            "delimiter_sniffed": delimiter_sniffed,
            "has_header": has_header,
            "row_count": 0,
            "column_count": 0,
            "finding_count": 1,
            "findings_truncated": False,
            "findings": [{
                "code": "CSV011",
                "severity": "error",
                "row": row,
                "col": None,
                "message": f"malformed quoting: {message}",
                "value_preview": None,
                "hint": _RULES["CSV011"][2],
            }],
        }
    table = _build_table(tool, records, has_header)
    header, data = table["header"], table["data"]
    empty_rows, expected_width = table["empty_rows"], table["expected_width"]

    findings: list = []

    def add(code: str, row: int, col: Optional[int], message: str,
            preview: Optional[str] = None) -> None:
        if code in disabled:
            return
        slug, severity, hint = _RULES[code]
        findings.append({
            "code": code,
            "severity": severity,
            "row": row,
            "col": col,
            "message": message,
            "value_preview": preview,
            "hint": hint,
        })

    secret_cols = _secret_columns(header, expected_width)

    # CSV001 bom
    if had_bom:
        add("CSV001", 1, 1,
            "UTF-8 byte-order mark at the start of the text; stripped "
            "before parsing but it pollutes BOM-unaware consumers")

    # CSV011 unclosed_quote (authoritative parse failure)
    if parse_error is not None:
        row, message = parse_error
        add("CSV011", row, None, f"malformed quoting: {message}")

    # CSV002 mixed_line_terminators
    counts, events = _scan_terminators(work_text)
    styles_seen = [style for style in _TERMINATOR_STYLES if counts[style]]
    if len(styles_seen) > 1:
        dominant = max(
            _TERMINATOR_STYLES,
            key=lambda style: (
                counts[style], -_TERMINATOR_STYLES.index(style)
            ),
        )
        first_row = next(
            ordinal for style, ordinal in events if style != dominant
        )
        breakdown = ", ".join(
            f"{counts[style]} {style.upper()}" for style in styles_seen
        )
        add("CSV002", first_row, None,
            f"mixed line terminators ({breakdown}); dominant style is "
            f"{dominant.upper()}, first differing ending terminates "
            f"record {first_row}")

    # CSV010 header_only
    if has_header and not data:
        add("CSV010", header[0], None,
            f"file contains only a header row (record {header[0]}), no "
            "data records")

    # CSV009 empty_rows (single summary finding)
    if empty_rows:
        shown = ", ".join(str(row) for row in empty_rows[:5])
        suffix = " ..." if len(empty_rows) > 5 else ""
        add("CSV009", empty_rows[0], None,
            f"{len(empty_rows)} empty row(s) at record(s) {shown}{suffix}; "
            "excluded from the table")

    # CSV005 inconsistent_column_count (single summary finding)
    if len(table["width_counts"]) > 1:
        first_offending = next(
            row_no for row_no, fields in
            ([header] if header is not None else []) + data
            if len(fields) != expected_width
        )
        breakdown = ", ".join(
            f"{count} row(s) with {width} field(s)"
            for width, count in sorted(
                table["width_counts"].items(), reverse=True
            )
        )
        source = ("header" if has_header else "modal data width")
        add("CSV005", first_offending, None,
            f"inconsistent field counts: {breakdown}; expected "
            f"{expected_width} from the {source}")

    # CSV003 / CSV004 ragged rows
    for row_no, fields in data:
        width = len(fields)
        if width < expected_width:
            add("CSV003", row_no, None,
                f"row has {width} field(s), expected {expected_width}")
        elif width > expected_width:
            add("CSV004", row_no, None,
                f"row has {width} field(s), expected {expected_width}")

    # Header rules
    if header is not None:
        seen: dict = {}
        for index, cell in enumerate(header[1]):
            col = index + 1
            if not cell.strip():
                add("CSV006", header[0], col,
                    f"header cell {col} is empty or whitespace-only",
                    _preview(cell))
            if cell in seen:
                add("CSV007", header[0], col,
                    f"duplicate header {cell!r} (first seen at column "
                    f"{seen[cell]})")
            else:
                seen[cell] = col

    # CSV008 cell whitespace (header and data cells)
    scanned = [header] if header is not None else []
    scanned += data
    for row_no, fields in scanned:
        for index, cell in enumerate(fields):
            if cell != cell.strip():
                preview = "***" if index in secret_cols else _preview(cell)
                add("CSV008", row_no, index + 1,
                    f"cell has leading/trailing whitespace "
                    f"({len(cell) - len(cell.strip())} character(s))",
                    preview)

    # CSV012 numeric_column_mixed_locale
    for index in range(expected_width):
        cells = [
            fields[index] for _, fields in data
            if len(fields) > index and fields[index].strip()
        ]
        if len(cells) < 2:
            continue
        numeric = [
            cell for cell in cells
            if (_numeric_value(cell) is not None
                or _COMMA_DECIMAL.match(cell)
                or _GROUPED_NUMBER.match(cell))
        ]
        if len(numeric) * 2 <= len(cells):
            continue
        has_dot = any(_DOT_DECIMAL.match(cell) for cell in cells)
        has_comma = any(_COMMA_DECIMAL.match(cell) for cell in cells)
        if has_dot and has_comma:
            first_row = next(
                row_no for row_no, fields in data
                if len(fields) > index
                and _COMMA_DECIMAL.match(fields[index])
            )
            name = _column_name(header, index)
            add("CSV012", first_row, index + 1,
                f'column "{name}" mixes dot-decimal ("1.5" / "1.234") and '
                'comma-grouped ("1,234" / "1,5") number shapes — '
                "indistinguishable thousands vs decimal separators "
                "(heuristic)")

    # CSV013 field_over_max_len (opt-in)
    if max_field_len is not None:
        for row_no, fields in scanned:
            for index, cell in enumerate(fields):
                if len(cell) > max_field_len:
                    preview = "***" if index in secret_cols else _preview(cell)
                    add("CSV013", row_no, index + 1,
                        f"field length {len(cell)} exceeds max_field_len "
                        f"{max_field_len}", preview)

    # CSV014 over_max_columns (opt-in)
    if max_columns is not None and expected_width > max_columns:
        add("CSV014", 1, None,
            f"table width {expected_width} exceeds max_columns "
            f"{max_columns}")

    findings.sort(
        key=lambda finding: (
            finding["row"], finding["col"] or 0, finding["code"]
        )
    )
    total = len(findings)
    truncated = total > tool.MAX_FINDINGS
    ok = not any(
        finding["severity"] in ("error", "warning")
        for finding in findings
    )
    return {
        "mode": "lint",
        "ok": ok,
        "delimiter": delimiter,
        "delimiter_sniffed": delimiter_sniffed,
        "has_header": has_header,
        "row_count": len(data),
        "column_count": expected_width,
        "finding_count": total,
        "findings_truncated": truncated,
        "findings": findings[: tool.MAX_FINDINGS],
    }


# ---------------------------------------------------------------------------
# profile mode
# ---------------------------------------------------------------------------

def _run_profile(tool: Any, text: str, delimiter: str,
                 delimiter_sniffed: bool, has_header: bool) -> dict:
    """Profile every column of the parsed table."""
    had_bom = text.startswith("\ufeff")
    work_text = text[1:] if had_bom else text
    records, parse_error = _parse_records(work_text, delimiter)
    if parse_error is not None:
        row, message = parse_error
        raise _err(
            f"profile needs a strictly parseable csv_text: malformed "
            f"quoting at record {row} ({message}); run lint mode first"
        )
    if len(records) > tool.max_rows:
        raise _err(
            f"input exceeds the {tool.max_rows:,}-record limit "
            f"(got {len(records):,} records)"
        )
    table = _build_table(tool, records, has_header)
    header, data = table["header"], table["data"]

    # Profile every column any row provides — ragged long rows
    # contribute their extra cells.
    widest = max(
        len(fields)
        for _, fields in ([header] if header is not None else []) + data
    )

    columns: list = []
    for index in range(widest):
        name = _column_name(header, index)
        secret = bool(_SECRET_NAME.search(name))
        cells = [
            fields[index] for _, fields in data if len(fields) > index
        ]
        non_null = [cell for cell in cells if cell.strip()]

        type_counts: dict = {}
        for cell in non_null:
            kind = _classify_cell(cell)
            type_counts[kind] = type_counts.get(kind, 0) + 1
        if type_counts:
            dominant = max(
                type_counts.items(),
                key=lambda item: (
                    item[1], -_TYPE_PRIORITY.index(item[0])
                ),
            )[0]
        else:
            dominant = "empty"

        value_counts: dict = {}
        for cell in non_null:
            value_counts[cell] = value_counts.get(cell, 0) + 1
        top = sorted(value_counts.items(), key=lambda item: (-item[1], item[0]))
        top_values = [
            {"value": "***" if secret else value, "count": count}
            for value, count in top[: tool.TOP_VALUES_LIMIT]
        ]

        numeric = [
            value for value in
            (_numeric_value(cell) for cell in non_null)
            if value is not None
        ]
        if numeric:
            as_float = any(isinstance(value, float) for value in numeric)
            minimum = min(numeric)
            maximum = max(numeric)
            if as_float:
                minimum, maximum = float(minimum), float(maximum)
        else:
            minimum = maximum = None

        columns.append({
            "name": name,
            "index": index + 1,
            "type": dominant,
            "nullable": len(non_null) < len(cells),
            "fill_rate": round(len(non_null) / len(cells), 4) if cells else 0.0,
            "distinct_count": len(value_counts),
            "top_values": top_values,
            "min": minimum,
            "max": maximum,
        })

    return {
        "mode": "profile",
        "delimiter": delimiter,
        "delimiter_sniffed": delimiter_sniffed,
        "has_header": has_header,
        "row_count": len(data),
        "column_count": widest,
        "columns": columns,
    }


# ---------------------------------------------------------------------------
# fix mode
# ---------------------------------------------------------------------------

def _run_fix(tool: Any, text: str, delimiter: str, delimiter_sniffed: bool,
             has_header: bool, strip_whitespace: bool,
             drop_empty_rows: bool, pad_short_rows: bool,
             terminator: str, max_field_len: Optional[int],
             max_columns: Optional[int]) -> dict:
    """Apply safe text-level repairs and re-lint the result."""
    had_bom = text.startswith("\ufeff")
    work_text = text[1:] if had_bom else text
    records, parse_error = _parse_records(work_text, delimiter)
    if parse_error is not None:
        row, message = parse_error
        raise _err(
            f"fix needs a strictly parseable csv_text: malformed quoting "
            f"at record {row} ({message}); run lint mode first"
        )
    if len(records) > tool.max_rows:
        raise _err(
            f"input exceeds the {tool.max_rows:,}-record limit "
            f"(got {len(records):,} records)"
        )

    kept: list = []
    dropped_empty = 0
    for row_no, fields in enumerate(records, 1):
        if drop_empty_rows and _is_empty_record(fields):
            dropped_empty += 1
            continue
        kept.append((row_no, fields))
    if not kept:
        raise _err("nothing to fix: no non-empty record remains")

    widest = max(len(fields) for _, fields in kept)
    if widest > tool.max_columns:
        raise _err(
            f"input exceeds the {tool.max_columns:,}-column limit "
            f"(got {widest:,} columns)"
        )

    if has_header:
        header = kept[0]
        data = kept[1:]
        expected_width = len(header[1])
    else:
        header = None
        data = kept
        counts: dict = {}
        for _, fields in data:
            width = len(fields)
            counts[width] = counts.get(width, 0) + 1
        expected_width = max(counts, key=lambda w: (counts[w], -w)) if counts \
            else 0

    padded = 0
    if pad_short_rows:
        # Zero-field records are kept blank lines (drop_empty_rows
        # False), not rows to pad.
        padded = sum(
            1 for row_no, fields in kept[1 if has_header else 0:]
            if 0 < len(fields) < expected_width
        )
        data = [
            (row_no, fields + [""] * (expected_width - len(fields))
             if 0 < len(fields) < expected_width else fields)
            for row_no, fields in data
        ]

    stripped = 0
    if strip_whitespace:
        trimmed: list = []
        for row_no, fields in ([header] if header is not None else []) + data:
            new_fields = []
            for cell in fields:
                trimmed_cell = cell.strip()
                if trimmed_cell != cell:
                    stripped += 1
                new_fields.append(trimmed_cell)
            trimmed.append((row_no, new_fields))
        if header is not None:
            header = trimmed[0]
            data = trimmed[1:]
        else:
            data = trimmed

    out_rows = ([header[1]] if header is not None else []) + [
        fields for _, fields in data
    ]
    buffer = io.StringIO()
    writer = csv.writer(
        buffer,
        delimiter=delimiter,
        lineterminator="\r\n" if terminator == "crlf" else "\n",
    )
    for fields in out_rows:
        writer.writerow(fields)
    fixed_text = buffer.getvalue()

    applied: list = []
    if had_bom:
        applied.append({"action": "strip_bom"})
    counts, _events = _scan_terminators(work_text)
    others = {
        "lf": counts["cr"] + counts["crlf"],
        "crlf": counts["lf"] + counts["cr"],
    }
    if others[terminator]:
        applied.append({"action": "normalize_terminator", "to": terminator})
    if dropped_empty:
        applied.append({"action": "drop_empty_rows", "count": dropped_empty})
    if padded:
        applied.append({"action": "pad_short_rows", "count": padded})
    if stripped:
        applied.append({"action": "strip_cell_whitespace", "count": stripped})

    relint = _run_lint(
        tool, fixed_text, delimiter, delimiter_sniffed=False,
        has_header=has_header, max_field_len=max_field_len,
        max_columns=max_columns, disabled=frozenset(),
    )
    return {
        "mode": "fix",
        "delimiter": delimiter,
        "delimiter_sniffed": delimiter_sniffed,
        "has_header": has_header,
        "fixed_text": fixed_text,
        "applied": applied,
        "row_count": relint["row_count"],
        "column_count": relint["column_count"],
        "remaining_count": relint["finding_count"],
        "remaining_truncated": relint["findings_truncated"],
        "remaining": relint["findings"],
    }


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class CsvLintTool(Tool):
    """RFC 4180 compliance and data-quality linter for CSV text, built
    purely on the stdlib.

    The tool never touches the filesystem or the network — it examines
    CSV *text* with the standard ``csv`` module in strict mode: lint
    its structure against the documented rule table, profile its
    columns, or apply safe text-level fixes. See the module docstring
    for the full rule table, the mode reference and the heuristics
    notes.

    Class attributes:
        MODES (tuple): Supported modes (lint, profile, fix).
        RULE_CODES (tuple): All implemented rule codes.
        MAX_FIELD_LEN_LIMIT (int): Upper bound for max_field_len.
        MAX_FINDINGS (int): Findings list cap per lint run.
        TOP_VALUES_LIMIT (int): top_values entries per profiled column.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "csv_lint_tool"
    description: str = (
        "CSV text compliance and quality linter — pure Python stdlib "
        "csv module in strict mode, no files, no network. lint mode "
        "checks RFC 4180 structure against a documented 14-rule table "
        "(BOM, mixed line terminators, ragged short/long rows, "
        "inconsistent field counts, empty or duplicate header cells, "
        "cell whitespace, empty rows, header-only files, unclosed or "
        "stray quotes with the failing record, mixed number locales, "
        "opt-in field length and column count caps), each finding "
        "carrying severity, 1-based row/column and a capped escaped "
        "value preview masked under secret-named headers; profile mode "
        "infers per-column types (int/float/bool/date/datetime/string), "
        "nullability, fill rate, distinct count, top values and numeric "
        "min/max; fix mode re-emits the table with BOM strip, empty-row "
        "drop, short-row padding, cell whitespace strip and terminator "
        "normalization, listing applied repairs and re-linting what "
        "remains. Delimiter is auto-sniffed (outside-quote counting, "
        "comma-first ties) or set explicitly among , ; tab |."
    )

    MODES: ClassVar[tuple] = ("lint", "profile", "fix")
    RULE_CODES: ClassVar[tuple] = _RULE_CODES
    MAX_FIELD_LEN_LIMIT: ClassVar[int] = 1_000_000
    MAX_FINDINGS: ClassVar[int] = 200
    TOP_VALUES_LIMIT: ClassVar[int] = 5

    max_input_chars: int = 100_000
    max_rows: int = 10_000
    max_columns: int = 1_000

    def execute(
        self,
        mode: Any = None,
        csv_text: Any = None,
        delimiter: Any = None,
        has_header: Any = None,
        max_field_len: Any = None,
        max_columns: Any = None,
        rules: Any = None,
        strip_whitespace: Any = None,
        drop_empty_rows: Any = None,
        pad_short_rows: Any = None,
        terminator: Any = None,
    ) -> dict:
        """Lint, profile or fix CSV text.

        Args:
            mode (str): One of ``lint``, ``profile`` or ``fix``.
            csv_text (str): The CSV text. A single leading UTF-8 BOM
                is stripped before any parsing or sniffing and
                reported by rule CSV001.
            delimiter (str): Optional explicit delimiter, one of
                ``,`` ``;`` ``\\t`` ``|``. When omitted the delimiter
                is sniffed by counting candidates outside quoted
                sections (comma wins ties); a text with no candidate
                sniffs to comma.
            has_header (bool): Treat record 1 as a header. Default
                True. With False the expected width is the modal data
                width and profile columns are named col_1..col_N.
            max_field_len (int): Turn rule CSV013 on with this field
                length threshold. Default None (off). Range
                1..1000000. Lint mode only.
            max_columns (int): Turn rule CSV014 on with this column
                count threshold. Default None (off). Range 1..1000.
                Lint mode only.
            rules (dict): Map a rule code (CSV001..CSV014) to False to
                disable that single rule for the call. Lint mode only.
            strip_whitespace (bool): Strip leading/trailing whitespace
                from every cell in fix mode. Default True. Fix mode
                only.
            drop_empty_rows (bool): Drop blank records in fix mode.
                Default True. Fix mode only.
            pad_short_rows (bool): Pad short rows to the expected
                width with empty cells in fix mode. Default True. Fix
                mode only.
            terminator (str): Line terminator for the fixed text,
                ``lf`` or ``crlf``. Default ``lf``. Fix mode only.

        Returns:
            dict: ``lint`` → ``{mode, ok, delimiter,
            delimiter_sniffed, has_header, row_count, column_count,
            finding_count, findings_truncated, findings}`` with each
            finding ``{code, severity, row, col, message,
            value_preview, hint}``; ``profile`` → ``{mode, delimiter,
            delimiter_sniffed, has_header, row_count, column_count,
            columns}`` with each column ``{name, index, type,
            nullable, fill_rate, distinct_count, top_values, min,
            max}``; ``fix`` → ``{mode, delimiter, delimiter_sniffed,
            has_header, fixed_text, applied, row_count, column_count,
            remaining_count, remaining_truncated, remaining}``.

        Raises:
            ValueError: If any argument is malformed, the input is
                empty or oversized, no non-empty record remains, a
                row exceeds the hard column cap — or, in profile and
                fix modes, the strict reader cannot parse the text.
        """
        if mode not in self.MODES:
            raise _err(f"mode must be one of {self.MODES}, got {mode!r}")

        provided = {
            "delimiter": delimiter, "has_header": has_header,
            "max_field_len": max_field_len, "max_columns": max_columns,
            "rules": rules, "strip_whitespace": strip_whitespace,
            "drop_empty_rows": drop_empty_rows,
            "pad_short_rows": pad_short_rows, "terminator": terminator,
        }
        for option, value in provided.items():
            if value is not None and option not in _MODE_OPTIONS[mode]:
                raise _err(
                    f"{option!r} is not a {mode} mode option "
                    f"(allowed: {sorted(_MODE_OPTIONS[mode])})"
                )

        if not isinstance(csv_text, str):
            raise _err(
                f"csv_text must be a string, got {type(csv_text).__name__}"
            )
        if not csv_text:
            raise _err("csv_text must be non-empty")
        if len(csv_text) > self.max_input_chars:
            raise _err(
                f"csv_text exceeds the {self.max_input_chars:,}-character "
                f"limit (got {len(csv_text):,} characters)"
            )

        delimiter = self._resolve_delimiter(delimiter)
        delimiter_sniffed = False
        if delimiter is None:
            delimiter = _sniff_delimiter(
                csv_text[1:] if csv_text.startswith("\ufeff") else csv_text
            )
            delimiter_sniffed = True
        if has_header is None:
            has_header = True
        if not isinstance(has_header, bool):
            raise _err(
                f"has_header must be a boolean, got {has_header!r}"
            )

        if mode == "lint":
            max_field_len = self._resolve_bounded_int(
                "max_field_len", max_field_len, 1, self.MAX_FIELD_LEN_LIMIT
            )
            max_columns = self._resolve_bounded_int(
                "max_columns", max_columns, 1, self.max_columns
            )
            disabled = self._resolve_rules(rules)
            return _run_lint(
                self, csv_text, delimiter, delimiter_sniffed, has_header,
                max_field_len, max_columns, disabled,
            )
        if mode == "profile":
            return _run_profile(
                self, csv_text, delimiter, delimiter_sniffed, has_header
            )
        for option, value in (
            ("strip_whitespace", strip_whitespace),
            ("drop_empty_rows", drop_empty_rows),
            ("pad_short_rows", pad_short_rows),
        ):
            if value is not None and not isinstance(value, bool):
                raise _err(f"{option} must be a boolean, got {value!r}")
        if terminator is None:
            terminator = "lf"
        if terminator not in ("lf", "crlf"):
            raise _err(
                f"terminator must be 'lf' or 'crlf', got {terminator!r}"
            )
        return _run_fix(
            self, csv_text, delimiter, delimiter_sniffed, has_header,
            True if strip_whitespace is None else strip_whitespace,
            True if drop_empty_rows is None else drop_empty_rows,
            True if pad_short_rows is None else pad_short_rows,
            terminator, None, None,
        )

    # -- validation helpers ------------------------------------------------

    @classmethod
    def _resolve_delimiter(cls, delimiter: Any) -> Any:
        """Validate the optional explicit ``delimiter``."""
        if delimiter is None:
            return None
        if not isinstance(delimiter, str) or \
                delimiter not in _DELIMITER_CANDIDATES:
            raise _err(
                f"delimiter must be None or one of "
                f"{list(_DELIMITER_CANDIDATES)}, got {delimiter!r}"
            )
        return delimiter

    @classmethod
    def _resolve_bounded_int(cls, name: str, value: Any, low: int,
                             high: int) -> Any:
        """Validate an optional integer option within [low, high]."""
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise _err(f"{name} must be an integer, got {value!r}")
        if not low <= value <= high:
            raise _err(f"{name} must be between {low} and {high}, got {value}")
        return value

    @classmethod
    def _resolve_rules(cls, rules: Any) -> frozenset:
        """Validate the per-rule disable map; returns disabled codes."""
        if rules is None:
            return frozenset()
        if not isinstance(rules, dict):
            raise _err(
                f"rules must be a dict, got {type(rules).__name__}"
            )
        disabled = set()
        for key, value in rules.items():
            if key not in _RULES:
                raise _err(
                    f"rules keys must be one of {list(_RULE_CODES)}, "
                    f"got {key!r}"
                )
            if not isinstance(value, bool):
                raise _err(
                    f"rules[{key!r}] must be a boolean, got {value!r}"
                )
            if not value:
                disabled.add(key)
        return frozenset(disabled)
