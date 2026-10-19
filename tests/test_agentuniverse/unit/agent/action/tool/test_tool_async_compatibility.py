import asyncio

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class LegacyInputTool(Tool):
    name: str = "legacy_input_tool"

    def execute(self, tool_input: ToolInput):
        return tool_input.get_data("value")


def test_async_run_supports_legacy_tool_input_signature():
    tool = LegacyInputTool(input_keys=["value"])

    result = asyncio.run(Tool.async_run.__wrapped__(tool, value="from-async-run"))

    assert result == "from-async-run"


def test_async_langchain_run_supports_legacy_tool_input_signature():
    tool = LegacyInputTool(input_keys=["value"])

    result = asyncio.run(
        Tool.async_langchain_run.__wrapped__(
            tool,
            "from-langchain",
        )
    )

    assert result == "from-langchain"
