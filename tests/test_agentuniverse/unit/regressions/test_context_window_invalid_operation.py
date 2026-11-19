import pytest

from agentuniverse.agent.context.context_model import ContextWindow


def test_invalid_token_operation_is_not_silently_ignored():
    window = ContextWindow(session_id="session", total_tokens=10)

    with pytest.raises(ValueError, match="Unsupported token operation: replace"):
        window.update_total_tokens(5, operation="replace")

    assert window.total_tokens == 10
