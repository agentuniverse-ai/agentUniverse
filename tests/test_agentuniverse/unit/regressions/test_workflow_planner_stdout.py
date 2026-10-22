from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agentuniverse.agent.plan.planner.workflow_planner.workflow_planner import WorkflowPlanner


def test_workflow_planner_does_not_print_intermediate_results(capsys):
    workflow = MagicMock(graph_config={})
    workflow.build.return_value = workflow
    workflow.run.return_value = SimpleNamespace(
        workflow_node_results={"node": "value"},
        workflow_end_params={"answer": "ok"},
    )
    agent_model = SimpleNamespace(plan={"planner": {"workflow_id": "workflow"}})
    input_object = MagicMock()
    input_object.to_dict.return_value = {"input": "value"}
    manager = SimpleNamespace(get_instance_obj=lambda component_instance_name: workflow)

    with patch(
        "agentuniverse.agent.plan.planner.workflow_planner.workflow_planner.WorkflowManager",
        return_value=manager,
    ):
        result = WorkflowPlanner().invoke(agent_model, {}, input_object)

    assert result == {"answer": "ok"}
    assert capsys.readouterr().out == ""
