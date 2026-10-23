# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: test_knowledge_context_synchronizer.py
"""Unit tests for KnowledgeContextSynchronizer and metadata-aware add_context.

The synchronizer delegates persistence to ``ContextManager.add_context``, so
these tests exercise both layers together: they pin down that the metadata a
caller passes actually reaches storage, and that the ids the synchronizer
tracks are the ids that really exist in the store. Coverage for the two paired
regressions lives here: ``add_context`` used to ignore the ``metadata``
argument, and the synchronizer used to record locally generated segment ids
that never matched anything in storage.
"""

import pytest

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextPriority,
    ContextType,
)
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.context.sync.knowledge_context_synchronizer import (
    ConflictResolutionStrategy,
    KnowledgeContextSynchronizer,
)


def _make_manager(name: str = "test_context_manager") -> ContextManager:
    """Build a ContextManager backed by an in-memory store.

    Mirrors the wiring used by the other context unit tests: the hot store is
    injected directly so no YAML component registration is required.
    """
    store = RamContextStore(
        name=f"{name}_ram_store",
        max_segments=100,
        ttl_hours=24,
    )
    manager = ContextManager(
        name=name,
        hot_store_name=f"{name}_ram_store",
        default_max_tokens=8000,
        default_reserved_tokens=1000,
    )
    manager._hot_store = store
    return manager


@pytest.fixture
def manager():
    """A ContextManager with an injected in-memory hot store."""
    return _make_manager()


@pytest.fixture
def synchronizer(manager):
    """A KnowledgeContextSynchronizer bound to the test ContextManager."""
    return KnowledgeContextSynchronizer(manager)


class TestAddContextMetadata:
    """``add_context`` must persist the metadata callers hand to it."""

    def test_returns_the_stored_instance(self, manager):
        returned = manager.add_context("s1", "content", ContextType.BACKGROUND)
        persisted = manager.get_context("s1")
        assert len(persisted) == 1
        # The caller needs identity, not a copy, to learn the persisted id.
        assert persisted[0] is returned
        assert returned.id

    def test_applies_context_metadata_instance(self, manager):
        metadata = ContextMetadata(custom={"knowledge_id": "doc", "role": "user"})
        returned = manager.add_context(
            "s1",
            "documents are searchable",
            ContextType.BACKGROUND,
            ContextPriority.HIGH,
            metadata=metadata,
        )

        stored = manager.get_context("s1")
        assert len(stored) == 1
        assert stored[0].id == returned.id
        assert stored[0].metadata.custom == {"knowledge_id": "doc", "role": "user"}

    def test_context_metadata_is_deep_copied(self, manager):
        metadata = ContextMetadata(custom={"knowledge_id": "doc"})
        stored_segment = manager.add_context(
            "s1",
            "content",
            ContextType.BACKGROUND,
            metadata=metadata,
        )

        # Mutating the caller's object must not retroactively rewrite storage.
        metadata.custom["knowledge_id"] = "tampered"
        persisted = manager.get_context("s1")[0]
        assert persisted.metadata.custom["knowledge_id"] == "doc"
        assert stored_segment.metadata.custom["knowledge_id"] == "doc"

    def test_accepts_plain_dict_as_custom_metadata(self, manager):
        segment = manager.add_context(
            "s1",
            "hello",
            ContextType.CONVERSATION,
            ContextPriority.HIGH,
            metadata={"role": "user"},
        )
        assert segment.metadata.custom == {"role": "user"}
        # The documented shorthand reaches storage unchanged.
        assert manager.get_context("s1")[0].metadata.custom == {"role": "user"}

    def test_dict_metadata_maps_named_model_fields(self, manager):
        segment = manager.add_context(
            "s1",
            "content",
            ContextType.BACKGROUND,
            metadata={"source_id": "doc-1", "role": "user"},
        )
        assert segment.metadata.source_id == "doc-1"
        assert segment.metadata.custom == {"role": "user"}

    def test_dict_metadata_merges_existing_custom(self, manager):
        segment = manager.add_context(
            "s1",
            "content",
            ContextType.BACKGROUND,
            metadata={"custom": {"knowledge_id": "doc"}, "role": "user"},
        )
        assert segment.metadata.custom == {"knowledge_id": "doc", "role": "user"}

    def test_none_metadata_yields_empty_custom(self, manager):
        segment = manager.add_context("s1", "content", ContextType.BACKGROUND)
        assert segment.metadata.custom == {}

    def test_rejects_unsupported_metadata_type(self, manager):
        with pytest.raises(TypeError):
            manager.add_context(
                "s1",
                "content",
                ContextType.BACKGROUND,
                metadata="not-a-metadata",
            )

    def test_applies_agent_and_task_ids(self, manager):
        segment = manager.add_context(
            "s1",
            "content",
            ContextType.TASK,
            ContextPriority.HIGH,
            agent_id="agent-1",
            task_id="task-1",
        )
        assert segment.agent_id == "agent-1"
        assert segment.task_id == "task-1"

    def test_applies_parent_and_related_ids(self, manager):
        parent = manager.add_context("s1", "parent", ContextType.TASK)
        related = [parent.id]
        child = manager.add_context(
            "s1",
            "child",
            ContextType.WORKSPACE,
            parent_id=parent.id,
            related_ids=related,
        )
        assert child.parent_id == parent.id
        assert child.related_ids == [parent.id]

        # related_ids is copied, so later mutation of the caller's list cannot
        # rewrite the stored relationship.
        related.append("ghost")
        assert child.related_ids == [parent.id]


