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
    """Base class for work patterns in the agentUniverse framework.
    
    WorkPattern is an abstract base class that defines the interface for work
    pattern components in the agentUniverse framework. Work patterns define
    how agents collaborate and execute tasks in a structured manner.
    
    This class provides a standardized way to implement work patterns,
    supporting both synchronous and asynchronous execution modes.
    
    Attributes:
        name (Optional[str]): Optional name identifier for the work pattern.
        description (Optional[str]): Optional description of the work pattern's 
            functionality.
    
    Example:
        >>> class MyWorkPattern(WorkPattern):
        ...     def invoke(self, input_object, work_pattern_input, **kwargs):
        ...         # Custom work pattern logic
        ...         return {'result': 'work_completed'}
        >>> 
        >>> pattern = MyWorkPattern()
        >>> result = pattern.invoke(input_object, work_pattern_input)
    
    Note:
        Subclasses must implement both `invoke` and `async_invoke` methods
        to provide specific work pattern logic.
    """
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

    def initialize_by_component_configer(self, work_pattern_configer: WorkPatternConfiger) -> 'WorkPattern':
        """Initialize the work pattern by the WorkPatternConfiger object.

        This method configures the WorkPattern instance using the provided
        configuration object. It sets the name and description attributes
        from the configuration.

        Args:
            work_pattern_configer (WorkPatternConfiger): A configuration object 
                containing WorkPattern basic information including name and 
                description.
        
        Returns:
            WorkPattern: The configured WorkPattern instance (self).
        
        Example:
            >>> config = WorkPatternConfiger()
            >>> config.name = "collaborative_pattern"
            >>> config.description = "Pattern for agent collaboration"
            >>> pattern = MyWorkPattern()
            >>> configured_pattern = pattern.initialize_by_component_configer(config)
        """
        self.name = work_pattern_configer.name
        self.description = work_pattern_configer.description
        return self

    def set_by_agent_model(self, **kwargs):
        pass
