# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/9/15 16:20
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: peer_planner.py
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.agent_util import assemble_memory_output

default_sub_agents = {
    "planning": "PlanningAgent",
    "executing": "ExecutingAgent",
    "expressing": "ExpressingAgent",
    "reviewing": "ReviewingAgent",
}

default_jump_step = "expressing"

default_eval_threshold = 60

default_retry_count = 2


class PeerPlanner(Planner):
    """Peer planner class."""

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        planner_config = agent_model.plan.get("planner")
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
            if config_data == "":
                continue
            agents[config_key] = AgentManager().get_instance_obj(config_data if config_data else default_agent)
        return agents

    @staticmethod
    def build_expert_framework(planner_config: dict, input_object: InputObject):
        """Build expert framework for the given planner config object.

        Args:
            planner_config (dict): Planner config object.
            input_object (InputObject): Agent input object.
        """
        expert_framework = planner_config.get("expert_framework")
        if expert_framework:
            context = expert_framework.get("context")
            selector = expert_framework.get("selector")
            if selector:
                selector_result = ToolManager().get_instance_obj(selector).run(**input_object.to_dict())
                input_object.add_data("expert_framework", selector_result)
            elif context:
                input_object.add_data("expert_framework", context)

    def agents_run(
        self, agent_model: AgentModel, agents: dict, planner_config: dict, agent_input: dict, input_object: InputObject
    ) -> dict:
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

        loopResults = list()
        planning_result = dict()
        executing_result = dict()
        expressing_result = dict()
        reviewing_result = dict()

        retry_count = planner_config.get("retry_count", default_retry_count)
        jump_step = planner_config.get("jump_step", default_jump_step)
        eval_threshold = planner_config.get("eval_threshold", default_eval_threshold)

        self.build_expert_framework(planner_config, input_object)

        planningAgent: Agent = agents.get("planning")
        executingAgent: Agent = agents.get("executing")
        expressingAgent: Agent = agents.get("expressing")
        reviewingAgent: Agent = agents.get("reviewing")

        peer_memory: Memory = self.handle_memory(agent_model, agent_input)

        for _ in range(retry_count):
            LOGGER.info(f"Starting peer agents, retry_count is {_ + 1}.")
            if not planning_result or jump_step == "planning":
                planning_result = self.planning_agent_run(planningAgent, input_object, agent_input, peer_memory)

            if not executing_result or jump_step in ["planning", "executing"]:
                executing_result = self.executing_agent_run(executingAgent, input_object, agent_input, peer_memory)

            if not expressing_result or jump_step in ["planning", "executing", "expressing"]:
                expressing_result = self.expressing_agent_run(expressingAgent, input_object, agent_input, peer_memory)

            if not reviewing_result or jump_step in ["planning", "executing", "expressing", "reviewing"]:
                reviewing_result = self.reviewing_agent_run(reviewingAgent, input_object, agent_input, peer_memory)

            if not reviewing_result.to_dict() or (
                reviewing_result.get_data("score") and reviewing_result.get_data("score") >= eval_threshold
            ):
                loopResults.append(
                    {
                        "planning_result": planning_result,
                        "executing_result": executing_result,
                        "expressing_result": expressing_result,
                        "reviewing_result": reviewing_result,
                    }
                )
                result["result"] = loopResults
                return result
            else:
                loopResults.append(
                    {
                        "planning_result": planning_result,
                        "executing_result": executing_result,
                        "expressing_result": expressing_result,
                        "reviewing_result": reviewing_result,
                    }
                )
        result["result"] = loopResults
        return result

    def planning_agent_run(
        self, planning_agent: Agent, input_object: InputObject, agent_input: dict, peer_memory: Memory
    ) -> OutputObject:
        """Run the planning agent.

        Args:
            planning_agent (Agent): Planning agent object.
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): Agent input object.
            peer_memory (Memory): Memory of the peer agent.
        Returns:
            OutputObject: The planning agent result.
        """
        planning_agent_name = planning_agent.agent_model.info.get("name") if planning_agent else ""
        if not planning_agent:
            LOGGER.warn("no planning agent.")
            planning_result = OutputObject({"framework": [agent_input.get("input")]})
        else:
            LOGGER.info(f"Starting planning agent.")
            planning_result = planning_agent.run(**input_object.to_dict())

        input_object.add_data("planning_result", planning_result)
        # add planning agent log info
        logger_info = f"\nPlanning agent execution result is :\n"
        for index, one_framework in enumerate(planning_result.get_data("framework")):
            logger_info += f"[{index + 1}] {one_framework} \n"
        LOGGER.info(logger_info)
        # add planning agent intermediate steps
        if planning_agent:
            self.stream_output(
                input_object,
                {
                    "data": {
                        "output": planning_result.get_data("framework"),
                        "agent_info": planning_agent.agent_model.info,
                    },
                    "type": "planning",
                },
            )
            content = (
                f"The agent responsible for planning and breaking down the task"
                f" raised by users into several sub-tasks is: {planning_agent_name}, "
                f"Human: {agent_input.get(self.input_key)}, "
                f"AI: {planning_result.get_data('framework')}"
            )
            assemble_memory_output(peer_memory, agent_input, content, planning_agent_name)
        return planning_result

    def executing_agent_run(
        self, executing_agent: Agent, input_object: InputObject, agent_input: dict, peer_memory: Memory
    ) -> OutputObject:
        """Run the executing agent.

        Args:
            executing_agent (Agent): Executing agent object.
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): Agent input object.
            peer_memory (Memory): Memory of the peer agent.
        Returns:
            OutputObject: The executing agent result.
        """
        executing_agent_name = executing_agent.agent_model.info.get("name") if executing_agent else ""
        if not executing_agent:
            LOGGER.warn("no executing agent.")
            executing_result = OutputObject({})
        else:
            LOGGER.info(f"Starting executing agent.")
            executing_result = executing_agent.run(**input_object.to_dict())

        input_object.add_data("executing_result", executing_result)
        # add executing agent log info
        logger_info = f"\nExecuting agent execution result is :\n"
        if executing_result.get_data("executing_result"):
            for index, one_exec_res in enumerate(executing_result.get_data("executing_result")):
                one_exec_log_info = f"[{index + 1}] input: {one_exec_res['input']}\n"
                one_exec_log_info += f"[{index + 1}] output: {one_exec_res['output']}\n"
                logger_info += one_exec_log_info
        LOGGER.info(logger_info)
        # add executing agent intermediate steps
        if executing_agent:
            self.stream_output(
                input_object,
                {
                    "data": {
                        "output": executing_result.get_data("executing_result"),
                        "agent_info": executing_agent.agent_model.info,
                    },
                    "type": "executing",
                },
            )
            content = (
                f"The agent responsible for executing the specific subtask is: {executing_agent_name}, "
                f"Human: {agent_input.get(self.input_key)}, "
                f"AI: {executing_result.get_data('executing_result')}"
            )
            assemble_memory_output(peer_memory, agent_input, content, executing_agent_name)
        return executing_result

    def expressing_agent_run(
        self, expressing_agent: Agent, input_object: InputObject, agent_input: dict, peer_memory: Memory
    ) -> OutputObject:
        """Run the expressing agent.

        Args:
            expressing_agent (Agent): Expressing agent object.
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): Agent input object.
            peer_memory (Memory): Memory of the peer agent.
        Returns:
            OutputObject: The expressing agent result.
        """
        expressing_agent_name = expressing_agent.agent_model.info.get("name") if expressing_agent else ""
        if not expressing_agent:
            LOGGER.warn("no expressing agent.")
            expressing_result = OutputObject({})
        else:
            LOGGER.info(f"Starting expressing agent.")
            expressing_result = expressing_agent.run(**input_object.to_dict())

        input_object.add_data("expressing_result", expressing_result)
        # add expressing agent log info
        logger_info = f"\nExpressing agent execution result is :\n"
        logger_info += f"{expressing_result.get_data('output')}"
        LOGGER.info(logger_info)
        # add expressing agent intermediate steps
        if expressing_agent:
            self.stream_output(
                input_object,
                {
                    "data": {
                        "output": expressing_result.get_data("output"),
                        "agent_info": expressing_agent.agent_model.info,
                    },
                    "type": "expressing",
                },
            )
            content = (
                f"The agent responsible for expressing and integrating the task raised by user"
                f" into a final result based on the results of several sub-tasks is: {expressing_agent_name}, "
                f"Human: {agent_input.get(self.input_key)}, "
                f"AI: {expressing_result.get_data('output')}"
            )
            assemble_memory_output(peer_memory, agent_input, content, expressing_agent_name)

        return expressing_result

    def reviewing_agent_run(
        self, reviewing_agent: Agent, input_object: InputObject, agent_input: dict, peer_memory: Memory
    ) -> OutputObject:
        """Run the reviewing agent.

        Args:
            reviewing_agent (Agent): Reviewing agent object.
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): Agent input object.
            peer_memory (Memory): Memory of the peer agent.
        Returns:
            OutputObject: The reviewing agent result.
        """
        reviewing_agent_name = reviewing_agent.agent_model.info.get("name") if reviewing_agent else ""
        if not reviewing_agent:
            LOGGER.warn("no reviewing agent.")
            reviewing_result = OutputObject({})
        else:
            LOGGER.info(f"Starting reviewing agent.")
            reviewing_result = reviewing_agent.run(**input_object.to_dict())

        input_object.add_data("reviewing_result", reviewing_result)
        # add reviewing agent log info
        logger_info = f"\nReviewing agent execution result is :\n"
        reviewing_info_str = f"review suggestion: {reviewing_result.get_data('suggestion')} \n"
        reviewing_info_str += f"review score: {reviewing_result.get_data('score')} \n"
        LOGGER.info(logger_info + reviewing_info_str)

        # add reviewing agent intermediate steps
        if reviewing_agent:
            # add reviewing agent intermediate steps
            self.stream_output(
                input_object,
                {
                    "data": {
                        "output": reviewing_result.get_data("suggestion"),
                        "agent_info": reviewing_agent.agent_model.info,
                    },
                    "type": "reviewing",
                },
            )
            content = (
                f"The agent responsible for reviewing"
                f" and evaluating the result to the task raised by user is {reviewing_agent_name}, "
                f"Human: {agent_input.get(self.input_key)}, "
                f"AI: {reviewing_result.get_data('suggestion')}"
            )
            assemble_memory_output(peer_memory, agent_input, content, reviewing_agent_name)
        return reviewing_result
