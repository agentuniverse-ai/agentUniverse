#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: json_formatter_tool.py

"""
JSON Formatter Tool — beautify, minify, validate, and extract JSON.

A dependency-free JSON utility for agent workflows. The tool wraps the Python
standard library ``json`` module with bounds checking, structured error
reporting, and a small set of operations that cover the common cases where an
agent must clean up, shrink, or sanity-check a JSON payload produced by another
tool, an LLM, or a downstream service.

Operations (``mode``):

- **beautify** — re-serialize JSON with consistent indentation so it is easy
  for a human to read. The indent width is configurable via ``indent``.
- **minify** — remove all optional whitespace to produce the most compact
  representation. Useful before storing or transmitting a payload.
- **validate** — parse the input and report whether it is well-formed JSON.
  The result includes the top-level type and, for objects, the number of
  keys. No output text is produced; this is a pure sanity check.
- **extract** — scan an arbitrary text (for example an LLM response or a log
  line) and return the first balanced JSON value found. Fences and leading
  prose are tolerated. This is handy when a model emits JSON embedded inside
  markdown.

The tool is deliberately strict about input size (``max_input_chars``) and
returns every result as a structured dict so that agents can branch on the
``status`` field rather than parsing free-form text. All exceptions are caught
and converted to ``{"status": "error", ...}`` payloads; the tool never raises.

Addresses #252 (common utility tools).
"""

import json
import re
from typing import Any, List, Optional

from agentuniverse.agent.action.tool.tool import Tool

# Public execute() converts validation/parsing exceptions into structured
# tool responses instead of raising.
# ruff: noqa: TRY003

# Bump this when a new mode is added so callers can feature-detect.
_SUPPORTED_MODES = ("beautify", "minify", "validate", "extract")

# A markdown fence that often wraps model-generated JSON.
_FENCE_RE = re.compile(r"^[\s\S]*?```(?:json|JSON)?\s*\n([\s\S]*?)\n?```", re.MULTILINE)

# Reasonable upper bound. Anything larger almost certainly indicates a caller
# mistake (for example passing a file path instead of contents).
_DEFAULT_MAX_INPUT_CHARS = 100_000
_DEFAULT_INDENT = 2


