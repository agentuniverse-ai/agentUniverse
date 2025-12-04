# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: context_manager_manager.py
"""Context manager manager singleton."""

from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.base.component.component_enum import ComponentEnum


class ContextManagerManager(ComponentManagerBase):
    """Manager for ContextManager instances (Singleton pattern).

    Usage:
        ctx_mgr = ContextManagerManager().get_instance_obj('default_context_manager')
    """

    def __init__(self):
        """Initialize the ContextManager manager."""
        super().__init__(ComponentEnum.CONTEXT_MANAGER)
