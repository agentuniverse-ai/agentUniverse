"""Exercise shared reader calls using real HTTP, HTML parsing and threads."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Lock, Thread
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.reader.file import website_bs4_reader
from agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader import (
    WebsiteBs4Reader,
)


@pytest.fixture
def website(monkeypatch):
    """Serve page graphs and optionally hold one response to coordinate calls."""
    site = SimpleNamespace(
        hits=Counter(), lock=Lock(), hold_first=False, hold_path="/root",
        blocked=Event(), release_first=Event())
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setattr(website_bs4_reader.random, "uniform", lambda *args: 0)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            with site.lock:
                site.hits[self.path] += 1
                count = site.hits[self.path]
            if self.path == site.hold_path and count == 1 and site.hold_first:
                site.blocked.set()
                if not site.release_first.wait(10):
                    self.send_error(500, "test response was not released")
                    return
            links = {
                "/root": ["/child"], "/child": ["/grandchild"], "/grandchild": [],
                "/fork": ["/fork/child", "/fork/sibling"],
                "/fork/child": [], "/fork/sibling": [], "/other": [],
            }
            if self.path not in links:
                self.send_error(500, "fixture failure")
                return
            body = '<html><body><div>' + (self.path + " content ") * 30 + '</div>'
            for link in links[self.path]:
                body += '<a href="' + link + '">next</a>'
            body = (body + '</body></html>').encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    site.base = "http://127.0.0.1:" + str(server.server_port)
    site.url = site.base + "/root"
    try:
        yield site
    finally:
        site.release_first.set()
        server.shutdown()
        server.server_close()
        thread.join(5)


def assert_pages(documents, website, paths, call):
    """Check both actual crawl output and invocation-specific metadata."""
    assert [doc.metadata["source"] for doc in documents] == [
        website.base + path for path in paths]
    assert all(doc.metadata["call"] == call for doc in documents)
    assert all(path + " content" in doc.text for path, doc in zip(paths, documents))


@pytest.mark.parametrize("overrides", [
    {"max_depth": 1}, {"max_links": 1}, {"max_depth": 1, "max_links": 1},
])
def test_limits_apply_only_to_the_current_call(website, overrides):
    """A limited call must not reduce the next call's configured crawl budget."""
    reader = WebsiteBs4Reader(max_depth=3, max_links=3)
    extra = dict(overrides, call="limited")
    limited = reader.load_data(website.url, ext_info=extra)
    ordinary = reader.load_data(website.url, ext_info={"call": "ordinary"})
    assert_pages(limited, website, ["/root"], "limited")
    assert all(doc.metadata[key] == value for doc in limited for key, value in extra.items())
    assert_pages(ordinary, website, ["/root", "/child", "/grandchild"], "ordinary")
    assert (reader.max_depth, reader.max_links) == (3, 3)
    assert extra == dict(overrides, call="limited")


def test_failed_fetch_does_not_change_configured_limits(website):
    """An unsuccessful limited call must leave later calls usable."""
    reader = WebsiteBs4Reader(max_depth=3, max_links=3)
    assert reader.load_data(
        website.base + "/failure", ext_info={"max_depth": 1, "max_links": 1}) == []
    documents = reader.load_data(website.url, ext_info={"call": "after failure"})
    assert_pages(documents, website, ["/root", "/child", "/grandchild"], "after failure")
    assert (reader.max_depth, reader.max_links) == (3, 3)


def test_overlapping_crawls_have_separate_visited_sets(website):
    """Completing a second crawl must not make the first skip its child page."""
    reader = WebsiteBs4Reader(max_depth=2, max_links=2)
    website.hold_first = True
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(reader.load_data, website.url, ext_info={"call": "first"})
        try:
            assert website.blocked.wait(5), "first HTTP request never arrived"
            second = executor.submit(
                reader.load_data, website.url, ext_info={"call": "second"}).result(10)
        finally:
            website.release_first.set()
        first = first.result(10)
    assert_pages(second, website, ["/root", "/child"], "second")
    assert_pages(first, website, ["/root", "/child"], "first")
    assert website.hits == {"/root": 2, "/child": 2}


def test_zero_budget_call_does_not_shrink_an_active_crawl(website):
    """A concurrent call with no page budget must not alter an in-flight call."""
    reader = WebsiteBs4Reader(max_depth=2, max_links=2)
    website.hold_first = True
    with ThreadPoolExecutor(max_workers=1) as executor:
        active = executor.submit(reader.load_data, website.url, ext_info={"call": "active"})
        try:
            assert website.blocked.wait(5), "first HTTP request never arrived"
            assert reader.load_data(website.url, ext_info={"max_links": 0}) == []
        finally:
            website.release_first.set()
        documents = active.result(10)
    assert_pages(documents, website, ["/root", "/child"], "active")
    assert (reader.max_depth, reader.max_links) == (2, 2)


def test_other_crawl_does_not_discard_a_queued_sibling(website):
    """A disjoint crawl must not clear the active crawl's pending URL queue."""
    reader = WebsiteBs4Reader(max_depth=2, max_links=3)
    website.hold_first = True
    website.hold_path = "/fork/child"
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(
            reader.load_data, website.base + "/fork", ext_info={"call": "fork"})
        try:
            assert website.blocked.wait(5), "child HTTP request never arrived"
            other = executor.submit(
                reader.load_data, website.base + "/other", ext_info={"call": "other"}
            ).result(10)
        finally:
            website.release_first.set()
        documents = first.result(10)
    assert_pages(other, website, ["/other"], "other")
    assert_pages(documents, website, ["/fork", "/fork/child", "/fork/sibling"], "fork")
    assert website.hits == {"/fork": 1, "/fork/child": 1, "/fork/sibling": 1, "/other": 1}


def test_serial_crawls_are_independent(website):
    """Keep the existing ability to crawl the same pages again on one reader."""
    reader = WebsiteBs4Reader(max_depth=2, max_links=2)
    for call in ("first", "second"):
        documents = reader.load_data(website.url, ext_info={"call": call})
        assert_pages(documents, website, ["/root", "/child"], call)
    assert website.hits == {"/root": 2, "/child": 2}


@pytest.mark.parametrize("url", [None, "", "ftp://example.com"])
def test_invalid_urls_keep_the_existing_contract(website, url):
    """Invalid inputs must not issue HTTP requests or change configuration."""
    reader = WebsiteBs4Reader(max_depth=2, max_links=2)
    if url and url.startswith("ftp:"):
        with pytest.raises(ValueError, match="Invalid URL format"):
            reader.load_data(url, ext_info={"max_links": 0})
    else:
        assert reader.load_data(url, ext_info={"max_links": 0}) == []
    assert not website.hits
    assert (reader.max_depth, reader.max_links) == (2, 2)
