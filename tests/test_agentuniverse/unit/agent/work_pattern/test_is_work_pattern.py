# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @FileName: test_is_work_pattern.py
"""Unit tests for the IS (Implementation-Supervision) work pattern.

These tests cover file/syntax validation, configuration injection and the full
checkpoint/correction loop logic of :class:`ISWorkPattern`.
"""
import asyncio
import os

import pytest
import yaml

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.implementation_agent_template import ImplementationAgentTemplate
from agentuniverse.agent.template.supervision_agent_template import SupervisionAgentTemplate
from agentuniverse.agent.work_pattern.is_work_pattern import ISWorkPattern
from pydantic import PrivateAttr


class _MockImplementationAgent(ImplementationAgentTemplate):
    """Mock implementation agent returning a scripted output."""

    _outputs: list = PrivateAttr(default=None)
    _call_index: int = PrivateAttr(default=0)

    def __init__(self, outputs=None, **data):
        super().__init__(**data)
        self._outputs = outputs or ["implementation output"]

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


class _MockSupervisionAgent(SupervisionAgentTemplate):
    """Mock supervision agent returning scripted correction flags."""

    _flags: list = PrivateAttr(default=None)
    _call_index: int = PrivateAttr(default=0)
    _feedback: str = PrivateAttr(default="needs fix")

    def __init__(self, correction_flags=None, feedback="needs fix", **data):
        super().__init__(**data)
        self._flags = correction_flags or [False]
        self._feedback = feedback

    def input_keys(self):
        return []

    def output_keys(self):
        return ['needs_correction', 'feedback']

    def parse_input(self, input_object, agent_input):
        return agent_input

    def parse_result(self, agent_result):
        return agent_result

    def run(self, **kwargs):
        flag = self._flags[min(self._call_index, len(self._flags) - 1)]
        self._call_index += 1
        return OutputObject({"needs_correction": flag, "feedback": self._feedback})

    async def async_run(self, **kwargs):
        flag = self._flags[min(self._call_index, len(self._flags) - 1)]
        self._call_index += 1
        return OutputObject({"needs_correction": flag, "feedback": self._feedback})


def _build_pattern(implementation=None, supervision=None):
    """Build an ISWorkPattern with the given mock agents."""
    pattern = ISWorkPattern()
    pattern.name = "is_work_pattern"
    pattern.description = "test"
    pattern.implementation = implementation
    pattern.supervision = supervision
    return pattern


def _make_input():
    return InputObject({"input": "execute task"})


# ---------------------------------------------------------------------------
# 1. File validation & syntax parsing
# ---------------------------------------------------------------------------

def test_is_work_pattern_importable():
    """ISWorkPattern can be imported and instantiated."""
    pattern = ISWorkPattern()
    assert pattern is not None
    assert pattern.implementation is None
    assert pattern.supervision is None


def test_is_yaml_config_parses():
    """The IS work pattern yaml is valid and references the class."""
    yaml_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "..", "agentuniverse", "agent", "work_pattern",
        "is_work_pattern.yaml"
    ))
    with open(yaml_path) as f:
        config = yaml.safe_load(f)
    assert config["name"] == "is_work_pattern"
    assert config["metadata"]["type"] == "WORK_PATTERN"
    assert config["metadata"]["class"] == "ISWorkPattern"


def test_is_agent_template_importable():
    """ISAgentTemplate can be imported."""
    from agentuniverse.agent.template.is_agent_template import ISAgentTemplate
    assert ISAgentTemplate is not None


# ---------------------------------------------------------------------------
# 2. Configuration injection
# ---------------------------------------------------------------------------

def test_is_default_checkpoint_and_correction_values():
    """Default config values are applied when not provided."""
    pattern = _build_pattern()
    result = pattern.invoke(_make_input(), {"input": "x"})
    assert "result" in result
    assert "execution_context" in result


