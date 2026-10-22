"""Real HTTP/XML tests for aligning fetched articles with the search ranking."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from urllib.parse import parse_qs, urlsplit

import pytest

from agentuniverse.agent.action.tool.common_tool.pubmed_tool import PubMedTool


@contextmanager
def pubmed_server(search_ids, fetched_ids):
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path)
            calls.append((path.path, parse_qs(path.query)))
            if path.path.endswith('/esearch.fcgi'):
                body = json.dumps({'esearchresult': {'count': '100', 'idlist': search_ids}}).encode()
            else:
                body = ('<PubmedArticleSet>' + ''.join(
                    f'<PubmedArticle><MedlineCitation><PMID>{pmid}</PMID><Article>'
                    f'<ArticleTitle>Paper {pmid}</ArticleTitle></Article></MedlineCitation></PubmedArticle>'
                    for pmid in fetched_ids
                ) + '</PubmedArticleSet>').encode()
            self.send_response(200)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01})
    worker.start()
    try:
        yield PubMedTool(base_url=f'http://127.0.0.1:{server.server_port}', api_key=None, email=None), calls
    finally:
        server.shutdown()
        worker.join(timeout=3)
        server.server_close()


@pytest.mark.parametrize('sort', ['relevance', 'pub_date', 'author', 'journal'])
def test_execute_preserves_search_order_across_fetch(sort):
    with pubmed_server(['30', '10', '20'], ['10', '20', '30']) as (tool, calls):
        result = tool.execute('ranking', sort=sort, max_results=3, page=2)
    assert [p['pmid'] for p in result['papers']] == ['30', '10', '20']
    assert [p['title'] for p in result['papers']] == ['Paper 30', 'Paper 10', 'Paper 20']
    assert result['total_results'] == 100
    assert result['returned_results'] == 3
    assert calls[0][1]['retstart'] == ['3']
    assert calls[1][1]['id'] == ['30,10,20']


@pytest.mark.parametrize('search_ids,fetched_ids,expected', [
    (['30', '10', '20'], ['20', '30'], ['30', '20']),
    (['30', '10'], ['10', '99', '30'], ['30', '10']),
    (['30', '10'], ['10', '30', '30'], ['30', '10']),
    (['30', '10'], ['', '10', '30'], ['30', '10']),
    (['30', '10', '30'], ['10', '30'], ['30', '10']),
    (['30', '10'], ['30', '10'], ['30', '10']),
    (['30'], [], []),
    ([], [], []),
])
def test_partial_or_unexpected_fetch_records_do_not_change_search_membership(search_ids, fetched_ids, expected):
    with pubmed_server(search_ids, fetched_ids) as (tool, calls):
        result = tool.execute('ranking')
    assert [p['pmid'] for p in result['papers']] == expected
    assert result['returned_results'] == len(expected)
    assert len(calls) == (2 if search_ids else 1)
