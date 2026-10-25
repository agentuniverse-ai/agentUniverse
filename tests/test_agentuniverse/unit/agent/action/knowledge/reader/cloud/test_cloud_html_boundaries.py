"""Cloud HTML readers should distinguish inline markup from text boundaries."""
from types import SimpleNamespace
import sys

import pytest

from agentuniverse.agent.action.knowledge.reader.cloud.google_docs_reader import GoogleDocsReader
from agentuniverse.agent.action.knowledge.reader.cloud.confluence_reader import ConfluenceReader


@pytest.mark.parametrize('reader_class', [GoogleDocsReader, ConfluenceReader])
@pytest.mark.parametrize('html, expected', [
    ('<p>micro<strong>service</strong> architecture</p>', 'microservice architecture'),
    ('<p>Revenue <b>$10</b> million.</p>', 'Revenue $10 million.'),
    ('<p>你好<b>世界</b>！</p>', '你好世界！'),
    ('<p><a href="#">alpha</a><span>beta</span></p>', 'alphabeta'),
    ('<p>A &amp; <code>B</code></p>', 'A & B'),
    ('<ul><li>Alpha <em>one</em></li><li>Beta</li></ul>', 'Alpha one\nBeta'),
    ('<p>First</p><p>Second</p>', 'First\nSecond'),
    ('<div>Before<br>after</div>', 'Before\nafter'),
    ('<div><h2>Heading</h2><p>Body</p></div>', 'Heading\nBody'),
    ('<table><tr><td>Cell <b>one</b></td><td>Two</td></tr></table>', 'Cell one\nTwo'),
    ('<html><head><title>Title</title></head><body>Plain body</body></html>', 'Title\nPlain body'),
    ('<p>Visible</p><script>hidden()</script><style>.x{}</style><noscript>hidden</noscript>', 'Visible'),
])
def test_native_html_conversion(reader_class, html, expected):
    assert reader_class()._html_to_text(html) == expected


def test_google_docs_public_load_preserves_inline_words(monkeypatch):
    monkeypatch.setattr(GoogleDocsReader, '_build_drive_service', lambda self, info: object())
    monkeypatch.setattr(GoogleDocsReader, '_export_html', lambda self, drive, file_id:
                        '<p>micro<strong>service</strong> facts</p><p>Next paragraph.</p>')
    docs = GoogleDocsReader().load_data('doc-1', ext_info={'project': 'example'})
    assert docs[0].text == 'microservice facts\nNext paragraph.'
    assert docs[0].metadata == {'source': 'google_docs', 'doc_id': 'doc-1', 'project': 'example'}


def test_confluence_public_load_preserves_inline_words(monkeypatch):
    calls = []

    def get_page(page_id, **kwargs):
        calls.append((page_id, kwargs))
        return {'title': 'Example', 'version': {'number': 3}, 'body': {'view': {'value':
                '<p>micro<strong>service</strong> facts</p><p>Next paragraph.</p>'}}}

    # Replace only the external Confluence client, retaining native HTML parsing.
    monkeypatch.setitem(sys.modules, 'atlassian', SimpleNamespace(
        Confluence=lambda **kwargs: SimpleNamespace(get_page_by_id=get_page)))
    docs = ConfluenceReader().load_data('page-1', ext_info={
        'site_url': 'https://example.atlassian.net', 'username': 'offline', 'token': 'offline-token'})
    assert docs[0].text == 'microservice facts\nNext paragraph.'
    assert docs[0].metadata['title'] == 'Example'
    assert docs[0].metadata['version'] == 3
    assert 'token' not in docs[0].metadata
    assert calls == [('page-1', {'expand': 'body.view,version,metadata.labels'})]
