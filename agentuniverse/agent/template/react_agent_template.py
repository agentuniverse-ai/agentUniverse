# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/25 15:06
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: react_agent_template.py
from typing import Sequence, Optional, Union, List

from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents import AgentExecutor, AgentOutputParser
from langchain.tools import Tool as LangchainTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.runnables import RunnableConfig, RunnablePassthrough, Runnable
from langchain_core.tools import BaseTool, ToolsRenderer, render_text_description
from datetime import datetime
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.plan.planner.react_planner.stream_callback import StreamOutPutCallbackHandler, \
    InvokeCallbackHandler
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class ReActAgentTemplate(AgentTemplate):
    agent_names: Optional[list[str]] = None
    stop_sequence: Optional[list[str]] = None
    max_iterations: Optional[int] = None

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        tools_context = self.build_tools_context()
        agent_input['tools'] = tools_context[0]
        agent_input['tool_names'] = tools_context[1]
        agent_input['agent_scratchpad'] = ''
        current_time = datetime.now()
        current_time_formatted = current_time.strftime("%Y-%m-%d %H:%M:%S")
        agent_input['current_time'] = current_time_formatted
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        self.load_memory(memory, agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        lc_tools: List[LangchainTool] = self._convert_to_langchain_tool()
        agent = self.create_react_agent(llm.as_langchain(), lc_tools, prompt.as_langchain(),
                                        stop_sequence=self.stop_sequence,
                                        bind_params=self.agent_model.llm_params())
        # Set stream_runnable based on LLM's streaming capability to avoid errors with non-streaming LLMs
        stream_runnable = getattr(llm, 'streaming', False) if llm else False
        agent_executor = AgentExecutor(agent=agent, tools=lc_tools,
                                       verbose=True,
                                       handle_parsing_errors=True,
                                       max_iterations=self.max_iterations,
                                       stream_runnable=stream_runnable)
        res = agent_executor.invoke(input=agent_input, memory=memory.as_langchain() if memory else None,
                                    chat_history=agent_input.get(memory.memory_key) if memory else '',
                                    config=self._get_run_config(input_object))
        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res.get('output')}")
        return res

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                                       llm: LLM, prompt: Prompt, **kwargs) -> dict:
        self.load_memory(memory, agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        lc_tools: List[LangchainTool] = await self._async_convert_to_langchain_tool()
        agent = self.create_react_agent(llm.as_langchain(), lc_tools, prompt.as_langchain(),
                                        stop_sequence=self.stop_sequence,
                                        bind_params=self.agent_model.llm_params())
        # Set stream_runnable based on LLM's streaming capability to avoid errors with non-streaming LLMs
        stream_runnable = getattr(llm, 'streaming', False) if llm else False
        agent_executor = AgentExecutor(agent=agent, tools=lc_tools,
                                       verbose=True,
                                       handle_parsing_errors=True,
                                       max_iterations=self.max_iterations,
                                       stream_runnable=stream_runnable)
        res = await agent_executor.ainvoke(input=agent_input, memory=memory.as_langchain() if memory else None,
                                           chat_history=agent_input.get(memory.memory_key) if memory else '',
                                           config=self._get_run_config(input_object))
        self.add_memory(memory, content=f"Human: {agent_input.get('input')}, AI: {res.get('output')}",
                        agent_input=agent_input)
        return res

    def create_react_agent(
            self,
            llm: BaseLanguageModel,
            tools: Sequence[BaseTool],
            prompt: BasePromptTemplate,
            output_parser: Optional[AgentOutputParser] = None,
            tools_renderer: ToolsRenderer = render_text_description,
            *,
            stop_sequence: Union[bool, List[str]] = True,
            bind_params: Optional[dict],
    ) -> Runnable:
        missing_vars = {"tools", "tool_names", "agent_scratchpad"}.difference(
            prompt.input_variables + list(prompt.partial_variables)
        )
        if missing_vars:
            raise ValueError(f"Prompt missing required variables: {missing_vars}")

        prompt = prompt.partial(
            tools=tools_renderer(list(tools)),
            tool_names=", ".join([t.name for t in tools]),
        )
        if stop_sequence:
            stop = ["\nObservation"] if stop_sequence is True else stop_sequence
            llm_with_stop = llm.bind(stop=stop, **(bind_params or {}))
        else:
            llm_with_stop = llm.bind(**(bind_params or {}))
        output_parser = output_parser or ReActSingleInputOutputParser()
        agent = (
                RunnablePassthrough.assign(
                    agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
                )
                | prompt
                | llm_with_stop
                | output_parser
        )
        return agent

    def build_tools_context(self) -> tuple[str, str]:
        lc_tools: [LangchainTool] = self._convert_to_langchain_tool()
        tools_context = ''
        if not lc_tools:
            return '', ''
        tool_names = []
        for lc_tool in lc_tools:
            tools_context += f"tool name: {lc_tool.name}, tool description: {lc_tool.description}\n"
            tool_names.append(lc_tool.name)
        return tools_context, "|".join(tool_names)

    def _convert_to_langchain_tool(self) -> list[LangchainTool]:
        lc_tools = []
        if self.tool_names:
            for tool_name in self.tool_names:
                tool: Tool = ToolManager().get_instance_obj(tool_name)
                lc_tools.append(tool.as_langchain())
        if self.knowledge_names:
            for knowledge_name in self.knowledge_names:
                knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_name)
                lc_tools.append(knowledge.as_langchain_tool())
        if self.agent_names:
            for agent_name in self.agent_names:
                agent: Agent = AgentManager().get_instance_obj(agent_name)
                lc_tools.append(agent.as_langchain_tool())
        return lc_tools

    async def _async_convert_to_langchain_tool(self) -> list[LangchainTool]:
        lc_tools = []
        if self.tool_names:
            for tool_name in self.tool_names:
                tool: Tool = ToolManager().get_instance_obj(tool_name)
                lc_tools.append(await tool.async_as_langchain())
        if self.knowledge_names:
            for knowledge_name in self.knowledge_names:
                knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_name)
                lc_tools.append(await knowledge.async_as_langchain_tool())
        if self.agent_names:
            for agent_name in self.agent_names:
                agent: Agent = AgentManager().get_instance_obj(agent_name)
                lc_tools.append(await agent.async_as_langchain_tool())
        return lc_tools

    def _get_run_config(self, input_object: InputObject) -> RunnableConfig:
        config = RunnableConfig()
        callbacks = []
        output_stream = input_object.get_data('output_stream')
        callbacks.append(StreamOutPutCallbackHandler(output_stream, agent_info=self.agent_model.info))
        callbacks.append(InvokeCallbackHandler(source=self.agent_model.info.get('name'),
                                               llm_name=self.agent_model.profile.get('llm_model').get('name')))
        config.setdefault("callbacks", callbacks)
        return config

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ReActAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_react_agent.cn')
        self.stop_sequence = self.agent_model.profile.get('stop_sequence')
        self.max_iterations = self.agent_model.profile.get('max_iterations', 10)
        self.agent_names = self.agent_model.action.get('agent', [])
        return self
