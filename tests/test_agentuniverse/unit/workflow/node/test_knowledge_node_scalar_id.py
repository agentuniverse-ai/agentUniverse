"""A configured scalar knowledge identifier is one ID, not its characters."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from agentuniverse.workflow.node.knowledge_node import KnowledgeNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


@pytest.mark.parametrize("configured", ["knowledge-main", {"content": "knowledge-main"},
                                         {"content": ["knowledge-main"]}])
def test_scalar_and_list_ids_resolve_same_knowledge(configured):
    """Both accepted literal forms and existing list form use the complete ID."""
    queries = []

    def query_knowledge(**kwargs):
        queries.append(kwargs)
        return [SimpleNamespace(text="retrieved content")]

    knowledge = SimpleNamespace(query_knowledge=query_knowledge)
    node = KnowledgeNode(id="lookup", data={
        "inputs": {
            "knowledge_param": [{"name": "id", "value": configured}],
            "input_param": [{"name": "query", "value": {"type": "input", "content": "question"}}],
        },
        "outputs": [{"name": "text", "type": "string"}],
    })
    workflow_output = WorkflowOutput()
    with patch("agentuniverse.workflow.node.knowledge_node.KnowledgeManager") as manager:
        manager.return_value.get_instance_obj.side_effect = (
            lambda identifier: knowledge if identifier == "knowledge-main" else None)
        result = node.run(workflow_output)
        manager.return_value.get_instance_obj.assert_called_once_with("knowledge-main")
    assert queries == [{"query_str": "question"}]
    assert result.result[0].value == "retrieved content"
    assert workflow_output.workflow_parameters["lookup"][0].value == "retrieved content"


@pytest.mark.parametrize("configured", ["", {"content": ""}])
def test_empty_scalar_is_reported_as_unknown_identifier(configured):
    """A scalar denotes one ID, so an empty ID follows the normal missing-ID error."""
    node = KnowledgeNode(data={"inputs": {"knowledge_param": [{"name": "id", "value": configured}]},
                               "outputs": [{"name": "text"}]})
    with patch("agentuniverse.workflow.node.knowledge_node.KnowledgeManager") as manager:
        manager.return_value.get_instance_obj.return_value = None
        with pytest.raises(ValueError, match="No knowledge with id  was found"):
            node.run(WorkflowOutput())
        manager.return_value.get_instance_obj.assert_called_once_with("")


def test_empty_list_remains_no_knowledge_selection():
    """The existing empty-list representation still produces empty retrieval text."""
    node = KnowledgeNode(id="lookup", data={
        "inputs": {"knowledge_param": [{"name": "id", "value": {"content": []}}]},
        "outputs": [{"name": "text"}],
    })
    with patch("agentuniverse.workflow.node.knowledge_node.KnowledgeManager") as manager:
        result = node.run(WorkflowOutput())
        manager.assert_not_called()
    assert result.result[0].value == ""
