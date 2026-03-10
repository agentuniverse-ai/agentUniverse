# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/12/16 14:07
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: choose_product_agent.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.ai_context.agent_context import AgentContext
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import parse_json_markdown
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel


class ChooseProductAgent(AgentTemplate):

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['product_list']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        i_object = input_object.to_dict()
        for key, value in i_object.items():
            agent_input[key] = value
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Agent result parser.

        Args:
            agent_result(dict): Agent result
        Returns:
            dict: Agent result object.
        """
        final_result = dict()

        output = agent_result.get('output')
        output = parse_json_markdown(output)
        final_result['product_list'] = output.get('product_list')
        final_result['reason'] = output.get('reason')
        final_result['company'] = output.get('company')
        return final_result

    def customized_execute(self, input_object: InputObject, agent_input: dict,
                           memory: Memory, llm: LLM,
                           agent_context: AgentContext = None, **kwargs) -> dict:
        # Use custom prompt logic (conditional prompt version selection)
        prompt: ChatPrompt = self.process_prompt(agent_input, **kwargs)
        messages = prompt.render(**agent_input)

        # Invoke LLM
        llm = agent_context.build_llm()
        llm_output = self.invoke_llm(llm, messages, input_object, agent_context=agent_context)
        res = llm_output.text
        return {'output': res}

    def process_prompt(self, agent_input: dict, **kwargs) -> ChatPrompt:
        expert_framework = agent_input.pop('expert_framework', '') or ''

        profile: dict = self.agent_model.profile

        profile_instruction = profile.get('instruction')
        profile_instruction = expert_framework + profile_instruction if profile_instruction else profile_instruction

        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile_instruction)

        # get the prompt by the prompt version (conditional logic based on input)
        input = agent_input.get('input')
        if "医疗险" in input:
            version_prompt: Prompt = PromptManager().get_instance_obj('choose_product_agent_v2.cn')
        else:
            version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)

        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            pm = version_prompt.prompt_model
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(pm, 'introduction', '') or '',
                target=getattr(pm, 'target', '') or '',
                instruction=expert_framework + (getattr(pm, 'instruction', '') or ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model

        chat_prompt = ChatPrompt().build_prompt(profile_prompt_model, ['introduction', 'target', 'instruction'])
        image_urls: list = agent_input.pop('image_urls', []) or []
        if image_urls:
            chat_prompt.generate_image_prompt(image_urls)
        return chat_prompt

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ChooseProductAgent':
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version')
        return self
