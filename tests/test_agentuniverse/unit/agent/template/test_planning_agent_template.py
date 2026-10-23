"""Tests for PlanningAgentTemplate.parse_result robustness.

parse_result must not crash when the agent output is empty, malformed, or
missing the expected keys. It previously raised inside parse_json_markdown
for None/malformed output and raised TypeError in enumerate() when the
`framework` key was absent.
"""

from agentuniverse.agent.template.planning_agent_template import (
    PlanningAgentTemplate,
)


def test_parse_result_with_valid_markdown_json():
    template = PlanningAgentTemplate()
    agent_result = {
        "output": '```json\n{"framework": ["step1", "step2"], "thought": "think"}\n```'
    }
    result = template.parse_result(agent_result)
    assert result["framework"] == ["step1", "step2"]
    assert result["thought"] == "think"


def test_parse_result_with_malformed_output_does_not_crash():
    template = PlanningAgentTemplate()
    result = template.parse_result({"output": "not json at all"})
    assert result["framework"] is None
    assert result["thought"] == ""


def test_parse_result_with_none_output_does_not_crash():
    template = PlanningAgentTemplate()
    result = template.parse_result({"output": None})
    assert result["framework"] is None
    assert result["thought"] == ""


def test_parse_result_with_missing_framework_key_does_not_crash():
    template = PlanningAgentTemplate()
    agent_result = {
        "output": '```json\n{"thought": "think only"}\n```'
    }
    result = template.parse_result(agent_result)
    assert result["framework"] is None
    assert result["thought"] == "think only"
