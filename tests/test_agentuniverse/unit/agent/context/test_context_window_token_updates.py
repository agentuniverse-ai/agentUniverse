"""Public token updates preserve the ContextWindow count invariant atomically."""
from datetime import datetime

import pytest

from agentuniverse.agent.context.context_model import ContextWindow


@pytest.mark.parametrize('operation', ['add', 'remove'])
@pytest.mark.parametrize('count', [-20, 1.5, True])
def test_invalid_counts_do_not_change_budget_state(operation, count):
    window = ContextWindow(session_id='test', total_tokens=10,
                           last_updated=datetime(2026, 1, 1))
    before = window.model_dump()
    with pytest.raises(ValueError):
        window.update_total_tokens(count, operation)
    assert window.model_dump() == before


@pytest.mark.parametrize('operation', ['subtract', '', None])
def test_unknown_operation_does_not_change_budget_state(operation):
    window = ContextWindow(session_id='test', total_tokens=10,
                           last_updated=datetime(2026, 1, 1))
    before = window.model_dump()
    with pytest.raises(ValueError):
        window.update_total_tokens(2, operation)
    assert window.model_dump() == before


@pytest.mark.parametrize('count,operation,expected', [
    (0, 'add', 10), (5, 'add', 15), (5, 'remove', 5), (20, 'remove', 0),
])
def test_valid_updates_keep_integer_counts_and_refresh_timestamp(count, operation, expected):
    window = ContextWindow(session_id='test', total_tokens=10,
                           last_updated=datetime(2026, 1, 1))
    window.update_total_tokens(count, operation)
    assert window.total_tokens == expected
    assert type(window.total_tokens) is int
    assert window.last_updated > datetime(2026, 1, 1)
    assert window.calculate_available_tokens() == window.calculate_input_tokens() - expected
