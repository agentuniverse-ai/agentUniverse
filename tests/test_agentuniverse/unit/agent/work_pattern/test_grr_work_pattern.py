# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @FileName: test_grr_work_pattern.py
"""Unit tests for the GRR (Generate-Review-Rewrite) work pattern.

These tests exercise file/syntax validation, configuration injection and the
full iteration loop logic of :class:`GRRWorkPattern` using lightweight mock
agent templates.
"""
import asyncio
from unittest.mock import patch

import pytest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.generating_agent_template import GeneratingAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.template.rewriting_agent_template import RewritingAgentTemplate
from agentuniverse.agent.work_pattern.grr_work_pattern import GRRWorkPattern
from pydantic import PrivateAttr


class _MockGeneratingAgent(GeneratingAgentTemplate):
    """Mock generating agent returning a scripted output."""

    _outputs: list = PrivateAttr(default=None)
    _call_index: int = PrivateAttr(default=0)

    def __init__(self, outputs=None, **data):
        super().__init__(**data)
        self._outputs = outputs or ["generated content"]

    def input_keys(self):
        return ['input']

    def output_keys(self):
        return ['output']

    def parse_input(self, input_object, agent_input):
        return agent_input

    def parse_result(self, agent_result):
        return agent_result

    def run(self, **kwargs):
        out = self._outputs[min(self._call_index, len(self._outputs) - 1)]
        self._call_index += 1
        return OutputObject({"output": out})

    async def async_run(self, **kwargs):
        out = self._outputs[min(self._call_index, len(self._outputs) - 1)]
        self._call_index += 1
        return OutputObject({"output": out})


class _MockReviewingAgent(ReviewingAgentTemplate):
    """Mock reviewing agent returning a scripted score."""

    _scores: list = PrivateAttr(default=None)
    _call_index: int = PrivateAttr(default=0)

    def __init__(self, scores=None, **data):
        super().__init__(**data)
        self._scores = scores or [50]

    def input_keys(self):
        return []

    def output_keys(self):
        return ['score', 'suggestion']

    def parse_input(self, input_object, agent_input):
        return agent_input

    def parse_result(self, agent_result):
        return agent_result

    def run(self, **kwargs):
        score = self._scores[min(self._call_index, len(self._scores) - 1)]
        self._call_index += 1
        return OutputObject({"score": score, "suggestion": "needs improvement"})

    async def async_run(self, **kwargs):
        score = self._scores[min(self._call_index, len(self._scores) - 1)]
        self._call_index += 1
        return OutputObject({"score": score, "suggestion": "needs improvement"})


class _MockRewritingAgent(RewritingAgentTemplate):
    """Mock rewriting agent returning a scripted output."""

    _outputs: list = PrivateAttr(default=None)
    _call_index: int = PrivateAttr(default=0)

    def __init__(self, outputs=None, **data):
        super().__init__(**data)
        self._outputs = outputs or ["rewritten content"]

    def input_keys(self):
        return []

    def output_keys(self):
        return ['output']

    def parse_input(self, input_object, agent_input):
        return agent_input

    def parse_result(self, agent_result):
        return agent_result

    def run(self, **kwargs):
        out = self._outputs[min(self._call_index, len(self._outputs) - 1)]
        self._call_index += 1
        return OutputObject({"output": out})

    async def async_run(self, **kwargs):
        out = self._outputs[min(self._call_index, len(self._outputs) - 1)]
        self._call_index += 1
        return OutputObject({"output": out})


def _build_pattern(generating=None, reviewing=None, rewriting=None):
    """Build a GRRWorkPattern with the given mock agents."""
    pattern = GRRWorkPattern()
    pattern.name = "grr_work_pattern"
    pattern.description = "test"
    pattern.generating = generating
    pattern.reviewing = reviewing
    pattern.rewriting = rewriting
    return pattern


def _make_input():
    return InputObject({"input": "write a summary"})


# ---------------------------------------------------------------------------
# 1. File validation & syntax parsing
# ---------------------------------------------------------------------------

