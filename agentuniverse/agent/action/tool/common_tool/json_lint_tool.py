#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: json_lint_tool.py

"""JSON document *quality and style linting* tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the linting layer on top of JSON: the sibling JSON
tools of this collection each address a different concern — format
conversion, path querying, RFC 6902 mutation and schema validation —
while this tool inspects a JSON **text** itself and reports the
style/quality problems a formatter, a query engine or a validator
would not mention, with exact line/column positions and no network
access and no third-party dependencies.

The key insight the tool is built around: once a JSON text is parsed,
some defects simply **cannot** be seen anymore. Duplicate keys are
impossible in a parsed Python ``dict`` yet perfectly possible in the
*text* — and ``json.loads`` silently keeps the last value, so
``{"a": 1, "a": 2}`` parses to ``{"a": 2}`` without any warning. The
linter therefore parses *and* scans the raw text: an
``object_pairs_hook`` provides the value-level truth of which key
names repeat inside one object (it sees every pair, decoded, before
dict construction collapses them), and a position-preserving raw-text
scanner locates those names in the text — the hook alone loses
positions (it never sees the source), the scanner alone would have to
re-implement string decoding, so the two cross-check each other and
the tool reports only names the hook confirmed, at the positions the
scanner found.

``lint`` mode rules (findings ``{code, severity, line, col, message}``
— line/col are 1-based character positions exactly matching the
convention ``json.JSONDecodeError`` uses on this interpreter):

* ``syntax_error`` — the document does not parse. The parser's
  ``JSONDecodeError`` position is converted ``pos`` → line/col with a
  single converter (cross-verified against the exception's own
  ``lineno``/``colno`` attributes, which CPython does carry, in the
  tests over 30 malformed documents), and the message keeps the
  original parser reason. Two frequent shapes get dedicated codes:
* ``trailing_comma_like`` — json5-style trailing commas
  (``[1, 2, ]``, ``{"a": 1,}``) are plain errors to ``json.loads``;
  recognized by the parser message plus the next non-whitespace
  character being ``]``/``}`` so the cause is named, not just
  "Expecting value".
* ``string_unescaped_control_char`` — raw control characters inside
  strings (verified: ``json.loads`` in its default ``strict=True``
  *rejects* them with "Invalid control character", so they surface as
  this classified syntax error; the ``\u0000`` escaped form is legal
  and never flagged).
* ``bom_not_allowed`` — a leading U+FEFF is illegal in JSON (RFC
  8259 §8.1); ``json.loads`` rejects it with "Unexpected UTF-8 BOM".
  The linter names the BOM precisely and keeps linting the rest of
  the document after the sigil, so one run reports everything; every
  finding still addresses the original text, where the sigil itself
  occupies line 1 column 1.
* ``empty_document`` — empty or whitespace-only text.
* ``duplicate_key`` — repeated key names inside one object (verified:
  ``json.loads`` silently keeps the last value). Detected across
  escape spellings — ``"a"`` and ``"\u0061"`` are the same key —
  because both the hook and the scanner decode string tokens with
  ``json.loads`` itself. The message says which value survives.
* ``non_rfc_number_literal`` — ``NaN``, ``Infinity`` and
  ``-Infinity`` (verified empirically: ``json.loads`` **accepts**
  these non-standard literals by default, so the document still
  lints as parseable). Flagged info as not RFC 8259 JSON, with the
  strictness note that ``json.dumps(..., allow_nan=False)`` — and
  most non-Python peers — refuse such values.
* ``mixed_number_formats`` — integer-valued floats written in float
  form (``1.0``, ``2e2``): info that ``1.0`` and ``1`` are the same
  JSON number but the two spellings usually signal an accidental
  type leak from a float-typed producer.
* ``very_long_lines`` — lines longer than 5000 characters (info;
  unreviewable single-line payloads).
* ``deeply_nested`` — container nesting deeper than 12 levels (info;
  reported with the actual maximum depth at the first position that
  exceeds the threshold).
* ``nesting_exceeds_parser_limit`` — nesting so deep the interpreter's
  own ``json.loads`` parser raised ``RecursionError`` (the C scanner
  recurses per container level, so around the default recursion limit
  a parse failure arrives as RecursionError, not JSONDecodeError); the
  tool reports it as a classified finding/error payload in every mode
  instead of crashing.
* ``inconsistent_key_case`` — one object mixing camelCase and
  snake_case keys (info heuristic; keys matching neither pattern are
  ignored).
* ``scalar_only_document`` — a bare scalar root (info; legal JSON,
  often an un-intended fragment).

``profile`` mode describes structure instead of judging it: type
counts (objects/arrays/strings/numbers/booleans/nulls), the
int/float split of the numbers, maximum container depth (a scalar
root is depth 0), total and distinct key names (distinct names
sorted, so output is deterministic), array length statistics and
string length statistics.

``fix_hints`` mode proposes — and only for one case provides —
mechanical fixes: a leading BOM is the single safe *textual* fix
(the byte-stripped text is returned as ``fixed_text``), everything
else is a suggestion with the exact position (``NaN`` → ``null``,
``2.0`` → ``2``) that is never auto-applied, because rewriting
values or structure is a decision the document's owner must make.
Structural changes are out of scope by design.

Input validation is strict and happens before any computation:
``mode`` must be one of the three, ``document`` must be the JSON
*text* (linting lives in the text — already-parsed values have lost
the very defects the tool detects) of at most 1,000,000 characters;
violations raise a ``ValueError``, mirroring the other common tools.
For ``lint`` a document that does not parse is a *finding*, not an
error; ``profile``/``fix_hints`` cannot proceed on a broken document
and return a structured ``error`` payload instead (the same holds for
a document whose nesting overflowed the parser recursion limit). The
tool is deterministic — output is a pure function of the input,
findings sorted by (line, col, code) — and read-only: the input text
is never modified. Line numbering counts ``\\n`` only, exactly like
``json.JSONDecodeError``, on every rule including the line-length
one. The text scan and the profile walk are iterative (explicit
index / explicit stack), so a document that parses never hits the
interpreter recursion limit inside the tool itself.
"""

