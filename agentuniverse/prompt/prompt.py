# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:22
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: prompt.py
"""Prompt base module."""
from typing import Any, Optional

from langchain_core.prompts import PromptTemplate
from pydantic import Field

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
from agentuniverse.base.util.prompt_util import generate_template
from agentuniverse.prompt.prompt_model import AgentPromptModel


class Prompt(ComponentBase):
    """Prompt class."""

    prompt_version: Optional[str] = None
    prompt_template: Optional[str] = None
    input_variables: Optional[list[str]] = None
    partial_variables: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.PROMPT, **kwargs)

    def as_langchain(self):
        """Convert the prompt template into a LangChain prompt template.

        Returns:
            PromptTemplate: The prompt template.
        """
        return PromptTemplate(template=self.prompt_template,
                              input_variables=self.input_variables,
                              partial_variables=self.partial_variables)

    def partial(self, **values: Any) -> 'Prompt':
        """Return an independent prompt with reusable variables bound.

        Values may be constants or zero-argument callables, matching LangChain
        partial prompt semantics.
        """
        template_variables = set(self._extract_input_variables())
        unknown_variables = sorted(set(values) - template_variables)
        if unknown_variables:
            raise ValueError(
                f'Cannot bind variables not present in the prompt template: '
                f'{", ".join(unknown_variables)}.'
            )
        copied = self.model_copy(deep=True)
        copied.partial_variables.update(values)
        copied.input_variables = [
            variable for variable in self._extract_input_variables()
            if variable not in copied.partial_variables
        ]
        return copied

    def format(self, **values: Any) -> str:
        """Render this prompt using its partial and invocation variables."""
        return self.as_langchain().format(**values)

    def _extract_input_variables(self) -> list[str]:
        """Return variables declared by the current f-string template."""
        if not self.prompt_template:
            return []
        return PromptTemplate.from_template(self.prompt_template).input_variables

    def build_prompt(self, agent_prompt_model: AgentPromptModel, prompt_assemble_order: list[str]) -> 'Prompt':
        """Build the prompt class.

        Args:
            agent_prompt_model (AgentPromptModel): The user agent prompt model.
            prompt_assemble_order (list[str]): The prompt assemble ordered list.

        Returns:
            Prompt: The prompt object.
        """
        self.prompt_template = generate_template(agent_prompt_model, prompt_assemble_order)
        self.input_variables = self._extract_input_variables()
        return self

    def get_instance_code(self) -> str:
        """Return the prompt version of the current prompt."""
        return self.prompt_version

    def initialize_by_component_configer(self, component_configer: PromptConfiger) -> 'Prompt':
        """Initialize the prompt by the PromptConfiger object.

        Args:
            component_configer(PromptConfiger): the PromptConfiger object
        Returns:
            Prompt: the prompt object
        """
        prompt_values = []
        for k, v in component_configer.configer.value.items():
            # ignore metadata values
            if k == 'metadata':
                continue
            self.__dict__[k] = v
            # splice the values in the prompt configer
            prompt_values.append(str(v))

        if component_configer.metadata_version:
            self.prompt_version = component_configer.metadata_version

        self.prompt_template = '\n'.join(prompt_values)

        self.input_variables = self._extract_input_variables()
        return self
