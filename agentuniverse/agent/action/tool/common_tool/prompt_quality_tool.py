# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Offline prompt quality checks for reproducible prompt iteration."""

import re
from typing import Any, Dict, List, Optional

from agentuniverse.agent.action.tool.tool import Tool


class PromptQualityTool(Tool):
    """Score basic prompt structure without calling an external model."""

    input_keys: List[str] = ["prompt"]

    def execute(
        self,
        prompt: str,
        min_length: int = 20,
        max_length: int = 8000,
        required_sections: Optional[List[str]] = None,
        require_output: bool = True,
        require_constraints: bool = True,
    ) -> Dict[str, Any]:
        self._validate_limits(min_length, max_length)
        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        normalized = self._normalize(prompt)
        issues: List[Dict[str, str]] = []
        suggestions: List[str] = []

        if not normalized:
            issues.append(self._issue("empty_prompt", "Prompt is empty."))
        elif len(normalized) < min_length:
            issues.append(self._issue(
                "prompt_too_short",
                f"Prompt is shorter than the configured minimum of {min_length} characters.",
            ))
        if len(normalized) > max_length:
            issues.append(self._issue(
                "prompt_too_long",
                f"Prompt exceeds the configured maximum of {max_length} characters.",
            ))

        if normalized and not self._contains_signal(
                normalized, ("task", "goal", "summarize", "classify", "extract",
                             "analyze", "write", "generate", "create", "要求",
                             "任务", "请")):
            issues.append(self._issue(
                "missing_task", "Prompt does not state an explicit task or goal."
            ))
            suggestions.append("State the task or goal as an action the model must complete.")

        if require_output and not self._contains_signal(
                normalized, ("output", "format", "return", "输出", "格式", "返回")):
            issues.append(self._issue(
                "missing_output_contract",
                "Prompt does not describe the expected output or format.",
            ))
            suggestions.append("Specify the expected output format and required fields.")

        if require_constraints and not self._contains_signal(
                normalized, ("must", "should", "do not", "only", "必须", "不要", "仅")):
            issues.append(self._issue(
                "missing_constraints", "Prompt does not state constraints or boundaries."
            ))
            suggestions.append("Add constraints, exclusions, or a definition of done.")

        for section in required_sections or []:
            if not isinstance(section, str) or not section.strip():
                raise ValueError("required_sections must contain non-empty strings")
            if not self._has_section(normalized, section):
                issues.append(self._issue(
                    "missing_section",
                    f"Prompt is missing the required section '{section}'.",
                ))
                suggestions.append(f"Add a '{section.strip()}' section.")

        score = max(0, 100 - (20 * len(issues)))
        return {
            "passed": not issues,
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
            "normalized_prompt": normalized,
            "metrics": {
                "character_count": len(normalized),
                "line_count": len(normalized.splitlines()) if normalized else 0,
                "required_section_count": len(required_sections or []),
            },
        }

    @staticmethod
    def _normalize(prompt: str) -> str:
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in prompt.splitlines()]
        normalized_lines: List[str] = []
        previous_blank = False
        for line in lines:
            is_blank = not line
            if is_blank and previous_blank:
                continue
            normalized_lines.append(line)
            previous_blank = is_blank
        return "\n".join(normalized_lines).strip()

    @staticmethod
    def _contains_signal(prompt: str, signals: tuple[str, ...]) -> bool:
        lowered = prompt.lower()
        return any(signal.lower() in lowered for signal in signals)

    @staticmethod
    def _has_section(prompt: str, section: str) -> bool:
        pattern = rf"(?im)^\s*#+\s*{re.escape(section.strip())}\s*:?[ \t]*$"
        return re.search(pattern, prompt) is not None

    @staticmethod
    def _issue(code: str, message: str) -> Dict[str, str]:
        return {"code": code, "message": message}

    @staticmethod
    def _validate_limits(min_length: int, max_length: int) -> None:
        if isinstance(min_length, bool) or not isinstance(min_length, int) or min_length < 0:
            raise ValueError("min_length must be a non-negative integer")
        if isinstance(max_length, bool) or not isinstance(max_length, int) or max_length < 1:
            raise ValueError("max_length must be a positive integer")
        if min_length > max_length:
            raise ValueError("min_length cannot exceed max_length")
