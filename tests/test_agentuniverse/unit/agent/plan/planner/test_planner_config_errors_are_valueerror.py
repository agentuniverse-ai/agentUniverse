#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Contract tests for planner / agent-template configuration errors.

The planners and SlaveRagAgentTemplate previously raised a bare ``Exception``
when an agent profile was missing both ``prompt_version`` and the
introduction/target/instruction triple. That made the failure impossible to
catch precisely and gave the user no hint which agent was misconfigured.

These tests pin the new contract:
- the raised exception is a ``ValueError`` (precise, catchable),
- the message names the offending agent (so a multi-agent setup points at the
  right config), and
- the workflow planner's missing-graph error is also a ``ValueError`` carrying
  the workflow id.

The tests build a minimal agent model + mocked PromptManager so the failure
path is reached without spinning up the full planner pipeline.
"""

import inspect
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_model import AgentPromptModel


def _agent_model_without_prompt() -> AgentModel:
    """An agent model that has neither prompt_version nor intro/target/instruction."""
    return AgentModel(info={"name": "broken_agent"}, profile={})


def _run_handle_prompt(planner_cls):
    """Instantiate the planner and drive its handle_prompt into the error path.

    PromptManager().get_instance_obj is stubbed to return None (no version
    prompt registered), so the only thing that can keep the planner out of the
    error branch is a non-empty profile_prompt_model — which the empty profile
    above guarantees is falsy.
    """
    planner = planner_cls()
    with patch(
        "agentuniverse.prompt.prompt_manager.PromptManager"
    ) as prompt_mgr:
        prompt_mgr.return_value.get_instance_obj.return_value = None
        planner.handle_prompt(_agent_model_without_prompt(), {})


class TestPlannerConfigErrorIsValueError(unittest.TestCase):
    """Every planner that validates prompt configuration raises ValueError."""

    PLANNER_MODULES = [
        "agentuniverse.agent.plan.planner.react_planner.react_planner",
        "agentuniverse.agent.plan.planner.nl2api_planner.nl2api_planner",
        "agentuniverse.agent.plan.planner.reviewing_planner.reviewing_planner",
        "agentuniverse.agent.plan.planner.executing_planner.executing_planner",
        "agentuniverse.agent.plan.planner.planning_planner.planning_planner",
        "agentuniverse.agent.plan.planner.rag_planner.rag_planner",
        "agentuniverse.agent.plan.planner.expressing_planner.expressing_planner",
    ]

    def _load(self, module_path: str):
        import importlib
        module = importlib.import_module(module_path)
        # The planner class is the only public top-level class in each module.
        classes = [obj for _, obj in inspect.getmembers(module, inspect.isclass)
                   if obj.__module__ == module_path and obj.__name__.endswith("Planner")]
        self.assertEqual(len(classes), 1,
                         f"expected exactly one Planner class in {module_path}, "
                         f"got {[c.__name__ for c in classes]}")
        return classes[0]

    def test_each_planner_raises_value_error_with_agent_name(self) -> None:
        for module_path in self.PLANNER_MODULES:
            with self.subTest(planner=module_path):
                planner_cls = self._load(module_path)
                with self.assertRaises(ValueError) as ctx:
                    _run_handle_prompt(planner_cls)
                # The agent name from the broken profile must appear in the
                # error so multi-agent setups can locate the misconfiguration.
                self.assertIn("broken_agent", str(ctx.exception),
                              f"{module_path} error did not name the agent: "
                              f"{ctx.exception}")

    def test_each_planner_does_not_raise_bare_exception(self) -> None:
        # Precise: the raised exception must be a ValueError, NOT a bare
        # Exception. `assertIsInstance(ValueError, ...)` would pass for
        # Exception too because ValueError is a subclass — so we assert the
        # concrete type is ValueError.
        for module_path in self.PLANNER_MODULES:
            with self.subTest(planner=module_path):
                planner_cls = self._load(module_path)
                try:
                    _run_handle_prompt(planner_cls)
                except ValueError:
                    pass
                except Exception as exc:  # noqa: BLE001 — the point of the test
                    self.fail(
                        f"{module_path} raised {type(exc).__name__} instead of "
                        "ValueError on missing prompt configuration")


class TestSlaveRagAgentTemplateConfigErrorIsValueError(unittest.TestCase):
    """The slave RAG template shares the same misconfiguration path."""

    def test_process_prompt_raises_value_error_with_agent_name(self) -> None:
        from agentuniverse.agent.template.slave_rag_agent_template import \
            SlaveRagAgentTemplate

        template = SlaveRagAgentTemplate()
        template.agent_model = _agent_model_without_prompt()
        with patch(
            "agentuniverse.prompt.prompt_manager.PromptManager"
        ) as prompt_mgr:
            prompt_mgr.return_value.get_instance_obj.return_value = None
            with self.assertRaises(ValueError) as ctx:
                # process_prompt pops expert_framework then builds the prompt
                # model from the (empty) profile.
                template.process_prompt({"prompt_name": "missing_prompt"})
        self.assertIn("broken_agent", str(ctx.exception))


class TestWorkflowPlannerMissingGraphIsValueError(unittest.TestCase):
    """The workflow planner's missing-graph error is a ValueError, not Exception."""

    def test_missing_graph_raises_value_error_with_workflow_id(self) -> None:
        from agentuniverse.agent.plan.planner.workflow_planner.workflow_planner \
            import WorkflowPlanner
        from agentuniverse.agent.input_object import InputObject

        planner = WorkflowPlanner()
        # An agent_model whose plan points at a workflow that has no graph.
        workflow = SimpleNamespace(graph_config=None)
        agent_model = AgentModel(
            info={"name": "wf_agent"},
            plan={"planner": {"workflow_id": "empty_workflow"}},
        )
        with patch(
            "agentuniverse.agent.plan.planner.workflow_planner.workflow_planner."
            "WorkflowManager"
        ) as wf_mgr:
            wf_mgr.return_value.get_instance_obj.return_value = workflow
            with self.assertRaises(ValueError) as ctx:
                planner.invoke(agent_model, {}, InputObject({}))
        # The workflow id appears so the user can locate the broken workflow.
        self.assertIn("empty_workflow", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
