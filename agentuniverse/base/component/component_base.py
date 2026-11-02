# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 15:35
# @Author  : jerry.zzw
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_base.py
import copy
import logging
from typing import Optional

from pydantic import BaseModel, ConfigDict

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Stdlib logger: the project LOGGER imports this module through system_util,
# so using it here would cycle. Callers still see the failure.
logger = logging.getLogger(__name__)


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
        """Return an isolated copy of this component.

        ``ComponentManagerBase.get_instance_obj(..., new_instance=True)`` uses
        this so a caller cannot mutate the registered instance.

        Prefer ``model_copy(deep=True)``. If that fails, fall back to
        ``copy.deepcopy`` and log the original error. A shallow
        ``model_copy()`` is not used: it would share mutable fields with the
        original. If both deep-copy paths fail, the ``copy.deepcopy`` error
        propagates.

        Returns:
            ComponentBase: an independent copy of this component.

        Raises:
            Exception: If neither deep-copy path can copy this component.
        """
        try:
            return self.model_copy(deep=True)
        except Exception as e:
            # Broad catch by design: deep model_copy can fail for varied field
            # types. Log it, then try stdlib deepcopy before giving up.
            logger.warning(
                "deep model_copy failed (%s); using deepcopy fallback", e
            )
            return copy.deepcopy(self)
