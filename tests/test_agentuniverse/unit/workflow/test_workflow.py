from unittest.mock import Mock, patch

import pytest

from agentuniverse.workflow.workflow import Workflow


def test_build_error_includes_workflow_id_and_graph_hint():
    workflow = Workflow(id="demo_workflow")

    with pytest.raises(ValueError) as exc_info:
        workflow.build()

    message = str(exc_info.value)
    assert "demo_workflow" in message
    assert "graph configuration is missing" in message
    assert "graph" in message


def test_run_error_includes_workflow_name_and_build_hint():
    workflow = Workflow(name="demo workflow")

    with pytest.raises(ValueError) as exc_info:
        workflow.run({})

    message = str(exc_info.value)
    assert "demo workflow" in message
    assert "has not been built" in message
    assert "build()" in message


def test_workflow_error_uses_unnamed_identity_when_id_and_name_missing():
    workflow = Workflow()

    with pytest.raises(ValueError) as exc_info:
        workflow.build()

    assert "<unnamed>" in str(exc_info.value)


def test_build_preserves_successful_workflow_behavior():
    graph_config = {"nodes": [{"id": "start"}], "edges": []}
    built_graph = Mock()
    workflow = Workflow(id="demo_workflow", graph_config=graph_config)

    with patch("agentuniverse.workflow.workflow.Graph") as graph_cls:
        graph_cls.return_value.build.return_value = built_graph

        result = workflow.build()

    assert result is workflow
    assert workflow.graph is built_graph
    graph_cls.return_value.build.assert_called_once_with("demo_workflow", graph_config)


def test_run_preserves_successful_workflow_behavior():
    graph = Mock()
    workflow = Workflow(id="demo_workflow")
    workflow.graph = graph
    input_params = {"question": "hello"}

    result = workflow.run(input_params)

    assert result.workflow_id == "demo_workflow"
    assert result.workflow_start_params == input_params
    graph.run.assert_called_once_with(result)
