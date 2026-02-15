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
from agentuniverse.prompt.prompt_model import AgentPromptModel, FewShotExample


class Prompt(ComponentBase):
    """Prompt class.

    Attributes:
        prompt_version: Version identifier (e.g. ``demo_agent.cn_v2``).
        prompt_model: Structured representation of the prompt content,
            preserving introduction / target / instruction / few_shot_examples /
            output_format and custom sections.
        prompt_template: Flat string template (kept for backward compat).
        input_variables: Placeholder names extracted from prompt_template.
    """

    prompt_version: Optional[str] = None
    prompt_model: Optional[AgentPromptModel] = None
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
        self.prompt_model = agent_prompt_model
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

        Parses the YAML config into both:
        1. An ``AgentPromptModel`` (``self.prompt_model``) that preserves
           structured fields (introduction, few_shot_examples, etc.).
        2. A flat ``prompt_template`` string for backward-compat callers
           that use ``prompt.prompt_template.format(...)``.
        """
        config = component_configer.configer.value
        named_fields = set(AgentPromptModel._NAMED_STR_FIELDS)

        model_kwargs = {}
        custom_sections = {}
        prompt_values: list[str] = []

        for k, v in config.items():
            if k == "metadata":
                continue

            # Classify into AgentPromptModel buckets
            if k in named_fields:
                model_kwargs[k] = v
            elif k == 'few_shot_examples' and isinstance(v, list):
                model_kwargs['few_shot_examples'] = [
                    FewShotExample(**ex) if isinstance(ex, dict) else ex
                    for ex in v
                ]
            elif isinstance(v, str):
                custom_sections[k] = v

            # Flat template: only string values
            if isinstance(v, str):
                prompt_values.append(v)

        self.prompt_model = AgentPromptModel(**model_kwargs, sections=custom_sections)

        if component_configer.metadata_version:
            self.prompt_version = component_configer.metadata_version

        self.prompt_template = '\n'.join(prompt_values)
        self.input_variables = re.findall(r'\{(.*?)}', self.prompt_template)
        return self
