# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/9/29 17:11
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: work_pattern.py
from abc import abstractmethod
from typing import Optional

from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.configers.work_pattern_configer import WorkPatternConfiger


class WorkPattern(ComponentBase):
    name: Optional[str] = None
    description: Optional[str] = None

    def __init__(self):
        """Initialize the ComponentBase."""
        super().__init__(component_type=ComponentEnum.WORK_PATTERN)

    @abstractmethod
    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Invoke the work pattern.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            work_pattern_input (dict): Work pattern input dictionary.
            **kwargs: Additional keyword arguments.
        Returns:
            dict: The work pattern result.
        """
        pass

    @abstractmethod
    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Asynchronously invoke the work pattern.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            work_pattern_input (dict): Work pattern input dictionary.
            **kwargs: Additional keyword arguments.
        Returns:
            dict: The work pattern result.
        """
        pass

    def initialize_by_component_configer(self, work_pattern_configer: WorkPatternConfiger) -> "WorkPattern":
        """Initialize the work pattern by the WorkPatternConfiger object.

        Args:
            work_pattern_configer(WorkPatternConfiger): the WorkPatternConfiger object
        Returns:
            WorkPattern: the work pattern object
        """
        self.name = work_pattern_configer.name
        self.description = work_pattern_configer.description
        return self

    def set_by_agent_model(self, **kwargs):
        pass
