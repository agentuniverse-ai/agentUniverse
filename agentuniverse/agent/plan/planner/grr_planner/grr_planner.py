# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2/17/25
# @Author  : quesheng
# @Email   : huiyi.why@antgroup.com

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.agent_util import assemble_memory_output
from agentuniverse.base.util.logging.logging_util import LOGGER

default_sub_agents = {
    'rag': 'RagAgent',
    'reviewing': 'ReviewingAgent',
    'rewriting': 'RewritingAgent'
}

class GrrPlanner(Planner):
    """Grr planner class."""

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        planner_config = agent_model.plan.get('planner')
        sub_agents = self.generate_sub_agents(planner_config)
        return self.agents_run(agent_model, sub_agents, planner_config, planner_input, input_object)

    @staticmethod
    def generate_sub_agents(planner_config: dict) -> dict:
        """Generate sub agents.

        Args:
            planner_config (dict): Planner config object.
        Returns:
            dict: Planner agents.
        """
        agents = dict()
        for config_key, default_agent in default_sub_agents.items():
            config_data = planner_config.get(config_key, None)
            if config_data == '':
                continue
            agents[config_key] = AgentManager().get_instance_obj(config_data if config_data else default_agent)
        return agents

    def agents_run(self, agent_model: AgentModel, agents: dict, planner_config: dict, agent_input: dict,
                   input_object: InputObject) -> dict:
        """Planner agents run.

        Args:
            agent_model (AgentModel): Agent model object.
            agents (dict): Planner agents.
            planner_config (dict): Planner config object.
            agent_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        Returns:
            dict: The planner result.
        """
        result: dict = dict()

        ragAgent: Agent = agents.get('rag')
        reviewingAgent: Agent = agents.get('reviewing')
        rewritingAgent: Agent = agents.get('rewriting')

        grr_memory: Memory = self.handle_memory(agent_model, agent_input)

        rag_result = self.rag_agent_run(ragAgent, input_object, agent_input, grr_memory)
        reviewing_result = self.reviewing_agent_run(reviewingAgent, input_object, agent_input, grr_memory)
        rewriting_result = self.rewriting_agent_run(rewritingAgent, input_object, agent_input, grr_memory)

        result['result'] = {
            "rag_result": rag_result,
            "reviewing_result": reviewing_result,
            "rewriting_result": rewriting_result
        }
        return result

    def rag_agent_run(self, rag_agent: Agent, input_object: InputObject,
                           agent_input: dict, grr_memory: Memory) -> OutputObject:
        """Run the rag agent.

        Args:
            rag_agent (Agent): rag_agent agent object.
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): Agent input object.
            grr_memory (Memory): Memory of the grr agent.
        Returns:
            OutputObject: The planning agent result.
        """
        rag_agent_name = rag_agent.agent_model.info.get('name') if rag_agent else ''
        if not rag_agent:
            LOGGER.warn("no rag agent.")
            rag_result = OutputObject({"framework": [agent_input.get('input')]})
        else:
            LOGGER.info(f"Starting rag agent.")
            rag_result = rag_agent.run(**input_object.to_dict())

        input_object.add_data('rag_result', rag_result)
        # add rag agent log info
        logger_info = f"\nrag agent execution result is :\n"
        logger_info += f"{rag_result.get_data('output')}"

        if rag_agent:
            self.stream_output(input_object, {"data": {
                'output': rag_result.get_data('output'),
                "agent_info": rag_agent.agent_model.info
            }, "type": "rag"})
            content = (f"The agent responsible for rag is {rag_agent_name},"
                       f"Human: {agent_input.get(self.input_key)}, "
                       f"AI: {rag_result.get_data('output')}")
            assemble_memory_output(grr_memory, agent_input, content, rag_agent_name)
        return rag_result

    def reviewing_agent_run(self, reviewing_agent: Agent,
                            input_object: InputObject, agent_input: dict, grr_memory: Memory) -> OutputObject:
        """Run the reviewing agent.

        Args:
            reviewing_agent (Agent): Reviewing agent object.
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): Agent input object.
            grr_memory (Memory): Memory of the peer agent.
        Returns:
            OutputObject: The reviewing agent result.
        """
        reviewing_agent_name = reviewing_agent.agent_model.info.get('name') if reviewing_agent else ''
        if not reviewing_agent:
            LOGGER.warn("no reviewing agent.")
            reviewing_result = OutputObject({})
        else:
            LOGGER.info(f"Starting reviewing agent.")
            reviewing_result = reviewing_agent.run(**input_object.to_dict())

        input_object.add_data('reviewing_result', reviewing_result)
        # add reviewing agent log info
        logger_info = f"\nReviewing agent execution result is :\n"
        reviewing_info_str = f"review suggestion: {reviewing_result.get_data('suggestion')} \n"
        reviewing_info_str += f"review score: {reviewing_result.get_data('score')} \n"
        LOGGER.info(logger_info + reviewing_info_str)

        # add reviewing agent intermediate steps
        if reviewing_agent:
            # add reviewing agent intermediate steps
            self.stream_output(input_object,
                               {"data": {
                                   'output': reviewing_result.get_data('suggestion'),
                                   "agent_info": reviewing_agent.agent_model.info
                               }, "type": "reviewing"})
            content = (
                f"The agent responsible for reviewing"
                f" and evaluating the result to the task raised by user is {reviewing_agent_name}, "
                f"Human: {agent_input.get(self.input_key)}, "
                f"AI: {reviewing_result.get_data('suggestion')}")
            assemble_memory_output(grr_memory, agent_input, content, reviewing_agent_name)
        return reviewing_result

    def rewriting_agent_run(self, rewriting_agent: Agent,
                            input_object: InputObject, agent_input: dict, grr_memory: Memory) -> OutputObject:
        """Run the rewriting agent.

        Args:
            rewriting_agent (Agent): Reviewing agent object.
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): Agent input object.
            grr_memory (Memory): Memory of the peer agent.
        Returns:
            OutputObject: The reviewing agent result.
        """
        rewriting_agent_name = rewriting_agent.agent_model.info.get('name') if rewriting_agent else ''
        if not rewriting_agent:
            LOGGER.warn("no rewriting agent.")
            rewriting_result = OutputObject({})
        else:
            LOGGER.info(f"Starting rewriting agent.")
            rewriting_result = rewriting_agent.run(**input_object.to_dict())

        input_object.add_data('rewriting_result', rewriting_result)
        # add rewriting agent log info
        logger_info = f"\nRewriting agent execution result is :\n"
        logger_info += f"{rewriting_result.get_data('output')}"
        LOGGER.info(logger_info)

        # add rewriting agent intermediate steps
        if rewriting_agent:
            # add rewriting agent intermediate steps
            self.stream_output(input_object,
                               {"data": {
                                   'output': rewriting_result.get_data('output'),
                                   "agent_info": rewriting_agent.agent_model.info
                               }, "type": "reviewing"})
            content = (
                f"The agent responsible for rewriting is {rewriting_agent_name}, "
                f"Human: {agent_input.get(self.input_key)}, "
                f"AI: {rewriting_result.get_data('output')}")
            assemble_memory_output(grr_memory, agent_input, content, rewriting_agent_name)
        return rewriting_result