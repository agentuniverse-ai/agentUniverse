# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:18
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_manager.py
import importlib

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.llm.llm import LLM


@singleton
class LLMManager(ComponentManagerBase):
    """The LLMManager class, which is used to manage the LLMs."""

    def __init__(self):
        """Initialize the LLMManager."""
        super().__init__(ComponentEnum.LLM)

    def get_instance_obj(self, component_instance_name: str, appname: str = None, new_instance: bool = True) -> LLM:
        """Return the tool instance object."""
        if component_instance_name == "__default_instance__":
            return self.get_default_instance(new_instance)
        appname = appname or ApplicationConfigManager().app_configer.base_info_appname
        instance_code = f"{appname}.{self._component_type.value.lower()}.{component_instance_name}"
        instance_obj = self._instance_obj_map.get(instance_code)
        # If the instance does not exist, try to create it using the configuration
        if instance_obj is None:
            # Retrieve the llm configuration map
            llm_configer_map: dict[str, LLMConfiger] = ApplicationConfigManager().app_configer.llm_configer_map
            if llm_configer_map and component_instance_name in llm_configer_map.keys():
                llm_configer = llm_configer_map.get(component_instance_name)
                if llm_configer:
                    # Dynamically import the module and retrieve the class specified in the configuration
                    if llm_configer.meta_class:
                        metadata_module = ".".join(llm_configer.meta_class.split(".")[:-1])
                        metadata_class = llm_configer.meta_class.split(".")[-1]
                        module = importlib.import_module(metadata_module)
                        component_clz = getattr(module, metadata_class)
                    else:
                        module = importlib.import_module(llm_configer.metadata_module)
                        component_clz = getattr(module, llm_configer.metadata_class)
                    # Initialize the llm instance using the configuration
                    instance_obj: LLM = component_clz().initialize_by_component_configer(llm_configer)
                    if instance_obj:
                        instance_obj.component_config_path = llm_configer.configer.path
                        self.register(instance_obj.get_instance_code(), instance_obj)
        # Return a new copy of the instance if required, otherwise return the existing instance
        if instance_obj and new_instance:
            return instance_obj.create_copy()
        return instance_obj
