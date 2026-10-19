from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class FakeCollection:
    def get(self):
        return {
            "metadatas": [
                {"session_id": "valid"},
                None,
                {},
                {"session_id": ""},
                {"session_id": 123},
            ]
        }


def test_chroma_session_listing_skips_malformed_metadata():
    store = ChromaContextStore()
    store._collection = FakeCollection()

    assert store.get_all_sessions() == ["valid"]
