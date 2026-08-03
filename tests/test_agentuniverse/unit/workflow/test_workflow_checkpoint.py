from typing import ClassVar

import pytest

from agentuniverse.workflow.graph.graph import Graph
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow import Workflow
from agentuniverse.workflow.workflow_output import WorkflowOutput


class _RecordingNode(Node):
    calls: ClassVar[dict[str, int]] = {}

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        self.calls[self.id] = self.calls.get(self.id, 0) + 1
        return NodeOutput(
            node_id=self.id,
            status=NodeStatusEnum.SUCCEEDED,
            result={"call": self.calls[self.id]},
        )


class _Interruption(RuntimeError):
    pass


def _workflow() -> Workflow:
    graph = Graph()
    for node_id, node_type in (
        ("start", NodeEnum.START),
        ("work", NodeEnum.TOOL),
        ("end", NodeEnum.END),
    ):
        graph.add_node(
            node_id,
            instance=_RecordingNode(id=node_id, type=node_type, data={}),
            type=node_type.value,
        )
    graph.add_edge("start", "work", source_handler=None)
    graph.add_edge("work", "end", source_handler=None)
    return Workflow(id="durable-workflow", graph=graph)


def test_checkpoint_callback_can_persist_partial_progress_and_resume():
    _RecordingNode.calls = {}
    workflow = _workflow()
    checkpoints = []

    def persist_then_interrupt(snapshot: WorkflowOutput):
        checkpoints.append(snapshot.to_checkpoint_json())
        if "work" in snapshot.workflow_node_results:
            raise _Interruption

    with pytest.raises(_Interruption):
        workflow.run(
            {"input": "question"},
            checkpoint_callback=persist_then_interrupt,
        )

    assert _RecordingNode.calls == {"start": 1, "work": 1}

    result = workflow.resume(checkpoints[-1])

    assert _RecordingNode.calls == {"start": 1, "work": 1, "end": 1}
    assert set(result.workflow_node_results) == {"start", "work", "end"}
    assert result.workflow_start_params == {"input": "question"}


def test_checkpoint_json_round_trip_preserves_node_status():
    output = WorkflowOutput(
        workflow_id="durable-workflow",
        workflow_node_results={
            "node": NodeOutput(node_id="node", status=NodeStatusEnum.SUCCEEDED),
        },
    )

    restored = WorkflowOutput.from_checkpoint_json(output.to_checkpoint_json())

    assert restored.workflow_node_results["node"].status is NodeStatusEnum.SUCCEEDED


def test_resume_does_not_mutate_the_supplied_checkpoint_object():
    _RecordingNode.calls = {}
    workflow = _workflow()
    checkpoint = WorkflowOutput(
        workflow_id="durable-workflow",
        workflow_node_results={
            "start": NodeOutput(node_id="start", status=NodeStatusEnum.SUCCEEDED),
        },
    )

    result = workflow.resume(checkpoint)

    assert set(checkpoint.workflow_node_results) == {"start"}
    assert set(result.workflow_node_results) == {"start", "work", "end"}


def test_resume_rejects_a_checkpoint_for_another_workflow():
    workflow = _workflow()

    with pytest.raises(ValueError, match="does not match"):
        workflow.resume(WorkflowOutput(workflow_id="another-workflow"))


def test_resume_rejects_changed_start_parameters():
    workflow = _workflow()
    checkpoint = WorkflowOutput(
        workflow_id="durable-workflow",
        workflow_start_params={"input": "original"},
    )

    with pytest.raises(ValueError, match="Input parameters"):
        workflow.run({"input": "changed"}, resume_from=checkpoint)
