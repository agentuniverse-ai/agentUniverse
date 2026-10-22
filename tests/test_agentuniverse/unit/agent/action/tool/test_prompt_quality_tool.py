# -*- coding:utf-8 -*-

import pytest

from agentuniverse.agent.action.tool.common_tool.prompt_quality_tool import (
    PromptQualityTool,
)


def test_prompt_quality_tool_returns_passing_structured_result():
    prompt = """
    # Task
    Summarize the report.

    # Constraints
    Use only the supplied text and do not invent facts.

    # Output
    Return JSON with summary and severity fields.
    """

    result = PromptQualityTool().execute(
        prompt=prompt,
        required_sections=["Task", "Constraints", "Output"],
    )

    assert result["passed"] is True
    assert result["score"] == 100
    assert result["issues"] == []
    assert result["metrics"]["line_count"] == 8
    assert "  " not in result["normalized_prompt"]


def test_prompt_quality_tool_reports_actionable_issues_deterministically():
    result = PromptQualityTool().execute(prompt="Summarize this.")

    assert result["passed"] is False
    assert [issue["code"] for issue in result["issues"]] == [
        "prompt_too_short", "missing_output_contract", "missing_constraints"
    ]
    assert "expected output format" in " ".join(result["suggestions"])
    assert result["normalized_prompt"] == "Summarize this."


def test_prompt_quality_tool_supports_length_and_signal_configuration():
    result = PromptQualityTool().execute(
        prompt="Do this.",
        min_length=1,
        require_output=False,
        require_constraints=False,
    )

    assert result["passed"] is False
    assert [issue["code"] for issue in result["issues"]] == ["missing_task"]


def test_prompt_quality_tool_validates_limits_and_sections():
    with pytest.raises(ValueError, match="cannot exceed"):
        PromptQualityTool().execute(prompt="Task", min_length=10, max_length=5)

    with pytest.raises(ValueError, match="non-empty strings"):
        PromptQualityTool().execute(
            prompt="Task: do it", required_sections=["Task", ""]
        )

    with pytest.raises(TypeError, match="must be a string"):
        PromptQualityTool().execute(prompt=42)
