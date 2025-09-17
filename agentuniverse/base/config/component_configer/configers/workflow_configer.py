# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 15:57
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_configer.py
from typing import Optional
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class WorkflowConfiger(ComponentConfiger):
    """The WorkflowConfiger class, which is used to load and manage the workflow configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the WorkflowConfiger."""
        super().__init__(configer)
        self.__id: Optional[str] = None
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None
        self.__graph: Optional[dict] = None

    @property
    def id(self) -> Optional[str]:
        """Return the id of the Workflow."""
        return self.__id

    @property
    def name(self) -> Optional[str]:
        """Return the name of the Workflow."""
        return self.__name

    @property
    def description(self) -> Optional[str]:
        """Return the description of the Workflow."""
        return self.__description

    @property
    def graph(self) -> Optional[dict]:
        return self.__graph

    def load(self) -> "WorkflowConfiger":
        """Load the configuration by the Configer object.
        Returns:
            WorkflowConfiger: the WorkflowConfiger object
        """
        return self.load_by_configer(self.__configer)

    def load_by_configer(self, configer: Configer) -> "WorkflowConfiger":
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            WorkflowConfiger: the WorkflowConfiger object
        """
        super().load_by_configer(configer)

        try:
            self.__id = configer.value.get("id")
            self.__name = configer.value.get("name")
            self.__description = configer.value.get("description")
            self.__graph = configer.value.get("graph")
        except Exception as e:
            raise Exception(f"Failed to parse the Workflow configuration: {e}")
        return self
