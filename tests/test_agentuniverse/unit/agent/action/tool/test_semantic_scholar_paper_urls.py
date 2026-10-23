"""Paper-page URL decorations must not become Semantic Scholar identifiers."""
import json
from urllib.parse import urlsplit

import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool import SemanticScholarTool

PAPER_ID = 'a' * 40
OTHER_ID = 'b' * 40


@pytest.fixture
def requests_seen(monkeypatch):
    seen = []

    def send(session, request, **kwargs):
        seen.append(request)
        response = requests.Response()
        response.request = request
        response.status_code = 200
        response.headers['Content-Type'] = 'application/json'
        path = urlsplit(request.url).path
        if request.method == 'POST':
            data = [{'paperId': identifier} for identifier in json.loads(request.body)['ids']]
        elif path.endswith(('/citations', '/references')):
            data = {'data': []}
        else:
            data = {'paperId': PAPER_ID}
        response._content = json.dumps(data).encode()
        return response

    monkeypatch.setattr(requests.Session, 'send', send)
    return seen


@pytest.mark.parametrize('mode', ['paper', 'citations', 'references'])
@pytest.mark.parametrize('source', [
    f'https://www.semanticscholar.org/paper/A-paper-title/{PAPER_ID}?utm_source=email#figure',
    f'https://semanticscholar.org/paper/{PAPER_ID}?redirect=a/b',
    f'https://semanticscholar.org/paper/A-title/{PAPER_ID}/',
    f'https://semanticscholar.org/paper/A-title/{PAPER_ID}',
    PAPER_ID.upper(),
])
def test_public_operations_normalize_paper_page_urls(requests_seen, mode, source):
    result = SemanticScholarTool(api_key=None).execute(source, mode=mode)
    assert 'error' not in result
    assert result['query'] == PAPER_ID
    suffix = '' if mode == 'paper' else '/' + mode
    assert urlsplit(requests_seen[0].url).path == '/graph/v1/paper/' + PAPER_ID + suffix
    assert len(requests_seen) == 1


def test_batch_uses_paper_ids_from_decorated_urls(requests_seen):
    urls = [f'https://semanticscholar.org/paper/First/{PAPER_ID}?utm_source=email',
            f'https://semanticscholar.org/paper/{OTHER_ID}#abstract']
    result = SemanticScholarTool(api_key=None).execute(urls, mode='batch')
    assert 'error' not in result
    assert result['query'] == [PAPER_ID, OTHER_ID]
    assert json.loads(requests_seen[0].body) == {'ids': [PAPER_ID, OTHER_ID]}
    assert [paper['paper_id'] for paper in result['papers']] == [PAPER_ID, OTHER_ID]
