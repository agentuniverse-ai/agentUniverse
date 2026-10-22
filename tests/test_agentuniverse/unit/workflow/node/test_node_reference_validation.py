import pytest

from agentuniverse.workflow.node.node import Node
from agentuniverse.workflow.workflow_output import WorkflowOutput
from agentuniverse.workflow.node.node_config import NodeInputParams


def test_resolve_input_params_rejects_incomplete_reference():
    input_param = NodeInputParams(
        name="value",
        value={"type": "reference", "content": ["source"]},
    )

    with pytest.raises(ValueError, match="node id and output name"):
        Node._resolve_input_params([input_param], WorkflowOutput())


def test_resolve_input_params_rejects_missing_value_object():
    input_param = NodeInputParams(name="value", value=None)

    with pytest.raises(ValueError, match="missing a value"):
        Node._resolve_input_params([input_param], WorkflowOutput())
