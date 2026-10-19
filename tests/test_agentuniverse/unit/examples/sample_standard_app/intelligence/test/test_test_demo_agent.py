# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the demo agent example's output-stream helper.

The example module itself requires a full ``AgentUniverse`` boot and an LLM
backend, so only the deterministic queue consumer ``DemoAgentTest.read_output``
is covered here: it relays every queued message to stdout until the EOF
sentinel ``{"type": "EOF"}`` is observed.  The source module is loaded through
``importlib`` so its ``unittest.TestCase`` subclass is not re-collected by
pytest and does not trigger a framework boot.
"""

import importlib
import queue

_demo_agent_module = importlib.import_module(
    "examples.sample_standard_app.intelligence.test.test_demo_agent"
)

EOF_MARKER = '{"type": "EOF"}'


def _agent():
    # Build the test case without running setUp, which would boot the framework.
    return _demo_agent_module.DemoAgentTest(methodName="read_output")


def test_read_output_prints_messages_until_eof(capsys):
    stream = queue.Queue()
    for message in ["first message", "second message", EOF_MARKER]:
        stream.put(message)

    _agent().read_output(stream)

    captured = capsys.readouterr().out
    assert "first message" in captured
    assert "second message" in captured
    assert EOF_MARKER not in captured


def test_read_output_with_leading_eof_prints_nothing(capsys):
    stream = queue.Queue()
    stream.put(EOF_MARKER)

    _agent().read_output(stream)

    captured = capsys.readouterr().out
    assert captured.strip() == ""


def test_read_output_handles_many_messages(capsys):
    stream = queue.Queue()
    for index in range(5):
        stream.put(f"message-{index}")
    stream.put(EOF_MARKER)

    _agent().read_output(stream)

    captured = capsys.readouterr().out
    for index in range(5):
        assert f"message-{index}" in captured


def test_read_output_preserves_message_content(capsys):
    stream = queue.Queue()
    stream.put('{"text": "hello demo agent"}')
    stream.put(EOF_MARKER)

    _agent().read_output(stream)

    captured = capsys.readouterr().out
    assert 'hello demo agent' in captured


def test_read_output_ignores_content_after_eof(capsys):
    stream = queue.Queue()
    stream.put("visible message")
    stream.put(EOF_MARKER)
    stream.put("hidden message")

    _agent().read_output(stream)

    captured = capsys.readouterr().out
    assert "visible message" in captured
    assert "hidden message" not in captured
