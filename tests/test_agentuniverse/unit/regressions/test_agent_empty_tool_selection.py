import asyncio
from types import SimpleNamespace

from agentuniverse.agent.agent import Agent


def test_sync_tool_invocation_honors_explicit_empty_selection():
    fake_agent = SimpleNamespace(tool_names=["configured"])

    assert Agent.invoke_tools(fake_agent, None, tool_names=[]) == ""


def test_async_tool_invocation_honors_explicit_empty_selection():
    fake_agent = SimpleNamespace(
        agent_model=SimpleNamespace(action={"tool": ["configured"]})
    )

    result = asyncio.run(Agent.async_invoke_tools(fake_agent, None, tool_names=[]))

    assert result == ""
