# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 17:13
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: sqldb_wrapper_config.py

from typing import Optional

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.util.system_util import parse_dynamic_str


class SQLDBWrapperConfiger(ComponentConfiger):
    """The SQLDBWrapperConfiger class, used to load and manage the sql db wrapper
    configuration."""

    _ComponentConfiger__metadata_class: Optional[str] = None
    _ComponentConfiger__metadata_module: Optional[str] = None

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the DBWrapperConfiger."""
        super().__init__(configer)
        self.__name: Optional[str] = None
        self.__description: Optional[str] = None

        self.sql_database_args: dict = {}
        self.db_uri: Optional[str] = None
        self.engine_args: dict = {}

        self.__set_default_meta_info()

    @property
    def name(self) -> Optional[str]:
        """Name field."""
        return self.__name

    @property
    def description(self) -> Optional[str]:
        """Description field."""
        return self.__description

    def __set_default_meta_info(self):
        """Set default instantiated class of service."""
        if not hasattr(self, "_ComponentConfiger__metadata_module") or self._ComponentConfiger__metadata_module is None:
            self._ComponentConfiger__metadata_module = "agentuniverse.database.sqldb_wrapper"
        if not hasattr(self, "_ComponentConfiger__metadata_class") or self._ComponentConfiger__metadata_class is None:
            self._ComponentConfiger__metadata_class = "SQLDBWrapper"

    def load(self) -> "SQLDBWrapperConfiger":
        """Setting property using own configer member property.

        Returns:
            SQLDBWrapperConfiger: A SQLDBWrapperConfiger instance.
        """
        return self.load_by_configer(self.configer)

    def load_by_configer(self, configer: Configer) -> "SQLDBWrapperConfiger":
        """Initialize self using given configer, get SQLDBWrapperConfiger property
        from it.
        Args:
            configer(Configer): A Configer instance.
        Returns:
            SQLDBWrapperConfiger: A SQLDBWrapperConfiger instance.
        """
        super().load_by_configer(configer)
        self.__set_default_meta_info()
        try:
            self.__name = configer.value.get("name")
            self.__description = configer.value.get("description")
            self.db_uri = parse_dynamic_str(configer.value.get("db_uri"))
            self.engine_args = dict(configer.value.get("engine_args", {}))
            self.sql_database_args = dict(configer.value.get("sql_database_args", {}))

        except Exception as e:
            raise Exception(f"Failed to parse the db wrapper configuration: {e}")
        return self
