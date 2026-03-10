# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/23
# @FileName: knowledge_tool.py

from typing import Optional, List

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.enum import ToolTypeEnum

# Prefix used to namespace knowledge wrapper tools in ToolManager,
# avoiding collision with regular tool names.
KNOWLEDGE_TOOL_PREFIX = "__knowledge_tool__"


class KnowledgeTool(Tool):
    """A Tool wrapper around a Knowledge instance.

    This allows a Knowledge to be exposed as a callable tool in the
    OpenAI function-calling schema, so that the LLM can decide when
    to query a knowledge base during agentic tool-calling loops.

    The tool schema is derived from ``knowledge.as_tool_schema()``, so
    Knowledge subclasses can override that method to customise the tool
    name, description, and parameters exposed to the LLM.
    """

    knowledge: Optional[Knowledge] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, knowledge: Knowledge, **kwargs):
        # Read the schema that the Knowledge wants to expose
        schema = knowledge.as_tool_schema()
        func_def = schema.get("function", {})

        tool_name = func_def.get("name", f"{KNOWLEDGE_TOOL_PREFIX}{knowledge.name}")
        description = func_def.get("description", "")
        parameters = func_def.get("parameters", {})

        super().__init__(
            name=tool_name,
            description=description,
            tool_type=ToolTypeEnum.FUNC,
            input_keys=list(parameters.get("required", ["query"])),
            **kwargs,
        )
        self.knowledge = knowledge
        self.args_model_schema = parameters

    def get_function_schema(self) -> dict:
        """Delegate to the Knowledge's own schema definition."""
        return self.knowledge.as_tool_schema()

    def execute(self, query: str = "", **kwargs) -> str:
        """Query the wrapped knowledge and return results as text."""
        if not query:
            return ""
        docs: List[Document] = self.knowledge.query_knowledge(
            query_str=query, **kwargs
        )
        return self.knowledge.to_llm(docs)

    async def async_execute(self, query: str = "", **kwargs) -> str:
        """Async version of execute."""
        if not query:
            return ""
        docs: List[Document] = await self.knowledge.async_query_knowledge(
            query_str=query, **kwargs
        )
        return self.knowledge.to_llm(docs)

    def create_copy(self):
        """Return self — KnowledgeTool is a lightweight wrapper, no need to deep-copy."""
        return self
