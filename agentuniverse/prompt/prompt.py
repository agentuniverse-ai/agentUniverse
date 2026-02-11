# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:22
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: prompt.py
"""Prompt base module."""
import re
from typing import Optional, List

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
from agentuniverse.base.util.prompt_util import generate_template, render_str
from agentuniverse.prompt.prompt_model import AgentPromptModel


class Prompt(ComponentBase):
    """Prompt class."""

    prompt_version: Optional[str] = None
    prompt_template: Optional[str] = None
    input_variables: Optional[list[str]] = None

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.PROMPT, **kwargs)

    def build_prompt(self, agent_prompt_model: AgentPromptModel, prompt_assemble_order: list[str]) -> 'Prompt':
        """Build the prompt class.

        Args:
            agent_prompt_model (AgentPromptModel): The user agent prompt model.
            prompt_assemble_order (list[str]): The prompt assemble ordered list.

        Returns:
            Prompt: The prompt object.
        """
        self.prompt_template = generate_template(agent_prompt_model, prompt_assemble_order)
        self.input_variables = re.findall(r'\{(.*?)}', self.prompt_template)
        return self

    def render(self, **kwargs) -> List[Message]:
        """渲染 prompt 模板，缺少变量时抛出 ValueError。"""
        if not self.prompt_template:
            user_str = ''
        else:
            user_str = render_str(self.prompt_template, kwargs)
        return [Message(type=ChatMessageEnum.USER, content=user_str)]

    def get_instance_code(self) -> str:
        """Return the prompt version of the current prompt."""
        return self.prompt_version

    def initialize_by_component_configer(self,
                                         component_configer: PromptConfiger) -> "Prompt":
        """Initialize the prompt by the PromptConfiger object.

        Args:
            component_configer: the PromptConfiger object.

        Returns:
            Prompt: the prompt object.
        """
        prompt_values = []
        for k, v in component_configer.configer.value.items():
            if k == "metadata":
                continue
            self.__dict__[k] = v
            # few_shot_examples 在配置中可能是 list[dict]，跳过直接拼接
            if isinstance(v, str):
                prompt_values.append(v)

        if component_configer.metadata_version:
            self.prompt_version = component_configer.metadata_version

        self.prompt_template = '\n'.join(prompt_values)

        self.input_variables = re.findall(r'\{(.*?)}', self.prompt_template)
        return self