def test_is_custom_checkpoint_count():
    """A custom checkpoint_count controls the number of checkpoints."""
    impl = _MockImplementationAgent(outputs=[f"step {i}" for i in range(5)])
    sup = _MockSupervisionAgent(correction_flags=[False] * 5)
    pattern = _build_pattern(impl, sup)
    result = pattern.invoke(_make_input(), {"input": "x", "checkpoint_count": 4})
    assert len(result["result"]) == 4


def test_is_custom_max_corrections():
    """max_corrections limits the number of corrections applied."""
    impl = _MockImplementationAgent(outputs=[f"c{i}" for i in range(10)])
    sup = _MockSupervisionAgent(correction_flags=[True] * 5)
    pattern = _build_pattern(impl, sup)
    result = pattern.invoke(_make_input(),
                            {"input": "x", "checkpoint_count": 3, "max_corrections": 1})
    ctx = result["execution_context"]
    assert ctx["corrections_made"] == 1


# ---------------------------------------------------------------------------
# 3. Full loop logic (sync)
# ---------------------------------------------------------------------------

def test_is_implementation_and_supervision_recorded():
    """Each checkpoint records implementation and supervision results."""
    impl = _MockImplementationAgent(outputs=["work"])
    sup = _MockSupervisionAgent(correction_flags=[False])
    pattern = _build_pattern(impl, sup)
    result = pattern.invoke(_make_input(), {"input": "x", "checkpoint_count": 1})
    round_result = result["result"][0]
    assert round_result["implementation_result"]["output"] == "work"
    assert round_result["supervision_result"]["needs_correction"] is False


def test_is_correction_triggered_when_needed():
    """A correction is executed when supervision requests it."""
    impl = _MockImplementationAgent(outputs=["work", "corrected work"])
    sup = _MockSupervisionAgent(correction_flags=[True])
    pattern = _build_pattern(impl, sup)
    result = pattern.invoke(_make_input(),
                            {"input": "x", "checkpoint_count": 1, "max_corrections": 2})
    assert "correction_result" in result["result"][0]


def test_is_correction_skipped_when_not_needed():
    """No correction when supervision approves."""
    impl = _MockImplementationAgent(outputs=["work"])
    sup = _MockSupervisionAgent(correction_flags=[False])
    pattern = _build_pattern(impl, sup)
    result = pattern.invoke(_make_input(),
                            {"input": "x", "checkpoint_count": 1, "max_corrections": 2})
    assert "correction_result" not in result["result"][0]


def test_is_correction_skipped_when_max_reached():
    """Corrections stop once max_corrections is reached."""
    impl = _MockImplementationAgent(outputs=[f"c{i}" for i in range(10)])
    sup = _MockSupervisionAgent(correction_flags=[True] * 3)
    pattern = _build_pattern(impl, sup)
    result = pattern.invoke(_make_input(),
                            {"input": "x", "checkpoint_count": 3, "max_corrections": 1})
    corrections_with_result = [r for r in result["result"] if "correction_result" in r]
    assert len(corrections_with_result) == 1


def test_is_checkpoint_history_recorded():
    """The execution_context records checkpoint history."""
    impl = _MockImplementationAgent(outputs=["a", "b"])
    sup = _MockSupervisionAgent(correction_flags=[False, False])
    pattern = _build_pattern(impl, sup)
    result = pattern.invoke(_make_input(), {"input": "x", "checkpoint_count": 2})
    history = result["execution_context"]["checkpoint_history"]
    assert len(history) == 2


def test_is_default_agents_when_none():
    """When both agents are None, defaults produce pass-through results."""
    pattern = _build_pattern(None, None)
    result = pattern.invoke(_make_input(), {"input": "x", "checkpoint_count": 2})
    assert len(result["result"]) == 2


def test_is_result_structure():
    """Result contains both 'result' and 'execution_context'."""
    pattern = _build_pattern()
    result = pattern.invoke(_make_input(), {"input": "x"})
    assert isinstance(result["result"], list)
    assert isinstance(result["execution_context"], dict)


