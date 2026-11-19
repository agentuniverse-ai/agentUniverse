from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_empty_id_delete_preserves_window_and_storage():
    manager = ContextManager(name="manager")
    manager._hot_store = RamContextStore(name="ram")
    window = manager.create_context_window("session")
    segment = manager.add_context("session", "retained context", ContextType.CONVERSATION)
    tokens_before = window.total_tokens

    manager.delete_context("session", segment_ids=[])

    assert window.total_tokens == tokens_before
    assert window.segment_ids == [segment.id]
    assert [item.id for item in manager._hot_store.get("session")] == [segment.id]
