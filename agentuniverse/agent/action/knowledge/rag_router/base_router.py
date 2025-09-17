# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/13 11:31
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: base_router.py

from typing import List, Tuple

from agentuniverse.agent.action.knowledge.rag_router.rag_router import RagRouter
from agentuniverse.agent.action.knowledge.store.query import Query


class BaseRouter(RagRouter):
    def _rag_route(self, query: Query, store_list: List[str]) -> List[Tuple[Query, str]]:
        return [(query, store) for store in store_list]
