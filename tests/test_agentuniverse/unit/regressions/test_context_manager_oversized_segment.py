import pytest

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import ContextType


def test_context_manager_rejects_segment_larger_than_window_budget():
    manager = ContextManager()
    window = manager.create_context_window(
        "session", max_tokens=10, reserved_tokens=2
    )

    with pytest.raises(ValueError, match="exceeding the window input budget of 8"):
        manager.add_context("session", "x" * 36, ContextType.TASK)

    assert window.total_tokens == 0
    assert window.segment_ids == []
