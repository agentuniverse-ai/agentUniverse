from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_add_normalizes_segment_to_storage_session():
    segment = ContextSegment(
        type=ContextType.CONVERSATION,
        content="context",
        tokens=1,
        session_id="stale-session",
    )
    store = RamContextStore(name="ram")

    store.add([segment], session_id="current-session")

    assert segment.session_id == "current-session"
    assert store.get("current-session")[0].session_id == "current-session"
