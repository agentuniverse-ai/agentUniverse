# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/12 20:02
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: agent_manager.py

"""Agents manager."""

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class AgentManager(ComponentManagerBase):
    """The AgentManager class, which is used to manage the agents."""

    def __init__(self):
        """Initialize the Agent manager."""
        super().__init__(ComponentEnum.AGENT)
