# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Deterministic assembly of structured prompt sections."""

from typing import Any, Dict, List, Optional

from agentuniverse.agent.action.tool.tool import Tool


class StructuredPromptBuilderTool(Tool):
    """Assemble named prompt sections in a stable, auditable order."""

    input_keys: List[str] = ["sections"]

    def execute(
        self,
        sections: Dict[str, str],
        section_order: Optional[List[str]] = None,
        required_sections: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not isinstance(sections, dict):
            return self._error("invalid_sections", "sections must be a mapping")
        if any(not isinstance(key, str) or not key.strip() for key in sections):
            return self._error("invalid_section_name", "section names must be non-empty strings")
        if any(not isinstance(value, str) for value in sections.values()):
            return self._error("invalid_section_content", "section content must be strings")

        order = list(section_order or sections)
        if len(set(order)) != len(order) or any(name not in sections for name in order):
            return self._error("invalid_section_order", "section_order must name supplied sections at most once")
        order.extend(name for name in sections if name not in order)

        required = required_sections or []
        if any(name not in sections for name in required):
            return self._error("invalid_required_section", "required_sections must reference supplied sections")

        included = [name for name in order if sections[name].strip()]
        missing = [name for name in required if not sections[name].strip()]
        blocks = [f"## {self._label(name)}\n{sections[name].strip()}" for name in included]
        result = {
            "valid": not missing,
            "prompt": "\n\n".join(blocks),
            "included_sections": included,
            "missing_sections": missing,
        }
        if missing:
            result["issues"] = [{"code": "empty_required_section", "section": name}
                                for name in missing]
        return result

    @staticmethod
    def _label(name: str) -> str:
        return name.replace("_", " ").strip().title()

    @staticmethod
    def _error(code: str, message: str) -> Dict[str, Any]:
        return {"valid": False, "prompt": "", "issues": [{"code": code, "message": message}]}
