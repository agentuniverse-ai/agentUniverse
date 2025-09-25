# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 12:01
# @Author  : jerry.zzw
# @Email   : jerry.zzw@antgroup.com
# @FileName: tool_configer.py
from typing import Optional, List
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class ToolConfiger(ComponentConfiger):
    """The ToolConfiger class, which is used to load and manage the Tool configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the ToolConfiger."""
        super().__init__(configer)
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None
        self.__tool_type: Optional[str] = None
        self.__input_keys: Optional[List] = None

    @property
    def name(self) -> Optional[str]:
        """Return the name of the Tool."""
        return self.__name

    @property
    def description(self) -> Optional[str]:
        """Return the description of the Tool."""
        return self.__description

    @property
    def tool_type(self) -> Optional[str]:
        return self.__tool_type

    @property
    def input_keys(self) -> Optional[List]:
        return self.__input_keys

    def load(self) -> "ToolConfiger":
        """Load the configuration by the Configer object.
        Returns:
            ToolConfiger: the ToolConfiger object
        """
        return self.load_by_configer(self.__configer)

    def load_by_configer(self, configer: Configer) -> "ToolConfiger":
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            ToolConfiger: the ToolConfiger object
        """
        super().load_by_configer(configer)

        try:
            self.__name = configer.value.get("name")
            self.__description = configer.value.get("description")
            self.__tool_type = configer.value.get("tool_type")
            self.__input_keys = configer.value.get("input_keys")
        except Exception as e:
            raise Exception(f"Failed to parse the Tool configuration: {e}")
        return self
