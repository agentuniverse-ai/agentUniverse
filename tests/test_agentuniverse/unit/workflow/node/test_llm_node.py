# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_llm_node.py

"""Unit tests for the workflow LLMNode with LLMManager mocked."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

import agentuniverse.workflow.node.llm_node as llm_node_module
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.llm_node import LLMNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


class FakeLLM:
    def __init__(self, answer="llm answer"):
        self.answer = answer
        self.set_kwargs = None
        self.call_kwargs = None

    def set_by_agent_model(self, **kwargs):
        self.set_kwargs = kwargs

    def call(self, **kwargs):
        self.call_kwargs = kwargs
        return SimpleNamespace(text=self.answer)


def build_llm_node(llm_param, input_param, outputs):
    return LLMNode(id="llm_1", name="llm",
                   data={"inputs": {"llm_param": llm_param,
                                    "input_param": input_param},
                         "outputs": outputs})


@pytest.fixture
def workflow_output():
    return WorkflowOutput()


class TestLLMNode:
    """Test LLMNode prompting, LLM invocation and output wiring."""

    def test_type_is_llm(self):
        node = build_llm_node([], [], [{"name": "answer", "value": None}])
        assert node.type == NodeEnum.LLM

    def test_run_calls_llm_with_resolved_prompt(self, workflow_output):
        fake = FakeLLM()
        node = build_llm_node(
            [{"name": "id", "value": "llm1"},
             {"name": "model_name", "value": "gpt-4o"},
             {"name": "prompt", "value": "Tell me about {{topic}}"}],
            [{"name": "topic", "value": {"type": "direct",
                                         "content": "agents"}}],
            [{"name": "answer", "value": None}])
        with patch.object(llm_node_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = fake
            result = node.run(workflow_output)
        assert result.status == NodeStatusEnum.SUCCEEDED
        assert result.result[0].value == "llm answer"
        assert fake.set_kwargs == {"model_name": "gpt-4o",
                                   "temperature": None}
        messages = fake.call_kwargs["messages"]
        assert messages[0]["content"] == "Tell me about agents"
        assert fake.call_kwargs["streaming"] is False
        assert workflow_output.workflow_parameters["llm_1"][0].value == \
            "llm answer"

    def test_missing_model_name_sets_temperature_only(self, workflow_output):
        fake = FakeLLM()
        node = build_llm_node(
            [{"name": "id", "value": "llm1"},
             {"name": "temperature", "value": {"content": "0.5"}},
             {"name": "prompt", "value": "hi"}],
            [], [{"name": "answer", "value": None}])
        with patch.object(llm_node_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = fake
            node.run(workflow_output)
        assert fake.set_kwargs == {"temperature": "0.5"}

    def test_missing_template_variable_raises(self, workflow_output):
        fake = FakeLLM()
        node = build_llm_node(
            [{"name": "id", "value": "llm1"},
             {"name": "prompt", "value": "hi {{unknown}}"}],
            [], [{"name": "answer", "value": None}])
        with patch.object(llm_node_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = fake
            with pytest.raises(ValueError, match="The variable unknown"):
                node.run(workflow_output)

    def test_missing_llm_raises(self, workflow_output):
        node = build_llm_node(
            [{"name": "id", "value": "ghost"},
             {"name": "prompt", "value": "hi"}],
            [], [{"name": "answer", "value": None}])
        with patch.object(llm_node_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = None
            with pytest.raises(ValueError, match="No llm with id ghost"):
                node.run(workflow_output)
