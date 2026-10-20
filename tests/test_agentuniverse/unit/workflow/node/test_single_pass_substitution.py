"""Values inserted into workflow templates are data, not further placeholders."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.node.llm_node import LLMNode
from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


def render(node_type, template, values):
    """Run the public node path, substituting only the external LLM service."""
    inputs = {"input_param": [
        {"name": key, "value": {"type": "reference", "content": ["source", key]}}
        for key in values
    ]}
    if node_type is EndNode:
        inputs["prompt"] = {"value": template}
    else:
        inputs["llm_param"] = [{"name": "id", "value": "test-llm"},
                               {"name": "prompt", "value": template}]
    node = node_type(id="render", data={"inputs": inputs, "outputs": [{"name": "text"}]})
    workflow_output = WorkflowOutput(workflow_parameters={
        "source": [NodeOutputParams(name=key, value=value) for key, value in values.items()]
    })
    if node_type is EndNode:
        result = node.run(workflow_output)
        assert workflow_output.workflow_end_params == {"text": result.result[0].value}
        return result.result[0].value
    with patch("agentuniverse.workflow.node.llm_node.LLMManager") as manager:
        llm = manager.return_value.get_instance_obj.return_value
        llm.call.return_value = SimpleNamespace(text="model output")
        result = node.run(workflow_output)
        assert result.result[0].value == "model output"
        llm.call.assert_called_once()
        assert llm.call.call_args.kwargs["streaming"] is False
        return llm.call.call_args.kwargs["messages"][0]["content"]


@pytest.mark.parametrize("node_type", [EndNode, LLMNode])
@pytest.mark.parametrize("template,values,expected", [
    ("{{first}} / {{second}}", {"first": "{{second}}", "second": "resolved"}, "{{second}} / resolved"),
    ("{{second}} / {{first}}", {"first": "{{second}}", "second": "resolved"}, "resolved / {{second}}"),
    ("{{first}} {{first}} {{second}}", {"first": "{{first}}!", "second": "done"}, "{{first}}! {{first}}! done"),
    ("{{first}}", {"first": r"literal\1\g<name>"}, r"literal\1\g<name>"),
    ("{{first}}", {"first": "{{unknown}}"}, "{{unknown}}"),
    ("{{a}} {{a.b}} {{a+b}}", {"a": "{{a.b}}", "a.b": "dot", "a+b": "plus"}, "{{a.b}} dot plus"),
])
def test_inserted_values_are_not_expanded(node_type, template, values, expected):
    """Each original placeholder is substituted once; keys and values stay literal."""
    assert render(node_type, template, values) == expected
    assert render(node_type, template, dict(reversed(list(values.items())))) == expected


@pytest.mark.parametrize("node_type", [EndNode, LLMNode])
@pytest.mark.parametrize("value", [0, False, [], None, ""])
def test_existing_falsey_semantics_are_unchanged(node_type, value):
    """This fix deliberately leaves the separate EndNode falsey-value issue alone."""
    expected = str(value) if node_type is LLMNode and value is not None else ""
    assert render(node_type, "before {{value}} after", {"value": value}) == f"before {expected} after"


@pytest.mark.parametrize("node_type", [EndNode, LLMNode])
def test_original_unknown_placeholder_still_raises(node_type):
    """Only unknown placeholders in inserted data are retained, not missing inputs."""
    with pytest.raises(ValueError, match=r"missing.*not found"):
        render(node_type, "{{known}} {{missing}}", {"known": "data"})
