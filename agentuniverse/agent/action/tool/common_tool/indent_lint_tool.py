#!/usr/bin/env python3
"""Python source indentation auditing: syntax, consistency, statistics,
conversion, and per-line explanation.

The tool accepts Python source text and offers four deterministic,
stdlib-only modes (``compile``/``ast``/``tokenize`` are the only engines):

- ``lint``    -- findings ``[{line, col, code, message, severity}]``
- ``stats``   -- indentation statistics and per-function nesting
- ``convert`` -- tab/space conversion verified to preserve semantics
- ``explain`` -- the indentation stack around one focus line

Policies (documented, deterministic):

Syntax level. The authoritative oracle is ``compile()`` itself. Every
``IndentationError``/``TabError`` the interpreter raises is mirrored as one
error finding whose ``line``, ``col`` and ``message`` come verbatim from the
exception (``col`` mirrors ``SyntaxError.offset``, which for indentation
errors points at the interpreter's own offending position and is not
uniformly 0- or 1-based across error classes). Error classes and their
messages:

- ``E_EXPECTED_INDENT``       -- "expected an indented block after ... on
  line N". The interpreter reports the line AFTER the block opener and embeds
  the opener's line number inside the message text.
- ``E_UNEXPECTED_INDENT``     -- "unexpected indent" (a code line deeper than
  any open block without a block opener).
- ``E_UNINDENT_MISMATCH``     -- "unindent does not match any outer
  indentation level" (dedent to a column that is no live level).
- ``E_TAB_INCONSISTENT``      -- TabError "inconsistent use of tabs and
  spaces in indentation" (the interpreter compares tab/space indents at
  hard-coded 8-column tab stops; a space-indented level and a tab landing on
  the same 8-stop column collide).
- ``E_INDENT_OTHER``          -- any other ``IndentationError``.

A non-indentation ``SyntaxError`` (for example an encoding artifact) cannot
be audited here; it is reported once as ``W_OTHER_SYNTAX`` so a "no error
findings" verdict always implies the source compiled. Consistency findings
carry the line's interpreter indent column as ``col``.

Consistency level (warnings/info; these never claim the file is broken):

- CPython's tokenizer hard-codes tab stops at 8 columns. The tool's
  *visual* model uses the caller's ``tab_width`` (default 4, PEP 8) to
  reason about what a human sees; ``W_DEDENT_LEVEL`` fires when a dedent
  lands on a column that is a live level for the interpreter (so it
  compiled) but not a level of the visual stack -- possible only when tabs
  and spaces disagree about columns.
- Per line: mixed tab+space indent (``W_TAB_SPACE_MIX``), a tab-only line in
  a space-majority file (``W_TAB_IN_SPACE_FILE``), a space-only line in a
  tab-majority file (``W_SPACE_IN_TAB_FILE``), and a space indent that is
  not a multiple of the inferred step (``W_INDENT_WIDTH`` -- the classic
  3-space copy-paste into a 4-space file).
- Continuation lines (inside brackets or after a backslash) have FREE
  indentation: ``compile()`` accepts arbitrary leading whitespace there, so
  the tool never reports errors for them, only ``I_CONTINUATION_TAB`` /
  ``I_CONTINUATION_MIXED`` style notes.
- Comment-only lines also have free indentation (verified against the
  tokenizer); they are never flagged for width.
- Empty lines containing whitespace (``W_BLANK_WHITESPACE``) and trailing
  whitespace after code (``W_TRAILING_WHITESPACE``) are reported except
  inside multi-line string literals, where whitespace is content.
- A form feed at the start of a line is LEGAL Python (``W_FORM_FEED`` info);
  the tokenizer resets its column counter at it. A form feed in the middle
  of an indentation prefix inside a block makes the line effectively
  unindented and is caught by the compile mirror instead.
- CRLF line endings (``W_CRLF`` info), mixed line endings
  (``W_MIXED_NEWLINE`` warning) and a leading BOM (``W_BOM`` warning -- the
  interpreter rejects raw ``\\ufeff`` with "invalid non-printable character";
  the tool strips it before analysis) are reported once per file.

Conversion (``convert``). Only leading indentation OUTSIDE multi-line string
literals is rewritten (string content is never touched). Tab-to-space
expands each tab to the next multiple of ``tab_width`` measured from the
start of the line; space-to-tab rewrites only pure-space indents that are
exact multiples of ``tab_width`` (non-multiple lines are left unchanged and
counted in ``notes``). Because the interpreter compares columns at 8-column
tab stops while the conversion uses ``tab_width``, a rewrite that is
locally plausible can still change block structure, so the result is ALWAYS
verified: the tool compiles before and after and compares ``ast.dump`` of
both trees. If the verification fails -- or the source does not compile at
all -- the ORIGINAL text is returned with ``changed_lines: 0`` and the
refusal explained in ``notes``. A successful conversion therefore provably
preserves semantics.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import ast
import io
import re
import tokenize
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

_LINE_SPLIT_RE = re.compile(r"\r\n|\r|\n")
_LEADING_WS_RE = re.compile(r"[ \t\f\v]*")

_MODES: ClassVar[tuple[str, ...]] = ("lint", "stats", "convert", "explain")
_TARGETS: ClassVar[tuple[str, ...]] = ("spaces", "tabs")

# CPython's tokenizer compares indentation at hard-coded 8-column tab stops.
INTERPRETER_TAB_STOPS = 8

# Multiline string token types; FSTRING_* exist only on Python 3.12+.
_FSTRING_TYPES: ClassVar[tuple[int, ...]] = tuple(
    getattr(tokenize, name)
    for name in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END")
    if hasattr(tokenize, name)
)
_STRING_TYPES: ClassVar[tuple[int, ...]] = (tokenize.STRING,) + _FSTRING_TYPES
_SKIP_TOKENS: ClassVar[tuple[int, ...]] = (
    tokenize.NEWLINE,
    tokenize.NL,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.COMMENT,
    tokenize.ENCODING,
    tokenize.ENDMARKER,
)

_INDENT_ERROR_CODES: ClassVar[tuple[tuple[str, str], ...]] = (
    ("inconsistent use of tabs and spaces", "E_TAB_INCONSISTENT"),
    ("expected an indented block", "E_EXPECTED_INDENT"),
    ("unexpected indent", "E_UNEXPECTED_INDENT"),
    ("unindent does not match any outer indentation level", "E_UNINDENT_MISMATCH"),
)


def _expand_columns(prefix: str, tab_width: int) -> int:
    """Column reached after ``prefix`` when tabs advance to multiples of
    ``tab_width``. Form feeds and vertical tabs reset/advance by one."""
    column = 0
    for char in prefix:
        if char == "\t":
            column = (column // tab_width + 1) * tab_width
        elif char == "\f":
            column = 0
        else:
            column += 1
    return column


class LineFacts:
    """Per-physical-line indentation facts."""

    __slots__ = (
        "number",
        "text",
        "terminator",
        "lead",
        "has_tab",
        "has_space",
        "has_formfeed",
        "classification",
    )

    def __init__(self, number: int, text: str, terminator: str) -> None:
        self.number = number
        self.text = text
        self.terminator = terminator
        self.lead = _LEADING_WS_RE.match(text).group(0)
        self.has_tab = "\t" in self.lead
        self.has_space = " " in self.lead
        self.has_formfeed = ("\f" in self.lead) or ("\v" in self.lead)
        if not text:
            self.classification = "empty"
        elif text.strip(" \t\f\v") == "" and text != "":
            self.classification = "blank"
        elif not self.lead:
            self.classification = "none"
        elif self.has_tab and self.has_space:
            self.classification = "mixed"
        elif self.has_tab:
            self.classification = "tabs"
        else:
            self.classification = "spaces"

    def body(self) -> str:
        """Line content after the leading whitespace prefix."""
        return self.text[len(self.lead) :]

    def interp_column(self) -> int:
        """Interpreter-visible indent column (hard-coded 8-column stops)."""
        return _expand_columns(self.lead, INTERPRETER_TAB_STOPS)

    def visual_column(self, tab_width: int) -> int:
        """Human-visual indent column under ``tab_width`` stops."""
        return _expand_columns(self.lead, tab_width)


class FileAnalysis:
    """Shared per-source analysis: lines, tokens, compile verdict, style."""

    __slots__ = (
        "lines",
        "findings",
        "truncated",
        "newline_style",
        "final_newline",
        "bom",
        "text",
        "compile_error",
        "tokenized",
        "string_rows",
        "logical_rows",
        "continuation_rows",
        "blank_rows",
        "depth_by_row",
        "indent_stack_by_row",
        "max_depth",
        "style_counts",
        "inferred_style",
        "inferred_step",
        "tab_width",
    )

    def __init__(self, tab_width: int) -> None:
        self.tab_width = tab_width
        self.lines: list[LineFacts] = []
        self.findings: list[dict[str, Any]] = []
        self.truncated = False
        self.newline_style = "lf"
        self.final_newline = True
        self.bom = False
        self.text = ""
        self.compile_error: BaseException | None = None
        self.tokenized = False
        self.string_rows: set[int] = set()
        self.logical_rows: set[int] = set()
        self.continuation_rows: set[int] = set()
        self.blank_rows: set[int] = set()
        self.depth_by_row: dict[int, int] = {}
        self.indent_stack_by_row: dict[int, list[int]] = {}
        self.max_depth = 0
        self.style_counts = {"tabs": 0, "spaces": 0, "mixed": 0}
        self.inferred_style: str | None = None
        self.inferred_step: int | None = None


class IndentLintTool(Tool):
    """Audit, measure, convert, and explain Python source indentation."""

    max_input_bytes: int = 2 * 1024 * 1024
    max_lines: int = 200_000
    max_line_bytes: int = 1_048_576
    warn_line_bytes: int = 65_536
    max_findings: int = 200
    max_functions: int = 5_000

    def execute(
        self,
        mode: str,
        source: str,
        line: int | None = None,
        target: str | None = None,
        tab_width: int | None = None,
    ) -> dict[str, Any]:
        try:
            operation = self._mode(mode)
            width = self._tab_width(tab_width)
            analysis = self._analyze(source, width)
            if operation == "lint":
                return self._lint_result(analysis)
            if operation == "stats":
                return self._stats_result(analysis)
            if operation == "convert":
                return self._convert_result(analysis, target, width)
            return self._explain_result(analysis, line)
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except RecursionError:  # pragma: no cover - defensive
            return self._error("validation_error", "source is too deeply nested")
        except Exception as exc:  # pragma: no cover - defensive
            return self._error("operation_error", f"Indentation analysis failed: {exc}")

    # ------------------------------------------------------------- input checks

    @staticmethod
    def _error(kind: str, message: str, **extra: Any) -> dict[str, Any]:
        result: dict[str, Any] = {"status": "error", "error_type": kind, "error": message}
        result.update(extra)
        return result

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in _MODES:
            raise ValueError("mode must be lint, stats, convert, or explain")
        return mode

    def _source_text(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("source must be a string")
        if value == "":
            raise ValueError("source must be a non-empty string")
        if self._byte_size(value) > self.max_input_bytes:
            raise ValueError(f"source exceeds max_input_bytes ({self.max_input_bytes})")
        return value

    @staticmethod
    def _tab_width(value: Any) -> int:
        if value is None:
            return 4
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("tab_width must be an integer when provided")
        if not 1 <= value <= 16:
            raise ValueError("tab_width must be between 1 and 16")
        return value

    def _target(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("target must be a string")
        target = value.strip().lower()
        if target not in _TARGETS:
            raise ValueError("target must be spaces or tabs")
        return target

    def _focus_line(self, value: Any, total: int) -> int:
        if value is None:
            raise TypeError("line is required for explain mode")
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("line must be an integer")
        if not 1 <= value <= total:
            raise ValueError(f"line must be between 1 and {total}")
        return value

    @staticmethod
    def _byte_size(value: str) -> int:
        return len(value.encode("utf-8", "replace"))

    # ---------------------------------------------------------------- analysis

    def _add_finding(
        self,
        analysis: FileAnalysis,
        line_no: int,
        code: str,
        message: str,
        severity: str = "warning",
        col: int = 0,
    ) -> None:
        if len(analysis.findings) >= self.max_findings:
            analysis.truncated = True
            return
        analysis.findings.append(
            {"line": line_no, "col": col, "code": code, "message": message, "severity": severity}
        )

    def _split_lines(self, text: str) -> list[tuple[str, str]]:
        """Split on universal newlines (\\r\\n, \\r, \\n); the last element
        carries an empty terminator when the text lacks a final newline."""
        pieces: list[tuple[str, str]] = []
        position = 0
        for match in _LINE_SPLIT_RE.finditer(text):
            pieces.append((text[position : match.start()], match.group(0)))
            position = match.end()
        pieces.append((text[position:], ""))
        return pieces

    def _analyze(self, value: Any, tab_width: int) -> FileAnalysis:
        text = self._source_text(value)
        analysis = FileAnalysis(tab_width)
        if text.startswith("\ufeff"):
            analysis.bom = True
            text = text[1:]
        analysis.text = text
        pieces = self._split_lines(text)
        if pieces and pieces[-1] == ("", ""):
            pieces.pop()
        if len(pieces) > self.max_lines:
            raise ValueError(f"source exceeds max_lines ({self.max_lines})")
        terminators = {term for _, term in pieces if term}
        analysis.final_newline = text.endswith(("\n", "\r"))
        if not terminators:
            analysis.newline_style = "lf"
        elif terminators <= {"\r\n"}:
            analysis.newline_style = "crlf"
        elif terminators <= {"\r"}:
            analysis.newline_style = "cr"
        elif terminators <= {"\n"}:
            analysis.newline_style = "lf"
        else:
            analysis.newline_style = "mixed"
        for index, (body, term) in enumerate(pieces, start=1):
            size = self._byte_size(body)
            if size > self.max_line_bytes:
                raise ValueError(f"line {index} exceeds max_line_bytes ({self.max_line_bytes})")
            if size > self.warn_line_bytes:
                self._add_finding(
                    analysis,
                    index,
                    "W_LONG_LINE",
                    f"line is {size} bytes; indentation reporting may be unwieldy",
                    "info",
                )
            analysis.lines.append(LineFacts(index, body, term))
        self._tokenize_walk(analysis)
        self._compile_mirror(analysis)
        self._infer_style(analysis)
        self._consistency_findings(analysis)
        analysis.findings.sort(key=lambda item: (item["line"], item["code"], item["message"]))
        return analysis

    def _tokenize_walk(self, analysis: FileAnalysis) -> None:
        """Tokenize to find logical-line starts, string content rows, and the
        interpreter's indent stack per row. Failure degrades to a raw
        fallback (all non-blank rows treated as indent-significant)."""
        text = analysis.text
        if analysis.newline_style not in ("lf", "crlf"):
            # tokenize counts rows on \\n only; bare-CR transport mismatches.
            self._fallback_rows(analysis)
            return
        try:
            tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
        except (tokenize.TokenError, IndentationError, SyntaxError, ValueError, RecursionError):
            self._fallback_rows(analysis)
            return
        analysis.tokenized = True
        for token in tokens:
            if token.type in _STRING_TYPES:
                start, end = token.start[0], token.end[0]
                if end > start:
                    analysis.string_rows.update(range(start + 1, end + 1))
        in_logical = False
        bracket_depth = 0
        stack: list[int] = [0]
        pending_dedents = 0
        comment_rows: set[int] = set()
        for token in tokens:
            kind = token.type
            if kind == tokenize.NEWLINE:
                in_logical = False
                pending_dedents = 0
                continue
            if kind == tokenize.NL:
                if bracket_depth == 0:
                    in_logical = False
                continue
            if kind == tokenize.INDENT:
                stack.append(_expand_columns(token.string, INTERPRETER_TAB_STOPS))
                continue
            if kind == tokenize.DEDENT:
                pending_dedents += 1
                continue
            if kind == tokenize.COMMENT:
                comment_rows.add(token.start[0])
                continue
            if kind in _SKIP_TOKENS:
                continue
            if token.string in ("(", "[", "{"):
                bracket_depth += 1
            elif token.string in (")", "]", "}"):
                bracket_depth = max(0, bracket_depth - 1)
            if not in_logical:
                row = token.start[0]
                for _ in range(pending_dedents):
                    if len(stack) > 1:
                        stack.pop()
                pending_dedents = 0
                analysis.logical_rows.add(row)
                depth = len(stack) - 1
                analysis.depth_by_row[row] = depth
                analysis.indent_stack_by_row[row] = list(stack)
                if depth > analysis.max_depth:
                    analysis.max_depth = depth
                in_logical = True
        blank = {"empty", "blank"}
        for facts in analysis.lines:
            if facts.classification in blank:
                analysis.blank_rows.add(facts.number)
        # Comment-only rows have free indentation too; never reported.
        free_rows = comment_rows | analysis.string_rows
        analysis.continuation_rows = {
            facts.number
            for facts in analysis.lines
            if facts.number not in analysis.logical_rows
            and facts.number not in analysis.blank_rows
            and facts.number not in free_rows
            and facts.classification not in blank
        }

    def _fallback_rows(self, analysis: FileAnalysis) -> None:
        """Without tokens every non-blank row is treated as indent-significant
        and no string masking is available (documented approximation)."""
        blank = {"empty", "blank"}
        visual_stack: list[int] = [0]
        for facts in analysis.lines:
            if facts.classification in blank:
                analysis.blank_rows.add(facts.number)
                continue
            analysis.logical_rows.add(facts.number)
            column = facts.interp_column()
            while len(visual_stack) > 1 and visual_stack[-1] > column:
                visual_stack.pop()
            if column > visual_stack[-1]:
                visual_stack.append(column)
            depth = len(visual_stack) - 1
            analysis.depth_by_row[facts.number] = depth
            analysis.indent_stack_by_row[facts.number] = list(visual_stack)
            if depth > analysis.max_depth:
                analysis.max_depth = depth

    def _compile_mirror(self, analysis: FileAnalysis) -> None:
        """Attempt compile() and mirror IndentationError family findings."""
        try:
            compile(analysis.text, "<indent-lint>", "exec")
            return
        except SyntaxError as exc:
            analysis.compile_error = exc
        exc = analysis.compile_error
        if isinstance(exc, (IndentationError, TabError)):
            code = "E_INDENT_OTHER"
            for prefix, mapped in _INDENT_ERROR_CODES:
                if str(exc.msg).startswith(prefix):
                    code = mapped
                    break
            self._add_finding(
                analysis,
                exc.lineno or 1,
                code,
                str(exc.msg),
                "error",
                col=exc.offset,
            )
            return
        self._add_finding(
            analysis,
            exc.lineno or 1,
            "W_OTHER_SYNTAX",
            f"compile failed with a non-indentation error (line {exc.lineno}): {exc.msg}",
            "warning",
        )

    def _logical_indent_lines(self, analysis: FileAnalysis) -> list[LineFacts]:
        """Indent-significant, non-blank, non-string-content lines."""
        return [
            facts
            for facts in analysis.lines
            if facts.number in analysis.logical_rows
            and facts.number not in analysis.string_rows
            and facts.classification not in ("empty", "blank")
        ]

    def _infer_style(self, analysis: FileAnalysis) -> None:
        indented = [
            facts
            for facts in self._logical_indent_lines(analysis)
            if facts.classification in ("tabs", "spaces", "mixed")
        ]
        for facts in indented:
            analysis.style_counts[facts.classification] += 1
        if indented:
            counts = analysis.style_counts
            if counts["mixed"] > counts["tabs"] and counts["mixed"] > counts["spaces"]:
                analysis.inferred_style = "mixed"
            elif counts["spaces"] >= counts["tabs"]:
                # Spaces also win ties: PEP 8 is the default reading.
                analysis.inferred_style = "spaces"
            else:
                analysis.inferred_style = "tabs"
        deltas: list[int] = []
        stack: list[int] = [0]
        for facts in self._logical_indent_lines(analysis):
            column = facts.interp_column()
            if column > stack[-1]:
                deltas.append(column - stack[-1])
                stack.append(column)
            else:
                while len(stack) > 1 and stack[-1] > column:
                    stack.pop()
        if deltas:
            ranking: dict[int, int] = {}
            for delta in deltas:
                ranking[delta] = ranking.get(delta, 0) + 1
            top = max(ranking.values())
            analysis.inferred_step = min(delta for delta, count in ranking.items() if count == top)

    def _consistency_findings(self, analysis: FileAnalysis) -> None:
        if analysis.bom:
            self._add_finding(
                analysis,
                1,
                "W_BOM",
                "UTF-8 BOM stripped before analysis; the interpreter rejects the raw text",
                "warning",
            )
        if analysis.newline_style == "crlf":
            self._add_finding(
                analysis, 1, "W_CRLF", "file uses CRLF line endings; PEP 8 prefers LF", "info"
            )
        elif analysis.newline_style == "cr":
            self._add_finding(
                analysis, 1, "W_CR_ONLY", "file uses bare CR line endings", "info"
            )
        elif analysis.newline_style == "mixed":
            self._add_finding(
                analysis,
                1,
                "W_MIXED_NEWLINE",
                "file mixes LF and CRLF line endings",
                "warning",
            )
        logical = self._logical_indent_lines(analysis)
        style = analysis.inferred_style
        step = analysis.inferred_step if analysis.inferred_style == "spaces" else None
        if style == "spaces" and step is not None and step != 4:
            self._add_finding(
                analysis,
                1,
                "I_PEP8_STEP",
                f"inferred indent step is {step} spaces; PEP 8 recommends 4",
                "info",
            )
        compile_failed = isinstance(analysis.compile_error, (IndentationError, TabError))
        rejected_line = analysis.compile_error.lineno if compile_failed else None
        visual_stack: list[int] = [0]
        for facts in logical:
            if facts.number == rejected_line:
                continue
            interp_col = facts.interp_column()
            if facts.has_formfeed:
                self._add_finding(
                    analysis,
                    facts.number,
                    "W_FORM_FEED",
                    "form feed in leading whitespace is legal; the tokenizer resets its column",
                    "info",
                    col=interp_col,
                )
            if facts.has_tab and facts.has_space:
                self._add_finding(
                    analysis,
                    facts.number,
                    "W_TAB_SPACE_MIX",
                    "line indents with both tabs and spaces",
                    "warning",
                    col=interp_col,
                )
            elif style == "spaces" and facts.has_tab:
                self._add_finding(
                    analysis,
                    facts.number,
                    "W_TAB_IN_SPACE_FILE",
                    "tab-indented line in a space-majority file",
                    "warning",
                    col=interp_col,
                )
            elif style == "tabs" and facts.has_space and not facts.has_tab:
                self._add_finding(
                    analysis,
                    facts.number,
                    "W_SPACE_IN_TAB_FILE",
                    "space-indented line in a tab-majority file",
                    "warning",
                    col=interp_col,
                )
            if step is not None and step >= 2 and facts.classification == "spaces":
                column = facts.interp_column()
                if column % step:
                    self._add_finding(
                        analysis,
                        facts.number,
                        "W_INDENT_WIDTH",
                        f"indent is {column} columns, not a multiple of the inferred step {step}",
                        "warning",
                        col=interp_col,
                    )
            if not compile_failed:
                column = facts.visual_column(analysis.tab_width)
                previous_top = visual_stack[-1]
                while len(visual_stack) > 1 and visual_stack[-1] > column:
                    visual_stack.pop()
                if column not in visual_stack:
                    if column > previous_top:
                        visual_stack.append(column)
                    else:
                        self._add_finding(
                            analysis,
                            facts.number,
                            "W_DEDENT_LEVEL",
                            (
                                f"dedent to visual column {column} matches no level of the "
                                f"visual stack {visual_stack}; the interpreter accepted it "
                                f"because its tab stops are {INTERPRETER_TAB_STOPS} columns"
                            ),
                            "warning",
                            col=interp_col,
                        )
                        visual_stack.append(column)
        for number in sorted(analysis.continuation_rows):
            facts = analysis.lines[number - 1]
            if facts.has_tab and facts.has_space:
                self._add_finding(
                    analysis,
                    number,
                    "I_CONTINUATION_MIXED",
                    "continuation line mixes tabs and spaces (indent is free here)",
                    "info",
                    col=facts.interp_column(),
                )
            elif facts.has_tab and analysis.inferred_style == "spaces":
                self._add_finding(
                    analysis,
                    number,
                    "I_CONTINUATION_TAB",
                    "tab in continuation-line indent (free per the interpreter; style only)",
                    "info",
                    col=facts.interp_column(),
                )
        for facts in analysis.lines:
            if facts.number in analysis.string_rows:
                continue
            if facts.classification == "blank":
                self._add_finding(
                    analysis,
                    facts.number,
                    "W_BLANK_WHITESPACE",
                    "blank line contains whitespace",
                    "warning",
                )
            elif facts.classification != "empty" and facts.text != facts.text.rstrip():
                self._add_finding(
                    analysis,
                    facts.number,
                    "W_TRAILING_WHITESPACE",
                    "trailing whitespace after code",
                    "warning",
                )

    # ------------------------------------------------------------------ modes

    def _lint_result(self, analysis: FileAnalysis) -> dict[str, Any]:
        counts = {"error": 0, "warning": 0, "info": 0}
        for finding in analysis.findings:
            counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1
        if isinstance(analysis.compile_error, (IndentationError, TabError)):
            compile_state = "indent_error"
        elif analysis.compile_error is not None:
            compile_state = "other_syntax_error"
        else:
            compile_state = "ok"
        return {
            "status": "success",
            "mode": "lint",
            "findings": analysis.findings,
            "findings_truncated": analysis.truncated,
            "counts": counts,
            "compile": compile_state,
            "inferred_style": analysis.inferred_style,
            "inferred_step": analysis.inferred_step,
            "total_lines": len(analysis.lines),
            "newline_style": analysis.newline_style,
            "bom": analysis.bom,
            "tokenized": analysis.tokenized,
        }

    def _stats_result(self, analysis: FileAnalysis) -> dict[str, Any]:
        tab_lines = space_lines = mixed_lines = indented_lines = blank_lines = 0
        for facts in analysis.lines:
            if facts.number in analysis.string_rows:
                continue
            if facts.classification in ("empty", "blank"):
                blank_lines += 1
                continue
            if facts.classification == "tabs":
                tab_lines += 1
                indented_lines += 1
            elif facts.classification == "spaces":
                space_lines += 1
                indented_lines += 1
            elif facts.classification == "mixed":
                mixed_lines += 1
                indented_lines += 1
        histogram: dict[int, int] = {}
        for depth in analysis.depth_by_row.values():
            histogram[depth] = histogram.get(depth, 0) + 1
        depth_histogram = {str(key): histogram[key] for key in sorted(histogram)}
        return {
            "status": "success",
            "mode": "stats",
            "total_lines": len(analysis.lines),
            "blank_lines": blank_lines,
            "indented_lines": indented_lines,
            "tab_lines": tab_lines,
            "space_lines": space_lines,
            "mixed_lines": mixed_lines,
            "inferred_step": analysis.inferred_step,
            "inferred_style": analysis.inferred_style,
            "continuation_lines": len(analysis.continuation_rows),
            "string_content_lines": len(analysis.string_rows),
            "max_depth": analysis.max_depth,
            "depth_histogram": depth_histogram,
            "per_function": self._per_function(analysis),
            "newline_style": analysis.newline_style,
            "final_newline": analysis.final_newline,
            "bom": analysis.bom,
            "tokenized": analysis.tokenized,
            "tab_width": analysis.tab_width,
        }

    def _per_function(self, analysis: FileAnalysis) -> list[dict[str, Any]]:
        if isinstance(analysis.compile_error, SyntaxError) or not analysis.tokenized:
            return []
        try:
            tree = ast.parse(analysis.text)
        except SyntaxError:
            return []
        functions: list[dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                base = analysis.depth_by_row.get(node.lineno, 0)
                deepest = base
                for row in range(node.lineno, min(node.end_lineno or node.lineno, len(analysis.lines)) + 1):
                    depth = analysis.depth_by_row.get(row)
                    if depth is not None and depth > deepest:
                        deepest = depth
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "max_nesting": deepest - base,
                    }
                )
                if len(functions) >= self.max_functions:
                    break
        functions.sort(key=lambda item: (item["line"], item["name"]))
        return functions

    def _convert_result(self, analysis: FileAnalysis, target_value: Any, tab_width: int) -> dict[str, Any]:
        target = self._target(target_value)
        notes: list[str] = []
        if isinstance(analysis.compile_error, SyntaxError):
            notes.append(
                "refused: the source does not compile, so semantics cannot be verified; "
                "the original text is returned unchanged"
            )
            return self._converted(analysis.text, analysis, 0, notes, refused=True)
        converted_lines: list[str] = []
        changed = 0
        skipped_strings = 0
        skipped_non_multiple = 0
        for facts in analysis.lines:
            line_text = facts.text
            if facts.number in analysis.string_rows:
                skipped_strings += 1
            elif target == "spaces":
                if facts.has_tab:
                    column = 0
                    rebuilt: list[str] = []
                    for char in facts.lead:
                        if char == "\t":
                            nxt = (column // tab_width + 1) * tab_width
                            rebuilt.append(" " * (nxt - column))
                            column = nxt
                        else:
                            rebuilt.append(char)
                            column += 1
                    line_text = "".join(rebuilt) + facts.body()
            else:
                if facts.classification == "spaces":
                    column = facts.interp_column()
                    if column % tab_width:
                        skipped_non_multiple += 1
                    else:
                        line_text = "\t" * (column // tab_width) + facts.body()
            if line_text != facts.text:
                changed += 1
            converted_lines.append(line_text + facts.terminator)
        converted = "".join(converted_lines)
        if target == "spaces":
            notes.append(
                f"each tab expanded to the next multiple of tab_width={tab_width} measured "
                "from the line start"
            )
        else:
            notes.append(
                f"pure-space indents that are exact multiples of tab_width={tab_width} became "
                "tabs; non-multiple indents were left unchanged"
            )
        if skipped_strings:
            notes.append(f"{skipped_strings} lines inside multi-line strings were never touched")
        if skipped_non_multiple:
            notes.append(f"{skipped_non_multiple} space-indented lines were not multiples of {tab_width}")
        try:
            before_tree = ast.parse(analysis.text)
            after_tree = ast.parse(converted)
        except SyntaxError:
            notes.append(
                "refused: the converted text does not parse; the original text is returned unchanged"
            )
            return self._converted(analysis.text, analysis, 0, notes, refused=True)
        if ast.dump(before_tree) != ast.dump(after_tree):
            notes.append(
                "refused: ast.dump differs between original and converted text (ambiguous "
                "tab/space columns), so the original text is returned unchanged"
            )
            return self._converted(analysis.text, analysis, 0, notes, refused=True)
        notes.append("verified: ast.dump of the converted tree equals the original tree")
        return self._converted(converted, analysis, changed, notes, refused=False)

    @staticmethod
    def _converted(text: str, analysis: FileAnalysis, changed: int, notes: list[str], refused: bool) -> dict[str, Any]:
        return {
            "status": "success",
            "mode": "convert",
            "converted": text,
            "changed_lines": changed,
            "notes": notes,
            "refused": refused,
            "total_lines": len(analysis.lines),
        }

    def _explain_result(self, analysis: FileAnalysis, line_value: Any) -> dict[str, Any]:
        total = len(analysis.lines)
        focus = self._focus_line(line_value, total)
        facts = analysis.lines[focus - 1]
        rejected = isinstance(analysis.compile_error, (IndentationError, TabError)) and (
            analysis.compile_error.lineno == focus
        )
        if rejected:
            preceding = [row for row in analysis.indent_stack_by_row if row < focus]
            levels = analysis.indent_stack_by_row[max(preceding)] if preceding else [0]
        else:
            levels = analysis.indent_stack_by_row.get(focus)
        if levels is None:
            enclosing = [
                row
                for row in analysis.indent_stack_by_row
                if row <= focus
            ]
            levels = analysis.indent_stack_by_row[max(enclosing)] if enclosing else [0]
        parent: dict[str, Any] | None = None
        construct_stack: list[dict[str, Any]] = []
        if not isinstance(analysis.compile_error, SyntaxError):
            try:
                tree = ast.parse(analysis.text)
            except SyntaxError:
                tree = None
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(
                        node,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef,
                            ast.ClassDef,
                            ast.If,
                            ast.While,
                            ast.For,
                            ast.AsyncFor,
                            ast.With,
                            ast.AsyncWith,
                            ast.Try,
                            ast.Match,
                        ),
                    ):
                        end = node.end_lineno or node.lineno
                        if node.lineno <= focus <= end:
                            construct_stack.append(
                                {
                                    "kind": type(node).__name__,
                                    "name": getattr(node, "name", None),
                                    "line": node.lineno,
                                    "end_line": end,
                                }
                            )
                construct_stack.sort(key=lambda item: (item["end_line"] - item["line"], item["line"]))
                if construct_stack:
                    parent = construct_stack[0]
        why: str | None = None
        exc = analysis.compile_error
        if isinstance(exc, (IndentationError, TabError)):
            if exc.lineno == focus:
                why = (
                    f"the interpreter rejects this line: {exc.msg} "
                    f"(reported col {exc.offset}); live levels at this point are "
                    f"{levels} in interpreter columns"
                )
            else:
                why = (
                    f"this line is not itself rejected; the interpreter fails at line "
                    f"{exc.lineno}: {exc.msg}"
                )
        elif exc is not None:
            why = f"this line is fine indentation-wise; compile fails elsewhere: {exc.msg}"
        return {
            "status": "success",
            "mode": "explain",
            "line": focus,
            "text": facts.text[:120],
            "leading_whitespace": repr(facts.lead),
            "classification": facts.classification,
            "interpreter_column": facts.interp_column(),
            "visual_column": facts.visual_column(analysis.tab_width),
            "levels": levels,
            "parent_construct": parent,
            "construct_stack": construct_stack,
            "why_the_line_fails": why,
        }
