# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/13 11:31
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: base_router.py

from typing import List, Tuple

from agentuniverse.agent.action.knowledge.rag_router.rag_router import \
    RagRouter
from agentuniverse.agent.action.knowledge.store.query import Query


class BaseRouter(RagRouter):
    """Pass-through rag router that routes a query to every store in the given store list.
    """
    def _rag_route(self, query: Query, store_list: List[str]) \
            -> List[Tuple[Query, str]]:
        """Return the query paired with every store name in store_list.

        Args:
            query(Query): The knowledge query.
            store_list(List[str]): Candidate store names.

        Returns:
            List[Tuple[Query, str]]: The query paired with each store name.
        """
        return [(query, store) for store in store_list]
