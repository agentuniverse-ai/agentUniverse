import pytest

from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "result=0"),
        (False, "result=False"),
        (None, "result="),
    ],
)
def test_end_node_preserves_falsey_template_values(value, expected):
    node = EndNode(
        id="end",
        data={
            "inputs": {
                "input_param": [
                    {
                        "name": "value",
                        "value": {
                            "type": "reference",
                            "content": ["source", "value"],
                        },
                    }
                ],
                "prompt": {"value": "result={{value}}"},
            },
            "outputs": [{"name": "answer"}],
        },
    )
    workflow_output = WorkflowOutput(
        workflow_parameters={
            "source": [NodeOutputParams(name="value", value=value)]
        }
    )

    result = node.run(workflow_output)

    assert result.result[0].value == expected
    assert workflow_output.workflow_end_params == {"answer": expected}
