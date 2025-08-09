# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 12:08
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: application_component_manager.py
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.llm.llm_manager import LLMManager


@singleton
class ApplicationComponentManager(object):
    """The ComponentManager class, which is used to manage the components."""

    def __init__(self):
        """Initialize the ComponentManager."""
        self.__agent_manager: AgentManager = AgentManager()
        self.__llm_manager: LLMManager = LLMManager()
        self.__planner_manager: PlannerManager = PlannerManager()
        self.__knowledge: KnowledgeManager = KnowledgeManager()
        self.__tool_manager: ToolManager = ToolManager()