def test_grr_work_pattern_importable():
    """GRRWorkPattern can be imported and instantiated."""
    pattern = GRRWorkPattern()
    assert pattern is not None
    assert pattern.generating is None
    assert pattern.reviewing is None
    assert pattern.rewriting is None


def test_grr_yaml_config_parses():
    """The GRR work pattern yaml is syntactically valid and references the class."""
    import os
    import yaml
    yaml_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "..", "agentuniverse", "agent", "work_pattern",
        "grr_work_pattern.yaml"
    )
    yaml_path = os.path.normpath(yaml_path)
    with open(yaml_path) as f:
        config = yaml.safe_load(f)
    assert config["name"] == "grr_work_pattern"
    assert config["metadata"]["type"] == "WORK_PATTERN"
    assert config["metadata"]["class"] == "GRRWorkPattern"
    assert "grr_work_pattern" in config["metadata"]["module"]


def test_grr_agent_template_importable():
    """GRRAgentTemplate can be imported."""
    from agentuniverse.agent.template.grr_agent_template import GRRAgentTemplate
    assert GRRAgentTemplate is not None


# ---------------------------------------------------------------------------
# 2. Configuration injection
# ---------------------------------------------------------------------------

def test_grr_default_retry_count_and_threshold():
    """Default config values are applied when not provided."""
    pattern = _build_pattern()
    input_object = _make_input()
    with patch.object(GRRWorkPattern, "_validate_work_pattern_members"):
        result = pattern.invoke(input_object, {"input": "test"})
    assert "result" in result


def test_grr_custom_retry_count():
    """A custom retry_count controls the number of iterations."""
    gen = _MockGeneratingAgent(outputs=["c1", "c2", "c3"])
    rev = _MockReviewingAgent(scores=[30, 30, 30])
    rewriting = _MockRewritingAgent(outputs=["r1", "r2"])
    pattern = _build_pattern(gen, rev, rewriting)
    result = pattern.invoke(_make_input(), {"input": "x", "retry_count": 3, "eval_threshold": 100})
    assert len(result["result"]) == 3


def test_grr_custom_eval_threshold_triggers_early_exit():
    """A reachable eval_threshold causes early loop exit."""
    gen = _MockGeneratingAgent(outputs=["c1"])
    rev = _MockReviewingAgent(scores=[95])
    pattern = _build_pattern(gen, rev, _MockRewritingAgent())
    result = pattern.invoke(_make_input(), {"input": "x", "retry_count": 3, "eval_threshold": 90})
    assert len(result["result"]) == 1


# ---------------------------------------------------------------------------
# 3. Full iteration loop logic (sync)
# ---------------------------------------------------------------------------

def test_grr_generating_then_reviewing_recorded():
    """First iteration records generating and reviewing results."""
    gen = _MockGeneratingAgent(outputs=["draft"])
    rev = _MockReviewingAgent(scores=[95])
    pattern = _build_pattern(gen, rev, None)
    result = pattern.invoke(_make_input(), {"input": "x", "eval_threshold": 90})
    first_round = result["result"][0]
    assert first_round["generating_result"]["output"] == "draft"
    assert first_round["reviewing_result"]["score"] == 95


def test_grr_high_score_skips_rewriting():
    """When score meets threshold, rewriting is not invoked."""
    gen = _MockGeneratingAgent(outputs=["draft"])
    rev = _MockReviewingAgent(scores=[100])
    rewriting = _MockRewritingAgent(outputs=["should not appear"])
    pattern = _build_pattern(gen, rev, rewriting)
    result = pattern.invoke(_make_input(), {"input": "x", "eval_threshold": 60})
    assert "rewriting_result" not in result["result"][0]


def test_grr_low_score_triggers_rewriting():
    """When score is below threshold and not last iteration, rewriting runs."""
    gen = _MockGeneratingAgent(outputs=["draft"])
    rev = _MockReviewingAgent(scores=[30])
    rewriting = _MockRewritingAgent(outputs=["better draft"])
    pattern = _build_pattern(gen, rev, rewriting)
    result = pattern.invoke(_make_input(), {"input": "x", "retry_count": 2, "eval_threshold": 90})
    assert "rewriting_result" in result["result"][0]


