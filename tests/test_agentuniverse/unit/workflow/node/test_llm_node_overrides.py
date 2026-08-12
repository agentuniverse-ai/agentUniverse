from unittest.mock import patch

from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.workflow.node.llm_node import LLMManager, LLMNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


class RecordingLLM:
    def __init__(self, model_name="base", temperature=0.9):
        self.model_name = model_name
        self.temperature = temperature
        self.call_count = 0

    def set_by_agent_model(self, **kwargs):
        return RecordingLLM(
            model_name=kwargs.get("model_name", self.model_name),
            temperature=kwargs.get("temperature", self.temperature),
        )

    def call(self, **kwargs):
        self.call_count += 1
        return LLMOutput(text=f"{self.model_name}:{self.temperature}")


def test_llm_node_calls_the_configured_llm_copy():
    base_llm = RecordingLLM()
    node = LLMNode(
        id="llm",
        data={
            "inputs": {
                "llm_param": [
                    {"name": "id", "value": "test_llm"},
                    {"name": "model_name", "value": "override"},
                    {"name": "temperature", "value": {"content": 0.2}},
                    {"name": "prompt", "value": "hello"},
                ],
                "input_param": [],
            },
            "outputs": [{"name": "answer"}],
        },
    )

    with patch.object(LLMManager(), "get_instance_obj", return_value=base_llm):
        result = node.run(WorkflowOutput())

    assert base_llm.call_count == 0
    assert result.result[0].value == "override:0.2"
