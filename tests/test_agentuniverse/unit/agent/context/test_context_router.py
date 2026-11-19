"""Tests for context tier routing."""

from agentuniverse.agent.context.router.context_router import ContextRouter


def test_historical_queries_prioritize_cold_storage():
    router = ContextRouter(enable_warm_tier=True, enable_cold_tier=True)

    tiers = router.optimize_search_order(
        "show previous archived results",
        task_type="data_analysis",
    )

    assert tiers == ["cold", "hot", "warm"]
