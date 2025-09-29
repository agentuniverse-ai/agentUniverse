# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 15:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_manager.py
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class WorkflowManager(ComponentManagerBase):
    """The WorkflowManager class, which is used to manage workflow."""

    def __init__(self):
        super().__init__(ComponentEnum.WORKFLOW)
