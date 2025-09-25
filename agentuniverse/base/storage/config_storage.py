# -*- coding:utf-8 -*-
import importlib
from typing import Optional, Dict, Type
from agentuniverse.base.annotation.singleton import singleton
from .loader.DB_config_loader import DBConfigLoader
from .loader.base_config_loader import BaseConfigLoader
from .storage_context import StorageContext
from ..component.component_enum import ComponentEnum
from ..component.component_manager_base import ComponentTypeVar
from ..config.configer import Configer

BUILTIN_LOADERS: Dict[str, Type[BaseConfigLoader]] = {
    "DB": DBConfigLoader,
    # "file": FileConfigLoader,
    # "redis": RedisConfigLoader,
}


@singleton
class ConfigStorage:
    """
    Persistent configuration storage manager.

    Handles saving and loading of configuration objects with
    version management and namespace support.
    """

    def __init__(self, configer: Configer):
        config_storage_cfg = configer.value.get("CONFIG_STORAGE", {})

        self.persist: bool = config_storage_cfg.get("persist", False)
        self.root_package_name: str = (
            configer.value.get("PACKAGE_PATH_INFO", {}).get("ROOT_PACKAGE", "default_package")
        )

        self.loader: Optional[BaseConfigLoader] = self._try_load_custom_loader(configer)
        if not self.loader:
            # 如果没有用户自定义，检查 CONFIG_STORAGE.type
            loader_type = config_storage_cfg.get("type", "DB")
            loader_cls = BUILTIN_LOADERS.get(loader_type)
            if not loader_cls:
                raise ValueError(f"Unknown config loader type: {loader_type}")

            self.loader = loader_cls(configer)

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------

    def load_from_storage(self, ctx: StorageContext) -> Configer:
        """
        Load configuration into a Configer instance from storage.
        """
        self.loader.load(ctx)
        return ctx.configer

    def persist_to_storage(self, ctx: StorageContext) -> None:
        """
        Persist a Configer instance into storage if persistence is enabled.
        """
        if not self.persist:
            return

        self.loader.save(ctx)

    def delete_from_storage(self, ctx: StorageContext) -> None:

        if not ctx.trimmed_path:
            raise ConfigStorageError(f"Invalid configer path: {ctx.trimmed_path}")

        self.loader.delete(ctx)

    # ----------------------------------------------------------------------
    # Internal Helpers
    # ----------------------------------------------------------------------

    def _try_load_custom_loader(self, configer: Configer) -> Optional[BaseConfigLoader]:
        """
        Try to load user-defined ConfigLoader from EXTENSION_MODULES.class_list.
        """
        ext_classes = configer.value.get("EXTENSION_MODULES", {}).get("class_list", [])
        if not isinstance(ext_classes, list):
            return None

        for ext_class in ext_classes:
            module_path, _, class_name = ext_class.rpartition('.')
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            if not cls:
                continue
            if issubclass(cls, BaseConfigLoader):
                return cls(configer)
        return None



class ConfigStorageError(Exception):
    """Base exception for config storage errors."""


class ConfigNotFoundError(ConfigStorageError):
    """Raised when a configuration is not found in storage."""


class InstanceLoadError(Exception):
    """Raised when a component instance cannot be loaded."""
