# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 15:46
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_manager_base.py
import copy
from typing import TypeVar, Generic

from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.system_util import is_system_builtin

# Add a type generic constraint.
ComponentTypeVar = TypeVar("ComponentTypeVar", bound=ComponentBase)


class ComponentManagerBase(Generic[ComponentTypeVar]):
    """The ComponentManagerBase class, which is used to define the base class of the component manager."""

    def __init__(self, component_type: ComponentEnum):
        """Initialize the ComponentManagerBase."""
        # The component pool map, which is used to store the component instance.
        # _instance_obj_map - Format: {component_instance_name: component_instance_obj}.
        self._instance_obj_map: dict[str, ComponentTypeVar] = {}
        # Alias and target values use the same fully-qualified codes as the
        # component pool. Targets are canonicalized when aliases are added.
        self._alias_map: dict[str, str] = {}
        self._component_type: ComponentEnum = component_type

    def register(self, component_instance_name: str, component_instance_obj: ComponentTypeVar):
        """Register the component instance."""
        if component_instance_name in self._alias_map:
            LOGGER.warn(f"{self._component_type.value} component name "
                        f"'{component_instance_name}' is already registered as an alias.")
            return
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
                         appname: str = None, new_instance: bool = True,
                         strict: bool = False) -> ComponentTypeVar:
        """Return the component instance object.

        Args:
            component_instance_name: Registered name of the component instance.
            appname: Application name; defaults to the current app's name.
            new_instance: When True, return an independent copy so callers
                cannot mutate the shared registered instance.
            strict: When True, raise a :class:`ValueError` with a descriptive
                message if the component is not registered, instead of
                returning ``None``. Use this at user-facing entry points so a
                missing component surfaces as an actionable error rather than a
                cryptic ``AttributeError`` on the returned ``None`` (e.g.
                ``'NoneType' object has no attribute 'query'``).
        """
        if component_instance_name == "__default_instance__":
            return self.get_default_instance(new_instance)
        appname = appname or ApplicationConfigManager().app_configer.base_info_appname
        instance_code = self._build_instance_code(component_instance_name, appname)
        instance_code = self._alias_map.get(instance_code, instance_code)
        instance = self._instance_obj_map.get(instance_code)
        if instance is None:
            if strict:
                raise ValueError(
                    f"{self._component_type.value} component "
                    f"'{component_instance_name}' is not registered (resolved "
                    f"instance code '{instance_code}'). Ensure the corresponding "
                    f"configuration is loaded before use — verify the component "
                    f"config file and the application bootstrap order."
                )
            return None
        if new_instance:
            return instance.create_copy()
        return instance

    def register_alias(self, alias_name: str, target_name: str,
                       appname: str = None) -> None:
        """Register an alternative name for an existing component.

        Alias targets are resolved to canonical component codes immediately.
        This permits alias chains without leaving cycles or dependencies
        between aliases.

        Args:
            alias_name: New bare component name used by callers.
            target_name: Existing bare component name or alias.
            appname: Application name; defaults to the configured app.

        Raises:
            ValueError: If the alias collides or the target is not registered.
        """
        appname = appname or ApplicationConfigManager().app_configer.base_info_appname
        alias_code = self._build_instance_code(alias_name, appname)
        target_code = self._build_instance_code(target_name, appname)
        canonical_target = self._alias_map.get(target_code, target_code)

        if alias_code in self._instance_obj_map or alias_code in self._alias_map:
            raise ValueError(
                f"Cannot register alias '{alias_name}': the name is already in use."
            )
        if canonical_target not in self._instance_obj_map:
            raise ValueError(
                f"Cannot register alias '{alias_name}': target component "
                f"'{target_name}' is not registered."
            )
        self._alias_map[alias_code] = canonical_target

    def unregister_alias(self, alias_name: str, appname: str = None) -> None:
        """Remove an alias without unregistering its target component."""
        appname = appname or ApplicationConfigManager().app_configer.base_info_appname
        self._alias_map.pop(self._build_instance_code(alias_name, appname))

    def get_alias_map(self) -> dict[str, str]:
        """Return an isolated alias-to-canonical-code mapping."""
        return self._alias_map.copy()

    def _build_instance_code(self, component_name: str, appname: str) -> str:
        """Build the registry key for a bare component name."""
        return f'{appname}.{self._component_type.value.lower()}.{component_name}'

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
