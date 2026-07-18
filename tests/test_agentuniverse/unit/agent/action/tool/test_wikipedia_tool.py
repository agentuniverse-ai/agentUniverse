#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import wikipedia_query as wiki_module
from agentuniverse.agent.action.tool.common_tool.wikipedia_query import WikipediaTool


class FakeWikipediaAPIWrapper:
    pass


class FakeWikipediaQueryRun:
    def __init__(self, api_wrapper):
        self.api_wrapper = api_wrapper


class TestWikipediaTool(unittest.TestCase):
    def test_init_langchain_tool_loads_wikipedia_classes_lazily(self):
        tool = WikipediaTool()

        with patch.object(
            wiki_module,
            "_get_wikipedia_tool_classes",
            return_value=(FakeWikipediaAPIWrapper, FakeWikipediaQueryRun),
        ) as load_classes:
            langchain_tool = tool.init_langchain_tool(component_configer=None)

        load_classes.assert_called_once_with()
        self.assertIsInstance(langchain_tool, FakeWikipediaQueryRun)
        self.assertIsInstance(langchain_tool.api_wrapper, FakeWikipediaAPIWrapper)


if __name__ == "__main__":
    unittest.main()
