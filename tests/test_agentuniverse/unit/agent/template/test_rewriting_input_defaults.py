#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.rewriting_agent_template import (
    RewritingAgentTemplate,
)


def test_parse_input_populates_prompt_fields_without_prior_results():
    template = RewritingAgentTemplate()
    result = template.parse_input(
        InputObject({"input": "draft", "expert_framework": None}), {}
    )

    assert result == {
        "input": "draft",
        "generated_content": "",
        "review_score": 0,
        "review_suggestion": "",
        "review_output": "",
        "expert_framework": "",
    }
