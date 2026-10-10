"""Offline regressions for session-scoped knowledge synchronization state."""

from unittest.mock import Mock

import pytest

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.context.sync.knowledge_context_synchronizer import (
    KnowledgeContextSynchronizer,
)


@pytest.fixture
def synchronizer():
    real_manager = ContextManager(name="sync_test")
    real_manager._hot_store = RamContextStore(name="sync_store")
    manager = Mock(spec=ContextManager, wraps=real_manager)
    return KnowledgeContextSynchronizer(manager)


def test_identical_knowledge_is_synced_once_per_session(synchronizer):
    first = synchronizer.sync_knowledge_to_context("knowledge", ["same"], "a")
    second = synchronizer.sync_knowledge_to_context("knowledge", ["same"], "b")

    assert first.segments_added == second.segments_added == 1
    assert synchronizer.context_manager.add_context.call_count == 2
    for session in ("a", "b"):
        result = synchronizer.sync_knowledge_to_context("knowledge", ["same"], session)
        assert result.segments_added == 0
        assert "skipped" in result.details
    assert synchronizer.context_manager.add_context.call_count == 2


@pytest.mark.parametrize("versioning", [True, False])
def test_invalidation_uses_only_target_session_mapping(synchronizer, versioning):
    synchronizer.enable_versioning = versioning
    synchronizer._invalidate_segments = Mock(return_value=1)
    synchronizer._get_segments_by_ids = Mock(return_value=[])
    synchronizer.sync_knowledge_to_context("knowledge", ["old"], "a")
    synchronizer.sync_knowledge_to_context("knowledge", ["different"], "b")
    # A first sync in B must not try to invalidate A's segment IDs.
    synchronizer._invalidate_segments.assert_not_called()

    synchronizer.update_knowledge_context("knowledge", "a")
    a_ids = synchronizer._invalidate_segments.call_args.args[1]
    synchronizer.update_knowledge_context("knowledge", "b")
    b_ids = synchronizer._invalidate_segments.call_args.args[1]
    assert a_ids and b_ids and a_ids != b_ids

    synchronizer.sync_knowledge_to_context("knowledge", ["replacement"], "a")
    synchronizer._invalidate_segments.assert_called_with("a", a_ids)
    synchronizer.update_knowledge_context("knowledge", "b", ["replacement"])
    synchronizer._get_segments_by_ids.assert_called_with("b", b_ids)


def test_failed_first_write_can_be_retried(synchronizer):
    synchronizer.context_manager.add_context.side_effect = RuntimeError("write failed")
    with pytest.raises(RuntimeError, match="write failed"):
        synchronizer.sync_knowledge_to_context("knowledge", ["same"], "a")
    assert synchronizer.get_knowledge_version("knowledge") is None
    synchronizer.context_manager.delete_context.assert_not_called()

    synchronizer.context_manager.add_context.side_effect = None
    result = synchronizer.sync_knowledge_to_context("knowledge", ["same"], "a")
    assert result.segments_added == 1
    assert synchronizer.get_knowledge_version("knowledge") == result.version
    assert "skipped" in synchronizer.sync_knowledge_to_context(
        "knowledge", ["same"], "a"
    ).details


@pytest.mark.parametrize("fail_after", [0, 1])
def test_failed_batch_does_not_publish_new_version(synchronizer, fail_after):
    previous = synchronizer.sync_knowledge_to_context("knowledge", ["old"], "a")
    synchronizer.context_manager.add_context.side_effect = (
        [Mock()] * fail_after + [RuntimeError("write failed")]
    )
    with pytest.raises(RuntimeError, match="write failed"):
        synchronizer.sync_knowledge_to_context("knowledge", ["new", "more"], "a")
    assert synchronizer.get_knowledge_version("knowledge") == previous.version

    synchronizer.context_manager.add_context.side_effect = None
    result = synchronizer.sync_knowledge_to_context("knowledge", ["new", "more"], "a")
    assert result.segments_added == 2


def test_session_version_queries_preserve_legacy_latest_view(synchronizer):
    first = synchronizer.sync_knowledge_to_context("knowledge", ["first"], "a")
    second = synchronizer.sync_knowledge_to_context("knowledge", ["second"], "b")
    assert synchronizer.get_knowledge_version("knowledge", session_id="a") == first.version
    assert synchronizer.get_knowledge_version("knowledge", session_id="b") == second.version
    assert synchronizer.get_knowledge_version("knowledge", session_id="missing") is None
    assert synchronizer.get_knowledge_version("knowledge") == second.version
    assert synchronizer.list_knowledge_versions("a") == {"knowledge": first.version}
    assert synchronizer.list_knowledge_versions("b") == {"knowledge": second.version}
    assert synchronizer.list_knowledge_versions("missing") == {}
    assert synchronizer.list_knowledge_versions() == {"knowledge": second.version}
    synchronizer.list_knowledge_versions().clear()
    assert synchronizer.get_knowledge_version("knowledge") == second.version

    updated = synchronizer.sync_knowledge_to_context("knowledge", ["third"], "a")
    assert synchronizer.get_knowledge_version("knowledge") == updated.version
    assert synchronizer.list_knowledge_versions() == {"knowledge": updated.version}


