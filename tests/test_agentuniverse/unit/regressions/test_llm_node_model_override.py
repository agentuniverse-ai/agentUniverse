"""Regression tests for workflow LLM node model overrides."""

from agentuniverse.workflow.node.llm_node import LLMNode
from agentuniverse.workflow.node.node_config import (
    LLMNodeInputParams,
    NodeInfoParams,
)
from agentuniverse.workflow.workflow_output import WorkflowOutput


class StubLLM:
    def __init__(self):
        self.model_name = "base"
        self.temperature = 0.9
        self.called_model_name = None

    def set_by_agent_model(self, **kwargs):
        copied = StubLLM()
        copied.model_name = kwargs.get("model_name", self.model_name)
        copied.temperature = kwargs.get("temperature", self.temperature)
        return copied

    def call(self, messages=None, streaming=False):
        return type("O", (), {"text": f"used:{self.model_name}"})()


def _build_llm_node(model_name, temperature):
    node = LLMNode(id="llm", type="llm")
    node._data.inputs = LLMNodeInputParams(
        llm_param=[
            NodeInfoParams(name="model_name", type="str", value={"content": model_name}),
            NodeInfoParams(name="temperature", type="str", value={"content": str(temperature)}),
            NodeInfoParams(name="prompt", type="str", value={"content": "say hi"}),
            NodeInfoParams(name="id", type="str", value={"content": "stub"}),
        ],
        input_param=[],
    )
    node._data.outputs = [type("P", (), {"name": "out", "value": None})()]
    return node


def test_llm_node_uses_configured_model_override():
    from agentuniverse.llm.llm_manager import LLMManager

    stub = StubLLM()
    LLMManager().get_instance_obj = lambda llm_id: stub

    node = _build_llm_node("override", 0.2)
    workflow_output = WorkflowOutput()
    result = node._run(workflow_output)
    assert result.result[0].value == "used:override"
