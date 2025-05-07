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
    name: Optional[str] = ""
    description: Optional[str] = ""
    tool: Optional[BaseTool] = None

    def execute(self, input: str, callbacks):
        return self.tool.run(input, callbacks=callbacks)

    async def async_execute(self, input: str, callbacks):
        return await self.tool.arun(input, callbacks=callbacks)

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> 'Tool':
        super().initialize_by_component_configer(component_configer)
        self.tool = self.init_langchain_tool(component_configer)
        if not component_configer.description and self.tool is not None:
            self.description = self.tool.description
        return self

    def init_langchain_tool(self, component_configer):
        langchain_info = component_configer.configer.value.get('langchain')
        module = langchain_info.get("module")
        class_name = langchain_info.get("class_name")
        module = importlib.import_module(module)
        clz = getattr(module, class_name)
        init_params = langchain_info.get("init_params")
        self.get_langchain_tool(init_params, clz)
        return self.tool

    def get_langchain_tool(self, init_params: dict, clz: Type[BaseTool]):
        if init_params:
            self.tool = clz(**init_params)
        else:
            self.tool = clz()
