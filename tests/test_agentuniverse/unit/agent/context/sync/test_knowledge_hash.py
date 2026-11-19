"""Tests for knowledge change detection."""

from agentuniverse.agent.context.sync.knowledge_context_synchronizer import (
    KnowledgeContextSynchronizer,
)


def test_document_boundaries_affect_knowledge_hash():
    synchronizer = KnowledgeContextSynchronizer(context_manager=None)

    assert synchronizer._compute_hash(["ab", "c"]) != synchronizer._compute_hash(
        ["a", "bc"]
    )
