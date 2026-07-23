# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 15:35
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_base.py
from typing import Optional

from pydantic import BaseModel, ConfigDict

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class ComponentBase(BaseModel):
    """The ComponentBase class, which is used to define the base class of the component."""

    component_type: ComponentEnum
    # component yaml path
    component_config_path: Optional[str] = None

    # Used to indicate whether this object is the default object for the corresponding component.
    default_symbol: bool = False
    # pydantic protected_namespaces config
    model_config = ConfigDict(protected_namespaces=())

    def get_instance_code(self) -> str:
        """Return the full name of the component."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'ComponentBase':
        """Initialize the component by the ComponentConfiger object.

        Args:
            component_configer(ComponentConfiger): the ComponentConfiger object
        Returns:
            ComponentBase: the component object
        """
        if hasattr(component_configer, "default_symbol"):
            self.default_symbol = component_configer.default_symbol
        self._initialize_by_component_configer(component_configer)

        return self

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'ComponentBase':
        pass

    def is_default_object(self):
        return self.default_symbol

    def create_copy(self):
        try:
            return self.model_copy(deep=True)
        except Exception:
            return self.model_copy()
