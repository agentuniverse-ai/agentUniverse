#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: front_matter_tool.py

"""Markdown YAML front-matter handling tool (parse / strip / set / merge).

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network utility for the document pipelines
agents build around markdown: reading metadata blocks, cleaning bodies
before further processing, stamping keys onto generated documents, and
combining metadata from two sources. ``MarkdownTocTool`` works on body
text; front matter is a separate concern handled here.

The tool is built purely on the standard library plus the framework's
existing PyYAML dependency (``tomllib`` joined the stdlib in Python
3.11, which is the project minimum) and supports four modes:

* ``parse`` — one markdown text to a structured description:
  ``front_matter`` (parsed mapping; an empty block parses to ``{}``),
  ``body`` (the remainder after the block, preserved byte for byte),
  ``has_front_matter`` and ``delimiters`` (which of the three supported
  fence forms was used). Three delimiter forms are supported — the
  YAML fences ``---`` ... ``---`` and ``...`` ... ``...`` (content
  parsed with ``yaml.safe_load``), and the TOML fence ``+++`` ... ``+++``
  (content parsed with ``tomllib.loads`` when it is valid TOML;
  otherwise the block is reported verbatim as ``raw_string`` with
  ``format: "raw_string"`` and ``front_matter: null`` — a documented
  fallback, not an error, because ``+++`` blocks in the wild are only
  TOML-ish). Other fences seen in the wild (``:::`` used by some
  remark/Nunjucks sites) are deliberately NOT supported; keeping to the
  three common forms keeps parsing unambiguous.
* ``strip`` — return the body only; a text without front matter is
  passed through unchanged.
* ``set`` — set one ``key`` / ``value`` pair in the front matter of a
  markdown text and return the full updated text. A dotted key
  (``a.b.c``) addresses a nested path, creating intermediate mappings.
  When the top-level key already exists only the lines belonging to
  that key are patched (a line-level patch), so the order of the other
  keys and comments above the patched key survive; new keys are
  appended at the end of the block. Serialization uses
  ``yaml.safe_dump(sort_keys=False)``. A text without front matter gets
  a fresh ``---`` block prepended. Setting a key in a ``+++`` block
  rewrites the block as a YAML ``---`` block (the stdlib has no TOML
  writer); the result reports the conversion via ``delimiters`` and
  ``converted_delimiters``.
* ``merge`` — merge the front matter of a first markdown text over the
  front matter of a second text and return the merged metadata plus the
  second text's body. ``precedence`` documents both conflict
  directions: ``"second"`` (default) keeps the second document's value
  for a key present in both, ``"first"`` flips it. Mapping values are
  merged recursively; every other type is replaced per key. ``+++``
  blocks are rewritten as YAML (same stdlib rationale as ``set``).

Front matter must start at the very first line of the text; the fence
line may carry trailing whitespace and must be exactly three
characters long (``----`` is a thematic break, not a fence). The
closing fence must equal the opening one, and the first matching fence
line closes the block.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing or non-string ``text`` /
``other_text``, missing or malformed ``key``, wrong ``value`` type,
unknown ``precedence``, oversized inputs) raise a ``ValueError``,
mirroring the other common tools. Errors that depend on the *content
being processed* are returned as a structured ``error`` payload
instead of raising: an unterminated front-matter block, YAML syntax
errors (carrying the 1-based ``line`` / ``column`` PyYAML reports for
the block), a front-matter block that parses to a non-mapping, TOML
front matter that is needed but not parseable (``set`` / ``merge``;
``parse`` falls back to ``raw_string``), and a dotted key whose
intermediate segment exists but is not a mapping.
"""

import re
import tomllib
from typing import Any, ClassVar

import yaml
from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# A top-level YAML key line: bare, single- or double-quoted key followed
# by a colon. Used by the set mode to locate the block to patch.
_TOP_KEY_RE = re.compile(
    r"\A(?:'([^']+)'|\"([^\"]+)\"|([^:\s][^:]*?))\s*:(?:\s|$)"
)


