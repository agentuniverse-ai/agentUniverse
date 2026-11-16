"""Fragments identify locations within a document, not additional crawl pages."""
import httpx
import pytest

from agentuniverse.agent.action.knowledge.reader.file import website_bs4_reader as module


def crawl(monkeypatch, start, pages, **limits):
    requested = []

    def get(url, **kwargs):
        requested.append(url)
        # A fragment is not part of the HTTP resource requested from the server.
        html = pages[url.split('#', 1)[0]]
        return httpx.Response(200, text=html, request=httpx.Request('GET', url))

    monkeypatch.setattr(module.httpx, 'get', get)
    monkeypatch.setattr(module.time, 'sleep', lambda _: None)
    reader = module.WebsiteBs4Reader(**limits)
    docs = reader.load_data(start, ext_info={'collection': 'fixture'})
    return docs, requested


@pytest.mark.parametrize('suffix', ['', '#intro'])
def test_same_page_anchors_do_not_consume_page_budget(monkeypatch, suffix):
    root = 'https://example.com/docs'
    pages = {
        root: '<div>Root</div><a href="#one">One</a><a href="#two">Two</a>'
              '<a href="/next#section">Next</a>',
        'https://example.com/next': '<div>Next page</div>',
    }
    docs, calls = crawl(monkeypatch, root + suffix, pages, max_depth=2, max_links=2)
    assert calls == [root, 'https://example.com/next']
    assert [d.text for d in docs] == ['Root', 'Next page']
    assert [d.metadata for d in docs] == [
        {'source': url, 'collection': 'fixture'} for url in calls
    ]


def test_different_fragments_of_linked_page_are_fetched_once(monkeypatch):
    root = 'https://example.com/'
    pages = {
        root: '<div>Root</div><a href="/next#a">A</a><a href="/next#b">B</a>'
              '<a href="/next">Bare</a>',
        'https://example.com/next': '<div>Next page</div><a href="#self">Self</a>',
    }
    docs, calls = crawl(monkeypatch, root, pages, max_depth=3, max_links=10)
    assert calls == [root, 'https://example.com/next']
    assert len(docs) == 2


def test_query_variants_and_encoded_hash_remain_distinct(monkeypatch):
    root = 'https://example.com/'
    urls = ['https://example.com/page?q=1', 'https://example.com/page?q=2',
            'https://example.com/a%23b?q=%23']
    pages = {root: '<div>Root</div>' + ''.join(
        f'<a href="{url}#section">Link</a>' for url in urls
    )}
    pages.update({url: f'<div>{index}</div>' for index, url in enumerate(urls)})
    docs, calls = crawl(monkeypatch, root, pages, max_depth=2, max_links=4)
    assert calls == [root, *urls]
    assert [d.metadata['source'] for d in docs] == calls


@pytest.mark.parametrize('limits', [{'max_depth': 1, 'max_links': 10},
                                  {'max_depth': 3, 'max_links': 1}])
def test_existing_depth_and_link_limits_remain(monkeypatch, limits):
    root = 'https://example.com/'
    docs, calls = crawl(monkeypatch, root, {
        root: '<div>Root</div><a href="/next">Next</a>',
    }, **limits)
    assert calls == [root]
    assert len(docs) == 1
