#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: json_yaml_tool.py

"""JSON <-> YAML conversion tool built on the framework's PyYAML dependency.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network format converter agents can call
whenever a payload has to cross the JSON/YAML boundary: preparing
configuration from API responses, embedding YAML data in JSON-based
orchestration payloads, or sanity-checking YAML before it is handed to
a human.

The tool wraps the standard library ``json`` module and PyYAML —
already a core framework dependency (``agentuniverse.base.config.configer``
imports it to parse every component configuration file) — and supports
three modes:

* ``to_yaml`` — parse JSON text and dump it as block-style YAML
  (``default_flow_style=False``) with ``allow_unicode=True`` so CJK
  and other non-ASCII text stays human-readable instead of being
  escaped. An optional ``sort_keys`` flag sorts mapping keys in the
  output.
* ``to_json`` — parse YAML text and dump it as JSON with an optional
  ``indent`` (default 2) and ``sort_keys`` flag. Non-ASCII characters
  are emitted literally (``ensure_ascii=False``), mirroring the
  ``allow_unicode`` behavior of the opposite direction.
* ``validate_yaml`` — parse YAML text and report the type of the root
  node plus its top-level key count (and item count for sequences),
  or a structured error with the 1-based line and column of the
  offending mark.

Security: every YAML parse goes through ``yaml.safe_load`` /
``yaml.safe_load_all`` — never ``yaml.load`` — so untrusted input can
never trigger arbitrary Python object construction. Anchors and merge
keys (``<<:``) are expanded to plain data by the safe resolver.
Multi-document streams (``---`` separators) are rejected with a clear
error instead of silently dropping all but the first document.

Round-trip guarantees:

* ``json -> yaml -> json`` is value-stable for any JSON input, because
  every JSON value (object / array / string / number / boolean /
  null) has a faithful YAML representation.
* ``yaml -> json -> yaml`` is value-stable for mappings, sequences and
  the scalar types JSON can represent (string / integer / float /
  boolean / null). Two caveats:

  1. Date and timestamp scalars: ``safe_load`` resolves unquoted ISO
     8601 scalars such as ``2024-01-15`` to ``datetime.date`` (and
     timestamps to ``datetime.datetime``), types JSON has no literal
     for. They are serialized explicitly as ISO 8601 strings via a
     ``json.dumps`` ``default`` hook (``isoformat()``, falling back to
     ``str`` for any other exotic value), so the data is preserved but
     a date round-trips into a *quoted* string rather than a bare
     date scalar.
  2. Non-string mapping keys (YAML allows integers, booleans or
     complex keys) are coerced by JSON to strings — ``{1: a}``
     becomes ``{"1": "a"}`` — and complex keys (e.g. ``? [one, two]``)
     or self-referencing aliases make the document unrepresentable in
     JSON, which is reported as a structured ``unsupported_type``
     error.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty or whitespace-only text,
unknown mode, non-boolean ``sort_keys``, non-integer or out-of-range
``indent``, text longer than the 1 MiB / 1,048,576-character cap)
raise a ``ValueError``, mirroring the other common tools. Errors that
depend on the *content being processed* — invalid JSON (reported with
line / column / character offset), YAML syntax errors (reported with
the 1-based line and column of the error mark), multi-document
streams, over-deep nesting and JSON-unrepresentable structures — are
returned as a structured ``error`` payload so an agent can react
without catching exceptions.
"""

from __future__ import annotations

import datetime
import json
from typing import Any, ClassVar, Dict, Optional, Tuple

import yaml
from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


