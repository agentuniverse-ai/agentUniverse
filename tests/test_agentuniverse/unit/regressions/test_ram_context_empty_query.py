from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_ram_context_search_blank_query_returns_no_results():
    store = RamContextStore(name="test_ram_store")
    store.add(
        [ContextSegment(type=ContextType.BACKGROUND, content="stored context", tokens=2)],
        session_id="session-1",
    )

    assert store.search("   ", "session-1") == []
