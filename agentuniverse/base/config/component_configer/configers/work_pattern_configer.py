# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/8 10:48
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: work_pattern_configer.py
from typing import Optional

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class WorkPatternConfiger(ComponentConfiger):
    """The WorkPatternConfiger class, which is used to load and manage the WorkPattern configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the WorkPatternConfiger."""
        super().__init__(configer)
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None

    @property
    def name(self) -> Optional[str]:
        """Return the name of the WorkPattern."""
        return self.__name

    @property
    def description(self) -> Optional[str]:
        """Return the description of the WorkPattern."""
        return self.__description

    def load(self) -> "WorkPatternConfiger":
        """Load the configuration by the Configer object.
        Returns:
            WorkPatternConfiger: the WorkPatternConfiger object
        """
        return self.load_by_configer(self.__configer)

    def load_by_configer(self, configer: Configer) -> "WorkPatternConfiger":
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            WorkPatternConfiger: the WorkPatternConfiger object
        """
        super().load_by_configer(configer)
        try:
            self.__name = configer.value.get("name")
            self.__description = configer.value.get("description")
        except Exception as e:
            raise Exception(f"Failed to parse the work pattern configuration: {e}")
        return self
