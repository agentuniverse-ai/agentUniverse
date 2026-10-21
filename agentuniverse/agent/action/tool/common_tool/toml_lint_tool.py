#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: toml_lint_tool.py

"""Quality and style linter for TOML text, built purely on the
stdlib ``tomllib`` parser plus a comment-stripped raw-text scan.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency review/QA layer for
agents that *emit or receive* TOML configuration. Parsing TOML is
already solved dependency-free — TomlTool (#3730) parses, validates
and resolves paths — but *nothing* examines the quality of a
document: an array that mixes ints and strings, a file that mixes
tab and space indentation, inconsistent digit grouping, or a
15-level-deep tree all parse cleanly and reach every consumer
silently. TomlLintTool sits in front of the readers: lint the
document, profile its shape, or ask for the safe textual fixes.

Everything runs offline on the ``toml_text`` string. Syntax problems
are delegated to the ``tomllib`` parser (the TOML 1.0 parser shipped
with Python 3.11+, provided by the ``tomli`` backport on Python 3.10);
style and quality rules run on a
same-length *masked* copy of the text in which string contents are
replaced by a sentinel byte and comments by blanks — so raw-text
checks never fire inside strings or comments, yet every character
offset still maps 1:1 back to the original document. No file I/O, no
network, no third-party packages.

Findings carry 1-based ``line`` and ``col`` (``col`` is ``None``
when tomllib reports the end of the document or no column applies),
a ``severity`` (error / warning / info) and a ``hint``. ``ok`` is
True only when no error or warning fired — info-only documents stay
ok.

Verified tomllib ground truths (each drives a rule below)
---------------------------------------------------------
* A leading UTF-8 BOM is **rejected** by tomllib ("Invalid
  statement", line 1, column 1) — reported as TOML001, stripped
  before parsing.
* Duplicate table headers (``[x]`` twice), duplicate keys within a
  table (``a = 1`` then ``a = 2``), multi-line inline tables, the
  capitalized booleans ``True`` / ``TRUE`` and every other malformed
  shape are **errors** raised by tomllib — surfaced as TOML002 with
  the position tomllib embeds in its message. No duplicate
  detection is re-implemented. This includes the hard version of
  the style clash: populating one table both via ``a.b = 1`` and
  via ``[a]`` is a tomllib "Cannot declare twice" error, so only
  the softer document-level style mix (TOML010) is a lint rule.
* Arrays mixing scalar types (``[1, "two"]``) and arrays mixing
  offset-aware with naive datetimes are **legal** — reported as
  the info rules TOML003 / TOML004.
* Tab indentation is legal — TOML006 fires only when tab-led and
  space-led lines are mixed.

Supported modes
---------------
* ``lint`` — run the rule table below over ``toml_text`` and return
  ``ok``, ``valid`` (whether tomllib accepted the document) and
  ``findings``. Each finding is ``{code, severity, line, col,
  message, hint}``. Line-level rules (TOML001, TOML005..TOML007)
  run on every document; parse-dependent rules are skipped when
  tomllib rejects the text (its error is the TOML002 finding).
  Findings are sorted by (line, col with None first, code), capped
  at 200 entries (``finding_count`` keeps the true total and
  ``findings_truncated`` flags the cut).
* ``profile`` — aggregate shape of the parsed document: ``tables``
  (dict containers excluding the root, arrays-of-tables entries
  included), ``arrays_of_tables`` (the number of ``[[x]]`` header
  paths), ``keys`` (leaf key/value pairs — scalars and arrays;
  array elements are not separate keys), ``scalar_type_histogram``
  (leaf types incl. date / datetime / time; homogeneous scalar
  arrays as ``array<type>``, mixed as ``array<mixed>``, empty as
  ``array<empty>``, sorted by count then name), ``max_depth`` and
  ``deepest_path`` (path length in segments — dotted keys and
  nested headers both count). Requires a valid document.
* ``fix_hints`` — apply the safe **textual-only** repairs: strip
  the UTF-8 BOM and remove trailing whitespace outside multiline
  strings (interior whitespace of multi-line basic / literal
  strings is preserved byte-for-byte). Never structural: values,
  tables, arrays, comments and line terminators are never
  re-serialized — a syntactically broken input is still fixed only
  where text-level repair is unambiguous, and ``remaining``
  re-lints the fixed text with the default options so exactly what
  fixing cannot heal (every structural problem) stays visible.

Rule table (mode ``lint``)
--------------------------
===========================  ======  =====================================  ==========================================================
Code                        Sev.    Trigger (exact)                        Hint
===========================  ======  =====================================  ==========================================================
TOML001 bom                 warn.   the text starts with a UTF-8 BOM       decode with utf-8-sig or strip the BOM — the TOML spec
                                    (``\\ufeff``); tomllib rejects it,      forbids it and tomllib raises on it (fix_hints strips it)
                                    so it is stripped before parsing
                                    here
TOML002 syntax_error        error   ``tomllib.TOMLDecodeError``: the       fix the reported position — tomllib stops at the first
                                    document is not valid TOML 1.0 —       error; duplicate table headers, duplicate keys,
                                    covers malformed values, unterminated  multi-line inline tables, capitalized True/False and
                                    strings, duplicate table headers       every other parse error land here
                                    / keys, multi-line inline tables,
                                    ``True``/``TRUE`` booleans; line/col
                                    from the position tomllib embeds in
                                    its message (end-of-document errors
                                    map to the last line, col None)
TOML003 mixed_array_types   info    a top-level array value mixes two      legal but risky — consumers must branch per element;
                                    or more scalar classes among its       split the array or keep one scalar type per array
                                    direct elements (bool / number —
                                    ints and floats are one class —
                                    string / datetime / date / time);
                                    nested arrays and inline tables
                                    do not participate
TOML004 datetime_mixed_     info    a top-level array's direct datetime    pick offset-aware (``Z`` / ``+HH:MM``) or naive local
      offsets                       elements mix offset-aware and          datetimes within one array — silently comparing them
                                    naive local datetimes (both are        is a classic aware-vs-naive bug
                                    legal TOML)
TOML005 trailing_spaces     info    one or more lines end with             trim the trailing whitespace (fix_hints mode) —
                                    whitespace outside multiline strings;  whitespace inside multi-line strings is preserved
                                    reported once, first offending line,
                                    total count in the message
TOML006 mixed_indent_       info    indented lines (outside multiline     pick one indentation style — spaces are the common
      styles                         strings) mix tab-led and space-led    choice; tabs are legal TOML, mixing them is not style
                                    indentation (both styles present);    — a run holding both tab and space counts as its
                                    reported once with the per-style       own "mixed" class
                                    line counts and first clashing line
TOML007 number_underscores_ info    the document uses both digit-grouped  group digits consistently — ``1_000`` everywhere or
      style                         numeric literals (``1_000``,          plain literals everywhere (both are legal TOML)
                                    ``0xdead_beef``) and plain long
                                    literals (``100000``, ``0xdeadbeef``,
                                    5+ digits); reported once at the
                                    first grouped literal
TOML008 empty_table         warn.   a header-declared table (``[x]`` or    populate it, drop the header, or comment why it is
                                    a ``[[x]]`` entry) contains no keys   intentionally empty; inline ``x = {}`` values are
                                    and no sub-tables at all              not flagged
TOML009 deeply_nested       info    the longest key path in the parsed    flatten the configuration — deep nesting is hard to
                                    document exceeds ``max_depth``        read and to override
                                    path segments (default 12, dotted
                                    keys and nested headers both count);
                                    reported once with the deepest path
TOML010 table_style_mixed   info    the document defines sub-tables via   pick one style per document — the hard clash (one
                                    both styles: dotted keys              table populated both ways) is a tomllib error and
                                    (``a.b = 1``, 2+ key segments) and    lands in TOML002; this reports the softer mix that
                                    headers whose section holds direct    still parses
                                    keys (``[x]`` + single-segment keys);
                                    reported once at the first dotted
                                    key
===========================  ======  =====================================  ==========================================================

Options and error matrix
------------------------
``rules`` maps any implemented rule code to False to disable that
single rule for the call (lint mode only). ``max_depth`` (int,
1..128, default 12) is the TOML009 threshold (lint mode only).

``ValueError`` is raised for: an unknown mode; a lint-only option in
another mode; a non-string, empty or oversized ``toml_text`` (over
``max_input_chars`` = 1,048,576 characters — 1 MiB); a malformed
``rules`` map (unknown code or non-boolean value); ``max_depth``
outside 1..128; and, in ``profile`` mode only, a document tomllib
cannot parse (the decode message is reported). A document whose
nesting exceeds the Python recursion limit raises ``ValueError`` in
every mode (tomllib cannot parse it, or the walk cannot descend it).
``lint`` and ``fix_hints`` never raise on any other content — a
broken document is a finding, not an exception. All findings and
statistics are exact and the run is fully deterministic.
"""

