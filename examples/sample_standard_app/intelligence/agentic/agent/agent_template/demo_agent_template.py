# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: demo_agent_template.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate


class DemoAgentTemplate(AgentTemplate):

    """Minimal demo agent template that returns a canned demo output and serves as a starting point for custom templates.
    """
    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Copy the user input from the input object into the agent input, falling back to the template topic when empty.

        Args:
            input_object(InputObject): The user input object.
            agent_input(dict): The agent input dictionary to be filled.

        Returns:
            dict: The updated agent input.
        """
        agent_input['input'] = input_object.get_data('input') or self.topic
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Return the agent result unchanged.

        Args:
            agent_result(dict): The raw agent result.

        Returns:
            dict: The agent result.
        """
        return agent_result

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Return a placeholder demo output dict.

        Args:
            input_object(InputObject): The user input object.
            agent_input(dict): The agent input dictionary.
            **kwargs: Extra keyword arguments accepted for interface compatibility.

        Returns:
            dict: A dict containing the demo output.
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
