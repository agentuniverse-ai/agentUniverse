from copy import deepcopy
from unittest.mock import patch

import pytest

from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.monitor import monitor as monitor_module
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.llm_output import LLMOutput


class _StubLLM:
    @staticmethod
    def get_num_tokens(text: str) -> int:
        return len(text)


def test_get_llm_token_usage_preserves_llm_input():
    llm_input = {
        "kwargs": {
            "messages": [
                {"role": "user", "content": "hello"},
            ]
        }
    }
    original_input = deepcopy(llm_input)

    usage = Monitor.get_llm_token_usage(
        _StubLLM(),
        llm_input,
        LLMOutput(text="response"),
    )

    assert usage["total_tokens"] > 0
    assert llm_input == original_input


@pytest.fixture
def token_usage_trace():
    """Isolate one trace's usage while exercising the real context manager."""
    context_manager = FrameworkContextManager()
    key = "monitor-merge-test_token_usage"
    token = context_manager.set_context(key, {})
    try:
        with patch.object(monitor_module, "AuTraceManager") as trace_manager:
            trace_manager.return_value.get_trace_id.return_value = "monitor-merge-test"
            yield trace_manager.return_value
    finally:
        context_manager.reset_context(key, token)


def test_add_token_usage_preserves_previous_fields_and_inputs(token_usage_trace):
    previous = {"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14}
    current = {"prompt_tokens": 5, "total_tokens": 5, "cached_tokens": 2}
    previous_snapshot = deepcopy(previous)
    current_snapshot = deepcopy(current)

    Monitor.add_token_usage(previous)
    stored_previous = Monitor.get_token_usage()
    Monitor.add_token_usage(current)

    assert Monitor.get_token_usage() == {
        "prompt_tokens": 15,
        "completion_tokens": 4,
        "total_tokens": 19,
        "cached_tokens": 2,
    }
    assert stored_previous == previous_snapshot
    assert previous == previous_snapshot
    assert current == current_snapshot


@pytest.mark.parametrize(
    ("previous", "current"),
    [
        ({"cached_tokens": 2}, "provider detail"),
        ({"cached_tokens": 2}, {"cached_tokens": 3}),
        (10, "unknown"),
        (None, 5),
    ],
)
def test_add_token_usage_keeps_newer_non_additive_value(token_usage_trace, previous, current):
    Monitor.add_token_usage({"prompt_tokens": 10, "meta": previous})
    messages = []
    handler = monitor_module.logger.add(
        messages.append,
        level="DEBUG",
        filter=lambda record: record["name"] == monitor_module.__name__,
    )
    try:
        Monitor.add_token_usage({"prompt_tokens": 5, "meta": current})
    finally:
        monitor_module.logger.remove(handler)

    assert Monitor.get_token_usage() == {"prompt_tokens": 15, "meta": current}
    assert len(messages) == 1
    assert messages[0].record["level"].name == "DEBUG"
    assert "meta" in messages[0].record["message"]
    assert "keeping newer value" in messages[0].record["message"]


@pytest.mark.parametrize("current", [None, {}])
def test_add_token_usage_empty_update_preserves_previous_usage(token_usage_trace, current):
    Monitor.add_token_usage({"prompt_tokens": 10})

    Monitor.add_token_usage(current)

    assert Monitor.get_token_usage() == {"prompt_tokens": 10}


def test_add_token_usage_requires_initialized_trace(token_usage_trace):
    FrameworkContextManager().set_context("monitor-merge-test_token_usage", None)

    Monitor.add_token_usage({"prompt_tokens": 5})

    assert Monitor.get_token_usage() is None


def test_add_token_usage_without_trace_leaves_existing_usage_alone(token_usage_trace):
    Monitor.add_token_usage({"prompt_tokens": 10})
    token_usage_trace.get_trace_id.return_value = None

    Monitor.add_token_usage({"prompt_tokens": 5})

    assert FrameworkContextManager().get_context("monitor-merge-test_token_usage") == {"prompt_tokens": 10}
