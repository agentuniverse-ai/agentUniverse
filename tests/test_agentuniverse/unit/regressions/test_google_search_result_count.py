import pytest

from agentuniverse.agent.action.tool.common_tool.google_search_tool_v2 import (
    GoogleScholarSearchTool,
    GoogleSearchTool,
)


@pytest.mark.parametrize(
    "tool",
    [
        GoogleSearchTool(serper_api_key="test-key"),
        GoogleScholarSearchTool(serper_api_key="test-key"),
    ],
)
@pytest.mark.parametrize("count", [0, -1, True, 101])
def test_google_search_rejects_invalid_result_counts(tool, count):
    with pytest.raises(ValueError, match="k must"):
        tool.execute("agent universe", k=count)
