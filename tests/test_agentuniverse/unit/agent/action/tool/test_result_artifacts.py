"""Real file/Tool/async/planner tests for opt-in artifact result transport."""

import asyncio
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from uuid import UUID

import pytest

from agentuniverse.agent.action.tool.result_artifacts import (
    ArtifactExpiredError,
    ArtifactReadTool,
    ArtifactResultTool,
    LocalToolArtifactStore,
)
from agentuniverse.agent.action.tool.tool import Tool


class EvidenceTool(Tool):
    name: str = "evidence"
    description: str = "Return synthetic evidence"
    input_keys: list = ["query"]

    def execute(self, query):
        return "alpha evidence 中文 " * 20


@pytest.fixture(autouse=True)
def trace_sinks():
    import agentuniverse.base.annotation.trace as trace_module

    with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
        monitor.get_invocation_chain.return_value = []
        yield


def test_real_tool_run_opt_in_and_async(tmp_path):
    store = LocalToolArtifactStore(tmp_path)
    tool = ArtifactResultTool(target=EvidenceTool(), artifact_store=store, threshold_bytes=8)
    expected = EvidenceTool().run(query="x")
    assert tool.run(query="x") == expected
    assert list(tmp_path.iterdir()) == []
    tool.enabled = True
    first = tool.run(query="x")
    second = asyncio.run(tool.async_run(query="x"))
    assert first["id"] != second["id"]
    for reference in (first, second):
        assert reference["sha256"] == hashlib.sha256(expected.encode()).hexdigest()
        assert "alpha" not in json.dumps(reference)
        assert store.read_page(reference["id"], expected_sha256=reference["sha256"])["text"] == expected


def test_planner_uses_reference_then_read_tool(tmp_path):
    from langchain.agents import AgentType, initialize_agent
    from langchain_community.llms.fake import FakeListLLM

    store = LocalToolArtifactStore(tmp_path)
    wrapped = ArtifactResultTool(
        name="fetch_evidence",
        target=EvidenceTool(),
        artifact_store=store,
        enabled=True,
        threshold_bytes=8,
        input_keys=["query"],
    )
    reader = ArtifactReadTool(artifact_store=store)
    fixed_id = "a" * 32
    llm = FakeListLLM(
        responses=[
            'Thought: fetch evidence\nAction: fetch_evidence\nAction Input: {"query":"x"}',
            'Thought: read stored evidence\nAction: artifact_read_tool\nAction Input: {"artifact_id":"'
            + fixed_id
            + '","offset":0,"limit":30}',
            "Thought: finished\nFinal Answer: reviewed stored evidence",
        ]
    )
    planner = initialize_agent(
        [wrapped.as_langchain(), reader.as_langchain()],
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        return_intermediate_steps=True,
    )
    with patch("agentuniverse.agent.action.tool.result_artifacts.uuid.uuid4", return_value=UUID(hex=fixed_id)):
        result = planner.invoke({"input": "Get and read evidence"})
    steps = result["intermediate_steps"]
    assert len(steps) == 2
    assert steps[0][1]["kind"] == "tool_artifact"
    assert "alpha" not in json.dumps(steps[0][1])
    assert steps[1][1]["text"] == EvidenceTool().execute("x")[:30]
    assert steps[1][1]["next_offset"] == 30


def test_json_unicode_pages_roundtrip(tmp_path):
    store = LocalToolArtifactStore(tmp_path, max_page_chars=5)
    value = {"中文": ["🌳", "evidence", 42]}
    reference = store.put(value)
    parts, offset = [], 0
    while True:
        page = store.read_page(reference["id"], offset=offset, limit=5)
        assert len(page["text"]) <= 5
        parts.append(page["text"])
        if page["complete"]:
            assert page["next_offset"] is None
            break
        offset = page["next_offset"]
    assert json.loads("".join(parts)) == value
    assert reference["bytes"] == len("".join(parts).encode())


def test_small_result_does_not_persist(tmp_path):
    store = LocalToolArtifactStore(tmp_path)
    tool = ArtifactResultTool(target=EvidenceTool(), artifact_store=store, enabled=True, threshold_bytes=10000)
    assert isinstance(tool.run(query="x"), str)
    assert list(tmp_path.iterdir()) == []


def test_expired_missing_and_explicit_remove(tmp_path):
    store = LocalToolArtifactStore(tmp_path, ttl_seconds=10)
    with patch("time.time", return_value=100):
        reference = store.put("evidence")
    with patch("time.time", return_value=109):
        assert store.read_page(reference["id"])["text"] == "evidence"
    with patch("time.time", return_value=110):
        with pytest.raises(ArtifactExpiredError):
            store.read_page(reference["id"])
    assert len(list(tmp_path.iterdir())) == 1
    store.remove(reference["id"])
    with pytest.raises(FileNotFoundError):
        store.read_page(reference["id"])


