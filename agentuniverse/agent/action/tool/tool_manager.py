# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 13:54
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool_manager.py
import importlib

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger


@singleton
class ToolManager(ComponentManagerBase):
    """The ToolManager class, which is used to manage the tools."""

    def __init__(self):
        """Initialize the ToolManager."""
        super().__init__(ComponentEnum.TOOL)

    def get_instance_obj(self, component_instance_name: str,
                         appname: str = None, new_instance: bool = True) -> Tool:
        """Return the tool instance object."""
        if component_instance_name == "__default_instance__":
            return self.get_default_instance(new_instance)
        appname = appname or ApplicationConfigManager().app_configer.base_info_appname
        instance_code = f'{appname}.{self._component_type.value.lower()}.{component_instance_name}'
        instance_obj = self._instance_obj_map.get(instance_code)
        # If the instance does not exist, try to create it using the configuration
        if instance_obj is None:
            # Retrieve the tool configuration map
            tool_configer_map: dict[str, ToolConfiger] = ApplicationConfigManager().app_configer.tool_configer_map
            toolkit_configer_map = ApplicationConfigManager().app_configer.toolkit_configer_map
            if toolkit_configer_map and '@' in component_instance_name:
                toolkit_name, tool_name = component_instance_name.split('@')
                from agentuniverse.agent.action.toolkit.toolkit_manager import \
                    ToolkitManager
                ToolkitManager().get_instance_obj(toolkit_name)
                instance_obj = self._instance_obj_map.get(instance_code)

            if not instance_obj and tool_configer_map and component_instance_name in tool_configer_map.keys():
                tool_configer = tool_configer_map.get(component_instance_name)
                if tool_configer:
                    # Dynamically import the module and retrieve the class specified in the configuration
                    if tool_configer.meta_class:
                        metadata_module = '.'.join(tool_configer.meta_class.split('.')[:-1])
                        metadata_class = tool_configer.meta_class.split('.')[-1]
                        module = importlib.import_module(metadata_module)
                        component_clz = getattr(module, metadata_class)
                    else:
                        module = importlib.import_module(tool_configer.metadata_module)
                        component_clz = getattr(module, tool_configer.metadata_class)
                    # Initialize the tool instance using the configuration
                    instance_obj: Tool = component_clz().initialize_by_component_configer(tool_configer)
                    if instance_obj:
                        instance_obj.component_config_path = tool_configer.configer.path
                        self.register(instance_obj.get_instance_code(), instance_obj)
        # Return a new copy of the instance if required, otherwise return the existing instance
        if instance_obj and new_instance:
            return instance_obj.create_copy()
        return instance_obj
