# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class ToolManager(ComponentManagerBase):
    """The ToolManager class, which is used to manage the tools."""

    def __init__(self):
        """Initialize the ToolManager."""
        super().__init__(ComponentEnum.TOOL)
