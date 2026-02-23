# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/24 21:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: rag_agent_template.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.ai_context.agent_context import AgentContext
from agentuniverse.base.config.component_configer.configers.agent_configer import \
    AgentConfiger
from agentuniverse.llm.llm import LLM


class RagAgentTemplate(AgentTemplate):
    """RAG agent template.

    After the tool-calling loop completes, extracts knowledge tool results
    from the conversation messages and populates the ``background`` field
    in the output so callers can inspect the retrieved content.
    """

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    @staticmethod
    def _extract_tool_background(context: AgentContext) -> str:
        """Collect content from all tool result messages in current_messages."""
        parts = []
        for msg in context.current_messages:
            if msg.type == ChatMessageEnum.TOOL and msg.content:
                parts.append(msg.content if isinstance(msg.content, str) else str(msg.content))
        return "\n\n".join(parts)

    def customized_execute(self, input_object: InputObject, agent_input: dict,
                           memory: Memory, llm: LLM,
                           agent_context: AgentContext = None,
                           **kwargs) -> dict:
        llm = agent_context.build_llm()

        llm_output = self.run_tool_calling_loop(
            llm, agent_context, input_object,
            max_iterations=agent_context.max_iterations,
        )

        res = llm_output.text

        # Extract knowledge retrieval results from tool messages
        background = self._extract_tool_background(agent_context)
        if background:
            agent_input['background'] = background

        self._save_memory(agent_context, llm_output, agent_input)
        self._emit_final_output(agent_context, res)

        return {**agent_input, 'output': res}

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict,
                                       memory: Memory, llm: LLM,
                                       agent_context: AgentContext = None,
                                       **kwargs) -> dict:
        llm = agent_context.build_llm()

        llm_output = await self.async_run_tool_calling_loop(
            llm, agent_context, input_object,
            max_iterations=agent_context.max_iterations,
        )

        res = llm_output.text

        background = self._extract_tool_background(agent_context)
        if background:
            agent_input['background'] = background

        self._save_memory(agent_context, llm_output, agent_input)
        self._emit_final_output(agent_context, res)

        return {**agent_input, 'output': res}

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'RagAgentTemplate':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_rag_agent.cn')
        return self
