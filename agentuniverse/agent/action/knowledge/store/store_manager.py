# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/24 11:45
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: store_manager.py

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.agent.action.knowledge.store.store import Store


@singleton
class StoreManager(ComponentManagerBase[Store]):
    """A singleton manager class of the reader."""

    def __init__(self):
        super().__init__(ComponentEnum.STORE)
