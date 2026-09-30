# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/29 15:31
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: framework_context.py

from typing import Dict, Any

from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


class FrameworkContext:
    """A context class that provides a thread level variable dictionary."""

    def __init__(self, context: Dict[str, Any]):
        """Save context dict and init an empty dict to save prior context.

        Args:
            context (`dict`):
                A dict contains all kv pairs
                which will be added to current context.
        """
        self.context = context
        self.old_state = {}

    def __enter__(self):
        """Preserve the prior context and set a new one."""
        # A FrameworkContext instance may be reused. Do not let values captured
        # by an earlier entry leak into a later restoration.
        self.old_state = {}
        for key, value in self.context.items():
            if FrameworkContextManager().is_context_exist(key):
                self.old_state[key] = FrameworkContextManager().get_context(key)
            FrameworkContextManager().set_context(key, value)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Clear the current context and revert to the prior context."""
        for key, value in self.context.items():
            if key in self.old_state:
                FrameworkContextManager().set_context(key, self.old_state[key])
            else:
                FrameworkContextManager().del_context(key)
