from unittest.mock import patch

import pytest
from pydantic import ValidationError

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.node.retry_policy import RetryPolicy
from agentuniverse.workflow.workflow_output import WorkflowOutput


class _TransientFailure(RuntimeError):
    pass


class _FlakyNode(Node):
    failures_before_success: int = 0
    calls: int = 0

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        self.calls += 1
        if self.calls <= self.failures_before_success:
            raise _TransientFailure
        return NodeOutput(
            node_id=self.id,
            status=NodeStatusEnum.SUCCEEDED,
            metadata={"source": "test"},
        )


def test_node_retries_transient_failure_and_reports_attempt_count():
    node = _FlakyNode(
        id="flaky",
        type=NodeEnum.TOOL,
        data={},
        failures_before_success=2,
        retry_policy={"max_attempts": 3},
    )

    result = node.run(WorkflowOutput(workflow_id="workflow"))

    assert node.calls == 3
    assert result.metadata == {"source": "test", "attempt_count": 3}


def test_node_preserves_fail_fast_behavior_by_default():
    node = _FlakyNode(
        id="flaky",
        type=NodeEnum.TOOL,
        data={},
        failures_before_success=1,
    )

    with pytest.raises(_TransientFailure):
        node.run(WorkflowOutput(workflow_id="workflow"))

    assert node.calls == 1


def test_node_reraises_original_exception_after_attempt_limit():
    node = _FlakyNode(
        id="flaky",
        type=NodeEnum.TOOL,
        data={},
        failures_before_success=5,
        retry_policy={"max_attempts": 2},
    )

    with pytest.raises(_TransientFailure):
        node.run(WorkflowOutput(workflow_id="workflow"))

    assert node.calls == 2


def test_retry_policy_applies_capped_exponential_backoff():
    node = _FlakyNode(
        id="flaky",
        type=NodeEnum.TOOL,
        data={},
        failures_before_success=3,
        retry_policy={
            "max_attempts": 4,
            "initial_delay": 0.5,
            "backoff_multiplier": 3,
            "max_delay": 2,
        },
    )

    with patch("agentuniverse.workflow.node.node.time.sleep") as sleep:
        node.run(WorkflowOutput(workflow_id="workflow"))

    assert [call.args[0] for call in sleep.call_args_list] == [0.5, 1.5, 2]


@pytest.mark.parametrize(
    "values",
    [
        {"max_attempts": 0},
        {"initial_delay": -1},
        {"backoff_multiplier": 0.5},
        {"initial_delay": 2, "max_delay": 1},
    ],
)
def test_retry_policy_rejects_invalid_configuration(values):
    with pytest.raises(ValidationError):
        RetryPolicy(**values)


def test_retry_policy_delay_is_zero_before_retry():
    policy = RetryPolicy(initial_delay=1)

    assert policy.delay_before_attempt(1) == 0