import datetime
import re
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from bisect import bisect_right
from typing import Any, ClassVar, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Static vocabulary
# ---------------------------------------------------------------------------

# Rule codes -> (slug, severity, hint). ``ok`` is False when any error
# or warning fires; info-only documents stay ok.
_RULES: dict = {
    "TOML001": ("bom", "warning",
                "decode with utf-8-sig or strip the BOM — the TOML spec "
                "forbids it and tomllib raises on it (fix_hints strips it)"),
    "TOML002": ("syntax_error", "error",
                "fix the reported position — tomllib stops at the first "
                "error; duplicate tables/keys, multi-line inline tables "
                "and capitalized booleans all land here"),
    "TOML003": ("mixed_array_types", "info",
                "legal but risky — consumers must branch per element; "
                "split the array or keep one scalar type per array"),
    "TOML004": ("datetime_mixed_offsets", "info",
                "pick offset-aware (Z or +HH:MM) or naive local datetimes "
                "within one array — comparing the two is a classic bug"),
    "TOML005": ("trailing_spaces", "info",
                "trim the trailing whitespace (fix_hints mode)"),
    "TOML006": ("mixed_indent_styles", "info",
                "pick one indentation style — spaces are the common "
                "choice; tabs are legal, mixing them is not style"),
    "TOML007": ("number_underscores_style", "info",
                "group digits consistently — 1_000 everywhere or plain "
                "literals everywhere (both are legal TOML)"),
    "TOML008": ("empty_table", "warning",
                "populate it, drop the header, or comment why it is "
                "intentionally empty"),
    "TOML009": ("deeply_nested", "info",
                "flatten the configuration — deep nesting is hard to "
                "read and to override"),
    "TOML010": ("table_style_mixed", "info",
                "pick one style per document — dotted keys or headers; "
                "the hard clash (one table both ways) is a tomllib "
                "error and lands in TOML002"),
}
_RULE_CODES: tuple = tuple(_RULES)

# Per-mode option gates for the error matrix.
_MODE_OPTIONS: dict = {
    "lint": frozenset({"rules", "max_depth"}),
    "profile": frozenset(),
    "fix_hints": frozenset(),
}

# tomllib embeds the error position in the message as
# "(at line 3, column 5)" or reports "(at end of document)".
_TOML_POSITION = re.compile(r"\(at line (\d+), column (\d+)\)\s*\Z")
_TOML_END_OF_DOC = "(at end of document)"
_TOML_POSITION_ANY = re.compile(
    r"\s*\(at (?:line \d+, column \d+|end of document)\)\s*\Z"
)

# String-content sentinel for the masked text: a control byte that can
# never appear in TOML code outside strings (bare keys and values are
# ASCII printable plus whitespace).
_SENTINEL = "\x00"

