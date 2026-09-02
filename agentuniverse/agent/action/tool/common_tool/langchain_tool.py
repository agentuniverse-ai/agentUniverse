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
    """Tool that wraps a langchain BaseTool instance."""
    name: Optional[str] = ""
    description: Optional[str] = ""
    tool: Optional[BaseTool] = None

    def execute(self, input: str, callbacks):
        """Run the wrapped langchain tool synchronously.
        
        Args:
            input (str): The tool input.
            callbacks: LangChain callbacks for the run.
        
        Returns:
            The tool execution result.
        """
        return self.tool.run(input, callbacks=callbacks)

    async def async_execute(self, input: str, callbacks):
        """Run the wrapped langchain tool asynchronously.
        
        Args:
            input (str): The tool input.
            callbacks: LangChain callbacks for the run.
        
        Returns:
            The tool execution result.
        """
        return await self.tool.arun(input, callbacks=callbacks)

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> 'Tool':
        """Initialize the tool from a component configer.
        
        Args:
            component_configer (ToolConfiger): The component configer.
        
        Returns:
            Tool: The initialized tool.
        """
        super().initialize_by_component_configer(component_configer)
        self.tool = self.init_langchain_tool(component_configer)
        if not component_configer.description and self.tool is not None:
            self.description = self.tool.description
        return self

    def init_langchain_tool(self, component_configer):
        """Instantiate the wrapped langchain tool from the configer's langchain section.
        
        Args:
            component_configer: The component configer holding langchain metadata.
        
        Returns:
            BaseTool: The instantiated langchain tool.
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
        """Create and store the langchain tool instance.
        
        Args:
            init_params (dict): Constructor kwargs for the tool class.
            clz (Type[BaseTool]): The langchain tool class.
        """
        if init_params:
            self.tool = clz(**init_params)
        else:
            self.tool = clz()
