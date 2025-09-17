# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 16:37
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: node_constant.py
from agentuniverse.workflow.node.agent_node import AgentNode
from agentuniverse.workflow.node.condition_node import ConditionNode
from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.node.knowledge_node import KnowledgeNode
from agentuniverse.workflow.node.llm_node import LLMNode
from agentuniverse.workflow.node.start_node import StartNode
from agentuniverse.workflow.node.tool_node import ToolNode

NODE_CLS_MAPPING = {
    "start": StartNode,
    "end": EndNode,
    "tool": ToolNode,
    "knowledge": KnowledgeNode,
    "agent": AgentNode,
    "llm": LLMNode,
    "ifelse": ConditionNode,
}
