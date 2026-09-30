from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_get_with_negative_limit_returns_no_segments():
    store = RamContextStore(name="ram")
    store.add([
        ContextSegment(type=ContextType.CONVERSATION, content="one", tokens=1),
        ContextSegment(type=ContextType.CONVERSATION, content="two", tokens=1),
    ], session_id="session")

    assert store.get("session", limit=-1) == []
