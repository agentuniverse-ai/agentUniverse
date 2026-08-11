from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextPriority,
    ContextType,
)


def test_add_context_preserves_serialized_knowledge_metadata():
    manager = ContextManager()
    metadata = ContextMetadata(
        source_type="knowledge_base",
        source_id="knowledge-42",
        custom={
            "knowledge_id": "knowledge-42",
            "version_id": "version-7",
            "document_index": 3,
            "source": "product-docs",
        },
    )

    segment = manager.add_context(
        session_id="session-1",
        content="Metadata must survive context construction.",
        context_type=ContextType.BACKGROUND,
        priority=ContextPriority.HIGH,
        metadata=metadata.model_dump(),
    )

    assert isinstance(segment.metadata, ContextMetadata)
    assert segment.metadata.source_type == "knowledge_base"
    assert segment.metadata.source_id == "knowledge-42"
    assert segment.metadata.custom == metadata.custom


def test_add_context_uses_default_metadata_when_not_supplied():
    manager = ContextManager()

    for session_id, metadata_kwargs in (
        ("metadata-omitted", {}),
        ("metadata-none", {"metadata": None}),
    ):
        segment = manager.add_context(
            session_id=session_id,
            content="Default metadata remains available.",
            context_type=ContextType.TASK,
            **metadata_kwargs,
        )

        assert isinstance(segment.metadata, ContextMetadata)
        assert segment.metadata.source_type == "user_input"
        assert segment.metadata.custom == {}
