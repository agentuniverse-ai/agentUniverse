#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: env_file_tool.py

"""dotenv (``.env``) file parsing / editing tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency helper agents can
call for environment plumbing: inspecting a ``.env`` payload, reading
one variable, editing one assignment without disturbing the rest of
the file, regenerating a canonical file, or checking variable
references. It complements ``IniConfigTool`` (#3725, INI sections via
:mod:`configparser`) and ``JsonYamlTool`` (#3579, JSON <-> YAML):
a dotenv file is *not* an INI file — it is a flat list of
shell-style ``KEY=value`` assignments with quote/escape semantics,
``export`` prefixes, last-wins duplicate keys and ``${VAR}`` /
``$VAR`` reference conventions of its own — so it gets a dedicated
tool instead of a stretch of :mod:`configparser`.

The tool operates purely on *text* (it never touches the filesystem)
and supports five modes:

* ``parse`` — parse ``.env`` *text* into an ordered dict plus
  metadata. Each entry records the ``value`` (parsed), the ``raw``
  value portion as written (quotes and inline comments included), the
  1-based ``line`` number of the winning occurrence, the ``exported``
  flag and the ``lines`` of every occurrence. Blank and comment lines
  are counted (``blank_lines`` / ``comment_lines``); lines that are
  neither blank, comment nor a well-formed assignment are listed in
  ``malformed_lines`` (with line number and trimmed content) instead
  of aborting the parse. Duplicate keys are *last-wins*: the value
  comes from the last occurrence while the dict keeps the first
  occurrence position, and every duplicated key is listed in
  ``duplicates`` with all its line numbers.
* ``get`` — look up one ``key`` (case-sensitive, like the shell) and
  return its parsed value, raw value, line and ``exported`` flag; a
  missing key is a structured ``key_not_found`` error payload that
  lists the defined keys.
* ``set`` — return *modified text* for a ``key``/``value`` update via
  a line-level patch: the first occurrence of the key is rewritten in
  place (order, comments, blank lines and unrelated assignments are
  preserved byte-for-byte), any *later* duplicate occurrences are
  removed, and a missing key is appended before the trailing
  blank/comment block (after the last assignment or malformed line;
  at the very end when the file has no content lines). The optional
  ``export`` flag forces ``export KEY=...`` on/off; by default the
  existing prefix of the first occurrence is preserved. The value is
  written with the canonical quoting rules of ``serialize``.
* ``serialize`` — render a dict of ``key -> value`` strings as
  canonical ``.env`` text: plain values are written unquoted, values
  containing whitespace, ``#``, ``'``, ``"`` or backslashes (or
  control characters) are double-quoted with ``\\\\``, ``\\"``,
  ``\\n``, ``\\t`` and ``\\r`` escapes, and exported keys are prefixed
  with ``export`` (``export`` accepts ``None``/``False`` for none,
  ``True`` for all, or a list of key names).
* ``validate`` — scan every parsed value for ``${VAR}`` and ``$VAR``
  references and report the variables that are *not* defined anywhere
  in the file as a ``warnings`` list (each with the referencing line
  numbers), plus the malformed lines. A ``$`` not followed by an
  identifier or ``{identifier}`` (``$5``, ``$ ``), or immediately
  preceded by another ``$`` (the literal ``$$``), is not a reference;
  escaping is not considered.

Value parsing follows dotenv rules: leading/trailing whitespace around
the key, the ``=`` and the value is ignored; only the *first* ``=``
separates key from value. A value starting with ``"`` is
double-quoted — it ends at the next unescaped ``"`` and the inner text
unescapes ``\\n``, ``\\t``, ``\\r``, ``\\\\`` and ``\\"`` (any other
escape sequence is kept literally, backslash included); anything after
the closing quote is ignored. A value starting with ``'`` is
single-quoted — it ends at the next ``'`` and the inner text is fully
literal (unlike python-dotenv, ``\\`` and ``\\'`` are *not*
unescaped: single quotes mean literal, per the tool contract). Any
other value is unquoted — it ends at the first ``#`` preceded by
whitespace and not escaped as ``\\#`` (an inline comment; a ``#``
glued directly after ``=`` or into text such as ``KEY=#c`` or ``a#b``
is data, and an escaped ``\\#`` shields the comment while staying in
the value as written — both matching python-dotenv); leading and
trailing whitespace is stripped and any other backslash is literal. A
quote that never closes is a structured ``unterminated_quote`` error
payload carrying the line number; multiline (spanning lines) quoted
values are not supported.

Malformed *parameters* (wrong types, empty text in the parse/validate/
get modes, unknown mode, key not matching ``[A-Za-z_][A-Za-z0-9_]*``,
non-string serialize values, oversized text/values/variable counts,
``export`` lists naming unknown keys) raise a ``ValueError`` before
any computation, mirroring the other common tools. Errors that depend
on the *content being processed* — unterminated quotes, a missing key
on ``get`` — are returned as a structured ``error`` payload so an
agent can react without catching exceptions.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# A dotenv key: same identifier charset the shell accepts.
_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
# assignment := [export + whitespace] key [whitespace*] "=" rest-of-line
_ASSIGN_RE = re.compile(r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
# ${VAR} / $VAR references (validate mode). A '$' immediately preceded
# by another '$' (as in the literal '$$') never starts a reference.
_REF_BRACED_RE = re.compile(r"(?<!\$)\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_REF_BARE_RE = re.compile(r"(?<!\$)\$([A-Za-z_][A-Za-z0-9_]*)")
# Escape sequences unescaped inside double-quoted values.
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"'}


class _EnvParseError(Exception):
    """Content-level parse failure (carries the line number)."""

    def __init__(self, line: int, message: str) -> None:
        super().__init__(message)
        self.line = line
        self.message = message


class EnvFileTool(Tool):
    """dotenv (``.env``) file parsing / editing tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` / ``value``
            input length; longer inputs are rejected before any work.
        max_variables (int): Upper bound on the number of variables the
            ``serialize`` mode accepts.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "env_file_tool"
    description: str = (
        "Env file tool — parse, inspect, edit, serialize and validate "
        "dotenv (.env) text purely on the Python stdlib, no network "
        "required. parse mode returns an ordered dict plus per-key raw "
        "value, parsed value, line numbers, export flag, duplicate and "
        "malformed-line metadata (mode='parse'); get reads one key "
        "(mode='get'); set returns patched text that updates the first "
        "occurrence in place, removes later duplicates and appends "
        "missing keys before trailing comments (mode='set'); serialize "
        "renders a dict as canonical .env text with dotenv quoting "
        "(mode='serialize'); validate lists ${VAR}/$VAR references to "
        "variables the file never defines (mode='validate')."
    )

    MODES: ClassVar[tuple] = ("parse", "get", "set", "serialize", "validate")

    max_text_chars: int = 100_000
    max_variables: int = 1_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        key: Any = None,
        value: Any = None,
        data: Any = None,
        export: Any = None,
    ) -> dict[str, Any]:
        """Run one dotenv (.env) operation.

        Args:
            mode (str): One of ``parse`` / ``get`` / ``set`` /
                ``serialize`` / ``validate``.
            text (str): The ``.env`` text — required for the ``parse``,
                ``get``, ``set`` and ``validate`` modes (non-empty,
                except ``set`` which accepts an empty string and turns
                it into a one-assignment file); not used by
                ``serialize``.
            key (str): Variable name — required for the ``get`` and
                ``set`` modes; must match ``[A-Za-z_][A-Za-z0-9_]*``.
            value (str): New value for the key — required for the
                ``set`` mode (may be empty); written with canonical
                quoting.
            data (dict): Mapping of variable name -> value string —
                required for the ``serialize`` mode; order is kept.
            export (bool | list[str]): ``set`` mode: ``True`` /
                ``False`` forces the ``export`` prefix on/off (default:
                keep the first occurrence's existing prefix).
                ``serialize`` mode: ``None``/``False`` for no prefixes,
                ``True`` for all keys, or a list of key names to
                prefix.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the call context and mode-specific fields)
                or a structured ``error`` payload for content-level
                failures (unterminated quote, missing key on ``get``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "serialize":
            return self._run_serialize(data, export)
        if mode == "set":
            clean_text = self._validate_text(text, allow_empty=True)
            clean_key = self._validate_key(key)
            clean_value = self._validate_value(value)
            clean_export = self._validate_export(export, allow_list=False)
            return self._run_set(clean_text, clean_key, clean_value, clean_export)
        clean_text = self._validate_text(text)
        if mode == "parse":
            return self._run_parse(clean_text)
        if mode == "get":
            return self._run_get(clean_text, self._validate_key(key))
        return self._run_validate(clean_text)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"env_file_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any, allow_empty: bool = False) -> str:
        """Validate the ``text`` input (the whole .env payload)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text and not allow_empty:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_key(cls, key: Any) -> str:
        """Validate a variable name against the identifier charset."""
        if key is None or isinstance(key, bool) or not isinstance(key, str):
            cls._invalid(f"key must be a variable name string (got {key!r})")
        if not _KEY_RE.match(key):
            cls._invalid(
                "key must match [A-Za-z_][A-Za-z0-9_]* with no surrounding "
                f"whitespace (got {key!r})"
            )
        return key

    @classmethod
    def _validate_value(cls, value: Any) -> str:
        """Validate a ``set``-mode value (any content, including empty)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"value must be a string (got {value!r})")
        if len(value) > 100_000:
            cls._invalid(
                f"value exceeds the {100_000:,}-character limit "
                f"(got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _validate_data(cls, data: Any) -> dict[str, str]:
        """Validate the ``serialize``-mode dict (keys and string values)."""
        if data is None or isinstance(data, bool) or not isinstance(data, dict):
            cls._invalid(f"data must be a dict of variable name -> string (got {data!r})")
        if len(data) > 1_000:
            cls._invalid(
                f"data exceeds the {1_000:,}-variable limit (got {len(data):,})"
            )
        for k, v in data.items():
            if k is None or isinstance(k, bool) or not isinstance(k, str):
                cls._invalid(f"data keys must be variable name strings (got {k!r})")
            if not _KEY_RE.match(k):
                cls._invalid(
                    "data keys must match [A-Za-z_][A-Za-z0-9_]* "
                    f"(got {k!r})"
                )
            if v is None or isinstance(v, bool) or not isinstance(v, str):
                cls._invalid(
                    f"data values must be strings (got {v!r} for key {k!r}) "
                    "— convert values to strings before serializing"
                )
            if len(v) > 100_000:
                cls._invalid(
                    f"value for key {k!r} exceeds the {100_000:,}-character "
                    f"limit (got {len(v):,} characters)"
                )
        return data

    @classmethod
    def _validate_export(
        cls, export: Any, allow_list: bool, known_keys: Any = None
    ) -> Any:
        """Validate the ``export`` flag (bool, or a list of key names)."""
        if export is None or isinstance(export, bool):
            return export
        if allow_list:
            if isinstance(export, (str, bytes)) or not isinstance(export, (list, tuple, set)):
                cls._invalid(
                    "export must be None, a boolean or a list of key names "
                    f"(got {export!r})"
                )
            names = list(export)
            if len(names) != len(set(names)):
                cls._invalid(f"export list contains duplicate key names (got {export!r})")
            for name in names:
                if name is None or isinstance(name, bool) or not isinstance(name, str):
                    cls._invalid(f"export list entries must be strings (got {name!r})")
                if not _KEY_RE.match(name):
                    cls._invalid(
                        f"export list entries must match [A-Za-z_][A-Za-z0-9_]* (got {name!r})"
                    )
                if known_keys is not None and name not in known_keys:
                    cls._invalid(
                        f"export list names a key that is not in data (got {name!r})"
                    )
            return names
        cls._invalid(
            f"export must be None or a boolean for this mode (got {export!r})"
        )

    # ------------------------------------------------------------------ #
    # Line parsing (shared by parse / get / set / validate)
    # ------------------------------------------------------------------ #

    @classmethod
    def _split_lines(cls, text: str) -> list[dict[str, Any]]:
        """Classify every physical line (1-based ``line`` numbers).

        Returns a list of records with ``kind`` one of ``blank`` /
        ``comment`` / ``assignment`` / ``malformed``. Assignment records
        additionally carry ``key``, ``raw``, ``value`` and ``exported``.
        Raises :class:`_EnvParseError` on an unterminated quote.
        """
        records: list[dict[str, Any]] = []
        # A trailing '\n' is a terminator, not an extra blank line, so
        # drop the final empty split element ("A=1\n" is one line, but
        # "A=1\n\n" still has a real blank second line).
        physical = text.split("\n")
        if physical and physical[-1] == "":
            physical.pop()
        for line_number, original in enumerate(physical, start=1):
            stripped = original.strip()
            if not stripped:
                records.append(
                    {"kind": "blank", "line": line_number, "text": original}
                )
                continue
            if stripped.startswith("#"):
                records.append(
                    {"kind": "comment", "line": line_number, "text": original}
                )
                continue
            match = _ASSIGN_RE.match(stripped)
            if match is None:
                records.append(
                    {"kind": "malformed", "line": line_number, "text": stripped}
                )
                continue
            # The optional export group only matches before the key, so
            # the key starting past column 0 means the prefix is there.
            exported = match.start(1) > 0
            value_portion = stripped[match.end() :]
            records.append(
                {
                    "kind": "assignment",
                    "line": line_number,
                    "key": match.group(1),
                    "raw": value_portion.strip(),
                    "value": cls._parse_value(value_portion, line_number),
                    "exported": exported,
                }
            )
        return records

    @classmethod
    def _parse_value(cls, value_part: str, line_number: int) -> str:
        """Parse one raw value portion according to dotenv quote rules.

        Leading whitespace before a quote is ignored; the unquoted
        branch must see the whitespace to apply the inline-comment
        rule, so it gets the portion as written.
        """
        probe = value_part.lstrip()
        if probe.startswith('"'):
            inner, closed = cls._read_double_quoted(probe)
            if not closed:
                raise _EnvParseError(
                    line_number,
                    f"line {line_number}: double-quoted value never closes "
                    f"(got {value_part[:64]!r})",
                )
            return cls._unescape(inner)
        if probe.startswith("'"):
            end = probe.find("'", 1)
            if end == -1:
                raise _EnvParseError(
                    line_number,
                    f"line {line_number}: single-quoted value never closes "
                    f"(got {value_part[:64]!r})",
                )
            return probe[1:end]
        return cls._parse_unquoted(value_part)

    @staticmethod
    def _read_double_quoted(value_part: str) -> tuple[str, bool]:
        """Return (inner, closed) for a double-quoted value portion."""
        index = 1
        length = len(value_part)
        while index < length:
            char = value_part[index]
            if char == "\\":
                index += 2
                continue
            if char == '"':
                return value_part[1:index], True
            index += 1
        return value_part[1:], False

    @staticmethod
    def _unescape(inner: str) -> str:
        """Unescape \\n / \\t / \\r / \\\\ / \\" inside double quotes.

        Any other escape sequence is kept literally, backslash included.
        """
        out: list[str] = []
        index = 0
        length = len(inner)
        while index < length:
            char = inner[index]
            if (
                char == "\\"
                and index + 1 < length
                and inner[index + 1] in _ESCAPES
            ):
                out.append(_ESCAPES[inner[index + 1]])
                index += 2
            else:
                out.append(char)
                index += 1
        return "".join(out)

    @staticmethod
    def _parse_unquoted(value_part: str) -> str:
        """Parse an unquoted value (dotenv inline-comment rules).

        The comment starts at the first ``#`` that is *preceded by
        whitespace* and not escaped as ``\\#`` — a ``#`` glued directly
        after ``=`` or into text (``KEY=#c`` / ``a#b``) is data, and an
        escaped ``\\#`` shields the comment while staying in the value
        as written (both matching python-dotenv). Leading and trailing
        whitespace is stripped; any other backslash is literal.
        """
        out: list[str] = []
        index = 0
        length = len(value_part)
        while index < length:
            char = value_part[index]
            if char == "\\" and index + 1 < length and value_part[index + 1] == "#":
                out.append("\\")
                out.append("#")
                index += 2
                continue
            if char == "#" and index > 0 and value_part[index - 1] in " \t":
                break
            out.append(char)
            index += 1
        return "".join(out).strip()

    @classmethod
    def _analyze(cls, text: str) -> dict[str, Any]:
        """Aggregate line records into the shared parse summary."""
        records = cls._split_lines(text)
        variables: dict[str, dict[str, Any]] = {}
        occurrence_lines: dict[str, list[int]] = {}
        malformed: list[dict[str, Any]] = []
        blank_lines = 0
        comment_lines = 0
        for record in records:
            kind = record["kind"]
            if kind == "blank":
                blank_lines += 1
            elif kind == "comment":
                comment_lines += 1
            elif kind == "malformed":
                malformed.append(
                    {"line": record["line"], "content": record["text"]}
                )
            else:
                key = record["key"]
                occurrence_lines.setdefault(key, []).append(record["line"])
                # Last-wins: refresh the payload fields on every
                # occurrence while the dict keeps the first position.
                variables[key] = {
                    "value": record["value"],
                    "raw": record["raw"],
                    "line": record["line"],
                    "exported": record["exported"],
                }
        for key, lines in occurrence_lines.items():
            variables[key]["lines"] = lines
        duplicates = [
            {"key": key, "lines": lines}
            for key, lines in occurrence_lines.items()
            if len(lines) > 1
        ]
        return {
            "records": records,
            "variables": variables,
            "duplicates": duplicates,
            "malformed_lines": malformed,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "total_lines": len(records),
        }

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _run_parse(self, text: str) -> dict[str, Any]:
        """Parse .env text into an ordered dict plus metadata."""
        try:
            analysis = self._analyze(text)
        except _EnvParseError as exc:
            return self._error_result(
                {"mode": "parse"}, error_type="unterminated_quote", message=exc.message
            )
        duplicates = analysis["duplicates"]
        malformed = analysis["malformed_lines"]
        summary = (
            f"{len(analysis['variables'])} variable(s) parsed from "
            f"{analysis['total_lines']} line(s)"
        )
        if duplicates:
            summary += f", {len(duplicates)} duplicated key(s) (last one wins)"
        if malformed:
            summary += f", {len(malformed)} malformed line(s)"
        return {
            "mode": "parse",
            "variables": analysis["variables"],
            "count": len(analysis["variables"]),
            "duplicates": duplicates,
            "blank_lines": analysis["blank_lines"],
            "comment_lines": analysis["comment_lines"],
            "malformed_lines": malformed,
            "result": summary,
        }

    # ------------------------------------------------------------------ #
    # get mode
    # ------------------------------------------------------------------ #

    def _run_get(self, text: str, key: str) -> dict[str, Any]:
        """Read one variable (case-sensitive, last occurrence wins)."""
        try:
            analysis = self._analyze(text)
        except _EnvParseError as exc:
            return self._error_result(
                {"mode": "get", "key": key},
                error_type="unterminated_quote",
                message=exc.message,
            )
        variables = analysis["variables"]
        if key not in variables:
            defined = sorted(variables)
            shown = ", ".join(defined[:20]) + (
                ", …" if len(defined) > 20 else ""
            )
            return self._error_result(
                {"mode": "get", "key": key},
                error_type="key_not_found",
                message=(
                    f"key {key!r} is not defined in the .env text "
                    f"(lookup is case-sensitive); defined keys: {shown or 'none'}"
                ),
            )
        entry = variables[key]
        return {
            "mode": "get",
            "key": key,
            "value": entry["value"],
            "raw": entry["raw"],
            "line": entry["line"],
            "exported": entry["exported"],
            "lines": entry["lines"],
            "result": entry["value"],
        }

    # ------------------------------------------------------------------ #
    # set mode (line-level patch of the original text)
    # ------------------------------------------------------------------ #

    def _run_set(
        self, text: str, key: str, value: str, export: Any
    ) -> dict[str, Any]:
        """Patch one assignment: update first, dedupe later, else append."""
        try:
            records = self._split_lines(text)
        except _EnvParseError as exc:
            return self._error_result(
                {"mode": "set", "key": key},
                error_type="unterminated_quote",
                message=exc.message,
            )
        occurrences = [
            record
            for record in records
            if record["kind"] == "assignment" and record["key"] == key
        ]

        if export is None:
            prefix = bool(occurrences and occurrences[0]["exported"])
        else:
            prefix = bool(export)
        new_line = (
            ("export " if prefix else "") + key + "=" + self._serialize_value(value)
        )

        physical = text.split("\n")
        removed: list[int] = []
        if occurrences:
            first = occurrences[0]
            physical[first["line"] - 1] = new_line
            for later in occurrences[1:]:
                removed.append(later["line"])
                physical[later["line"] - 1] = None  # type: ignore[assignment]
            updated_line: int | None = first["line"]
            appended = False
        elif not text:
            physical = [new_line, ""]
            updated_line = 1
            appended = True
        else:
            insertion_index: int | None = None
            for record in reversed(records):
                if record["kind"] in ("assignment", "malformed"):
                    insertion_index = record["line"]
                    break
            if insertion_index is None:
                # No content lines at all: append at the very end while
                # keeping the file's trailing-newline style.
                insertion_index = (
                    len(physical) - 1
                    if text.endswith("\n") and physical
                    else len(physical)
                )
            physical.insert(insertion_index, new_line)
            updated_line = insertion_index + 1
            appended = True

        new_text = "\n".join(line for line in physical if line is not None)
        return {
            "mode": "set",
            "key": key,
            "value": value,
            "export": prefix,
            "updated_line": updated_line,
            "removed_duplicate_lines": removed,
            "appended": appended,
            "result": new_text,
        }

    # ------------------------------------------------------------------ #
    # serialize mode
    # ------------------------------------------------------------------ #

    def _run_serialize(self, data: Any, export: Any) -> dict[str, Any]:
        """Render a dict of variable -> value as canonical .env text."""
        clean_data = self._validate_data(data)
        clean_export = self._validate_export(
            export, allow_list=True, known_keys=clean_data
        )
        if clean_export is True:
            exported_keys = list(clean_data)
        elif clean_export:
            exported_keys = list(clean_export)
        else:
            exported_keys = []
        exported_set = set(exported_keys)
        lines = [
            ("export " if key in exported_set else "")
            + key
            + "="
            + self._serialize_value(value)
            for key, value in clean_data.items()
        ]
        new_text = "\n".join(lines) + ("\n" if lines else "")
        return {
            "mode": "serialize",
            "count": len(clean_data),
            "exported_keys": exported_keys,
            "result": new_text,
        }

    @staticmethod
    def _serialize_value(value: str) -> str:
        """Quote and escape one value following the canonical rules.

        Plain values (no whitespace, ``#``, ``'``, ``"``, backslash or
        control characters) are written unquoted; anything else is
        double-quoted with ``\\\\``, ``\\"``, ``\\n``, ``\\t`` and
        ``\\r`` escapes. The empty value is written as a bare ``KEY=``.
        """
        if value == "":
            return ""
        needs_quoting = any(
            char in " \t\r\n#'\"\\" or ord(char) < 0x20 or ord(char) == 0x7F
            for char in value
        )
        if not needs_quoting:
            return value
        out = ['"']
        for char in value:
            if char == "\\":
                out.append("\\\\")
            elif char == '"':
                out.append('\\"')
            elif char == "\n":
                out.append("\\n")
            elif char == "\t":
                out.append("\\t")
            elif char == "\r":
                out.append("\\r")
            else:
                out.append(char)
        out.append('"')
        return "".join(out)

    # ------------------------------------------------------------------ #
    # validate mode (undefined-variable reference scan)
    # ------------------------------------------------------------------ #

    def _run_validate(self, text: str) -> dict[str, Any]:
        """List ${VAR} / $VAR references to variables the file never defines."""
        try:
            analysis = self._analyze(text)
        except _EnvParseError as exc:
            return self._error_result(
                {"mode": "validate"},
                error_type="unterminated_quote",
                message=exc.message,
            )
        defined = set(analysis["variables"])
        undefined: dict[str, set[int]] = {}
        for record in analysis["records"]:
            if record["kind"] != "assignment":
                continue
            value = record["value"]
            referenced = [m.group(1) for m in _REF_BRACED_RE.finditer(value)]
            referenced += [m.group(1) for m in _REF_BARE_RE.finditer(value)]
            for name in referenced:
                if name not in defined:
                    undefined.setdefault(name, set()).add(record["line"])
        warnings = [
            {"variable": name, "lines": sorted(lines)}
            for name, lines in undefined.items()
        ]
        malformed = analysis["malformed_lines"]
        if warnings:
            names = ", ".join(w["variable"] for w in warnings)
            summary = (
                f"{len(warnings)} undefined variable(s) referenced: {names}"
            )
        else:
            summary = (
                f"ok — {len(defined)} variable(s) defined, no undefined "
                "references"
            )
        if malformed:
            summary += f"; {len(malformed)} malformed line(s)"
        return {
            "mode": "validate",
            "warnings": warnings,
            "defined_count": len(defined),
            "malformed_lines": malformed,
            "result": summary,
        }

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
