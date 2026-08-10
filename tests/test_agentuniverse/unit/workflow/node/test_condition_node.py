from agentuniverse.workflow.node.condition_node import ConditionNode
from agentuniverse.workflow.node.node_config import (
    ConditionBranchParams,
    ConditionParams,
    InputValueParams,
    NodeInputParams,
    NodeOutputParams,
)
from agentuniverse.workflow.workflow_output import WorkflowOutput


def _const(value, input_type: str = 'const'):
    """A node input whose value is a literal constant."""
    return NodeInputParams(value=InputValueParams(type=input_type, content=value))


def _condition(compare: str, left, right=None):
    return ConditionParams(
        compare=compare,
        left=_const(left),
        right=_const(right) if right is not None else None,
    )


def _run_branches(branches, workflow_parameters=None) -> str:
    node = ConditionNode(id='c', data={'inputs': {'branches': branches}})
    workflow_output = WorkflowOutput()
    if workflow_parameters:
        workflow_output.workflow_parameters = workflow_parameters
    return node.run(workflow_output).edge_source_handler


# --- regression: single branch / single condition (protects the current demo behavior) ---

def test_single_branch_single_condition_match():
    branches = [ConditionBranchParams(name='branch-1', conditions=[_condition('equal', 'yes', 'yes')])]
    assert _run_branches(branches) == 'branch-1'


def test_single_branch_single_condition_no_match_falls_to_default():
    branches = [ConditionBranchParams(name='branch-1', conditions=[_condition('equal', 'yes', 'no')])]
    assert _run_branches(branches) == 'branch-default'


def test_not_equal_compare_match():
    branches = [ConditionBranchParams(name='branch-1', conditions=[_condition('not_equal', 'a', 'b')])]
    assert _run_branches(branches) == 'branch-1'


def test_blank_compare_match():
    branches = [ConditionBranchParams(name='branch-1', conditions=[_condition('blank', None)])]
    assert _run_branches(branches) == 'branch-1'


# --- fix scenario A: multi-branch if/elif/else ---

def test_multi_branch_matches_second_branch():
    # Before: only branches[0] was evaluated, so a matching 2nd branch was ignored
    #         and the node wrongly fell through to 'branch-default'.
    branches = [
        ConditionBranchParams(name='branch-1', conditions=[_condition('equal', 'yes', 'no')]),
        ConditionBranchParams(name='branch-2', conditions=[_condition('equal', 'yes', 'yes')]),
    ]
    assert _run_branches(branches) == 'branch-2'


def test_multi_branch_none_match_falls_to_default():
    branches = [
        ConditionBranchParams(name='branch-1', conditions=[_condition('equal', 'a', 'b')]),
        ConditionBranchParams(name='branch-2', conditions=[_condition('equal', 'c', 'd')]),
    ]
    assert _run_branches(branches) == 'branch-default'


def test_multi_branch_first_match_wins():
    # When two branches both match, the first one wins (if/elif order).
    branches = [
        ConditionBranchParams(name='branch-1', conditions=[_condition('equal', 'x', 'x')]),
        ConditionBranchParams(name='branch-2', conditions=[_condition('equal', 'x', 'x')]),
    ]
    assert _run_branches(branches) == 'branch-1'


# --- fix scenario B: multiple conditions combined with AND within a branch ---

def test_multi_condition_and_all_match():
    branches = [ConditionBranchParams(name='branch-1', conditions=[
        _condition('equal', 'x', 'x'),
        _condition('equal', 'y', 'y'),
    ])]
    assert _run_branches(branches) == 'branch-1'


def test_multi_condition_and_partial_match_does_not_hit():
    # Before: only conditions[0] was evaluated, so a partially-matching branch
    #         was wrongly taken (effectively loosening the AND requirement).
    branches = [ConditionBranchParams(name='branch-1', conditions=[
        _condition('equal', 'x', 'x'),
        _condition('equal', 'x', 'y'),  # False -> AND must fail
    ])]
    assert _run_branches(branches) == 'branch-default'


# --- fix scenario E: empty conditions list behaves as an else / catch-all branch ---

def test_empty_conditions_treated_as_else():
    branches = [ConditionBranchParams(name='branch-1', conditions=[])]
    assert _run_branches(branches) == 'branch-1'


def test_empty_conditions_branch_acts_as_catch_all():
    branches = [
        ConditionBranchParams(name='branch-1', conditions=[_condition('equal', 'a', 'b')]),
        ConditionBranchParams(name='branch-2', conditions=[]),  # else / catch-all
    ]
    assert _run_branches(branches) == 'branch-2'


# --- reference value resolution (protects resolve_value during the refactor) ---

def test_reference_value_resolution_from_upstream_node():
    # Upstream node '1' produced an output named 'amount' with value '5000'.
    workflow_parameters = {
        '1': [NodeOutputParams(name='amount', type='string', value='5000')]
    }
    left = NodeInputParams(value=InputValueParams(type='reference', content=['1', 'amount']))
    right = _const('5000')
    branches = [ConditionBranchParams(name='branch-1', conditions=[
        ConditionParams(compare='equal', left=left, right=right)
    ])]
    assert _run_branches(branches, workflow_parameters=workflow_parameters) == 'branch-1'
