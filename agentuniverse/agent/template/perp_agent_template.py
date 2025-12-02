# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/19 15:48
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: perp_agent_template.py
from typing import List
from dataclasses import field

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.dynamic_planning_agent_template import DynamicPlanningAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class PerpAgentTemplate(AgentTemplate):
    planner_agent_name: str = "PlannerAgent"
    executor_agent_names: List[str] = field(default_factory=lambda: [])
    max_execute_tasks: int = 20

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input.update({'max_execute_tasks': self.max_execute_tasks})
        return agent_input

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        perp_work_pattern = WorkPatternManager().get_instance_obj('plan_execute_re_plan_work_pattern')
        perp_work_pattern = perp_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = self.customized_execute(input_object=input_object, agent_input=agent_input, memory=memory,
                                                      perp_work_pattern=perp_work_pattern)
        self.add_peer_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        perp_work_pattern = WorkPatternManager().get_instance_obj('plan_execute_re_plan_work_pattern')
        perp_work_pattern = perp_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = await self.customized_async_execute(input_object=input_object, agent_input=agent_input,
                                                                  memory=memory, perp_work_pattern=perp_work_pattern)
        self.add_peer_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                           perp_work_pattern, **kwargs) -> dict:
        work_pattern_result = perp_work_pattern.invoke(input_object, agent_input)
        return work_pattern_result

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                                       perp_work_pattern, **kwargs) -> dict:
        work_pattern_result = await perp_work_pattern.async_invoke(input_object, agent_input)
        return work_pattern_result

    def parse_result(self, agent_result: dict) -> dict:
        return {'output': agent_result.get('final_output', {}).get('final_answer', '')}

    def _generate_agents(self) -> dict:
        planner_agent = self._get_and_validate_agent(self.planner_agent_name, DynamicPlanningAgentTemplate)

        executor_agents = []
        for executing_agent_name in self.executor_agent_names:
            executing_agent = self._get_and_validate_agent(executing_agent_name, AgentTemplate)
            if executing_agent:
                executor_agents.append(executing_agent)
        executor_tools = []
        for tool_name in self.tool_names:
            tool = ToolManager().get_instance_obj(tool_name)
            if tool:
                executor_tools.append(tool)
        return {'planner': planner_agent,
                'agents': executor_agents,
                'tools': executor_tools}

    @staticmethod
    def _get_and_validate_agent(agent_name: str, expected_type: type):
        agent = AgentManager().get_instance_obj(agent_name)
        if not agent:
            return None
        if not isinstance(agent, expected_type):
            raise ValueError(f"{agent_name} is not of the expected type {expected_type.__name__}")
        return agent

    def add_peer_memory(self, peer_memory: Memory, agent_input: dict, work_pattern_result: dict):
        if not peer_memory:
            return
        query = agent_input.get('input')
        message_list = []

        def _create_message_content(round, role, agent_name, result):
            content = (f"PERP work pattern round {round + 1}: The agent responsible for {role} is: {agent_name} \n"
                       f"Human: {query} \nAI: {result}")
            return Message(source=agent_name, content=content)

        perp_results = work_pattern_result.get('result', [])
        final_output = work_pattern_result.get('final_output', {})

        for i, single_turn_res in enumerate(perp_results):
            # Process planning results
            planning_result = single_turn_res.get('planning_result', {})
            if planning_result:
                plan = planning_result.get('plan', [])
                if plan and isinstance(plan, list):
                    task_infos = []
                    for task in plan:
                        if isinstance(task, dict):
                            task_infos.append(f"Thought: {task.get('thought', '')} \n Description: {task.get('description', '')} \n Tool: {task.get('tool', '')} \n Tool input: {task.get('question', '')}")
                        else:
                            task_infos.append(str(task))
                    message_list.append(_create_message_content(i, "Planner", self.planner_agent_name, '\n'.join(task_infos)))
                else:
                    message_list.append(_create_message_content(i, "Planner", self.planner_agent_name, str(plan)))

            # Process executor results
            executing_result = single_turn_res.get('executing_result', {})
            if executing_result:
                current_task = executing_result.get('current_task', '')
                selected_executor = current_task.get('tool', 'Executor')
                task_output = single_turn_res.get('tool_result', '')
                message_list.append(
                    _create_message_content(i, 'Executor', selected_executor, f"Executing with task: {current_task}, the result is: {task_output}"))

            # Process information results
            information_result = single_turn_res.get('information', {})
            if information_result:
                message_list.append(
                    _create_message_content(i, 'Information', 'Information', f"Information result is: {information_result}"))

        # Add final output to memory
        if final_output:
            final_content = f"The final answer of the question is: {final_output.get('final_answer', '')}"
            message_list.append(Message(source="PERP", content=final_content))

        peer_memory.add(message_list, **agent_input)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'PerpAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        planner_config = self.agent_model.plan.get('planner', {})
        
        # Parse planner agent configuration
        if self.agent_model.profile.get('planner') is not None or planner_config.get('planner') is not None:
            self.planner_agent_name = self.agent_model.profile.get('planner') \
                if self.agent_model.profile.get('planner') is not None else planner_config.get('planner')
        
        # Parse executors configuration
        executor_config = self.agent_model.profile.get('executors') or planner_config.get('executors')
        if executor_config:
            if isinstance(executor_config, list):
                # If it's a list, use multiple executor names
                self.executor_agent_names = executor_config
            elif isinstance(executor_config, str):
                # If it's a string, convert to single-element list
                self.executor_agent_names = [executor_config]
            else:
                # Keep default value
                self.executor_agent_names = []

        # Parse other configuration parameters
        self.memory_name = self.agent_model.memory.get('name')
        if self.agent_model.profile.get('max_execute_tasks') or planner_config.get('max_execute_tasks'):
            self.max_execute_tasks = self.agent_model.profile.get('max_execute_tasks') or planner_config.get('max_execute_tasks')
        return self
