# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/25 16:04
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: service_configer.py

from typing import TYPE_CHECKING, Optional

from ..base.config.component_configer.component_configer import ComponentConfiger
from ..base.config.configer import Configer

if TYPE_CHECKING:
    from ..agent.agent import Agent


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
        self.__agent: Optional['Agent'] = None
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
    def agent(self) -> Optional['Agent']:
        """Agent field."""
        return self.__agent

    def __set_default_meta_info(self):
        """Set default instantiated class of service."""
        if (not hasattr(self, '_ComponentConfiger__metadata_module')
                or self._ComponentConfiger__metadata_module is None):
            self._ComponentConfiger__metadata_module = ("agentuniverse."
                                                        "agent_serve.service")
        if (not hasattr(self, '_ComponentConfiger__metadata_class')
                or self._ComponentConfiger__metadata_class is None):
            self._ComponentConfiger__metadata_class = 'Service'

    def load(self) -> 'ServiceConfiger':
        """Setting property using own configer member property.

        Returns:
            ServiceConfiger: A ServiceConfiger instance.
        """
        return self.load_by_configer(self.configer)

    def load_by_configer(self, configer: Configer) -> 'ServiceConfiger':
        """Initialize self using given configer, get ServiceConfiger property
        from it.
        Args:
            configer(Configer): A Configer instance.
        Returns:
            ServiceConfiger: A ServiceConfiger instance.
        """
        super().load_by_configer(configer)
        agent_code = configer.value.get('agent')
        service_name = configer.value.get('name') or '<unnamed>'
        config_path = configer.path or '<unknown>'
        self.__set_default_meta_info()
        try:
            self.__name = configer.value.get('name')
            self.__description = configer.value.get('description')
            if not agent_code:
                raise ValueError(
                    f"Service '{service_name}' in config '{config_path}' must define a non-empty 'agent'."
                )
            from ..agent.agent_manager import AgentManager

            agent_manager = AgentManager()
            self.__agent = agent_manager.get_instance_obj(agent_code)
            if not self.__agent:
                registered_agents = agent_manager.get_instance_name_list()
                registered_hint = (
                    f" Registered agents: {registered_agents}."
                    if registered_agents else
                    " No agents are registered."
                )
                raise ValueError(
                    f"No such Agent: '{agent_code}' referenced by service '{service_name}' "
                    f"in config '{config_path}'.{registered_hint}"
                )
        except ValueError as e:
            raise ValueError(str(e)) from e
        except Exception as e:
            raise Exception(
                f"Failed to parse the Agent configuration for service '{service_name}' "
                f"in config '{config_path}': {e}"
            ) from e
        return self
