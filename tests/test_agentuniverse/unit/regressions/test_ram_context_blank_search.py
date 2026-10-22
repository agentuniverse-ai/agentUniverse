import pytest

from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


@pytest.mark.parametrize("query", [None, "", "   "])
def test_blank_search_does_not_match_every_segment(query):
    store = RamContextStore(name="ram")
    store.add([
        ContextSegment(type=ContextType.CONVERSATION, content="context", tokens=1)
    ], session_id="session")

    assert store.search(query, "session") == []
