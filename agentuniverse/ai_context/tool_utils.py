# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/13
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: tool_utils.py

from typing import Dict, List, Tuple

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


def register_knowledge_as_tools(knowledge_names: List[str]) -> Tuple[List[str], List[Dict]]:
    """Wrap each Knowledge as a KnowledgeTool, register it, and return schemas.

    For each knowledge name, creates a ``KnowledgeTool`` wrapper and
    registers it in ``ToolManager`` so that the LLM tool-calling loop
    can dispatch calls to it just like a regular tool.

    Args:
        knowledge_names: List of registered knowledge names.

    Returns:
        A tuple of (tool_names, tool_schemas) for the created wrappers.
    """
    if not knowledge_names:
        return [], []

    from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
    from agentuniverse.agent.action.knowledge.knowledge_tool import (
        KnowledgeTool, KNOWLEDGE_TOOL_PREFIX,
    )

    manager = ToolManager()
    km = KnowledgeManager()
    tool_names: List[str] = []
    schemas: List[Dict] = []

    for kname in knowledge_names:
        knowledge = km.get_instance_obj(kname)
        if knowledge is None:
            continue
        # Derive the wrapper tool name from the knowledge's own schema,
        # so subclasses that override as_tool_schema() are respected.
        schema = knowledge.as_tool_schema()
        wrapper_name = schema.get("function", {}).get(
            "name", f"{KNOWLEDGE_TOOL_PREFIX}{knowledge.name}"
        )
        # Avoid duplicate registration
        existing = manager.get_instance_obj(wrapper_name, new_instance=False)
        if existing is None:
            wrapper = KnowledgeTool(knowledge=knowledge)
            manager.register(wrapper.get_instance_code(), wrapper)
        tool_names.append(wrapper_name)
        schemas.append(schema)

    return tool_names, schemas
