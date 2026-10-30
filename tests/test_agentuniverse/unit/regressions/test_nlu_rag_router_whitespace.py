from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.rag_router.nlu_rag_router import (
    NluRagRouter,
)
from agentuniverse.agent.action.knowledge.store.query import Query


def test_nlu_router_strips_store_names_before_filtering_and_limiting():
    router = NluRagRouter(agent_name="test_router_agent", store_amount=2)
    agent = MagicMock()
    agent.run.return_value.output = " vector_store, keyword_store "

    stores = {
        "vector_store": MagicMock(description="vector"),
        "keyword_store": MagicMock(description="keyword"),
    }
    with patch(
        "agentuniverse.agent.action.knowledge.rag_router.nlu_rag_router.AgentManager"
    ) as agent_manager, patch(
        "agentuniverse.agent.action.knowledge.rag_router.nlu_rag_router.StoreManager"
    ) as store_manager:
        agent_manager.return_value.get_instance_obj.return_value = agent
        store_manager.return_value.get_instance_obj.side_effect = stores.get

        routed = router._rag_route(Query(query_str="q"), list(stores))

    assert [store for _, store in routed] == ["vector_store", "keyword_store"]
