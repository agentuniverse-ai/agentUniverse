# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/17 11:55
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: work_pattern_manager.py
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class WorkPatternManager(ComponentManagerBase[WorkPattern]):
    """A singleton manager class of the WorkPattern."""

    def __init__(self):
        """Initialize the work pattern manager.
        """
        super().__init__(ComponentEnum.WORK_PATTERN)
