# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/10 18:53
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_storage_manager.py
from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class MemoryStorageManager(ComponentManagerBase[MemoryStorage]):
    """A singleton manager class of the MemoryStorage."""

    def __init__(self):
        """Initialize the memory storage manager.
        """
        super().__init__(ComponentEnum.MEMORY_STORAGE)
