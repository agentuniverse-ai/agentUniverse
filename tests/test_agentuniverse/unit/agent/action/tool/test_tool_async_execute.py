import asyncio

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class AsyncExecuteTool(Tool):
    name = "async_execute_tool"

    async def execute(self, value):
        await asyncio.sleep(0)
        return f"async:{value}"


class LegacyAsyncExecuteTool(Tool):
    name = "legacy_async_execute_tool"

    async def execute(self, tool_input: ToolInput):
        await asyncio.sleep(0)
        return f"legacy-async:{tool_input.get_data('value')}"


def test_async_run_awaits_async_execute_implementation():
    tool = AsyncExecuteTool(input_keys=["value"])

    result = asyncio.run(tool.async_run(value="payload"))

    assert result == "async:payload"


def test_async_run_awaits_legacy_async_execute_implementation():
    tool = LegacyAsyncExecuteTool(input_keys=["value"])

    result = asyncio.run(tool.async_run(value="payload"))

    assert result == "legacy-async:payload"


def test_async_langchain_run_awaits_async_execute_implementation():
    tool = AsyncExecuteTool(input_keys=["value"])

    result = asyncio.run(tool.async_langchain_run('{"value": "payload"}'))

    assert result == "async:payload"
