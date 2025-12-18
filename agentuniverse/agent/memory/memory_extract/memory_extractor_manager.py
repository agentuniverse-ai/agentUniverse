# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 13:55
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com

from agentuniverse.agent.memory.memory_extract.memory_extract import MemoryExtract
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class MemoryExtractorManager(ComponentManagerBase[MemoryExtract]):
    """A singleton manager class of the MemoryExtract."""

    def __init__(self):
        super().__init__(ComponentEnum.MEMORY_EXTRACTOR)
