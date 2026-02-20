# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21
# @Author  :
# @Email   :
# @FileName: sql_database_tool.py

from typing import Optional, List

from sqlalchemy import inspect, MetaData, text
from sqlalchemy.schema import CreateTable

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager


class QuerySqlDbTool(Tool):
    """Execute a SQL query against the database and return the string result."""

    db_wrapper_name: Optional[str] = None

    def execute(self, input: str, **kwargs) -> str:
        db_wrapper = self._get_db_wrapper()
        try:
            return db_wrapper.run_with_str_return(input)
        except Exception as e:
            return f"Error: {e}"

    def _get_db_wrapper(self) -> SQLDBWrapper:
        return SQLDBWrapperManager().get_instance_obj(self.db_wrapper_name)


class ListSqlDbTool(Tool):
    """List all table names in the database, separated by commas."""

    db_wrapper_name: Optional[str] = None

    def execute(self, input: str = "", **kwargs) -> str:
        db_wrapper = self._get_db_wrapper()
        inspector = inspect(db_wrapper.engine)
        tables = inspector.get_table_names()
        return ", ".join(tables)

    def _get_db_wrapper(self) -> SQLDBWrapper:
        return SQLDBWrapperManager().get_instance_obj(self.db_wrapper_name)


class InfoSqlDbTool(Tool):
    """Get schema information (CREATE TABLE DDL and sample rows) for specified tables.

    Input should be a comma-separated list of table names.
    """

    db_wrapper_name: Optional[str] = None
    sample_rows_in_table_info: int = 3

    def execute(self, input: str, **kwargs) -> str:
        db_wrapper = self._get_db_wrapper()
        table_names = [t.strip() for t in input.split(",") if t.strip()]
        return self._get_table_info(db_wrapper, table_names)

    def _get_table_info(self, db_wrapper: SQLDBWrapper, table_names: List[str]) -> str:
        engine = db_wrapper.engine
        inspector = inspect(engine)
        available_tables = set(inspector.get_table_names())

        result_parts = []
        for table_name in table_names:
            if table_name not in available_tables:
                result_parts.append(f"Error: table '{table_name}' not found in database.")
                continue

            # Generate CREATE TABLE DDL
            metadata = MetaData()
            metadata.reflect(bind=engine, only=[table_name])
            table = metadata.tables[table_name]
            ddl = str(CreateTable(table).compile(engine))

            # Get sample rows
            sample_rows = ""
            if self.sample_rows_in_table_info > 0:
                try:
                    with engine.connect() as conn:
                        result = conn.execute(
                            text(f"SELECT * FROM \"{table_name}\" LIMIT {self.sample_rows_in_table_info}")
                        )
                        columns = list(result.keys())
                        rows = result.fetchall()
                        if rows:
                            sample_rows = (
                                f"\n\n/*\n{self.sample_rows_in_table_info} rows from "
                                f"{table_name} table:\n"
                            )
                            sample_rows += "\t".join(columns) + "\n"
                            for row in rows:
                                sample_rows += "\t".join(str(v) for v in row) + "\n"
                            sample_rows += "*/"
                except Exception:
                    pass

            result_parts.append(ddl.strip() + sample_rows)

        return "\n\n".join(result_parts)

    def _get_db_wrapper(self) -> SQLDBWrapper:
        return SQLDBWrapperManager().get_instance_obj(self.db_wrapper_name)
