from agentuniverse.agent.action.tool.common_tool import tavily_tool


class FakeClient:
    def __init__(self, api_key):
        self.search_calls = 0

    def search(self, **kwargs):
        self.search_calls += 1
        return kwargs


def test_tavily_search_rejects_whitespace_query(monkeypatch):
    client = FakeClient("key")
    monkeypatch.setattr(tavily_tool, "_get_tavily_client_class", lambda: lambda **kwargs: client)
    tool = tavily_tool.TavilyTool(api_key="key")

    result = tool.execute("   ")

    assert result == {"error": "未提供搜索查询"}
    assert client.search_calls == 0
