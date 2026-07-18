# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: wikipedia_query.py

from agentuniverse.agent.action.tool.common_tool.langchain_tool import LangChainTool


def _get_wikipedia_tool_classes():
    try:
        from langchain_community.tools import WikipediaQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper
    except ImportError as exc:
        raise ImportError(
            "langchain-community and wikipedia are required to use WikipediaTool. "
            "Install them with `pip install langchain-community wikipedia`."
        ) from exc
    return WikipediaAPIWrapper, WikipediaQueryRun


class WikipediaTool(LangChainTool):
    def init_langchain_tool(self, component_configer):
        WikipediaAPIWrapper, WikipediaQueryRun = _get_wikipedia_tool_classes()
        wrapper = WikipediaAPIWrapper()
        return WikipediaQueryRun(api_wrapper=wrapper)
