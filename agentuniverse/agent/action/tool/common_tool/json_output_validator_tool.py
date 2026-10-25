# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Deterministic validation for JSON-shaped model output."""

import json
import re
from typing import Any, Dict, List, Optional

from agentuniverse.agent.action.tool.tool import Tool


class JsonOutputValidatorTool(Tool):
    """Parse and validate JSON output without executing or transforming it."""

    input_keys: List[str] = ["text"]
    _TYPE_NAMES = {"string", "number", "integer", "boolean", "array", "object", "null"}

    def execute(
        self,
        text: str,
        required_keys: Optional[List[str]] = None,
        type_expectations: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        if not isinstance(text, str):
            return self._error("invalid_input", "text must be a string")
        try:
            value = json.loads(
                self._strip_code_fence(text),
                parse_constant=self._reject_non_json_constant,
            )
        except json.JSONDecodeError as exc:
            return self._error(
                "invalid_json", f"Invalid JSON at line {exc.lineno}, column {exc.colno}"
            )
        except ValueError as exc:
            return self._error("invalid_json", f"Invalid JSON: {exc}")
        if not isinstance(value, dict):
            return self._error("expected_object", "JSON output must be an object")

        issues: List[Dict[str, str]] = []
        for key in required_keys or []:
            if not isinstance(key, str) or not key:
                return self._error("invalid_schema", "required_keys must contain non-empty strings")
            if key not in value:
                issues.append({"code": "missing_key", "key": key})

        for key, expected_type in (type_expectations or {}).items():
            if expected_type not in self._TYPE_NAMES:
                return self._error(
                    "invalid_schema",
                    f"Unsupported type expectation for {key}: {expected_type}",
                )
            if key in value and not self._matches_type(value[key], expected_type):
                issues.append({
                    "code": "type_mismatch",
                    "key": key,
                    "expected": expected_type,
                })

        return {
            "valid": not issues,
            "issues": issues,
            "data": value,
        }

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        stripped = text.strip()
        match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else stripped

    @staticmethod
    def _reject_non_json_constant(value: str) -> None:
        raise ValueError(f"non-finite numeric constant is not valid JSON: {value}")

    @staticmethod
    def _matches_type(value: Any, expected_type: str) -> bool:
        if expected_type == "null":
            return value is None
        if expected_type == "boolean":
            return isinstance(value, bool)
        if expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected_type == "string":
            return isinstance(value, str)
        if expected_type == "array":
            return isinstance(value, list)
        if expected_type == "object":
            return isinstance(value, dict)
        return False

    @staticmethod
    def _error(code: str, message: str) -> Dict[str, Any]:
        return {"valid": False, "issues": [{"code": code, "message": message}]}
