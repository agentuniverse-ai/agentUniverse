from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agentuniverse.agent.default.workflow_agent.workflow_agent import WorkflowAgent


def test_workflow_agent_does_not_print_intermediate_results(capsys):
    workflow = MagicMock(graph_config={})
    workflow.build.return_value = workflow
    workflow.run.return_value = SimpleNamespace(
        workflow_node_results={"node": "value"},
        workflow_end_params={"answer": "ok"},
    )
    input_object = MagicMock()
    input_object.to_dict.return_value = {"input": "value"}
    agent = SimpleNamespace(workflow_id="workflow")

    manager = SimpleNamespace(get_instance_obj=lambda _: workflow)
    with patch(
        "agentuniverse.agent.default.workflow_agent.workflow_agent.WorkflowManager",
        return_value=manager,
    ):
        result = WorkflowAgent.execute(agent, input_object, {})

    assert result == {"answer": "ok"}
    assert capsys.readouterr().out == ""
