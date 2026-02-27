# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/27
# @FileName: skill_fork_agent_template.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.ai_context.agent_context import AgentContext
from agentuniverse.llm.llm import LLM


class SkillForkAgentTemplate(Agent):
    """Internal agent template for skill fork mode sub-agents.

    This is a lightweight Agent subclass used exclusively by
    ``LoadSkillTool._execute_fork``.  It is **not** registered via YAML and
    is constructed programmatically at runtime.

    The caller prepares a fully-built ``AgentContext`` (with system_message,
    tools_schema, current_messages, etc.) and passes it via ``InputObject``
    under the key ``'agent_context'``.  The template's ``execute`` /
    ``async_execute`` picks it up and runs the standard tool-calling loop.

    Key characteristics:
    - Minimal implementation — no memory, prompt loading, or YAML init.
    - ``run`` / ``async_run`` are the public entry points (standard Agent API).
    - ``MAX_NESTED_DEPTH`` prevents recursive fork spawning.
    """

    MAX_NESTED_DEPTH: int = 1

    def __init__(self, agent_model: AgentModel = None, **kwargs):
        super().__init__(**kwargs)
        if agent_model is None:
            agent_model = AgentModel(
                info={'name': 'skill_fork_agent'},
                profile={},
                memory={},
                action={},
            )
        self.agent_model = agent_model

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return agent_result

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute fork mode using the pre-built AgentContext from InputObject."""
        agent_context: AgentContext = input_object.get_data('agent_context')
        llm: LLM = input_object.get_data('llm')
        max_iterations: int = input_object.get_data('max_iterations') or 10

        llm_output = self.run_tool_calling_loop(
            llm, agent_context, input_object,
            max_iterations=max_iterations,
        )

        res = llm_output.text if llm_output else ""
        return {**agent_input, 'output': res}

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Async execute fork mode using the pre-built AgentContext from InputObject."""
        agent_context: AgentContext = input_object.get_data('agent_context')
        llm: LLM = input_object.get_data('llm')
        max_iterations: int = input_object.get_data('max_iterations') or 10

        llm_output = await self.async_run_tool_calling_loop(
            llm, agent_context, input_object,
            max_iterations=max_iterations,
        )

        res = llm_output.text if llm_output else ""
        return {**agent_input, 'output': res}
