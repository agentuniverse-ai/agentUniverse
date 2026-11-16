"""Run the configured sample through real agents and the OpenAI HTTP client.

Set RUN_LIVE_LLM_TESTS=1, OPENAI_API_KEY, OPENAI_API_BASE and DEBATE_MODEL_NAME
for live validation; otherwise a local HTTP fixture supplies model responses.
"""

# ruff: noqa: S101 - pytest assertions

import asyncio
import json
import os
import shutil
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
import yaml

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.llm.llm_manager import LLMManager


@pytest.fixture(scope="module")
def configured_app(tmp_path_factory, backend):
    """Start the actual application using its TOML and YAML configuration."""
    app = tmp_path_factory.mktemp("debate") / "app"
    shutil.copytree(
        Path(__file__).resolve().parents[2],
        app,
        ignore=shutil.ignore_patterns("__pycache__", ".debate_log_dir", "*.db", "*.log"),
    )
    with pytest.MonkeyPatch.context() as patch:
        patch.chdir(app)
        patch.syspath_prepend(str(app))
        patch.setenv("DEBATE_MODEL_NAME", os.environ["DEBATE_MODEL_NAME"] if backend is None else "integration-model")
        if backend is not None:
            patch.setenv("OPENAI_API_BASE", backend[0])
            patch.setenv("OPENAI_API_KEY", "offline-fixture")
        llm_path = app / "intelligence/agentic/llm/default_openai_llm.yaml"
        llm_config = yaml.safe_load(llm_path.read_text())
        llm_config.update(max_tokens=1024, max_retries=0, request_timeout=90)
        llm_path.write_text(yaml.safe_dump(llm_config))
        AgentUniverse().start(config_path=str(app / "config/config.toml"))
        agent = AgentManager().get_instance_obj("demo_debate_agent")
        assert agent.agent_model.memory["name"] == "demo_memory"
        for name in ("demo_proposer_agent", "demo_critic_agent", "demo_judge_agent"):
            role = AgentManager().get_instance_obj(name)
            assert role.agent_model.memory["name"] == "demo_memory"
            assert role.llm_name == "default_openai_llm"
        yield agent


@pytest.fixture(scope="module")
def backend():
    """Use the supplied live service or a deterministic HTTP server."""
    if os.getenv("RUN_LIVE_LLM_TESTS") == "1":
        assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required for live tests"
        yield None
        return

    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            assert self.path == "/v1/chat/completions"
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append(request)
            index = len(requests) - 1
            role = index % 3
            text = ("proposal", "critique", "")[role]
            if role == 2:
                text = json.dumps(
                    {
                        "score": 40 if index < 3 else 80,
                        "suggestion": "revise" if index < 3 else "accepted",
                        "final_answer": "4",
                    }
                )
            response = json.dumps(
                {
                    "id": "chatcmpl-integration",
                    "object": "chat.completion",
                    "created": 0,
                    "model": request["model"],
                    "choices": [
                        {"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_configured_debate_round_trip(configured_app, backend, asynchronous):
    """Run all roles, parse judgment, and persist the final exchange."""
    agent = configured_app
    if backend is not None:
        backend = backend[1]
        backend.clear()
    session_id = f"debate-integration-{asynchronous}"
    params = {
        "input": "What is 2 + 2? Give a short answer and a brief reason.",
        "debate_rounds": 2,
        "consensus_threshold": 60,
        "session_id": session_id,
    }
    result = (asyncio.run(agent.async_run(**params)) if asynchronous else agent.run(**params)).to_dict()
    rounds = result["debate_results"]
    context = result["execution_context"]
    assert result["output"] and "4" in result["output"]
    assert context["rounds_completed"] == len(rounds)
    assert 1 <= len(rounds) <= 2
    for round_result in rounds:
        assert round_result["proposal_result"]["output"]
        assert round_result["critic_result"]["output"]
        assert isinstance(round_result["judge_result"]["score"], int)
        assert round_result["judge_result"]["output"]["final_answer"]

    memory = MemoryManager().get_instance_obj("demo_memory")
    messages = memory.get(session_id=session_id, agent_id="demo_debate_agent")
    assert any(result["output"] in message.content for message in messages)
    if backend is not None:
        assert len(backend) == 6
        assert len(rounds) == 2
        assert context["consensus_reached"] is True
        assert context["final_score"] == 80
        assert all(request["model"] == "integration-model" for request in backend)
        assert "critique" in json.dumps(backend[3]["messages"])
    print(
        f"mode={'async' if asynchronous else 'sync'} "
        f"model={LLMManager().get_instance_obj('default_openai_llm').model_name} "
        f"rounds={len(rounds)} score={context['final_score']}"
    )
