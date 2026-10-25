"""Truncation markers share the allocated character/token budget."""
import pytest

from agentuniverse.agent.context.compressor.truncate_compressor import TruncateCompressor
from agentuniverse.agent.context.context_model import ContextMetadata, ContextPriority, ContextSegment, ContextType


@pytest.mark.parametrize('priority', [ContextPriority.HIGH, ContextPriority.CRITICAL])
@pytest.mark.parametrize('budget,marker', [(20, '... [truncated]'), (10, ''),
                                         (1, '... [truncated]'), (10, 'marker' * 30)])
def test_marker_is_included_in_reported_budget(budget, marker, priority):
    source = ContextSegment(type=ContextType.CONVERSATION,
                            priority=priority, content='x' * 400,
                            tokens=100, session_id='session', metadata=ContextMetadata(decay_rate=0))
    before = source.model_dump()
    result, metrics = TruncateCompressor(min_segment_tokens=1, truncate_marker=marker).compress(
        [source], budget)
    assert len(result) == 1
    compressed = result[0]
    # This fixture has exactly four characters per estimated token.
    assert len(compressed.content) <= budget * 4
    assert compressed.tokens == budget
    assert metrics.compressed_tokens == budget
    assert compressed.tokens >= 0
    assert compressed.id == source.id
    assert compressed.session_id == source.session_id
    assert source.model_dump() == before
    if len(marker) <= budget * 4:
        assert compressed.content == 'x' * (budget * 4 - len(marker)) + marker
    else:
        assert compressed.content == marker[:budget * 4]


def test_untruncated_segment_does_not_gain_marker_or_tokens():
    source = ContextSegment(type=ContextType.CONVERSATION, content='unchanged', tokens=3)
    result, metrics = TruncateCompressor().compress([source], 20)
    assert result == [source]
    assert result[0] is source
    assert metrics.compressed_tokens == 3
