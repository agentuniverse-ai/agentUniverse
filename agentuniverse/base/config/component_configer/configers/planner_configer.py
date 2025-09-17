# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 12:01
# @Author  : jerry.zzw
# @Email   : jerry.zzw@antgroup.com
# @FileName: planner_configer.py
from typing import Optional
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class PlannerConfiger(ComponentConfiger):
    """The PlannerConfiger class, which is used to load and manage the Planner configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the PlannerConfiger."""
        super().__init__(configer)
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None
        self.__input_key: Optional[str] = None
        self.__output_key: Optional[str] = None
        self.__memory_key: Optional[str] = None

    @property
    def input_key(self) -> Optional[str]:
        """Return the input key of the Planner."""
        return self.__input_key

    @property
    def output_key(self) -> Optional[str]:
        """Return the output key of the Planner."""
        return self.__output_key

    @property
    def memory_key(self) -> Optional[str]:
        """Return the memory key of the Planner."""
        return self.__memory_key

    @property
    def name(self) -> Optional[str]:
        """Return the name of the Planner."""
        return self.__name

    @property
    def description(self) -> Optional[str]:
        """Return the description of the Planner."""
        return self.__description

    def load(self) -> "PlannerConfiger":
        """Load the configuration by the Configer object.
        Returns:
            PlannerConfiger: the PlannerConfiger object
        """
        return self.load_by_configer(self.__configer)

    def load_by_configer(self, configer: Configer) -> "PlannerConfiger":
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            PlannerConfiger: the PlannerConfiger object
        """
        super().load_by_configer(configer)

        try:
            self.__name = configer.value.get("name")
            self.__description = configer.value.get("description")
        except Exception as e:
            raise Exception(f"Failed to parse the Planner configuration: {e}")
        return self
