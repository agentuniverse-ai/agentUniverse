import asyncio
import unittest
from copy import deepcopy
from unittest.mock import patch

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject


class _StubAgent(Agent):
    """A minimal Agent stub exposing the abstract interface directly."""

    def input_keys(self) -> list[str]:
        """Return an empty list of input keys for the stub agent."""
        return []

    def output_keys(self) -> list[str]:
        """Return an empty list of output keys for the stub agent."""
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Pass the agent input through unchanged.

        Args:
            input_object: The input object received by the agent.
            agent_input: The parsed agent input dictionary.

        Returns:
            The agent input dictionary unmodified.
        """
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Pass the agent result through unchanged.

        Args:
            agent_result: The agent result dictionary.

        Returns:
            The agent result dictionary unmodified.
        """
        return agent_result


def test_process_prompt_preserves_agent_input_for_repeated_calls():
    """Verify repeated process_prompt calls do not mutate the agent input."""
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
        """Build the dict of failing/ok tool instances used by the tests.

        Returns:
            A mapping of tool name to Tool instance, containing one tool that
            always raises and one tool that always succeeds.
        """
        from agentuniverse.agent.action.tool.tool import Tool

        # The tool's NAME is "failing_tool"; the exception MESSAGE is the
        # sensitive token "secret_token_value" so the leak test can tell them
        # apart and assert only the name (not the exception) reaches the agent.
        class _FailingTool(Tool):
            """A tool that always raises on invocation."""

            def execute(self, *args, **kwargs):
                """Raise a RuntimeError carrying the sensitive marker."""
                raise RuntimeError("secret_token_value leaked")

            def run(self, **kwargs):
                """Raise a RuntimeError carrying the sensitive marker."""
                raise RuntimeError("secret_token_value leaked")

            async def async_run(self, **kwargs):
                """Raise a RuntimeError carrying the sensitive marker."""
                raise RuntimeError("secret_token_value leaked")

        class _OkTool(Tool):
            """A tool that always succeeds with a fixed result."""

            def execute(self, *args, **kwargs):
                """Return the fixed ok result."""
                return "ok"

            def run(self, **kwargs):
                """Return the fixed ok result."""
                return "ok"

            async def async_run(self, **kwargs):
                """Return the fixed ok result."""
                return "ok"

        return {
            "failing_tool": _FailingTool(input_keys=[]),
            "ok": _OkTool(input_keys=[]),
        }

    def test_failing_tool_leaves_marker_and_others_still_run(self):
        """Verify a failing tool becomes a marker and other tools still run."""
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
        """Verify only the tool-named marker, never exception detail, is visible."""
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
        """Verify mixed success/failure output order matches the input order."""
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
        """Verify async invocation also turns a failing tool into a marker."""
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
        """Verify async mixed output order matches the input tool order."""
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


def test_generate_result_returns_empty_text_for_empty_stream():
    """Verify an empty stream yields empty text from generate_result."""
    agent = _StubAgent()

    assert agent.generate_result([]) == ""


def test_tool_names_does_not_mutate_agent_action(monkeypatch):
    """Verify reading tool_names leaves the underlying agent action unchanged."""

    class _StubToolkit:
        """A minimal toolkit stub exposing a fixed tool name list."""

        def __init__(self):
            """Initialize the stub with a single toolkit tool name."""
            self.tool_names = ["toolkit_tool"]

    class _StubToolkitManager:
        """A minimal toolkit manager returning the stub toolkit by name."""

        def get_instance_obj(self, toolkit_name):
            """Assert the requested toolkit name and return the stub toolkit.

            Args:
                toolkit_name: The toolkit name being resolved.

            Returns:
                A _StubToolkit instance.
            """
            assert toolkit_name == "test_toolkit"
            return _StubToolkit()

    monkeypatch.setattr(
        "agentuniverse.agent.agent.ToolkitManager",
        _StubToolkitManager,
    )
    agent = _StubAgent()
    agent.agent_model = AgentModel(
        action={
            "tool": ["direct_tool"],
            "toolkit": ["test_toolkit"],
        }
    )

    assert agent.tool_names == ["direct_tool", "toolkit_tool"]
    assert agent.tool_names == ["direct_tool", "toolkit_tool"]
    assert agent.agent_model.action["tool"] == ["direct_tool"]
