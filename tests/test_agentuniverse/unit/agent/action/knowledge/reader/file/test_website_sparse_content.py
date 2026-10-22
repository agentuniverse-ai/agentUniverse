"""Keep visible content on pages without div/section wrappers."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from bs4 import BeautifulSoup

from agentuniverse.agent.action.knowledge.reader.file import website_bs4_reader
from agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader import WebsiteBs4Reader


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        ("<html><head><title>Metadata</title></head><body>"
         "<h1>Heading</h1><p>中文正文 &amp; text</p></body></html>",
         "Heading 中文正文 & text"),
        ("<h1>Heading</h1><p>Body text</p>", "Heading Body text"),
        ("<head><title>Metadata</title></head><h1>Heading</h1><p>Text</p>",
         "Heading Text"),
        ("<body><nav>Navigation</nav><article>Short article</article>"
         "<footer>Footer</footer></body>", "Short article"),
        ("<body><nav>Navigation</nav><main>Short main</main></body>",
         "Short main"),
        ("<body><article><div></div>Short article</article></body>",
         "Short article"),
        ("<body><div> </div><p>Visible text</p></body>", "Visible text"),
        ("<body><!-- comment --><script>secret()</script>"
         "<style>p {color:red}</style><p>Visible</p></body>", "Visible"),
        ("<head><title>Metadata only</title></head>", ""),
        ("<body> \n <div> </div> </body>", ""),
        ("<body><div>Small</div><section>Largest block</section>"
         "Outside text</body>", "Largest block"),
        ("<body><article>" + "Article " * 30 + "</article><div>"
         + "Sidebar " * 50 + "</div></body>", ("Article " * 30).strip()),
    ],
    ids=["bare-body", "fragment", "implicit-body", "short-article",
         "short-main", "article-empty-div", "empty-div", "hidden-text",
         "head-only", "empty-body", "largest-block", "long-article"],
)
def test_sparse_page_content_and_existing_selection(markup, expected):
    soup = BeautifulSoup(markup, "html.parser")
    assert WebsiteBs4Reader()._extract_main_content(soup) == expected


def test_crawls_sparse_pages_over_real_http(monkeypatch):
    pages = {
        "/": "<html><body><h1>First page</h1><p>中文正文</p>"
             "<a href='/next'>Next</a></body></html>",
        "/next": "<html><body><h1>Second page</h1><p>More text</p></body></html>",
    }

    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(self.path)
            payload = pages[self.path].encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    monkeypatch.setattr(website_bs4_reader.time, "sleep", lambda _: None)
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01},
                    daemon=True)
    thread.start()
    url = "http://127.0.0.1:{}/".format(server.server_port)
    extra = {"collection": "pages"}
    try:
        documents = WebsiteBs4Reader(max_depth=2, max_links=2).load_data(
            url, ext_info=extra
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

    assert seen == ["/", "/next"]
    assert [doc.text for doc in documents] == [
        "First page 中文正文 Next", "Second page More text"
    ]
    assert [doc.metadata for doc in documents] == [
        {"source": url, "collection": "pages"},
        {"source": url + "next", "collection": "pages"},
    ]
    assert extra == {"collection": "pages"}
