# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/25 16:56
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: translation_agent.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel


class TranslationAgent(RagAgentTemplate):
    """RAG agent template subclass that translates text based on the execute_type and country profile settings.
    """
    def input_keys(self) -> list[str]:
        """Return the input keys declared in the agent profile.

        Returns:
            list[str]: The configured input keys.
        """
        return self.agent_model.profile.get('input_keys')

    def output_keys(self) -> list[str]:
        """Return the output keys declared in the agent profile.

        Returns:
            list[str]: The configured output keys.
        """
        return self.agent_model.profile.get('output_keys')

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Copy every data field of the input object into the agent input.

        Args:
            input_object(InputObject): The user input object.
            agent_input(dict): The agent input dictionary to be filled.

        Returns:
            dict: The updated agent input.
        """
        for key in input_object.to_dict():
            agent_input[key] = input_object.get_data(key)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """Return the agent result unchanged.

        Args:
            planner_result(dict): The raw agent result.

        Returns:
            dict: The agent result.
        """
        return planner_result

    def process_prompt(self, agent_input: dict, **kwargs) -> ChatPrompt:
        """Build the chat prompt, selecting a prompt version based on the translation type and the target country when relevant.

        Args:
            agent_input(dict): The agent input containing translation hints.
            **kwargs: Extra keyword arguments accepted for interface compatibility.

        Returns:
            ChatPrompt: The built chat prompt.

        Raises:
            Exception: If neither a prompt version nor an inline prompt model is available.
        """
        profile: dict = self.agent_model.profile
        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile.get('instruction'))
        # get the prompt by the prompt version
        prompt_version = self.prompt_version
        translation_type = agent_input.get('execute_type')
        if translation_type == "multi":
            prompt_version = f"multi_{self.prompt_version}"
        if agent_input.get('country') and self.agent_model.info.get('name') == 'translation_reflection_agent':
            prompt_version = f"country_{self.prompt_version}"

        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)
        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model
        return ChatPrompt().build_prompt(profile_prompt_model, ['introduction', 'target', 'instruction'])
