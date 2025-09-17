# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 14:16
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: rag_router_manager.py

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.agent.action.knowledge.rag_router.rag_router import RagRouter


@singleton
class RagRouterManager(ComponentManagerBase[RagRouter]):
    """A singleton manager class of the RagRouter."""

    def __init__(self):
        super().__init__(ComponentEnum.RAG_ROUTER)
