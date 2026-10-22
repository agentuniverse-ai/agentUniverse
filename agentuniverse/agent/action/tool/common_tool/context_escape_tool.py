#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: context_escape_tool.py

"""Context-safe text escaping tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency helper agents can
call before *embedding* arbitrary text into another format. Unlike
RegexTool (which matches and replaces text), this tool prepares text
for safe embedding: given a target context, ``escape`` neutralises the
characters that break that context and ``unescape`` reverses the
transform, so every context pair round-trips exactly —
``unescape(escape(x)) == x`` — even for text that already contains
escape markers, quotes, pipes, newlines or CJK / emoji.

Supported contexts:

* ``markdown_table`` — GFM table cells are broken by pipes and raw
  newlines. ``escape`` turns ``|`` into ``\\|`` (the GFM cell idiom),
  ``\\n`` into a literal ``<br>`` marker and a bare ``\\r`` into a
  ``<cr>`` marker, so LF, CR and CRLF all survive verbatim and no raw
  newline is left in the cell. Backslashes are doubled and literal
  ``<br>`` / ``<cr>`` markers already present in the input are escaped
  to ``\\<br>`` / ``\\<cr>``, which keeps the transform exactly
  invertible.
* ``csv`` — RFC 4180 field encoding: the field is wrapped in double
  quotes (with every embedded ``"`` doubled) when — and only when — it
  contains a comma, a double quote, a CR or an LF. ``unescape`` parses
  a strictly well-formed quoted field and rejects unterminated quotes,
  unescaped inner quotes and trailing junk.
* ``shell_single`` — POSIX single-quote wrapping: the text is wrapped
  in ``'...'`` with every embedded single quote spelled as the
  standard ``'"'"'`` idiom (close quote, quoted quote, reopen quote).
  ``unescape`` parses exactly that idiom and rejects any other use of
  a single quote.
* ``html_attr`` — escapes the full five-entity set ``& < > " '`` as
  ``&amp; &lt; &gt; &quot; &#x27;`` (safe for double- or
  single-quoted attribute values). ``unescape`` decodes exactly those
  five entities and passes anything else through verbatim.
* ``html_text`` — escapes only the three characters that are special
  in HTML text content (``& < >``); quotes are left alone. ``unescape``
  decodes exactly those three entities.
* ``json_string`` — ``json.dumps`` / ``json.loads`` on the whole
  string literal (surrounding double quotes included), with an
  ``ensure_ascii`` option (default ``True``) that controls whether
  non-ASCII characters are emitted as ``\\uXXXX`` escapes. Decoding
  works for both forms and requires the input to be a single,
  complete JSON string literal.
* ``regex`` — ``escape`` is ``re.escape``. ``unescape`` reverses a
  backslash placed before any ASCII punctuation character or the
  whitespace characters space / tab / LF / CR / VT / FF — the
  documented superset of what ``re.escape`` produces — and rejects
  regex escape sequences such as ``\\d`` that never appear in
  ``re.escape`` output.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text, unknown mode or
context, ``ensure_ascii`` outside the ``json_string`` context,
oversized text) raise a ``ValueError``, mirroring the other common
tools. Errors that depend on the *content being processed* — a
malformed markdown escape, an ill-formed CSV field, non-idiomatic
shell quoting, input that is not a JSON string literal, or an
unsupported regex escape — are returned as a structured ``error``
payload so an agent can react without catching exceptions.
"""

import json
import re
import string
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ASCII punctuation plus the whitespace characters re.escape may escape.
_REGEX_UNESCAPE_FOLLOWERS = frozenset(string.punctuation) | frozenset(
    " \t\n\r\v\f"
)
# html_attr entities (in no particular order — their second characters differ).
_HTML_ATTR_ENTITIES: tuple[tuple[str, str], ...] = (
    ("&", "&amp;"),
    ("<", "&lt;"),
    (">", "&gt;"),
    ('"', "&quot;"),
    ("'", "&#x27;"),
)
_HTML_TEXT_ENTITIES: tuple[tuple[str, str], ...] = (
    ("&", "&amp;"),
    ("<", "&lt;"),
    (">", "&gt;"),
)
# Characters that force RFC 4180 field quoting.
_CSV_QUOTE_TRIGGERS = frozenset(',"\r\n')
_SHELL_QUOTE_IDIOM = "'\"'\"'"


