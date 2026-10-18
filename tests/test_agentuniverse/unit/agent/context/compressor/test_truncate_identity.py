"""Content truncation preserves segment identity and reports retained context accurately."""

import pytest

from agentuniverse.agent.context.compressor.truncate_compressor import TruncateCompressor
from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextPriority,
    ContextSegment,
    ContextType,
)


@pytest.fixture
def segment():
    return ContextSegment(
        id='source-segment',
        type=ContextType.WORKSPACE,
        priority=ContextPriority.HIGH,
        content='abcd' * 100,
        tokens=100,
        session_id='session-a',
        agent_id='agent-a',
        task_id='task-a',
        parent_id='parent-segment',
        related_ids=['related-segment'],
        metadata=ContextMetadata(
            version=3,
            keywords=['workspace'],
            entities={'document': {'name': 'source.py'}},
            custom={'tags': ['original']},
        ),
    )


def test_truncation_preserves_identity_and_scope(segment):
    compressed, _ = TruncateCompressor().compress([segment], target_tokens=90)

    assert len(compressed) == 1
    result = compressed[0]
    assert result.content != segment.content
    assert result.id == segment.id
    assert result.session_id == segment.session_id
    assert result.agent_id == segment.agent_id
    assert result.task_id == segment.task_id
    assert result.parent_id == segment.parent_id
    assert result.related_ids == segment.related_ids
    assert result.type == segment.type
    assert result.priority == segment.priority


def test_retained_segment_is_not_reported_as_removed(segment):
    compressor = TruncateCompressor()
    compressed, metrics = compressor.compress([segment], target_tokens=90)

    assert metrics.segments_compressed == 1
    assert metrics.segments_preserved == 1
    assert metrics.segments_removed == 0
    expected_loss = 1 - compressed[0].tokens / segment.tokens
    assert metrics.information_loss_estimate == pytest.approx(expected_loss)
    assert compressor.validate_compression_result(compressed, 90, metrics)


def test_truncated_metadata_is_independent_of_source(segment):
    compressed, _ = TruncateCompressor().compress([segment], target_tokens=90)
    result = compressed[0]

    result.metadata.keywords.append('compressed')
    result.metadata.entities['document']['name'] = 'compressed.py'
    result.metadata.custom['tags'].append('compressed')
    result.related_ids.append('new-relation')

    assert segment.metadata.keywords == ['workspace']
    assert segment.metadata.entities == {'document': {'name': 'source.py'}}
    assert segment.metadata.custom == {'tags': ['original']}
    assert segment.related_ids == ['related-segment']
    assert segment.metadata.version == 3
    assert not segment.metadata.compressed
    assert segment.tokens == 100
    assert segment.content == 'abcd' * 100


def test_truncated_content_hash_and_version_match_new_content(segment):
    compressed, _ = TruncateCompressor().compress([segment], target_tokens=90)
    result = compressed[0]

    assert result is not segment
    assert result.metadata.compressed
    assert result.metadata.version == 4
    assert not result.update_content(result.content, result.tokens)
    assert result.metadata.version == 4


def test_under_budget_segment_remains_unchanged(segment):
    before = segment.model_dump()
    compressed, metrics = TruncateCompressor().compress([segment], target_tokens=120)

    assert compressed == [segment]
    assert segment.model_dump() == before
    assert metrics.segments_removed == 0
    assert metrics.information_loss_estimate == 0
