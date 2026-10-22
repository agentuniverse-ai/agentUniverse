"""Manager for context router components."""

from agentuniverse.agent.context.router.context_router import ContextRouter
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase


@singleton
class ContextRouterManager(ComponentManagerBase[ContextRouter]):
    """A singleton manager for ContextRouter instances."""

    def __init__(self):
        super().__init__(ComponentEnum.CONTEXT_ROUTER)
