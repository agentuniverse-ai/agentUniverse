# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/12/16 14:07
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: choose_product_agent.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from langchain_core.utils.json import parse_json_markdown


class ChooseProductAgent(AgentTemplate):
    """Agent template that picks the best-matching product for the user.

    It evaluates the user requirement together with the candidate product
    descriptions and returns the chosen product list with a reason.
    """

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

    def process_prompt(self, agent_input: dict, **kwargs) -> ChatPrompt:
        """Build the chat prompt for choosing the product.

        Args:
            agent_input (dict): agent input, which may carry an expert
                framework and image urls.
            **kwargs: additional agent execution arguments.
        Returns:
            ChatPrompt: the assembled chat prompt.
        """
        expert_framework = agent_input.pop('expert_framework', '') or ''

        profile: dict = self.agent_model.profile

        profile_instruction = profile.get('instruction')
        profile_instruction = expert_framework + profile_instruction if profile_instruction else profile_instruction

        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile_instruction)

        # get the prompt by the prompt version
        input = agent_input.get('input')
        if "医疗险" in input:
            version_prompt: Prompt = PromptManager().get_instance_obj('choose_product_agent_v2.cn')
        else:
            version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)

        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=expert_framework + getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model

        chat_prompt = ChatPrompt().build_prompt(profile_prompt_model, ['introduction', 'target', 'instruction'])
        image_urls: list = agent_input.pop('image_urls', []) or []
        if image_urls:
            chat_prompt.generate_image_prompt(image_urls)
        return chat_prompt

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ChooseProductAgent':
        """Initialize the agent and cache its configured prompt version.

        Args:
            component_configer (AgentConfiger): the agent component configer.
        Returns:
            ChooseProductAgent: the initialized agent instance.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version')
        return self