# Bare key characters (TOML 1.0).
_BARE_KEY = re.compile(r"[A-Za-z0-9_-]+")

# Element shapes over masked text (strings appear as "..." / '...' with
# sentinel content; sentinel never matches these alphabets).
_ELEM_BOOL = re.compile(r"(?:true|false)\Z")
_ELEM_DATETIME = re.compile(
    r"\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?"
    r"(?:[Zz]|[+-]\d{2}:\d{2})?\Z"
)
_ELEM_DATETIME_OFFSET = re.compile(r"(?:[Zz]|[+-]\d{2}:\d{2})\Z")
_ELEM_DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
_ELEM_TIME = re.compile(r"\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?\Z")
_ELEM_INT = re.compile(
    r"[+-]?(?:0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+"
    r"|[0-9][0-9_]*)\Z"
)
_ELEM_FLOAT = re.compile(
    r"[+-]?(?:[0-9][0-9_]*(?:\.[0-9][0-9_]*)?"
    r"(?:[eE][+-]?[0-9][0-9_]*)?|inf|nan)\Z"
)

# Digit-grouped numeric literals (legal TOML, style question) and the
# plain 5+-digit literals they may be inconsistently mixed with.
_UNDERSCORED_NUMBER = re.compile(
    r"(?<![\w.])[+-]?(?:0[xX][0-9a-fA-F_]*_[0-9a-fA-F_]*"
    r"|0[oO][0-7_]*_[0-7_]*|0[bB][01_]*_[01_]*"
    r"|[0-9][0-9_]*_[0-9_]*(?:\.[0-9_]+)?(?:[eE][+-]?[0-9_]+)?)"
    r"(?![\w.])"
)
_PLAIN_LONG_NUMBER = re.compile(
    r"(?<![\w._])[+-]?(?:0[xX][0-9a-fA-F]{4,}|0[oO][0-7]{4,}"
    r"|0[bB][01]{4,}|[0-9]{5,})(?![\w._])"
)

_TRAILING_WS = re.compile(r"[ \t]+\Z")
_LEADING_WS = re.compile(r"[ \t]+")  # used with .match() — start-anchored


def _err(message: str) -> ValueError:
    """Return the ValueError every validation branch raises."""
    return ValueError(message)


# ---------------------------------------------------------------------------
# Masked text — string contents become sentinel bytes, comments blanks
# ---------------------------------------------------------------------------

def _mask_text(text: str) -> str:
    """Return a same-length copy with string contents and comments erased.

    Basic and literal strings (single-line and multi-line) keep their
    quote delimiters but have every content byte — escapes included —
    replaced by ``_SENTINEL``; comments become blanks. Every offset in
    the result therefore maps 1:1 to the original text, and no
    raw-text pattern can ever match inside a string or a comment. An
    unterminated string masks to the end of the text; tomllib reports
    the syntax error itself. In a multi-line string up to two quote
    characters may sit in the content directly before the closing
    delimiter — they are masked as content, never as a closer.
    """
    out: list = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "#":
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
        elif ch == '"' or ch == "'":
            delim = ch * 3 if text.startswith(ch * 3, i) else ch
            dlen = len(delim)
            out.append(delim)
            i += dlen
            escaped = False
            while i < n:
                c = text[i]
                if escaped:
                    escaped = False
                    out.append(_SENTINEL)
                    i += 1
                elif c == "\\" and ch == '"':
                    # Escapes exist only in basic strings.
                    escaped = True
                    out.append(_SENTINEL)
                    i += 1
                elif text.startswith(delim, i):
                    if dlen == 3:
                        run = i
                        while run < n and text[run] == ch:
                            run += 1
                        extra = run - i - dlen
                        if extra > 0:
                            out.extend(_SENTINEL * extra)
                            i += extra
                            continue
                    out.append(delim)
                    i += dlen
                    break
                else:
                    out.append(_SENTINEL)
                    i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _line_starts(text: str) -> list:
    """Offsets at which each 1-based line (split on ``\\n``) starts."""
    starts = [0]
    for idx, ch in enumerate(text):
        if ch == "\n":
            starts.append(idx + 1)
    return starts


def _line_col(starts: list, offset: int) -> tuple:
    """Map a 0-based offset to a 1-based (line, col) pair."""
    line = bisect_right(starts, offset)
    return line, offset - starts[line - 1] + 1


def _physical_lines(text: str) -> list:
    """Split on ``\\n``; one ``(content, start_offset, sep_len)`` per
    line. The separator is the optional ``\\r`` plus the ``\\n`` that
    ``split`` consumed — zero only for the final line, which may have
    no terminator at all."""
    result: list = []
    offset = 0
    parts = text.split("\n")
    for index, part in enumerate(parts):
        content = part[:-1] if part.endswith("\r") else part
        sep_len = len(part) - len(content)  # the \r, if any
        if index < len(parts) - 1:
            sep_len += 1  # the \n consumed by the split
        result.append((content, offset, sep_len))
        offset += len(part) + 1
    return result


def _format_path(path: tuple) -> str:
    """Render a key path, quoting segments that are not bare keys."""
    parts: list = []
    for segment in path:
        if _BARE_KEY.fullmatch(segment):
            parts.append(segment)
        else:
            parts.append('"' + segment.replace("\\", "\\\\")
                         .replace('"', '\\"') + '"')
    return ".".join(parts)


# ---------------------------------------------------------------------------
# Statement-level raw scan over the masked text
# ---------------------------------------------------------------------------

def _skip_masked_string(masked: str, i: int) -> int:
    """Skip the masked string starting at ``i``; return the index after.

    Masked string content is sentinel bytes, so the first same-quote
    delimiter found is always the real closer. Returns ``len(masked)``
    for an unterminated string.
    """
    ch = masked[i]
    delim = ch * 3 if masked.startswith(ch * 3, i) else ch
    dlen = len(delim)
    close = masked.find(delim, i + dlen)
    if close == -1:
        return len(masked)
    return close + dlen


