"""Explicit type preservation survives a fully consumed critical budget."""
import pytest

from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
from agentuniverse.agent.context.context_model import ContextPriority, ContextSegment, ContextType


def segment(name, tokens, priority, kind):
    return ContextSegment(id=name, content=name, tokens=tokens, priority=priority, type=kind)


@pytest.mark.parametrize('critical_tokens', [10, 20])
@pytest.mark.parametrize('preserved_priority', [ContextPriority.LOW, ContextPriority.EPHEMERAL])
def test_preserved_types_survive_exhausted_critical_budget(critical_tokens, preserved_priority):
    critical = segment('critical', critical_tokens, ContextPriority.CRITICAL, ContextType.SYSTEM)
    task = segment('task', 3, preserved_priority, ContextType.TASK)
    optional = segment('optional', 1, ContextPriority.HIGH, ContextType.CONVERSATION)
    docs = [optional, task, critical]
    snapshot = [doc.model_dump() for doc in docs]

    result, metrics = SelectiveCompressor().compress(
        docs, 10, preserve_types=[ContextType.SYSTEM, ContextType.TASK], min_segments=3)

    assert [doc.id for doc in result] == ['critical', 'task']
    assert result[0] is critical and result[1] is task
    assert metrics.original_tokens == critical_tokens + 4
    assert metrics.compressed_tokens == critical_tokens + 3
    assert metrics.segments_preserved == 2
    assert metrics.segments_removed == 1
    assert [doc.model_dump() for doc in docs] == snapshot


def test_no_preserve_types_keeps_only_critical_when_budget_is_full():
    docs = [segment('critical', 10, ContextPriority.CRITICAL, ContextType.SYSTEM),
            segment('task', 3, ContextPriority.LOW, ContextType.TASK)]
    result, metrics = SelectiveCompressor().compress(docs, 10)
    assert [doc.id for doc in result] == ['critical']
    assert metrics.compressed_tokens == 10


def test_mandatory_union_does_not_duplicate_critical_type():
    docs = [segment('critical', 4, ContextPriority.CRITICAL, ContextType.SYSTEM),
            segment('task', 3, ContextPriority.LOW, ContextType.TASK),
            segment('large', 20, ContextPriority.HIGH, ContextType.CONVERSATION)]
    result, metrics = SelectiveCompressor().compress(
        docs, 7, preserve_types=[ContextType.SYSTEM, ContextType.TASK])
    assert [doc.id for doc in result] == ['critical', 'task']
    assert metrics.compressed_tokens == 7
