from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.workflow_output import WorkflowOutput
from agentuniverse.workflow.node.node_config import NodeOutputParams


def test_end_node_preserves_falsey_template_values():
    node = EndNode(
        id="end",
        data={
            "inputs": {
                "prompt": {"value": "count={{count}}, enabled={{enabled}}"},
                "input_param": [
                    {"name": "count", "value": {"type": "reference", "content": ["source", "count"]}},
                    {"name": "enabled", "value": {"type": "reference", "content": ["source", "enabled"]}},
                ],
            },
            "outputs": [{"name": "result"}],
        },
    )
    workflow_output = WorkflowOutput(workflow_id="workflow")
    workflow_output.workflow_parameters["source"] = [
        NodeOutputParams(name="count", value=0),
        NodeOutputParams(name="enabled", value=False),
    ]

    result = node.run(workflow_output)

    assert result.result[0].value == "count=0, enabled=False"
