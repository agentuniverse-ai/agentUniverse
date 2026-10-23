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
from sqlalchemy import Integer, String, DateTime, Text, Column, Index, and_, func

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
        message = Column(Text)
        gmt_created = Column(DateTime, default=func.now())

        __table_args__ = (
            Index('idx_session_id_source', 'session_id', 'agent_id', 'source'),
            Index('idx_agent_id_source', 'agent_id', 'source'),
            Index('idx_gmt_created', 'gmt_created'),
        )

    return MemoryModel


class DefaultMemoryConverter(BaseMemoryConverter):
    """The default memory converter for SqlAlchemyMemory."""

    def __init__(self, table_name: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.model_class = create_memory_model(table_name, declarative_base())

    def from_sql_model(self, sql_message: Any) -> Message:
        """Convert a SQLAlchemy model to a Message instance."""
        return Message.from_dict({'id': sql_message.id, **json.loads(sql_message.message)})

    def to_sql_model(self, message: Message, session_id: str = None, agent_id: str = None, source: str = None) -> Any:
        """Convert a Message instance to a SQLAlchemy model."""
        return self.model_class(
            session_id=session_id, agent_id=agent_id, source=source,
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
        """Create the db table if it does not exist."""
        with self._sqldb_wrapper.sql_database._engine.connect() as conn:
            if not conn.dialect.has_table(conn, self.sqldb_table_name):
                self.memory_converter.get_sql_model_class().__table__.create(conn)

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
            top_k (int): The number of messages to get.
            source (str): The source of the messages to get.

        Returns:
            List[Message]: The list of messages retrieved from the memory.
        """
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
            if kwargs.get('type'):
                if isinstance(kwargs['type'], list):
                    types = kwargs['type']
                if not isinstance(kwargs['type'], str):
                    types = [kwargs['type']]
                type_col = getattr(model_class, 'type')
                conditions.append(conditions.append(type_col.in_(types)))

            # build the query with dynamic conditions
            query = session.query(self.memory_converter.model_class)
            if conditions:
                query = query.where(and_(*conditions))
            query = query.order_by(model_class.gmt_created.asc())

            # Execute the query and fetch the results
            records = query.all()

            records = records[-top_k:]

            messages = []
            for record in records:
                messages.append(self.memory_converter.from_sql_model(record))
            return messages
