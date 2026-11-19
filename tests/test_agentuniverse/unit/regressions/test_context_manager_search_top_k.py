from agentuniverse.agent.context.context_manager import ContextManager


class SearchStore:
    def __init__(self):
        self.calls = 0

    def search(self, **kwargs):
        self.calls += 1
        return [object()]


def test_context_manager_skips_nonpositive_search_limits():
    manager = ContextManager()
    store = SearchStore()
    manager._hot_store = store

    assert manager.search_context("session", "query", top_k=0) == []
    assert manager.search_context("session", "query", top_k=-3) == []
    assert store.calls == 0
