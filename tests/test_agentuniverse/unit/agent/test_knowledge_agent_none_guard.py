#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for knowledge.py operator-priority, agent None+str, react_planner acquire_tools None guard."""

import unittest


class TestKnowledgeOperatorPriority(unittest.TestCase):

    def test_as_langchain_tool_source_has_parenthesised_append(self):
        import inspect
        from agentuniverse.agent.action.knowledge.knowledge import Knowledge
        src = inspect.getsource(Knowledge.as_langchain_tool)
        # The fix parenthesises: (self.description or '') + args_description
        self.assertIn("(self.description or '') + args_description", src)
        # The buggy form must be gone.
        self.assertNotIn("self.description or '' + args_description", src)


class TestAgentDescriptionNoneGuard(unittest.TestCase):

    def test_as_langchain_tool_source_guards_none_description(self):
        import inspect
        from agentuniverse.agent.agent import Agent
        src = inspect.getsource(Agent.as_langchain_tool)
        self.assertIn('info.get("description") or ""', src)
        self.assertNotIn('info.get("description") + args_description', src)


class TestAgentExecutePlannerNoneGuard(unittest.TestCase):

    def test_execute_source_guards_planner_none(self):
        import inspect
        from agentuniverse.agent.agent import Agent
        src = inspect.getsource(Agent.execute)
        self.assertIn("plan.get('planner') or {}", src)
        self.assertNotIn("plan.get('planner').get('name')", src)


class TestReactPlannerAcquireToolsNoneGuard(unittest.TestCase):

    def test_acquire_tools_guards_none_tools(self):
        import inspect
        from agentuniverse.agent.plan.planner.react_planner.react_planner \
            import ReActPlanner
        src = inspect.getsource(ReActPlanner.acquire_tools)
        # Must have "is None" guards for tool, knowledge_tool, agent_tool.
        self.assertGreaterEqual(src.count("is None"), 3,
                                "acquire_tools must guard None for tool, "
                                "knowledge_tool, and agent_tool")


if __name__ == "__main__":
    unittest.main(verbosity=2)
