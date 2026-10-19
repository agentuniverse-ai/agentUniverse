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
        "plain result",
        "session-1",
        "trace-1",
        "pair-1",
    )

    call_kwargs = module._add_trace_info.call_args.kwargs
    assert call_kwargs["params"] == {"output": "plain result"}
