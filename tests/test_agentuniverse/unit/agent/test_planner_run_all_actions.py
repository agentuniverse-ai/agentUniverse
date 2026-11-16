#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.action.tool.tool import Tool


class _StubPlanner(Planner):
    def invoke(self, agent_model: AgentModel, planner_input: dict,
               input_object: InputObject) -> dict:
        return {}


class _DemoTool(Tool):
    def execute(self, *args, **kwargs):
        return "tool result"

    def run(self, **kwargs):
        return "tool result"


class TestPlannerRunAllActionsBackground(unittest.TestCase):
    @staticmethod
    def _run(background: str) -> str:
        tools = {"demo_tool": _DemoTool(input_keys=[])}
        with patch("agentuniverse.agent.plan.planner.planner.ToolManager") as mgr:
            mgr.return_value.get_instance_obj.side_effect = lambda name: tools.get(name)
            planner = _StubPlanner()
            agent_model = AgentModel(profile={}, action={"tool": ["demo_tool"]})
            planner_input = {"background": background}
            planner.run_all_actions(agent_model, planner_input, InputObject({}))
        return planner_input["background"]

    def test_action_results_are_appended_to_existing_background(self) -> None:
        background = self._run("existing background")
        self.assertEqual(background, "existing backgroundtool result")

    def test_action_results_fill_empty_background(self) -> None:
        background = self._run("")
        self.assertEqual(background, "tool result")


if __name__ == '__main__':
    unittest.main()
