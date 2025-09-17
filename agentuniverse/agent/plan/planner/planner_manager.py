# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 11:04
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: planner_manager.py
"""Planner Management Class."""

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class PlannerManager(ComponentManagerBase):
    """The PlannerManager class, which is used to manage the planners."""

    def __init__(self):
        """Initialize the PlannerManager."""
        super().__init__(ComponentEnum.PLANNER)