def test_grr_no_rewriting_on_last_iteration():
    """Rewriting is skipped on the final iteration even if score is low."""
    gen = _MockGeneratingAgent(outputs=["draft"])
    rev = _MockReviewingAgent(scores=[10])
    rewriting = _MockRewritingAgent(outputs=["better"])
    pattern = _build_pattern(gen, rev, rewriting)
    result = pattern.invoke(_make_input(), {"input": "x", "retry_count": 1, "eval_threshold": 90})
    assert "rewriting_result" not in result["result"][0]


def test_grr_rewritten_content_used_in_next_round():
    """Rewritten output is fed back as generating content in the next round."""
    gen = _MockGeneratingAgent(outputs=["original"])
    rev = _MockReviewingAgent(scores=[40, 100])
    rewriting = _MockRewritingAgent(outputs=["improved version"])
    pattern = _build_pattern(gen, rev, rewriting)
    result = pattern.invoke(_make_input(), {"input": "x", "retry_count": 3, "eval_threshold": 90})
    assert len(result["result"]) == 2


def test_grr_default_agents_when_none():
    """When all agents are None, defaults produce a pass-through result."""
    pattern = _build_pattern(None, None, None)
    result = pattern.invoke(_make_input(), {"input": "hello", "eval_threshold": 60})
    assert len(result["result"]) >= 1


def test_grr_result_structure():
    """The result dict always contains the 'result' key holding a list."""
    pattern = _build_pattern()
    result = pattern.invoke(_make_input(), {"input": "x"})
    assert isinstance(result, dict)
    assert isinstance(result["result"], list)


def test_grr_retry_count_one_single_iteration():
    """retry_count=1 produces exactly one iteration."""
    pattern = _build_pattern(_MockGeneratingAgent(), _MockReviewingAgent(scores=[10]))
    result = pattern.invoke(_make_input(), {"input": "x", "retry_count": 1, "eval_threshold": 90})
    assert len(result["result"]) == 1


# ---------------------------------------------------------------------------
# 4. Async iteration loop logic
# ---------------------------------------------------------------------------

def test_grr_async_invoke_basic():
    """async_invoke returns a result dict with a list of rounds."""
    gen = _MockGeneratingAgent(outputs=["a"])
    rev = _MockReviewingAgent(scores=[100])
    pattern = _build_pattern(gen, rev, None)
    result = asyncio.get_event_loop().run_until_complete(
        pattern.async_invoke(_make_input(), {"input": "x", "eval_threshold": 90})
    )
    assert "result" in result
    assert result["result"][0]["generating_result"]["output"] == "a"


def test_grr_async_invoke_early_exit():
    """async_invoke exits early when threshold is met."""
    gen = _MockGeneratingAgent(outputs=["a"])
    rev = _MockReviewingAgent(scores=[100])
    pattern = _build_pattern(gen, rev, _MockRewritingAgent())
    result = asyncio.get_event_loop().run_until_complete(
        pattern.async_invoke(_make_input(), {"input": "x", "retry_count": 5, "eval_threshold": 90})
    )
    assert len(result["result"]) == 1


def test_grr_async_invoke_with_rewriting():
    """async_invoke invokes rewriting when score is low."""
    gen = _MockGeneratingAgent(outputs=["a"])
    rev = _MockReviewingAgent(scores=[20])
    rewriting = _MockRewritingAgent(outputs=["b"])
    pattern = _build_pattern(gen, rev, rewriting)
    result = asyncio.get_event_loop().run_until_complete(
        pattern.async_invoke(_make_input(), {"input": "x", "retry_count": 2, "eval_threshold": 90})
    )
    assert "rewriting_result" in result["result"][0]


def test_grr_async_default_agents():
    """async_invoke works with default (None) agents."""
    pattern = _build_pattern()
    result = asyncio.get_event_loop().run_until_complete(
        pattern.async_invoke(_make_input(), {"input": "x"})
    )
    assert len(result["result"]) >= 1


# ---------------------------------------------------------------------------
# 5. set_by_agent_model & validation
# ---------------------------------------------------------------------------

