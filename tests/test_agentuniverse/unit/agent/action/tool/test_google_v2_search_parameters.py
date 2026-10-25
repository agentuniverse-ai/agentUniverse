"""Extra search parameters must survive the real LangChain HTTP wrappers."""
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from urllib.parse import parse_qs, urlsplit

import aiohttp
import pytest
import requests

from agentuniverse.agent.action.tool.common_tool.google_search_tool_v2 import GoogleSearchTool, GoogleScholarSearchTool


@pytest.fixture
def endpoint(monkeypatch):
    received = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            received.append(parse_qs(urlsplit(self.path).query))
            data = json.dumps({'organic': [{'title': 'Title', 'snippet': 'Result snippet'}]}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    with ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
        server.daemon_threads = True
        local = f'http://127.0.0.1:{server.server_port}/search'
        original_sync = requests.Session.request
        original_async = aiohttp.ClientSession._request

        def redirect_sync(self, method, url, **kwargs):
            return original_sync(self, method, local if str(url).startswith('https://google.serper.dev/') else url, **kwargs)

        async def redirect_async(self, method, url, **kwargs):
            return await original_async(self, method, local if str(url).startswith('https://google.serper.dev/') else url, **kwargs)

        monkeypatch.setattr(requests.Session, 'request', redirect_sync)
        monkeypatch.setattr(aiohttp.ClientSession, '_request', redirect_async)
        thread = Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
        thread.start()
        try:
            yield received
        finally:
            server.shutdown()
            thread.join(5)
            assert not thread.is_alive()


@pytest.mark.parametrize('tool_class', [GoogleSearchTool, GoogleScholarSearchTool])
@pytest.mark.parametrize('asynchronous', [False, True])
@pytest.mark.parametrize('options', [
    {'page': 2},
    {'tbs': 'qdr:y'},
    {'page': 3, 'tbs': 'qdr:m', 'location': 'Berlin, Germany'},
    {},
])
def test_extra_search_options_reach_native_http(endpoint, tool_class, asynchronous, options):
    tool = tool_class(serper_api_key='offline')
    result = (asyncio.run(tool.async_execute(query='retrieval', k=3, **options))
              if asynchronous else tool.execute(query='retrieval', k=3, **options))
    assert 'Result snippet' in result
    assert len(endpoint) == 1
    request = endpoint[0]
    for key, value in options.items():
        assert request.get(key) == [str(value)]
    assert request['num'] == ['3']
    assert 'retrieval' in request['q'][0]


@pytest.mark.parametrize('asynchronous', [False, True])
def test_scholar_region_options_use_wrapper_configuration(endpoint, asynchronous):
    tool = GoogleScholarSearchTool(serper_api_key='offline')
    options = {'gl': 'de', 'hl': 'de'}
    result = (asyncio.run(tool.async_execute(query='retrieval', **options))
              if asynchronous else tool.execute(query='retrieval', **options))
    assert 'Result snippet' in result
    assert endpoint[0]['gl'] == ['de']
    assert endpoint[0]['hl'] == ['de']
