from agentuniverse.agent.action.tool.common_tool import tavily_tool


class RecordingClient:
    searches = []

    def __init__(self, api_key):
        self.api_key = api_key

    def search(self, **kwargs):
        self.searches.append(kwargs)
        return kwargs


def test_request_override_does_not_leak_to_later_calls(monkeypatch):
    RecordingClient.searches = []
    monkeypatch.setattr(tavily_tool, "_get_tavily_client_class", lambda: RecordingClient)
    tool = tavily_tool.TavilyTool(api_key="key", max_results=5)

    tool.execute("first", max_results=1)
    tool.execute("second")

    assert [call["max_results"] for call in RecordingClient.searches] == [1, 5]
    assert tool.max_results == 5
