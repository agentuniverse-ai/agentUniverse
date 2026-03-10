# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/24 12:00
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: rag_router.py

import asyncio
from abc import abstractmethod
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class RagRouter(ComponentBase):
    """The basic class for rag router."""

    component_type: ComponentEnum = ComponentEnum.RAG_ROUTER
    name: Optional[str] = None
    description: Optional[str] = None

    def rag_route(self, query: Query, store_list: List[str]) \
            -> List[Tuple[Query, str]]:
        """Accept query a list of store instance name, and return a list of
         query-store pair."""
        return self._rag_route(query, store_list)

    async def async_rag_route(self, query: Query, store_list: List[str]) \
            -> List[Tuple[Query, str]]:
        """Async version of :meth:`rag_route`.

        Default implementation delegates to the synchronous method via
        ``asyncio.to_thread``.  Subclasses may override for true async.
        """
        return await asyncio.to_thread(self.rag_route, query, store_list)

    def _rag_route(self, query: Query, store_list: List[str]) \
            -> List[Tuple[Query, str]]:
        """Accept query a list of store instance name, and return a list of
         query-store pair."""
        pass

    def _initialize_by_component_configer(self,
                                         rag_router_config: ComponentConfiger) \
            -> 'RagRouter':
        """Initialize the rag router by the ComponentConfiger object.

        Args:
            rag_router_config(ComponentConfiger): A configer contains rag router
            basic info.
        Returns:
            RagRouter: A rag router instance.
        """
        if rag_router_config.name:
            self.name = rag_router_config.name
        if rag_router_config.description:
            self.description = rag_router_config.description
        return self
