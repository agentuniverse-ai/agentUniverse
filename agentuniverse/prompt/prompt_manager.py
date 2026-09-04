# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/17 17:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt_manager.py
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class PromptManager(ComponentManagerBase):
    """The PromptManager class, which is used to manage prompts."""

    def __init__(self):
        """Initialize the prompt manager with the prompt component type.
        """
        super().__init__(ComponentEnum.PROMPT)

    def get_instance_obj(self, component_instance_name: str, appname: str = None, new_instance: bool = False):
        """Return the registered prompt instance by its name, or None when it is not registered.

        Args:
            component_instance_name(str): The registered prompt name.
            appname: Unused, kept for interface compatibility.
            new_instance(bool): Unused, kept for interface compatibility.

        Returns:
            The prompt instance or None.
        """
        return self._instance_obj_map.get(component_instance_name)
