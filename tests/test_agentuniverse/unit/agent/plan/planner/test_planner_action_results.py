from types import SimpleNamespace

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner import planner as planner_module


class ConcretePlanner(planner_module.Planner):
    def invoke(self, agent_model, planner_input, input_object):
        return {}


class StructuredResultTool:
    input_keys = []

    def run(self, **kwargs):
        return {"status": "成功", "items": [1, 2]}


class StructuredResultToolManager:
    def get_instance_obj(self, name):
        return StructuredResultTool()


def test_run_all_actions_serializes_structured_tool_results(monkeypatch):
    monkeypatch.setattr(planner_module, "ToolManager", StructuredResultToolManager)
    planner_input = {"background": ""}

    ConcretePlanner().run_all_actions(
        SimpleNamespace(action={"tool": ["structured_result_tool"]}),
        planner_input,
        InputObject({}),
    )

    assert planner_input["background"] == '{"status": "成功", "items": [1, 2]}'