@pytest.mark.parametrize(
    "kwargs", [{"offset": -1}, {"offset": True}, {"limit": 0}, {"limit": 4097}, {"limit": False}, {"offset": 100}]
)
def test_page_bounds(tmp_path, kwargs):
    store = LocalToolArtifactStore(tmp_path)
    reference = store.put("small")
    with pytest.raises(ValueError):
        store.read_page(reference["id"], **kwargs)


@pytest.mark.parametrize("artifact_id", ["../secret", "/etc/passwd", "A" * 32, "a" * 31, None])
def test_ids_cannot_select_paths(tmp_path, artifact_id):
    store = LocalToolArtifactStore(tmp_path)
    with pytest.raises(ValueError):
        store.read_page(artifact_id)


def test_digest_and_corruption(tmp_path):
    store = LocalToolArtifactStore(tmp_path)
    reference = store.put("complete evidence")
    with pytest.raises(ValueError, match="reference digest"):
        store.read_page(reference["id"], expected_sha256="0" * 64)
    path = tmp_path / (reference["id"] + ".json")
    data = json.loads(path.read_bytes())
    data["payload"] = "dGFtcGVyZWQ="
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        store.read_page(reference["id"])


def test_concurrent_same_result_has_unique_complete_artifacts(tmp_path):
    store = LocalToolArtifactStore(tmp_path)
    with ThreadPoolExecutor(max_workers=8) as executor:
        refs = list(executor.map(lambda _: store.put("same" * 100), range(24)))
    assert len({r["id"] for r in refs}) == 24
    assert len({r["sha256"] for r in refs}) == 1
    for reference in refs:
        assert store.read_page(reference["id"])["text"] == "same" * 100
    assert len(list(tmp_path.iterdir())) == 24


def test_failed_publication_and_id_collision_cleanup(tmp_path):
    store = LocalToolArtifactStore(tmp_path)
    with patch("os.link", side_effect=OSError("filesystem failure")):
        with pytest.raises(OSError):
            store.put("result")
    assert list(tmp_path.iterdir()) == []
    with patch("agentuniverse.agent.action.tool.result_artifacts.uuid.uuid4", return_value=UUID(hex="b" * 32)):
        reference = store.put("first")
        with pytest.raises(FileExistsError):
            store.put("second")
    assert store.read_page(reference["id"])["text"] == "first"
    assert len(list(tmp_path.iterdir())) == 1


def test_target_failure_and_cancel_do_not_store(tmp_path):
    store = LocalToolArtifactStore(tmp_path)

    class Failing(Tool):
        def execute(self, **kwargs):
            raise RuntimeError("target failed")

        async def async_execute(self, **kwargs):
            raise asyncio.CancelledError()

    tool = ArtifactResultTool(target=Failing(), artifact_store=store, enabled=True, threshold_bytes=1)
    with pytest.raises(RuntimeError):
        tool.run()
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(tool.async_run())
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("value", [{1: "coercion"}, {"x": (1, 2)}, {"x": float("nan")}, 42])
def test_invalid_json_or_type_is_not_silently_coerced(tmp_path, value):
    store = LocalToolArtifactStore(tmp_path)
    with pytest.raises(ValueError):
        store.put(value)
    assert list(tmp_path.iterdir()) == []


def test_limits_and_empty_artifacts(tmp_path):
    with pytest.raises(ValueError):
        LocalToolArtifactStore(tmp_path, max_bytes=True)
    store = LocalToolArtifactStore(tmp_path, max_bytes=4)
    with pytest.raises(ValueError):
        store.put("too large")
    reference = store.put("")
    page = store.read_page(reference["id"])
    assert page["text"] == "" and page["complete"]


def test_legacy_json_tool_and_public_async_page_reader(tmp_path):
    from agentuniverse.agent.action.tool.tool import ToolInput

    class Legacy(Tool):
        input_keys: list = ["query"]

        def execute(self, tool_input: ToolInput):
            return {"evidence": [tool_input.get_data("query")] * 20}

    store = LocalToolArtifactStore(tmp_path)
    wrapped = ArtifactResultTool(target=Legacy(), artifact_store=store, enabled=True, threshold_bytes=4)
    reference = asyncio.run(wrapped.async_run(query="中文"))
    page_tool = ArtifactReadTool(artifact_store=store)
    page = asyncio.run(page_tool.async_run(artifact_id=reference["id"], expected_sha256=reference["sha256"]))
    assert json.loads(page["text"]) == {"evidence": ["中文"] * 20}


def test_store_failure_propagates_without_truncation(tmp_path):
    store = LocalToolArtifactStore(tmp_path, max_bytes=4)
    wrapped = ArtifactResultTool(target=EvidenceTool(), artifact_store=store, enabled=True, threshold_bytes=1)
    with pytest.raises(ValueError, match="byte limit"):
        wrapped.run(query="x")
    assert list(tmp_path.iterdir()) == []
