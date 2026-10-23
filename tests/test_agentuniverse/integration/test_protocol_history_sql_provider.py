"""SQLite restart -> public ChatPrompt -> real OpenAI SDK -> local HTTP server.

No mocked memory, replaced provider client, paid API, image fetch or tool execution.
"""

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import (
    DefaultMemoryConverter,
    SqlAlchemyMemoryStorage,
)
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.memory.protocol_history import ProtocolHistory
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import SQLDBWrapperConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.llm.openai_llm import OpenAILLM
from agentuniverse.prompt.chat_prompt import ChatPrompt


def open_storage(path):
    config = SQLDBWrapperConfiger()
    config.db_uri = f"sqlite:///{path}"
    wrapper = SQLDBWrapper(db_wrapper_configer=config)
    converter = DefaultMemoryConverter("history")
    converter.model_class.metadata.create_all(wrapper.sql_database._engine)
    storage = SqlAlchemyMemoryStorage(memory_converter=converter)
    storage._sqldb_wrapper = wrapper
    return storage, wrapper


@pytest.fixture
def endpoint():
    received = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            received.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            response = json.dumps(
                {
                    "id": "completion-local",
                    "object": "chat.completion",
                    "created": 1,
                    "model": "local-test",
                    "choices": [
                        {"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "verified"}}
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_sqlite_restart_prompt_public_adapter_and_real_sdk(tmp_path, endpoint, mode, monkeypatch):
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    wire = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "literal {account}: 中文"},
                {"type": "image_url", "image_url": {"url": "https://example.invalid/image", "detail": "low"}},
            ],
        },
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {"id": "c1", "type": "function", "function": {"name": "read", "arguments": '{ "value": "{x}" }'}},
                {"id": "c2", "type": "function", "function": {"name": "read", "arguments": '{"value":"中文"}'}},
            ],
        },
        {"role": "tool", "tool_call_id": "c2", "content": "二", "name": "read"},
        {"role": "tool", "tool_call_id": "c1", "content": "literal {response}"},
        {"role": "assistant", "content": "OK"},
    ]
    path = tmp_path / "history.sqlite"
    storage, wrapper = open_storage(path)
    storage.add(
        ProtocolHistory.from_wire(wire, message_ids=[f"m{i}" for i in range(len(wire))]),
        session_id="session",
        agent_id="agent",
    )
    storage.add([Message(type="human", content="other session")], session_id="other", agent_id="agent")
    wrapper.sql_database._engine.dispose()
    del storage, wrapper
    reopened, second_wrapper = open_storage(path)
    try:
        history = reopened.get(session_id="session", agent_id="agent", top_k=100)
        assert ProtocolHistory.to_wire(history) == wire
        assert [m.id for m in ProtocolHistory.as_langchain(history)] == [f"m{i}" for i in range(len(wire))]
        prompt = ChatPrompt(
            messages=[Message(type="system", content="Policy: {policy}"), Message(type="human", content="{input}")]
        )
        formatted = prompt.as_langchain_with_history(history, history_index=1)
        assert set(formatted.input_variables) == {"policy", "input"}
        config = Configer()
        config.value = {"BASE_INFO": {"appname": "protocol-test"}}
        manager = ApplicationConfigManager()
        monkeypatch.setattr(manager, "_ApplicationConfigManager__app_configer", AppConfiger().load_by_configer(config))
        llm = OpenAILLM(
            model_name="local-test",
            openai_api_key="local-test-key",
            openai_organization=None,
            openai_proxy=None,
            openai_api_base=endpoint[0],
            max_retries=0,
            request_timeout=5,
        )
        if mode == "sync":
            try:
                assert (formatted | llm.as_langchain()).invoke(
                    {"policy": "test", "input": "next"}
                ).content == "verified"
            finally:
                if llm.client is not None:
                    llm.client.close()
        else:

            async def invoke():
                try:
                    result = await (formatted | llm.as_langchain()).ainvoke({"policy": "test", "input": "next"})
                    assert result.content == "verified"
                finally:
                    if llm.async_client is not None:
                        await llm.async_client.close()

            asyncio.run(invoke())
        assert endpoint[1][-1]["messages"] == [
            {"role": "system", "content": "Policy: test"},
            *wire,
            {"role": "user", "content": "next"},
        ]
        assert ProtocolHistory.to_wire(history) == wire
    finally:
        second_wrapper.sql_database._engine.dispose()


@pytest.mark.parametrize("index", [-1, 2, True, "0"])
def test_prompt_history_insertion_index(index):
    with pytest.raises(ValueError):
        ChatPrompt(messages=[Message(type="human", content="{input}")]).as_langchain_with_history(
            [], history_index=index
        )
