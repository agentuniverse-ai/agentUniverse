import asyncio
import inspect
import threading

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject


class _LangChainAgent(Agent):
    def input_keys(self) -> list[str]:
        return ["value"]

    def output_keys(self) -> list[str]:
        return ["result"]

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return agent_result

    def run(self, **kwargs) -> OutputObject:
        return OutputObject({"result": f"sync:{kwargs['value']}"})

    async def async_run(self, **kwargs) -> OutputObject:
        await asyncio.sleep(0)
        return OutputObject({"result": f"async:{kwargs['value']}"})


class _LangChainKnowledge(Knowledge):
    def query_knowledge(
        self,
        query_str: str,
        similarity_top_k: int,
        **kwargs,
    ) -> list[Document]:
        execution_path = "sync" if threading.current_thread() is threading.main_thread() else "async"
        return [Document(text=f"{execution_path}:{query_str}:{similarity_top_k}")]


class _LangChainTool(Tool):
    name: str = "langchain_test_tool"
    description: str = "LangChain conversion test tool"

    def execute(self, value: str) -> str:
        return f"sync:{value}"

    async def async_execute(self, value: str) -> str:
        await asyncio.sleep(0)
        return f"async:{value}"


def _run_without_tracing(func, *args, **kwargs):
    return func(*args, **kwargs)


async def _async_run_without_tracing(func, *args, **kwargs):
    return await func(*args, **kwargs)


def _assert_completed(result, expected):
    try:
        assert not inspect.isawaitable(result)
        assert result == expected
    finally:
        if inspect.iscoroutine(result):
            result.close()


def test_agent_async_langchain_tool_uses_registered_coroutine():
    agent = _LangChainAgent()
    agent.agent_model = AgentModel(info={"name": "langchain_test_agent", "description": "test agent"})
    langchain_tool = asyncio.run(agent.async_as_langchain_tool())

    async_result = asyncio.run(langchain_tool.ainvoke('{"value": "agent"}'))

    _assert_completed(async_result, {"result": "async:agent"})
    assert langchain_tool.invoke('{"value": "agent"}') == {"result": "sync:agent"}


def test_knowledge_async_langchain_tool_uses_registered_coroutine():
    knowledge = _LangChainKnowledge(
        name="langchain_test_knowledge",
        description="test knowledge",
    )
    langchain_tool = asyncio.run(knowledge.async_as_langchain_tool())

    async_result = asyncio.run(langchain_tool.ainvoke('{"query_str": "knowledge", "similarity_top_k": 2}'))

    _assert_completed(
        async_result,
        "This is Query Result:\nasync:knowledge:2",
    )
    assert (
        langchain_tool.invoke('{"query_str": "knowledge", "similarity_top_k": 2}')
        == "This is Query Result:\nsync:knowledge:2"
    )


def test_tool_async_langchain_conversion_keeps_json_sync_fallback(monkeypatch):
    monkeypatch.setattr(
        "agentuniverse.base.annotation.trace._tool_wrapper_sync",
        _run_without_tracing,
    )
    monkeypatch.setattr(
        "agentuniverse.base.annotation.trace._tool_wrapper_async",
        _async_run_without_tracing,
    )
    tool = _LangChainTool(input_keys=["value"])
    langchain_tool = asyncio.run(tool.async_as_langchain())

    async_result = asyncio.run(langchain_tool.ainvoke('{"value": "tool"}'))

    _assert_completed(async_result, "async:tool")
    assert langchain_tool.invoke('{"value": "tool"}') == "sync:tool"
