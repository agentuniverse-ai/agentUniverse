# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/10 19:45
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: sqlite_conversation_memory_storage.py
import datetime
import json
import uuid
from abc import abstractmethod
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Integer, String, DateTime, Text, Column, Index, and_, func, or_, create_engine, Engine, insert

from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.conversation_memory.enum import ConversationMessageEnum, ConversationMessageSourceType
from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper


class BaseMemoryConverter(BaseModel):
    """ The base class for memory converter used for converting between aU Message and SQLAlchemy model.

    Attributes:
        model_class: The SQLAlchemy model class.
        model_config: The model configuration.
    """

    model_class: Any = None
    model_config = ConfigDict(protected_namespaces=())

    @abstractmethod
    def from_sql_model(self, sql_message: Any) -> ConversationMessage:
        """Convert a SQLAlchemy model to a Message instance."""
        raise NotImplementedError

    @abstractmethod
    def to_sql_model(self, message: ConversationMessage, **kwargs) -> Any:
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
        content = Column(Text)
        trace_id = Column(String(100), default='')
        source = Column(String(50), default='')
        source_type = Column(String(50), default='')
        target = Column(String(50), default='')
        target_type = Column(String(50), default='')
        type = Column(String(50), default='')
        prefix = Column(String(200), default='')
        timestamp = Column(DateTime, default=func.now())
        params = Column(Text)
        pair_id = Column(String(50), default=0)
        message_id = Column(String(100), unique=True)
        additional_args = Column(Text)

        __table_args__ = (
            Index(f"idx_{table_name}_session_id_source", 'session_id', 'source', 'source_type'),
            Index(f"idx_{table_name}_session_id_source_type", 'session_id', 'target', 'target_type'),
            Index(f"idx_{table_name}_session_id_gmt_created", 'session_id', 'timestamp'),
            Index(f"idx_{table_name}_message_id_unique", 'message_id', unique=True)
        )

    return MemoryModel


