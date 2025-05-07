# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: sql_langchain_tool.py

from typing import Type, Optional
from agentuniverse.agent.action.tool.common_tool.langchain_tool import LangChainTool
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager
from langchain_core.tools import BaseTool, Tool as LangchainTool


class SqlLangchainTool(LangChainTool):
    db_wrapper_name: Optional[str] = ""
    clz: Type[BaseTool] = BaseTool

    def execute(self, input: str, callbacks):
        if self.tool is None:
            self.get_sql_database()
        return super().execute(input, callbacks)

    def get_sql_database(self):
        db_wrapper = SQLDBWrapperManager().get_instance_obj(self.db_wrapper_name)
        self.tool = self.clz(db=db_wrapper.sql_database)
        self.description = self.tool.description

    def as_langchain(self) -> LangchainTool:
        if self.tool is None:
            self.get_sql_database()
        return super().as_langchain()

    def get_langchain_tool(self, init_params: dict, clz: Type[BaseTool]):
        self.db_wrapper_name = init_params.get("db_wrapper")
        self.clz = clz
