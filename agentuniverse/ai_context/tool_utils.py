# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/13
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: tool_utils.py

from typing import Dict, List

from agentuniverse.agent.action.tool.tool_manager import ToolManager


def build_tools_schema(tool_names: List[str]) -> List[Dict]:
    """Build OpenAI function-calling compatible tool schemas from tool names.

    Resolves each tool name through ToolManager, then calls
    ``tool.get_function_schema()`` to produce the schema dict.

    Args:
        tool_names: List of registered tool names.

    Returns:
        List of tool schema dicts in OpenAI function-calling format.
        Tools that cannot be resolved are silently skipped.
    """
    if not tool_names:
        return []

    manager = ToolManager()
    schemas: List[Dict] = []
    for name in tool_names:
        tool = manager.get_instance_obj(name, new_instance=False)
        if tool is not None:
            schemas.append(tool.get_function_schema())
    return schemas
