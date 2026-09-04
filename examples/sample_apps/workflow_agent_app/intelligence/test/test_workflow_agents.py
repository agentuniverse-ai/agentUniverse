# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/7 10:49
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_workflow_agents.py
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class WorkflowAgentsTest(unittest.TestCase):
    """Test cases for the workflow demo agent.

    Exercises the ``demo_workflow_agent`` registered by the workflow agent
    sample app through the AgentManager public API.
    """

    def setUp(self) -> None:
        """Start the AgentUniverse runtime for the workflow demo app.

        Initializes the global runtime from ``config/config.toml`` so the
        workflow agent instance can be retrieved in the test method.
        """
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_discussion_agents(self):
        """Run the demo workflow agent and print its output.

        Fetches the ``demo_workflow_agent`` instance, runs it with a sample
        question and prints the 'output' field of the returned OutputObject
        so the workflow execution result can be inspected manually.
        """
        instance: Agent = AgentManager().get_instance_obj('demo_workflow_agent')
        output_object: OutputObject = instance.run(input="姚明是谁？")
        res_info = f"\nWorkflow agent execution result is :\n"
        res_info += output_object.get_data('output')
        print(res_info)


if __name__ == '__main__':
    unittest.main()
