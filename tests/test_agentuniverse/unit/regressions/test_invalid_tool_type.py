from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.tool.tool import Tool


class StubTool(Tool):
    def execute(self, **kwargs):
        return None


def test_invalid_tool_type_raises_descriptive_value_error():
    configer = SimpleNamespace(
        configer=SimpleNamespace(value={}),
        name="tool",
        description="tool",
        tool_type="invalid",
        input_keys=[],
    )

    with pytest.raises(ValueError, match="Unsupported tool_type: invalid"):
        StubTool().initialize_by_component_configer(configer)
