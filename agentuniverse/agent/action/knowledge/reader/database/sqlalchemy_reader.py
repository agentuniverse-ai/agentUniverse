#!/usr/bin/env python3

# @Time    : 2025/11/3 19:58
# @Author  : sunhailin.shl
# @Email   : sunhailin.shl@antgroup.com
# @FileName: sqlalchemy_reader.py
from typing import ClassVar, Dict, Any, Optional
from pydantic import PrivateAttr

from sqlalchemy import and_, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class SQLAlchemyReader(Reader):
    """
    A data reader implementation using SQLAlchemy to load data from databases.
    """

    DIALECT_BASE_MAP: ClassVar[Dict[str, Any]] = {}

    connection_string: Optional[str] = None
    echo: bool = False

    _engine: Any = PrivateAttr()
    _session_factory: Any = PrivateAttr()
    _Base: Any = PrivateAttr()
    _db_type: str = PrivateAttr()

    def initialize_connection(self, connection_string: str, echo: bool = False):
        """
        Initialize SQLAlchemy connection and ORM base dynamically.

        Args:
            connection_string (str): Database connection URI.
            echo (bool): Whether to display SQL debug logs.
        """
        self.connection_string = connection_string
        self.echo = echo

        # init engine and session
        self._engine = create_engine(connection_string, echo=echo)
        self._session_factory = sessionmaker(bind=self._engine)

        # detect dialects then select ORM Base
        self._db_type = self._detect_db_type(connection_string)
        self._Base = self._get_declarative_base(self._db_type)

    @staticmethod
    def _detect_db_type(conn_str: str) -> str:
        """Detect DB type from connection string."""
        scheme = conn_str.split("://")[0].lower()
        if scheme.startswith("oceanbase"):
            return "oceanbase"
        elif scheme.startswith("clickhouse"):
            return "clickhouse"
        else:
            return "generic"

    def _get_declarative_base(self, db_type: str):
        """Return a proper declarative base based on db type."""
        if db_type in self.DIALECT_BASE_MAP:
            return self.DIALECT_BASE_MAP[db_type]

        if db_type == "clickhouse":
            try:
                from clickhouse_sqlalchemy import get_declarative_base
            except Exception:
                raise ImportError("Install clickhouse_sqlalchemy: "
                                  "`pip install clickhouse_sqlalchemy`")
            base = get_declarative_base()
        else:
            # Default and for oceanbase, mysql, pg etc
            base = declarative_base()

        self.DIALECT_BASE_MAP[db_type] = base
        return base

    def create_table_model(
        self,
        table_name: str,
        columns: dict[str, Any],
    ) -> type:
        """
        Dynamically create ORM table class.

        Args:
            table_name (str): Name of the table.
            columns (Dict[str, Any]): Mapping: column_name -> Column(...)
        Returns:
            ORM mapped class.
        """
        if not hasattr(self, "_Base"):
            raise RuntimeError("Connection not initialized. "
                               "Call initialize_connection() first.")
        attrs = {"__tablename__": table_name}
        attrs.update(columns)
        model = type(table_name.capitalize(), (self._Base,), attrs)
        return model

    def _load_data(
        self,
        table_cls: Any,
        filters: dict | None = None,
        join_cls: Any | None = None,
        join_condition: Any | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Document]:
        """Generic loader supporting any SQLAlchemy dialect."""
        session = self._session_factory()
        try:
            stmt = select(table_cls)

            if join_cls is not None and join_condition is not None:
                stmt = stmt.join(join_cls, join_condition)

            if filters:
                conditions = []
                for col_name, value in filters.items():
                    col_attr = getattr(table_cls, col_name)
                    conditions.append(col_attr == value)
                stmt = stmt.where(and_(*conditions))

            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)

            results = session.execute(stmt).scalars().all()

            documents = []
            for row in results:
                metadata = {col.name: getattr(row, col.name)
                            for col in row.__table__.columns}
                text = " | ".join(f"{k}: {v}" for k, v in metadata.items())
                documents.append(Document(text=text, metadata=metadata))

            return documents
        finally:
            session.close()