class _ContentError(Exception):
    """Internal carrier for content-level failures (never leaks out)."""

    def __init__(
        self,
        error_type: str,
        message: str,
        line: Any = None,
        column: Any = None,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.line = line
        self.column = column


class FrontMatterTool(Tool):
    """Markdown front-matter utility (parse / strip / set / merge).

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` / ``other_text``
            inputs (and on a string ``value``); longer inputs are rejected
            before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "front_matter_tool"
    description: str = (
        "Markdown front-matter tool — pure stdlib plus the framework's "
        "existing PyYAML, no network required. Parse a markdown text into "
        "its front-matter mapping and body (mode='parse'; YAML fences --- "
        "and ..., TOML fences +++ parsed with tomllib or reported as "
        "raw_string), return the body only (mode='strip'), set one "
        "key/value pair — dotted keys address nested paths — with a "
        "line-level patch that preserves key order and comments above the "
        "patched key (mode='set'), and merge the front matter of two "
        "markdown texts with documented per-key precedence in both "
        "directions plus the second text's body (mode='merge')."
    )

    MODES: ClassVar[tuple] = ("parse", "strip", "set", "merge")
    DELIMITERS: ClassVar[tuple] = ("---", "...", "+++")
    PRECEDENCES: ClassVar[tuple] = ("second", "first")

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        other_text: Any = None,
        key: Any = None,
        value: Any = None,
        precedence: Any = None,
    ) -> dict[str, Any]:
        """Run one front-matter operation.

        Args:
            mode (str): One of ``parse`` / ``strip`` / ``set`` / ``merge``.
            text (str): The markdown text to operate on. Required by every
                mode; for ``merge`` this is the *first* document whose
                front matter is merged over the second one's.
            other_text (str): Merge mode only — the *second* markdown
                document; the merged front matter is returned with this
                document's body.
            key (str): Set mode only — the key to set. A dotted key such
                as ``a.b.c`` addresses the nested path ``a -> b -> c``,
                creating intermediate mappings as needed.
            value (str | int | float | bool | None): Set mode only — the
                value to store (a Python ``None`` stores an explicit YAML
                ``null``).
            precedence (str): Merge mode only — ``"second"`` (default)
                keeps the second document's value when a key exists in
                both front matters; ``"first"`` keeps the first one's.

        Returns:
            Dict[str, Any]: The operation result (``result`` string for
                the ``strip`` / ``set`` / ``merge`` modes, the full
                front-matter description for ``parse``) or a structured
                ``error`` payload for content-level failures
                (unterminated block, YAML syntax errors with 1-based
                ``line`` / ``column``, non-mapping front matter,
                unparseable TOML needed by ``set`` / ``merge``, dotted
                key hitting a non-mapping segment).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text, name="text")
        if mode == "parse":
            return self._run_parse(clean_text)
        if mode == "strip":
            return self._run_strip(clean_text)
        if mode == "merge":
            clean_precedence = self._validate_precedence(precedence)
            clean_other = self._validate_text(other_text, name="other_text")
            return self._run_merge(clean_text, clean_other, clean_precedence)

        clean_key = self._validate_key(key)
        clean_value = self._validate_value(value)
        return self._run_set(clean_text, clean_key, clean_value)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"front_matter_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any, name: str) -> str:
        """Validate a markdown text input."""
        if (
            text is None
            or isinstance(text, bool)
            or not isinstance(text, str)
        ):
            cls._invalid(f"{name} must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid(f"{name} must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"{name} exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_key(cls, key: Any) -> str:
        """Validate the set-mode ``key`` (a dotted nested path)."""
        if key is None or isinstance(key, bool) or not isinstance(key, str):
            cls._invalid(f"key must be a non-empty dotted string (got {key!r})")
        if not key:
            cls._invalid("key must be a non-empty dotted string (got '')")
        if len(key) > 512:
            cls._invalid(
                f"key exceeds the 512-character limit (got {len(key)} characters)"
            )
        segments = key.split(".")
        for segment in segments:
            if not segment or re.search(r"[\s:]", segment):
                cls._invalid(
                    "key must be dot-separated path segments without "
                    f"whitespace or ':' characters (got {key!r})"
                )
        return key

    @classmethod
    def _validate_value(cls, value: Any) -> Any:
        """Validate the set-mode ``value`` (scalar YAML types only)."""
        if value is None or isinstance(value, (str, int, float, bool)):
            if isinstance(value, str) and len(value) > 100_000:
                cls._invalid(
                    "value exceeds the "
                    f"{100_000:,}-character limit (got {len(value):,} characters)"
                )
            return value
        cls._invalid(
            "value must be a string, int, float, bool or None "
            f"(got {type(value).__name__})"
        )

    @classmethod
    def _validate_precedence(cls, precedence: Any) -> str:
        """Validate the merge-mode ``precedence`` selector."""
        if precedence is None:
            return "second"
        if precedence not in cls.PRECEDENCES:
            cls._invalid(
                "precedence must be one of: "
                f"{', '.join(cls.PRECEDENCES)} (got {precedence!r})"
            )
        return precedence

    # ------------------------------------------------------------------ #
    # Front-matter splitting (fence detection)
    # ------------------------------------------------------------------ #

    @classmethod
    def _split_front_matter(
        cls, text: str
    ) -> tuple[str, str, str, str]:
        """Split ``text`` into ``(status, delimiter, block, body)``.

        ``status`` is ``"none"`` (no front matter), ``"ok"`` (a complete
        block) or ``"unterminated"`` (an opening fence with no matching
        closing fence — ``block`` is empty in that case).
        """
        lines = text.splitlines(keepends=True)
        if not lines:
            return ("none", "", "", text)
        opening = lines[0].rstrip("\r\n").rstrip()
        if opening not in cls.DELIMITERS:
            return ("none", "", "", text)
        for index in range(1, len(lines)):
            candidate = lines[index].rstrip("\r\n").rstrip()
            if candidate == opening:
                block = "".join(lines[1:index])
                body = "".join(lines[index + 1:])
                return ("ok", opening, block, body)
        return ("unterminated", opening, "", text)

    @classmethod
    def _parse_block(cls, delimiter: str, block: str) -> tuple[dict, str]:
        """Parse a front-matter block into ``(mapping, format)``.

        Raises the internal ``_ContentError`` for YAML syntax errors
        (with 1-based line / column), non-mapping YAML results and —
        only for callers that need structured data (``set`` / ``merge``,
        via ``strict_toml=True`` at the call sites below) — unparseable
        TOML. The ``parse`` mode handles the TOML fallback itself.
        """
        if delimiter == "+++":
            try:
                data = tomllib.loads(block)
            except tomllib.TOMLDecodeError as exc:
                raise _ContentError(
                    "invalid_toml_front_matter",
                    "TOML front matter (+++ fence) could not be parsed "
                    f"with tomllib: {exc}",
                ) from exc
            return (data, "toml")

        if not block.strip():
            return ({}, "yaml")
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as exc:
            mark = getattr(exc, "problem_mark", None)
            if mark is None:
                mark = getattr(exc, "context_mark", None)
            if mark is not None:
                line, column = mark.line + 1, mark.column + 1
                location = f" at line {line}, column {column} of the block"
            else:
                line, column = None, None
                location = ""
            raise _ContentError(
                "yaml_parse_error",
                f"front matter is not valid YAML{location}: {exc}",
                line=line,
                column=column,
            ) from exc
        if data is None:
            return ({}, "yaml")
        if not isinstance(data, dict):
            raise _ContentError(
                "front_matter_not_mapping",
                "front matter must parse to a YAML mapping "
                f"(got {type(data).__name__})",
            )
        return (data, "yaml")

    # ------------------------------------------------------------------ #
    # Serialization helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _dump_lines(mapping: dict) -> list:
        """Serialize a mapping to YAML block lines (order preserved)."""
        dumped = yaml.safe_dump(
            mapping,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
            width=1_000_000,
        )
        return dumped.splitlines()

    @staticmethod
    def _assemble(
        delimiter: str, block_lines: list, body: str, newline: str
    ) -> str:
        """Rebuild a markdown text from fence, block lines and body."""
        parts = [delimiter, newline]
        block = newline.join(block_lines)
        if block:
            parts.extend([block, newline])
        parts.extend([delimiter, newline, body])
        return "".join(parts)

    @staticmethod
    def _detect_newline(text: str) -> str:
        """Pick the newline style for reassembly from the input text."""
        return "\r\n" if "\r\n" in text else "\n"

    # ------------------------------------------------------------------ #
    # parse / strip modes
    # ------------------------------------------------------------------ #

    def _run_parse(self, text: str) -> dict[str, Any]:
        """Describe the front matter of ``text`` and return its body."""
        status, delimiter, block, body = self._split_front_matter(text)
        if status == "none":
            return {
                "mode": "parse",
                "has_front_matter": False,
                "delimiters": None,
                "format": None,
                "front_matter": {},
                "body": text,
            }
        if status == "unterminated":
            return self._content_error(
                "parse",
                delimiter,
                "unterminated_front_matter",
                f"front matter opened with {delimiter!r} has no matching "
                "closing fence line",
            )
        if delimiter == "+++":
            try:
                data = tomllib.loads(block)
            except tomllib.TOMLDecodeError as exc:
                return {
                    "mode": "parse",
                    "has_front_matter": True,
                    "delimiters": delimiter,
                    "format": "raw_string",
                    "front_matter": None,
                    "raw_string": block,
                    "reason": (
                        "the +++ block is not valid TOML, so it is "
                        f"reported verbatim: {exc}"
                    ),
                    "body": body,
                }
            return {
                "mode": "parse",
                "has_front_matter": True,
                "delimiters": delimiter,
                "format": "toml",
                "front_matter": data,
                "body": body,
            }
        try:
            data, _ = self._parse_block(delimiter, block)
        except _ContentError as exc:
            return self._content_error(
                "parse", delimiter, exc.error_type, exc.message,
                line=exc.line, column=exc.column,
            )
        return {
            "mode": "parse",
            "has_front_matter": True,
            "delimiters": delimiter,
            "format": "yaml",
            "front_matter": data,
            "body": body,
        }

    def _run_strip(self, text: str) -> dict[str, Any]:
        """Return the body of ``text`` (passthrough without front matter)."""
        status, _, _, body = self._split_front_matter(text)
        return {
            "mode": "strip",
            "has_front_matter": status == "ok",
            "result": body if status == "ok" else text,
        }

    # ------------------------------------------------------------------ #
    # set mode
    # ------------------------------------------------------------------ #

    def _run_set(self, text: str, key: str, value: Any) -> dict[str, Any]:
        """Set one dotted key in the front matter of ``text``."""
        status, delimiter, block, body = self._split_front_matter(text)
        if status == "unterminated":
            return self._content_error(
                "set",
                delimiter,
                "unterminated_front_matter",
                f"front matter opened with {delimiter!r} has no matching "
                "closing fence line",
            )
        if status == "none":
            # No front matter yet: build a fresh --- block on top of the
            # untouched original text.
            front_matter: dict = {}
            delimiter, converted = "---", False
        else:
            try:
                front_matter, _ = self._parse_block(delimiter, block)
            except _ContentError as exc:
                return self._content_error(
                    "set", delimiter, exc.error_type, exc.message,
                    line=exc.line, column=exc.column,
                )
            converted = delimiter == "+++"
            if converted:
                # The stdlib can read TOML but not write it: rewrite the
                # block as YAML, values preserved.
                delimiter = "---"

        try:
            front_matter = self._set_path(front_matter, key, value)
        except _ContentError as exc:
            return self._content_error("set", delimiter, exc.error_type, exc.message)

        newline = self._detect_newline(text)
        top_key = key.split(".")[0]
        replacement = self._dump_lines({top_key: front_matter[top_key]})
        if converted:
            # The +++ block was parsed as TOML: rebuild it wholesale as
            # YAML — TOML key lines (``key = value``) cannot be patched
            # with YAML line matching.
            block_lines = self._dump_lines(front_matter)
        elif status == "none":
            block_lines = list(replacement)
        else:
            block_lines = self._patch_block_lines(block, top_key, replacement)
        result = self._assemble(delimiter, block_lines, body, newline)
        return {
            "mode": "set",
            "key": key,
            "value": value,
            "has_front_matter": True,
            "delimiters": delimiter,
            "converted_delimiters": converted,
            "result": result,
        }

    @classmethod
    def _patch_block_lines(
        cls, block: str, top_key: str, replacement: list
    ) -> list:
        """Line-level patch of one top-level key inside a block.

        An existing key has its lines (the key line plus the indented
        continuation lines that belong to it) replaced by ``replacement``,
        which keeps the order of the other keys and any comment lines
        above the patched key intact. A missing key is appended after
        the last non-blank line of the block.
        """
        lines = block.splitlines()
        index = cls._find_top_level_key(lines, top_key)
        if index is None:
            stripped = list(lines)
            while stripped and not stripped[-1].strip():
                stripped.pop()
            return stripped + list(replacement)
        end = cls._key_block_extent(lines, index)
        return lines[:index] + list(replacement) + lines[end:]

    @staticmethod
    def _find_top_level_key(lines: list, name: str):
        """Return the index of the top-level YAML key line ``name``."""
        for index, line in enumerate(lines):
            match = _TOP_KEY_RE.match(line)
            if match is None:
                continue
            found = match.group(1) or match.group(2) or match.group(3)
            if found == name:
                return index
        return None

    @staticmethod
    def _key_block_extent(lines: list, start: int) -> int:
        """Return the exclusive end of the block owned by ``lines[start]``.

        The block spans the key line plus consecutive lines that are
        indented; a run of blank lines counts only when it is followed
        by another indented line. Column-0 lines (the next key or a
        comment attached to it) end the block.
        """
        end, count = start + 1, len(lines)
        while end < count:
            line = lines[end]
            if not line.strip():
                peek = end + 1
                while peek < count and not lines[peek].strip():
                    peek += 1
                if peek < count and lines[peek][:1] in (" ", "\t"):
                    end = peek
                    continue
                break
            if line[:1] in (" ", "\t"):
                end += 1
                continue
            break
        return end

    @staticmethod
    def _set_path(mapping: dict, key: str, value: Any) -> dict:
        """Set a dotted ``key`` inside a copy of ``mapping``.

        Intermediate mappings are created as needed; an intermediate
        segment that exists but is not a mapping (or an explicit null
        being replaced by a mapping) raises a ``_ContentError``.
        """
        result = dict(mapping)
        cursor = result
        segments = key.split(".")
        for segment in segments[:-1]:
            existing = cursor.get(segment)
            if existing is None:
                child: dict = {}
                cursor[segment] = child
                cursor = child
            elif isinstance(existing, dict):
                child = dict(existing)
                cursor[segment] = child
                cursor = child
            else:
                raise _ContentError(
                    "key_conflict",
                    f"cannot set {key!r}: segment {segment!r} already "
                    f"exists and is a {type(existing).__name__}, not a "
                    "mapping",
                )
        cursor[segments[-1]] = value
        return result

    # ------------------------------------------------------------------ #
    # merge mode
    # ------------------------------------------------------------------ #

    def _run_merge(
        self, text: str, other_text: str, precedence: str
    ) -> dict[str, Any]:
        """Merge front matters; return merged metadata + second body."""
        first, first_error = self._parse_for_merge(text, "text")
        if first_error is not None:
            return first_error
        second, second_error = self._parse_for_merge(other_text, "other_text")
        if second_error is not None:
            return second_error

        if precedence == "second":
            merged = self._deep_merge(first["front_matter"], second["front_matter"])
        else:
            merged = self._deep_merge(second["front_matter"], first["front_matter"])
        has_front_matter = first["has"] or second["has"]
        delimiter = (
            second["delimiter"]
            if second["has"]
            else (first["delimiter"] if first["has"] else None)
        )
        if not has_front_matter:
            result = second["body"]
        else:
            newline = self._detect_newline(other_text)
            # An empty merged mapping yields an empty block, not a "{}" line.
            block_lines = self._dump_lines(merged) if merged else []
            result = self._assemble(delimiter, block_lines, second["body"], newline)
        return {
            "mode": "merge",
            "precedence": precedence,
            "has_front_matter": has_front_matter,
            "delimiters": delimiter,
            "result": result,
        }

    def _parse_for_merge(self, text: str, name: str) -> tuple:
        """Parse one side of a merge into ``(description, error)``.

        ``description`` is ``None`` when ``error`` (a structured error
        payload ready to return) is set.
        """
        status, delimiter, block, body = self._split_front_matter(text)
        if status == "unterminated":
            return (
                None,
                self._content_error(
                    "merge",
                    delimiter,
                    "unterminated_front_matter",
                    f"front matter opened with {delimiter!r} in {name} has "
                    "no matching closing fence line",
                ),
            )
        if status == "none":
            return (
                {
                    "has": False,
                    "delimiter": None,
                    "front_matter": {},
                    "body": body,
                },
                None,
            )
        try:
            data, _ = self._parse_block(delimiter, block)
        except _ContentError as exc:
            return (
                None,
                self._content_error(
                    "merge",
                    delimiter,
                    exc.error_type,
                    exc.message,
                    line=exc.line,
                    column=exc.column,
                ),
            )
        return (
            {"has": True, "delimiter": delimiter, "front_matter": data, "body": body},
            None,
        )

    @staticmethod
    def _deep_merge(base: dict, overlay: dict) -> dict:
        """Recursively merge ``overlay`` over ``base`` (overlay wins)."""
        result = dict(base)
        for key, value in overlay.items():
            existing = result.get(key)
            if isinstance(existing, dict) and isinstance(value, dict):
                result[key] = FrontMatterTool._deep_merge(existing, value)
            else:
                result[key] = value
        return result

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _content_error(
        mode: str,
        delimiter,
        error_type: str,
        message: str,
        line: Any = None,
        column: Any = None,
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        error: dict[str, Any] = {"type": error_type, "message": str(message)[:500]}
        if line is not None:
            error["line"] = line
        if column is not None:
            error["column"] = column
        payload: dict[str, Any] = {"mode": mode, "error": error}
        if delimiter:
            payload["delimiters"] = delimiter
        return payload
