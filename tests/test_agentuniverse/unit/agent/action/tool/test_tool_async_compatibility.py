import asyncio

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class LegacyInputTool(Tool):
    name: str = "legacy_input_tool"

    def execute(self, tool_input: ToolInput):
        return tool_input.get_data("value")


class NoInputTool(Tool):
    name: str = "no_input_tool"

    def execute(self, **kwargs):
        return "no-input-result"


class LegacyNoInputTool(Tool):
    name: str = "legacy_no_input_tool"

    def execute(self, tool_input: ToolInput):
        return "legacy-no-input-result"


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


def test_langchain_run_supports_no_input_tool():
    tool = NoInputTool()

    result = Tool.langchain_run.__wrapped__(tool, "{}")

    assert result == "no-input-result"


def test_async_langchain_run_supports_no_input_tool():
    tool = NoInputTool()

    result = asyncio.run(Tool.async_langchain_run.__wrapped__(tool, "{}"))

    assert result == "no-input-result"


def test_langchain_run_supports_legacy_no_input_tool():
    tool = LegacyNoInputTool()

    result = Tool.langchain_run.__wrapped__(tool, "")

    assert result == "legacy-no-input-result"


def test_async_langchain_run_supports_legacy_no_input_tool():
    tool = LegacyNoInputTool()

    result = asyncio.run(Tool.async_langchain_run.__wrapped__(tool, ""))

    assert result == "legacy-no-input-result"