class TestSyncTracksStoredIds:
    """The knowledge -> segment mapping must reference stored segments."""

    def test_sync_persists_knowledge_metadata(self, manager, synchronizer):
        result = synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")
        assert result.segments_added == 1

        stored = manager.get_context("s1")
        assert len(stored) == 1
        custom = stored[0].metadata.custom
        assert custom["knowledge_id"] == "doc"
        assert custom["document_index"] == 0
        assert custom["source"] == "knowledge_base"
        assert custom["version_id"] is not None

    def test_tracked_ids_match_stored_segments(self, manager, synchronizer):
        synchronizer.sync_knowledge_to_context("doc", ["a", "b"], "s1")

        tracked = set(synchronizer._knowledge_context_map["doc"])
        stored_ids = {seg.id for seg in manager.get_context("s1")}
        assert tracked == stored_ids
        assert len(tracked) == 2

    def test_resync_invalidates_exactly_previous_segments(self, manager, synchronizer):
        first = synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")
        assert first.segments_invalidated == 0
        first_ids = set(synchronizer._knowledge_context_map["doc"])

        second = synchronizer.sync_knowledge_to_context("doc", ["v2"], "s1")
        assert second.segments_invalidated == 1

        stored = {seg.id: seg for seg in manager.get_context("s1")}
        assert first_ids <= set(stored)
        for seg_id in first_ids:
            assert stored[seg_id].priority == ContextPriority.LOW
            assert stored[seg_id].metadata.custom["invalidated"] is True
            assert "invalidated_at" in stored[seg_id].metadata.custom

        # The replacement is tracked; the invalidated id is not.
        assert first_ids.isdisjoint(set(synchronizer._knowledge_context_map["doc"]))

    def test_identical_resync_is_a_noop(self, manager, synchronizer):
        synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")
        before = {seg.id for seg in manager.get_context("s1")}

        result = synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")
        assert result.details.get("skipped")
        assert result.segments_added == 0
        assert result.segments_invalidated == 0
        assert {seg.id for seg in manager.get_context("s1")} == before

    def test_force_update_resyncs_unchanged_content(self, manager, synchronizer):
        synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")

        result = synchronizer.sync_knowledge_to_context(
            "doc", ["v1"], "s1", force_update=True
        )
        assert result.segments_invalidated == 1
        assert result.segments_added == 1

    def test_invalidation_is_scoped_per_knowledge_id(self, manager, synchronizer):
        synchronizer.sync_knowledge_to_context("doc_a", ["a"], "s1")
        synchronizer.sync_knowledge_to_context("doc_b", ["b"], "s1")

        result = synchronizer.sync_knowledge_to_context("doc_a", ["a2"], "s1")
        assert result.segments_invalidated == 1

        by_content = {seg.content: seg for seg in manager.get_context("s1")}
        assert by_content["b"].priority == ContextPriority.HIGH
        assert by_content["a"].priority == ContextPriority.LOW

    def test_lookup_segment_by_knowledge_id_metadata(self, manager, synchronizer):
        synchronizer.sync_knowledge_to_context("doc_a", ["alpha"], "s1")
        synchronizer.sync_knowledge_to_context("doc_b", ["beta"], "s1")

        def find(knowledge_id):
            return [
                seg for seg in manager.get_context("s1")
                if seg.metadata.custom.get("knowledge_id") == knowledge_id
            ]

        assert [seg.content for seg in find("doc_a")] == ["alpha"]
        assert [seg.content for seg in find("doc_b")] == ["beta"]

    def test_sync_without_versioning_still_stores_metadata(self, manager):
        synchronizer = KnowledgeContextSynchronizer(manager, enable_versioning=False)
        synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")

        stored = manager.get_context("s1")
        assert len(stored) == 1
        assert stored[0].metadata.custom["knowledge_id"] == "doc"
        assert stored[0].metadata.custom["version_id"] is None

    def test_segment_lookup_uses_real_ids(self, manager, synchronizer):
        synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")
        tracked = synchronizer._knowledge_context_map["doc"]

        found = synchronizer._get_segments_by_ids("s1", tracked)
        assert [seg.id for seg in found] == tracked
        # The bug recorded ids of objects that were never stored, so a lookup
        # of a locally built id always came back empty.
        assert synchronizer._get_segments_by_ids("s1", ["not-a-real-id"]) == []


