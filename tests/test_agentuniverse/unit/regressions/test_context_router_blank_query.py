import pytest

from agentuniverse.agent.context.router.context_router import ContextRouter


@pytest.mark.parametrize("query", [None, "", "   "])
def test_blank_query_keeps_default_search_order(query):
    router = ContextRouter(name="router", enable_warm_tier=True)

    assert router.optimize_search_order(query, task_type="code_generation") == [
        "hot",
        "warm",
    ]
