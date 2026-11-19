from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


def test_enabling_metrics_initializes_non_ram_stores():
    store = RedisContextStore(name="redis", enable_metrics=True)

    metrics = store.get_metrics()

    assert metrics["add_count"] == 0
    assert metrics["get_count"] == 0
    assert metrics["search_count"] == 0
