# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/23 11:28
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: embedding_manager.py

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding


@singleton
class EmbeddingManager(ComponentManagerBase[Embedding]):
    """A singleton manager class of the embedding."""

    def __init__(self):
        super().__init__(ComponentEnum.EMBEDDING)