def _json_default(obj: Any) -> str:
    """``json.dumps`` hook for values JSON has no literal for.

    ``yaml.safe_load`` resolves unquoted ISO 8601 date / timestamp
    scalars to ``datetime.date`` / ``datetime.datetime`` objects; they
    are serialized as ISO 8601 strings (``date.isoformat()``). Any
    other non-JSON value falls back to ``str(obj)``.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)


class JsonYamlTool(Tool):
    """JSON <-> YAML converter tool built on the framework's PyYAML dependency.

    Attributes:
        max_input_chars (int): Upper bound on the ``text`` input length
            (1 MiB measured in characters); longer inputs are rejected
            before any computation.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "json_yaml_tool"
    description: str = (
        "JSON/YAML conversion tool — offline, built on the framework's "
        "PyYAML dependency and yaml.safe_load only. Convert JSON text to "
        "block-style YAML with allow_unicode=True and an optional "
        "sort_keys flag (mode='to_yaml'), convert YAML text to JSON with "
        "optional indent and sort_keys (mode='to_json'), or validate YAML "
        "and report the root type and key count with 1-based line/column "
        "error marks (mode='validate_yaml')."
    )

    MODES: ClassVar[tuple] = ("to_yaml", "to_json", "validate_yaml")
    MAX_INDENT: ClassVar[int] = 10

    max_input_chars: int = 1_048_576

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        sort_keys: Any = None,
        indent: Any = None,
    ) -> Dict[str, Any]:
        """Run one JSON/YAML conversion.

        Args:
            mode (str): One of ``to_yaml`` / ``to_json`` /
                ``validate_yaml``.
            text (str): The JSON text (``to_yaml``) or YAML text
                (``to_json`` / ``validate_yaml``) to process. Required;
                must be a non-empty string after stripping whitespace
                and at most 1,048,576 characters long.
            sort_keys (bool): Sort mapping keys in the output. Applied
                by ``to_yaml`` and ``to_json``; type-checked in every
                mode and ignored by ``validate_yaml``. Defaults to
                ``False`` (preserve insertion order).
            indent (int): JSON indentation width for ``to_json`` — an
                integer between 0 and 10, defaulting to 2. Type-checked
                in every mode; ignored by ``to_yaml`` and
                ``validate_yaml``.

        Returns:
            Dict[str, Any]: The conversion result (always a ``result``
                string plus the call context for the conversion modes,
                or ``valid`` / ``root_type`` / ``key_count`` /
                ``item_count`` for ``validate_yaml``) or a structured
                ``error`` payload for content-level failures (invalid
                JSON with position, YAML syntax errors with line and
                column, multi-document streams, over-deep nesting,
                JSON-unrepresentable structures).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        clean_sort_keys = self._validate_sort_keys(sort_keys)
        clean_indent = self._validate_indent(indent)
        if mode == "to_yaml":
            return self._run_to_yaml(clean_text, clean_sort_keys)
        if mode == "to_json":
            return self._run_to_json(clean_text, clean_sort_keys, clean_indent)
        return self._run_validate_yaml(clean_text)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"json_yaml_tool: {message}")

    def _validate_text(self, text: Any) -> str:
        """Validate the ``text`` input (non-empty string within the cap)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a non-empty string (got {text!r})")
        if text == "":
            self._invalid("text must be a non-empty string (got '')")
        if not text.strip():
            self._invalid("text must contain more than whitespace")
        if len(text) > self.max_input_chars:
            self._invalid(
                f"text exceeds the {self.max_input_chars:,}-character "
                f"limit (got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_sort_keys(cls, sort_keys: Any) -> bool:
        """Validate the optional ``sort_keys`` flag (default ``False``)."""
        if sort_keys is None:
            return False
        if isinstance(sort_keys, bool):
            return sort_keys
        cls._invalid(f"sort_keys must be a boolean or None (got {sort_keys!r})")

    @classmethod
    def _validate_indent(cls, indent: Any) -> int:
        """Validate the optional ``indent`` width (default 2, range 0-10)."""
        if indent is None:
            return 2
        if isinstance(indent, bool) or not isinstance(indent, int):
            cls._invalid(
                f"indent must be an integer between 0 and {cls.MAX_INDENT} "
                f"or None (got {indent!r})"
            )
        if not 0 <= indent <= cls.MAX_INDENT:
            cls._invalid(
                f"indent must be an integer between 0 and {cls.MAX_INDENT} "
                f"(got {indent})"
            )
        return indent

    # ------------------------------------------------------------------ #
    # to_yaml mode
    # ------------------------------------------------------------------ #

    def _run_to_yaml(self, text: str, sort_keys: bool) -> Dict[str, Any]:
        """Parse JSON text and dump it as block-style YAML."""
        context = {"mode": "to_yaml", "sort_keys": sort_keys}
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            detail = {
                "type": "invalid_json",
                "message": (
                    f"{exc.msg} (line {exc.lineno}, column {exc.colno}, "
                    f"character offset {exc.pos})"
                ),
                "line": exc.lineno,
                "column": exc.colno,
                "position": exc.pos,
            }
            return {**context, "error": detail}
        except RecursionError:
            return {**context, "error": self._too_deep_detail()}
        # json.loads only produces dict / list / str / int / float /
        # bool / None — all natively representable by yaml.safe_dump.
        result = yaml.safe_dump(
            data,
            sort_keys=sort_keys,
            default_flow_style=False,
            allow_unicode=True,
        )
        return {**context, "result": result}

    # ------------------------------------------------------------------ #
    # YAML parsing core (shared by to_json and validate_yaml)
    # ------------------------------------------------------------------ #

    def _parse_single_yaml(self, text: str) -> Tuple[Any, Optional[Dict[str, Any]]]:
        """Parse exactly one YAML document with ``safe_load`` semantics.

        Returns a ``(data, error_detail)`` tuple; exactly one element
        is ``None``. Multi-document streams are rejected so no document
        is ever silently dropped.
        """
        try:
            documents = list(yaml.safe_load_all(text))
        except yaml.YAMLError as exc:
            return None, self._yaml_error_detail(exc)
        except RecursionError:
            return None, self._too_deep_detail()
        if len(documents) > 1:
            return None, {
                "type": "multi_document_yaml",
                "message": (
                    f"YAML input contains {len(documents)} documents "
                    "separated by '---' markers; exactly one document is "
                    "required — split the input and convert each document "
                    "separately"
                ),
            }
        # An empty stream (e.g. a comment-only document) yields no
        # documents; that is represented as a null root value.
        return (documents[0] if documents else None), None

    @staticmethod
    def _yaml_error_detail(exc: yaml.YAMLError) -> Dict[str, Any]:
        """Build the structured detail for a YAML parse error.

        The 1-based line and column are taken from the error mark when
        PyYAML provides one (``error_mark`` / ``problem_mark`` /
        ``context_mark``, in that order of preference).
        """
        mark = (
            getattr(exc, "error_mark", None)
            or getattr(exc, "problem_mark", None)
            or getattr(exc, "context_mark", None)
        )
        message = getattr(exc, "problem", None) or str(exc)
        detail: Dict[str, Any] = {"type": "yaml_error"}
        if mark is not None:
            detail["line"] = mark.line + 1
            detail["column"] = mark.column + 1
            message = f"{message} (line {mark.line + 1}, column {mark.column + 1})"
        detail["message"] = str(message)[:500]
        return detail

    @staticmethod
    def _too_deep_detail() -> Dict[str, Any]:
        """Build the structured detail for over-deep nesting."""
        return {
            "type": "too_deeply_nested",
            "message": (
                "input nesting is too deep to be processed within the "
                "interpreter recursion limit"
            ),
        }

    # ------------------------------------------------------------------ #
    # to_json mode
    # ------------------------------------------------------------------ #

    def _run_to_json(
        self, text: str, sort_keys: bool, indent: int
    ) -> Dict[str, Any]:
        """Parse YAML text and dump it as JSON."""
        context = {
            "mode": "to_json",
            "indent": indent,
            "sort_keys": sort_keys,
        }
        data, error = self._parse_single_yaml(text)
        if error is not None:
            return {**context, "error": error}
        try:
            result = json.dumps(
                data,
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=False,
                default=_json_default,
            )
        except (TypeError, ValueError) as exc:
            return {**context, "error": {
                "type": "unsupported_type",
                "message": (
                    "the YAML document contains a structure JSON cannot "
                    f"represent ({exc}); typical causes are complex mapping "
                    "keys, sets, bytes or self-referencing aliases"
                ),
            }}
        return {**context, "result": result}

    # ------------------------------------------------------------------ #
    # validate_yaml mode
    # ------------------------------------------------------------------ #

    def _run_validate_yaml(self, text: str) -> Dict[str, Any]:
        """Parse YAML text and report the root type and key count."""
        context = {"mode": "validate_yaml"}
        data, error = self._parse_single_yaml(text)
        if error is not None:
            return {**context, "valid": False, "error": error}
        result: Dict[str, Any] = {
            **context,
            "valid": True,
            "root_type": self._root_type_name(data),
            "key_count": len(data) if isinstance(data, dict) else 0,
        }
        if isinstance(data, list):
            result["item_count"] = len(data)
        return result

    @staticmethod
    def _root_type_name(value: Any) -> str:
        """Name the type of a parsed YAML root node."""
        if isinstance(value, bool):  # before int — bool is an int subclass
            return "boolean"
        if isinstance(value, dict):
            return "mapping"
        if isinstance(value, list):
            return "sequence"
        if value is None:
            return "null"
        if isinstance(value, str):
            return "string"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "float"
        if isinstance(value, datetime.datetime):  # before date — subclass
            return "datetime"
        if isinstance(value, datetime.date):
            return "date"
        if isinstance(value, bytes):
            return "bytes"
        if isinstance(value, set):
            return "set"
        return type(value).__name__
