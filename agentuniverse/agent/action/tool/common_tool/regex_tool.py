#!/usr/bin/env python3
"""Regex pattern matching tool.

Provides match, extract, replace, and split operations using Python's
built-in ``re`` module. Zero third-party dependency. Bounded: max matches
returned, max input length enforced. Addresses #252.
"""

# ruff: noqa: TRY003, TRY004

import logging
import re
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class RegexTool(Tool):
    """Regex operations tool: match, extract, replace, split.

    Attributes:
        max_input_chars: Maximum input text length (default 100_000).
        max_matches: Maximum number of matches returned (default 1000).
    """

    max_input_chars: int = 100_000
    max_matches: int = 1000

    def execute(self, mode: str, pattern: str = "", text: str = "",
                replacement: str = "", flags: str = "",
                **kwargs) -> dict:
        try:
            op = self._normalize_mode(mode)
            if not pattern:
                return self._error("validation_error", "pattern is required")
            if not isinstance(text, str):
                return self._error("validation_error", "text must be a string")
            if len(text) > self.max_input_chars:
                return self._error("validation_error",
                                   f"Input exceeds max_input_chars ({self.max_input_chars})")

            re_flags = self._parse_flags(flags)
            try:
                compiled = re.compile(pattern, re_flags)
            except re.error as exc:
                return self._error("validation_error",
                                   f"Invalid regex pattern: {exc}")

            if op == "match":
                return self._match(compiled, text)
            if op == "extract":
                return self._extract(compiled, text)
            if op == "replace":
                return self._replace(compiled, text, replacement)
            if op == "split":
                return self._split(compiled, text)
            return self._error("validation_error", f"Unknown mode: {mode}")
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:
            return self._error("operation_error", str(exc))

    @staticmethod
    def _normalize_mode(mode: str) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        normalized = mode.strip().lower()
        allowed = {"match", "extract", "replace", "split"}
        if normalized not in allowed:
            raise ValueError(f"mode must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @staticmethod
    def _parse_flags(flags_str: str) -> int:
        flags_map = {
            "i": re.IGNORECASE,
            "m": re.MULTILINE,
            "s": re.DOTALL,
            "x": re.VERBOSE,
            "a": re.ASCII,
        }
        result = 0
        for char in (flags_str or "").lower():
            result |= flags_map.get(char, 0)
        return result

    @staticmethod
    def _error(error_type: str, message: str) -> dict:
        return {"status": "error", "error_type": error_type, "error": message}

    @staticmethod
    def _ok(**kwargs) -> dict:
        return {"status": "success", **kwargs}

    def _match(self, compiled: re.Pattern, text: str) -> dict:
        m = compiled.search(text)
        if m is None:
            return self._ok(mode="match", matched=False)
        groups = [g if g is not None else "" for g in m.groups()]
        return self._ok(
            mode="match", matched=True,
            match=m.group(0),
            start=m.start(), end=m.end(),
            groups=groups,
        )

    def _extract(self, compiled: re.Pattern, text: str) -> dict:
        matches = []
        for i, m in enumerate(compiled.finditer(text)):
            if i >= self.max_matches:
                break
            matches.append({
                "match": m.group(0),
                "start": m.start(),
                "end": m.end(),
                "groups": [g if g is not None else "" for g in m.groups()],
            })
        return self._ok(
            mode="extract",
            matches=matches,
            count=len(matches),
            truncated=len(matches) >= self.max_matches,
        )

    def _replace(self, compiled: re.Pattern, text: str,
                 replacement: str) -> dict:
        count_before = len(compiled.findall(text))
        result = compiled.sub(replacement, text)
        return self._ok(
            mode="replace",
            result=result,
            replacements_made=count_before,
        )

    def _split(self, compiled: re.Pattern, text: str) -> dict:
        parts = compiled.split(text)
        return self._ok(mode="split", parts=parts, count=len(parts))

    def _initialize_by_component_configer(self, configer: ComponentConfiger) \
            -> "RegexTool":
        super()._initialize_by_component_configer(configer)
        if hasattr(configer, "max_input_chars"):
            self.max_input_chars = configer.max_input_chars
        if hasattr(configer, "max_matches"):
            self.max_matches = configer.max_matches
        return self
