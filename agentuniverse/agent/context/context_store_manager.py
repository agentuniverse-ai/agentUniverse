# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: context_store_manager.py
"""Context store manager singleton."""

from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.base.component.component_enum import ComponentEnum


class ContextStoreManager(ComponentManagerBase):
    """Manager for ContextStore instances (Singleton pattern).

    Usage:
        store = ContextStoreManager().get_instance_obj('ram_context_store')
    """

    def __init__(self):
        """Initialize the ContextStore manager."""
        super().__init__(ComponentEnum.CONTEXT_STORE)
