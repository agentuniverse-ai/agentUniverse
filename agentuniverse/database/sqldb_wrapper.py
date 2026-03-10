# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 17:12
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: sqldb_wrapper.py

import json
from typing import Optional, Sequence, Any, Dict

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from ..base.config.application_configer.application_config_manager import (
    ApplicationConfigManager
)
from ..base.config.component_configer.configers.sqldb_wrapper_config import SQLDBWrapperConfiger
from ..base.component.component_base import ComponentBase
from ..base.component.component_enum import ComponentEnum


class SQLDBWrapper(ComponentBase):
    """A sql DB wrapper based on sqlalchemy."""

    # Basic attributes of the service class.
    component_type: ComponentEnum = ComponentEnum.SQLDB_WRAPPER
    name: Optional[str] = None
    description: Optional[str] = None
    _engine: Optional[Engine] = None
    _max_string_length: int = -1
    db_session: Optional[sessionmaker] = None
    db_wrapper_configer: Optional[SQLDBWrapperConfiger] = None

    class Config:
        arbitrary_types_allowed = True

    def get_instance_code(self) -> str:
        """Generate the full instance code from sql db wrapper name. """
        app_cfg_manager: ApplicationConfigManager = ApplicationConfigManager()
        appname = app_cfg_manager.app_configer.base_info_appname
        return f"{appname}.{self.component_type.value.lower()}.{self.name}"

    def initialize_by_component_configer(self,
                                         db_wrapper_configer: SQLDBWrapperConfiger
                                         ) -> 'SQLDBWrapper':
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

    def _execute(self, command: str) -> Sequence[Dict[str, Any]]:
        """Execute SQL command and return results as a list of dicts."""
        with self.engine.begin() as conn:
            cursor = conn.execute(text(command))
            if cursor.returns_rows:
                columns = list(cursor.keys())
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            return []

    def run(self, command: str) -> Sequence[Dict[str, Any]]:
        """
        Execute given sql command and return a result sequence.
        """
        return self._execute(command=command)

    def run_with_str_return(self, command: str) -> str:
        """
        Execute given sql command and return a str result, intended to be used
        as a part of llm input. If db wrapper's 'max_string_length' property is
        not negative, result str will be truncated.
        """
        result = self._execute(command=command)
        if not result:
            return ""
        if self._max_string_length > 0:
            result = [
                {
                    k: (v[:self._max_string_length]
                        if isinstance(v, str) and len(v) > self._max_string_length
                        else v)
                    for k, v in row.items()
                }
                for row in result
            ]
        res = [tuple(row.values()) for row in result]
        return str(res)

    @property
    def engine(self) -> Engine:
        """
        Lazy init, to ensure that database engine can be init correctly in
        separate processes like gunicorn.
        """
        if not self._engine:
            self.db_wrapper_configer.engine_args.setdefault(
                "json_serializer", lambda x: json.dumps(x, ensure_ascii=False)
            )
            sql_db_args = dict(self.db_wrapper_configer.sql_database_args)
            self._max_string_length = sql_db_args.pop("max_string_length", -1)
            # Remove langchain-specific args that are not applicable to create_engine
            sql_db_args.pop("sample_rows_in_table_info", None)
            self._engine = create_engine(
                self.db_wrapper_configer.db_uri,
                **self.db_wrapper_configer.engine_args
            )
        return self._engine

    def get_session(self):
        """
           Get a sqlalchemy session, used for operating with orm.
        """
        if self.db_session:
            return self.db_session
        # Create database engine
        self.db_session = sessionmaker(bind=self.engine)
        return self.db_session
