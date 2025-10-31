# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/03 18:30
# @Author  : zhangxi
# @Email   : 1724585800@qq.com
# @FileName: discussion_group_template.py
from collections import deque
from typing import Optional

from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.agent_util import assemble_memory_output, assemble_memory_input
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt


class DiscussionGroupTemplate(AgentTemplate):
    participant_names: Optional[list[str]] = None
    total_round: int = 2
    topic: Optional[str] = None

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input') or self.topic
        agent_input['participants'] = self.participant_names
        agent_input['total_round'] = self.total_round
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return agent_result

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        participant_agents = self.generate_participant_agents()
        return self.agents_run(participant_agents, agent_input, input_object)

    def generate_participant_agents(self) -> dict:
        if len(self.participant_names) == 0:
            raise ValueError("The participant agents is empty.")
        agents = dict()
        for participant_name in self.participant_names:
            agents[participant_name] = AgentManager().get_instance_obj(participant_name)
        return agents

    def agents_run(self, participant_agents: dict, agent_input: dict, input_object: InputObject) -> dict:
        """ Invoke the participant agents and host agent.

        Args:
            participant_agents (dict): Participant agents.
            agent_input (dict): Agent input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The agent result.
        """
        total_round: int = self.total_round
        LOGGER.info(f"The topic of discussion is {agent_input.get('input')}")
        LOGGER.info(f"The participant agents are {'|'.join(participant_agents.keys())}")

        # The memory list is used to store memory information that will be passed between participant agents.
        shared_memory_list = deque(maxlen=len(participant_agents) - 1)

        input_object.add_data('total_round', total_round)
        input_object.add_data('participants', ' and '.join(participant_agents.keys()))

        # get the host agent memory.
        host_agent_memory: Memory = self.process_memory(agent_input)

        for i in range(total_round):
            LOGGER.info("------------------------------------------------------------------")
            LOGGER.info(f"Start a discussion, round is {i + 1}.")
            for participant_agent_name, participant_agent in participant_agents.items():
                LOGGER.info("------------------------------------------------------------------")
                LOGGER.info(f"Start speaking: agent is {participant_agent_name}.")
                LOGGER.info("------------------------------------------------------------------")

                # invoke participant agent
                input_object.add_data('chat_history', shared_memory_list)
                input_object.add_data('agent_name', participant_agent_name)
                input_object.add_data('cur_round', i + 1)
                output_object: OutputObject = participant_agent.run(**input_object.to_dict())

                # get the string output.
                current_output = output_object.get_data('output', '')

                # add the memory to the host agent memory instance.
                memory_content = (
                    f"the round {i + 1} participant agent in discussion group is: {participant_agent_name}, "
                    f"Human: {agent_input.get('input')}, AI: {current_output}")
                # append the current memory to the shared memory list.
                shared_memory_list = assemble_memory_output(host_agent_memory,
                                                            agent_input,
                                                            memory_content,
                                                            participant_agent_name,
                                                            shared_memory_list)

                # add to the stream queue.
                stream_output(input_object.get_data('output_stream'), {"data": {
                    'output': current_output,
                    "agent_info": self.agent_model.info
                }, "type": "participant_agent"})

                LOGGER.info(
                    f"the round {i + 1} agent {participant_agent_name} thought: {output_object.get_data('output', '')}")

        # concatenate the agent input parameters of the host agent.
        agent_input['total_round'] = total_round
        agent_input['participants'] = ' and '.join(participant_agents.keys())

        # finally invoke host agent
        return self.host_agent_run(agent_input, input_object)

    def host_agent_run(self, agent_input: dict, input_object: InputObject) -> dict:
        """ Invoke the host agent.

        Args:
            agent_input (dict): Agent input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The agent result.
        """
        LOGGER.info("------------------------------------------------------------------")
        LOGGER.info(f"Discussion end.")
        LOGGER.info(f"Host agent starts summarize the discussion.")
        LOGGER.info("------------------------------------------------------------------")
        memory: Memory = self.process_memory(agent_input)

        llm: LLM = self.process_llm()

        prompt: ChatPrompt = self.process_prompt(agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)

        assemble_memory_input(memory, agent_input)

        chain = prompt.as_langchain() | llm.as_langchain_runnable(self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object)

        content = (f"human: {agent_input.get('input')}, "
                   f"ai: after several rounds of discussions among the participants, "
                   f"the host in the discussion group came to the conclusion:{res}")

        assemble_memory_output(memory, agent_input, content, '')

        LOGGER.info(f"Discussion summary is: {res}")
        return {**agent_input, 'output': res}

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'DiscussionGroupTemplate':
        super().initialize_by_component_configer(component_configer)
        if self.agent_model.profile.get('topic'):
            self.topic = self.agent_model.profile.get('topic')
        if self.agent_model.profile.get('participant_names'):
            self.participant_names = self.agent_model.profile.get('participant_names')
        if self.agent_model.profile.get('total_round'):
            self.total_round = self.agent_model.profile.get('total_round')
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'discussion_group_agent.cn')
        return self
