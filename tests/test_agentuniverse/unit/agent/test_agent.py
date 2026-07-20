import asyncio
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
    """A failing tool must not abort the whole tool invocation loop.

    The failure is preserved as an explicit, per-tool marker in the returned
    string so a partial execution cannot look like a complete success to the
    downstream agent; the raw exception (which may carry sensitive detail)
    stays in the operator-facing log.
    """

    @staticmethod
    def _make_tools():
        from agentuniverse.agent.action.tool.tool import Tool

        # The tool's NAME is "failing_tool"; the exception MESSAGE is the
        # sensitive token "secret_token_value" so the leak test can tell them
        # apart and assert only the name (not the exception) reaches the agent.
        class _FailingTool(Tool):
            def execute(self, *args, **kwargs):
                raise RuntimeError("secret_token_value leaked")

            def run(self, **kwargs):
                raise RuntimeError("secret_token_value leaked")

            async def async_run(self, **kwargs):
                raise RuntimeError("secret_token_value leaked")

        class _OkTool(Tool):
            def execute(self, *args, **kwargs):
                return "ok"

            def run(self, **kwargs):
                return "ok"

            async def async_run(self, **kwargs):
                return "ok"

        return {
            "failing_tool": _FailingTool(input_keys=[]),
            "ok": _OkTool(input_keys=[]),
        }

    def test_failing_tool_leaves_marker_and_others_still_run(self):
        tools = self._make_tools()
        with patch("agentuniverse.agent.agent.ToolManager") as mgr:
            mgr.return_value.get_instance_obj.side_effect = lambda name: tools.get(name)
            agent = _StubAgent()
            result = agent.invoke_tools(
                InputObject({}), tool_names=["ok", "failing_tool", "ok"]
            )

        # The failing tool is replaced by a stable per-tool marker, in order, so
        # the downstream agent can tell this was a partial execution rather than
        # a clean "ok\n\nok".
        self.assertEqual(result, "ok\n\n[tool failing_tool failed]\n\nok")

    def test_failed_tool_marker_does_not_leak_exception_detail(self):
        tools = self._make_tools()
        with patch("agentuniverse.agent.agent.ToolManager") as mgr:
            mgr.return_value.get_instance_obj.side_effect = lambda name: tools.get(name)
            agent = _StubAgent()
            result = agent.invoke_tools(InputObject({}), tool_names=["failing_tool"])

        # The exception message and type must not reach the downstream agent;
        # only the stable, tool-named marker is visible.
        self.assertEqual(result, "[tool failing_tool failed]")
        self.assertNotIn("secret_token_value", result)
        self.assertNotIn("RuntimeError", result)

    def test_mixed_success_failure_ordering_is_preserved(self):
        tools = self._make_tools()
        with patch("agentuniverse.agent.agent.ToolManager") as mgr:
            mgr.return_value.get_instance_obj.side_effect = lambda name: tools.get(name)
            agent = _StubAgent()
            # failing first, then ok, then failing again — output order must match.
            result = agent.invoke_tools(
                InputObject({}), tool_names=["failing_tool", "ok", "failing_tool"]
            )
        self.assertEqual(
            result, "[tool failing_tool failed]\n\nok\n\n[tool failing_tool failed]"
        )

    def test_async_failing_tool_leaves_marker_and_others_still_run(self):
        tools = self._make_tools()
        with patch("agentuniverse.agent.agent.ToolManager") as mgr:
            mgr.return_value.get_instance_obj.side_effect = lambda name: tools.get(name)
            agent = _StubAgent()
            result = asyncio.new_event_loop().run_until_complete(
                agent.async_invoke_tools(
                    InputObject({}), tool_names=["ok", "failing_tool", "ok"]
                )
            )

        # Same contract as the sync path: failing tool is a stable marker, in
        # order, without leaking the exception detail.
        self.assertEqual(result, "ok\n\n[tool failing_tool failed]\n\nok")
        self.assertNotIn("secret_token_value", result)

    def test_async_mixed_success_failure_ordering_is_preserved(self):
        tools = self._make_tools()
        with patch("agentuniverse.agent.agent.ToolManager") as mgr:
            mgr.return_value.get_instance_obj.side_effect = lambda name: tools.get(name)
            agent = _StubAgent()
            result = asyncio.new_event_loop().run_until_complete(
                agent.async_invoke_tools(
                    InputObject({}), tool_names=["failing_tool", "ok", "failing_tool"]
                )
            )
        self.assertEqual(
            result, "[tool failing_tool failed]\n\nok\n\n[tool failing_tool failed]"
        )
