"""Crawl links relative to the document's declared HTML base URL."""
import httpx
import pytest

from agentuniverse.agent.action.knowledge.reader.file import website_bs4_reader as module
from agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader import WebsiteBs4Reader


@pytest.mark.parametrize('base,link,expected', [
    ('<base href="/guide/">', 'chapter', 'https://example.com/guide/chapter'),
    ('<base href="../guide/">', 'chapter', 'https://example.com/guide/chapter'),
    ('<base href="https://example.com/docs/">', 'chapter', 'https://example.com/docs/chapter'),
    ('<base target="_blank"><base href="/guide/">', 'chapter', 'https://example.com/guide/chapter'),
    ('<base href="/first/"><base href="/second/">', 'chapter', 'https://example.com/first/chapter'),
    ('', 'chapter', 'https://example.com/start/chapter'),
    ('<base href="">', 'chapter', 'https://example.com/start/chapter'),
    ('<base href="javascript:void(0)">', 'chapter', 'https://example.com/start/chapter'),
    ('<base href="data:text/plain,ignored">', 'chapter', 'https://example.com/start/chapter'),
    ('<base href="https://[invalid">', 'chapter', 'https://example.com/start/chapter'),
    ('<base href=" /guide/ ">', 'chapter', 'https://example.com/guide/chapter'),
    ('<base href="/guide/">', '/chapter', 'https://example.com/chapter'),
    ('<base href="/guide/">', 'https://example.com/fixed', 'https://example.com/fixed'),
])
def test_crawl_resolves_base_href(monkeypatch, base, link, expected):
    start = 'https://example.com/start/index.html'
    calls = []

    def respond(request):
        calls.append(str(request.url))
        html = (f'<html><head>{base}</head><body><main>Start page.</main>'
                f'<a href="{link}">Chapter</a><a href="{link}#section">Same chapter</a></body></html>')
        return httpx.Response(200, text=html if str(request.url) == start else '<main>Chapter content.</main>')

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        monkeypatch.setattr(module.httpx, 'get', client.get)
        monkeypatch.setattr(module.time, 'sleep', lambda duration: None)
        documents = WebsiteBs4Reader(max_depth=2, max_links=3).load_data(start)
    assert calls == [start, expected]
    assert [doc.metadata['source'] for doc in documents] == calls
    assert documents[1].text == 'Chapter content.'


def test_external_base_keeps_domain_filter(monkeypatch):
    start = 'https://example.com/start/index.html'
    calls = []

    def respond(request):
        calls.append(str(request.url))
        return httpx.Response(200, text='''<head><base href="https://other.test/docs/"></head>
            <main>Start page.</main><a href="chapter">External</a>
            <a href="https://example.com/allowed">Allowed</a>'''
            if str(request.url) == start else '<main>Allowed page.</main>')

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        monkeypatch.setattr(module.httpx, 'get', client.get)
        monkeypatch.setattr(module.time, 'sleep', lambda duration: None)
        documents = WebsiteBs4Reader(max_depth=2, max_links=3).load_data(start)
    assert calls == [start, 'https://example.com/allowed']
    assert len(documents) == 2
