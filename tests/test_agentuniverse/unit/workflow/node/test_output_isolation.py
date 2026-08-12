from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.node.start_node import StartNode
from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


def test_start_node_outputs_are_isolated_between_runs():
    node = StartNode(id="start", data={"outputs": [{"name": "input"}]})
    first_workflow = WorkflowOutput(workflow_start_params={"input": "first"})
    first_node_output = node.run(first_workflow)

    second_workflow = WorkflowOutput(workflow_start_params={"input": "second"})
    second_node_output = node.run(second_workflow)

    assert first_workflow.workflow_parameters["start"][0].value == "first"
    assert first_node_output.result[0].value == "first"
    assert second_workflow.workflow_parameters["start"][0].value == "second"
    assert first_node_output.result[0] is not second_node_output.result[0]


def test_end_node_outputs_are_isolated_between_runs():
    node = EndNode(
        id="end",
        data={
            "inputs": {
                "prompt": {"value": "{{answer}}"},
                "input_param": [
                    {
                        "name": "answer",
                        "value": {"type": "reference", "content": ["source", "answer"]},
                    }
                ],
            },
            "outputs": [{"name": "result"}],
        },
    )
    first_workflow = WorkflowOutput(
        workflow_parameters={"source": [NodeOutputParams(name="answer", value="first")]}
    )
    node.run(first_workflow)

    second_workflow = WorkflowOutput(
        workflow_parameters={"source": [NodeOutputParams(name="answer", value="second")]}
    )
    node.run(second_workflow)

    assert first_workflow.workflow_end_params == {"result": "first"}
    assert first_workflow.workflow_parameters["end"][0].value == "first"
    assert second_workflow.workflow_end_params == {"result": "second"}
