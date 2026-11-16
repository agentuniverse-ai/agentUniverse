import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agentuniverse.agent.plan.planner.nl2api_planner.nl2api_planner import Nl2ApiPlanner
from agentuniverse.agent.plan.planner.react_planner.react_planner import ReActPlanner
from agentuniverse.base.util import agent_util


class FakeTool:
    """Minimal Tool double that exposes the LangChain conversion."""

    def __init__(self, name):
        self.name = name

    def as_langchain(self):
        return SimpleNamespace(name=self.name)


def toolkit_manager(mapping):
    """Build a ToolkitManager double whose lookups come from ``mapping``."""
    manager = MagicMock()
    manager.get_instance_obj.side_effect = lambda name: mapping.get(name)
    return manager


def tool_manager(names):
    """Build a ToolManager double that returns a FakeTool for known names."""
    manager = MagicMock()
    manager.get_instance_obj.side_effect = lambda name: FakeTool(name) if name in names else None
    return manager


class ResolveToolNamesTest(unittest.TestCase):
    def test_direct_tools_and_toolkit_tools_are_merged_in_order(self):
        kit = SimpleNamespace(tool_names=["alpha", "beta"])
        manager = toolkit_manager({"kit": kit})

        with patch.object(agent_util, "ToolkitManager", return_value=manager):
            names = agent_util.resolve_tool_names({"tool": ["direct"], "toolkit": ["kit"]})

        self.assertEqual(names, ["direct", "alpha", "beta"])

    def test_unknown_toolkit_is_skipped(self):
        manager = toolkit_manager({})

        with patch.object(agent_util, "ToolkitManager", return_value=manager):
            names = agent_util.resolve_tool_names({"tool": ["direct"], "toolkit": ["missing"]})

        self.assertEqual(names, ["direct"])

    def test_toolkit_without_tools_contributes_nothing(self):
        manager = toolkit_manager({"kit": SimpleNamespace(tool_names=None)})

        with patch.object(agent_util, "ToolkitManager", return_value=manager):
            names = agent_util.resolve_tool_names({"toolkit": ["kit"]})

        self.assertEqual(names, [])

    def test_empty_action_returns_empty_list(self):
        manager = toolkit_manager({})

        with patch.object(agent_util, "ToolkitManager", return_value=manager):
            self.assertEqual(agent_util.resolve_tool_names({}), [])
            self.assertEqual(agent_util.resolve_tool_names({"tool": None, "toolkit": None}), [])

    def test_configured_tools_and_toolkits_keep_independent_copies(self):
        action = {"tool": ["direct"], "toolkit": []}
        manager = toolkit_manager({})

        with patch.object(agent_util, "ToolkitManager", return_value=manager):
            first = agent_util.resolve_tool_names(action)
            first.append("mutated")
            second = agent_util.resolve_tool_names(action)

        self.assertEqual(second, ["direct"])
        self.assertEqual(action["tool"], ["direct"])


class PlannerToolkitTest(unittest.TestCase):
    def test_react_planner_includes_toolkit_tools(self):
        action = {"tool": ["direct"], "toolkit": ["kit"]}
        toolkit = SimpleNamespace(tool_names=["alpha", "beta"])

        with patch.object(agent_util, "ToolkitManager", return_value=toolkit_manager({"kit": toolkit})), \
                patch("agentuniverse.agent.plan.planner.react_planner.react_planner.ToolManager",
                      return_value=tool_manager({"direct", "alpha", "beta"})):
            tools = ReActPlanner.acquire_tools(action)

        self.assertEqual([tool.name for tool in tools], ["direct", "alpha", "beta"])

    def test_nl2api_planner_includes_toolkit_tools(self):
        action = {"toolkit": ["kit"]}
        toolkit = SimpleNamespace(tool_names=["alpha", "beta"])

        with patch.object(agent_util, "ToolkitManager", return_value=toolkit_manager({"kit": toolkit})), \
                patch("agentuniverse.agent.plan.planner.nl2api_planner.nl2api_planner.ToolManager",
                      return_value=tool_manager({"alpha", "beta"})):
            tools = Nl2ApiPlanner.acquire_tools(action)

        self.assertEqual([tool.name for tool in tools], ["alpha", "beta"])

    def test_react_planner_keeps_working_without_a_toolkit(self):
        action = {"tool": ["direct"]}

        with patch.object(agent_util, "ToolkitManager", return_value=toolkit_manager({})), \
                patch("agentuniverse.agent.plan.planner.react_planner.react_planner.ToolManager",
                      return_value=tool_manager({"direct"})):
            tools = ReActPlanner.acquire_tools(action)

        self.assertEqual([tool.name for tool in tools], ["direct"])


if __name__ == "__main__":
    unittest.main()