def _read_key_path(masked: str, text: str, i: int) -> tuple:
    """Read a dotted key path at statement level.

    Returns ``(segments, next_index)``. Quoted segments are extracted
    from the original text at the same offsets; bare segments match
    ``[A-Za-z0-9_-]+`` on the masked text directly. A malformed key
    yields an empty tuple and the scan resynchronizes (tomllib owns
    the syntax error).
    """
    segments: list = []
    n = len(masked)
    while True:
        while i < n and masked[i] in " \t":
            i += 1
        if i < n and masked[i] in "\"'":
            quote = masked[i]
            close = masked.find(quote, i + 1)
            if close == -1:
                return tuple(segments), n
            raw = text[i + 1:close]
            if quote == '"':
                # Minimal basic-string unescaping for key names.
                raw = raw.replace('\\"', '"').replace("\\\\", "\\")
            segments.append(raw)
            i = close + 1
        else:
            match = _BARE_KEY.match(masked, i)
            if match is None:
                return tuple(segments), i
            segments.append(match.group(0))
            i = match.end()
        while i < n and masked[i] in " \t":
            i += 1
        if i < n and masked[i] == ".":
            i += 1
            continue
        return tuple(segments), i


def _skip_value(masked: str, i: int) -> int:
    """Skip a statement value at ``i``; return the index of its newline."""
    n = len(masked)
    depth = 0
    while i < n:
        ch = masked[i]
        if ch in "\"'":
            i = _skip_masked_string(masked, i)
            continue
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            if depth == 0:
                return i
            depth -= 1
        elif ch == "\n" and depth == 0:
            return i
        i += 1
    return i


def _read_array(masked: str, i: int) -> tuple:
    """Read the array literal whose ``[`` sits at ``i``.

    Returns ``(elements, next_index)`` where ``elements`` are the
    masked strings of the *direct* elements: commas split only at
    bracket depth 1 and brace depth 0, so nested arrays and inline
    tables stay whole.
    """
    n = len(masked)
    elements: list = []
    bracket_depth = 0
    brace_depth = 0
    element_start: Optional[int] = None
    while i < n:
        ch = masked[i]
        if ch in "\"'":
            i = _skip_masked_string(masked, i)
            continue
        if ch == "[":
            bracket_depth += 1
            if bracket_depth == 1:
                element_start = i + 1
        elif ch == "]":
            if bracket_depth == 1 and element_start is not None:
                elements.append(masked[element_start:i])
            bracket_depth -= 1
            if bracket_depth <= 0:
                return elements, i + 1
        elif ch == "{":
            brace_depth += 1
        elif ch == "}":
            brace_depth -= 1
        elif ch == "," and bracket_depth == 1 and brace_depth == 0:
            elements.append(masked[element_start:i])
            element_start = i + 1
        i += 1
    return elements, n


def _scan_statements(masked: str, text: str) -> tuple:
    """Walk the masked text at statement level.

    Returns ``(headers, statements, arrays)`` in document order:

    * ``headers`` — ``(path, is_aot, key_offset)`` for every ``[x]`` /
      ``[[x]]`` header (the offset points at the opening bracket);
    * ``statements`` — ``(full_key_path, key_segment_count,
      key_offset)`` for every key/value pair (the table context
      prefix included; the offset is the first key character);
    * ``arrays`` — ``(key_offset, element_list)`` for every array
      literal that is a statement's value.

    The scanner resynchronizes at the next newline on anything it
    cannot read; such documents fail the tomllib parse anyway, and
    only the parse-independent rules are reported for them.
    """
    headers: list = []
    statements: list = []
    arrays: list = []
    i = 0
    n = len(masked)
    ctx: tuple = ()
    while i < n:
        ch = masked[i]
        if ch in " \t\r\n":
            i += 1
            continue
        if ch == "[":
            is_aot = masked.startswith("[[", i)
            key_offset = i
            i += 2 if is_aot else 1
            path, i = _read_key_path(masked, text, i)
            if is_aot:
                if masked.startswith("]]", i):
                    i += 2
            elif masked.startswith("]", i):
                i += 1
            ctx = path
            headers.append((path, is_aot, key_offset))
            continue
        key_offset = i
        path, i = _read_key_path(masked, text, i)
        while i < n and masked[i] in " \t":
            i += 1
        if not path or i >= n or masked[i] != "=":
            while i < n and masked[i] != "\n":
                i += 1
            continue
        i += 1  # '='
        while i < n and masked[i] in " \t":
            i += 1
        statements.append((ctx + path, len(path), key_offset))
        if i < n and masked[i] == "[":
            elements, i = _read_array(masked, i)
            arrays.append((key_offset, elements))
        else:
            i = _skip_value(masked, i)
    return headers, statements, arrays


# ---------------------------------------------------------------------------
# Rule helpers
# ---------------------------------------------------------------------------

def _classify_element(masked_element: str) -> Optional[tuple]:
    """Classify one masked array element.

    Returns ``(kind, offset_aware)`` — ``kind`` is one of the scalar
    classes ``bool`` / ``number`` (integers and floats are one class:
    ``[1, 2.5]`` is ordinary numeric data, not a type mix) /
    ``string`` / ``datetime`` / ``date`` / ``time``, or the container
    markers ``array`` / ``inline_table``; ``offset_aware`` is only
    meaningful for datetimes. Unclassifiable (or trailing-comma
    empty) elements return ``None``.
    """
    token = masked_element.strip(" \t\r\n")
    if not token or token == _SENTINEL * len(token):
        return None
    if token[0] in "\"'":
        return ("string", None)
    if token[0] == "[":
        return ("array", None)
    if token[0] == "{":
        return ("inline_table", None)
    if _ELEM_BOOL.match(token):
        return ("bool", None)
    if _ELEM_DATETIME.match(token):
        return ("datetime", bool(_ELEM_DATETIME_OFFSET.search(token)))
    if _ELEM_DATE.match(token):
        return ("date", None)
    if _ELEM_TIME.match(token):
        return ("time", None)
    if _ELEM_INT.match(token) or _ELEM_FLOAT.match(token):
        return ("number", None)
    return None


