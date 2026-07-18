import unittest
from copy import deepcopy
from unittest.mock import patch

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject


class _StubAgent(Agent):
    def input_keys(self) -> list[str]:
        return []

    def output_keys(self) -> list[str]:
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return agent_result


def test_process_prompt_preserves_agent_input_for_repeated_calls():
    agent = _StubAgent()
    agent.agent_model = AgentModel(
        profile={
            "introduction": "Introduction",
            "target": "Target",
            "instruction": "Instruction",
        }
    )
    agent_input = {
        "expert_framework": "Expert framework: ",
        "image_urls": [{"url": "https://example.com/image.png"}],
        "audio_url": "https://example.com/audio.mp3",
        "input": "Question",
    }
    original_input = deepcopy(agent_input)

    first_prompt = agent.process_prompt(agent_input)
    second_prompt = agent.process_prompt(agent_input)

    assert agent_input == original_input
    assert first_prompt.messages == second_prompt.messages


class TestInvokeToolsErrorIsolation(unittest.TestCase):
    """A failing tool must not abort the whole tool invocation loop."""

    def test_failing_tool_is_skipped_and_others_still_run(self):
        from agentuniverse.agent.action.tool.tool import Tool

        class _BoomTool(Tool):
            def execute(self, *args, **kwargs):
                raise RuntimeError("boom")

            def run(self, **kwargs):
                raise RuntimeError("boom")

        class _OkTool(Tool):
            def execute(self, *args, **kwargs):
                return "ok"

            def run(self, **kwargs):
                return "ok"

        tools = {"boom": _BoomTool(input_keys=[]), "ok": _OkTool(input_keys=[])}
        with patch("agentuniverse.agent.agent.ToolManager") as mgr:
            mgr.return_value.get_instance_obj.side_effect = lambda name: tools.get(name)
            agent = _StubAgent()
            result = agent.invoke_tools(InputObject({}), tool_names=["ok", "boom", "ok"])

        # The failing tool was skipped; both good invocations are joined.
        self.assertEqual(result, "ok\n\nok")
