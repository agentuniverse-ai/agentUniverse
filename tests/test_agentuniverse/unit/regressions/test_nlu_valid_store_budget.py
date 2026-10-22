"""Only distinct configured stores consume the NLU routing budget."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.knowledge.rag_router.nlu_rag_router import NluRagRouter
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.mark.parametrize("response,amount,expected", [
    ("unknown, beta", 1, ["beta"]),
    ("unknown, alpha, beta", 2, ["alpha", "beta"]),
    ("alpha, alpha, beta", 2, ["alpha", "beta"]),
    (" alpha, ,alpha,unknown, beta, gamma ", 2, ["alpha", "beta"]),
    ("gamma,beta,alpha", 2, ["gamma", "beta"]),
    ("ALPHA,alpha", 1, ["alpha"]),
    ("unknown,unknown", 2, []),
    (" , \n,", 2, []),
    ("alpha", 3, ["alpha"]),
    ("alpha,beta", 0, []),
])
def test_valid_store_budget(monkeypatch, response, amount, expected):
    agent = Mock()
    agent.run.return_value = SimpleNamespace(output=response)
    stores = {name: SimpleNamespace(description=name + " description")
              for name in ["alpha", "beta", "gamma"]}
    prefix = "agentuniverse.agent.action.knowledge.rag_router.nlu_rag_router."
    monkeypatch.setattr(prefix + "AgentManager", lambda: SimpleNamespace(
        get_instance_obj=lambda name: agent))
    monkeypatch.setattr(prefix + "StoreManager", lambda: SimpleNamespace(
        get_instance_obj=stores.get))
    query = Query(query_str="which report?", ext_info={"filter": [1]})
    store_names = list(stores)
    result = NluRagRouter(store_amount=amount).rag_route(query, store_names)
    assert [name for _, name in result] == expected
    assert all(item is query for item, _ in result)
    assert store_names == ["alpha", "beta", "gamma"]
    assert query.ext_info == {"filter": [1]}
    assert json.loads(agent.run.call_args.kwargs["store_info"]) == {
        name: item.description for name, item in stores.items()}
    assert agent.run.call_args.kwargs["store_amount"] == amount
