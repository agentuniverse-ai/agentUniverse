# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 17:12
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: sqldb_wrapper.py

import json
from typing import Optional, Sequence, Any, Dict

from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy.orm import sessionmaker

from ..base.config.application_configer.application_config_manager import ApplicationConfigManager
from ..base.config.component_configer.configers.sqldb_wrapper_config import SQLDBWrapperConfiger
from ..base.component.component_base import ComponentBase
from ..base.component.component_enum import ComponentEnum


class SQLDBWrapper(ComponentBase):
    """A sql DB wrapper based on sqlalchemy and langchain sql database,"""

    # Basic attributes of the service class.
    component_type: ComponentEnum = ComponentEnum.SQLDB_WRAPPER
    name: Optional[str] = None
    description: Optional[str] = None
    __sql_database: Optional[SQLDatabase] = None
    db_session: Optional[sessionmaker] = None
    db_wrapper_configer: Optional[SQLDBWrapperConfiger] = None

    class Config:
        arbitrary_types_allowed = True

    def get_instance_code(self) -> str:
        """Generate the full instance code from sql db wrapper name."""
        app_cfg_manager: ApplicationConfigManager = ApplicationConfigManager()
        appname = app_cfg_manager.app_configer.base_info_appname
        return f"{appname}.{self.component_type.value.lower()}.{self.name}"

    def initialize_by_component_configer(self, db_wrapper_configer: SQLDBWrapperConfiger) -> "SQLDBWrapper":
        """Initialize the SQLDBWrapper by the ComponentConfiger object.

        Args:
            db_wrapper_configer(SQLDBWrapperConfiger): A configer contains service
            basic info.
        Returns:
            SQLDBWrapper: A SQLDBWrapper instance.
        """
        self.name = db_wrapper_configer.name
        self.description = db_wrapper_configer.description
        self.db_wrapper_configer = db_wrapper_configer
        return self

    def run(self, command: str) -> Sequence[Dict[str, Any]]:
        """
        Execute given sql command and return a result sequence.
        """
        return self.sql_database._execute(command=command)

    def run_with_str_return(self, command: str) -> str:
        """
        Execute given sql command and return a str result, intended to be used
        as a part of llm input. If db wrapper's 'max_string_length' property is
        not negative, result str will be truncated.
        """
        return self.sql_database.run(command, fetch="all")

    @property
    def sql_database(self):
        """
        Lazy init, to ensure that database engine can be init correctly in
        separate processes like gunicorn.
        """
        if not self.__sql_database:
            self.db_wrapper_configer.engine_args.setdefault(
                "json_serializer", lambda x: json.dumps(x, ensure_ascii=False)
            )
            self.db_wrapper_configer.sql_database_args.setdefault("sample_rows_in_table_info", 3)
            self.db_wrapper_configer.sql_database_args.setdefault("max_string_length", -1)
            self.__sql_database = SQLDatabase.from_uri(
                engine_args=self.db_wrapper_configer.engine_args,
                database_uri=self.db_wrapper_configer.db_uri,
                **self.db_wrapper_configer.sql_database_args,
            )
        return self.__sql_database

    def get_session(self):
        """
        Get a sqlalchemy session, used for operating with orm.
        """
        if self.db_session:
            return self.db_session
        # Create database engine
        self.db_session = sessionmaker(bind=self.sql_database._engine)
        return self.db_session
