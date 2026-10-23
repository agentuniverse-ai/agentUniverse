"""Exercise real Anthropic clients against a loopback HTTP server."""
import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

import anthropic
import pytest

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.llm.default.claude_llm import ClaudeLLM


@pytest.fixture
def endpoint():
    requests = []
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append((self.path, json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
            body = json.dumps({
                "id": "fixture", "type": "message", "role": "assistant", "model": "fixture",
                "content": [{"type": "text", "text": "response"}],
                "stop_reason": "end_turn", "stop_sequence": None,
                "usage": {"input_tokens": 2, "output_tokens": 1},
            }).encode()
            self.send_response(self.server.status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Retry-After", "0.001")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.status = 200
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", server, requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.fixture(autouse=True)
def application_config(monkeypatch):
    manager = ApplicationConfigManager()
    monkeypatch.setattr(manager, "_ApplicationConfigManager__app_configer", AppConfiger())
    # Keep test transports isolated from host proxy configuration.
    for name in ("ANTHROPIC_PROXY", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("proxy", [False, True])
@pytest.mark.parametrize("limit", [None, 7])
def test_public_call_accepts_pool_limit_with_or_without_proxy(endpoint, asynchronous, proxy, limit):
    url, _, requests = endpoint
    llm = ClaudeLLM(api_key="offline", model_name="fixture",
                    api_url="http://upstream.invalid" if proxy else url,
                    proxy=url if proxy else None, connection_pool_limits=limit)
    async def call():
        try:
            return await llm.acall(messages=[{"role": "user", "content": "hello"}])
        finally:
            if llm.async_client:
                await llm.async_client.close()
    if asynchronous:
        result = asyncio.run(call())
    else:
        try:
            result = llm.call(messages=[{"role": "user", "content": "hello"}])
        finally:
            if llm.client:
                llm.client.close()
    assert result.text == "response"
    assert len(requests) == 1
    assert requests[0][1]["messages"] == [{"role": "user", "content": "hello"}]
    assert requests[0][0] == ("http://upstream.invalid/v1/messages" if proxy else "/v1/messages")
    client = llm.async_client if asynchronous else llm.client
    if limit is not None:
        transport = client._client._transport
        if proxy:
            transport = next(value for value in client._client._mounts.values() if value is not None)
        assert transport._pool._max_connections == limit


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("retries, attempts", [(0, 1), (1, 2), (None, 3)])
def test_native_retry_budget_controls_real_requests(endpoint, asynchronous, retries, attempts):
    url, server, requests = endpoint
    server.status = 503
    llm = ClaudeLLM(api_key="offline", model_name="fixture", api_url=url, max_retries=retries)
    async def call():
        try:
            await llm.acall(messages=[{"role": "user", "content": "hello"}])
        finally:
            if llm.async_client:
                await llm.async_client.close()
    with pytest.raises(anthropic.APIStatusError):
        if asynchronous:
            asyncio.run(call())
        else:
            try:
                llm.call(messages=[{"role": "user", "content": "hello"}])
            finally:
                if llm.client:
                    llm.client.close()
    assert len(requests) == attempts
