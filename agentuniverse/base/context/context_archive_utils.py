# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/17 11:00
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: context_archive_utils.py
import re
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


def get_current_context_archive():
    """Get (and lazily initialize) the current context archive.

        The archive is stored in FrameworkContextManager under the key
        ``'context_archive'``. If it does not exist, this function will create
        an empty dict and set it into the framework context.

        Returns:
            dict: The current context archive dictionary. Keys are arbitrary names,
            values are dicts containing at least ``data`` and ``description`` fields.

        Example:
            >>> archive = get_current_context_archive()
            >>> isinstance(archive, dict)
            True
        """
    context_archive = FrameworkContextManager().get_context(
        'context_archive', None)
    if not context_archive:
        context_archive = {}
        FrameworkContextManager().set_context('context_archive', {})

    return context_archive


def update_context_archive(name, data, description):
    """Update (or insert) a record in the current context archive.

        This method is a convenience wrapper to store arbitrary structured data
        into the framework-level archive. The record will be accessible by
        ``name`` and contain two fields: ``data`` and ``description``.

        Args:
            name: Unique key for the record (e.g., a step name or component name).
            data: Any serializable payload you want to archive.
            description: Human-readable description of the record.

        Example:
            >>> update_context_archive("retrieval", {"docs": 3}, "top-3 docs for query")
        """
    react_memory = get_current_context_archive()
    react_memory[name] = {
        'data': data,
        'description': description
    }