def test_force_update_still_writes_and_disabled_versioning_tracks_nothing(synchronizer):
    synchronizer.sync_knowledge_to_context("knowledge", ["same"], "a")
    result = synchronizer.sync_knowledge_to_context(
        "knowledge", ["same"], "a", force_update=True
    )
    assert result.segments_added == 1
    synchronizer.enable_versioning = False
    result = synchronizer.sync_knowledge_to_context("unversioned", ["same"], "a")
    assert result.version is None
    assert synchronizer.get_knowledge_version("unversioned") is None


@pytest.mark.parametrize("versioning", [True, False])
def test_partial_failure_rolls_back_only_new_segments(synchronizer, versioning):
    synchronizer.enable_versioning = versioning
    manager = synchronizer.context_manager
    previous = synchronizer.sync_knowledge_to_context("knowledge", ["old"], "a")
    synchronizer.sync_knowledge_to_context("knowledge", ["other session"], "b")
    old_a = manager.get_context("a")
    old_b = manager.get_context("b")
    old_ids = [segment.id for segment in old_a]
    real_add = manager.add_context._mock_wraps
    written_ids = []
    write_error = RuntimeError("second write failed")

    def fail_second(*args, **kwargs):
        if written_ids:
            raise write_error
        segment = real_add(*args, **kwargs)
        written_ids.append(segment.id)
        return segment

    manager.add_context.side_effect = fail_second
    with pytest.raises(RuntimeError, match="second write failed"):
        synchronizer.sync_knowledge_to_context("knowledge", ["new", "more"], "a")
    manager.delete_context.assert_called_once_with("a", segment_ids=written_ids)
    assert [segment.id for segment in manager.get_context("a")] == old_ids
    assert all(not segment.metadata.custom.get("invalidated") for segment in old_a)
    assert manager.get_context("b") == old_b
    assert synchronizer.get_knowledge_version("knowledge", "a") == previous.version

    manager.add_context.side_effect = None
    result = synchronizer.sync_knowledge_to_context("knowledge", ["new", "more"], "a")
    assert result.segments_added == 2
    assert result.segments_invalidated == 1
    assert sorted(segment.content for segment in manager.get_context("a")) == ["more", "new", "old"]
    assert old_a[0].metadata.custom["invalidated"] is True
    if versioning:
        result = synchronizer.sync_knowledge_to_context("knowledge", ["new", "more"], "a")
        assert "skipped" in result.details
        assert len(manager.get_context("a")) == 3


def test_rollback_error_is_explicit_and_version_is_not_committed(synchronizer):
    manager = synchronizer.context_manager
    write_error = RuntimeError("write failed")
    rollback_error = RuntimeError("rollback failed")
    manager.add_context.side_effect = [Mock(id="written"), write_error]
    manager.delete_context.side_effect = rollback_error
    with pytest.raises(RuntimeError, match="rollback failed") as raised:
        synchronizer.sync_knowledge_to_context("knowledge", ["one", "two"], "a")
    assert raised.value.__cause__ is write_error
    assert synchronizer.get_knowledge_version("knowledge") is None


def test_invalidation_read_failure_rolls_back_new_writes(synchronizer):
    manager = synchronizer.context_manager
    previous = synchronizer.sync_knowledge_to_context("knowledge", ["old"], "a")
    old_ids = [segment.id for segment in manager.get_context("a")]
    manager.get_context.side_effect = RuntimeError("read failed")
    with pytest.raises(RuntimeError, match="read failed"):
        synchronizer.sync_knowledge_to_context("knowledge", ["new"], "a")
    manager.get_context.side_effect = None
    assert [segment.id for segment in manager.get_context("a")] == old_ids
    assert synchronizer.get_knowledge_version("knowledge", "a") == previous.version
    assert not manager.get_context("a")[0].metadata.custom.get("invalidated")
    result = synchronizer.sync_knowledge_to_context("knowledge", ["new"], "a")
    assert result.segments_added == result.segments_invalidated == 1
