#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import builtins
import unittest
from unittest.mock import Mock, patch

from agentuniverse.agent.plan.planner.workflow_planner.workflow_planner import WorkflowPlanner


class WorkflowPlannerTest(unittest.TestCase):
    def test_invoke_logs_node_results_without_printing(self):
        planner = WorkflowPlanner()
        agent_model = Mock(plan={"planner": {"workflow_id": "workflow"}})
        workflow_output = Mock(
            workflow_node_results={"node": "ok"},
            workflow_end_params={"answer": "done"}
        )
        workflow = Mock(graph_config={"nodes": []})
        workflow.build.return_value = workflow
        workflow.run.return_value = workflow_output
        input_object = Mock()
        input_object.to_dict.return_value = {"input": "hello"}

        with patch("agentuniverse.agent.plan.planner.workflow_planner.workflow_planner.WorkflowManager") as manager_cls, \
                patch("agentuniverse.agent.plan.planner.workflow_planner.workflow_planner.LOGGER") as mock_logger, \
                patch.object(builtins, "print") as mock_print:
            manager_cls.return_value.get_instance_obj.return_value = workflow
            result = planner.invoke(agent_model, {}, input_object)

        self.assertEqual(result, {"answer": "done"})
        mock_logger.debug.assert_called_once_with("Workflow node results: {'node': 'ok'}")
        mock_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()