def _extract_tomllib_position(message: str, line_count: int) -> tuple:
    """Map a tomllib error message to a 1-based (line, col) pair.

    tomllib embeds ``"(at line N, column M)"`` in the message text or
    reports ``"(at end of document)"`` — the latter maps to the last
    line with ``col=None``. Any unexpected shape falls back to line 1
    with ``col=None``.
    """
    match = _TOML_POSITION.search(message)
    if match:
        return int(match.group(1)), int(match.group(2))
    if _TOML_END_OF_DOC in message:
        return line_count, None
    return 1, None


def _syntax_message(exc: tomllib.TOMLDecodeError) -> str:
    """The decode message without its trailing position marker."""
    return _TOML_POSITION_ANY.sub("", str(exc))


def _path_offset_map(headers: list, statements: list) -> dict:
    """First declaration offset of every path and prefix seen in the scan."""
    offsets: dict = {}
    for path, _is_aot, key_offset in headers:
        offsets.setdefault(path, key_offset)
    for path, _key_len, key_offset in statements:
        for size in range(1, len(path) + 1):
            offsets.setdefault(path[:size], key_offset)
    return offsets


def _lookup_offset(offsets: dict, path: tuple) -> Optional[int]:
    """Exact or longest-prefix offset lookup for a parsed path."""
    for size in range(len(path), 0, -1):
        offset = offsets.get(path[:size])
        if offset is not None:
            return offset
    return None


def _iter_empty_tables(data: Any) -> list:
    """Header-declared tables that ended up with no keys and no children.

    Returns ``(path, occurrence)`` pairs; ``occurrence`` indexes the
    ``[[x]]`` entry among the dict entries of that array-of-tables
    (always 0 for plain tables reached through a dict key, whose path
    is unique). Whether a table is header-declared is decided by the
    caller (the raw header map); inline ``x = {}`` values and
    dotted-key-created empty containers reach this walk too but are
    filtered out there. The walk is iterative so documents nested
    deeper than the Python recursion limit still descend.
    """
    empties: list = []
    stack: list = [(data, (), None)]
    while stack:
        node, path, occurrence = stack.pop()
        if isinstance(node, dict):
            if not node and path:
                empties.append((path, occurrence if occurrence
                                is not None else 0))
            for key, value in reversed(node.items()):
                stack.append((value, path + (key,), None))
        elif isinstance(node, list):
            entries: list = []
            index = 0
            for element in node:
                if isinstance(element, dict):
                    entries.append((element, path, index))
                    index += 1
            stack.extend(reversed(entries))
    return empties


def _walk_depths(data: Any) -> tuple:
    """Return ``(max_depth, deepest_path)`` over the parsed document.

    Depth is the key-path length in segments: dotted keys
    (``a.b.c = 1``) and nested headers (``[x.y.z]``) both produce
    depth-3 leaves. Array-of-tables entries live at their array's
    path; plain arrays are leaves of their key. The walk is iterative
    so documents nested deeper than the Python recursion limit still
    descend.
    """
    best_depth = 0
    best_path: tuple = ()
    stack: list = [(data, ())]
    while stack:
        node, path = stack.pop()
        if len(path) > best_depth:
            best_depth = len(path)
            best_path = path
        if isinstance(node, dict):
            for key, value in reversed(node.items()):
                stack.append((value, path + (key,)))
        elif isinstance(node, list):
            for element in node:
                if isinstance(element, dict):
                    stack.append((element, path))
    return best_depth, best_path


def _scalar_type(value: Any) -> str:
    """TOML 1.0 type name of a parsed scalar (bool before int!)."""
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    # datetime.datetime is a subclass of datetime.date — test it first.
    if isinstance(value, datetime.datetime):
        return "datetime"
    if isinstance(value, datetime.date):
        return "date"
    if isinstance(value, datetime.time):
        return "time"
    return "unknown"


def _array_type(value: list) -> str:
    """Histogram label for an array leaf."""
    if not value:
        return "array<empty>"
    kinds: set = set()
    for element in value:
        if isinstance(element, (dict, list)):
            kinds.add("container")
        else:
            kinds.add(_scalar_type(element))
    if len(kinds) == 1:
        only = next(iter(kinds))
        return "array<mixed>" if only == "container" else f"array<{only}>"
    return "array<mixed>"


def _profile_stats(data: Any, aot_paths: frozenset) -> dict:
    """Aggregate shape statistics for the parsed document.

    The walk is iterative so documents nested deeper than the Python
    recursion limit still descend.
    """
    table_count = 0
    key_count = 0
    histogram: dict = {}
    max_depth = 0
    deepest_path: Optional[str] = None
    stack: list = [(data, ())]

    while stack:
        node, path = stack.pop()
        if len(path) > max_depth:
            max_depth = len(path)
            deepest_path = _format_path(path)
        children: list = []
        if isinstance(node, dict):
            if path:
                table_count += 1
            children = [(value, path + (key,))
                        for key, value in node.items()]
        elif isinstance(node, list) and path in aot_paths:
            # Array of tables: every dict entry is a table at this
            # path and is walked so its keys are counted too.
            children = [(element, path) for element in node
                        if isinstance(element, dict)]
        else:
            key_count += 1
            if isinstance(node, list):
                label = _array_type(node)
            else:
                label = _scalar_type(node)
            histogram[label] = histogram.get(label, 0) + 1
        stack.extend(reversed(children))
    ordered: dict = {}
    for label in sorted(histogram, key=lambda name: (-histogram[name],
                                                     name)):
        ordered[label] = histogram[label]
    return {
        "tables": table_count,
        "arrays_of_tables": len(aot_paths),
        "keys": key_count,
        "scalar_type_histogram": ordered,
        "max_depth": max_depth,
        "deepest_path": deepest_path,
    }


