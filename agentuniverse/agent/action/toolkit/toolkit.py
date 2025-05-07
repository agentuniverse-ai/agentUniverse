# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import copy
from typing import List, Optional

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import \
    ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class Toolkit(ComponentBase):
    """
    The toolkit is a collection of tools.

    Attributes:
        name (str): The name of the toolkit.
        description (str): The description of the tool.
        include (list):
    """

    name: str = ""
    description: Optional[str] = None
    include: Optional[List[str]] = []

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.TOOLKIT, **kwargs)

    @property
    def tool_names(self) -> list:
        """Return all tool names in toolkit."""
        return copy.deepcopy(self.include)


    @property
    def tool_descriptions(self) -> list:
        """Return all tools' descriptions in toolkit."""
        tools = [ToolManager().get_instance_obj(tool_name, new_instance=False) for tool_name in self.include]
        tools_descriptions = [f'tool name:{tool.name}\ntool description:{tool.description}\n' for tool in tools]
        return tools_descriptions

    @property
    def func_call_list(self) -> list:
        raise NotImplementedError

    def get_instance_code(self) -> str:
        """Return the full name of the toolkit."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'Toolkit':
        """Initialize the Toolkit by the ComponentConfiger object.
        Args:
            component_configer(LLMConfiger): the ComponentConfiger object
        Returns:
            Toolkit: the Toolkit object
        """
        try:
            for key, value in component_configer.configer.value.items():
                if key != 'metadata':
                    setattr(self, key, value)
        except Exception as e:
            print(f"Error during configuration initialization: {str(e)}")
        if component_configer.name:
            self.name = component_configer.name
        if component_configer.description:
            self.description = component_configer.description
        if hasattr(component_configer, "include"):
            self.include = component_configer.include
        self._initialize_by_component_configer(component_configer)
        return self
