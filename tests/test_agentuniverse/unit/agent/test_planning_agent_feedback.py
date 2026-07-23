from pathlib import Path

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def test_default_english_prompt_uses_peer_review_feedback():
    prompt = (PROJECT_ROOT / "agentuniverse/agent/default/planning_agent/default_en_prompt.yaml").read_text(
        encoding="utf-8"
    )

    assert "{previous_planning_result}" in prompt
    assert "{review_score}" in prompt
    assert "{review_suggestion}" in prompt
    assert "revise" in prompt.lower()


def test_default_chinese_prompt_uses_peer_review_feedback():
    prompt = (PROJECT_ROOT / "agentuniverse/agent/default/planning_agent/default_cn_prompt.yaml").read_text(
        encoding="utf-8"
    )

    assert "{previous_planning_result}" in prompt
    assert "{review_score}" in prompt
    assert "{review_suggestion}" in prompt
    assert "修订" in prompt


def test_parse_input_defaults_feedback_on_first_round():
    agent_input = PlanningAgentTemplate().parse_input(
        InputObject({"input": "analyse the event"}),
        {},
    )

    assert agent_input.get("previous_planning_result") == []
    assert agent_input.get("review_score") == ""
    assert agent_input.get("review_suggestion") == ""


def test_parse_input_exposes_output_object_feedback():
    agent_input = PlanningAgentTemplate().parse_input(
        InputObject(
            {
                "input": "analyse the event",
                "planning_result": OutputObject({"framework": ["first plan"]}),
                "reviewing_result": OutputObject(
                    {
                        "score": 20,
                        "suggestion": "add evidence",
                    }
                ),
            }
        ),
        {},
    )

    assert agent_input.get("previous_planning_result") == ["first plan"]
    assert agent_input.get("review_score") == 20
    assert agent_input.get("review_suggestion") == "add evidence"


def test_parse_input_exposes_dict_feedback_and_preserves_zero_score():
    agent_input = PlanningAgentTemplate().parse_input(
        InputObject(
            {
                "input": "analyse the event",
                "planning_result": {"framework": ["first plan"]},
                "reviewing_result": {
                    "score": 0,
                    "suggestion": "add evidence",
                },
            }
        ),
        {},
    )

    assert agent_input.get("previous_planning_result") == ["first plan"]
    assert agent_input.get("review_score") == 0
    assert agent_input.get("review_suggestion") == "add evidence"


@pytest.mark.parametrize("score", [True, False])
def test_parse_input_defaults_boolean_review_score(score):
    agent_input = PlanningAgentTemplate().parse_input(
        InputObject(
            {
                "input": "analyse the event",
                "reviewing_result": {"score": score},
            }
        ),
        {},
    )

    assert agent_input.get("review_score") == ""


def test_parse_input_defaults_malformed_top_level_feedback():
    agent_input = PlanningAgentTemplate().parse_input(
        InputObject(
            {
                "input": "analyse the event",
                "planning_result": object(),
                "reviewing_result": [],
            }
        ),
        {},
    )

    assert agent_input.get("previous_planning_result") == []
    assert agent_input.get("review_score") == ""
    assert agent_input.get("review_suggestion") == ""


def test_parse_input_defaults_malformed_feedback_fields():
    agent_input = PlanningAgentTemplate().parse_input(
        InputObject(
            {
                "input": "analyse the event",
                "planning_result": {"framework": "first plan"},
                "reviewing_result": {
                    "score": None,
                    "suggestion": ["add evidence"],
                },
            }
        ),
        {},
    )

    assert agent_input.get("previous_planning_result") == []
    assert agent_input.get("review_score") == ""
    assert agent_input.get("review_suggestion") == ""