import json
import math
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Input size limit (bounded purely to reject pathological inputs
# early; far above real payloads).
_MAX_TEXT = 1_000_000

# Style thresholds (info-level rules).
_LONG_LINE = 5_000
_DEEP_NESTING = 12

# Whitespace JSON itself allows between tokens.
_WS = " \t\r\n"

# Value-position tokens of a successfully parsed document: the three
# RFC 8259 literals, the three non-standard extensions json.loads
# accepts, and numbers (numbers are validated by the parse already
# having succeeded — the regex only locates the token end).
_VALUE_TOKEN = re.compile(
    r"(true|false|null|NaN|Infinity|-Infinity"
    r"|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)"
)

# Key-name style heuristics for the inconsistent_key_case rule.
_SNAKE = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+\Z")
_CAMEL = re.compile(r"[a-z][a-z0-9]*(?:[A-Z][a-z0-9]+)+\Z")

# Non-standard float literals accepted by json.loads (flagged, and
# suggested to become null in fix_hints mode).
_NAN_LITERALS = ("NaN", "Infinity", "-Infinity")


def _pos_to_line_col(text: str, pos: int) -> Tuple[int, int]:
    """Convert a 0-based character offset into 1-based (line, col).

    Uses exactly the convention of ``json.JSONDecodeError``: the col
    counts characters since the last ``\\n`` plus one (the tests
    cross-verify the two against each other on malformed corpora).
    """
    line = text.count("\n", 0, pos) + 1
    col = pos - (text.rfind("\n", 0, pos) + 1) + 1
    return line, col


def _finding(
    code: str, severity: str, line: int, col: int, message: str
) -> Dict[str, Any]:
    """Build one ordered finding dict."""
    return {
        "code": code,
        "severity": severity,
        "line": line,
        "col": col,
        "message": message,
    }


def _strip_bom(text: str) -> Tuple[bool, str]:
    """Whether the text starts with U+FEFF, and the sigil-stripped text."""
    if text.startswith("﻿"):
        return True, text[1:]
    return False, text


def _shift_after_bom(items: List[Dict[str, Any]]) -> None:
    """Re-address line-1 positions to the BOM-prefixed original text.

    Positions are computed on the sigil-stripped text, but the caller
    only holds the original: on line 1 every column is one short while
    the BOM occupies column 1. The BOM finding itself already points
    at the sigil and must not move. Works for findings and for
    fix_hints hints alike (both carry line/col/code).
    """
    for item in items:
        if item["line"] == 1 and item["code"] != "bom_not_allowed":
            item["col"] += 1


def _classify_syntax_error(
    text: str, exc: "json.JSONDecodeError"
) -> Dict[str, Any]:
    """Map a JSONDecodeError to a precise, classified finding.

    The exception carries ``msg``, ``pos``, ``lineno`` and ``colno``
    (verified on this interpreter); line/col are recomputed from
    ``pos`` with the single shared converter so every rule reports
    positions through one code path.
    """
    line, col = _pos_to_line_col(text, exc.pos)

    if exc.msg == "Unexpected UTF-8 BOM":
        return _finding(
            "bom_not_allowed", "error", line, col,
            "Unexpected UTF-8 BOM (U+FEFF) — illegal in JSON "
            "(RFC 8259 section 8.1); strip the sigil and re-encode "
            "as plain UTF-8",
        )

    if exc.msg == "Invalid control character at":
        return _finding(
            "string_unescaped_control_char", "error", line, col,
            "Raw control character inside a string — must be escaped "
            f"({exc.doc[exc.pos]!r} at offset {exc.pos}); "
            "json.loads strict mode rejects it, and \\uXXXX escapes "
            "are the legal spelling",
        )

    if exc.msg in (
        "Expecting value",
        "Expecting property name enclosed in double quotes",
    ):
        # A trailing-comma shape iff a comma immediately precedes the
        # failure point and the first non-whitespace character after
        # it closes the container ('[1, 2, ]' yes, '{"a":}' no —
        # that one is a missing value).
        doc = exc.doc
        k = exc.pos - 1
        while k >= 0 and doc[k] in _WS:
            k -= 1
        j = exc.pos
        while j < len(doc) and doc[j] in _WS:
            j += 1
        if k >= 0 and doc[k] == "," and j < len(doc) and doc[j] in "]}":
            return _finding(
                "trailing_comma_like", "error", line, col,
                f"Trailing comma before {doc[j]!r} — trailing commas "
                "are json5 syntax, not JSON; remove the comma",
            )

    snippet = exc.doc[exc.pos:exc.pos + 1]
    return _finding(
        "syntax_error", "error", line, col,
        f"Invalid JSON: {exc.msg}"
        + (f" at character {snippet!r}" if snippet else ""),
    )


class _Hook:
    """object_pairs_hook collecting the value-level duplicate truth.

    ``json.loads`` calls it for every object with the full decoded
    pair list *before* dict construction collapses duplicates, so it
    is the authority on which names repeat inside one object —
    including keys that only collide after escape decoding. It also
    returns the regular last-wins dict, so the parse result is the
    standard one and profile mode can walk it.
    """

    def __init__(self) -> None:
        self.duplicates: List[List[str]] = []  # per object, in order

    def __call__(self, pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        names = [name for name, _ in pairs]
        seen = set()
        dups = []
        for name in names:
            if name in seen and name not in dups:
                dups.append(name)
            seen.add(name)
        if dups:
            self.duplicates.append(sorted(dups))
        return dict(pairs)


def _scan_text(text: str) -> Dict[str, Any]:
    """Position-preserving raw-text scan of a *parsed-OK* JSON text.

    Walks the text once tracking string tokens (escape-aware),
    container nesting and value tokens, and returns everything the
    position-carrying rules need:

    * ``scopes`` — one record per object: its opening position and
      its key names in document order (names decoded with
      ``json.loads``, so escape spellings equal raw spellings);
    * ``nan_tokens`` — positions of NaN/Infinity/-Infinity;
    * ``float_form_ints`` — integer-valued float tokens with their
      suggested int spelling;
    * ``max_depth`` — maximum container depth (scalar root = 0) and
      the first position exceeding the nesting threshold.

    The scan is strictly O(len(text)): the current line and its start
    offset are carried incrementally instead of being recomputed per
    token, so a one-million-character single-line document costs one
    pass. Newlines are counted in ``\\n`` only — the same convention
    ``json.JSONDecodeError`` and every other rule of this tool use —
    and in a parsed-OK text a raw ``\\n`` cannot occur inside a string
    token (strict mode rejects control characters), so the invariant
    holds by construction; the defensive recount below keeps it true
    for any input regardless.
    """
    scopes: List[Dict[str, Any]] = []
    nan_tokens: List[Dict[str, Any]] = []
    float_form_ints: List[Dict[str, Any]] = []
    stack: List[Dict[str, Any]] = []  # {'kind': 'obj'|'arr', ...}
    max_depth = 0
    deep_pos: Optional[Tuple[int, int]] = None
    line, line_start = 1, 0

    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in _WS:
            if c == "\n":
                line += 1
                line_start = i + 1
            i += 1
            continue

        if c == '"':
            # String token: honor backslash escapes inside.
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == '"':
                    break
                j += 1
            raw = text[i:j + 1]
            key_col = i - line_start + 1
            key_line = line
            i = j + 1
            if "\n" in raw:
                line += raw.count("\n")
                line_start = i - len(raw) + raw.rfind("\n") + 1
            # A string is a key iff the next non-ws character is the
            # member-colon (true only in objects, post-parse).
            k = i
            while k < n and text[k] in _WS:
                k += 1
            if k < n and text[k] == ":" and stack and stack[-1]["kind"] == "obj":
                name = json.loads(raw)  # decode escapes — parse-validated
                scope = stack[-1]
                scope["names"].append(name)
                scope.setdefault("positions", {}).setdefault(name, []).append(
                    (key_line, key_col)
                )
            continue

        if c == "{":
            depth = len(stack) + 1
            if depth > max_depth:
                max_depth = depth
            if depth > _DEEP_NESTING and deep_pos is None:
                deep_pos = (line, i - line_start + 1)
            stack.append({"kind": "obj", "names": [], "positions": {},
                          "open": (line, i - line_start + 1)})
            i += 1
            continue

        if c == "[":
            depth = len(stack) + 1
            if depth > max_depth:
                max_depth = depth
            if depth > _DEEP_NESTING and deep_pos is None:
                deep_pos = (line, i - line_start + 1)
            stack.append({"kind": "arr", "open": (line, i - line_start + 1)})
            i += 1
            continue

        if c in "}]":
            closing = stack.pop()
            if closing["kind"] == "obj":
                closing.pop("kind")
                scopes.append(closing)
            i += 1
            continue

        if c in ":,":
            i += 1
            continue

        m = _VALUE_TOKEN.match(text, i)
        if m is None:  # pragma: no cover - parse succeeded already
            i += 1
            continue
        token = m.group(0)
        col = i - line_start + 1
        if token in _NAN_LITERALS:
            nan_tokens.append(
                {"token": token, "line": line, "col": col}
            )
        elif token[0].isdigit() or token[0] == "-":
            if ("." in token) or ("e" in token) or ("E" in token):
                try:
                    value = float(token)
                except ValueError:  # pragma: no cover - parse validated
                    value = None
                if value is not None and math.isfinite(value) \
                        and value == int(value):
                    float_form_ints.append(
                        {"token": token, "int_form": str(int(value)),
                         "line": line, "col": col}
                    )
        # true/false/null carry no lint rule.
        i = m.end()

    return {
        "scopes": scopes,
        "nan_tokens": nan_tokens,
        "float_form_ints": float_form_ints,
        "max_depth": max_depth,
        "deep_pos": deep_pos,
    }


def _walk_profile(value: Any) -> Dict[str, Any]:
    """Collect structural statistics of a parsed document.

    Counts are exact; ``max_depth`` counts container levels (a
    scalar root is 0, ``{"a": 1}`` is 1, ``[[1]]`` is 2). All lists
    are emitted sorted, keeping the output deterministic. The walk
    is iterative (explicit stack) so a document whose nesting the
    parser accepted never overflows the interpreter recursion limit
    inside this tool, however close to the limit the parse was.
    """
    counts = {
        "object": 0, "array": 0, "string": 0,
        "number": 0, "boolean": 0, "null": 0,
    }
    numbers = {"int": 0, "float": 0}
    array_lens: List[int] = []
    string_lens: List[int] = []
    all_keys: List[str] = []
    max_depth = 0

    stack: List[Tuple[Any, int]] = [(value, 0)]
    while stack:
        node, depth = stack.pop()
        if isinstance(node, bool):
            counts["boolean"] += 1
            continue
        if isinstance(node, dict):
            counts["object"] += 1
            if depth + 1 > max_depth:
                max_depth = depth + 1
            for key, child in node.items():
                all_keys.append(key)
                stack.append((child, depth + 1))
            continue
        if isinstance(node, list):
            counts["array"] += 1
            if depth + 1 > max_depth:
                max_depth = depth + 1
            array_lens.append(len(node))
            for child in node:
                stack.append((child, depth + 1))
            continue
        if node is None:
            counts["null"] += 1
            continue
        if isinstance(node, str):
            counts["string"] += 1
            string_lens.append(len(node))
            continue
        if isinstance(node, int):
            counts["number"] += 1
            numbers["int"] += 1
            continue
        if isinstance(node, float):
            counts["number"] += 1
            numbers["float"] += 1
            continue
        # Non-JSON scalars cannot occur (parse produced the value).

    def lens_stat(lens: List[int]) -> Dict[str, Any]:
        if not lens:
            return {"count": 0}
        return {
            "count": len(lens),
            "min_len": min(lens),
            "max_len": max(lens),
            "total_len": sum(lens),
            "avg_len": round(sum(lens) / len(lens), 2),
        }

    distinct = sorted(set(all_keys))
    return {
        "type_counts": counts,
        "numbers": numbers,
        "max_depth": max_depth,
        "keys": {
            "total": len(all_keys),
            "distinct": len(distinct),
            "distinct_names": distinct,
        },
        "arrays": lens_stat(array_lens),
        "strings": lens_stat(string_lens),
    }


def _syntax_payload(mode: str, text: str,
                    exc: "json.JSONDecodeError") -> Dict[str, Any]:
    """Structured error payload for profile / fix_hints on broken text."""
    finding = _classify_syntax_error(text, exc)
    return {
        "mode": mode,
        "error": {
            "code": finding["code"],
            "message": finding["message"],
            "line": finding["line"],
            "col": finding["col"],
        },
    }


class JsonLintTool(Tool):
    """JSON document quality and style linter built purely on the stdlib.

    Attributes:
        max_text (int): Upper bound on the accepted document text;
            longer inputs are rejected before any work.
        long_line_threshold (int): Line length above which the
            ``very_long_lines`` info finding fires.
        deep_nesting_threshold (int): Container depth above which
            the ``deeply_nested`` info finding fires.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "json_lint_tool"
    description: str = (
        "JSON document quality and style linting tool — pure Python "
        "stdlib, no network required. Lint a JSON text (mode='lint') "
        "for style and quality findings with exact line/col "
        "positions: duplicate keys across escape spellings (which "
        "json.loads silently collapses last-wins), trailing commas, "
        "raw control characters in strings, a leading BOM, the "
        "non-standard NaN/Infinity literals json.loads nonetheless "
        "accepts, integer-valued floats (1.0 vs 1), very long lines, "
        "deep nesting, nesting beyond the parser's own recursion "
        "limit (reported as a finding, never crashing), mixed "
        "camelCase/snake_case keys and scalar "
        "roots. Profile a document's structure (mode='profile': "
        "type counts, int/float split, max depth, key statistics, "
        "array and string length statistics) or get safe fix hints "
        "(mode='fix_hints': BOM strip as the only auto-applicable "
        "textual fix, everything else suggestion-only with exact "
        "positions — structural changes are never proposed)."
    )

    MODES: ClassVar[tuple] = ("lint", "profile", "fix_hints")

    max_text: int = _MAX_TEXT
    long_line_threshold: int = _LONG_LINE
    deep_nesting_threshold: int = _DEEP_NESTING

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        document: Any = None,
    ) -> Dict[str, Any]:
        """Run one JSON linting operation.

        Args:
            mode (str): One of ``lint`` / ``profile`` / ``fix_hints``.
            document (str): The JSON document **text** to inspect
                (linting lives in the text: parsed values have lost
                the very defects this tool detects).

        Returns:
            Dict[str, Any]: For ``lint``: ``findings`` plus a
            ``summary`` (validity flag, per-severity counts,
            per-rule counts, line/char totals). For ``profile``:
            the structural statistics of the parsed document. For
            ``fix_hints``: ``hints`` and — only when a BOM was
            present — the sigil-stripped ``fixed_text``.
        """
        if not isinstance(mode, str) or mode not in self.MODES:
            raise ValueError(
                "mode must be one of "
                f"{', '.join(self.MODES)} (got {mode!r})"
            )
        if not isinstance(document, str):
            raise ValueError(
                "document must be the JSON text to lint (a str); "
                "already-parsed values cannot be linted because "
                "duplicate keys and formatting details are lost "
                f"on parse (got {type(document).__name__})"
            )
        if len(document) > self.max_text:
            raise ValueError(
                f"document exceeds the {self.max_text}-character cap "
                f"({len(document)} characters)"
            )

        if mode == "lint":
            return self._lint(document)
        if mode == "profile":
            return self._profile(document)
        return self._fix_hints(document)

    # ------------------------------------------------------------------ #
    # lint
    # ------------------------------------------------------------------ #

    def _lint(self, text: str) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []

        # Rule: BOM (illegal; keep linting the rest of the document).
        had_bom, text = _strip_bom(text)
        if had_bom:
            findings.append(_finding(
                "bom_not_allowed", "error", 1, 1,
                "Document starts with a UTF-8 BOM (U+FEFF) — illegal "
                "in JSON (RFC 8259 section 8.1); json.loads rejects "
                "it ('Unexpected UTF-8 BOM'); strip the sigil",
            ))

        # Rule: empty document (nothing else can be reported).
        if not text.strip():
            findings.append(_finding(
                "empty_document", "error", 1, 1,
                "Document is empty (or whitespace-only) — the JSON "
                "text contains no value",
            ))
            if had_bom:
                _shift_after_bom(findings)
            return self._lint_result(text, findings)

        # Rule: syntax (classified) — a parse failure IS the finding.
        hook = _Hook()
        try:
            value = json.loads(text, object_pairs_hook=hook)
        except json.JSONDecodeError as exc:
            findings.append(_classify_syntax_error(text, exc))
            # Text-level rules that do not need a parse still apply.
            findings.extend(self._long_line_findings(text))
            if had_bom:
                _shift_after_bom(findings)
            return self._lint_result(text, findings)
        except RecursionError:
            findings.append(_finding(
                "nesting_exceeds_parser_limit", "error", 1, 1,
                "Container nesting exceeds this interpreter's JSON "
                "parser recursion limit — json.loads itself raised "
                "RecursionError while parsing; split or flatten the "
                "document",
            ))
            findings.extend(self._long_line_findings(text))
            if had_bom:
                _shift_after_bom(findings)
            return self._lint_result(text, findings)

        # Rule: scalar-only root (legal, info).
        if not isinstance(value, (dict, list)):
            findings.append(_finding(
                "scalar_only_document", "info", 1, 1,
                "Document is a bare scalar "
                f"({type(value).__name__}) — legal JSON, but often an "
                "unintended fragment of an object or array",
            ))

        scan = _scan_text(text)

        # Rule: duplicate keys — hook is the value truth, scanner
        # holds the positions; they are reconciled per object.
        findings.extend(self._duplicate_findings(hook, scan))

        # Rule: NaN / Infinity literals (accepted by json.loads —
        # flagged as non-RFC with the strictness note).
        for tok in scan["nan_tokens"]:
            findings.append(_finding(
                "non_rfc_number_literal", "info",
                tok["line"], tok["col"],
                f"{tok['token']} is not RFC 8259 JSON — json.loads "
                "accepts it by default, but strict parsers and "
                "serializers (json.dumps with allow_nan=False) reject "
                "it; use null or a finite number",
            ))

        # Rule: integer-valued floats in float form (1.0 vs 1).
        for tok in scan["float_form_ints"]:
            findings.append(_finding(
                "mixed_number_formats", "info",
                tok["line"], tok["col"],
                f"number {tok['token']} is an integer-valued float — "
                f"JSON does not distinguish {tok['token']} from "
                f"{tok['int_form']}, but float spelling usually "
                "signals an accidental type leak from a float-typed "
                "producer",
            ))

        # Rule: very long lines (text-level, parse-independent).
        findings.extend(self._long_line_findings(text))

        # Rule: deep nesting (info).
        if scan["deep_pos"] is not None:
            line, col = scan["deep_pos"]
            findings.append(_finding(
                "deeply_nested", "info", line, col,
                f"Container nesting reaches depth {scan['max_depth']} "
                f"(threshold {self.deep_nesting_threshold}) — deeply "
                "nested documents are hard to review and to query",
            ))

        # Rule: mixed key naming styles inside one object (info).
        findings.extend(self._key_case_findings(scan))

        if had_bom:
            _shift_after_bom(findings)
        return self._lint_result(text, findings)

    def _lint_result(
        self, text: str, findings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Sort findings deterministically and build the summary."""
        findings.sort(key=lambda f: (f["line"], f["col"], f["code"]))
        rule_counts: Dict[str, int] = {}
        severity_counts = {"error": 0, "warning": 0, "info": 0}
        for f in findings:
            rule_counts[f["code"]] = rule_counts.get(f["code"], 0) + 1
            severity_counts[f["severity"]] += 1
        return {
            "mode": "lint",
            "valid_json": severity_counts["error"] == 0,
            "findings": findings,
            "summary": {
                "findings": len(findings),
                "severity_counts": severity_counts,
                "rule_counts": dict(sorted(rule_counts.items())),
                "lines": len(text.split("\n")),
                "chars": len(text),
            },
        }

    def _long_line_findings(self, text: str) -> List[Dict[str, Any]]:
        """Info findings for lines longer than the threshold.

        Lines are delimited by ``\\n`` alone — the convention every
        other position rule and ``json.JSONDecodeError`` use — so a
        raw U+2028/U+0085 inside a string (legal JSON, and one line
        to this tool) can never split a line in half here.
        """
        out = []
        for idx, line in enumerate(text.split("\n"), start=1):
            if len(line) > self.long_line_threshold:
                out.append(_finding(
                    "very_long_lines", "info", idx, 1,
                    f"Line {idx} is {len(line)} characters long "
                    f"(threshold {self.long_line_threshold}) — "
                    "single-line payloads are hard to review and to "
                    "diff",
                ))
        return out

    def _duplicate_findings(
        self, hook: _Hook, scan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Duplicate-key findings: hook truth, scanner positions.

        The scanner emits one finding per duplicated name per object,
        at the position of its *second* occurrence (the point where
        the earlier value starts being shadowed), and only for names
        the hook confirmed — if the scanner cannot locate a confirmed
        duplicate (which would mean a scanner escape-decoding gap), a
        positionless fallback finding is still emitted so the defect
        is never silently dropped.
        """
        out = []
        confirmed: List[str] = [
            name for dups in hook.duplicates for name in dups
        ]
        for scope in scan["scopes"]:
            positions = scope.get("positions", {})
            for name in sorted(set(scope["names"])):
                if len(positions.get(name, [])) < 2:
                    continue
                occurrences = positions[name]
                line, col = occurrences[1]
                out.append(_finding(
                    "duplicate_key", "warning", line, col,
                    f"Duplicate key {json.dumps(name, ensure_ascii=False)} "
                    f"in one object — appears {len(occurrences)} times; "
                    "json.loads silently keeps the LAST value, so every "
                    "earlier value is lost",
                ))
                if name in confirmed:
                    confirmed.remove(name)
        # Hook-confirmed duplicates the scanner could not place.
        for name in confirmed:
            out.append(_finding(
                "duplicate_key", "warning", 1, 1,
                f"Duplicate key {json.dumps(name, ensure_ascii=False)} "
                "in one object (position undetermined) — json.loads "
                "silently keeps the LAST value",
            ))
        return out

    def _key_case_findings(
        self, scan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Info findings for objects mixing camelCase and snake_case."""
        out = []
        for scope in scan["scopes"]:
            names = scope["names"]
            if len(names) < 2:
                continue
            snake = [k for k in names if _SNAKE.match(k)]
            camel = [k for k in names if _CAMEL.match(k)]
            if snake and camel:
                line, col = scope["open"]
                out.append(_finding(
                    "inconsistent_key_case", "info", line, col,
                    f"Object mixes key naming styles — camelCase "
                    f"({camel[0]!r}) and snake_case ({snake[0]!r}) in "
                    "the same object; pick one convention",
                ))
        return out

    # ------------------------------------------------------------------ #
    # profile
    # ------------------------------------------------------------------ #

    def _profile(self, text: str) -> Dict[str, Any]:
        had_bom, text = _strip_bom(text)
        if had_bom:
            return {
                "mode": "profile",
                "error": {
                    "code": "bom_not_allowed",
                    "message": "Document starts with a UTF-8 BOM "
                    "(U+FEFF) — illegal in JSON; strip the sigil "
                    "(fix_hints mode returns the stripped text)",
                    "line": 1,
                    "col": 1,
                },
            }
        if not text.strip():
            return {
                "mode": "profile",
                "error": {
                    "code": "empty_document",
                    "message": "Document is empty — nothing to profile",
                    "line": 1,
                    "col": 1,
                },
            }
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            return _syntax_payload("profile", text, exc)
        except RecursionError:
            return {
                "mode": "profile",
                "error": {
                    "code": "nesting_exceeds_parser_limit",
                    "message": "Container nesting exceeds this "
                    "interpreter's JSON parser recursion limit — "
                    "json.loads itself raised RecursionError while "
                    "parsing; nothing can be profiled",
                    "line": 1,
                    "col": 1,
                },
            }
        profile = _walk_profile(value)
        profile["mode"] = "profile"
        return profile

    # ------------------------------------------------------------------ #
    # fix_hints
    # ------------------------------------------------------------------ #

    def _fix_hints(self, text: str) -> Dict[str, Any]:
        had_bom, stripped = _strip_bom(text)

        if not stripped.strip():
            code = "bom_not_allowed" if had_bom else "empty_document"
            return {
                "mode": "fix_hints",
                "error": {
                    "code": code,
                    "message": (
                        "Document starts with a UTF-8 BOM and nothing "
                        "else — strip the sigil, then provide a value"
                        if had_bom else
                        "Document is empty — nothing to hint"
                    ),
                    "line": 1,
                    "col": 1,
                },
            }

        try:
            json.loads(stripped)
        except json.JSONDecodeError as exc:
            # Broken text: only the classification is a safe hint.
            payload = _syntax_payload("fix_hints", stripped, exc)
            payload["error"]["message"] += (
                "; fix the syntax error first — hinting beyond it "
                "would guess"
            )
            if had_bom:
                _shift_after_bom([payload["error"]])
            return payload
        except RecursionError:
            return {
                "mode": "fix_hints",
                "error": {
                    "code": "nesting_exceeds_parser_limit",
                    "message": "Container nesting exceeds this "
                    "interpreter's JSON parser recursion limit — "
                    "json.loads itself raised RecursionError while "
                    "parsing; no hint is safe past that point",
                    "line": 1,
                    "col": 1,
                },
            }

        hints: List[Dict[str, Any]] = []

        if had_bom:
            hints.append({
                "code": "bom_not_allowed",
                "line": 1,
                "col": 1,
                "message": "Strip the leading UTF-8 BOM (U+FEFF) — "
                "the only fix that is purely textual, so it is "
                "applied in fixed_text",
                "suggestion": "remove the BOM character",
                "applied": True,
            })

        scan = _scan_text(stripped)
        for tok in scan["nan_tokens"]:
            hints.append({
                "code": "non_rfc_number_literal",
                "line": tok["line"],
                "col": tok["col"],
                "message": f"{tok['token']} is not RFC 8259 JSON; "
                "replacing a value changes document semantics, so "
                "this stays a suggestion — never auto-applied",
                "suggestion": "null",
                "applied": False,
            })
        for tok in scan["float_form_ints"]:
            hints.append({
                "code": "mixed_number_formats",
                "line": tok["line"],
                "col": tok["col"],
                "message": f"{tok['token']} is an integer-valued "
                "float; renumbering is left to the owner — never "
                "auto-applied",
                "suggestion": tok["int_form"],
                "applied": False,
            })

        hints.sort(key=lambda h: (h["line"], h["col"], h["code"]))
        if had_bom:
            _shift_after_bom(hints)
        result: Dict[str, Any] = {
            "mode": "fix_hints",
            "hints": hints,
            "fixed_text": stripped if had_bom else None,
            "note": "Only the BOM strip is auto-applicable (purely "
            "textual); every other hint is a suggestion at an exact "
            "position — structural or value-changing edits are "
            "never applied automatically",
        }
        return result