# ---------------------------------------------------------------------------
# Line-level rules and the textual fixer over the masked text
# ---------------------------------------------------------------------------

def _trailing_space_lines(masked: str, physical: list) -> list:
    """(line, col) of every line ending in code whitespace.

    Trailing runs inside multi-line strings contain sentinel bytes
    and never match.
    """
    hits: list = []
    for number, (content, start, _sep) in enumerate(physical, start=1):
        match = _TRAILING_WS.search(content)
        if match is not None:
            run = masked[start + match.start(): start + match.end()]
            if _SENTINEL not in run:
                hits.append((number, match.start() + 1))
    return hits


def _indent_classes(masked: str, physical: list) -> list:
    """(line, class) for every indented code line.

    Class is ``tab``, ``space`` or ``mixed`` (one run holding both).
    Lines inside multi-line strings carry sentinel bytes in their
    indent run and are skipped.
    """
    classes: list = []
    for number, (content, start, _sep) in enumerate(physical, start=1):
        if not content.strip(" \t"):
            continue
        match = _LEADING_WS.match(content)
        if match is None:
            continue
        run = masked[start: start + match.end()]
        if _SENTINEL in run:
            continue
        if "\t" in run and " " in run:
            kind = "mixed"
        elif "\t" in run:
            kind = "tab"
        else:
            kind = "space"
        classes.append((number, kind))
    return classes


def _fix_text(scan_text: str, masked: str, physical: list) -> tuple:
    """Apply the safe textual repairs; return ``(fixed_text, applied)``.

    ``scan_text`` is the BOM-stripped input. Trailing whitespace is
    trimmed only on lines whose trailing run is code (no sentinel);
    line terminators are copied verbatim from the source, so CRLF
    documents stay CRLF.
    """
    applied: list = []
    parts: list = []
    trimmed = 0
    for content, start, sep_len in physical:
        cut = len(content)
        match = _TRAILING_WS.search(content)
        if match is not None:
            run = masked[start + match.start(): start + match.end()]
            if _SENTINEL not in run:
                cut = match.start()
                trimmed += 1
        parts.append(scan_text[start: start + cut])
        # The separator sits at the *original* end of the line — the
        # trimmed run (if any) is skipped, the \r\n / \n kept verbatim.
        sep_begin = start + len(content)
        parts.append(scan_text[sep_begin: sep_begin + sep_len])
    fixed = "".join(parts)
    if trimmed:
        applied.append({"repair": "trailing_space_strip",
                        "count": trimmed})
    return fixed, applied


# ---------------------------------------------------------------------------
# Mode runners
# ---------------------------------------------------------------------------

