"""Regression coverage for whitespace in the routing agent response."""

import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from agentuniverse.agent.action.knowledge.rag_router import nlu_rag_router
from agentuniverse.agent.action.knowledge.rag_router.nlu_rag_router import NluRagRouter
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.mark.parametrize(
    "output, amount, expected",
    [
        ("store_a, store_b", 2, ["store_a", "store_b"]),
        (" store_b , store_a ", 2, ["store_b", "store_a"]),
        ("store_a\n", 1, ["store_a"]),
        ("\tstore_a,\nstore_b\r\n", 2, ["store_a", "store_b"]),
        (" store_b , store_a", 1, ["store_b"]),
        ("store_a,store_b", 2, ["store_a", "store_b"]),
        ("store_b,store_a", 1, ["store_b"]),
        (" unknown , store_a ", 2, ["store_a"]),
        ("   \n", 2, []),
        ("store a", 2, []),
    ],
)
def test_routing_response_whitespace(output, amount, expected):
    query = Query(query_str="Which knowledge bases explain this topic?")
    agent = Mock()
    agent.run.return_value = SimpleNamespace(output=output)
    stores = {
        "store_a": SimpleNamespace(description="First source"),
        "store_b": SimpleNamespace(description="Second source"),
    }
    # Only external service lookups are replaced; routing and Query are real.
    with patch.object(nlu_rag_router.AgentManager(), "get_instance_obj", return_value=agent), \
            patch.object(nlu_rag_router.StoreManager(), "get_instance_obj", side_effect=stores.__getitem__):
        routes = NluRagRouter(store_amount=amount).rag_route(query, list(stores))

    assert [name for _, name in routes] == expected
    assert all(routed_query is query for routed_query, _ in routes)
    agent.run.assert_called_once_with(
        query=query.query_str,
        store_info=json.dumps({name: store.description for name, store in stores.items()}),
        store_amount=amount,
    )
