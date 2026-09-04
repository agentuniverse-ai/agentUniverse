# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/17 11:51
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: slave_rag_agent_template.py
# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import Any
from langchain_core.runnables import RunnableSerializable
import datetime
import re

from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.input_object import InputObject
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from agentuniverse.base.context.context_archive_utils import get_current_context_archive


class SlaveRagAgentTemplate(AgentTemplate):

    """RAG agent template used as a slave (sub) agent, resolving prompt params and context archive placeholders before invoking the configured prompt.
    """
    def input_keys(self) -> list[str]:
        return ['prompt_name', 'prompt_params']

    def output_keys(self) -> list[str]:
        """Return the output keys produced by this template.

        Returns:
            list[str]: The list of output keys.
        """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:

        """Copy prompt_name and prompt_params from the input object, resolve context archive placeholders and expose every prompt param back into the input object.

        Args:
            input_object(InputObject): The user input object.
            agent_input(dict): The agent input dictionary to be filled.

        Returns:
            dict: The updated agent input.
        """
        agent_input['prompt_name'] = input_object.get_data('prompt_name')
        agent_input['prompt_params'] = input_object.get_data('prompt_params')
        context_archive = get_current_context_archive()

        # get archive data from context
        agent_input.update(agent_input.get('prompt_params'))
        for k, v in agent_input.items():
            result = v
            if isinstance(v, str):
                pattern = r'\$\#\{(\w+)\}'
                result = re.sub(pattern, lambda match: context_archive.get(match.group(1), {}).get('data', match.group(0)), v)
            elif isinstance(v, list):
                replaced_str = []
                for origin_str in v:
                    pattern = r'\$\#\{(\w+)\}'
                    replaced_str.append(re.sub(pattern, lambda match: context_archive.get(
                        match.group(1), {}).get('data', match.group(0)), origin_str))
                result = '\n****************************\n'.join(replaced_str)

            agent_input[k] = result
            input_object.add_data(k, result)
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Return the agent result enriched with its output value.

        Args:
            agent_result(dict): The raw agent result.

        Returns:
            dict: The agent result with the output key present.
        """
        return {**agent_result, 'output': agent_result['output']}

    def process_prompt(self, agent_input: dict, **kwargs) -> ChatPrompt:
        """Build the chat prompt from the profile and the configured prompt version, prepending the expert framework and optional image URLs when present.

        Args:
            agent_input(dict): The agent input containing prompt_name and prompt params.
            **kwargs: Extra keyword arguments accepted for interface compatibility.

        Returns:
            ChatPrompt: The built chat prompt.

        Raises:
            Exception: If neither a prompt version nor an inline prompt model is available.
        """
        expert_framework = agent_input.pop('expert_framework', '') or ''

        profile: dict = self.agent_model.profile

        profile_instruction = profile.get('instruction')
        profile_instruction = expert_framework + profile_instruction if profile_instruction else profile_instruction

        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile_instruction)
        # get the prompt by the prompt version
        version_prompt: Prompt = PromptManager().get_instance_obj(agent_input['prompt_name'])

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
