from ..base.annotation.singleton import singleton
from ..base.component.component_enum import ComponentEnum
from ..base.component.component_manager_base import ComponentManagerBase
from .service import Service


@singleton
class ServiceManager(ComponentManagerBase[Service]):
    """A singleton manager class of the service."""

    def __init__(self):
        """Initialize the ServiceManager with the service component type."""
        super().__init__(ComponentEnum.SERVICE)

