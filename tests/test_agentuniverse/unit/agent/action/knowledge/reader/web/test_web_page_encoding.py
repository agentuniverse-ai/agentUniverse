"""Serve encoded HTML to real HTTP clients and article extractors."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys
from threading import Thread

import pytest

from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader


CONTENT = "中文知识库需要正确读取页面编码，保留完整的正文内容。"


def html_bytes(encoding, meta=None):
    declaration = '<meta charset="{}">'.format(meta) if meta else ""
    markup = ("<html><head>" + declaration + "<title>中文资料</title></head>"
              "<body><article><h1>网页资料</h1><p>" + CONTENT * 30
              + "</p></article></body></html>")
    return markup.encode(encoding)


@pytest.fixture(scope="module")
def html_server():
    pages = {
        "/meta-gbk": (html_bytes("gb18030", "gb18030"), "text/html"),
        "/utf8": (html_bytes("utf-8", "utf-8"), "text/html"),
        "/header-gbk": (html_bytes("gb18030"), "text/html; charset=gb18030"),
        "/bom-utf16": (html_bytes("utf-16"), "text/html"),
    }

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            payload, content_type = pages[self.path]
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01},
                    daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:{}".format(server.server_port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


@pytest.mark.parametrize("path", ["/meta-gbk", "/utf8", "/header-gbk", "/bom-utf16"])
@pytest.mark.parametrize("transport", ["httpx", "requests"])
@pytest.mark.parametrize("extractor", ["trafilatura", "readability", "bs4"])
def test_html_encoding_through_real_clients_and_extractors(
    html_server, monkeypatch, path, transport, extractor
):
    pytest.importorskip(extractor)
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    if transport == "requests":
        monkeypatch.setitem(sys.modules, "httpx", None)
    else:
        pytest.importorskip("httpx")
        import requests

        def reject_fallback(*args, **kwargs):
            raise AssertionError("httpx test must not silently use requests")

        monkeypatch.setattr(requests, "get", reject_fallback)
    if extractor != "trafilatura":
        monkeypatch.setitem(sys.modules, "trafilatura", None)
    if extractor == "bs4":
        monkeypatch.setitem(sys.modules, "readability", None)
    url = html_server + path

    documents = WebPageReader().load_data(url, ext_info={"collection": "pages"})

    assert len(documents) == 1
    assert CONTENT in documents[0].text
    assert documents[0].metadata == {
        "source": "web", "url": url, "extractor": extractor, "collection": "pages"
    }
