#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/01 23:50
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: enhanced_executing_agent_template.py
import asyncio
import json
from typing import Optional, Dict, Any

from langchain_core.output_parsers import StrOutputParser
from agentuniverse.base.util.json_util import parse_json
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import ConversationMemoryModule
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class EnhancedExecutingAgentTemplate(AgentTemplate):
    _context_values: Optional[dict] = {}

    class Config:
        arbitrary_types_allowed = True

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['executing_result']

    def parse_input(self, input_object: InputObject,
                    agent_input: Dict[str, Any]) -> Dict[str, Any]:
        agent_input['input'] = input_object.get_data('input')
        agent_input['debate_history'] = input_object.get_data(
            'debate_history', [])
        agent_input['tool_call_history'] = []
        agent_input['framework'] = input_object.get_data(
            'planning_result').get_data('framework', [])
        agent_input['expert_framework'] = input_object.get_data(
            'expert_framework', {}).get('executing')
        return agent_input

    def customized_execute(self, input_object: InputObject, agent_input: dict,
                           memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        return self._execute_tasks(input_object, agent_input, memory, llm,
                                   prompt)

    async def customized_async_execute(self, input_object: InputObject,
                                       agent_input: dict, memory: Memory,
                                       llm: LLM, prompt: Prompt,
                                       **kwargs) -> dict:
        return await asyncio.get_running_loop().run_in_executor(
            None, self._execute_tasks, input_object, agent_input, memory, llm,
            prompt)

    def _execute_tasks(self, input_object: InputObject, agent_input: dict,
                       memory: Memory, llm: LLM, prompt: Prompt,
                       **kwargs) -> dict:
        self._context_values: dict = FrameworkContextManager(
        ).get_all_contexts()
        self._process_tool_inputs(agent_input)
        knowledge: str = self.invoke_knowledge(input_object.get_data("input"),
                                               input_object)
        input_object.add_data('background', knowledge)

        def __exe() -> Dict[str, Any]:
            context_tokens = {}
            FrameworkContextManager().set_all_contexts(
                kwargs.get('context_values', {}))
            try:
                process_llm_token(llm, prompt.as_langchain(),
                                  self.agent_model.profile, agent_input)
                chain = prompt.as_langchain() | llm.as_langchain_runnable(
                    self.agent_model.llm_params()) | StrOutputParser()
                res: str = self.invoke_chain(chain, agent_input, input_object)
                try:
                    return parse_json(res)
                except Exception as e:
                    LOGGER.error(f'Format resposne from {res} error: {e}')
                    return {}
            finally:
                for var_name, token in context_tokens.items():
                    FrameworkContextManager().reset_context(var_name, token)

        def __tool(tool_call: Dict[str, Any]) -> None:
            d = {"tool_names": tool_call.get("tool_name", "")}
            d.update(tool_call.get("params"))
            tool_res: str = self.invoke_tools(InputObject(d))
            tool_call.update({'result': tool_res if tool_res else 'success'})
            agent_input['tool_call_history'].append(tool_call)

        tool_call = __exe()
        while tool_call.get("tool_name", "") != "" and tool_call.get(
                "tool_name", "") not in ["finish", "end"]:
            __tool(tool_call)
            tool_call = __exe()

        return {
            'executing_result': memory,
            'output_stream': input_object.get_data('output_stream', None)
        }

    def parse_result(self, agent_result: dict) -> dict:
        stream_output(
            agent_result.pop('output_stream'), {
                "data": {
                    'output': agent_result.get('executing_result'),
                    "agent_info": self.agent_model.info
                },
                "type": "executing"
            })
        return agent_result

    def _process_tool_inputs(self, agent_input: Dict[str, Any]) -> None:
        agent_input.update({
            "available_tools":
            "\n".join(ToolManager().get_instance_obj(tool).prompt
                      for tool in self.tool_names)
        })

    def initialize_by_component_configer(
            self, component_configer: AgentConfiger
    ) -> 'EnhancedExecutingAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get(
            'prompt_version', 'default_executing_agent.cn')
        return self