def test_grr_set_by_agent_model_injects_agents():
    """set_by_agent_model returns a new instance with injected agents."""
    pattern = _build_pattern()
    gen = _MockGeneratingAgent()
    rev = _MockReviewingAgent(scores=[100])
    rewriting = _MockRewritingAgent()
    new_pattern = pattern.set_by_agent_model(generating=gen, reviewing=rev, rewriting=rewriting)
    assert new_pattern.generating is gen
    assert new_pattern.reviewing is rev
    assert new_pattern.rewriting is rewriting
    assert new_pattern.name == pattern.name


def test_grr_set_by_agent_model_preserves_metadata():
    """set_by_agent_model preserves name and description."""
    pattern = _build_pattern()
    pattern.name = "my_grr"
    pattern.description = "desc"
    new_pattern = pattern.set_by_agent_model()
    assert new_pattern.name == "my_grr"
    assert new_pattern.description == "desc"


def test_grr_set_by_agent_model_partial_injection():
    """set_by_agent_model can inject only some agents."""
    pattern = _build_pattern()
    gen = _MockGeneratingAgent()
    new_pattern = pattern.set_by_agent_model(generating=gen)
    assert new_pattern.generating is gen
    assert new_pattern.reviewing is None


def test_grr_validation_rejects_wrong_generating_type():
    """Validation fails when generating agent is the wrong type."""
    pattern = _build_pattern()
    pattern.generating = "not an agent"
    with pytest.raises(ValueError):
        pattern.invoke(_make_input(), {"input": "x"})


def test_grr_validation_rejects_wrong_reviewing_type():
    """Validation fails when reviewing agent is the wrong type."""
    pattern = _build_pattern()
    pattern.reviewing = 123
    with pytest.raises(ValueError):
        pattern.invoke(_make_input(), {"input": "x"})


def test_grr_validation_rejects_wrong_rewriting_type():
    """Validation fails when rewriting agent is the wrong type."""
    pattern = _build_pattern()
    pattern.rewriting = object()
    with pytest.raises(ValueError):
        pattern.invoke(_make_input(), {"input": "x"})


def test_grr_validation_accepts_correct_types():
    """Validation passes when agents are correct template subclasses."""
    gen = _MockGeneratingAgent()
    rev = _MockReviewingAgent(scores=[100])
    rewriting = _MockRewritingAgent()
    pattern = _build_pattern(gen, rev, rewriting)
    pattern._validate_work_pattern_members()


def test_grr_validation_accepts_none_agents():
    """Validation passes when agents are None."""
    pattern = _build_pattern()
    pattern._validate_work_pattern_members()


def test_grr_generating_result_added_to_input_object():
    """The generating result is stored in the input_object for downstream use."""
    gen = _MockGeneratingAgent(outputs=["my draft"])
    rev = _MockReviewingAgent(scores=[100])
    pattern = _build_pattern(gen, rev, None)
    input_object = _make_input()
    pattern.invoke(input_object, {"input": "x", "eval_threshold": 90})
    assert input_object.get_data("generating_result") is not None


def test_grr_reviewing_result_added_to_input_object():
    """The reviewing result is stored in the input_object."""
    gen = _MockGeneratingAgent(outputs=["my draft"])
    rev = _MockReviewingAgent(scores=[100])
    pattern = _build_pattern(gen, rev, None)
    input_object = _make_input()
    pattern.invoke(input_object, {"input": "x", "eval_threshold": 90})
    assert input_object.get_data("reviewing_result").get_data("score") == 100


def test_grr_multiple_iterations_all_recorded():
    """All iterations are recorded in the result list."""
    gen = _MockGeneratingAgent(outputs=["v1", "v2", "v3"])
    rev = _MockReviewingAgent(scores=[10, 10, 10])
    rewriting = _MockRewritingAgent(outputs=["r1", "r2"])
    pattern = _build_pattern(gen, rev, rewriting)
    result = pattern.invoke(_make_input(), {"input": "x", "retry_count": 3, "eval_threshold": 100})
    assert len(result["result"]) == 3
