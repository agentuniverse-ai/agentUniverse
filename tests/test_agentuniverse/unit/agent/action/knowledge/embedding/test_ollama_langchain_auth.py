"""Check Ollama LangChain authentication through real loopback HTTP requests."""
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread

import pytest

from agentuniverse.agent.action.knowledge.embedding.ollama_embedding import OllamaEmbedding


@pytest.fixture
def endpoint():
    calls = []
    settings = {"authorization": None}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            authorization = self.headers.get("Authorization")
            calls.append((self.path, authorization, body))
            allowed = authorization == settings["authorization"]
            payload = {"embedding": [1.0, 0.0]} if allowed else {"error": "fixture authorization required"}
            data = json.dumps(payload).encode()
            self.send_response(200 if allowed else 401)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        server.daemon_threads = True
        thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}", settings, calls
        finally:
            server.shutdown()
            thread.join(5)
            assert not thread.is_alive()


@pytest.mark.parametrize("key", [None, "", "offline-fixture-token"])
@pytest.mark.parametrize("method", ["embed_query", "embed_documents", "aembed_query", "aembed_documents"])
def test_langchain_conversion_preserves_configured_auth(endpoint, key, method):
    address, settings, calls = endpoint
    expected_header = f"Bearer {key}" if key else None
    settings["authorization"] = expected_header

    async def check():
        embedding = OllamaEmbedding(ollama_base_url=address, ollama_api_key=key,
                                    embedding_model_name="fixture-model")
        try:
            if method.startswith("a"):
                direct = await embedding.async_get_embeddings(["native control"])
            else:
                direct = embedding.get_embeddings(["native control"])
            assert direct == [[1.0, 0.0]]
            sync_client, async_client = embedding.client, embedding.async_client
            converted = embedding.as_langchain()
            assert embedding.client is sync_client and embedding.async_client is async_client

            argument = ["first", "second"] if method.endswith("documents") else "question"
            operation = getattr(converted, method)
            result = await operation(argument) if method.startswith("a") else operation(argument)
            assert result == ([[1.0, 0.0], [1.0, 0.0]] if method.endswith("documents") else [1.0, 0.0])
            assert len(calls) == (3 if method.endswith("documents") else 2)
            assert all(path == "/api/embeddings" and authorization == expected_header
                       and body["model"] == "fixture-model" for path, authorization, body in calls)
            assert not sync_client.is_closed and not async_client.is_closed
            assert embedding.ollama_api_key == key
        finally:
            if embedding.client is not None:
                embedding.client.close()
            if embedding.async_client is not None:
                await embedding.async_client.aclose()

    asyncio.run(check())


@pytest.mark.parametrize("method", ["embed_query", "aembed_query"])
def test_langchain_still_reports_unauthorized_credentials(endpoint, method):
    address, settings, calls = endpoint
    settings["authorization"] = "Bearer required-fixture-token"

    async def check():
        embedding = OllamaEmbedding(ollama_base_url=address, ollama_api_key="wrong-fixture-token",
                                    embedding_model_name="fixture-model")
        try:
            converted = embedding.as_langchain()
            with pytest.raises(ValueError, match="HTTP code: 401"):
                if method.startswith("a"):
                    await getattr(converted, method)("question")
                else:
                    getattr(converted, method)("question")
            assert len(calls) == 1
        finally:
            embedding.client.close()
            await embedding.async_client.aclose()

    asyncio.run(check())

