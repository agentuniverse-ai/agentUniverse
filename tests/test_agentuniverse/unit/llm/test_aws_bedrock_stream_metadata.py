"""Offline regression tests for the ConverseStream trailing metadata events."""

import asyncio
import copy
import socket
from types import SimpleNamespace

import pytest

from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.default.aws_bedrock_llm import AWSBedrockLLM
from agentuniverse.llm.llm_output import LLMOutput


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    def fail_connect(*args, **kwargs):
        pytest.fail("Bedrock stream tests must not use the network")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)
    monkeypatch.setattr(socket, "create_connection", fail_connect)


def events(reason="end_turn", input_tokens=47, output_tokens=20):
    return [
        {"messageStart": {"role": "assistant"}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": "Hello"}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": " world"}}},
        {"contentBlockStop": {"contentBlockIndex": 0}},
        {"messageStop": {"stopReason": reason}},
        {
            "metadata": {
                "usage": {
                    "inputTokens": input_tokens,
                    "outputTokens": output_tokens,
                    "totalTokens": input_tokens + output_tokens,
                },
                "metrics": {"latencyMs": 100},
            }
        },
    ]


def parse(sequence):
    return list(AWSBedrockLLM()._generate_stream_result({"stream": iter(sequence)}))


@pytest.mark.parametrize("asynchronous", [False, True])
def test_complete_stream_preserves_text_stop_and_usage(asynchronous):
    sequence = events()
    original = copy.deepcopy(sequence)
    llm = AWSBedrockLLM(model_name="anthropic.claude-3-haiku-20240307-v1:0")
    requests = []
    messages = [
        {"role": "system", "content": "Be concise."},
        {"role": "user", "content": "hello"},
    ]
    original_messages = copy.deepcopy(messages)

    def converse_stream(**kwargs):
        requests.append(kwargs)
        return {"stream": iter(sequence)}

    llm._client = SimpleNamespace(converse_stream=converse_stream)
    if asynchronous:

        async def run():
            result = await llm._acall(messages, streaming=True)
            return [chunk async for chunk in result]

        chunks = asyncio.run(run())
    else:
        chunks = list(llm._call(messages, streaming=True))
    assert "".join(chunk.text for chunk in chunks) == "Hello world"
    assert [chunk.raw for chunk in chunks] == [sequence[i] for i in (1, 2, 4, 5)]
    assert chunks[-2].finish_reason == "stop"
    assert chunks[-1].usage.prompt_tokens == 47
    assert chunks[-1].usage.completion_tokens == 20
    assert chunks[-1].usage.total_tokens == 67
    assert sum(chunk.usage is not None for chunk in chunks) == 1
    assert sequence == original
    assert messages == original_messages
    assert len(requests) == 1
    assert requests[0]["system"] == [{"text": "Be concise."}]
    assert requests[0]["messages"] == [{"role": "user", "content": [{"text": "hello"}]}]


@pytest.mark.parametrize(
    "reason, expected",
    [
        ("end_turn", "stop"),
        ("stop_sequence", "stop"),
        ("max_tokens", "length"),
        ("tool_use", "tool_calls"),
        ("guardrail_intervened", "content_filter"),
        ("content_filtered", "content_filter"),
        ("malformed_model_output", "error"),
        ("malformed_tool_use", "error"),
        ("model_context_window_exceeded", "length"),
        ("future_reason", None),
    ],
)
def test_stop_reason_is_normalized_without_discarding_raw(reason, expected):
    event = {"messageStop": {"stopReason": reason}}
    chunks = parse([event])
    assert len(chunks) == 1
    assert chunks[0].text == ""
    assert chunks[0].finish_reason == expected
    assert chunks[0].raw == event
    assert chunks[0].usage is None


@pytest.mark.parametrize("input_tokens, output_tokens", [(0, 0), (47, 20)])
def test_usage_values_are_not_estimated(input_tokens, output_tokens):
    chunks = parse(events(input_tokens=input_tokens, output_tokens=output_tokens))
    assert chunks[-1].usage.prompt_tokens == input_tokens
    assert chunks[-1].usage.completion_tokens == output_tokens


def test_usage_is_consumable_by_monitor_without_tokenizer_fallback():
    chunks = parse(events())
    result = LLMOutput(
        text="".join(chunk.text for chunk in chunks), usage=next((chunk.usage for chunk in chunks if chunk.usage), None)
    )

    def fail_tokenizer(text):
        pytest.fail("Reported usage must take precedence over token estimates")

    usage = Monitor.get_llm_token_usage(
        SimpleNamespace(get_num_tokens=fail_tokenizer),
        {"kwargs": {"messages": [{"role": "user", "content": "hi"}]}},
        result,
    )
    assert usage["prompt_tokens"] == 47
    assert usage["completion_tokens"] == 20
    assert usage["total_tokens"] == 67


def test_missing_metadata_does_not_invent_usage():
    chunks = parse(events()[:-1])
    assert "".join(chunk.text for chunk in chunks) == "Hello world"
    assert all(chunk.usage is None for chunk in chunks)


def test_exception_after_stop_is_not_silently_swallowed():
    def interrupted():
        yield {"messageStop": {"stopReason": "end_turn"}}
        message = "interrupted before metadata"
        raise OSError(message)

    with pytest.raises(RuntimeError, match="interrupted before metadata"):
        parse(interrupted())


def test_events_match_real_sdk_response_shapes():
    botocore = pytest.importorskip("botocore.session")
    from botocore.validate import validate_parameters

    model = botocore.get_session().get_service_model("bedrock-runtime")
    shape = model.operation_model("ConverseStream").output_shape.members["stream"]
    for event in events():
        validate_parameters(event, shape)
    assert parse(events())[-1].usage.total_tokens == 67


def test_real_sdk_event_stream_retains_trailing_metadata():
    pytest.importorskip("botocore")
    import json
    import struct
    import zlib

    from botocore.eventstream import EventStream
    from botocore.parsers import EventStreamJSONParser
    from botocore.session import get_session

    # Encode AWS event-stream frames locally; the real SDK decodes their CRCs,
    # headers and payloads before the adapter receives any event dictionaries.
    frames = []
    for event in events():
        name, payload = next(iter(event.items()))
        headers = b""
        for key, value in [(":message-type", "event"), (":event-type", name), (":content-type", "application/json")]:
            key, value = key.encode(), value.encode()
            headers += bytes([len(key)]) + key + b"\x07" + struct.pack(">H", len(value)) + value
        payload = json.dumps(payload).encode()
        prelude = struct.pack(">II", 16 + len(headers) + len(payload), len(headers))
        frame = prelude + struct.pack(">I", zlib.crc32(prelude)) + headers + payload
        frames.append(frame + struct.pack(">I", zlib.crc32(frame)))
    model = get_session().get_service_model("bedrock-runtime")
    shape = model.operation_model("ConverseStream").output_shape.members["stream"]
    raw_stream = SimpleNamespace(stream=lambda: iter(frames))
    sdk_stream = EventStream(raw_stream, shape, EventStreamJSONParser(), "ConverseStream")
    chunks = parse(sdk_stream)
    assert "".join(chunk.text for chunk in chunks) == "Hello world"
    assert chunks[-1].usage.total_tokens == 67