# ---------------------------------------------------------------------------
# 4. Async loop logic
# ---------------------------------------------------------------------------

def test_is_async_invoke_basic():
    """async_invoke returns result and execution_context."""
    impl = _MockImplementationAgent(outputs=["a", "b"])
    sup = _MockSupervisionAgent(correction_flags=[False, False])
    pattern = _build_pattern(impl, sup)
    result = asyncio.get_event_loop().run_until_complete(
        pattern.async_invoke(_make_input(), {"input": "x", "checkpoint_count": 2})
    )
    assert len(result["result"]) == 2


def test_is_async_correction_triggered():
    """async_invoke executes corrections when requested."""
    impl = _MockImplementationAgent(outputs=["a", "corrected"])
    sup = _MockSupervisionAgent(correction_flags=[True])
    pattern = _build_pattern(impl, sup)
    result = asyncio.get_event_loop().run_until_complete(
        pattern.async_invoke(_make_input(),
                             {"input": "x", "checkpoint_count": 1, "max_corrections": 1})
    )
    assert "correction_result" in result["result"][0]


def test_is_async_default_agents():
    """async_invoke works with default (None) agents."""
    pattern = _build_pattern()
    result = asyncio.get_event_loop().run_until_complete(
        pattern.async_invoke(_make_input(), {"input": "x", "checkpoint_count": 1})
    )
    assert len(result["result"]) == 1


# ---------------------------------------------------------------------------
# 5. set_by_agent_model & validation
# ---------------------------------------------------------------------------

def test_is_set_by_agent_model_injects_agents():
    """set_by_agent_model returns a new instance with injected agents."""
    pattern = _build_pattern()
    impl = _MockImplementationAgent()
    sup = _MockSupervisionAgent(correction_flags=[False])
    new_pattern = pattern.set_by_agent_model(implementation=impl, supervision=sup)
    assert new_pattern.implementation is impl
    assert new_pattern.supervision is sup


def test_is_set_by_agent_model_preserves_metadata():
    """set_by_agent_model preserves name and description."""
    pattern = _build_pattern()
    pattern.name = "my_is"
    pattern.description = "desc"
    new_pattern = pattern.set_by_agent_model()
    assert new_pattern.name == "my_is"
    assert new_pattern.description == "desc"


def test_is_validation_rejects_wrong_implementation_type():
    """Validation fails when implementation agent is the wrong type."""
    pattern = _build_pattern()
    pattern.implementation = "not an agent"
    with pytest.raises(ValueError):
        pattern.invoke(_make_input(), {"input": "x"})


def test_is_validation_rejects_wrong_supervision_type():
    """Validation fails when supervision agent is the wrong type."""
    pattern = _build_pattern()
    pattern.supervision = 123
    with pytest.raises(ValueError):
        pattern.invoke(_make_input(), {"input": "x"})


def test_is_validation_accepts_correct_types():
    """Validation passes when agents are correct template subclasses."""
    impl = _MockImplementationAgent()
    sup = _MockSupervisionAgent(correction_flags=[False])
    pattern = _build_pattern(impl, sup)
    pattern._validate_work_pattern_members()


def test_is_implementation_result_added_to_input_object():
    """The implementation result is stored in the input_object."""
    impl = _MockImplementationAgent(outputs=["done"])
    sup = _MockSupervisionAgent(correction_flags=[False])
    pattern = _build_pattern(impl, sup)
    input_object = _make_input()
    pattern.invoke(input_object, {"input": "x", "checkpoint_count": 1})
    assert input_object.get_data("implementation_result") is not None


def test_is_supervision_result_added_to_input_object():
    """The supervision result is stored in the input_object."""
    impl = _MockImplementationAgent(outputs=["done"])
    sup = _MockSupervisionAgent(correction_flags=[True])
    pattern = _build_pattern(impl, sup)
    input_object = _make_input()
    pattern.invoke(input_object, {"input": "x", "checkpoint_count": 1, "max_corrections": 1})
    assert input_object.get_data("supervision_result") is not None
