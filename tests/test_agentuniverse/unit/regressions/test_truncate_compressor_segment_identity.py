import hashlib

from agentuniverse.agent.context.compressor.truncate_compressor import (
    TruncateCompressor,
)
from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextPriority,
    ContextSegment,
    ContextType,
)


def test_truncation_preserves_segment_identity_scope_and_metadata_isolation():
    metadata = ContextMetadata(
        version=3,
        custom={"source": {"labels": ["important"]}},
    )
    segment = ContextSegment(
        id="stable-segment-id",
        type=ContextType.CONVERSATION,
        priority=ContextPriority.HIGH,
        content="A long piece of conversation content that must be shortened.",
        tokens=30,
        metadata=metadata,
        parent_id="parent-segment",
        related_ids=["related-segment"],
        task_id="task-1",
        agent_id="agent-1",
        session_id="session-1",
    )
    original_content = segment.content
    original_version = segment.metadata.version

    compressed = TruncateCompressor()._truncate_content(segment, 10)

    assert compressed.id == segment.id
    assert compressed.parent_id == segment.parent_id
    assert compressed.related_ids == segment.related_ids
    assert compressed.task_id == segment.task_id
    assert compressed.agent_id == segment.agent_id
    assert compressed.session_id == segment.session_id
    assert compressed.metadata.custom == metadata.custom
    assert compressed.metadata.custom is not metadata.custom
    assert compressed.metadata.compressed is True
    assert compressed.metadata.original_tokens == segment.tokens
    assert compressed.metadata.compression_method == "truncate"
    assert compressed.metadata.version == original_version + 1
    assert compressed._content_hash == hashlib.md5(
        compressed.content.encode("utf-8")
    ).hexdigest()

    compressed.metadata.custom["source"]["labels"].append("changed")
    assert metadata.custom == {"source": {"labels": ["important"]}}
    assert segment.content == original_content
    assert segment.tokens == 30
    assert segment.metadata.compressed is False
