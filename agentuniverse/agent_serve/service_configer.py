# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/25 16:04
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: service_configer.py

from typing import Optional

from ..agent.agent import Agent
from ..agent.agent_manager import AgentManager
from ..base.config.component_configer.component_configer import ComponentConfiger
from ..base.config.configer import Configer


class ServiceConfiger(ComponentConfiger):
    """The ServiceConfiger class, used to load and manage the service
    configuration."""

    _ComponentConfiger__metadata_class: Optional[str] = None
    _ComponentConfiger__metadata_module: Optional[str] = None

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the ServiceConfiger."""
        super().__init__(configer)
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None
        self.__agent: Optional[Agent] = None
        self.__set_default_meta_info()

    @property
    def name(self) -> Optional[str]:
        """Name field."""
        return self.__name

    @property
    def description(self) -> Optional[str]:
        """Description field."""
        return self.__description

    @property
    def agent(self) -> Optional[Agent]:
        """Agent field."""
        return self.__agent

    def __set_default_meta_info(self):
        """Set default instantiated class of service."""
        if not hasattr(self, "_ComponentConfiger__metadata_module") or self._ComponentConfiger__metadata_module is None:
            self._ComponentConfiger__metadata_module = "agentuniverse.agent_serve.service"
        if not hasattr(self, "_ComponentConfiger__metadata_class") or self._ComponentConfiger__metadata_class is None:
            self._ComponentConfiger__metadata_class = "Service"

    def load(self) -> "ServiceConfiger":
        """Setting property using own configer member property.

        Returns:
            ServiceConfiger: A ServiceConfiger instance.
        """
        return self.load_by_configer(self.configer)

    def load_by_configer(self, configer: Configer) -> "ServiceConfiger":
        """Initialize self using given configer, get ServiceConfiger property
        from it.
        Args:
            configer(Configer): A Configer instance.
        Returns:
            ServiceConfiger: A ServiceConfiger instance.
        """
        super().load_by_configer(configer)
        agent_code = configer.value.get("agent")
        self.__set_default_meta_info()
        try:
            self.__name = configer.value.get("name")
            self.__description = configer.value.get("description")
            agent_manager: AgentManager = AgentManager()
            self.__agent = agent_manager.get_instance_obj(agent_code)
            if not self.__agent:
                raise ValueError
        except ValueError:
            raise ValueError(f"No such Agent: {agent_code}")
        except Exception as e:
            raise Exception(f"Failed to parse the Agent configuration: {e}")
        return self
