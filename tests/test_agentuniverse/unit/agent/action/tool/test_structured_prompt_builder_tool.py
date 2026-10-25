# -*- coding:utf-8 -*-

from agentuniverse.agent.action.tool.common_tool.structured_prompt_builder_tool import (
    StructuredPromptBuilderTool,
)


def test_structured_prompt_builder_orders_and_labels_sections():
    result = StructuredPromptBuilderTool().execute(
        sections={"output_format": "Return JSON.", "task": "Summarize."},
        section_order=["task", "output_format"],
        required_sections=["task", "output_format"],
    )

    assert result["valid"] is True
    assert result["prompt"] == "## Task\nSummarize.\n\n## Output Format\nReturn JSON."
    assert result["included_sections"] == ["task", "output_format"]


def test_structured_prompt_builder_omits_empty_optional_sections():
    result = StructuredPromptBuilderTool().execute(
        sections={"task": "Do it.", "context": "", "output": "Done."},
        section_order=["task", "context", "output"],
    )

    assert result["valid"] is True
    assert "Context" not in result["prompt"]
    assert result["missing_sections"] == []


def test_structured_prompt_builder_reports_missing_required_content():
    result = StructuredPromptBuilderTool().execute(
        sections={"task": "", "output": "Return text."},
        required_sections=["task", "output"],
    )

    assert result["valid"] is False
    assert result["missing_sections"] == ["task"]
    assert result["issues"] == [{"code": "empty_required_section", "section": "task"}]
