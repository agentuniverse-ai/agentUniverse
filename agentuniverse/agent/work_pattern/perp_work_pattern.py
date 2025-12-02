# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/18 12:58
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: perp_work_pattern.py
import json
from typing import List, Dict, Any, Optional

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.dynamic_planning_agent_template import DynamicPlanningAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern
from agentuniverse.base.util.logging.logging_util import LOGGER


class PlanExecuteRePlanWorkPattern(WorkPattern):
    planner: DynamicPlanningAgentTemplate = None
    agents: List[AgentTemplate] = None
    tools: Optional[List[Tool]] = None

    # runtime init
    executor_map: Optional[Dict[str, Any]] = None
    tool_map: Optional[Dict[str, Tool]] = None
    agent_map: Optional[Dict[str, AgentTemplate]] = None
    executor_text: str = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Execute PERP work pattern synchronously"""
        self._validate_work_pattern_members()
        self._init_executors_from_tool_and_agent()
        max_execute_tasks = work_pattern_input.get('max_execute_tasks')
        return self._execute_perp(input_object, max_execute_tasks)

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Execute PERP work pattern asynchronously"""
        self._validate_work_pattern_members()
        self._init_executors_from_tool_and_agent()
        max_execute_tasks = work_pattern_input.get('max_execute_tasks')
        return await self._async_execute_perp(input_object, max_execute_tasks)

    def _execute_perp(self, input_object: InputObject, max_execute_tasks: int) -> dict:
        """Common logic for executing PERP main loop

        Args:
            input_object: Input object
            max_execute_tasks: Maximum number of tasks to execute

        Returns:
            Execution result
        """
        perp_results = list()

        # Initial planning - generate structured plan
        planning_result = self._invoke_planning(input_object, perp_results)
        perp_results.append({"planning_result": planning_result})
        # Check if there's a final answer (direct answer case)
        if planning_result.get('final_answer'):
            final_result = {
                'type': 'direct_answer',
                'final_answer': planning_result.get('final_answer'),
                'thought': planning_result.get('thought', '')
            }
            return {'result': perp_results, 'final_output': final_result}

        # Get task list
        tasks = planning_result.get('plan', [])
        if not tasks or not isinstance(tasks, list):
            # Planning failed, but you can retry with the output
            return self._no_answer(perp_results,
                                   default_msg=f"Can't get the initial plan. The planning result is: {planning_result}")

        # Loop with: plan -> execute -> re_plan
        return self._execute_loop_iterations(input_object, tasks, max_execute_tasks, perp_results)

    async def _async_execute_perp(self, input_object: InputObject, max_execute_tasks: int) -> dict:
        """Common logic for executing PERP main loop

        Args:
            input_object: Input object
            max_execute_tasks: Maximum number of tasks to execute

        Returns:
            Execution result
        """
        perp_results = list()

        # Initial planning - generate structured plan
        planning_result = await self._async_invoke_planning(input_object, perp_results)
        perp_results.append({"planning_result": planning_result})
        # Check if there's a final answer (direct answer case)
        if planning_result.get('final_answer'):
            final_result = {
                'type': 'direct_answer',
                'final_answer': planning_result.get('final_answer'),
                'thought': planning_result.get('thought', '')
            }
            return {'result': perp_results, 'final_output': final_result}

        # Get task list
        tasks = planning_result.get('plan', [])
        if not tasks or not isinstance(tasks, list):
            # Planning failed, but you can retry with the output
            return self._no_answer(perp_results,
                                   default_msg=f"Can't get the initial plan. The planning result is: {planning_result}")

        # Loop with: plan -> execute -> re_plan
        return await self._async_execute_loop_iterations(input_object, tasks, max_execute_tasks, perp_results)

    def _execute_loop_iterations(self, input_object: InputObject, tasks: list, max_execute_tasks: int,
                                 perp_results: list) -> dict:
        """Common logic for executing loop iterations

        Args:
            input_object: Input object
            tasks: Task list
            max_execute_tasks: Maximum number of tasks to execute
            perp_results: Results list

        Returns:
            Execution result
        """
        current_task_index = 0
        execution_results = []
        completed_task_ids = set()
        all_task_finished = False

        while True:
            perp_round_results = {}
            max_task_exceed = len(execution_results) >= max_execute_tasks
            if max_task_exceed:
                perp_results.append({"information": "The executed tasks is too much, please give the answer directly!"})
            if all_task_finished or len(tasks) <= 0:
                perp_results.append({"information": "All tasks are completed!"})
            else:
                # Execute current task
                current_task = tasks[current_task_index] if current_task_index < len(tasks) else None
                if not current_task:
                    all_task_finished = True
                    continue
                tool_name = current_task.get('tool')
                tool_detail = current_task.get('question', '').strip()
                task_id = f"Tool:{tool_name}, with parameters: {tool_detail}"

                # Skip completed tasks
                if task_id in completed_task_ids:
                    current_task_index += 1
                    continue

                perp_round_results['current_task'] = current_task
                executor_result = self._invoke_executor(input_object, tool_name, current_task)
                execution_results.append(executor_result)
                completed_task_ids.add(task_id)

                perp_round_results['task_result'] = executor_result
                perp_round_results['completed_tasks'] = set(completed_task_ids)
                perp_results.append({"executing_result": perp_round_results})

            # Re-planning: decide next step based on current execution results
            re_planning_result = self._invoke_planning(input_object, perp_results)
            perp_results.append({"planning_result": re_planning_result})

            # Check if there's a final answer
            if re_planning_result.get('final_answer'):
                final_result = {
                    'type': 'planning_answer',
                    'final_answer': re_planning_result.get('final_answer'),
                    'thought': re_planning_result.get('thought', '')
                }
                return {'result': perp_results, 'final_output': final_result}

            if max_task_exceed:
                return self._no_answer(perp_results,
                                       default_msg=f"Exceed the max tasks and not get the answer. The finial output is: {re_planning_result}")

            # Check if all tasks are completed
            new_tasks = re_planning_result.get('plan', [])
            if not isinstance(new_tasks, list):
                new_tasks = []
            new_task_ids = self._get_task_ids(new_tasks)
            old_task_ids = self._get_task_ids(tasks)
            if self._is_tasks_complete(new_task_ids, completed_task_ids):
                all_task_finished = True
            else:
                all_task_finished = False

            # Update task list and index
            if new_task_ids != old_task_ids:  # If task list changes
                tasks = new_tasks
                current_task_index = 0
            else:  # Otherwise continue to next task
                current_task_index += 1

    async def _async_execute_loop_iterations(self, input_object: InputObject, tasks: list, max_execute_tasks: int,
                                             perp_results: list) -> dict:
        """Common logic for executing loop iterations

        Args:
            input_object: Input object
            tasks: Task list
            max_execute_tasks: Maximum number of tasks to execute
            perp_results: Results list

        Returns:
            Execution result
        """
        current_task_index = 0
        execution_results = []
        completed_task_ids = set()
        all_task_finished = False

        while True:
            perp_round_results = {}
            max_task_exceed = len(execution_results) >= max_execute_tasks
            if max_task_exceed:
                perp_results.append({"information": "The executed tasks is too much, please give the answer directly!"})
            if all_task_finished or len(tasks) <= 0:
                perp_results.append({"information": "All tasks are completed!"})
            else:
                # Execute current task
                current_task = tasks[current_task_index] if current_task_index < len(tasks) else None
                if not current_task:
                    all_task_finished = True
                    continue
                tool_name = current_task.get('tool')
                tool_detail = current_task.get('question', '').strip()
                task_id = f"Tool:{tool_name}, with parameters: {tool_detail}"

                # Skip completed tasks
                if task_id in completed_task_ids:
                    current_task_index += 1
                    continue

                perp_round_results['current_task'] = current_task
                executor_result = await self._async_invoke_executor(input_object, tool_name, current_task)
                execution_results.append(executor_result)
                completed_task_ids.add(task_id)

                perp_round_results['task_result'] = executor_result
                perp_round_results['completed_tasks'] = set(completed_task_ids)
                perp_results.append({"executing_result": perp_round_results})

            # Re-planning: decide next step based on current execution results
            re_planning_result = await self._async_invoke_planning(input_object, perp_results)
            perp_results.append({"planning_result": re_planning_result})

            # Check if there's a final answer
            if re_planning_result.get('final_answer'):
                final_result = {
                    'type': 'planning_answer',
                    'final_answer': re_planning_result.get('final_answer'),
                    'thought': re_planning_result.get('thought', '')
                }
                return {'result': perp_results, 'final_output': final_result}

            if max_task_exceed:
                return self._no_answer(perp_results,
                                       default_msg=f"Exceed the max tasks and not get the answer. The finial output is: {re_planning_result}")

            # Check if all tasks are completed
            new_tasks = re_planning_result.get('plan', [])
            if not isinstance(new_tasks, list):
                new_tasks = []
            new_task_ids = self._get_task_ids(new_tasks)
            old_task_ids = self._get_task_ids(tasks)
            if self._is_tasks_complete(new_task_ids, completed_task_ids):
                all_task_finished = True
            else:
                all_task_finished = False

            # Update task list and index
            if new_task_ids != old_task_ids:  # If task list changes
                tasks = new_tasks
                current_task_index = 0
            else:  # Otherwise continue to next task
                current_task_index += 1

    def _invoke_planning(self, input_object: InputObject, perp_all_round_results: list) -> dict:
        input_object.add_data("executors", self.executor_text)
        input_object.add_data('perp_round_results', perp_all_round_results)
        planning_result = self.planner.run(**input_object.to_dict())
        return planning_result.to_dict()

    async def _async_invoke_planning(self, input_object: InputObject, perp_all_round_results: list) -> dict:
        input_object.add_data("executors", self.executor_text)
        input_object.add_data('perp_round_results', perp_all_round_results)
        planning_result = await self.planner.async_run(**input_object.to_dict())
        return planning_result.to_dict()

    def _invoke_agent(self, input_object: InputObject, tool_name: str) -> dict:
        """Select appropriate executor based on tool name - use agent_map to find, return error if not found

        Args:
            input_object: Input object
            tool_name: Tool/executor name

        Returns:
            Execution result
        """
        selected_agent = self.agent_map.get(tool_name)
        try:
            executing_result = selected_agent.run(**input_object.to_dict())
            return self._parse_agent_output(executing_result, selected_agent, tool_name)
        except Exception as e:
            return {
                'error': f"Tool '{tool_name}' execution error: {str(e)}",
                'tool_name': tool_name,
                'status': 'execution_error'
            }

    async def _async_invoke_agent(self, input_object: InputObject, tool_name: str) -> dict:
        """Select appropriate executor based on tool name - use agent_map to find, return error if not found

               Args:
                   input_object: Input object
                   tool_name: Tool/executor name

               Returns:
                   Execution result
               """
        selected_agent = self.agent_map.get(tool_name)
        try:
            executing_result = await selected_agent.async_run(**input_object.to_dict())
            return self._parse_agent_output(executing_result, selected_agent, tool_name)
        except Exception as e:
            return {
                'error': f"Tool '{tool_name}' execution error: {str(e)}",
                'tool_name': tool_name,
                'status': 'execution_error'
            }

    def _parse_agent_output(self, executing_result, selected_agent, tool_name):
        out_put_keys = selected_agent.output_keys()
        if out_put_keys:
            agent_out_put = {}
            for output_key in out_put_keys:
                agent_out_put[output_key] = executing_result.get_data(output_key, '')
            executing_result = OutputObject(agent_out_put)
        return {
            'tool_result': executing_result.to_dict(),
            'tool_name': tool_name,
            'status': 'success'
        }

    def _invoke_executor(self, input_object: InputObject, tool_name: str, task_data: dict = None) -> dict:
        """Encapsulate synchronous calls for executors and tools, intelligently determine whether it's a tool or executor

        Args:
            input_object: Input object
            tool_name: Tool/executor name
            task_data: Task data, including tool type and other information

        Returns:
            Execution result
        """
        # Use map to determine whether it's a tool or executor
        LOGGER.info(f"\nPERP executor start with name: {tool_name}...")
        is_tool_or_executor = self._is_tool_or_executor(tool_name)
        if is_tool_or_executor is None:
            # Both tool or executor not found, return error message
            error_result = OutputObject({
                'error': f"Tool '{tool_name}' not found in available tools",
                'available_tools': list(self.tool_map.keys()) + list(self.agent_map.keys()),
                'status': 'not_found'
            })
            return error_result.to_dict()
        tool_input_object = self._prepare_executor_input(input_object, task_data)
        if is_tool_or_executor:
            return self._invoke_tool(tool_input_object, tool_name)
        else:
            return self._invoke_agent(tool_input_object, tool_name)

    async def _async_invoke_executor(self, input_object: InputObject, tool_name: str,
                                     task_data: dict = None) -> dict:
        """Encapsulate synchronous calls for executors and tools, intelligently determine whether it's a tool or executor

               Args:
                   input_object: Input object
                   tool_name: Tool/executor name
                   task_data: Task data, including tool type and other information

               Returns:
                   Execution result
               """
        # Use map to determine whether it's a tool or executor
        LOGGER.info(f"\nPERP executor start with name: {tool_name}...")
        is_tool_or_executor = self._is_tool_or_executor(tool_name)
        tool_input_object = self._prepare_executor_input(input_object, task_data)
        if is_tool_or_executor is None:
            # Both tool or executor not found, return error message
            error_result = OutputObject({
                'error': f"Tool '{tool_name}' not found in available tools",
                'available_tools': list(self.tool_map.keys()) + list(self.agent_map.keys()),
                'status': 'not_found'
            })
            return error_result.to_dict()
        elif is_tool_or_executor:
            return await self._async_invoke_tool(tool_input_object, tool_name)
        else:
            return await self._async_invoke_agent(tool_input_object, tool_name)

    def _invoke_tool(self, input_object: InputObject, tool_name: str) -> dict:
        """Method to call tool - directly use agent_template's invoke_tools

        Args:
            input_object: Tool input parameters
            tool_name: Tool name

        Returns:
            Tool execution result
        """
        try:
            # Get actual tool object from tool_map
            tool_obj = self.tool_map.get(tool_name)
            tool_input = {key: input_object.get_data(key) for key in tool_obj.input_keys}
            tool_result = tool_obj.run(**tool_input)
            result_obj = OutputObject({
                'tool_result': tool_result,
                'tool_name': tool_name,
                'status': 'success'
            })
            return result_obj.to_dict()

        except Exception as e:
            error_result = OutputObject({
                'error': str(e),
                'tool_name': tool_name,
                'status': 'error'
            })
            return error_result.to_dict()

    async def _async_invoke_tool(self, input_object: InputObject, tool_name: str) -> dict:
        """Asynchronously call tool method - directly use agent_template's async_invoke_tools

        Args:
            input_object: Tool input parameters
            tool_name: Tool name

        Returns:
            Tool execution result
        """
        try:
            # Get actual tool object from tool_map
            tool_obj = self.tool_map.get(tool_name)
            tool_input = {key: input_object.get_data(key) for key in tool_obj.input_keys}
            tool_result = await tool_obj.async_run(**tool_input)
            result_obj = OutputObject({
                'tool_result': tool_result,
                'tool_name': tool_name,
                'status': 'success'
            })
            return result_obj.to_dict()

        except Exception as e:
            error_result = OutputObject({
                'error': str(e),
                'tool_name': tool_name,
                'status': 'error'
            })
            return error_result.to_dict()

    def _validate_work_pattern_members(self):
        if self.planner and not isinstance(self.planner, DynamicPlanningAgentTemplate):
            raise ValueError(f"{self.planner} is not of the expected type DynamicPlanningAgentTemplate.")
        if not self.tools and not self.agents:
            raise ValueError("Both tools and agents are empty, at least one must be provided.")
        if self.agents:
            for i, agent in enumerate(self.agents):
                if not isinstance(agent, AgentTemplate):
                    raise ValueError(f"Agent {i} {agent} is not of the expected type ExecutingAgentTemplate.")
                agent_name = agent.agent_model.info.get('name', '')
                agent_description = agent.agent_model.info.get('description', '')
                if not agent_name or not agent_description:
                    raise ValueError(f"Agent {i} {agent} is missing name or description.")

    def _init_executors_from_tool_and_agent(self):
        executor_strings = []
        tool_map = {}
        agent_map = {}
        self.tools = self.tools or []
        self.agents = self.agents or []

        for tool in self.tools:
            args_schema = f"args: {str(tool.args)}" if hasattr(tool, 'args') else ""
            executor_strings.append(f"Tool name: {tool.name}, description: {tool.description} {args_schema}")
            tool_map[tool.name] = tool
        if self.agents:
            for agent in self.agents:
                agent_name = agent.agent_model.info.get('name')
                agent_description = agent.agent_model.info.get('description')
                executor_strings.append(f"Tool name: {agent_name}, description: {agent_description}")
                agent_map[agent_name] = agent
        self.tool_map = tool_map
        self.agent_map = agent_map
        # Merge two dictionaries, tool_map takes priority (in case of same name)
        self.executor_map = {**agent_map, **tool_map}
        self.executor_text = "\n".join(executor_strings)

    def set_by_agent_model(self, **kwargs):
        perp_work_pattern_instance = self.__class__()
        perp_work_pattern_instance.name = self.name
        perp_work_pattern_instance.description = self.description
        for key in ['planner', 'agents', 'tools']:
            if key in kwargs:
                setattr(perp_work_pattern_instance, key, kwargs[key])
        return perp_work_pattern_instance

    def _get_task_ids(self, tasks: list) -> set[str]:
        new_task_ids = set()
        for task in tasks:
            tool_name = task.get('tool')
            tool_detail = task.get('question', '').strip()
            task_id = f"Tool:{tool_name}, with parameters: {tool_detail}"
            new_task_ids.add(task_id)
        return new_task_ids

    def _no_answer(self, execute_results, default_msg='Sorry, I don\'t know the answer') -> dict:
        return {'result': execute_results, 'final_output': {
            'type': 'no_answer',
            'final_answer': default_msg
        }}

    def _is_tasks_complete(self, tasks: set, completed_task_ids: set) -> bool:
        """Determine whether structured tasks are all completed

        Args:
            tasks: Current task list
            completed_task_ids: Completed task ID set

        Returns:
            Whether all tasks are completed
        """
        if not tasks:
            return True
        return tasks.issubset(completed_task_ids)

    def _is_tool_or_executor(self, tool_name: str) -> bool | None:
        """Determine whether the given name is a tool or executor, use map for lookup

        Args:
            tool_name: Tool name

        Returns:
            Whether it's a tool (True for tool, False for executor, None for not found)
        """
        # Use tool_map to find first
        if tool_name in self.tool_map:
            return True

        # Use agent_map to find
        if tool_name in self.agent_map:
            return False

        # If not found in both maps, return None to indicate not found
        return None

    def _prepare_executor_input(self, input_object, task_data):
        copy_input_object = {**input_object.to_dict()}
        tool_input_object = InputObject(copy_input_object)
        tool_input = task_data.get('question', '')
        tool_input_object.add_data('question', tool_input)
        if tool_input.startswith('{') and tool_input.endswith('}'):
            try:
                tool_input = json.loads(tool_input)
                for key, value in tool_input.items():
                    tool_input_object.add_data(key, value)
            except:
                LOGGER.warn(f"Tool input is not a valid json format, tool_input: {tool_input}")
                pass
        return tool_input_object
