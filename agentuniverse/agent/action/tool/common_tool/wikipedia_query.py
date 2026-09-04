# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: wikipedia_query.py


from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from agentuniverse.agent.action.tool.common_tool.langchain_tool import LangChainTool


class WikipediaTool(LangChainTool):
    """LangChain tool wrapper that answers queries by running the langchain Wikipedia query tool.
    """
    def init_langchain_tool(self, component_configer):
        """Build and return the langchain Wikipedia query run tool.

        Args:
            component_configer: The component configer (kept for interface compatibility).

        Returns:
            The langchain WikipediaQueryRun instance.
        """
        wrapper = WikipediaAPIWrapper()
        return WikipediaQueryRun(api_wrapper=wrapper)
