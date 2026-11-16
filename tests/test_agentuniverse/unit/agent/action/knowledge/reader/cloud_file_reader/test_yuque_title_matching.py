"""Match real parsed page titles before sanitizing output metadata."""
import html
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, urlsplit

import pytest
from requests.adapters import HTTPAdapter

from agentuniverse.agent.action.knowledge.reader.cloud_file_reader import yuque_reader


@pytest.fixture
def load_yuque(monkeypatch):
    routes = {}
    requested = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            requested.append(path)
            body = routes.get(path)
            self.send_response(200 if body is not None else 404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write((body or "missing").encode("utf-8"))

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    origin = "http://127.0.0.1:" + str(server.server_port)
    thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.01))
    thread.start()

    class LoopbackAdapter(HTTPAdapter):
        def send(self, request, **kwargs):
            parsed = urlsplit(request.url)
            request.url = origin + parsed.path + ("?" + parsed.query if parsed.query else "")
            return super().send(request, **kwargs)

    reader = yuque_reader.YuqueReader()
    reader.session.trust_env = False
    reader.session.mount("https://www.yuque.com/", LoopbackAdapter())
    monkeypatch.setattr(yuque_reader.time, "sleep", lambda _: None)

    def load(title, toc=None):
        if toc is None:
            toc = [{"title": title, "url": "selected"}]
        payload = {"book": {"id": 42, "toc": toc}}
        routes["/demo/book"] = (
            "<html><head><title>" + html.escape(title) + " · 语雀</title></head>"
            + '<script>JSON.parse(decodeURIComponent("'
            + quote(json.dumps(payload)) + '"));</script></html>'
        )
        routes["/api/docs/selected"] = json.dumps({"data": {"sourcecode": "# 正确文档"}})
        routes["/api/docs/other"] = json.dumps({"data": {"sourcecode": "# Other document"}})
        return reader.load_data("https://www.yuque.com/demo/book"), requested

    try:
        yield load
    finally:
        reader.session.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.parametrize("title", [
    "C/C++", "Windows\\Paths", "API: Methods", "wild*card", "Why?",
    'Call "run"', "x < y", "x > y", "A|B", "Plain title", "中文标题", "A-B",
])
def test_title_punctuation_does_not_drop_document(load_yuque, title):
    documents, requested = load_yuque(title)

    assert len(documents) == 1
    assert documents[0].text == "# 正确文档"
    assert documents[0].metadata == {
        "source": "https://www.yuque.com/demo/book",
        "doc_title": title,
        "sanitized_title": title.translate(str.maketrans({c: "_" for c in '\\/:*?"<>|\n\r'})),
    }
    assert requested == ["/demo/book", "/demo/book", "/api/docs/selected"]


def test_similar_sanitized_title_does_not_select_other_document(load_yuque):
    toc = [
        {"title": "Guide-Setup", "url": "other"},
        {"title": "Guide/Setup", "url": "selected"},
    ]

    documents, requested = load_yuque("Guide/Setup", toc)

    assert [document.text for document in documents] == ["# 正确文档"]
    assert documents[0].metadata["doc_title"] == "Guide/Setup"
    assert "/api/docs/other" not in requested


def test_unmatched_page_still_does_not_fetch_unrelated_document(load_yuque):
    documents, requested = load_yuque("Missing", [{"title": "Other", "url": "other"}])

    assert documents == []
    assert requested == ["/demo/book", "/demo/book"]
