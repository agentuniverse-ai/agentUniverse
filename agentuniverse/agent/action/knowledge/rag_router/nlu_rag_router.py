# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/13 16:25
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: nlu_rag_router.py

import json
from typing import List, Tuple, Optional

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.rag_router.rag_router import \
    RagRouter
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class NluRagRouter(RagRouter):
    llm: Optional[dict] = None
    agent_name: str = 'nlu_rag_route_agent'
    store_amount: int = 1

    def _rag_route(self, query: Query, store_list: List[str]) \
            -> List[Tuple[Query, str]]:

        agent = AgentManager().get_instance_obj(self.agent_name)
        if self.llm:
            agent.agent_model.profile['llm_model'] = self.llm
        store_info = {}
        for _store in store_list:
            store_info[_store] = StoreManager().get_instance_obj(_store).description
        agent_result = agent.run(
            query=query.query_str,
            store_info=json.dumps(store_info),
            store_amount=self.store_amount
        )
        target_store_list = agent_result.output.split(",")
        if len(target_store_list) > self.store_amount:
            target_store_list = target_store_list[:self.store_amount]
        filtered_store_list = [_store for _store in target_store_list if _store in store_list]

        return [(query, store) for store in filtered_store_list]

    def _initialize_by_component_configer(self,
                                          rag_router_config: ComponentConfiger) -> 'RagRouter':
        super()._initialize_by_component_configer(rag_router_config)
        if hasattr(rag_router_config, "llm"):
            self.llm = rag_router_config.llm
        if hasattr(rag_router_config, "agent_name"):
            self.agent_name = rag_router_config.agent_name
        if hasattr(rag_router_config, "store_amount"):
            self.store_amount = rag_router_config.store_amount
