from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class UnexpectedCollectionAccess:
    def get(self, **kwargs):
        raise AssertionError("Chroma should not be queried for an empty result window")


def test_get_with_nonpositive_limit_skips_chroma():
    store = ChromaContextStore(name="chroma")
    store._collection = UnexpectedCollectionAccess()

    assert store.get("session", limit=-1) == []
    assert store.get("session", limit=0) == []