class JSONFormatterTool(Tool):
    """Beautify, minify, validate, and extract JSON payloads.

    Attributes:
        max_input_chars: Hard limit on the size of the ``input`` string.
            Inputs longer than this are rejected with ``validation_error``.
            Defaults to 100000.
        indent: Number of spaces used by ``beautify``. Must be a positive
            integer. Defaults to 2.
    """

    name: str = "json_formatter_tool"
    description: Optional[str] = (
        "Beautify, minify, validate, and extract JSON payloads using only "
        "the Python standard library."
    )
    input_keys: Optional[List[str]] = ["mode", "input"]

    max_input_chars: int = _DEFAULT_MAX_INPUT_CHARS
    indent: int = _DEFAULT_INDENT

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def execute(self, mode: str, input: str, **_: Any) -> dict:
        """Run a JSON formatting operation.

        Args:
            mode: One of ``beautify``, ``minify``, ``validate``, ``extract``.
            input: The JSON text (or, for ``extract``, text that may contain
                JSON) to process.

        Returns:
            A dict with at least a ``status`` key (``success`` or ``error``).
            Successful ``beautify``/``minify`` results carry an ``output``
            key; ``validate`` carries ``valid`` and ``type`` keys; ``extract``
            carries ``output``, ``start``, and ``end`` keys.
        """
        try:
            self._validate_config()
            operation = self._normalize_mode(mode)
            self._validate_input(input)
            if operation == "beautify":
                return self._beautify(input)
            if operation == "minify":
                return self._minify(input)
            if operation == "validate":
                return self._validate(input)
            return self._extract(input)
        except json.JSONDecodeError as exc:
            # Must precede ValueError — JSONDecodeError subclasses it.
            return self._error(
                "json_error",
                f"Invalid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}",
                mode,
            )
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc), mode)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error("operation_error", f"JSON operation failed: {exc}", mode)

    # ------------------------------------------------------------------
    # Configuration / validation helpers
    # ------------------------------------------------------------------
    def _validate_config(self) -> None:
        for name in ("max_input_chars", "indent"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
            if value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.max_input_chars > 10_000_000:
            raise ValueError("max_input_chars must not exceed 10000000")

    @staticmethod
    def _normalize_mode(mode: Any) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        operation = mode.strip().lower()
        if operation not in _SUPPORTED_MODES:
            raise ValueError(
                "mode must be one of: " + ", ".join(_SUPPORTED_MODES)
            )
        return operation

    def _validate_input(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("input must be a string")
        if len(value) > self.max_input_chars:
            raise ValueError(
                f"input length ({len(value)}) exceeds max_input_chars "
                f"({self.max_input_chars})"
            )

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------
    def _beautify(self, text: str) -> dict:
        """Re-serialize JSON with indentation for readability."""
        data = json.loads(text)
        output = json.dumps(data, indent=self.indent, ensure_ascii=False)
        return {
            "status": "success",
            "mode": "beautify",
            "output": output,
            "input_chars": len(text),
            "output_chars": len(output),
        }

    def _minify(self, text: str) -> dict:
        """Re-serialize JSON with all optional whitespace removed."""
        data = json.loads(text)
        # ``separators`` with trailing commas suppressed produces minimal JSON.
        output = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return {
            "status": "success",
            "mode": "minify",
            "output": output,
            "input_chars": len(text),
            "output_chars": len(output),
        }

    def _validate(self, text: str) -> dict:
        """Check whether ``text`` is well-formed JSON and report its shape."""
        stripped = text.strip()
        if not stripped:
            return {
                "status": "success",
                "mode": "validate",
                "valid": False,
                "type": None,
                "error": "empty input",
            }
        data = json.loads(stripped)
        return {
            "status": "success",
            "mode": "validate",
            "valid": True,
            "type": _classify(data),
            "size": _describe_size(data),
        }

    def _extract(self, text: str) -> dict:
        """Find and return the first balanced JSON value in ``text``.

        Tries, in order: a fenced code block, a direct parse of the whole
        string, and a brace/bracket scan. Returns an error payload if no JSON
        value can be located.
        """
        # 1. Markdown-fenced JSON (```json ... ```).
        match = _FENCE_RE.search(text)
        if match:
            candidate = match.group(1)
            value, start, end = self._try_extract(candidate, match.start(1) - match.start())
            if value is not None:
                return self._extract_success(value, start + match.start(), end + match.start())

        # 2. Whole-string parse (handles strings that are pure JSON).
        whole = self._try_extract(text, 0)
        if whole[0] is not None:
            return self._extract_success(whole[0], whole[1], whole[2])

        # 3. Brace/bracket scan for the first balanced structure.
        for opener in ("{", "["):
            value, start, end = self._scan_balanced(text, opener)
            if value is not None:
                return self._extract_success(value, start, end)

        return self._error(
            "json_error",
            "No JSON value could be extracted from the input.",
            "extract",
        )

    def _try_extract(self, text: str, offset: int):
        """Attempt to parse ``text`` as JSON. Returns (data, start, end) or (None, ...)."""
        try:
            data = json.loads(text.strip())
        except (json.JSONDecodeError, ValueError):
            return None, 0, 0
        start = offset + len(text) - len(text.lstrip())
        end = offset + len(text.rstrip())
        return data, start, end

    @staticmethod
    def _scan_balanced(text: str, opener: str):
        """Scan ``text`` for the first balanced ``{...}`` or ``[...]`` block.

        Performs a lightweight scan that respects string literals and escape
        sequences so that braces inside strings do not break balancing.
        """
        closer = "}" if opener == "{" else "]"
        start = text.find(opener)
        if start == -1:
            return None, 0, 0

        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
                continue
            if char == opener:
                depth += 1
            elif char == closer:
                depth -= 1
                if depth == 0:
                    candidate = text[start : index + 1]
                    try:
                        import json as _json

                        return _json.loads(candidate), start, index + 1
                    except (ValueError, json.JSONDecodeError):
                        return None, 0, 0
        return None, 0, 0

    @staticmethod
    def _extract_success(data: Any, start: int, end: int) -> dict:
        return {
            "status": "success",
            "mode": "extract",
            "output": json.dumps(data, ensure_ascii=False),
            "type": _classify(data),
            "start": start,
            "end": end,
        }

    # ------------------------------------------------------------------
    # Error helper
    # ------------------------------------------------------------------
    @staticmethod
    def _error(kind: str, message: str, mode: Optional[str]) -> dict:
        result: dict = {"status": "error", "error_type": kind, "error": message}
        if mode is not None:
            result["mode"] = mode
        return result


# ----------------------------------------------------------------------
# Module-level helpers
# ----------------------------------------------------------------------
def _classify(value: Any) -> str:
    """Return a human-readable type name for a parsed JSON value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _describe_size(value: Any) -> dict:
    """Return a small summary of the structure's size."""
    if isinstance(value, dict):
        return {"keys": len(value)}
    if isinstance(value, list):
        return {"items": len(value)}
    if isinstance(value, str):
        return {"chars": len(value)}
    return {}
