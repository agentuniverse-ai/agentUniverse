
from abc import ABC, abstractmethod

from agentuniverse.base.config.configer import Configer
from agentuniverse.base.storage.storage_context import StorageContext


class BaseConfigLoader(ABC):
    """
    Base class for all config loaders.

    All loaders must accept a Configer in __init__,
    so they can extract necessary settings (DB uri, Redis info, etc.)
    """

    def __init__(self,  configer: Configer):
        self.configer = configer

    @abstractmethod
    def load(self,  ctx: StorageContext) -> dict:
        """Load config for given Configer."""
        pass

    @abstractmethod
    def save(self,  ctx: StorageContext) -> None:
        """Persist config to storage."""
        pass

    @abstractmethod
    def delete(self,  ctx: StorageContext) -> None:
        """Delete config from storage."""
        pass