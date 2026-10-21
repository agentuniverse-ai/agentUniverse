# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/10 19:45
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: sql_alchemy_memory_storage.py
from abc import abstractmethod
import json
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import declarative_base
from sqlalchemy import Integer, String, DateTime, Text, Column, Index, and_, func, inspect, or_, select, text, update

from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager


class BaseMemoryConverter(BaseModel):
    """ The base class for memory converter used for converting between aU Message and SQLAlchemy model.

    Attributes:
        model_class: The SQLAlchemy model class.
        model_config: The model configuration.
    """

    model_class: Any = None
    model_config = ConfigDict(protected_namespaces=())

    @abstractmethod
    def from_sql_model(self, sql_message: Any) -> Message:
        """Convert a SQLAlchemy model to a Message instance."""
        raise NotImplementedError

    @abstractmethod
    def to_sql_model(self, message: Message) -> Any:
        """Convert a Message instance to a SQLAlchemy model."""
        raise NotImplementedError

    @abstractmethod
    def get_sql_model_class(self) -> Any:
        """Get the SQLAlchemy model class."""
        raise NotImplementedError


def create_memory_model(table_name: str, DynamicBase: Any) -> Any:
    """
    Create a memory model for a given table name.

    Args:
        table_name: The name of the table to use.
        DynamicBase: The base class to use for the model.

    Returns:
        The model class.
    """

    class MemoryModel(DynamicBase):
        """The default memory model for SqlAlchemyMemory."""
        __tablename__ = table_name
        id = Column(Integer, primary_key=True, autoincrement=True)
        session_id = Column(String(100), default='')
        agent_id = Column(String(100), default='')
        source = Column(String(500), default='')
        # Message type used to be stored only inside the JSON payload.  Keep it
        # in a dedicated column as well so ``get(type=...)`` can filter in SQL
        # instead of reading an attribute that does not exist on the model.
        type = Column(String(50), default='')
        message = Column(Text)
        gmt_created = Column(DateTime, default=func.now())

        __table_args__ = (
            Index('idx_session_id_source', 'session_id', 'agent_id', 'source'),
            Index('idx_agent_id_source', 'agent_id', 'source'),
            Index('idx_session_id_agent_id_type', 'session_id', 'agent_id', 'type'),
            Index('idx_gmt_created', 'gmt_created'),
        )

    return MemoryModel


