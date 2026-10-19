#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: ini_config_tool.py

"""INI configuration inspection / editing tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency INI helper agents can
call for configuration plumbing: inspecting settings files, reading one
value, or editing one key without disturbing the rest of the file. It
complements JsonYamlTool (json <-> yaml conversion, #3579) by covering
INI — the third widely used configuration format — via a thin,
strictly-validated façade over :mod:`configparser`, with five modes:

* ``parse`` — parse INI *text* into a nested dict
  ``{section: {key: value}}``. Section names keep their file spelling
  and file order; keys are lowercased (``RawConfigParser.optionxform``
  semantics — INI keys are case-insensitive, sections are
  case-sensitive and only the exact header ``[DEFAULT]`` is special).
  Values are RAW: the tool uses ``RawConfigParser`` behaviour, so
  ``%``-interpolation is disabled and ``%(name)s`` / ``100%%`` pass
  through untouched — no interpolation surprises. The ``[DEFAULT]``
  section is kept distinct in the output while still merging into the
  other sections per configparser read semantics: with
  ``include_defaults=True`` (the default) every non-DEFAULT section
  dict also contains the ``[DEFAULT]`` keys — a value defined in both
  places is overridden by the section's own entry, and the inherited
  keys appear first (exactly what ``parser.items(section)`` returns).
  With ``include_defaults=False`` each section dict contains only the
  keys literally written in that section.
* ``get`` — read one ``section`` + ``key`` value (key lookup is
  case-insensitive and falls back to ``[DEFAULT]`` per configparser
  semantics; the payload's ``source`` field reports whether the value
  came from the section itself, from ``[DEFAULT]``, or from the
  optional ``fallback`` string, which — like
  ``parser.get(..., fallback=...)`` — is returned instead of an error
  when the section or key is missing).
* ``set`` — return *modified text* for a ``section``/``key``/``value``
  update. Comment and ordering preservation is best-effort by design:
  the tool never rewrites the file through ``configparser.write()``
  (which would drop comments, blank-line structure and reorder
  nothing but still normalise everything else); instead it keeps the
  original lines and patches only the target key line as a string
  edit. Full-line ``#`` / ``;`` comments and key order elsewhere in
  the file are therefore preserved exactly — what is replaced is only
  the value portion of the target key line plus its continuation
  lines (which may themselves contain inline text, since inline
  comments are disabled by default in configparser). When the key is
  missing it is appended after the last line of the section (never
  after a trailing comment that documents the *next* section), and
  when the section is missing ``[section]`` plus the key are appended
  at the end of the text. Values containing newlines are written as
  indented continuation lines. After every edit the result is
  re-parsed and structurally compared with the original: if anything
  except the target key changed (possible for pathological layouts
  such as blank lines inside multiline values), a structured
  ``patch_failed`` error is returned instead of corrupted text.
* ``sections`` — list the sections in file order with their literal
  key counts (``[DEFAULT]`` is listed like any other section and its
  keys are not counted in the other sections).
* ``validate`` — attempt a strict parse; on success report section
  and option counts, on failure return the error with the line number
  extracted from the ``configparser.Error`` message / ``lineno``
  attribute (configparser never reports column positions, so
  ``column`` is always ``None``).

Malformed *parameters* (wrong types, unknown mode, missing section /
key / value, keys containing ``=``/``:`` or starting with ``#``/``;``,
padded values — configparser strips surrounding whitespace on read —
oversized text) raise a ``ValueError`` before any computation,
mirroring the other common tools. Errors that depend on the *content
being processed* — unparseable INI, duplicate sections or keys
(strict mode), missing section / key on ``get``, values that cannot
round-trip through an INI file, failed patch verification — are
returned as a structured ``error`` payload so an agent can react
without catching exceptions.
"""

import configparser
import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Section header line, matched against the stripped line exactly like
# configparser.SECTCRE (a match at the start is enough; trailing junk
# after the closing bracket is ignored by configparser as well).
_SECTION_LINE_RE = re.compile(r"\[(?P<header>[^]]+)\]")
# First "=" or ":" delimiter on an option line (configparser's OPTCRE
# is non-greedy, so the first delimiter occurrence always wins).
_ERROR_LINE_RE = re.compile(r"\[line\s+(\d+)\]")
# Impossible default-section name: parsing the text a second time with
# this as default_section yields the LITERAL keys of every section
# (including [DEFAULT] as a regular section) without any merging.
_LITERAL_DEFAULT_SENTINEL = "\ue000ini-tool-literal\x00"


