#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: env_lint_tool.py

"""dotenv (``.env``) *file linting* tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the quality layer for dotenv files: unlike
``EnvFileTool`` (#3727, parse / edit dotenv text) and
``EnvSchemaTool`` (#4002, validate dotenv *values* against a declared
schema), this tool lints the *file itself* — no schema, no declared
contract needed, just the raw ``.env`` text and 17 deterministic
style / consistency / syntax rules. Three modes, all offline and
deterministic:

* ``lint`` — analyze ``.env`` text and report findings as
  ``[{code, severity, line, message}]`` sorted by ``(line, code)``:

  - Syntax (severity ``error``): ``duplicate_keys`` (same exact key
    defined twice — dotenv loaders silently keep the last value),
    ``key_with_spaces`` (dotenv keys cannot contain spaces — the
    line reads like ``MY KEY=1``), ``line_without_assignment``
    (bare text that is neither blank, comment nor ``KEY=VALUE``).
  - Correctness risks (severity ``warning``):
    ``inconsistent_key_case`` (``FOO`` and ``foo`` both present — on
    case-insensitive platforms one silently shadows the other),
    ``empty_value_without_default_marker`` (``KEY=`` with neither a
    value nor a same-line ``# default`` / ``# optional`` comment —
    the empty string usually means "forgot to fill me in"),
    ``value_with_unquoted_spaces`` (shell sourcing would split the
    value into multiple words), ``value_with_unquoted_hash``
    (parsers disagree whether an unquoted ``#`` starts a comment or
    is data — e.g. ``COLOR=#fff`` and ``KEY=v # note``),
    ``spacing_around_equals`` (``KEY = V`` and ``KEY=V`` mixed in
    one file — some parsers reject the spaced form outright),
    ``quote_style_mixing`` and ``export_prefix_mixing`` (part of the
    file uses one style, part the other — flagged on every line that
    deviates from the dominant style, which must strictly outnumber
    every other; a tie at the top stays silent), ``bom_present`` (a
    UTF-8 BOM becomes part of the first key for many loaders).
  - Style (severity ``info``): ``lowercase_key`` (convention is
    UPPER_SNAKE), ``trailing_whitespace``,
    ``missing_final_newline``, ``crlf_line_endings``,
    ``very_long_line`` (>5000 characters), ``order_grouping_breaks``
    (a key sorts *below* its predecessor inside a run of consecutive
    assignment lines with no blank / comment separator — insert a
    blank line to start a new block or reorder; runs with a
    separator between them are independent blocks and never
    compared).

* ``fix_hints`` — apply the *safe textual* fixes only (exact line
  edits, never a re-format): strip the BOM, normalize CRLF line
  endings to LF, strip trailing whitespace, quote unquoted values
  that contain spaces or ``#`` (double quotes, backslashes and
  embedded double quotes escaped so the *parsed* value is unchanged;
  a whitespace-preceded inline comment stays outside the quotes) and
  add the final newline. The payload carries each ``fixes`` entry
  ``{line, fix, before, after}``, the full ``fixed_text`` and a
  re-lint of it (``remaining_findings`` / ``remaining_codes`` /
  ``resolved_codes``) proving the targeted codes are gone. Spacing,
  export prefixes, key case, ordering and duplicate keys are never
  touched — those need a human decision; quoting only the risky
  values can also *surface* a ``quote_style_mixing`` finding against
  the untouched majority, which the re-lint reports honestly.
  Idempotent: fixing an already-fixed text changes nothing.

* ``stats`` — file-level arithmetic: ``vars`` (distinct keys),
  ``exported_vars``, ``quoted`` / ``unquoted`` / ``empty`` value
  counts and ``quoted_ratio``, ``total_lines`` / ``blank_lines`` /
  ``comment_lines`` / ``assignment_lines``, an ``encoding`` block
  (BOM flag, ``line_ending`` ``lf`` | ``crlf`` | ``mixed`` |
  ``none``, ``final_newline``) and a ``grouping`` block
  (``runs``, ``order_breaks``, ``assessment``: ``alphabetical`` /
  ``mostly_alphabetical`` (breaks <= a quarter of the assignment
  lines) / ``unsorted`` / ``no assignments``).

Secret masking (family rule, same as ``EnvFileTool`` /
``EnvSchemaTool``): a variable whose *name* contains ``KEY``,
``SECRET``, ``PASSWORD`` or ``TOKEN`` (case-insensitive substring)
never has its value echoed in full — fix ``before`` / ``after``
snapshots render the value as ``***`` (quote characters preserved),
unparseable-line previews render the whole line as ``***`` when it
contains a secret marker, and ``fixed_text`` masks secret values the
same way (it is a review artifact; the per-line fixes carry the
exact edits). Finding *messages* never contain values at all, only
key names.

Value parsing follows dotenv rules consistent with the family
tools: blank / ``#`` lines are skipped, an optional ``export``
prefix is accepted, the first ``=`` splits key from value, keys
match ``[A-Za-z_][A-Za-z0-9_]*``, double-quoted values unescape
``\\n`` ``\\t`` ``\\r`` ``\\\\`` ``\\"``, single-quoted values are
fully literal, and unquoted values end at the first ``#`` directly
preceded by whitespace (a ``#`` glued directly after ``=`` or into
text such as ``KEY=#c`` is data). Unterminated quotes are treated
as quoted-to-end-of-line (a lint result, not a crash). Empty
*quoted* values (``KEY=""``) count as intentionally empty and are
not flagged; empty values have no quote style and are excluded from
quote-mixing statistics.

Malformed *parameters* (unknown mode, non-string text, oversized
input) raise a ``ValueError`` before any computation. The tool never
touches the filesystem or the network.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# dotenv line classification (family-consistent rules)
# --------------------------------------------------------------------- #

# assignment := [export + whitespace] key [whitespace*] "=" rest
_ASSIGN_RE = re.compile(r"(?P<export>export[ \t]+)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)[ \t]*=")
# A line that *looks like* an assignment whose key part contains
# spaces ("MY KEY=1") — the illegal-key heuristic.
_SPACED_KEY_RE = re.compile(r"(?:export[ \t]+)?([A-Za-z_][A-Za-z0-9_]*(?:[ \t]+[A-Za-z0-9_]+)*)[ \t]*=")
# Escape sequences unescaped inside double-quoted values.
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"'}

# --------------------------------------------------------------------- #
# lint rule registry: code -> severity (single source of truth)
# --------------------------------------------------------------------- #

SEVERITIES = {
    "duplicate_keys": "error",
    "key_with_spaces": "error",
    "line_without_assignment": "error",
    "inconsistent_key_case": "warning",
    "empty_value_without_default_marker": "warning",
    "value_with_unquoted_spaces": "warning",
    "value_with_unquoted_hash": "warning",
    "spacing_around_equals": "warning",
    "quote_style_mixing": "warning",
    "export_prefix_mixing": "warning",
    "bom_present": "warning",
    "lowercase_key": "info",
    "trailing_whitespace": "info",
    "missing_final_newline": "info",
    "crlf_line_endings": "info",
    "very_long_line": "info",
    "order_grouping_breaks": "info",
}

RULES = tuple(sorted(SEVERITIES))

# Name substrings marking a variable as secret-ish (case-insensitive).
_SECRET_MARKERS = ("KEY", "SECRET", "PASSWORD", "TOKEN")

_MASK = "***"
_PREVIEW_CHARS = 24
_VERY_LONG_LINE = 5_000
_MAX_TEXT_CHARS = 100_000


class EnvLintTool(Tool):
    """dotenv (``.env``) file linting tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``.env`` text input;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "env_lint_tool"
    description: str = (
        "Env lint tool — lint a dotenv (.env) file for style, "
        "consistency and syntax problems with no schema needed, purely "
        "on the Python stdlib, no network required. lint mode reports "
        "findings [{code, severity, line, message}] from 17 "
        "deterministic rules (duplicate keys, case collisions, quote/"
        "export/spacing consistency, unquoted spaces and '#' in values, "
        "empty values without a default marker, bare lines, keys with "
        "spaces, lowercase keys, trailing whitespace, final newline, "
        "CRLF, BOM, very long lines, alphabetical block breaks) "
        "(mode='lint'); fix_hints applies only the safe textual fixes "
        "with exact line edits and re-lints the result "
        "(mode='fix_hints'); stats summarizes variable counts, quoted "
        "ratio, comment/blank lines and grouping (mode='stats'). "
        "Values of secret-ish names (KEY/SECRET/PASSWORD/TOKEN) are "
        "never echoed in full."
    )

    MODES: ClassVar[tuple] = ("lint", "fix_hints", "stats")

    max_text_chars: int = _MAX_TEXT_CHARS

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(self, mode: Any = None, text: Any = None) -> dict[str, Any]:
        """Run one .env lint operation.

        Args:
            mode (str): One of ``lint`` / ``fix_hints`` / ``stats``.
            text (str): The ``.env`` text (required for every mode;
                may be empty — an empty file lints clean).

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the mode-specific fields).

        Raises:
            ValueError: If a parameter is malformed (raised before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})")
        clean_text = self._validate_text(text)
        prepared = self._prepare(clean_text)
        if mode == "lint":
            return self._run_lint(prepared)
        if mode == "fix_hints":
            return self._run_fix(prepared)
        return self._run_stats(prepared)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"env_lint_tool: {message}")

    def _validate_text(self, text: Any) -> str:
        """Validate the .env text input (may be empty, must be str)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a string (got {text!r})")
        limit = self.max_text_chars
        if len(text) > limit:
            self._invalid(
                f"text exceeds the {limit:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    # ------------------------------------------------------------------ #
    # Preparation: BOM / CRLF detection, physical line splitting
    # ------------------------------------------------------------------ #

    @classmethod
    def _prepare(cls, text: str) -> dict[str, Any]:
        """Split text into normalized physical lines plus byte-level flags.

        The returned record carries ``bom`` (bool), ``crlf_count``,
        ``first_crlf_line`` (int or ``None``), ``lf_count`` (pure-LF
        terminators), ``final_newline`` (bool), ``lines`` (list of
        line strings with BOM stripped and CRLF normalized — the
        trailing empty split artifact removed) and ``line_count``.
        """
        bom = text.startswith("\ufeff")
        raw = text[1:] if bom else text
        crlf_count = raw.count("\r\n")
        lf_count = raw.count("\n") - crlf_count
        first_crlf_line = None
        if crlf_count:
            first_crlf_line = raw.split("\r\n", 1)[0].count("\n") + 1
        normalized = raw.replace("\r\n", "\n")
        lines = normalized.split("\n")
        if lines and lines[-1] == "":
            lines.pop()  # trailing newline is a terminator, not a line
        return {
            "bom": bom,
            "crlf_count": crlf_count,
            "first_crlf_line": first_crlf_line,
            "lf_count": lf_count,
            "final_newline": normalized.endswith("\n"),
            "lines": lines,
            "line_count": len(lines),
        }

    # ------------------------------------------------------------------ #
    # Per-line classification
    # ------------------------------------------------------------------ #

    @classmethod
    def _classify(cls, line: str) -> dict[str, Any]:
        """Classify one physical line into a per-line record."""
        stripped = line.strip()
        record: dict[str, Any] = {
            "raw": line,
            "stripped": stripped,
            "kind": "blank",
            "key": None,
            "exported": False,
            "spaced": None,
            "quote": None,
            "style": None,
            "data": "",
            "has_hash": False,
        }
        if not stripped:
            return record
        if stripped.startswith("#"):
            record["kind"] = "comment"
            return record
        match = _ASSIGN_RE.match(stripped)
        if match is None:
            if _SPACED_KEY_RE.match(stripped) is not None:
                record["kind"] = "spaced_key"
            else:
                record["kind"] = "bare"
            return record
        record["kind"] = "assignment"
        record["key"] = match.group("key")
        record["exported"] = match.group("export") is not None
        equals_at = match.end() - 1  # index of '=' within the stripped line
        before = stripped[equals_at - 1] == " " or stripped[equals_at - 1] == "\t"
        value_raw = stripped[equals_at + 1 :]
        record["value_raw"] = value_raw
        cls._analyze_value(record, value_raw)
        # Space after '=' only counts as spacing when actual (non
        # comment-only) data follows — an empty value whose only tail
        # is an inline comment must not fabricate a spacing style.
        after = bool(value_raw) and (value_raw[0] == " " or value_raw[0] == "\t") and bool(record["data"])
        record["spaced"] = "spaced" if (before or after) else "tight"
        return record

    @classmethod
    def _comment_boundary(cls, value_raw: str) -> int | None:
        """Index of the inline-comment ``#`` in a raw value portion.

        The comment boundary is the first ``#`` directly preceded by
        whitespace (a ``#`` glued directly after ``=`` or into text —
        ``KEY=#fff`` — is data). Scanning happens on the raw portion
        *before* any lstrip so ``KEY= # note`` reads as an empty value
        plus a comment, consistently for parsing, the default-marker
        check and the quoting fix.
        """
        for index in range(1, len(value_raw)):
            if value_raw[index] == "#" and value_raw[index - 1] in " \t":
                return index
        return None

    @classmethod
    def _analyze_value(cls, record: dict[str, Any], value_raw: str) -> None:
        """Fill quote style / parsed data / hash flag for a value portion."""
        probe = value_raw.lstrip(" \t")
        data = ""
        quote = "none"
        if probe.startswith('"'):
            quote = "double"
            data = cls._read_double_quoted(probe)
        elif probe.startswith("'"):
            quote = "single"
            end = probe.find("'", 1)
            data = probe[1:] if end < 0 else probe[1:end]
        else:
            # Unquoted: the value ends at the inline-comment boundary.
            cut = cls._comment_boundary(value_raw)
            data = (value_raw if cut is None else value_raw[:cut]).strip()
        record["quote"] = quote
        record["data"] = data
        record["empty"] = data == ""
        # style: quoted vs unquoted; empty unquoted values carry no
        # style so they never fabricate quote-mixing findings.
        if quote in ("double", "single"):
            record["style"] = "quoted"
        elif data:
            record["style"] = "unquoted"
        else:
            record["style"] = None
        # Any '#' in the raw portion of an unquoted value is a
        # comment-boundary risk (start-of-value, glued or inline).
        record["has_hash"] = quote == "none" and "#" in value_raw

    @classmethod
    def _read_double_quoted(cls, probe: str) -> str:
        """Read a double-quoted value: unescape \\n \\t \\r \\\\ \\".

        An unterminated quote reads to the end of the line (a lint
        result, not a crash).
        """
        chars: list[str] = []
        index = 1
        length = len(probe)
        while index < length:
            char = probe[index]
            if char == "\\":
                if index + 1 >= length:
                    break  # dangling backslash before end of line
                escape = probe[index + 1]
                chars.append(_ESCAPES.get(escape, "\\" + escape))
                index += 2
                continue
            if char == '"':
                break  # content after the quote is ignored
            chars.append(char)
            index += 1
        return "".join(chars)

    # ------------------------------------------------------------------ #
    # Secret masking / previews (family rule)
    # ------------------------------------------------------------------ #

    @classmethod
    def _is_secret(cls, name: str) -> bool:
        """True when the name marks its value as secret-ish."""
        upper = name.upper()
        return any(marker in upper for marker in _SECRET_MARKERS)

    @classmethod
    def _mask_tail(cls, tail: str) -> str:
        """Mask a value portion, preserving quote shape only."""
        stripped = tail.lstrip(" \t")
        if stripped[:1] in ('"', "'"):
            quote_char = stripped[0]
            if quote_char in stripped[1:]:
                return quote_char + _MASK + quote_char
            return quote_char + _MASK
        return _MASK

    @classmethod
    def _mask_line(cls, line: str) -> str:
        """Render a line for a fix snapshot: mask secret values.

        The head (up to and including the first ``=``) is kept so the
        edit shape stays visible; only the value tail is masked for
        secret-ish names. Lines without ``=`` are masked whole when
        they mention a secret marker (a pasted secret can hide in a
        bare line).
        """
        equals_at = line.find("=")
        if equals_at < 0:
            if cls._is_secret(line.upper()):
                return _MASK
            return line
        head, tail = line[: equals_at + 1], line[equals_at + 1 :]
        core = tail.rstrip(" \t")
        trailing = tail[len(core) :]
        key_part = head.split("=", 1)[0]
        if cls._is_secret(key_part):
            return head + cls._mask_tail(core) + trailing
        return line

    @classmethod
    def _preview(cls, line: str) -> str:
        """A <=24-char preview for unparseable-line findings.

        Fail-safe: a line mentioning a secret marker is masked (its
        value tail after ``=`` when there is one, the whole line if
        not — a pasted secret can hide anywhere in a broken line).
        """
        if cls._is_secret(line.upper()):
            equals_at = line.find("=")
            if equals_at < 0:
                return _MASK
            return line[: equals_at + 1] + cls._mask_tail(line[equals_at + 1 :])
        if len(line) > _PREVIEW_CHARS:
            return line[:_PREVIEW_CHARS] + "..."
        return line

    # ------------------------------------------------------------------ #
    # Shared payload helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _context(cls, mode: str, **extra: Any) -> dict[str, Any]:
        """Build the call-context prefix shared by every payload."""
        return {"mode": mode, **extra}

    @classmethod
    def _records_with_numbers(cls, prepared: dict[str, Any]) -> list[dict[str, Any]]:
        """Classified records with their 1-based physical line numbers."""
        records = [cls._classify(line) for line in prepared["lines"]]
        for number, record in enumerate(records, start=1):
            record["number"] = number
        return records

    # ------------------------------------------------------------------ #
    # lint mode
    # ------------------------------------------------------------------ #

    def _run_lint(self, prepared: dict[str, Any]) -> dict[str, Any]:
        """Run all 17 rules over the prepared text."""
        context = self._context("lint", rules=len(RULES))
        findings = self._collect_findings(prepared)
        findings.sort(key=lambda f: (f["line"], f["code"]))
        counts = {"error": 0, "warning": 0, "info": 0}
        for finding in findings:
            counts[finding["severity"]] += 1
        if not findings:
            result = "clean"
        else:
            result = (
                f"{len(findings)} finding(s): {counts['error']} error(s), "
                f"{counts['warning']} warning(s), {counts['info']} info(s)"
            )
        return {
            **context,
            "result": result,
            "clean": not findings,
            "findings": findings,
            "counts": {**counts, "total": len(findings)},
        }

    def _collect_findings(self, prepared: dict[str, Any]) -> list[dict[str, Any]]:
        """Produce the raw findings list (unsorted)."""
        records = self._records_with_numbers(prepared)
        findings: list[dict[str, Any]] = []
        self._byte_level_rules(prepared, findings)
        self._line_level_rules(records, findings)
        self._key_level_rules(records, findings)
        self._consistency_rules(records, findings)
        self._order_rules(records, findings)
        return findings

    # -- byte-level ---------------------------------------------------- #

    @classmethod
    def _byte_level_rules(cls, prepared: dict[str, Any], findings: list[dict[str, Any]]) -> None:
        """BOM, CRLF and final-newline findings."""
        if prepared["bom"]:
            findings.append(
                {
                    "code": "bom_present",
                    "severity": SEVERITIES["bom_present"],
                    "line": 1,
                    "message": (
                        "UTF-8 BOM at the start of the file: many dotenv "
                        "loaders include it in the first key and silently "
                        "break that assignment; strip it"
                    ),
                }
            )
        if prepared["crlf_count"]:
            findings.append(
                {
                    "code": "crlf_line_endings",
                    "severity": SEVERITIES["crlf_line_endings"],
                    "line": prepared["first_crlf_line"],
                    "message": (
                        f"CRLF line endings ({prepared['crlf_count']} of "
                        f"{prepared['line_count']} lines): normalize to LF "
                        "for cross-platform consistency"
                    ),
                }
            )
        if prepared["lines"] and not prepared["final_newline"]:
            findings.append(
                {
                    "code": "missing_final_newline",
                    "severity": SEVERITIES["missing_final_newline"],
                    "line": prepared["line_count"],
                    "message": "file does not end with a newline: POSIX tools " "expect a final newline",
                }
            )

    # -- line-level ----------------------------------------------------- #

    @classmethod
    def _line_level_rules(cls, records: list[dict[str, Any]], findings: list[dict[str, Any]]) -> None:
        """Per-line syntax / value / style findings."""
        for record in records:
            number = record["number"]
            raw = record["raw"]
            if raw != raw.rstrip():
                findings.append(
                    {
                        "code": "trailing_whitespace",
                        "severity": SEVERITIES["trailing_whitespace"],
                        "line": number,
                        "message": "trailing whitespace",
                    }
                )
            if len(raw) > _VERY_LONG_LINE:
                findings.append(
                    {
                        "code": "very_long_line",
                        "severity": SEVERITIES["very_long_line"],
                        "line": number,
                        "message": (
                            f"line is {len(raw):,} characters long "
                            f"(> {_VERY_LONG_LINE:,}); consider moving giant "
                            "blobs out of the .env"
                        ),
                    }
                )
            kind = record["kind"]
            if kind == "bare":
                findings.append(
                    {
                        "code": "line_without_assignment",
                        "severity": SEVERITIES["line_without_assignment"],
                        "line": number,
                        "message": "line is neither blank, comment nor KEY=VALUE " "assignment",
                        "preview": cls._preview(record["stripped"]),
                    }
                )
                continue
            if kind == "spaced_key":
                findings.append(
                    {
                        "code": "key_with_spaces",
                        "severity": SEVERITIES["key_with_spaces"],
                        "line": number,
                        "message": "key contains spaces: dotenv keys cannot " "contain spaces",
                        "preview": cls._preview(record["stripped"]),
                    }
                )
                continue
            if kind == "assignment":
                cls._value_level_rules(record, findings)

    @classmethod
    def _value_level_rules(cls, record: dict[str, Any], findings: list[dict[str, Any]]) -> None:
        """Per-assignment key/value findings for one classified line."""
        number = record["number"]
        key = record["key"]
        if key != key.upper():
            findings.append(
                {
                    "code": "lowercase_key",
                    "severity": SEVERITIES["lowercase_key"],
                    "line": number,
                    "message": f"key '{key}' is not UPPER-case; the dotenv " "convention is UPPER_SNAKE",
                }
            )
        if record["empty"] and record["quote"] == "none" and not cls._has_default_marker(record):
            findings.append(
                {
                    "code": "empty_value_without_default_marker",
                    "severity": SEVERITIES["empty_value_without_default_marker"],
                    "line": number,
                    "message": (
                        f"key '{key}' is set to an empty value "
                        "without a default marker; add a value or "
                        "an inline '# default' / '# optional' comment"
                    ),
                }
            )
        if record["quote"] == "none" and record["data"] and (" " in record["data"] or "\t" in record["data"]):
            findings.append(
                {
                    "code": "value_with_unquoted_spaces",
                    "severity": SEVERITIES["value_with_unquoted_spaces"],
                    "line": number,
                    "message": (
                        f"unquoted value of '{key}' contains whitespace: "
                        "shell sourcing would split it into multiple "
                        "words; quote it"
                    ),
                }
            )
        if record["has_hash"]:
            findings.append(
                {
                    "code": "value_with_unquoted_hash",
                    "severity": SEVERITIES["value_with_unquoted_hash"],
                    "line": number,
                    "message": (
                        f"unquoted value of '{key}' contains '#': "
                        "parsers disagree whether this starts a comment "
                        "or is data; quote it"
                    ),
                }
            )

    @classmethod
    def _has_default_marker(cls, record: dict[str, Any]) -> bool:
        """A same-line inline comment mentioning default/optional."""
        value_raw = record.get("value_raw", "")
        comment_at = cls._comment_boundary(value_raw)
        if comment_at is None:
            return False
        comment = value_raw[comment_at:].lower()
        return "default" in comment or "optional" in comment

    # -- key-level ------------------------------------------------------ #

    @classmethod
    def _key_level_rules(cls, records: list[dict[str, Any]], findings: list[dict[str, Any]]) -> None:
        """Duplicate-key and case-collision findings."""
        seen: dict[str, int] = {}
        case_first: dict[str, tuple[str, int]] = {}
        for record in records:
            if record["kind"] != "assignment":
                continue
            key = record["key"]
            number = record["number"]
            first = seen.get(key)
            if first is not None:
                findings.append(
                    {
                        "code": "duplicate_keys",
                        "severity": SEVERITIES["duplicate_keys"],
                        "line": number,
                        "message": (
                            f"key '{key}' is defined again (first at line "
                            f"{first}); dotenv loaders keep the last value — "
                            "remove the stale entry"
                        ),
                    }
                )
            else:
                seen[key] = number
            upper = key.upper()
            if upper in case_first and case_first[upper][0] != key:
                other, other_line = case_first[upper]
                findings.append(
                    {
                        "code": "inconsistent_key_case",
                        "severity": SEVERITIES["inconsistent_key_case"],
                        "line": number,
                        "message": (
                            f"key '{key}' differs only in case from "
                            f"'{other}' (line {other_line}); "
                            "case-insensitive environments silently shadow "
                            "one of them"
                        ),
                    }
                )
            else:
                case_first.setdefault(upper, (key, number))

    # -- consistency ----------------------------------------------------- #

    @classmethod
    def _dominant(cls, styled: list[tuple[str, dict[str, Any]]]) -> tuple[str | None, list[dict[str, Any]]]:
        """Dominant style + deviating records.

        A dominant style must be used by *strictly* more lines than
        every other style; on a tie at the top the rule stays silent
        (no side is authoritative enough to call the other wrong).
        """
        if not styled:
            return None, []
        counts: dict[str, int] = {}
        for style, _ in styled:
            counts[style] = counts.get(style, 0) + 1
        dominant = None
        for style, count in counts.items():
            if all(count > other for other_style, other in counts.items() if other_style != style):
                dominant = style
                break
        if dominant is None:
            return None, []
        deviants = [record for style, record in styled if style != dominant]
        return dominant, deviants

    @classmethod
    def _consistency_rules(cls, records: list[dict[str, Any]], findings: list[dict[str, Any]]) -> None:
        """spacing / quoting / export consistency across the file."""
        assignments = [record for record in records if record["kind"] == "assignment"]
        spaced = [(record["spaced"], record) for record in assignments]
        dominant, deviants = cls._dominant(spaced)
        if dominant is not None and deviants:
            usage = sum(1 for style, _ in spaced if style == dominant)
            for record in deviants:
                findings.append(
                    {
                        "code": "spacing_around_equals",
                        "severity": SEVERITIES["spacing_around_equals"],
                        "line": record["number"],
                        "message": (
                            f"spacing around '=' inconsistent with the "
                            f"dominant '{dominant}' style "
                            f"({usage} of {len(spaced)} assignments)"
                        ),
                    }
                )
        quoted = [(record["style"], record) for record in assignments if record["style"] is not None]
        dominant, deviants = cls._dominant(quoted)
        if dominant is not None and deviants:
            usage = sum(1 for style, _ in quoted if style == dominant)
            for record in deviants:
                findings.append(
                    {
                        "code": "quote_style_mixing",
                        "severity": SEVERITIES["quote_style_mixing"],
                        "line": record["number"],
                        "message": (
                            f"quoting inconsistent with the dominant "
                            f"'{dominant}' style ({usage} of {len(quoted)} "
                            "valued assignments)"
                        ),
                    }
                )
        exports = [("exported" if record["exported"] else "plain", record) for record in assignments]
        dominant, deviants = cls._dominant(exports)
        if dominant is not None and deviants:
            usage = sum(1 for style, _ in exports if style == dominant)
            for record in deviants:
                findings.append(
                    {
                        "code": "export_prefix_mixing",
                        "severity": SEVERITIES["export_prefix_mixing"],
                        "line": record["number"],
                        "message": (
                            f"export prefix inconsistent with the dominant "
                            f"'{dominant}' style ({usage} of {len(exports)} "
                            "assignments)"
                        ),
                    }
                )

    # -- ordering -------------------------------------------------------- #

    @classmethod
    def _order_rules(cls, records: list[dict[str, Any]], findings: list[dict[str, Any]]) -> None:
        """Alphabetical-block breaks inside consecutive assignment runs."""
        previous: dict[str, Any] | None = None
        for record in records:
            if record["kind"] != "assignment":
                previous = None  # blank/comment separates blocks
                continue
            if previous is not None:
                prev_key = previous["key"]
                key = record["key"]
                if key.upper() < prev_key.upper():
                    findings.append(
                        {
                            "code": "order_grouping_breaks",
                            "severity": SEVERITIES["order_grouping_breaks"],
                            "line": record["number"],
                            "message": (
                                f"key '{key}' breaks the alphabetical order "
                                f"of its block (after '{prev_key}'); reorder "
                                "or start a new block with a blank line or "
                                "comment"
                            ),
                        }
                    )
            previous = record

    @classmethod
    def _run_breaks(cls, records: list[dict[str, Any]]) -> tuple[int, int]:
        """Count runs of consecutive assignments and order breaks."""
        runs = 0
        breaks = 0
        in_run = False
        previous: dict[str, Any] | None = None
        for record in records:
            if record["kind"] != "assignment":
                in_run = False
                previous = None
                continue
            if not in_run:
                runs += 1
                in_run = True
            if previous is not None and record["key"].upper() < previous["key"].upper():
                breaks += 1
            previous = record
        return runs, breaks

    # ------------------------------------------------------------------ #
    # fix_hints mode
    # ------------------------------------------------------------------ #

    def _run_fix(self, prepared: dict[str, Any]) -> dict[str, Any]:
        """Apply the safe textual fixes; re-lint the fixed text."""
        context = self._context("fix_hints")
        before_payload = self._run_lint(prepared)
        before_codes = sorted({f["code"] for f in before_payload["findings"]})

        fixes: list[dict[str, Any]] = []
        lines = list(prepared["lines"])
        if prepared["bom"]:
            first_line = lines[0] if lines else ""
            fixes.append(
                {
                    "line": 1,
                    "fix": "strip_bom",
                    "before": self._mask_line("\ufeff" + first_line),
                    "after": self._mask_line(first_line),
                }
            )
        if prepared["crlf_count"]:
            fixes.append(
                {
                    "line": prepared["first_crlf_line"],
                    "fix": "crlf_to_lf",
                    "before": f"{prepared['crlf_count']} line(s) end with CRLF",
                    "after": "all line endings normalized to LF",
                }
            )
        # Pass 1: strip trailing whitespace.
        for index, line in enumerate(lines):
            stripped = line.rstrip()
            if stripped != line:
                lines[index] = stripped
                fixes.append(
                    {
                        "line": index + 1,
                        "fix": "strip_trailing_whitespace",
                        "before": self._mask_line(line),
                        "after": self._mask_line(stripped),
                    }
                )
        # Pass 2: quote unquoted values containing spaces or '#'.
        for index, line in enumerate(lines):
            fixed_line = self._quote_line(line)
            if fixed_line is not None and fixed_line != line:
                lines[index] = fixed_line
                fixes.append(
                    {
                        "line": index + 1,
                        "fix": "quote_value",
                        "before": self._mask_line(line),
                        "after": self._mask_line(fixed_line),
                    }
                )
        # Pass 3: final newline.
        if lines and not prepared["final_newline"]:
            fixes.append(
                {
                    "line": len(lines),
                    "fix": "add_final_newline",
                    "before": "<missing final newline>",
                    "after": "<final newline added>",
                }
            )
        fixed_text = "\n".join(lines) + "\n" if lines else ""

        after_payload = self._run_lint(self._prepare(fixed_text))
        after_codes = sorted({f["code"] for f in after_payload["findings"]})
        resolved = [code for code in before_codes if code not in after_codes]

        fixes_by_type: dict[str, int] = {}
        for entry in fixes:
            fixes_by_type[entry["fix"]] = fixes_by_type.get(entry["fix"], 0) + 1
        changed_lines = len({entry["line"] for entry in fixes})
        if fixes:
            result = (
                f"{len(fixes)} fix(es) across {changed_lines} line(s); "
                f"re-lint: {after_payload['counts']['total']} finding(s) "
                "remain"
            )
        else:
            result = f"no safe fixes needed; re-lint: " f"{after_payload['counts']['total']} finding(s) remain"
        return {
            **context,
            "result": result,
            "fixes": fixes,
            "fixes_by_type": fixes_by_type,
            "fixed_text": self._mask_fixed_text(fixed_text),
            "resolved_codes": resolved,
            "remaining_findings": after_payload["findings"],
            "remaining_codes": after_codes,
            "remaining_counts": after_payload["counts"],
        }

    @classmethod
    def _quote_line(cls, line: str) -> str | None:
        """Quote an unquoted value containing spaces or '#'.

        Returns the rebuilt line, or ``None`` when nothing to do.
        Double quotes are used; backslashes and embedded double
        quotes are escaped so the *parsed* value is unchanged. A
        whitespace-preceded inline comment stays outside the quotes.
        """
        stripped = line.strip()
        match = _ASSIGN_RE.match(stripped)
        if match is None:
            return None
        equals_at = match.end() - 1
        value_raw = stripped[equals_at + 1 :]
        probe = value_raw.lstrip(" \t")
        if probe.startswith('"') or probe.startswith("'"):
            return None  # already quoted
        # Split off the inline comment (same boundary rule as parsing).
        comment_at = cls._comment_boundary(value_raw)
        data = value_raw if comment_at is None else value_raw[:comment_at]
        data = data.strip()
        if not data or not (" " in data or "\t" in data or "#" in data):
            return None
        quoted = '"' + data.replace("\\", "\\\\").replace('"', '\\"') + '"'
        leading = value_raw[: len(value_raw) - len(value_raw.lstrip(" \t"))]
        head = line[: line.find("=") + 1]
        tail = leading + quoted
        if comment_at is not None:
            tail += " " + value_raw[comment_at:]
        return head + tail

    @classmethod
    def _mask_fixed_text(cls, fixed_text: str) -> str:
        """Mask secret values line-by-line so the text can be echoed."""
        masked_lines = []
        for line in fixed_text.split("\n"):
            masked_lines.append(cls._mask_line(line))
        return "\n".join(masked_lines)

    # ------------------------------------------------------------------ #
    # stats mode
    # ------------------------------------------------------------------ #

    def _run_stats(self, prepared: dict[str, Any]) -> dict[str, Any]:
        """Summarize counts, quoting ratio and grouping."""
        context = self._context("stats")
        records = self._records_with_numbers(prepared)
        assignments = [record for record in records if record["kind"] == "assignment"]
        quoted = sum(1 for r in assignments if r["style"] == "quoted")
        unquoted = sum(1 for r in assignments if r["style"] == "unquoted")
        empty = sum(1 for r in assignments if r["empty"])
        denominator = quoted + unquoted
        ratio = round(quoted / denominator, 2) if denominator else None
        exported_vars = {record["key"] for record in assignments if record["exported"]}
        distinct_vars = {record["key"] for record in assignments}
        runs, breaks = self._run_breaks(records)
        assignment_lines = len(assignments)
        if assignment_lines == 0:
            assessment = "no assignments"
        elif breaks == 0:
            assessment = "alphabetical"
        elif breaks * 4 <= assignment_lines:
            assessment = "mostly_alphabetical"
        else:
            assessment = "unsorted"
        if prepared["crlf_count"] and prepared["lf_count"] == 0:
            line_ending = "crlf"
        elif prepared["crlf_count"] == 0 and prepared["lf_count"] > 0:
            line_ending = "lf"
        elif prepared["crlf_count"] == 0:
            line_ending = "none"
        else:
            line_ending = "mixed"
        pct = f"{round(ratio * 100)}%" if ratio is not None else "n/a"
        return {
            **context,
            "result": f"{len(distinct_vars)} variable(s), {pct} quoted, " f"grouping: {assessment}",
            "total_lines": prepared["line_count"],
            "blank_lines": sum(1 for r in records if r["kind"] == "blank"),
            "comment_lines": sum(1 for r in records if r["kind"] == "comment"),
            "assignment_lines": assignment_lines,
            "vars": len(distinct_vars),
            "exported_vars": len(exported_vars),
            "quoted": quoted,
            "unquoted": unquoted,
            "empty_values": empty,
            "quoted_ratio": ratio,
            "grouping": {
                "runs": runs,
                "order_breaks": breaks,
                "assessment": assessment,
            },
            "encoding": {
                "bom": prepared["bom"],
                "line_ending": line_ending,
                "final_newline": prepared["final_newline"],
            },
        }
