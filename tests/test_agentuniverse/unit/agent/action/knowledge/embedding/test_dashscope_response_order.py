"""Verify batch-local text indices through real sync and async HTTP calls."""
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread

import pytest

from agentuniverse.agent.action.knowledge.embedding import dashscope_embedding as module


@pytest.fixture
def endpoint(monkeypatch):
    calls = []
    settings = {"order": "identity", "indexed": True, "error": False}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            calls.append((self.path, self.headers.get("Authorization"), body))
            entries = []
            for index, text in enumerate(body["input"]["texts"]):
                entry = {"embedding": [float(text), 1.0]}
                if settings["indexed"]:
                    entry["text_index"] = index
                entries.append(entry)
            if settings["order"] == "reverse":
                entries.reverse()
            elif settings["order"] == "rotate":
                entries = entries[1:] + entries[:1]
            payload = ({"code": "InvalidApiKey", "message": "fixture rejected key"}
                       if settings["error"] else {"output": {"embeddings": entries}})
            data = json.dumps(payload).encode()
            self.send_response(401 if settings["error"] else 200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        server.daemon_threads = True
        monkeypatch.setattr(module, "DASHSCOPE_EMBEDDING_URL",
                            f"http://127.0.0.1:{server.server_port}/embeddings")
        thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        thread.start()
        try:
            yield settings, calls
        finally:
            server.shutdown()
            thread.join(5)
            assert not thread.is_alive()


def embed(texts, asynchronous):
    embedding = module.DashscopeEmbedding(dashscope_api_key="offline-fixture",
                                          embedding_model_name="text-embedding-v2")
    if asynchronous:
        return asyncio.run(embedding.async_get_embeddings(texts, text_type="query"))
    return embedding.get_embeddings(texts, text_type="query")


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("count,order", [
    (1, "identity"), (3, "identity"), (3, "reverse"), (3, "rotate"),
    (26, "reverse"), (51, "rotate"),
])
def test_results_follow_input_order_across_batches(endpoint, asynchronous, count, order):
    settings, calls = endpoint
    settings["order"] = order
    texts = [str(index) for index in range(count)]
    result = embed(texts, asynchronous)
    assert [vector[0] for vector in result] == list(range(count))
    assert all(vector[1] == 1.0 for vector in result)
    expected_batches = [texts[start:start + 25] for start in range(0, count, 25)]
    assert [body["input"]["texts"] for _, _, body in calls] == expected_batches
    assert all(path == "/embeddings" and authorization == "Bearer offline-fixture"
               and body["model"] == "text-embedding-v2"
               and body["parameters"] == {"text_type": "query"}
               for path, authorization, body in calls)


@pytest.mark.parametrize("asynchronous", [False, True])
def test_unindexed_responses_retain_legacy_arrival_order(endpoint, asynchronous):
    settings, _ = endpoint
    settings.update(indexed=False, order="reverse")
    assert embed(["0", "1", "2"], asynchronous) == [[2.0, 1.0], [1.0, 1.0], [0.0, 1.0]]


@pytest.mark.parametrize("asynchronous", [False, True])
def test_api_errors_still_propagate(endpoint, asynchronous):
    settings, _ = endpoint
    settings["error"] = True
    with pytest.raises(Exception, match="InvalidApiKey.*fixture rejected key"):
        embed(["0"], asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
def test_empty_input_sends_no_http_request(endpoint, asynchronous):
    _, calls = endpoint
    assert embed([], asynchronous) == []
    assert calls == []