class TestUpdateKnowledgeContext:
    """Conflict resolution must work on stored segments, not on duplicates."""

    def test_newest_wins_replaces_stale_content(self, manager, synchronizer):
        synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")
        old_id = synchronizer._knowledge_context_map["doc"][0]

        result = synchronizer.update_knowledge_context(
            "doc",
            "s1",
            new_documents=["v2"],
            conflict_strategy=ConflictResolutionStrategy.NEWEST_WINS,
        )

        assert result.conflicts_resolved == 1
        assert result.segments_updated == 1
        assert result.segments_invalidated == 1

        stored = {seg.id: seg for seg in manager.get_context("s1")}
        # The outdated segment is demoted instead of lingering at priority.
        assert stored[old_id].priority == ContextPriority.LOW
        assert stored[old_id].metadata.custom["invalidated"] is True

        # Only the replacement is tracked from now on.
        new_ids = synchronizer._knowledge_context_map["doc"]
        assert old_id not in new_ids
        assert [stored[seg_id].content for seg_id in new_ids] == ["v2"]
        # The replacement was not appended twice.
        assert sum(1 for seg in stored.values() if seg.content == "v2") == 1

    def test_critical_preserved_keeps_critical_and_replaces_rest(
        self, manager, synchronizer
    ):
        # Seed one CRITICAL and one ordinary segment under the same knowledge
        # id: a plain sync gives every segment the same priority.
        critical = manager.add_context(
            "s1",
            "critical v1",
            ContextType.BACKGROUND,
            ContextPriority.CRITICAL,
            metadata={"knowledge_id": "doc"},
        )
        regular = manager.add_context(
            "s1",
            "regular v1",
            ContextType.BACKGROUND,
            ContextPriority.HIGH,
            metadata={"knowledge_id": "doc"},
        )
        synchronizer._knowledge_context_map["doc"] = [critical.id, regular.id]

        result = synchronizer.update_knowledge_context(
            "doc",
            "s1",
            new_documents=["v2"],
            conflict_strategy=ConflictResolutionStrategy.CRITICAL_PRESERVED,
        )

        assert result.conflicts_resolved == 2
        assert result.segments_invalidated == 1

        stored = {seg.id: seg for seg in manager.get_context("s1")}
        # The CRITICAL segment survives untouched...
        assert stored[critical.id].priority == ContextPriority.CRITICAL
        assert stored[critical.id].content == "critical v1"
        assert "invalidated" not in stored[critical.id].metadata.custom
        # ...while the ordinary one is demoted.
        assert stored[regular.id].priority == ContextPriority.LOW
        assert stored[regular.id].metadata.custom["invalidated"] is True

        replacements = [seg for seg in stored.values() if seg.content == "v2"]
        assert len(replacements) == 1
        assert replacements[0].metadata.custom["knowledge_id"] == "doc"
        assert set(synchronizer._knowledge_context_map["doc"]) == {
            critical.id,
            replacements[0].id,
        }

    def test_merge_keeps_old_and_appends_new_without_duplicating(
        self, manager, synchronizer
    ):
        synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")
        old_id = synchronizer._knowledge_context_map["doc"][0]

        synchronizer.update_knowledge_context(
            "doc",
            "s1",
            new_documents=["v2"],
            conflict_strategy=ConflictResolutionStrategy.MERGE,
        )

        stored = {seg.id: seg for seg in manager.get_context("s1")}
        assert len(stored) == 2
        assert stored[old_id].content == "v1"
        assert stored[old_id].priority == ContextPriority.HIGH
        assert set(synchronizer._knowledge_context_map["doc"]) == set(stored)

    def test_version_both_marks_versions_without_duplicating(
        self, manager, synchronizer
    ):
        synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")
        old_id = synchronizer._knowledge_context_map["doc"][0]

        synchronizer.update_knowledge_context(
            "doc",
            "s1",
            new_documents=["v2"],
            conflict_strategy=ConflictResolutionStrategy.VERSION_BOTH,
        )

        stored = {seg.id: seg for seg in manager.get_context("s1")}
        assert len(stored) == 2
        assert stored[old_id].metadata.custom["version"] == "old"
        assert stored[old_id].priority == ContextPriority.MEDIUM

        new_segments = [seg for seg in stored.values() if seg.content == "v2"]
        assert len(new_segments) == 1
        assert new_segments[0].metadata.custom["version"] == "new"
        assert set(synchronizer._knowledge_context_map["doc"]) == set(stored)

    def test_update_without_documents_only_invalidates(self, manager, synchronizer):
        synchronizer.sync_knowledge_to_context("doc", ["v1"], "s1")
        tracked = synchronizer._knowledge_context_map["doc"][0]

        result = synchronizer.update_knowledge_context("doc", "s1")

        assert result.segments_invalidated == 1
        assert result.segments_added == 0

        stored = {seg.id: seg for seg in manager.get_context("s1")}
        assert stored[tracked].priority == ContextPriority.LOW
        assert stored[tracked].metadata.custom["invalidated"] is True
        # Only invalidation was requested, so the mapping is untouched.
        assert synchronizer._knowledge_context_map["doc"] == [tracked]

    def test_update_without_known_segments_still_stores_new_content(
        self, manager, synchronizer
    ):
        result = synchronizer.update_knowledge_context(
            "unknown",
            "s1",
            new_documents=["v1"],
            conflict_strategy=ConflictResolutionStrategy.MERGE,
        )

        assert result.conflicts_resolved == 0
        stored = manager.get_context("s1")
        assert len(stored) == 1
        assert stored[0].content == "v1"
        assert synchronizer._knowledge_context_map["unknown"] == [stored[0].id]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
