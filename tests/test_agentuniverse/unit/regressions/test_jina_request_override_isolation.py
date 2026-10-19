from agentuniverse.agent.action.tool.common_tool.jina_ai_tool import JinaAITool


def test_jina_request_overrides_do_not_mutate_shared_tool(monkeypatch):
    monkeypatch.setattr(
        JinaAITool,
        "search_query",
        lambda self, query: (self.mode, self.timeout, self.remove_image, query),
    )
    tool = JinaAITool(mode="read", timeout=30, remove_image=True)

    result = tool.execute("query", mode="search", timeout=5, remove_image=False)

    assert result == ("search", 5, False, "query")
    assert tool.mode == "read"
    assert tool.timeout == 30
    assert tool.remove_image is True
