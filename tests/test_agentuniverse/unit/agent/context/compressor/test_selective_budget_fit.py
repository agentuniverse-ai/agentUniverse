"""Optional segments must fit the remaining budget even during fallback."""
import pytest

from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
from agentuniverse.agent.context.context_model import ContextMetadata, ContextPriority, ContextSegment, ContextType


def segment(identifier, tokens, priority, score):
    return ContextSegment(id=identifier, type=ContextType.CONVERSATION, content=identifier,
                          tokens=tokens, priority=priority,
                          metadata=ContextMetadata(relevance_score=score, decay_rate=0))


@pytest.mark.parametrize('priority', [ContextPriority.HIGH, ContextPriority.MEDIUM, ContextPriority.LOW])
@pytest.mark.parametrize('min_segments', [0, 1])
def test_skip_oversized_candidate_and_keep_fitting_segment(priority, min_segments):
    docs = [segment('large', 100, priority, 1), segment('small', 10, priority, .8)]
    result, metrics = SelectiveCompressor().compress(docs, 20, min_segments=min_segments)
    assert [item.id for item in result] == ['small']
    assert metrics.compressed_tokens == 10
    assert metrics.segments_removed == 1
    assert [item.tokens for item in docs] == [100, 10]


def test_minimum_count_is_best_effort_within_budget():
    docs = [segment('one', 10, ContextPriority.HIGH, 1),
            segment('two', 10, ContextPriority.HIGH, .8),
            segment('three', 10, ContextPriority.HIGH, .7)]
    result, metrics = SelectiveCompressor().compress(docs, 10, min_segments=3)
    assert [item.id for item in result] == ['one']
    assert metrics.compressed_tokens == 10


def test_all_optional_segments_too_large_returns_empty():
    docs = [segment('one', 100, ContextPriority.HIGH, 1)]
    result, metrics = SelectiveCompressor().compress(docs, 20)
    assert result == []
    assert metrics.compressed_tokens == 0


@pytest.mark.parametrize('mandatory', ['critical', 'type'])
def test_mandatory_preservation_can_still_exceed_budget(mandatory):
    doc = segment('mandatory', 100, ContextPriority.CRITICAL if mandatory == 'critical' else ContextPriority.LOW, 1)
    kwargs = {'preserve_types': [ContextType.CONVERSATION]} if mandatory == 'type' else {}
    result, metrics = SelectiveCompressor().compress([doc], 20, **kwargs)
    assert [item.id for item in result] == ['mandatory']
    assert metrics.compressed_tokens == 100
