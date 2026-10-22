#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for toolkit + react_agent_template None guard fixes."""

import unittest


class TestToolkitToolDescriptionsNoneGuard(unittest.TestCase):

    def test_source_guards_none_tools(self):
        import inspect
        from agentuniverse.agent.action.toolkit.toolkit import Toolkit
        src = inspect.getsource(Toolkit.tool_descriptions.fget)
        self.assertIn("if tool is not None", src,
                      "tool_descriptions must filter None tools")


class TestAgentGetToolNamesNoneGuard(unittest.TestCase):

    def test_source_guards_none_toolkit(self):
        import inspect
        from agentuniverse.agent.agent import Agent
        src = inspect.getsource(Agent._get_tool_names)
        self.assertIn("if toolkit is None", src,
                      "_get_tool_names must guard None toolkit")


class TestReactAgentTemplateNoneGuard(unittest.TestCase):

    def test_convert_to_langchain_tool_guards_none(self):
        import inspect
        from agentuniverse.agent.template.react_agent_template import \
            ReActAgentTemplate
        src = inspect.getsource(ReActAgentTemplate._convert_to_langchain_tool)
        # Must have 3 None guards (tool, knowledge, agent)
        self.assertGreaterEqual(src.count("is None"), 3,
                                "_convert_to_langchain_tool must guard None "
                                "for tool, knowledge, and agent")

    def test_async_convert_guards_none(self):
        import inspect
        from agentuniverse.agent.template.react_agent_template import \
            ReActAgentTemplate
        src = inspect.getsource(ReActAgentTemplate._async_convert_to_langchain_tool)
        self.assertGreaterEqual(src.count("is None"), 3,
                                "_async_convert_to_langchain_tool must guard "
                                "None for tool, knowledge, and agent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