class ContextEscapeTool(Tool):
    """Escape / unescape text for safe embedding into a target context.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "context_escape_tool"
    description: str = (
        "Context escape tool — prepare text for safe embedding, pure "
        "Python stdlib, no network required. escape/unescape for seven "
        "contexts: markdown_table (pipes -> \\|, newlines -> <br>, CR -> "
        "<cr>, marker-safe round trip), csv (RFC 4180 field quoting with "
        "doubled quotes), shell_single (POSIX '...' wrapping with the "
        "'\"'\"' idiom for embedded quotes), html_attr (& < > \" ' -> "
        "entities), html_text (& < > -> entities), json_string "
        "(json.dumps/json.loads with an ensure_ascii option), regex "
        "(re.escape and its documented inverse). Every context pair "
        "round-trips exactly: unescape(escape(x)) == x."
    )

    MODES: ClassVar[tuple] = ("escape", "unescape")
    CONTEXTS: ClassVar[tuple] = (
        "markdown_table",
        "csv",
        "shell_single",
        "html_attr",
        "html_text",
        "json_string",
        "regex",
    )

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        context: str,
        text: Any = None,
        ensure_ascii: Any = None,
    ) -> dict[str, Any]:
        """Run one escape / unescape operation.

        Args:
            mode (str): ``escape`` or ``unescape``.
            context (str): One of ``markdown_table`` / ``csv`` /
                ``shell_single`` / ``html_attr`` / ``html_text`` /
                ``json_string`` / ``regex``.
            text (str): The text to transform (non-empty string).
            ensure_ascii (bool): ``json_string`` context only — passed to
                ``json.dumps`` when escaping (``True`` emits non-ASCII
                characters as ``\\uXXXX`` escapes, the default; ``False``
                keeps them verbatim). Ignored-as-error for any other
                context.

        Returns:
            Dict[str, Any]: The operation result (a ``result`` string plus
                the call context; the ``json_string`` context also reports
                the effective ``ensure_ascii`` flag) or a structured
                ``error`` payload for content-level failures (malformed
                markdown escape, ill-formed CSV field, non-idiomatic shell
                quoting, non-JSON-string input, unsupported regex escape).

        Raises:
            ValueError: If any parameter is malformed (before any
                transformation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if context not in self.CONTEXTS:
            self._invalid(
                "context must be one of: "
                f"{', '.join(self.CONTEXTS)} (got {context!r})"
            )
        clean_text = self._validate_text(text)
        clean_ensure_ascii = self._validate_ensure_ascii(ensure_ascii, context)

        runners = {
            "markdown_table": self._run_markdown_table,
            "csv": self._run_csv,
            "shell_single": self._run_shell_single,
            "html_attr": lambda op, t: self._run_html(op, t, "html_attr"),
            "html_text": lambda op, t: self._run_html(op, t, "html_text"),
            "json_string": lambda op, t: self._run_json_string(
                op, t, clean_ensure_ascii
            ),
            "regex": self._run_regex,
        }
        return runners[context](mode, clean_text)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"context_escape_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_ensure_ascii(cls, ensure_ascii: Any, context: str) -> bool:
        """Validate the ``ensure_ascii`` option (json_string only)."""
        if ensure_ascii is None:
            return True
        if isinstance(ensure_ascii, bool):
            if context != "json_string":
                cls._invalid(
                    "ensure_ascii only applies to the json_string context "
                    f"(got context={context!r})"
                )
            return ensure_ascii
        cls._invalid(f"ensure_ascii must be a boolean or None (got {ensure_ascii!r})")

    # ------------------------------------------------------------------ #
    # markdown_table context
    # ------------------------------------------------------------------ #

    def _run_markdown_table(self, operation: str, text: str) -> dict[str, Any]:
        """Escape / unescape GFM table cell content (pipes + newlines)."""
        context = {"mode": operation, "context": "markdown_table"}
        if operation == "escape":
            # Order matters: protect backslashes first so the markers we
            # introduce below are unambiguous, then protect literal
            # markers, then escape pipes, then map the newline code points
            # to their markers (CR before LF so CRLF becomes <cr><br>).
            protected = (
                text.replace("\\", "\\\\")
                .replace("<br>", "\\<br>")
                .replace("<cr>", "\\<cr>")
            )
            escaped = (
                protected.replace("|", "\\|")
                .replace("\r", "<cr>")
                .replace("\n", "<br>")
            )
            return {**context, "result": escaped}

        out: list[str] = []
        i = 0
        length = len(text)
        while i < length:
            char = text[i]
            if char == "\\":
                if text.startswith("\\\\", i):
                    out.append("\\")
                    i += 2
                elif text.startswith("\\|", i):
                    out.append("|")
                    i += 2
                elif text.startswith("\\<br>", i):
                    out.append("<br>")
                    i += 5
                elif text.startswith("\\<cr>", i):
                    out.append("<cr>")
                    i += 5
                else:
                    return self._error_result(
                        context,
                        error_type="invalid_escape_sequence",
                        message=(
                            "input contains a '\\' that is not followed by "
                            "'\\', '|', '<br>' or '<cr>' — only the escapes "
                            "produced by the escape direction are accepted "
                            f"(got {text[:64]!r})"
                        ),
                    )
            elif text.startswith("<br>", i):
                out.append("\n")
                i += 4
            elif text.startswith("<cr>", i):
                out.append("\r")
                i += 4
            else:
                out.append(char)
                i += 1
        return {**context, "result": "".join(out)}

    # ------------------------------------------------------------------ #
    # csv context (RFC 4180)
    # ------------------------------------------------------------------ #

    def _run_csv(self, operation: str, text: str) -> dict[str, Any]:
        """RFC 4180 field encoding / strict field parsing."""
        context = {"mode": operation, "context": "csv"}
        if operation == "escape":
            if any(char in _CSV_QUOTE_TRIGGERS for char in text):
                return {**context, "result": '"' + text.replace('"', '""') + '"'}
            return {**context, "result": text}

        if not text.startswith('"'):
            if '"' in text:
                return self._error_result(
                    context,
                    error_type="invalid_csv_field",
                    message=(
                        "an unquoted RFC 4180 field must not contain double "
                        "quotes; quote the field and double embedded quotes "
                        f"instead (got {text[:64]!r})"
                    ),
                )
            return {**context, "result": text}

        out: list[str] = []
        i = 1
        length = len(text)
        while i < length:
            char = text[i]
            if char == '"':
                if i + 1 < length and text[i + 1] == '"':
                    out.append('"')
                    i += 2
                    continue
                if i + 1 == length:
                    return {**context, "result": "".join(out)}
                return self._error_result(
                    context,
                    error_type="invalid_csv_field",
                    message=(
                        "quoted field has a double quote that is neither "
                        "doubled nor the closing quote, or trailing content "
                        f"after the closing quote (got {text[:64]!r})"
                    ),
                )
            out.append(char)
            i += 1
        return self._error_result(
            context,
            error_type="invalid_csv_field",
            message=(
                "quoted field is not terminated by a closing double quote "
                f"(got {text[:64]!r})"
            ),
        )

    # ------------------------------------------------------------------ #
    # shell_single context (POSIX single quoting)
    # ------------------------------------------------------------------ #

    def _run_shell_single(self, operation: str, text: str) -> dict[str, Any]:
        """Wrap in POSIX single quotes with the '\"'\"' idiom."""
        context = {"mode": operation, "context": "shell_single"}
        if operation == "escape":
            return {
                **context,
                "result": "'" + text.replace("'", _SHELL_QUOTE_IDIOM) + "'",
            }

        if len(text) < 2 or text[0] != "'" or text[-1] != "'":
            return self._error_result(
                context,
                error_type="invalid_shell_quoting",
                message=(
                    "input is not a POSIX single-quoted string: it must "
                    "start and end with ' and be at least two characters "
                    f"long (got {text[:64]!r})"
                ),
            )
        inner = text[1:-1]
        out: list[str] = []
        i = 0
        length = len(inner)
        while i < length:
            if inner[i] == "'":
                if inner.startswith(_SHELL_QUOTE_IDIOM, i):
                    out.append("'")
                    i += 5
                else:
                    return self._error_result(
                        context,
                        error_type="invalid_shell_quoting",
                        message=(
                            "embedded single quotes must use the '\"'\"' "
                            "idiom (close quote, quoted quote, reopen "
                            f"quote) (got {text[:64]!r})"
                        ),
                    )
            else:
                out.append(inner[i])
                i += 1
        return {**context, "result": "".join(out)}

    # ------------------------------------------------------------------ #
    # html_attr / html_text contexts
    # ------------------------------------------------------------------ #

    def _run_html(
        self, operation: str, text: str, context_name: str
    ) -> dict[str, Any]:
        """Escape / unescape HTML attribute (5 entities) or text (3)."""
        context = {"mode": operation, "context": context_name}
        entities = (
            _HTML_ATTR_ENTITIES if context_name == "html_attr" else _HTML_TEXT_ENTITIES
        )
        if operation == "escape":
            # '&' must be replaced first so entity introducers introduced
            # by later replacements are not escaped twice.
            escaped = text
            for char, entity in entities:
                escaped = escaped.replace(char, entity)
            return {**context, "result": escaped}

        out: list[str] = []
        i = 0
        length = len(text)
        while i < length:
            if text[i] == "&":
                for char, entity in entities:
                    if text.startswith(entity, i):
                        out.append(char)
                        i += len(entity)
                        break
                else:
                    # A bare '&' (or an entity outside this context's set)
                    # passes through verbatim.
                    out.append("&")
                    i += 1
            else:
                out.append(text[i])
                i += 1
        return {**context, "result": "".join(out)}

    # ------------------------------------------------------------------ #
    # json_string context
    # ------------------------------------------------------------------ #

    def _run_json_string(
        self, operation: str, text: str, ensure_ascii: bool
    ) -> dict[str, Any]:
        """Encode / decode a complete JSON string literal."""
        context = {
            "mode": operation,
            "context": "json_string",
            "ensure_ascii": ensure_ascii,
        }
        if operation == "escape":
            return {**context, "result": json.dumps(text, ensure_ascii=ensure_ascii)}
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return self._error_result(
                context,
                error_type="invalid_json_string",
                message=(
                    "input is not a valid JSON string literal (a complete "
                    'value like "text" with surrounding double quotes); '
                    f"got {text[:64]!r}"
                ),
            )
        if not isinstance(value, str):
            return self._error_result(
                context,
                error_type="invalid_json_string",
                message=(
                    "input is valid JSON but not a string literal — numbers, "
                    "booleans, null, arrays and objects are not accepted "
                    f"(got {text[:64]!r})"
                ),
            )
        return {**context, "result": value}

    # ------------------------------------------------------------------ #
    # regex context
    # ------------------------------------------------------------------ #

    def _run_regex(self, operation: str, text: str) -> dict[str, Any]:
        """re.escape and its inverse over the documented escape subset."""
        context = {"mode": operation, "context": "regex"}
        if operation == "escape":
            return {**context, "result": re.escape(text)}

        out: list[str] = []
        i = 0
        length = len(text)
        while i < length:
            if text[i] == "\\":
                if i + 1 >= length:
                    return self._error_result(
                        context,
                        error_type="invalid_regex_escape",
                        message=(
                            "input ends with a trailing backslash (got "
                            f"{text[:64]!r})"
                        ),
                    )
                follower = text[i + 1]
                if follower in _REGEX_UNESCAPE_FOLLOWERS:
                    out.append(follower)
                    i += 2
                else:
                    return self._error_result(
                        context,
                        error_type="invalid_regex_escape",
                        message=(
                            "input contains a regex escape sequence that "
                            "re.escape never produces; only a backslash "
                            "before an ASCII punctuation or whitespace "
                            "character can be reversed (got "
                            f"{text[:64]!r})"
                        ),
                    )
            else:
                out.append(text[i])
                i += 1
        return {**context, "result": "".join(out)}

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any], error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
