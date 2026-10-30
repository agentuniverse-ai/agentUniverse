from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_ram_context_search_excludes_segments_without_matches():
    store = RamContextStore(name="test_ram_store")
    store.add(
        [
            ContextSegment(
                type=ContextType.BACKGROUND,
                content="Python is a programming language",
                tokens=5,
            )
        ],
        session_id="session-1",
    )

    assert store.search("database", "session-1") == []
