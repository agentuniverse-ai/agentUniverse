"""Check crawl decisions without sending requests to external hosts."""

from urllib.parse import urljoin

import httpx
import pytest

from agentuniverse.agent.action.knowledge.reader.file import website_bs4_reader
from agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader import WebsiteBs4Reader


def crawl_with_recorded_requests(monkeypatch, start, href):
    requests = []

    def fetch(url, timeout):
        requests.append(url)
        markup = "<div>Page content</div>"
        if url == start:
            markup += '<a href="{}">Next</a>'.format(href)
        return httpx.Response(200, text=markup, request=httpx.Request("GET", url))

    monkeypatch.setattr(website_bs4_reader.httpx, "get", fetch)
    monkeypatch.setattr(website_bs4_reader.time, "sleep", lambda _: None)
    documents = WebsiteBs4Reader(max_depth=2, max_links=3).load_data(start)
    return requests, [doc.metadata["source"] for doc in documents]


@pytest.mark.parametrize("href", [
    "https://badexample.com/page",
    "https://evil-example.com/page",
    "https://example.com.evil/page",
    "https://example.com@badexample.com/page",
    "ftp://example.com/page",
    "javascript:alert(1)",
])
def test_rejects_deceptive_hosts_and_non_http_links(monkeypatch, href):
    start = "https://example.com/"
    requests, sources = crawl_with_recorded_requests(monkeypatch, start, href)
    assert requests == [start]
    assert sources == [start]


@pytest.mark.parametrize("href", [
    "https://docs.example.com/page",
    "/about",
    "https://EXAMPLE.COM:8443/page",
    "https://docs.example.com./page",
])
def test_keeps_matching_hostname_links(monkeypatch, href):
    start = "https://example.com/"
    expected = [start, urljoin(start, href)]
    requests, sources = crawl_with_recorded_requests(monkeypatch, start, href)
    assert requests == expected
    assert sources == expected


@pytest.mark.parametrize("start", [
    "https://WWW.EXAMPLE.COM:8443/",
    "https://user:pass@docs.example.com:8443/",
    "https://docs.example.com./",
])
def test_domain_scope_uses_hostname_of_start_url(monkeypatch, start):
    href = "https://example.com/page"
    requests, sources = crawl_with_recorded_requests(monkeypatch, start, href)
    assert requests == [start, href]
    assert sources == [start, href]
