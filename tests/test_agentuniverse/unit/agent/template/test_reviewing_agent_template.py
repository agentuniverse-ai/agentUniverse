"""Tests for reviewing-agent result parsing."""

import pytest

from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate


@pytest.mark.parametrize(
    ("value", "expected_score"),
    [("false", 0), ("False", 0), ("true", 80), ("YES", 80)],
)
def test_parse_result_normalizes_string_booleans(value, expected_score):
    template = ReviewingAgentTemplate()

    result = template.parse_result(
        {"output": f'{{"is_useful": "{value}", "suggestion": "review"}}'}
    )

    assert result["score"] == expected_score