class DefaultMemoryConverter(BaseMemoryConverter):
    """The default memory converter for SqlAlchemyMemory."""

    def __init__(self, table_name: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.model_class = create_memory_model(table_name, declarative_base())

    def from_sql_model(self, sql_message: Any) -> Message:
        """Convert a SQLAlchemy model to a Message instance.

        The dedicated ``type`` column is authoritative when it is populated.
        Rows written before the column existed only carry the type in their
        JSON payload, so fall back to it to keep those messages readable even
        if the one-time backfill has not run yet.
        """
        payload = json.loads(sql_message.message)
        persisted_type = getattr(sql_message, 'type', None)
        if persisted_type:
            payload['type'] = persisted_type
        return Message.from_dict({'id': sql_message.id, **payload})

    def to_sql_model(self, message: Message, session_id: str = None, agent_id: str = None, source: str = None) -> Any:
        """Convert a Message instance to a SQLAlchemy model."""
        return self.model_class(
            session_id=session_id, agent_id=agent_id, source=source,
            type=message.type or '',
            message=json.dumps(message.to_dict(), ensure_ascii=False)
        )

    def get_sql_model_class(self) -> Any:
        """Get the SQLAlchemy model class."""
        return self.model_class


class SqlAlchemyMemoryStorage(MemoryStorage):
    """SqlAlchemyMemoryStorage class that stores messages in a SQL database.

    Attributes:
        sqldb_table_name (str): The name of the table to store for the memory.
        sqldb_wrapper_name (str): The name of the SQLDBWrapper to use for the memory.
        memory_converter (BaseMemoryConverter): The memory converter to use for the memory.
        _sqldb_wrapper (SQLDBWrapper): The SQLDBWrapper instance to use for the memory.
    """

    sqldb_table_name: Optional[str] = 'memory'
    sqldb_wrapper_name: Optional[str] = None
    memory_converter: BaseMemoryConverter = None
    _sqldb_wrapper: SQLDBWrapper = None

    def _initialize_by_component_configer(self,
                                          memory_storage_config: ComponentConfiger) -> 'SqlAlchemyMemoryStorage':
        """Initialize the SqlAlchemyMemoryStorage by the ComponentConfiger object.

        Args:
            memory_storage_config(ComponentConfiger): A configer contains sql_alchemy_memory_storage basic info.
        Returns:
            SqlAlchemyMemoryStorage: A SqlAlchemyMemoryStorage instance.
        """
        super()._initialize_by_component_configer(memory_storage_config)
        if getattr(memory_storage_config, 'sqldb_table_name', None):
            self.sqldb_table_name = memory_storage_config.sqldb_table_name
        if getattr(memory_storage_config, 'sqldb_wrapper_name', None):
            self.sqldb_wrapper_name = memory_storage_config.sqldb_wrapper_name
        if self.sqldb_wrapper_name is None:
            raise Exception('`sqldb_wrapper_name` is not set')
        # initialize the memory converter if not set
        if self.memory_converter is None:
            self.memory_converter = DefaultMemoryConverter(self.sqldb_table_name)
        return self

    def _init_db(self) -> None:
        """Initialize the database."""
        self._sqldb_wrapper = SQLDBWrapperManager().get_instance_obj(self.sqldb_wrapper_name)
        if self._sqldb_wrapper is None:
            raise Exception('The sqldb_wrapper for the `sqldb_wrapper_name` was not found,'
                            ' please check the `sqldb_wrapper_name`.')
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        """Create the db table or upgrade an existing table's schema.

        Tables created by older releases do not have the ``type`` column, so
        the storage cannot filter summaries after an upgrade unless the column
        is added here.  ``engine.begin()`` is used instead of ``connect()`` so
        that the schema change is committed consistently on every dialect.
        """
        model_class = self.memory_converter.get_sql_model_class()
        table = model_class.__table__
        engine = self._sqldb_wrapper.sql_database._engine
        with engine.begin() as conn:
            if conn.dialect.name == 'sqlite' and isinstance(self.memory_converter, DefaultMemoryConverter):
                # SQLite's deferred transactions allow two workers to inspect
                # the same old schema before either ALTER runs. Obtain the
                # write lock before inspecting so the second worker sees the
                # completed migration instead of trying to add the column twice.
                conn.exec_driver_sql('BEGIN IMMEDIATE')
            if not conn.dialect.has_table(conn, self.sqldb_table_name):
                table.create(conn)
                return
            if isinstance(self.memory_converter, DefaultMemoryConverter):
                self._upgrade_existing_table(conn, table)

    def _upgrade_existing_table(self, conn: Any, table: Any) -> None:
        """Add missing columns/indexes and backfill data for legacy tables."""
        existing_columns = {column['name'] for column in inspect(conn).get_columns(table.name)}
        column_added = False
        if table.c.type.name not in existing_columns:
            self._add_type_column(conn, table)
            column_added = True

        # ``create`` with ``checkfirst`` keeps this method idempotent because
        # initialization can run more than once for the same storage instance
        # and every process performs it on startup.
        for index in table.indexes:
            index.create(conn, checkfirst=True)

        if column_added:
            self._backfill_type_column(conn, table)

    @staticmethod
    def _add_type_column(conn: Any, table: Any) -> None:
        """Add the ``type`` column to a table created by an older release."""
        column = table.c.type
        quoted_table = conn.dialect.identifier_preparer.quote(table.name)
        quoted_column = conn.dialect.identifier_preparer.quote(column.name)
        column_type = column.type.compile(dialect=conn.dialect)
        # Table and column names are quoted through the dialect's preparer;
        # the type is compiled from the model definition, so no user input is
        # interpolated into this DDL statement.
        conn.execute(text(
            f"ALTER TABLE {quoted_table} ADD COLUMN {quoted_column} {column_type} DEFAULT ''"
        ))

    @staticmethod
    def _backfill_type_column(conn: Any, table: Any) -> None:
        """Copy message types from the JSON payload into the new column.

        Existing deployments have summaries whose type only exists inside the
        serialized message.  Without this backfill, ``get(type='summarize')``
        would silently stop returning them after the schema upgrade.
        """
        rows = conn.execute(
            select(table.c.id, table.c.message).where(
                or_(table.c.type.is_(None), table.c.type == '')
            )
        ).all()
        for row in rows:
            try:
                payload = json.loads(row.message)
            except (TypeError, ValueError):
                # A malformed legacy payload must not prevent the storage from
                # starting; it simply has no type to copy.
                continue
            if not isinstance(payload, dict):
                continue
            message_type = payload.get('type')
            if not isinstance(message_type, str) or not message_type:
                continue
            conn.execute(
                update(table).where(table.c.id == row.id).values(type=message_type)
            )

    @staticmethod
    def _normalize_memory_types(memory_types: Any) -> List[str]:
        """Normalize the ``type`` argument accepted by :meth:`get`.

        Callers pass either a single type name (``'summarize'``) or a group of
        names (``['human', 'ai']``).  Empty values are dropped so that an
        omitted or blank filter keeps the previous "return everything"
        behaviour, while unsupported container types are rejected instead of
        being silently converted into a filter that can never match.
        """
        if memory_types is None:
            return []
        if isinstance(memory_types, str):
            return [memory_types] if memory_types else []
        if isinstance(memory_types, (list, tuple, set, frozenset)):
            return [memory_type for memory_type in memory_types if memory_type]
        raise ValueError('type must be a list or a string')

    def delete(self, session_id: str = None, agent_id: str = None, **kwargs) -> None:
        """Delete the memory from the database.

        Args:
            session_id (str): The session id of the memory to delete.
            agent_id (str): The agent id of the memory to delete.
        """
        if self._sqldb_wrapper is None:
            self._init_db()
        if session_id is None and agent_id is None:
            return
        with self._sqldb_wrapper.get_session()() as session:
            model_class = self.memory_converter.get_sql_model_class()
            query = session.query(model_class)
            # construct query based on the provided session_id and agent_id
            if session_id is not None:
                query = query.filter(getattr(model_class, 'session_id') == session_id)
            if agent_id is not None:
                query = query.filter(getattr(model_class, 'agent_id') == agent_id)

            # execute delete and commit the session
            query.delete(synchronize_session=False)
            session.commit()

    def add(self, message_list: List[Message], session_id: str = None, agent_id: str = None, **kwargs) -> None:
        """Add messages to the memory db.

        Args:
            message_list (List[Message]): The list of messages to add.
            session_id (str): The session id of the memory to add.
            agent_id (str): The agent id of the memory to add.
        """
        if self._sqldb_wrapper is None:
            self._init_db()
        if message_list is None:
            return
        with self._sqldb_wrapper.get_session()() as session:
            for message in message_list:
                session.add(
                    self.memory_converter.to_sql_model(message=message, session_id=session_id if session_id else None,
                                                       agent_id=agent_id if agent_id else None,
                                                       source=message.source if message.source else None))
            session.commit()

    def get(self, session_id: str = None, agent_id: str = None, top_k=10, source: str = None, **kwargs) -> List[
        Message]:
        """Get messages from the memory db.

        Args:
            session_id (str): The session id of the memory to get.
            agent_id (str): The agent id of the memory to get.
            top_k (int): The number of messages to get after filtering.
            source (str): The source of the messages to get.
            **kwargs: ``type`` accepts a single message type or a list of
                message types.  An empty value keeps every type; other argument
                types raise ``ValueError``.

        Returns:
            List[Message]: The list of messages retrieved from the memory.
        """
        if top_k <= 0:
            return []
        if self._sqldb_wrapper is None:
            self._init_db()
        with self._sqldb_wrapper.get_session()() as session:
            # get the messages from the memory by session_id and agent_id
            model_class = self.memory_converter.get_sql_model_class()
            conditions = []

            # conditionally add session_id to the query
            if session_id:
                session_id_col = getattr(model_class, 'session_id')
                conditions.append(session_id_col == session_id)

            # conditionally add agent_id to the query
            if agent_id:
                agent_id_col = getattr(model_class, 'agent_id')
                conditions.append(agent_id_col == agent_id)

            # conditionally add source to the query
            if source:
                source_col = getattr(model_class, 'source')
                conditions.append(source_col == source)
            # A single type is normalized to a one-element list so the SQL
            # condition is identical for both supported call styles.  An empty
            # filter (None, '' or []) intentionally keeps all message types.
            types = self._normalize_memory_types(kwargs.get('type'))
            if types:
                type_col = getattr(model_class, 'type')
                conditions.append(type_col.in_(types))

            # build the query with dynamic conditions
            query = session.query(self.memory_converter.model_class)
            if conditions:
                query = query.where(and_(*conditions))
            query = query.order_by(model_class.gmt_created.asc())

            # Execute the query and fetch the results
            records = query.all()

            # top_k is applied after the type filter so that a limit of one
            # returns the newest matching message, not the newest message of
            # any type.
            records = records[-top_k:]

            messages = []
            for record in records:
                messages.append(self.memory_converter.from_sql_model(record))
            return messages
