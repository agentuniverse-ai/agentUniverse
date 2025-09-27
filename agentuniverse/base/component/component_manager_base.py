# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 15:46
# @Author  : jerry.zzw
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_manager_base.py
import copy
from typing import TypeVar, Generic

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.storage.storage_context import StorageContext
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.system_util import is_system_builtin

# 添加类型泛型限定
ComponentTypeVar = TypeVar("ComponentTypeVar", bound=ComponentBase)


class ComponentManagerBase(Generic[ComponentTypeVar]):
    """The ComponentManagerBase class, which is used to define the base class of the component manager."""

    def __init__(self, component_type: ComponentEnum):
        """Initialize the ComponentManagerBase."""
        # The component pool map, which is used to store the component instance.
        # _instance_obj_map - Format: {component_instance_name: component_instance_obj}.
        self._instance_obj_map: dict[str, ComponentTypeVar] = {}
        self._component_type: ComponentEnum = component_type

    def register(self, component_instance_name: str, component_instance_obj: ComponentTypeVar):
        """Register the component instance."""
        if component_instance_name in self._instance_obj_map.keys():
            if is_system_builtin(component_instance_obj):
                LOGGER.info(f"Component name '{component_instance_name}' is already registered. "
                            f"Skipping system built-in component in favor of user-configured component.")
                return
            LOGGER.warn(f"{self._component_type.value} component object instance with name "
                        f"'{component_instance_name}' already exists.")
            return
        self._instance_obj_map[component_instance_name] = component_instance_obj
        if component_instance_obj.default_symbol:
            self._instance_obj_map["__default_instance__"] = component_instance_obj

    def unregister(self, component_instance_name: str):
        """Unregister the component instance abstractmethod."""
        self._instance_obj_map.pop(component_instance_name)

    def get_instance_obj(self, component_instance_name: str,
                         appname: str = None, new_instance: bool = True) -> ComponentTypeVar:
        """Return the component instance object."""
        if component_instance_name == "__default_instance__":
            return self.get_default_instance(new_instance)
        appname = appname or ApplicationConfigManager().app_configer.base_info_appname
        instance_code = f'{appname}.{self._component_type.value.lower()}.{component_instance_name}'
        instance = self._instance_obj_map.get(instance_code)
        if not instance:
            instance = self._load_instance(instance_code)
        if instance:
            return instance.create_copy() if new_instance else instance

    def _load_instance(self, instance_code: str) -> ComponentTypeVar:
        from agentuniverse.base.storage.config_storage import ConfigStorage, ConfigNotFoundError, InstanceLoadError
        LOGGER.info(f"Loading {self._component_type.value} component instance '{instance_code}' from storage.")
        try:
            ctx = StorageContext(
                instance_code=instance_code,
                configer_type=self._component_type
            )
            configer = ConfigStorage().load_from_storage(ctx)
        except Exception as e:
            raise InstanceLoadError(
                f"Unexpected error while loading config for {instance_code}: {e}"
            ) from e
        from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
        if configer.value:
            configer_clz = ComponentConfigerUtil.get_component_config_clz_by_type(self._component_type)
            configer_instance = configer_clz().load_by_configer(configer)
            component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(configer_instance)
            new_instance_obj = component_clz().initialize_by_component_configer(configer_instance)

            if not new_instance_obj:
                raise InstanceLoadError(f"Failed to initialize instance for {instance_code}")

            new_instance_obj.component_config_path = configer.path
            self._instance_obj_map[instance_code] = new_instance_obj

            return new_instance_obj

    def get_default_instance(self, new_instance: bool = False) -> ComponentTypeVar:
        """Return the default instance of component."""
        if new_instance:
            return copy.deepcopy(self._instance_obj_map.get("__default_instance__"))
        return self._instance_obj_map.get("__default_instance__")

    def get_instance_name_list(self) -> list[str]:
        """Return the component instance list."""
        return list(self._instance_obj_map.keys())

    def get_instance_obj_list(self) -> list[ComponentTypeVar]:
        """Return the component instance object list."""
        return list(self._instance_obj_map.values())
