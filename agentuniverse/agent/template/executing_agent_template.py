# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/17 16:54
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: executing_agent_template.py
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Optional

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import ConversationMemoryModule
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.ai_context.agent_context import AgentContext
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM


class ExecutingAgentTemplate(AgentTemplate):
    _context_values: Optional[dict] = {}

    class Config:
        arbitrary_types_allowed = True

    def input_keys(self) -> list[str]:
        return ['input', 'planning_result']

    def output_keys(self) -> list[str]:
        return ['executing_result']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['framework'] = input_object.get_data('planning_result').get_data('framework')
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('executing')
        return agent_input

    def customized_execute(self, input_object: InputObject, agent_input: dict,
                           memory: Memory, llm: LLM,
                           agent_context: AgentContext = None,
                           **kwargs) -> dict:
        return self._execute_tasks(input_object, agent_input, memory, llm, agent_context)

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict,
                                       memory: Memory, llm: LLM,
                                       agent_context: AgentContext = None,
                                       **kwargs) -> dict:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._execute_tasks, input_object, agent_input,
                                          memory, llm, agent_context)

    def _execute_tasks(self, input_object: InputObject, agent_input: dict,
                       memory: Memory, llm: LLM,
                       agent_context: AgentContext = None,
                       **kwargs) -> dict:
        self._context_values: dict = FrameworkContextManager().get_all_contexts()
        _context_values: dict = FrameworkContextManager().get_all_contexts()
        framework = agent_input.get('framework', [])

        if len(framework) == 0:
            return {'executing_result': [],
                    'output_stream': input_object.get_data('output_stream', None)}

        with ThreadPoolExecutor(max_workers=min(len(framework), 10),
                                thread_name_prefix="executing_agent_template") as thread_executor:
            futures = []
            for i, subtask in enumerate(framework):
                future = thread_executor.submit(self._execute_subtask, subtask, input_object,
                                                agent_input, i, memory, llm, agent_context,
                                                context_values=_context_values)
                futures.append(future)
                time.sleep(1)

            executing_result = [future.result() for future in as_completed(futures)]

        executing_result.sort(key=lambda x: x['index'])
        return {'executing_result': [result for result in executing_result],
                'output_stream': input_object.get_data('output_stream', None)}

    def _execute_subtask(self, subtask, input_object, agent_input, index,
                         memory, llm, agent_context, **kwargs) -> dict:
        context_tokens = {}
        FrameworkContextManager().set_all_contexts(kwargs.get('context_values', {}))
        try:
            pair_id = uuid.uuid4().hex
            ConversationMemoryModule().add_agent_input_info(
                start_info=input_object.get_data('memory_source_info'),
                instance=self,
                params={'input': agent_input.get('framework')[index]},
                pair_id=pair_id,
                auto=False
            )
            input_object_copy = InputObject(input_object.to_dict())
            agent_input_copy = dict(agent_input)

            self._process_tool_inputs(input_object_copy, subtask)

            knowledge_res = self.invoke_knowledge(subtask, input_object_copy)
            tools_res = self.invoke_tools(input_object_copy)
            agent_input_copy['background'] = f"knowledge result: {knowledge_res} \n\n tools result: {tools_res}"
            agent_input_copy['input'] = subtask

            # Build a per-subtask AgentContext and invoke LLM
            sub_context = self._create_agent_context(input_object_copy, agent_input_copy, memory)
            sub_llm = sub_context.build_llm()
            messages = sub_context.build_messages()
            llm_output = self.invoke_llm(sub_llm, messages, input_object_copy, agent_context=sub_context)
            res = llm_output.text

            self._save_memory(sub_context, llm_output, agent_input)
            ConversationMemoryModule().add_agent_result_info(
                agent_instance=self,
                agent_result={'output': res},
                target_info=input_object.get_data('memory_source_info'),
                pair_id=pair_id,
                auto=False
            )
            return {
                'index': index,
                'input': f"Question {index + 1}: {subtask}",
                'output': f"Answer {index + 1}: {res}"
            }
        finally:
            for var_name, token in context_tokens.items():
                FrameworkContextManager().reset_context(var_name, token)

    def parse_result(self, agent_result: dict) -> dict:
        stream_output(agent_result.pop('output_stream'),
                      {"data": {
                          'output': agent_result.get('executing_result'),
                          "agent_info": self.agent_model.info
                      }, "type": "executing"})

        logger_info = f"\nExecuting agent execution result is :\n"
        if agent_result.get('executing_result'):
            for index, one_exec_res in enumerate(agent_result.get('executing_result')):
                one_exec_log_info = f"[{index + 1}] input: {one_exec_res['input']}\n"
                one_exec_log_info += f"[{index + 1}] output: {one_exec_res['output']}\n"
                logger_info += one_exec_log_info
        LOGGER.info(logger_info)

        return agent_result

    def _process_tool_inputs(self, input_object: InputObject, subtask: str) -> None:
        if not self.tool_names:
            return
        for tool_name in self.tool_names:
            tool = ToolManager().get_instance_obj(tool_name)
            if tool is not None:
                input_object.add_data(tool.input_keys[0], subtask)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ExecutingAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_executing_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')
