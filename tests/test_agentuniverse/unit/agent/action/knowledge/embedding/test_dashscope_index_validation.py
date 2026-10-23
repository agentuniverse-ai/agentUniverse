"""Indexed embedding rows must not silently identify the wrong input text."""
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread

import pytest

from agentuniverse.agent.action.knowledge.embedding import dashscope_embedding as module


@pytest.fixture
def endpoint(monkeypatch):
    settings = {'mode': 'ordered'}
    batches = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            texts = body['input']['texts']
            batches.append(texts)
            rows = [{'text_index': i, 'embedding': [float(text), 1.0]}
                    for i, text in enumerate(texts)]
            mode = settings['mode']
            if mode == 'duplicate':
                rows[1]['text_index'] = 0
            elif mode == 'negative':
                rows[1]['text_index'] = -1
            elif mode == 'out_of_range':
                rows[1]['text_index'] = len(texts)
            elif mode == 'boolean':
                rows[0]['text_index'] = False
            elif mode == 'string':
                rows[0]['text_index'] = '0'
            elif mode == 'mixed':
                del rows[1]['text_index']
            elif mode == 'unindexed':
                for row in rows:
                    del row['text_index']
            elif mode == 'reverse':
                rows.reverse()
            data = json.dumps({'output': {'embeddings': rows}}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    with ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
        server.daemon_threads = True
        monkeypatch.setattr(module, 'DASHSCOPE_EMBEDDING_URL',
                            f'http://127.0.0.1:{server.server_port}/embeddings')
        thread = Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
        thread.start()
        try:
            yield settings, batches
        finally:
            server.shutdown()
            thread.join(5)
            assert not thread.is_alive()


def embed(texts, asynchronous):
    model = module.DashscopeEmbedding(dashscope_api_key='offline', embedding_model_name='text-embedding-v2')
    return asyncio.run(model.async_get_embeddings(texts)) if asynchronous else model.get_embeddings(texts)


@pytest.mark.parametrize('asynchronous', [False, True])
@pytest.mark.parametrize('mode', ['duplicate', 'negative', 'out_of_range', 'boolean', 'string', 'mixed'])
def test_invalid_indices_rejected_despite_matching_count(endpoint, asynchronous, mode):
    settings, batches = endpoint
    settings['mode'] = mode
    with pytest.raises(ValueError, match='text_index'):
        embed(['0', '1', '2'], asynchronous)
    assert batches == [['0', '1', '2']]


@pytest.mark.parametrize('asynchronous', [False, True])
@pytest.mark.parametrize('mode', ['ordered', 'reverse', 'unindexed'])
def test_valid_and_legacy_batches_keep_alignment(endpoint, asynchronous, mode):
    settings, batches = endpoint
    settings['mode'] = mode
    texts = [str(i) for i in range(26)]
    assert embed(texts, asynchronous) == [[float(i), 1.0] for i in range(26)]
    assert batches == [texts[:25], texts[25:]]
