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
    """LangChain tool wrapper that runs SQL through a configured database wrapper, loading the SQL database lazily on first use.
    """
    db_wrapper_name: Optional[str] = ""
    clz: Type[BaseTool] = BaseTool

    def execute(self, input: str, callbacks):
        """Execute the SQL tool, loading the sql database from the configured wrapper when the tool has not been initialized yet.

        Args:
            input(str): The sql command or tool input string.
            callbacks: The langchain callbacks passed to the underlying tool.

        Returns:
            The result of the underlying langchain tool execution.
        """
        if self.tool is None:
            self.get_sql_database()
        return super().execute(input, callbacks)

    def get_sql_database(self):
        """Build the underlying tool with the sql database of the configured wrapper and cache it on this instance.
        """
        db_wrapper = SQLDBWrapperManager().get_instance_obj(self.db_wrapper_name)
        self.tool = self.clz(db=db_wrapper.sql_database)
        self.description = self.tool.description

    def as_langchain(self) -> LangchainTool:
        """Return this tool in langchain tool form, loading the sql database first when needed.

        Returns:
            LangchainTool: The langchain representation of this tool.
        """
        if self.tool is None:
            self.get_sql_database()
        return super().as_langchain()

    def get_langchain_tool(self, init_params: dict, clz: Type[BaseTool]):
        """Record the database wrapper name and tool class that will be used to build the underlying sql tool.

        Args:
            init_params(dict): Init parameters containing the db_wrapper key.
            clz(Type[BaseTool]): The langchain tool class to instantiate.
        """
        self.db_wrapper_name = init_params.get("db_wrapper")
        self.clz = clz
