from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader import WebsiteBs4Reader


class _Response:
    def __init__(self, content=b"", error=None):
        self.content = content
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error


def test_failed_fetch_consumes_max_links_budget():
    root = (
        b"<html><main>" + b"root content " * 30 +
        b"</main><a href='/child-0'>bad</a><a href='/child-1'>good</a></html>"
    )
    responses = {
        "https://example.com": _Response(root),
        "https://example.com/child-0": _Response(error=RuntimeError("offline")),
        "https://example.com/child-1": _Response(b"<main>" + b"good " * 60 + b"</main>"),
    }
    calls = []

    def get(url, timeout):
        calls.append(url)
        return responses[url]

    reader = WebsiteBs4Reader(max_depth=2, max_links=2)
    with patch(
        "agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader.httpx.get",
        side_effect=get,
    ), patch("agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader.time.sleep"):
        result = reader._crawl_website("https://example.com")

    assert calls == ["https://example.com", "https://example.com/child-0"]
    assert list(result) == ["https://example.com"]
