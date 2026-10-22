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
        """Initialize the SQL tool lazily and execute the supplied input."""
        if self.tool is None:
            self.get_sql_database()
        return super().execute(input, callbacks)

    async def async_execute(self, input: str, callbacks):
        if self.tool is None:
            self.get_sql_database()
        return await super().async_execute(input, callbacks)

    def get_sql_database(self):
        """Bind the configured database wrapper to the LangChain SQL tool."""
        db_wrapper = SQLDBWrapperManager().get_instance_obj(self.db_wrapper_name)
        self.tool = self.clz(db=db_wrapper.sql_database)
        self.description = self.tool.description

    def as_langchain(self) -> LangchainTool:
        """Return the lazily initialized SQL tool as a LangChain tool."""
        if self.tool is None:
            self.get_sql_database()
        return super().as_langchain()

    def get_langchain_tool(self, init_params: dict, clz: Type[BaseTool]):
        """Store the database wrapper name and SQL tool class for lazy setup."""
        self.db_wrapper_name = init_params.get("db_wrapper")
        self.clz = clz
