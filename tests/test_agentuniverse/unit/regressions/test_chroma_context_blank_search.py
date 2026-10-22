import pytest

from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class UnexpectedCollectionAccess:
    def query(self, **kwargs):
        raise AssertionError("Chroma should not be queried for a blank search")


@pytest.mark.parametrize("query", [None, "", "   "])
def test_blank_search_skips_chroma(query):
    store = ChromaContextStore(name="chroma")
    store._collection = UnexpectedCollectionAccess()

    assert store.search(query, "session") == []
