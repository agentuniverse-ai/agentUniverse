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

    # def sync_configer(self, config_file_str: str, config_type: ComponentEnum) -> Configer:
    #     """
    #     Get a Configer instance, syncing with storage if necessary.
    #
    #     - If local config is empty → load from storage.
    #     - Otherwise → persist local config into storage.
    #
    #     Args:
    #         config_type: Type of the configer.
    #         config_file_str: Path string of the config file.
    #
    #     Returns:
    #         Configer: The synced Configer instance.
    #     """
    #     configer = Configer(path=config_file_str).load()
    #     ctx = self._build_context(configer, config_type)
    #     if not configer.value:
    #         self.load_from_storage(ctx)
    #     elif self.persist:
    #         self.persist_to_storage(ctx)
    #     return ctx.configer

    def load_from_storage(self, ctx: StorageContext) -> Configer:
        """
        Load configuration into a Configer instance from storage.
        """
        # path = self._check_and_trim_path(configer.path)
        # if not ctx.trimmed_path:
        # raise ConfigStorageError(f"Invalid configer path: {ctx.trimmed_path}")

        value = self.loader.load(ctx)
        # if not value:
        # raise ConfigNotFoundError(f"Config not found in storage for path={ctx.trimmed_path}")
        ctx.configer.value = value
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

    def _check_and_trim_path(self, path: str) -> Optional[str]:
        """
        Ensure path contains root_package_name, and return trimmed path.
        """
        idx = path.find(self.root_package_name)
        return None if idx == -1 else path[idx:]

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

    # def build_context(self, instance_code: str, configer: Configer, config_type: ComponentEnum) -> StorageContext:
    #     trimmed = self._check_and_trim_path(configer.path)
    #     return StorageContext(
    #         raw_path=configer.path,
    #         instance_code=instance_code,
    #         trimmed_path=trimmed,
    #         configer_type=config_type,
    #         configer=configer,
    #         metadata={}
    #     )

    # def build_context(self, instance_code: str, config_type: ComponentEnum) -> StorageContext:
    #     return StorageContext(
    #         instance_code=instance_code,
    #         configer_type=config_type,
    #         metadata={}
    #     )


class ConfigStorageError(Exception):
    """Base exception for config storage errors."""


class ConfigNotFoundError(ConfigStorageError):
    """Raised when a configuration is not found in storage."""


class InstanceLoadError(Exception):
    """Raised when a component instance cannot be loaded."""
