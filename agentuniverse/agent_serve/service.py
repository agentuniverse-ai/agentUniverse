from typing import Optional

from .service_configer import ServiceConfiger
from ..agent.agent import Agent
from ..base.config.application_configer.application_config_manager import ApplicationConfigManager
from ..base.component.component_base import ComponentBase
from ..base.component.component_enum import ComponentEnum


class Service(ComponentBase):
    """The basic class of the service."""

    # Basic attributes of the service class.
    component_type: ComponentEnum = ComponentEnum.SERVICE
    name: Optional[str] = None
    description: Optional[str] = None
    agent: Optional[Agent] = None

    def __post_init_post_parse__(self):
        """Init service code with service name."""
        self.__service_code: Optional[str] = self.get_instance_code()

    def get_instance_code(self) -> str:
        """Generate the full service code from service name."""
        app_cfg_manager: ApplicationConfigManager = ApplicationConfigManager()
        appname = app_cfg_manager.app_configer.base_info_appname
        return f"{appname}.service.{self.name}"

    def initialize_by_component_configer(self, service_configer: ServiceConfiger) -> "Service":
        """Initialize the Service by the ComponentConfiger object.

        Args:
            service_configer(ServiceConfiger): A configer contains service
            basic info.
        Returns:
            Service: A Service instance.
        """
        self.name = service_configer.name
        self.description = service_configer.description
        self.agent = service_configer.agent
        return self

    def run(self, **kwargs) -> str:
        """The executed function when the service is called."""
        if hasattr(self.agent, "agent_model") and "streaming" in kwargs:
            llm_model = self.agent.agent_model.profile.get("llm_model", {})
            llm_model["streaming"] = kwargs["streaming"]
            self.agent.agent_model.profile["llm_model"] = llm_model
        return self.agent.run(**kwargs).to_json_str()

    @property
    def service_code(self):
        """The unique code of each service, generate from service name."""
        return self.__service_code
