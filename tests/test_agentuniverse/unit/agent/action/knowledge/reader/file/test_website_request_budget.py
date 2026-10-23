"""A crawl's max_links limits attempted fetches, including unsuccessful ones."""
import httpx
import pytest

from agentuniverse.agent.action.knowledge.reader.file import website_bs4_reader as module
from agentuniverse.agent.action.knowledge.reader.file.website_bs4_reader import WebsiteBs4Reader


@pytest.mark.parametrize('failure', ['http_error', 'empty', 'transport_error', 'success'])
@pytest.mark.parametrize('override', [False, True])
def test_unsuccessful_fetches_consume_budget(monkeypatch, failure, override):
    root = 'https://example.com/root'
    calls = []
    children = ''.join(f'<a href="/child-{i}">next</a>' for i in range(5))

    def respond(request):
        calls.append(str(request.url))
        if str(request.url) == root:
            return httpx.Response(200, text=f'<main>Root content.</main>{children}')
        if str(request.url).endswith('/child-0'):
            if failure == 'transport_error':
                raise httpx.ConnectError('Connection failed', request=request)
            if failure == 'http_error':
                return httpx.Response(404, text='Not found')
            if failure == 'empty':
                return httpx.Response(200, text='<html><body></body></html>')
        return httpx.Response(200, text='<main>Child content.</main>')

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        monkeypatch.setattr(module.httpx, 'get', client.get)
        monkeypatch.setattr(module.time, 'sleep', lambda duration: None)
        reader = WebsiteBs4Reader(max_depth=2, max_links=20 if override else 2)
        docs = reader.load_data(root, ext_info={'max_links': 2} if override else None)
    assert calls == [root, 'https://example.com/child-0']
    assert len(docs) == (2 if failure == 'success' else 1)


def test_empty_root_uses_single_request_allowance(monkeypatch):
    calls = []

    def respond(request):
        calls.append(str(request.url))
        return httpx.Response(200, text='<a href="/child"></a>'
                              if len(calls) == 1 else '<main>Child content.</main>')

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        monkeypatch.setattr(module.httpx, 'get', client.get)
        monkeypatch.setattr(module.time, 'sleep', lambda duration: None)
        docs = WebsiteBs4Reader(max_depth=2, max_links=1).load_data('https://example.com/root')
    assert calls == ['https://example.com/root']
    assert docs == []


def test_filtered_links_do_not_consume_fetch_budget(monkeypatch):
    calls = []

    def respond(request):
        calls.append(str(request.url))
        return httpx.Response(200, text='''<main>Root.</main>
            <a href="https://other.test/page">external</a><a href="/image.png">image</a>
            <a href="/root#same">same page</a><a href="/child">child</a>'''
            if len(calls) == 1 else '<main>Child.</main>')

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        monkeypatch.setattr(module.httpx, 'get', client.get)
        monkeypatch.setattr(module.time, 'sleep', lambda duration: None)
        docs = WebsiteBs4Reader(max_depth=2, max_links=2).load_data('https://example.com/root')
    assert calls == ['https://example.com/root', 'https://example.com/child']
    assert len(docs) == 2