def _run_lint(tool: Any, text: str, disabled: frozenset,
              max_depth: int) -> dict:
    """Run the rule table; ``text`` still carries any BOM."""
    findings: list = []

    def add(code: str, line: Any, col: Any, message: str) -> None:
        _slug, severity, hint = _RULES[code]
        findings.append({
            "code": code,
            "severity": severity,
            "line": line,
            "col": col,
            "message": message,
            "hint": hint,
        })

    bom = text.startswith("\ufeff")
    scan_text = text[1:] if bom else text
    if bom and "TOML001" not in disabled:
        add("TOML001", 1, 1,
            "the document starts with a UTF-8 BOM (\\ufeff); tomllib "
            "rejects it, it was stripped before parsing here")

    masked = _mask_text(scan_text)
    starts = _line_starts(scan_text)
    physical = _physical_lines(scan_text)
    line_count = len(physical)

    # --- parse --------------------------------------------------------
    try:
        data = tomllib.loads(scan_text)
        valid = True
    except tomllib.TOMLDecodeError as exc:
        valid = False
        if "TOML002" not in disabled:
            line, col = _extract_tomllib_position(str(exc), line_count)
            add("TOML002", line, col,
                f"tomllib rejected the document: {_syntax_message(exc)}")
    except RecursionError:
        raise _err(
            "document nesting exceeds the Python recursion limit and "
            "cannot be linted"
        )

    # --- line-level rules (parse-independent) --------------------------
    if "TOML005" not in disabled:
        trailing = _trailing_space_lines(masked, physical)
        if trailing:
            first_line, first_col = trailing[0]
            add("TOML005", first_line, first_col,
                f"{len(trailing)} line(s) end with whitespace outside "
                f"strings (first at line {first_line})")

    if "TOML006" not in disabled:
        classes = _indent_classes(masked, physical)
        if classes:
            kinds: dict = {}
            first_class = classes[0][1]
            clash = None
            for number, kind in classes:
                kinds[kind] = kinds.get(kind, 0) + 1
                if kind != first_class and clash is None:
                    clash = number
            if len(kinds) > 1:
                summary = ", ".join(
                    f"{count} {kind}-led" for kind, count in kinds.items()
                )
                add("TOML006", clash, 1,
                    f"indentation mixes styles: {summary} line(s); first "
                    f"clash at line {clash}")

    if "TOML007" not in disabled:
        grouped = list(_UNDERSCORED_NUMBER.finditer(masked))
        plain = list(_PLAIN_LONG_NUMBER.finditer(masked))
        if grouped and plain:
            line, col = _line_col(starts, grouped[0].start())
            add("TOML007", line, col,
                f"number style is mixed: {len(grouped)} digit-grouped "
                f"literal(s) (e.g. 1_000) and {len(plain)} plain long "
                f"literal(s) (e.g. 100000, 5+ digits)")

    # --- parse-dependent rules -----------------------------------------
    if valid:
        headers, statements, arrays = _scan_statements(masked, scan_text)
        header_lines: dict = {}
        aot_paths = set()
        for path, is_aot, key_offset in headers:
            header_lines.setdefault(path, []).append(key_offset)
            if is_aot:
                aot_paths.add(path)

        if "TOML003" not in disabled or "TOML004" not in disabled:
            for key_offset, elements in arrays:
                kinds_seen: list = []
                offset_flags: list = []
                for element in elements:
                    classified = _classify_element(element)
                    if classified is None:
                        continue
                    kind, offset_aware = classified
                    if kind not in ("array", "inline_table"):
                        if kind not in kinds_seen:
                            kinds_seen.append(kind)
                    if kind == "datetime":
                        offset_flags.append(offset_aware)
                line, col = _line_col(starts, key_offset)
                if len(kinds_seen) >= 2 and "TOML003" not in disabled:
                    add("TOML003", line, col,
                        f"array of key at line {line} mixes scalar "
                        f"types: {', '.join(kinds_seen)}")
                if (offset_flags and True in offset_flags
                        and False in offset_flags
                        and "TOML004" not in disabled):
                    add("TOML004", line, col,
                        f"array of key at line {line} mixes offset-aware "
                        f"and naive datetimes "
                        f"({offset_flags.count(True)} aware, "
                        f"{offset_flags.count(False)} naive)")

        if "TOML008" not in disabled:
            for path, occurrence in _iter_empty_tables(data):
                occurrences = header_lines.get(path)
                if not occurrences:
                    continue
                index = min(occurrence, len(occurrences) - 1)
                line, col = _line_col(starts, occurrences[index])
                add("TOML008", line, col,
                    f"table [{_format_path(path)}] is declared but "
                    f"empty (no keys, no sub-tables)")

        if "TOML009" not in disabled:
            depth, deepest = _walk_depths(data)
            if depth > max_depth:
                offsets = _path_offset_map(headers, statements)
                offset = _lookup_offset(offsets, deepest)
                if offset is None:
                    line, col = 1, None
                else:
                    line, col = _line_col(starts, offset)
                add("TOML009", line, col,
                    f"deepest path {_format_path(deepest)} nests "
                    f"{depth} levels (max_depth={max_depth})")

        if "TOML010" not in disabled:
            dotted_keys = [key_offset for _path, key_len, key_offset
                           in statements if key_len >= 2]
            header_style: set = set()
            ctx: tuple = ()
            header_index = 0
            for path, key_len, key_offset in statements:
                while (header_index < len(headers)
                        and headers[header_index][2] < key_offset):
                    ctx = headers[header_index][0]
                    header_index += 1
                if key_len == 1 and ctx:
                    header_style.add(ctx)
            if dotted_keys and header_style:
                line, col = _line_col(starts, dotted_keys[0])
                add("TOML010", line, col,
                    f"table definition style is mixed: "
                    f"{len(dotted_keys)} dotted-key definition(s) "
                    f"(e.g. a.b = 1) and {len(header_style)} "
                    f"header-defined table(s) with direct keys")

    # --- assemble -------------------------------------------------------
    findings.sort(key=lambda f: (f["line"] if f["line"] else 0,
                                 f["col"] if f["col"] is not None else 0,
                                 f["code"]))
    truncated = len(findings) > tool.MAX_FINDINGS
    ok = not any(f["severity"] in ("error", "warning")
                 for f in findings)
    return {
        "mode": "lint",
        "ok": ok,
        "valid": valid,
        "finding_count": len(findings),
        "findings_truncated": truncated,
        "findings": findings[: tool.MAX_FINDINGS],
    }


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class TomlLintTool(Tool):
    """Quality and style linter for TOML text, built purely on the
    stdlib ``tomllib`` parser plus a comment-stripped raw-text scan.

    The tool never touches the filesystem or the network — it examines
    TOML *text*: lint it against the documented rule table, profile
    its shape, or apply the safe textual repairs. See the module
    docstring for the full rule table, the mode reference and the
    verified tomllib ground truths.

    Class attributes:
        MODES (tuple): Supported modes (lint, profile, fix_hints).
        RULE_CODES (tuple): All implemented rule codes.
        MAX_FINDINGS (int): Findings list cap per lint run.
        DEFAULT_MAX_DEPTH (int): TOML009 threshold default.
        MAX_DEPTH_LIMIT (int): Upper bound for the max_depth option.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "toml_lint_tool"
    description: str = (
        "TOML quality and style linter — pure Python stdlib tomllib "
        "plus a comment-stripped raw-text scan, no files, no network. "
        "lint mode checks a document against a documented 10-rule "
        "table (mode='lint' — UTF-8 BOM, tomllib syntax errors with "
        "line/column mapped from the decode failure — duplicate "
        "tables, duplicate keys, multi-line inline tables and "
        "capitalized True/False all land here — mixed-type arrays, "
        "arrays mixing offset-aware and naive datetimes, trailing "
        "spaces, mixed tab/space indentation, inconsistent digit "
        "grouping in numbers, header-declared empty tables, nesting "
        "over a max_depth threshold, dotted-key and header table "
        "definitions mixed in one document), each finding carrying "
        "severity, 1-based line/column and a hint; profile mode "
        "aggregates tables, arrays-of-tables, key count, a scalar "
        "type histogram including date/datetime/time and the maximum "
        "path depth (mode='profile'); fix_hints mode applies the safe "
        "textual repairs only — BOM strip and trailing-whitespace "
        "trim outside multiline strings, never structural — and "
        "re-lints what remains (mode='fix_hints')."
    )

    MODES: ClassVar[tuple] = ("lint", "profile", "fix_hints")
    RULE_CODES: ClassVar[tuple] = _RULE_CODES
    MAX_FINDINGS: ClassVar[int] = 200
    DEFAULT_MAX_DEPTH: ClassVar[int] = 12
    MAX_DEPTH_LIMIT: ClassVar[int] = 128

    max_input_chars: int = 1_048_576

    def execute(
        self,
        mode: Any = None,
        toml_text: Any = None,
        rules: Any = None,
        max_depth: Any = None,
    ) -> dict:
        """Lint, profile or fix TOML text.

        Args:
            mode (str): One of ``lint``, ``profile`` or ``fix_hints``.
            toml_text (str): The TOML text. A leading UTF-8 BOM is
                reported (TOML001) and stripped before parsing.
            rules (dict): Map a rule code (TOML001..TOML010) to False
                to disable that single rule for the call. Lint mode
                only.
            max_depth (int): TOML009 nesting threshold in path
                segments. Default 12, range 1..128. Lint mode only.

        Returns:
            dict: ``lint`` → ``{mode, ok, valid, finding_count,
            findings_truncated, findings}`` with each finding
            ``{code, severity, line, col, message, hint}``;
            ``profile`` → ``{mode, tables, arrays_of_tables, keys,
            scalar_type_histogram, max_depth, deepest_path}``;
            ``fix_hints`` → ``{mode, fixed_text, applied,
            remaining_count, remaining_truncated, remaining}``.

        Raises:
            ValueError: If any argument is malformed, the input is
                empty or oversized, a lint-only option is used in
                another mode — or, in profile mode, the document is
                not valid TOML.
        """
        if mode not in self.MODES:
            raise _err(f"mode must be one of {self.MODES}, got {mode!r}")

        provided = {"rules": rules, "max_depth": max_depth}
        for option, value in provided.items():
            if value is not None and option not in _MODE_OPTIONS[mode]:
                raise _err(
                    f"{option!r} is not a {mode} mode option "
                    f"(allowed: {sorted(_MODE_OPTIONS[mode])})"
                )

        if not isinstance(toml_text, str):
            raise _err(
                f"toml_text must be a string, got "
                f"{type(toml_text).__name__}"
            )
        if not toml_text:
            raise _err("toml_text must be non-empty")
        if len(toml_text) > self.max_input_chars:
            raise _err(
                f"toml_text exceeds the {self.max_input_chars:,}-character "
                f"limit (1 MiB; got {len(toml_text):,} characters)"
            )

        if mode == "lint":
            disabled = self._resolve_rules(rules)
            depth = self._resolve_max_depth(max_depth)
            return _run_lint(self, toml_text, disabled, depth)

        scan_text = (toml_text[1:] if toml_text.startswith("\ufeff")
                     else toml_text)

        if mode == "profile":
            try:
                data = tomllib.loads(scan_text)
            except tomllib.TOMLDecodeError as exc:
                raise _err(
                    f"profile mode requires valid TOML — tomllib "
                    f"rejected the document: {_syntax_message(exc)}"
                ) from exc
            except RecursionError:
                raise _err(
                    "document nesting exceeds the Python recursion "
                    "limit and cannot be linted"
                )
            masked = _mask_text(scan_text)
            headers, _statements, _arrays = _scan_statements(
                masked, scan_text)
            aot_paths = frozenset(
                path for path, is_aot, _offset in headers if is_aot
            )
            stats = _profile_stats(data, aot_paths)
            return {
                "mode": "profile",
                "tables": stats["tables"],
                "arrays_of_tables": stats["arrays_of_tables"],
                "keys": stats["keys"],
                "scalar_type_histogram": stats["scalar_type_histogram"],
                "max_depth": stats["max_depth"],
                "deepest_path": stats["deepest_path"],
            }

        # fix_hints — textual repairs only, never structural.
        masked = _mask_text(scan_text)
        physical = _physical_lines(scan_text)
        fixed, applied = _fix_text(scan_text, masked, physical)
        if toml_text.startswith("\ufeff"):
            applied.insert(0, {"repair": "bom_strip", "count": 1})
        relint = _run_lint(self, fixed, frozenset(),
                           self.DEFAULT_MAX_DEPTH)
        return {
            "mode": "fix_hints",
            "fixed_text": fixed,
            "applied": applied,
            "remaining_count": relint["finding_count"],
            "remaining_truncated": relint["findings_truncated"],
            "remaining": relint["findings"],
        }

    @classmethod
    def _resolve_rules(cls, rules: Any) -> frozenset:
        """Validate the per-rule disable map; return disabled codes."""
        if rules is None:
            return frozenset()
        if not isinstance(rules, dict):
            raise _err(
                f"rules must be a dict mapping rule codes to booleans, "
                f"got {type(rules).__name__}"
            )
        disabled: set = set()
        for code, value in rules.items():
            if code not in _RULES:
                raise _err(
                    f"unknown rule code {code!r} "
                    f"(implemented: {list(_RULE_CODES)})"
                )
            if not isinstance(value, bool):
                raise _err(
                    f"rule {code!r} must map to a boolean, got {value!r}"
                )
            if value is False:
                disabled.add(code)
        return frozenset(disabled)

    @classmethod
    def _resolve_max_depth(cls, max_depth: Any) -> int:
        """Validate the TOML009 threshold; default when omitted."""
        if max_depth is None:
            return cls.DEFAULT_MAX_DEPTH
        if isinstance(max_depth, bool) or not isinstance(max_depth, int):
            raise _err(
                f"max_depth must be an integer, got {max_depth!r}"
            )
        if not 1 <= max_depth <= cls.MAX_DEPTH_LIMIT:
            raise _err(
                f"max_depth must be within 1..{cls.MAX_DEPTH_LIMIT}, "
                f"got {max_depth}"
            )
        return max_depth
