# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 19:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: message_library.py
import datetime

from sqlalchemy import JSON, Integer, String, DateTime, Column, Index, asc
from sqlalchemy.orm import declarative_base

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager
from agentuniverse_product.dal.model.message_do import MessageDO

MESSAGE_TABLE_NAME = 'message'
Base = declarative_base()


class MessageORM(Base):
    """Sqlalchemy orm Model for message table."""
    __tablename__ = MESSAGE_TABLE_NAME
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), nullable=False)
    content = Column(JSON)
    ext_info = Column(JSON)
    gmt_created = Column(DateTime, default=datetime.datetime.now)
    gmt_modified = Column(DateTime, default=datetime.datetime.now,
                          onupdate=datetime.datetime.now)
    __table_args__ = (
        Index('message_ix_session_id', 'session_id'),
    )


@singleton
class MessageLibrary:
    """Messagelibrary.
    """
    @staticmethod
    def get_db_session():
        """Get the database session."""
        system_sqldb_wrapper = SQLDBWrapperManager().get_instance_obj('__system_db__', new_instance=False)
        return system_sqldb_wrapper.get_session()()

    def add_message(self, message_do: MessageDO) -> int:
        """Add a message to the database."""
        with self.get_db_session() as db_session:
            message_orm = MessageORM(**message_do.model_dump())
            db_session.add(message_orm)
            db_session.commit()
            return message_orm.id

    def delete_messages(self, session_id: str):
        """Delete messages from the database using the provided `session_id`."""
        with self.get_db_session() as db_session:
            message_orm_list = db_session.query(MessageORM).filter(
                MessageORM.session_id == session_id)
            if message_orm_list:
                for message_orm in message_orm_list:
                    db_session.delete(message_orm)
                db_session.commit()

    def get_messages(self, session_id: str) -> list[MessageDO]:
        """Get messages from the database using the provided `session_id`."""
        with self.get_db_session() as db_session:
            message_orm_list = db_session.query(MessageORM).filter(
                MessageORM.session_id == session_id).order_by(asc(MessageORM.gmt_modified)).all()
            res = []
            if message_orm_list:
                for message_orm in message_orm_list:
                    res.append(self.__message_orm_to_do(message_orm))
            return res

    @staticmethod
    def __message_orm_to_do(message_orm: MessageORM) -> MessageDO:
        """Convert a MessageORM object to a MessageDO object."""
        message_do = MessageDO(
            session_id="",
            content='',
            ext_info=dict(),
        )
        for column in message_orm.__table__.columns:
            setattr(message_do, column.name,
                    getattr(message_orm, column.name))
        return message_do
