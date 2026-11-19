# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: demo_agent_template.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate


class DemoAgentTemplate(AgentTemplate):
    """Demo agent template echoing a single ``input`` key to a demo output."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Put the request input under the ``input`` agent key.

        Falls back to the template topic when the request carries no input.

        Args:
            input_object: The agent's input object.
            agent_input: The dict of agent input parameters.

        Returns:
            dict: The agent input dict enriched with the ``input`` key.
        """
        agent_input['input'] = input_object.get_data('input') or self.topic
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Return the raw agent result unchanged.

        Args:
            agent_result: The dict produced by the agent execution.

        Returns:
            dict: The same agent result dict.
        """
        return agent_result

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Run the demo template and return a placeholder output.

        Replace this body with the real template logic when extending the demo.

        Args:
            input_object: The agent's input object.
            agent_input: The dict of agent input parameters.

        Returns:
            dict: The execution result, e.g. ``{'output': 'demo output.'}``.
        """
        result = {'output': 'demo output.'}
        # Please fill out your template codes. The following is a sample of a peer template.
        # #================= sample ====================#
        # memory: Memory = self.process_memory(agent_input, **kwargs)
        # agents = self._generate_agents()
        # peer_work_pattern: PeerWorkPattern = WorkPatternManager().get_instance_obj('peer_work_pattern')
        # peer_work_pattern = peer_work_pattern.set_by_agent_model(**agents)
        # work_pattern_result = self.customized_execute(input_object=input_object, agent_input=agent_input,
        # memory=memory, peer_work_pattern=peer_work_pattern)
        # self.add_peer_memory(memory, agent_input, work_pattern_result)
        return result