class DefaultMemoryConverter(BaseMemoryConverter):
    """The default memory converter for SqlAlchemyMemory."""

    def __init__(self, table_name: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.model_class = create_memory_model(table_name, declarative_base())

    def from_sql_model(self, sql_message: Any) -> Message:
        """Convert a SQLAlchemy model to a Message instance."""
        return ConversationMessage.from_dict({'id': sql_message.message_id,
                                              'conversation_id': sql_message.session_id,
                                              'source': sql_message.source,
                                              'source_type': sql_message.source_type,
                                              'target': sql_message.target,
                                              'target_type': sql_message.target_type,
                                              'content': sql_message.content,
                                              'metadata': {
                                                  'prefix': sql_message.prefix,
                                                  'timestamp': sql_message.timestamp,
                                                  'params': sql_message.params,
                                                  'pair_id': sql_message.pair_id,
                                                  'gmt_created': sql_message.timestamp
                                              },
                                              'type': sql_message.type,
                                              'trace_id': sql_message.trace_id,
                                              'additional_args': json.loads(sql_message.additional_args)
                                              })

    def to_sql_model(self, message: ConversationMessage, session_id: str = None, **kwargs) -> Any:
        """Convert a Message instance to a SQLAlchemy model."""
        return self.model_class(
            session_id=session_id, content=message.content,
            trace_id=message.trace_id,
            source=message.source,
            source_type=message.source_type,
            target=message.target,
            target_type=message.target_type,
            type=message.type,
            prefix=message.metadata.get('prefix'),
            timestamp=message.metadata.get('timestamp', datetime.datetime.now()),
            params=message.metadata.get('params'),
            pair_id=message.metadata.get('pair_id'),
            message_id=message.id or uuid.uuid4().hex,
            additional_args=json.dumps(message.additional_args)
        )

    def get_sql_model_class(self) -> Any:
        """Get the SQLAlchemy model class."""
        return self.model_class


class SqliteMemoryStorage(MemoryStorage):
    """SqlAlchemyMemoryStorage class that stores messages in a SQL database.

    Attributes:
        sqldb_table_name (str): The name of the table to store for the memory.
        sqldb_wrapper_name (str): The name of the SQLDBWrapper to use for the memory.
        memory_converter (BaseMemoryConverter): The memory converter to use for the memory.
        _sqldb_wrapper (SQLDBWrapper): The SQLDBWrapper instance to use for the memory.
    """

    sqldb_table_name: Optional[str] = 'memory'
    sqldb_path: Optional[str] = None
    memory_converter: BaseMemoryConverter = None
    engine: Optional[Engine] = None
    session: Optional[Any] = None

    model_config = {
        "arbitrary_types_allowed": True,  # Allow any type.
    }

    def _new_client(self):
        self.engine = create_engine(self.sqldb_path, echo=False)
        self.session = sessionmaker(bind=self.engine)
        self._init_db()

    def _initialize_by_component_configer(self,
                                          memory_storage_config: ComponentConfiger) -> 'SqlAlchemyMemoryStorage':
        """Initialize the SqlAlchemyMemoryStorage by the ComponentConfiger object.

        Args:
            memory_storage_config(ComponentConfiger): A configer contains sql_alchemy_memory_storage basic info.
        Returns:
            SqlAlchemyMemoryStorage: A SqlAlchemyMemoryStorage instance.
        """
        super()._initialize_by_component_configer(memory_storage_config)
        if getattr(memory_storage_config, 'sql_table_name', None):
            self.sqldb_table_name = memory_storage_config.sql_table_name
        if getattr(memory_storage_config, 'sqldb_path', None):
            self.sqldb_path = memory_storage_config.sqldb_path
        if self.sqldb_path is None:
            raise Exception('`sqldb_wrapper_name` is not set')
        # initialize the memory converter if not set
        if self.memory_converter is None:
            self.memory_converter = DefaultMemoryConverter(self.sqldb_table_name)
        self._new_client()
        return self

    def _init_db(self) -> None:
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        """Create the db table if it does not exist."""
        with self.engine.connect() as conn:
            if not conn.dialect.has_table(conn, self.sqldb_table_name):
                self.memory_converter.get_sql_model_class().__table__.create(conn)

    def delete(self, session_id: str = None, agent_id: str = None, trace_id: str = None, **kwargs) -> None:
        """Delete the memory from the database.

        Args:
            session_id (str): The session id of the memory to delete.
            agent_id (str): The agent id of the memory to delete.
        """
        if self.engine is None:
            self._init_db()
        if session_id is None and agent_id is None:
            return
        with self.session() as session:
            model_class = self.memory_converter.get_sql_model_class()
            query = session.query(model_class)
            # construct query based on the provided session_id and agent_id
            if session_id is not None:
                query = query.filter(getattr(model_class, 'session_id') == session_id)
            if agent_id is not None:
                source_col = getattr(model_class, 'source')
                type_col = getattr(model_class, 'type')
                source_type_col = getattr(model_class, 'source_type')
                source_condition = and_(source_col == agent_id,
                                        type_col == ConversationMessageEnum.OUTPUT.value,
                                        source_type_col == ConversationMessageSourceType.AGENT.value
                                        )
                target_col = getattr(model_class, 'target')
                target_type_col = getattr(model_class, 'target_type')

                target_condition = and_(target_col == agent_id,
                                        type_col == ConversationMessageEnum.INPUT.value,
                                        target_type_col == ConversationMessageSourceType.AGENT.value)
                agent_id_col = or_(source_condition, target_condition)

                query.filter(agent_id_col)
            if trace_id is not None:
                query.filter(getattr(model_class, 'trace_id') == trace_id)

            # execute delete and commit the session
            query.delete(synchronize_session=False)
            session.commit()

    def add(self, message_list: List[ConversationMessage], session_id: str = None, agent_id: str = None,
            **kwargs) -> None:
        """Add messages to the memory db.

        Args:
            message_list (List[Message]): The list of messages to add.
            session_id (str): The session id of the memory to add.
            agent_id (str): The agent id of the memory to add.
        """
        message_list = ConversationMessage.check_and_convert_message(message_list, session_id)
        if self.engine is None:
            self._init_db()
        if message_list is None:
            return

        with self.session() as session:
            for message in message_list:
                existing_message = session.query(self.memory_converter.get_sql_model_class()).filter_by(
                    message_id=message.id).first()
                if not existing_message:
                    session.add(self.memory_converter.to_sql_model(message=message,
                                                                   session_id=session_id if session_id else None,
                                                                   agent_id=agent_id, **kwargs))
            session.commit()

    def get(self, session_id: str = None, agent_id: str = None, top_k=20, trace_id: str = None, **kwargs) -> List[
        ConversationMessage]:
        """Get messages from the memory db.

        Args:
            session_id (str): The session id of the memory to get.
            agent_id (str): The agent id of the memory to get.
            top_k (int): The number of messages to get.

        Returns:
            List[Message]: The list of messages retrieved from the memory.
        """
        if self.session is None:
            self._init_db()
        with self.session() as session:
            # get the messages from the memory by session_id and agent_id
            model_class = self.memory_converter.get_sql_model_class()
            conditions = []

            # conditionally add session_id to the query
            if session_id:
                session_id_col = getattr(model_class, 'session_id')
                conditions.append(session_id_col == session_id)

            source_col = getattr(model_class, 'source')
            type_col = getattr(model_class, 'type')
            agent_type_col = getattr(model_class, 'source_type')
            target_col = getattr(model_class, 'target')
            target_agent_type_col = getattr(model_class, 'target_type')
            if 'type' in kwargs:
                memory_type_col = getattr(model_class, 'type')
                if isinstance(kwargs['type'], list):
                    conditions.append(memory_type_col.in_(kwargs['type']))
                elif isinstance(kwargs['type'], str):
                    conditions.append(type_col == kwargs['type'])
                else:
                    raise ValueError("type must be a list or str")
            if agent_id:
                agent_qa_col = and_(target_col == agent_id,
                                    target_agent_type_col == ConversationMessageSourceType.AGENT.value)
                if kwargs.get("memory_types", None) and len(kwargs["memory_types"]) > 0:
                    types_col = and_(source_col == agent_id,
                                     agent_type_col == ConversationMessageSourceType.AGENT.value,
                                     target_agent_type_col.in_(kwargs["memory_types"]))
                    conditions.append(or_(
                        types_col,
                        agent_qa_col
                    ))
                else:
                    conditions.append(agent_qa_col)
            if trace_id:
                trace_id_col = getattr(model_class, 'trace_id')
                conditions.append(trace_id_col == trace_id)
            # build the query with dynamic conditions
            query = session.query(self.memory_converter.model_class)
            if conditions:
                query = query.where(and_(*conditions))
            query = query.order_by(model_class.timestamp.asc())

            # Execute the query and fetch the results
            records = query.all()

            records = records[-top_k:]

            messages = []
            for record in records:
                messages.append(self.memory_converter.from_sql_model(record))
            return messages
