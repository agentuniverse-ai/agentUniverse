"""Elasticsearch bulk persistence must preserve data and report item failures."""

import json

import httpx
import pytest

from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.conversation_memory.memory_storage.es_conversation_memory_storage import (
    DefaultMemoryConverter,
    ElasticsearchMemoryStorage,
)


@pytest.mark.parametrize("additional_args", [{"step": 2, "nested": {"ok": True}}, {}, None])
def test_bulk_round_trip_preserves_additional_args(additional_args):
    """Top-level conversation arguments, not similarly named metadata, are stored."""
    requests = []

    def handler(request):
        requests.append(request)
        if request.url.path.endswith("/_search"):
            document = json.loads(requests[0].content.splitlines()[1])
            return httpx.Response(200, json={"hits": {"hits": [{"_id": "m1", "_source": document}]}})
        return httpx.Response(200, json={"errors": False, "items": [{"index": {"status": 201}}]})

    with httpx.Client(base_url="http://offline.invalid", transport=httpx.MockTransport(handler)) as client:
        converter = DefaultMemoryConverter("memory")
        storage = ElasticsearchMemoryStorage.model_construct(client=client, memory_converter=converter)
        message = ConversationMessage(id="m1", content="hello", metadata={"additional_args": {"wrong": 1}},
                                      additional_args=additional_args)
        assert storage.add([message], session_id="session") is None
        assert len(requests) == 1
        request = requests[0]
        assert request.url.path == "/memory/_bulk"
        assert request.headers["content-type"] == "application/x-ndjson"
        assert request.content.endswith(b"\n")
        action, document = map(json.loads, request.content.splitlines())
        assert action == {"index": {"_index": "memory", "_id": "m1"}}
        assert document["additional_args"] == additional_args
        restored, = storage.get(session_id="session")
        assert len(requests) == 2
        assert restored.additional_args == additional_args
        assert restored.content == "hello"
        assert restored.conversation_id == "session"


@pytest.mark.parametrize("statuses", [[400], [201, 400], [429]])
def test_bulk_item_failures_raise_without_retry_or_response_content(statuses):
    """HTTP success does not mean every item was indexed; avoid replaying successes."""
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"errors": True, "items": [
            {"index": {"status": status, "error": {"reason": "private document contents"}}}
            if status >= 400 else {"index": {"status": status}} for status in statuses
        ]})

    with httpx.Client(base_url="http://offline.invalid", transport=httpx.MockTransport(handler)) as client:
        storage = ElasticsearchMemoryStorage.model_construct(
            client=client, memory_converter=DefaultMemoryConverter("memory"))
        messages = [ConversationMessage(content="hello", metadata={}) for _ in statuses]
        with pytest.raises(RuntimeError, match="some messages may have been stored") as error:
            storage.add(messages, session_id="session")
        assert "private document contents" not in str(error.value)
        assert len(requests) == 1


def test_bulk_http_error_remains_an_error():
    """An HTTP error must not be parsed as a successful bulk response."""
    with httpx.Client(base_url="http://offline.invalid", transport=httpx.MockTransport(
        lambda request: httpx.Response(503, text="service unavailable")
    )) as client:
        storage = ElasticsearchMemoryStorage.model_construct(
            client=client, memory_converter=DefaultMemoryConverter("memory"))
        with pytest.raises(Exception, match="Failed to add documents: service unavailable"):
            storage.add([ConversationMessage(content="hello", metadata={})])


def test_empty_bulk_does_not_send_request():
    """An empty add remains a no-op without requesting a bulk response."""
    def unexpected_request(request):
        pytest.fail("Empty bulk should not send a request")

    with httpx.Client(base_url="http://offline.invalid", transport=httpx.MockTransport(unexpected_request)) as client:
        storage = ElasticsearchMemoryStorage.model_construct(
            client=client, memory_converter=DefaultMemoryConverter("memory"))
        assert storage.add([]) is None
