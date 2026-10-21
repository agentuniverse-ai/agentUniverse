#!/usr/bin/env python3
"""Detect and neutralize spreadsheet formula injection (OWASP "CSV Injection")."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import csv
import io
import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# OWASP CSV Injection trigger set: a cell whose first character is one of
# "=", "+", "-", "@", TAB (U+0009) or CR (U+000D) can be interpreted as a
# formula by Excel, Google Sheets or LibreOffice on import. Note that "%" is
# deliberately NOT part of the trigger set: spreadsheets treat a leading "%"
# as a number-format hint (percentage style), never as a formula start, so
# "%"-prefixed cells are documented as excluded instead of being flagged.
_TRIGGER_CHARS = "=+-@\t\r"

# Characters stripped before trigger detection. TAB and CR are themselves
# OWASP triggers used as obfuscation prefixes; the remaining code points are
# zero-width and bidi controls (U+200B-U+200D, U+200E-U+200F, U+202A-U+202E,
# U+2060, U+2066-U+2069, U+FEFF) that can visually hide a payload.
_TAB_CR = "\t\r"
_BIDI_CONTROLS = "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"
_ZERO_WIDTH = "\u200b\u200c\u200d\u2060\ufeff"
_OBFUSCATION_PREFIX = _TAB_CR + ("\u200b\u200c\u200d\u200e\u200f"
                                 "\u202a\u202b\u202c\u202d\u202e"
                                 "\u2060\u2066\u2067\u2068\u2069\ufeff")

# Fullwidth homoglyphs of the trigger characters. Excel does NOT evaluate
# these as formulas; they are reported at info level because normalization
# pipelines or human review may confuse them with the ASCII trigger.
_FULLWIDTH_TRIGGERS = {"\uff1d": "=", "\uff0b": "+", "\uff0d": "-", "\uff20": "@"}

# DDE-style reference: an identifier immediately followed by "|", as in
# =cmd|' /C calc'!A0 or =SUM(1+9)*cmd|'/C calc'!A0 (cmd, MSEXCEL, ...).
_DDE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\|")

# Remote-content functions whose presence in a formula-prefixed cell means
# outbound requests or clickable payloads on import.
_REMOTE_FUNC_RE = re.compile(
    r"\b(HYPERLINK|WEBSERVICE|IMPORTXML|IMPORTHTML|IMPORTFEED|IMPORTDATA|IMPORTRANGE)\s*\(",
    re.IGNORECASE,
)

# Function-call shape after a trigger character, e.g. "SUM(" in "=SUM(1,2)".
_FUNC_SHAPE_RE = re.compile(r"^[A-Za-z_]\w*\s*\(")

# Pure numeric literal (including a leading sign): "-2", "+3.14", "-1e-5".
# These parse as harmless numbers, not formulas, so they are not flagged.
_NUMERIC_RE = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")

_ARITHMETIC_OPS = "+-*/^"

# Sensitive header keywords used by the "headers" mode and by scan summaries
# to prioritize reporting. Sorted for deterministic matching.
_SENSITIVE_HIGH = (
    "access_key", "api_key", "apikey", "auth", "credential", "credentials",
    "passwd", "password", "private_key", "pwd", "secret", "token",
)
_SENSITIVE_MEDIUM = (
    "account", "address", "balance", "bic", "birth", "birthday",
    "card_number", "credit_card", "dob", "email", "iban", "income",
    "license", "mail", "mobile", "passport", "phone", "salary", "ssn", "wage",
)

_RISK_ORDER = {"high": 0, "medium": 1, "info": 2, "low": 3, "none": 4}

_SPREADSHEET_BEHAVIOR = {
    "DDE": (
        "Excel and LibreOffice parse the cell as a formula on import and issue a "
        "Dynamic Data Exchange (DDE) request, launching the referenced program "
        "(for example cmd.exe) or connecting to the named DDE server."
    ),
    "HYPERLINK": (
        "Excel, Google Sheets and LibreOffice parse the cell as a formula and "
        "embed a clickable link; following it opens the attacker-controlled URL."
    ),
    "WEBSERVICE": (
        "Excel evaluates the formula and performs an outbound HTTP request at "
        "recalculation time, which can exfiltrate cell contents."
    ),
    "IMPORTXML": (
        "Google Sheets fetches and parses the remote XML/HTML content on import, "
        "which can leak referenced cell data to the remote host."
    ),
    "IMPORT_FUNCTION": (
        "Google Sheets evaluates an IMPORT* function that fetches remote content "
        "(IMPORTHTML/IMPORTFEED/IMPORTDATA/IMPORTRANGE) on import."
    ),
    "AT_FUNCTION": (
        "Excel accepts the legacy '@'-prefixed formula (Lotus compatibility) and "
        "executes the function on import."
    ),
    "FORMULA_LIKE": (
        "Spreadsheets treat entries starting with =, +, - or @ as formulas, so "
        "the cell is evaluated instead of being stored as literal text."
    ),
    "QUOTE_ESCAPED": (
        "The leading apostrophe forces text mode, so nothing executes; the "
        "visible escape indicates prior sanitization or a hidden prefix."
    ),
    "HOMOGLYPH": (
        "Fullwidth lookalike characters are not formula triggers in Excel, so "
        "the cell is stored as text; the risk is confusing reviewers or "
        "downstream normalization into treating it as a formula."
    ),
    "RTL_OVERRIDE": (
        "Bidirectional control characters mangle the on-screen rendering, which "
        "can visually hide a payload from human reviewers."
    ),
}

_EXCLUSION_NOTES = (
    "Trigger set per OWASP CSV Injection: =, +, -, @, TAB (U+0009), CR (U+000D).",
    "Cells starting with % are NOT flagged: spreadsheets treat a leading % as a "
    "number-format hint (percentage style), never as a formula start.",
    "Pure numeric literals after a leading + or - (e.g. -2, +3.14, -1e-5, +2e+10) "
    "are parsed as numbers, not formulas, and are not flagged in scan results; "
    "the neutralize mode still prefixes them per the strict OWASP remediation.",
    "Fullwidth homoglyphs (U+FF1D/U+FF0B/U+FF0D/U+FF20) are not executable "
    "formula prefixes and are reported at info level only.",
)


def _a1_column(col: int) -> str:
    """Convert a 0-based column index to spreadsheet letters (0=A, 26=AA)."""
    letters = ""
    remaining = col
    while True:
        letters = chr(ord("A") + remaining % 26) + letters
        remaining = remaining // 26 - 1
        if remaining < 0:
            return letters


def _escape_ascii(value: str) -> str:
    """Render control/bidi characters as visible ASCII escapes."""
    return value.encode("unicode_escape").decode("ascii")


# Maximum number of hidden prefix characters echoed as evidence in findings
# and explain output; longer prefixes are summarized with a "..." marker so
# cell content is never echoed unbounded (cells can carry secrets/tokens).
_MAX_PREFIX_EVIDENCE = 12


def _evidence_prefix(prefix_hidden: str, lead: str) -> str:
    """Render a bounded, control-escaped evidence prefix (hidden chars + trigger)."""
    capped = prefix_hidden[:_MAX_PREFIX_EVIDENCE]
    marker = "..." if len(prefix_hidden) > _MAX_PREFIX_EVIDENCE else ""
    return _escape_ascii(capped) + marker + _escape_ascii(lead)


def _hidden_kind(prefix: str) -> str:
    """Describe which obfuscation character classes a prefix contains."""
    kinds = []
    if any(char in _TAB_CR for char in prefix):
        kinds.append("TAB/CR")
    if any(char in _BIDI_CONTROLS for char in prefix):
        kinds.append("bidi control")
    if any(char in _ZERO_WIDTH for char in prefix):
        kinds.append("zero-width")
    return "/".join(kinds) if kinds else "invisible"


def _classify_cell(value: str) -> dict[str, Any] | None:
    """Classify one cell value; return a finding dict or None when harmless.

    Detection first strips leading obfuscation characters (TAB, CR, zero-width
    and bidi controls), then applies the OWASP trigger rules in risk order:
    high (DDE, remote-content functions, legacy @-formulas), medium (potential
    formulas, obfuscated prefixes, visible quote-escapes), info (homoglyph and
    bidi tricks).
    """
    stripped = value.lstrip(_OBFUSCATION_PREFIX)
    prefix_hidden = value[: len(value) - len(stripped)]
    lead = stripped[:1]

    if lead in "=+-@":
        body = stripped[1:]
        if lead in "+-" and _NUMERIC_RE.fullmatch(stripped):
            return None
        obfuscation = (
            f"Obfuscated by leading {_hidden_kind(prefix_hidden)} prefix. " if prefix_hidden else ""
        )
        shown_prefix = _evidence_prefix(prefix_hidden, lead)
        if _DDE_RE.search(stripped):
            return {
                "code": "DDE",
                "risk": "high",
                "payload_prefix": shown_prefix,
                "reason": obfuscation
                + "Formula-prefixed cell contains a DDE reference (identifier followed "
                + "by '|'), the classic =cmd|' /C calc'!A0 command-execution vector.",
            }
        remote = _REMOTE_FUNC_RE.search(stripped)
        if remote:
            name = remote.group(1).upper()
            code = name if name in {"HYPERLINK", "WEBSERVICE", "IMPORTXML"} else "IMPORT_FUNCTION"
            return {
                "code": code,
                "risk": "high",
                "payload_prefix": shown_prefix,
                "reason": obfuscation
                + f"Formula-prefixed cell calls {name}(), which embeds a link or fetches "
                + "remote content when the spreadsheet evaluates it.",
            }
        if lead == "@" and _FUNC_SHAPE_RE.match(body):
            return {
                "code": "AT_FUNCTION",
                "risk": "high",
                "payload_prefix": shown_prefix,
                "reason": obfuscation
                + "Legacy '@'-prefixed function call (Lotus compatibility); Excel "
                + "executes it as a formula on import.",
            }
        if _FUNC_SHAPE_RE.match(body):
            return {
                "code": "FORMULA_LIKE",
                "risk": "medium",
                "payload_prefix": shown_prefix,
                "reason": obfuscation
                + "Bare trigger character followed by a function-call shape; the cell "
                + "is evaluated as a formula instead of literal text.",
            }
        if body[:1].isalpha():
            return {
                "code": "FORMULA_LIKE",
                "risk": "medium",
                "payload_prefix": shown_prefix,
                "reason": obfuscation
                + "Bare trigger character followed by letters; spreadsheets can parse "
                + "the entry as a formula or reference on import.",
            }
        if any(op in body for op in _ARITHMETIC_OPS):
            return {
                "code": "FORMULA_LIKE",
                "risk": "medium",
                "payload_prefix": shown_prefix,
                "reason": obfuscation
                + "Trigger character followed by an arithmetic expression; the cell is "
                + "evaluated as a formula on import.",
            }
        if lead == "=" and body:
            return {
                "code": "FORMULA_LIKE",
                "risk": "medium",
                "payload_prefix": shown_prefix,
                "reason": obfuscation
                + "Leading '=' makes the spreadsheet evaluate the cell as a formula.",
            }
        return None

    if lead == "'" and len(stripped) > 1:
        return {
            "code": "QUOTE_ESCAPED",
            "risk": "medium",
            "payload_prefix": "'",
            "reason": "Leading apostrophe quote-escape is visible; nothing executes, but "
            "the escape can hide a payload or mark prior sanitization.",
        }

    if any(char in _BIDI_CONTROLS for char in prefix_hidden):
        return {
            "code": "RTL_OVERRIDE",
            "risk": "info",
            "payload_prefix": _escape_ascii(prefix_hidden[:1]),
            "reason": "Cell starts with bidirectional control characters that mangle "
            "visual rendering and can hide a payload from reviewers.",
        }
    if lead in _FULLWIDTH_TRIGGERS:
        return {
            "code": "HOMOGLYPH",
            "risk": "info",
            "payload_prefix": _escape_ascii(lead),
            "reason": "Cell starts with the fullwidth homoglyph of "
            f"'{_FULLWIDTH_TRIGGERS[lead]}'; not an executable formula prefix, "
            "but a lookalike-confusion risk.",
        }
    return None


def _needs_neutralization(value: str) -> bool:
    """Return True when a cell starts with an OWASP trigger character."""
    return bool(value) and value[0] in _TRIGGER_CHARS


def _keyword_in_tokens(keyword: str, tokens: list[str]) -> bool:
    """Match a keyword against normalized header tokens at token boundaries.

    Single-token keywords must equal a whole token (so "secretary" does not
    match "secret"); compound keywords such as "credit_card" must equal
    consecutive tokens.
    """
    parts = keyword.split("_")
    if len(parts) == 1:
        return keyword in tokens
    return any(tokens[i : i + len(parts)] == parts for i in range(len(tokens) - len(parts) + 1))


def _header_sensitivity(name: str) -> tuple[str, list[str]]:
    """Weigh one header name against the sensitive keyword lists."""
    normalized = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    tokens = normalized.split("_") if normalized else []
    for risk_level, keywords in (("high", _SENSITIVE_HIGH), ("medium", _SENSITIVE_MEDIUM)):
        matched = [kw for kw in keywords if _keyword_in_tokens(kw, tokens)]
        if matched:
            return risk_level, matched
    return "low", []


class CsvInjectionTool(Tool):
    """Detect, explain, and neutralize CSV/TSV spreadsheet formula injection.

    Unlike structure-oriented CSV linters, this tool inspects cell VALUES for
    payloads (DDE, HYPERLINK, WEBSERVICE, IMPORT*, legacy @-formulas) that
    Excel, Google Sheets, or LibreOffice would auto-execute on import.
    """

    max_csv_chars: int = 5_000_000
    max_cells: int = 200_000
    max_findings: int = 2_000
    max_snippet: int = 80

    _MODES: ClassVar[tuple[str, ...]] = ("scan", "neutralize", "explain", "headers")
    _DIALECTS: ClassVar[tuple[str, ...]] = ("excel", "excel-tab", "unix")
    _DIALECT_DELIMITERS: ClassVar[dict[str, str]] = {"excel": ",", "excel-tab": "\t", "unix": ","}

    def execute(
        self,
        mode: str,
        csv_text: str | None = None,
        cell_value: str | None = None,
        dialect: str = "excel",
        delimiter: str | None = None,
        quotechar: str | None = None,
        has_header: bool = True,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._validated_mode(mode)
            if not isinstance(has_header, bool):
                raise TypeError("has_header must be a boolean")
            if operation == "explain":
                return self._explain(cell_value)
            reader_kwargs = self._validated_dialect(dialect, delimiter, quotechar)
            text = self._validated_text(csv_text)
            rows = self._parse_rows(text, reader_kwargs)
            if operation == "scan":
                return self._scan(rows, has_header, dialect, delimiter, quotechar)
            if operation == "neutralize":
                return self._neutralize(text, rows, reader_kwargs)
            return self._headers(rows, has_header)
        except (TypeError, ValueError) as exc:
            return {"status": "error", "error_type": "validation_error", "error": str(exc)}
        except csv.Error as exc:
            return {"status": "error", "error_type": "parse_error", "error": f"CSV parsing failed: {exc}"}
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return {"status": "error", "error_type": "operation_error", "error": f"Scan failed: {exc}"}

    def _validate_config(self) -> None:
        """Validate the bounded-size class attributes."""
        for name in ("max_csv_chars", "max_cells", "max_findings", "max_snippet"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.max_snippet > 10_000:
            raise ValueError("max_snippet must not exceed 10000")

    @staticmethod
    def _validated_mode(value: Any) -> str:
        """Validate and normalize the mode argument."""
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in CsvInjectionTool._MODES:
            raise ValueError("mode must be scan, neutralize, explain, or headers")
        return mode

    def _validated_text(self, value: Any) -> str:
        """Validate the CSV text argument against type and size caps."""
        if not isinstance(value, str):
            raise TypeError("csv_text must be a string")
        if len(value) > self.max_csv_chars:
            raise ValueError(f"csv_text exceeds max_csv_chars ({self.max_csv_chars})")
        return value

    @staticmethod
    def _validated_dialect(dialect: Any, delimiter: Any, quotechar: Any) -> dict[str, Any]:
        """Validate dialect options and build csv.reader keyword arguments."""
        if not isinstance(dialect, str):
            raise TypeError("dialect must be a string")
        name = dialect.strip().lower()
        if name not in CsvInjectionTool._DIALECTS:
            raise ValueError("dialect must be excel, excel-tab, or unix")
        if delimiter is None and quotechar is None:
            return {"dialect": name}
        if delimiter is not None:
            if not isinstance(delimiter, str) or len(delimiter) != 1 or delimiter in "\r\n":
                raise ValueError("delimiter must be a single character other than CR/LF")
        if quotechar is not None:
            if not isinstance(quotechar, str) or len(quotechar) != 1 or quotechar in "\r\n":
                raise ValueError("quotechar must be a single character other than CR/LF")
        resolved_delimiter = delimiter or CsvInjectionTool._DIALECT_DELIMITERS[name]
        resolved_quote = quotechar or '"'
        if resolved_delimiter == resolved_quote:
            raise ValueError("delimiter and quotechar must differ")
        return {
            "delimiter": resolved_delimiter,
            "quotechar": resolved_quote,
            "doublequote": True,
            "escapechar": None,
            "skipinitialspace": False,
            "quoting": csv.QUOTE_MINIMAL,
        }

    def _parse_rows(self, text: str, reader_kwargs: dict[str, Any]) -> list[list[str]]:
        """Parse the CSV text into rows, enforcing the cell-count cap.

        csv.field_size_limit is raised to max_csv_chars for the duration of
        the parse (so a legitimate 1 MB cell is accepted) and restored after,
        keeping the bound deterministic.
        """
        previous_limit = csv.field_size_limit(self.max_csv_chars + 1)
        try:
            rows = list(csv.reader(io.StringIO(text), **reader_kwargs))
        finally:
            csv.field_size_limit(previous_limit)
        cells = sum(len(row) for row in rows)
        if cells > self.max_cells:
            raise ValueError(f"input exceeds max_cells ({self.max_cells}): {cells} cells")
        return rows

    def _snippet(self, value: str) -> str:
        """Truncate a cell value to max_snippet characters."""
        if len(value) <= self.max_snippet:
            return value
        return value[: self.max_snippet] + "..."

    @staticmethod
    def _header_names(rows: list[list[str]], has_header: bool) -> list[str]:
        """Derive header names from the first row or synthesize column names."""
        if not rows:
            return []
        width = max(len(row) for row in rows)
        if has_header:
            first = rows[0]
            return [
                first[col] if col < len(first) and first[col] != "" else f"column{col + 1}"
                for col in range(width)
            ]
        return [f"column{col + 1}" for col in range(width)]

    def _scan(
        self,
        rows: list[list[str]],
        has_header: bool,
        dialect: str,
        delimiter: str | None,
        quotechar: str | None,
    ) -> dict[str, Any]:
        """Scan parsed rows and assemble findings plus the whole-file summary."""
        findings: list[dict[str, Any]] = []
        per_column: dict[int, dict[str, Any]] = {}
        risk_counts = {"high": 0, "medium": 0, "info": 0}
        unique_payloads: set[str] = set()
        truncated = False
        cells_scanned = 0
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                cells_scanned += 1
                finding = _classify_cell(value)
                if finding is None:
                    continue
                risk_counts[finding["risk"]] += 1
                unique_payloads.add(finding["payload_prefix"])
                stats = per_column.setdefault(
                    col_index,
                    {"col": col_index, "cells": 0, "findings": 0, "high": 0, "medium": 0, "info": 0},
                )
                stats["findings"] += 1
                stats[finding["risk"]] += 1
                if len(findings) < self.max_findings:
                    findings.append(
                        {
                            "row": row_index,
                            "col": col_index,
                            "cell_ref": f"{_a1_column(col_index)}{row_index + 1}",
                            "code": finding["code"],
                            "payload_prefix": finding["payload_prefix"],
                            "formula_snippet": self._snippet(value),
                            "risk": finding["risk"],
                            "reason": finding["reason"],
                        }
                    )
                else:
                    truncated = True
        for col_index, stats in per_column.items():
            stats["cells"] = sum(1 for row in rows if col_index < len(row))
        names = self._header_names(rows, has_header)
        headers_involved = []
        for col_index in sorted(per_column):
            stats = per_column[col_index]
            name = names[col_index] if col_index < len(names) else f"column{col_index + 1}"
            sensitivity, _ = _header_sensitivity(name)
            headers_involved.append(
                {
                    "header": name,
                    "column": _a1_column(col_index),
                    "col": col_index,
                    "findings": stats["findings"],
                    "max_risk": next(risk for risk in ("high", "medium", "info") if stats[risk]),
                    "sensitivity": sensitivity,
                }
            )
        headers_involved.sort(
            key=lambda item: (_RISK_ORDER[item["max_risk"]], _RISK_ORDER[item["sensitivity"]], item["col"])
        )
        per_column_list = [
            dict(per_column[col], column=_a1_column(col), header=names[col] if col < len(names) else None)
            for col in sorted(per_column)
        ]
        return {
            "status": "success",
            "mode": "scan",
            "dialect": self._dialect_summary(dialect, delimiter, quotechar),
            "findings": findings,
            "summary": {
                "rows_scanned": len(rows),
                "cells_scanned": cells_scanned,
                "unique_payloads": len(unique_payloads),
                "risk_counts": risk_counts,
                "per_column": per_column_list,
                "headers_involved": headers_involved,
                "findings_truncated": truncated,
                "notes": list(_EXCLUSION_NOTES),
            },
        }

    @staticmethod
    def _dialect_summary(dialect: str, delimiter: str | None, quotechar: str | None) -> dict[str, Any]:
        """Describe the dialect actually used for parsing."""
        name = dialect.strip().lower()
        return {
            "name": name,
            "delimiter": delimiter or CsvInjectionTool._DIALECT_DELIMITERS[name],
            "quotechar": quotechar or '"',
        }

    def _neutralize(self, text: str, rows: list[list[str]], reader_kwargs: dict[str, Any]) -> dict[str, Any]:
        """Prefix "'" onto trigger cells and re-serialize with the csv module.

        The round-trip through csv.reader/csv.writer keeps the document
        structurally valid: embedded delimiters, quotes, and newlines inside
        unchanged cells survive as identical parsed values, and only cells
        starting with an OWASP trigger character (=, +, -, @, TAB, CR) receive
        the recommended apostrophe prefix.
        """
        changed: list[dict[str, Any]] = []
        safe_rows: list[list[str]] = []
        changed_count = 0
        for row_index, row in enumerate(rows):
            safe_row: list[str] = []
            for col_index, value in enumerate(row):
                if _needs_neutralization(value):
                    escaped = "'" + value
                    changed_count += 1
                    if len(changed) < self.max_findings:
                        changed.append(
                            {
                                "row": row_index,
                                "col": col_index,
                                "cell_ref": f"{_a1_column(col_index)}{row_index + 1}",
                                "before": self._snippet(value),
                                "after": self._snippet(escaped),
                            }
                        )
                    safe_row.append(escaped)
                else:
                    safe_row.append(value)
            safe_rows.append(safe_row)
        lineterminator = "\r\n" if "\r\n" in text else "\n"
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator=lineterminator, **self._writer_kwargs(reader_kwargs))
        writer.writerows(safe_rows)
        safe_csv = buffer.getvalue()
        previous_limit = csv.field_size_limit(self.max_csv_chars + 1)
        try:
            reparsed = list(csv.reader(io.StringIO(safe_csv), **reader_kwargs))
        finally:
            csv.field_size_limit(previous_limit)
        return {
            "status": "success",
            "mode": "neutralize",
            "safe_csv": safe_csv,
            "changed_cells": changed,
            "changed_count": changed_count,
            "changed_cells_truncated": changed_count > self.max_findings,
            "dialect_preserved": reparsed == safe_rows,
        }

    @staticmethod
    def _writer_kwargs(reader_kwargs: dict[str, Any]) -> dict[str, Any]:
        """Adapt reader dialect options to csv.writer keyword arguments."""
        if "dialect" in reader_kwargs:
            return {"dialect": reader_kwargs["dialect"]}
        return dict(reader_kwargs)

    def _headers(self, rows: list[list[str]], has_header: bool) -> dict[str, Any]:
        """Rank header names by data sensitivity for reporting priority."""
        names = self._header_names(rows, has_header)
        ranked = []
        for col_index, name in enumerate(names):
            sensitivity, matched = _header_sensitivity(name)
            ranked.append(
                {
                    "name": name,
                    "col": col_index,
                    "column": _a1_column(col_index),
                    "sensitivity": sensitivity,
                    "matched_keywords": matched,
                    "why": (
                        f"matches sensitive keywords: {', '.join(matched)}" if matched else "no sensitive keyword match"
                    ),
                }
            )
        ranked.sort(key=lambda item: (_RISK_ORDER[item["sensitivity"]], item["col"]))
        return {
            "status": "success",
            "mode": "headers",
            "has_header": has_header,
            "rows_scanned": len(rows),
            "headers": ranked,
            "notes": list(_EXCLUSION_NOTES),
        }

    def _explain(self, value: Any) -> dict[str, Any]:
        """Explain what one cell value would do in a spreadsheet."""
        if not isinstance(value, str):
            raise TypeError("cell_value must be a string")
        if len(value) > self.max_csv_chars:
            raise ValueError(f"cell_value exceeds max_csv_chars ({self.max_csv_chars})")
        finding = _classify_cell(value)
        stripped = value.lstrip(_OBFUSCATION_PREFIX)
        prefix_hidden = value[: len(value) - len(stripped)]
        lead = stripped[:1]
        first = value[:1]
        if first in _TRIGGER_CHARS and first not in _OBFUSCATION_PREFIX:
            trigger = _escape_ascii(first)
        elif lead in "=+-@":
            trigger = _evidence_prefix(prefix_hidden, lead)
        elif lead == "'":
            trigger = "'"
        else:
            trigger = None
        code = finding["code"] if finding else None
        risk = finding["risk"] if finding else "none"
        if stripped:
            control_escaped = _evidence_prefix(prefix_hidden, lead) + stripped[1:]
        else:
            marker = "..." if len(value) > _MAX_PREFIX_EVIDENCE else ""
            control_escaped = _escape_ascii(value[:_MAX_PREFIX_EVIDENCE]) + marker
        return {
            "status": "success",
            "mode": "explain",
            "cell_value_snippet": self._snippet(value),
            "is_payload": risk in {"high", "medium"},
            "risk": risk,
            "code": code,
            "trigger": trigger,
            "decoded_variants": {
                "python_repr": self._snippet(repr(value)),
                "leading_whitespace_stripped": self._snippet(stripped),
                "control_escaped": self._snippet(control_escaped),
            },
            "what_spreadsheet_would_do": _SPREADSHEET_BEHAVIOR.get(
                code, "Stored as literal text; no formula interpretation."
            ),
            "recommended_neutralization": (
                self._snippet("'" + value) if _needs_neutralization(value) else None
            ),
            "notes": list(_EXCLUSION_NOTES),
        }