class IniConfigTool(Tool):
    """INI configuration inspection / editing tool, stdlib only.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "ini_config_tool"
    description: str = (
        "INI config tool — pure Python stdlib configparser, no network "
        "required. Parse INI text to a nested dict with DEFAULT-section "
        "merge control (mode='parse'), read one section/key value with "
        "DEFAULT fallback and an optional fallback default "
        "(mode='get'), edit one key with comment- and order-preserving "
        "string-level patching (mode='set'), list sections with key "
        "counts (mode='sections'), and strict validation with error "
        "line numbers (mode='validate'). RawConfigParser semantics: "
        "values are raw, %-interpolation disabled."
    )

    MODES: ClassVar[tuple] = ("parse", "get", "set", "sections", "validate")
    DEFAULT_SECTION: ClassVar[str] = "DEFAULT"

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        section: Any = None,
        key: Any = None,
        value: Any = None,
        fallback: Any = None,
        include_defaults: Any = None,
    ) -> dict[str, Any]:
        """Run one INI operation.

        Args:
            mode (str): One of ``parse`` / ``get`` / ``set`` /
                ``sections`` / ``validate``.
            text (str): The INI text to operate on (files are read with
                other tools; this tool is text in / text out). Required,
                non-empty, at most ``max_text_chars`` characters.
            section (str): Required for ``get`` and ``set`` — the exact
                section name (case-sensitive per INI semantics;
                ``DEFAULT`` addresses the ``[DEFAULT]`` section).
                May not contain ``[`` / ``]`` or newlines.
            key (str): Required for ``get`` and ``set`` — the option
                name, matched case-insensitively (INI keys are
                lowercased on read). May not contain ``=`` / ``:`` /
                newlines, start with ``#`` / ``;``, or carry padding
                whitespace.
            value (str): Required for ``set`` — the new value. May
                contain newlines (written as continuation lines) but
                not padding whitespace or ``\\r``: configparser strips
                surrounding whitespace on read, so padded values could
                never round-trip.
            fallback (str): ``get`` only — string returned instead of a
                missing-section / missing-key error (mirrors
                ``parser.get(..., fallback=...)``).
            include_defaults (bool): ``parse`` only — when ``True``
                (the default) ``[DEFAULT]`` keys are merged into every
                other section (configparser ``items()`` semantics);
                when ``False`` only literally written keys are
                returned. ``[DEFAULT]`` itself always appears as its
                own ``"DEFAULT"`` entry.

        Returns:
            Dict[str, Any]: The operation result (primary output under
                ``result``, plus the call context) or a structured
                ``error`` payload for content-level failures
                (``parse_error`` with ``error_class`` / ``line`` /
                ``column`` fields, ``section_not_found``,
                ``key_not_found``, ``unrepresentable_value``,
                ``patch_failed``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)

        if mode == "validate":
            return self._run_validate(clean_text)
        if mode == "parse":
            return self._run_parse(clean_text, include_defaults)
        if mode == "sections":
            return self._run_sections(clean_text)
        if mode == "get":
            return self._run_get(clean_text, section, key, fallback)
        return self._run_set(clean_text, section, key, value)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"ini_config_tool: {message}")

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
    def _validate_section(cls, section: Any) -> str:
        """Validate the ``section`` input (get / set modes)."""
        if (
            section is None
            or isinstance(section, bool)
            or not isinstance(section, str)
        ):
            cls._invalid(
                f"section must be a non-empty string (got {section!r})"
            )
        if not section:
            cls._invalid("section must be a non-empty string (got '')")
        for char in "\n\r[]":
            if char in section:
                cls._invalid(
                    "section must not contain '[', ']' or newlines — "
                    f"such names cannot appear in an INI section header "
                    f"(got {section!r})"
                )
        return section

    @classmethod
    def _validate_key(cls, key: Any) -> str:
        """Validate the ``key`` input (get / set modes)."""
        if key is None or isinstance(key, bool) or not isinstance(key, str):
            cls._invalid(f"key must be a non-empty string (got {key!r})")
        if not key:
            cls._invalid("key must be a non-empty string (got '')")
        if key != key.strip():
            cls._invalid(
                "key must not carry leading/trailing whitespace — "
                "configparser strips it on read "
                f"(got {key!r})"
            )
        for char in "\n\r=:":
            if char in key:
                cls._invalid(
                    "key must not contain '=', ':' or newlines — the "
                    "first delimiter on a line ends the key per "
                    f"configparser parsing rules (got {key!r})"
                )
        if key[0] in "#;":
            cls._invalid(
                "key must not start with '#' or ';' — such a line is a "
                f"full-line INI comment (got {key!r})"
            )
        return key

    @classmethod
    def _validate_value(cls, value: Any) -> str:
        """Validate the ``value`` input (set mode)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"value must be a string (got {value!r})")
        if value != value.strip():
            cls._invalid(
                "value must not carry leading/trailing whitespace — "
                "configparser strips surrounding whitespace on read, so "
                "padded values could never round-trip "
                f"(got {value!r})"
            )
        if "\r" in value:
            cls._invalid(
                "value must not contain carriage returns (got "
                f"{value[:64]!r})"
            )
        return value

    @classmethod
    def _validate_fallback(cls, fallback: Any) -> Any:
        """Validate the ``fallback`` input (get mode)."""
        if fallback is None or isinstance(fallback, str):
            return fallback
        cls._invalid(
            f"fallback must be a string or None (got {fallback!r})"
        )

    @classmethod
    def _validate_include_defaults(cls, include_defaults: Any) -> bool:
        """Validate the ``include_defaults`` flag (parse mode)."""
        if include_defaults is None:
            return True
        if isinstance(include_defaults, bool):
            return include_defaults
        cls._invalid(
            "include_defaults must be a boolean or None (got "
            f"{include_defaults!r})"
        )

    # ------------------------------------------------------------------ #
    # configparser plumbing (public API only)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _strict_parse(text: str) -> configparser.RawConfigParser:
        """Strict RawConfigParser parse — no interpolation, duplicates raise."""
        parser = configparser.RawConfigParser()
        parser.read_string(text)
        return parser

    @classmethod
    def _literal_view(cls, text: str) -> dict[str, dict[str, str]]:
        """Map every section to its *literally written* keys.

        The text is re-parsed with an impossible ``default_section`` so
        no DEFAULT merging happens and ``[DEFAULT]`` shows up as a
        regular section. Keys are lowercased (optionxform); multiline
        values are already joined; order follows the file.
        """
        parser = configparser.RawConfigParser(
            default_section=_LITERAL_DEFAULT_SENTINEL, strict=False
        )
        parser.read_string(text)
        return {
            section: dict(parser.items(section))
            for section in parser.sections()
        }

    @staticmethod
    def _parse_error_payload(
        context: dict[str, Any], exc: configparser.Error
    ) -> dict[str, Any]:
        """Build a structured parse-error payload with a line number.

        Duplicate-section / duplicate-option / missing-section-header
        errors carry a ``lineno`` attribute; ParsingError only embeds
        ``[line  N]`` in its message, which is regex-extracted.
        configparser never reports column positions — ``column`` is
        always ``None``.
        """
        line = getattr(exc, "lineno", None)
        if not isinstance(line, int):
            match = _ERROR_LINE_RE.search(str(exc))
            line = int(match.group(1)) if match else None
        return {
            **context,
            "error": {
                "type": "parse_error",
                "error_class": type(exc).__name__,
                "message": str(exc)[:500],
                "line": line,
                "column": None,
            },
        }

    # ------------------------------------------------------------------ #
    # parse / sections / validate modes
    # ------------------------------------------------------------------ #

    def _run_parse(
        self, text: str, include_defaults: Any
    ) -> dict[str, Any]:
        """Parse INI text to a nested dict with DEFAULT merge control."""
        flag = self._validate_include_defaults(include_defaults)
        context: dict[str, Any] = {
            "mode": "parse",
            "include_defaults": flag,
        }
        try:
            defaults = dict(self._strict_parse(text).defaults())
            literal = self._literal_view(text)
        except configparser.Error as exc:
            return self._parse_error_payload(context, exc)
        if flag:
            result = {
                name: dict(defaults) if name == self.DEFAULT_SECTION
                else {**defaults, **keys}
                for name, keys in literal.items()
            }
        else:
            result = {name: dict(keys) for name, keys in literal.items()}
        return {
            **context,
            "result": result,
            "section_count": len(result),
            "option_count": sum(len(keys) for keys in literal.values()),
        }

    def _run_sections(self, text: str) -> dict[str, Any]:
        """List sections in file order with literal key counts."""
        context: dict[str, Any] = {"mode": "sections"}
        try:
            self._strict_parse(text)
            literal = self._literal_view(text)
        except configparser.Error as exc:
            return self._parse_error_payload(context, exc)
        listing = [
            {"name": name, "key_count": len(keys)}
            for name, keys in literal.items()
        ]
        return {
            **context,
            "default_section": self.DEFAULT_SECTION,
            "count": len(listing),
            "result": listing,
        }

    def _run_validate(self, text: str) -> dict[str, Any]:
        """Strict parse attempt with error line extraction."""
        context: dict[str, Any] = {"mode": "validate"}
        try:
            self._strict_parse(text)
            literal = self._literal_view(text)
        except configparser.Error as exc:
            payload = self._parse_error_payload(context, exc)
            return {**payload, "valid": False}
        return {
            **context,
            "valid": True,
            "section_count": len(literal),
            "option_count": sum(len(keys) for keys in literal.values()),
        }

    # ------------------------------------------------------------------ #
    # get mode
    # ------------------------------------------------------------------ #

    def _run_get(
        self, text: str, section: Any, key: Any, fallback: Any
    ) -> dict[str, Any]:
        """Read one value: section literal -> DEFAULT -> fallback."""
        clean_section = self._validate_section(section)
        clean_key = self._validate_key(key)
        clean_fallback = self._validate_fallback(fallback)
        context: dict[str, Any] = {
            "mode": "get",
            "section": clean_section,
            "key": clean_key,
        }
        try:
            defaults = dict(self._strict_parse(text).defaults())
            literal = self._literal_view(text)
        except configparser.Error as exc:
            return self._parse_error_payload(context, exc)

        lookup = clean_key.lower()
        if clean_section not in literal:
            if clean_fallback is not None:
                return {**context, "result": clean_fallback, "source": "fallback"}
            return self._error_result(
                context,
                error_type="section_not_found",
                message=(
                    f"section {clean_section!r} not found (available "
                    f"sections: {', '.join(literal) or 'none'})"
                ),
            )
        literal_keys = literal[clean_section]
        if lookup in literal_keys:
            return {**context, "result": literal_keys[lookup], "source": "section"}
        if lookup in defaults:
            return {**context, "result": defaults[lookup], "source": "DEFAULT"}
        if clean_fallback is not None:
            return {**context, "result": clean_fallback, "source": "fallback"}
        available = sorted(set(defaults) | set(literal_keys))
        return self._error_result(
            context,
            error_type="key_not_found",
            message=(
                f"key {clean_key!r} not found in section "
                f"{clean_section!r} (available keys: "
                f"{', '.join(available) or 'none'})"
            ),
        )

    # ------------------------------------------------------------------ #
    # set mode
    # ------------------------------------------------------------------ #

    def _run_set(
        self, text: str, section: Any, key: Any, value: Any
    ) -> dict[str, Any]:
        """Patch / append one key and return the modified text."""
        clean_section = self._validate_section(section)
        clean_key = self._validate_key(key)
        clean_value = self._validate_value(value)
        context: dict[str, Any] = {
            "mode": "set",
            "section": clean_section,
            "key": clean_key,
            "value": clean_value,
        }
        try:
            self._strict_parse(text)
            original = self._literal_view(text)
        except configparser.Error as exc:
            return self._parse_error_payload(context, exc)

        lines = text.splitlines(keepends=True)
        scanned = self._scan_sections(lines)
        target = next(
            (entry for entry in scanned if entry["name"] == clean_section),
            None,
        )
        if target is None:
            new_lines, action, key_line = self._append_section(
                lines, clean_section, clean_key, clean_value
            )
        elif clean_key.lower() in target["options"]:
            new_lines, action, key_line = self._patch_option(
                lines, target, clean_key, clean_value
            )
        else:
            new_lines, action, key_line = self._append_option(
                lines, target, clean_key, clean_value
            )
        new_text = "".join(new_lines)
        failure = self._verify(original, new_text, clean_section, clean_key.lower(), clean_value)
        if failure is not None:
            return self._error_result(context, error_type=failure[0], message=failure[1])
        return {
            **context,
            "action": action,
            "line": key_line,
            "result": new_text,
        }

    @staticmethod
    def _split_line(raw: str) -> tuple[str, str]:
        """Split a kept-ends line into (body, line_ending)."""
        for ending in ("\r\n", "\n", "\r"):
            if raw.endswith(ending):
                return raw[: -len(ending)], ending
        return raw, ""

    @staticmethod
    def _first_delimiter(body: str) -> int:
        """Index of the first ``=`` or ``:`` on the line, or ``-1``."""
        candidates = [
            index
            for index in (body.find("="), body.find(":"))
            if index != -1
        ]
        return min(candidates) if candidates else -1

    @classmethod
    def _scan_sections(cls, lines: list[str]) -> list[dict[str, Any]]:
        """Locate sections and their option lines (configparser rules).

        Mirrors ``RawConfigParser._read`` line classification: blank and
        full-line ``#`` / ``;`` comment lines are skipped (they neither
        open nor close a value); a line indented deeper than the last
        option/header line continues that option's value; a stripped
        line starting with ``[name]`` opens a section (exact name,
        case-sensitive); anything else is an option line whose key runs
        up to the first ``=`` / ``:`` delimiter.
        """
        sections: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        active_option: str | None = None
        indent_level = 0
        for index, raw in enumerate(lines):
            body, _ending = cls._split_line(raw)
            value = body.strip()
            if not value:
                # Blank line or full-line comment: skipped entirely, the
                # active option stays open for further continuations.
                continue
            cur_indent = len(body) - len(body.lstrip())
            if current is not None and active_option is not None and cur_indent > indent_level:
                current["options"][active_option]["last_line"] = index
                current["last_content"] = index
                continue
            match = _SECTION_LINE_RE.match(value)
            if match:
                current = {
                    "name": match.group("header"),
                    "options": {},
                    "last_content": index,
                }
                sections.append(current)
                active_option = None
                indent_level = cur_indent
                continue
            delimiter = cls._first_delimiter(body)
            if delimiter == -1 or current is None:
                # Cannot occur in text that passed the strict parse;
                # skipped defensively.
                continue
            key_text = body[:delimiter].rstrip()
            after = delimiter + 1
            while after < len(body) and body[after] in " \t":
                after += 1
            current["options"][key_text.strip().lower()] = {
                "index": index,
                "prefix": body[:after],
                "indent": cur_indent,
                "last_line": index,
            }
            active_option = key_text.strip().lower()
            indent_level = cur_indent
            current["last_content"] = index
        return sections

    @staticmethod
    def _value_lines(
        key_text: str, value: str, indent: int, ending: str
    ) -> list[str]:
        """Render ``key = value`` plus indented continuation lines.

        Newlines in the value become continuation lines indented one
        level deeper than the key (configparser strips continuation
        indentation on read and joins with ``\\n``).
        """
        parts = value.split("\n")
        rendered = [f"{key_text} = {parts[0]}{ending}"]
        continuation = " " * (indent + 1)
        rendered.extend(
            (continuation + part if part else "") + ending
            for part in parts[1:]
        )
        return rendered

    def _patch_option(
        self,
        lines: list[str],
        target: dict[str, Any],
        key: str,
        value: str,
    ) -> tuple[list[str], str, int]:
        """Replace the value part of the existing key line in place.

        The original leading whitespace, key spelling and delimiter
        style are preserved (string-level edit); any continuation lines
        of the old value are dropped and re-rendered from the new
        value.
        """
        option = target["options"][key.lower()]
        index = option["index"]
        _body, ending = self._split_line(lines[index])
        continuation = " " * (option["indent"] + 1)
        parts = value.split("\n")
        # A final line without a trailing newline keeps its shape unless
        # continuation lines must follow it.
        patched_ending = ending or ("\n" if len(parts) > 1 else "")
        patched = option["prefix"] + parts[0] + patched_ending
        new_lines = list(lines)
        # Drop the old continuation lines, then splice in the new ones.
        del new_lines[index + 1 : option["last_line"] + 1]
        extra = [
            (continuation + part if part else "") + (ending or "\n")
            for part in parts[1:]
        ]
        new_lines[index : index + 1] = [patched, *extra]
        return new_lines, "replaced", index + 1

    def _append_option(
        self,
        lines: list[str],
        target: dict[str, Any],
        key: str,
        value: str,
    ) -> tuple[list[str], str, int]:
        """Append the key after the last content line of the section.

        Inserting right after the last option / continuation line — not
        in front of the next section header — keeps trailing comments
        attached to the section they document.
        """
        insert_at = target["last_content"] + 1
        _, ending = self._split_line(lines[target["last_content"]])
        new_lines = self._ensure_ending(lines, insert_at)
        rendered = self._value_lines(key, value, 0, ending or "\n")
        new_lines[insert_at:insert_at] = rendered
        return new_lines, "added", insert_at + 1

    def _append_section(
        self, lines: list[str], section: str, key: str, value: str
    ) -> tuple[list[str], str, int]:
        """Append ``[section]`` plus the key at the end of the text."""
        new_lines = self._ensure_ending(lines, len(lines))
        ending = self._dominant_ending(new_lines)
        new_lines.append(f"[{section}]{ending}")
        key_line = len(new_lines) + 1
        new_lines.extend(self._value_lines(key, value, 0, ending))
        return new_lines, "created_section", key_line

    @staticmethod
    def _ensure_ending(lines: list[str], insert_at: int) -> list[str]:
        """Copy lines, giving the line before ``insert_at`` an ending."""
        new_lines = list(lines)
        if insert_at and insert_at <= len(new_lines):
            body, ending = IniConfigTool._split_line(new_lines[insert_at - 1])
            if not ending:
                new_lines[insert_at - 1] = body + "\n"
        return new_lines

    @staticmethod
    def _dominant_ending(lines: list[str]) -> str:
        """Line ending of the last line that has one (default ``\\n``)."""
        for raw in reversed(lines):
            _, ending = IniConfigTool._split_line(raw)
            if ending:
                return ending
        return "\n"

    def _verify(
        self,
        original: dict[str, dict[str, str]],
        new_text: str,
        section: str,
        key: str,
        value: str,
    ) -> tuple[str, str] | None:
        """Re-parse the edited text and compare the full structure.

        Everything except the target key must be byte-for-byte
        equivalent in parsed form; the target key must read back as the
        exact value that was set. Returns ``None`` on success or an
        ``(error_type, message)`` pair describing the failure.
        """
        expected = {name: dict(keys) for name, keys in original.items()}
        expected.setdefault(section, {})[key] = value
        try:
            self._strict_parse(new_text)
            actual = self._literal_view(new_text)
        except configparser.Error as exc:
            return (
                "patch_failed",
                "the edit produced text that no longer parses cleanly "
                f"({type(exc).__name__}: {str(exc)[:200]})",
            )
        if actual == expected:
            return None
        actual_value = actual.get(section, {}).get(key)
        if actual_value is not None and actual_value != value:
            return (
                "unrepresentable_value",
                "the value cannot round-trip through INI syntax — "
                "configparser strips continuation-line indentation on "
                "read, so the value reads back differently "
                f"(wanted {value!r}, got {actual_value!r})",
            )
        return (
            "patch_failed",
            "the edit changed more than the target key — the file layout "
            "(e.g. blank lines inside multiline values) is not supported "
            "for this edit; the original text is returned unchanged",
        )

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
