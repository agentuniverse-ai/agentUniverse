# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: langchain_tool.py
import importlib
import importlib
from typing import Optional, Type
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from langchain_core.tools import BaseTool


class LangChainTool(Tool):
    """LangChain tool wrapper for integrating LangChain tools into AgentUniverse.

    This tool acts as a bridge between AgentUniverse's tool system and LangChain's tool ecosystem.
    It dynamically loads and initializes LangChain tools based on configuration.
    
    Attributes:
        name: Tool name
        description: Tool description
        tool: The underlying LangChain tool instance
    """
    name: Optional[str] = ""
    description: Optional[str] = ""
    tool: Optional[BaseTool] = None

    def execute(self, input: str, callbacks):
        """Execute the LangChain tool with input and callbacks.
        
        Args:
            input (str): Input string for the tool
            callbacks: Callback handlers for the execution
            
        Returns:
            Any: Result from the LangChain tool execution
        """
        return self.tool.run(input, callbacks=callbacks)

    async def async_execute(self, input: str, callbacks):
        """Execute the LangChain tool asynchronously with input and callbacks.
        
        Args:
            input (str): Input string for the tool
            callbacks: Callback handlers for the execution
            
        Returns:
            Any: Result from the LangChain tool execution
        """
        return await self.tool.arun(input, callbacks=callbacks)

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> 'Tool':
        """Initialize the tool using component configer.
        
        Args:
            component_configer: Tool configuration object
            
        Returns:
            Tool: Initialized tool instance
        """
        super().initialize_by_component_configer(component_configer)
        self.tool = self.init_langchain_tool(component_configer)
        if not component_configer.description and self.tool is not None:
            self.description = self.tool.description
        return self

    def init_langchain_tool(self, component_configer):
        """Initialize the LangChain tool from configuration.
        
        Args:
            component_configer: Tool configuration object
            
        Returns:
            BaseTool: Initialized LangChain tool instance
        """
        langchain_info = component_configer.configer.value.get('langchain')
        module = langchain_info.get("module")
        class_name = langchain_info.get("class_name")
        module = importlib.import_module(module)
        clz = getattr(module, class_name)
        init_params = langchain_info.get("init_params")
        self.get_langchain_tool(init_params, clz)
        return self.tool

    def get_langchain_tool(self, init_params: dict, clz: Type[BaseTool]):
        """Create LangChain tool instance with initialization parameters.
        
        Args:
            init_params: Initialization parameters for the tool
            clz: LangChain tool class to instantiate
        """
        if init_params:
            self.tool = clz(**init_params)
        else:
            self.tool = clz()
