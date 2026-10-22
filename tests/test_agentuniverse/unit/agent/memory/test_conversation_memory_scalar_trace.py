from unittest.mock import Mock

from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import (
    ConversationMemoryModule,
)


def test_add_trace_wraps_scalar_parameters_before_persisting():
    module = object.__new__(ConversationMemoryModule.__wrapped__)
    module._add_trace_info = Mock()

    module._add_trace(
        {"source": "agent-a", "type": "agent"},
        {"source": "tool-a", "type": "tool"},
        "output",
        "kwargs are mentioned in this result",
        "session-1",
        "trace-1",
        "pair-1",
    )

    call_kwargs = module._add_trace_info.call_args.kwargs
    assert call_kwargs["params"] == {"output": "kwargs are mentioned in this result"}


def test_add_trace_still_unwraps_mapping_kwargs():
    module = object.__new__(ConversationMemoryModule.__wrapped__)
    module._add_trace_info = Mock()

    module._add_trace(
        {"source": "agent-a", "type": "agent"},
        {"source": "tool-a", "type": "tool"},
        "input",
        {"kwargs": {"value": "payload"}},
        "session-1",
        "trace-1",
        "pair-1",
    )

    assert module._add_trace_info.call_args.kwargs["params"] == {"value": "payload"}
