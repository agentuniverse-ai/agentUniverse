"""Two loopback OpenAI-compatible servers, actual SDK and registered LLMs."""

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import openai
import pytest

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM
from agentuniverse.llm.registered_failover import RegisteredLLMFailover


@pytest.fixture
def servers(monkeypatch):
    monkeypatch.setattr(ApplicationConfigManager(), "_ApplicationConfigManager__app_configer", AppConfiger())
    monkeypatch.setattr(LLMManager(), "_instance_obj_map", {})
    running = []
    requests = []
    clients = []
    async_clients = []
    for name, status in [("unavailable", 503), ("healthy", 200)]:

        def handler(provider, code):
            class Handler(BaseHTTPRequestHandler):
                def log_message(self, *args):
                    pass

                def do_POST(self):
                    request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                    requests.append((provider, request))
                    self.send_response(code)
                    if code != 200:
                        payload = b'{"error":{"message":"synthetic unavailable","type":"server_error"}}'
                        mime = "application/json"
                    elif request["stream"]:
                        chunk = {
                            "id": "local",
                            "object": "chat.completion.chunk",
                            "created": 1,
                            "model": "local-model",
                            "choices": [{"index": 0, "delta": {"content": "local answer"}, "finish_reason": None}],
                        }
                        payload = ("data: " + json.dumps(chunk) + "\n\ndata: [DONE]\n\n").encode()
                        mime = "text/event-stream"
                    else:
                        payload = json.dumps(
                            {
                                "id": "local",
                                "object": "chat.completion",
                                "created": 1,
                                "model": "local-model",
                                "choices": [
                                    {
                                        "index": 0,
                                        "message": {"role": "assistant", "content": "local answer"},
                                        "finish_reason": "stop",
                                    }
                                ],
                                "usage": {"prompt_tokens": 2, "completion_tokens": 2, "total_tokens": 4},
                            }
                        ).encode()
                        mime = "application/json"
                    self.send_header("Content-Type", mime)
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)

            return Handler

        server = ThreadingHTTPServer(("127.0.0.1", 0), handler(name, status))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        running.append((server, thread))
        url = f"http://127.0.0.1:{server.server_port}/v1"
        sync = openai.OpenAI(
            api_key="synthetic-local-only", base_url=url, max_retries=0, http_client=httpx.Client(trust_env=False)
        )
        async_client = openai.AsyncOpenAI(
            api_key="synthetic-local-only", base_url=url, max_retries=0, http_client=httpx.AsyncClient(trust_env=False)
        )
        clients.append(sync)
        async_clients.append(async_client)
        provider = OpenAIStyleLLM(
            name=name,
            api_base=url,
            api_key="synthetic-local-only",
            model_name="local-model",
            client=sync,
            async_client=async_client,
            max_retries=0,
        )
        LLMManager().register(f"local.llm.{name}", provider)
    chain = RegisteredLLMFailover(
        ["unavailable", "healthy"], appname="local", retry_errors=(openai.InternalServerError,)
    )
    try:
        yield chain, requests, async_clients
    finally:
        for client in clients:
            client.close()
        # Async callers close clients in their owning event loop.
        for server, thread in running:
            server.shutdown()
            server.server_close()
            thread.join()


@pytest.mark.parametrize("streaming", [False, True])
def test_sync_sdk_provider_chain(servers, streaming):
    chain, requests, async_clients = servers
    args = {"messages": [{"role": "user", "content": "synthetic prompt"}]}
    result = list(chain.stream(**args))[0] if streaming else chain.call(**args)
    assert result.provider == "healthy" and result.output.text == "local answer"
    assert [name for name, _ in requests] == ["unavailable", "healthy"]
    assert result.attempts[0].error_type == "InternalServerError"

    async def close():
        for client in async_clients:
            await client.close()

    asyncio.run(close())


@pytest.mark.parametrize("streaming", [False, True])
def test_async_sdk_provider_chain(servers, streaming):
    chain, requests, async_clients = servers

    async def run():
        try:
            args = {"messages": [{"role": "user", "content": "synthetic prompt"}]}
            result = [chunk async for chunk in chain.astream(**args)][0] if streaming else await chain.acall(**args)
            assert result.provider == "healthy" and result.output.text == "local answer"
            assert [name for name, _ in requests] == ["unavailable", "healthy"]
        finally:
            for client in async_clients:
                await client.close()

    asyncio.run(run())
