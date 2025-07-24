# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 15:18
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: request_library.py
import datetime

from sqlalchemy import JSON, Integer, String, DateTime, Text, Column
from sqlalchemy import select
from sqlalchemy.orm import declarative_base

from .entity.request_do import RequestDO
from agentuniverse.base.util.system_util import get_project_root_path
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import \
    SQLDBWrapperConfiger
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

REQUEST_TABLE_NAME = 'request_task'
Base = declarative_base()


@singleton
class RequestLibrary:
    def __init__(self, configer: Configer = None):
        """Init the database connection. Use uri in config file or use sqlite
        as default database."""
        system_db_uri = None
        if Configer:
            system_db_uri = configer.get('DB', {}).get('system_db_uri')
            if not system_db_uri:
                system_db_uri = configer.get('DB', {}).get('mysql_uri')
        if system_db_uri and system_db_uri.strip():
            pass
        else:
            db_path = get_project_root_path() / 'intelligence' / 'db' / 'agent_universe.db'
            db_path.parent.mkdir(parents=True, exist_ok=True)
            system_db_uri = f'sqlite:///{db_path}'
        self.update_interval = configer.get('DB', {}).get('update_interval', 5)
        # define system table name
        request_table_name = configer.get('DB', {}).get('request_table_name',
                                                        REQUEST_TABLE_NAME)
        self.request_table_name = request_table_name

        class RequestORM(Base):
            """SQLAlchemy ORM Model for RequestDO."""
            __tablename__ = request_table_name
            id = Column(Integer, primary_key=True, autoincrement=True)
            request_id = Column(String(50), nullable=False)
            query = Column(Text)
            session_id = Column(String(50))
            state = Column(String(20))
            result = Column(JSON)
            steps = Column(JSON)
            additional_args = Column(JSON)
            gmt_create = Column(DateTime, default=datetime.datetime.now)
            gmt_modified = Column(DateTime, default=datetime.datetime.now,
                                  onupdate=datetime.datetime.now)

        self.request_orm = RequestORM

        self.session = None
        # create a sqldb_wrapper_instance
        _configer = SQLDBWrapperConfiger()
        _configer.db_uri = system_db_uri
        _configer.sql_database_args = {
            'lazy_table_reflection': True
        }
        self.sqldb_wrapper = SQLDBWrapper(
            name="__system_db__",
            db_wrapper_configer=_configer
        )
        SQLDBWrapperManager().register(self.sqldb_wrapper.get_instance_code(),
                                       self.sqldb_wrapper)

    def __init_request_table(self):
        with self.sqldb_wrapper.sql_database._engine.connect() as conn:
            if not conn.dialect.has_table(conn, self.request_table_name):
                Base.metadata.create_all(
                    self.sqldb_wrapper.sql_database._engine)

    def get_session(self):
        if not self.session:
            self.__init_request_table()
            self.session = self.sqldb_wrapper.get_session()
        return self.session()

    def query_request_by_request_id(self, request_id: str) -> RequestDO | None:
        """Get a RequestDO with given request_id.

        Args:
            request_id(`str`): The unique request id of request task.

        Return:
            The target RequestDO or none when no such data.
        """
        session = self.get_session()
        try:
            result = session.execute(
                select(self.request_orm).where(self.request_orm.request_id == request_id)
            ).scalars().first()
            if not result:
                return None
            return self.__request_orm_to_do(result)
        finally:
            session.close()

    def add_request(self, request_do: RequestDO) -> int:
        """Add the given RequestDO to database.

        Args:
            request_do(`RequestDO`): A new RequestDO to be added.

        Return:
            A int stands unique data id in table.
        """
        session = self.get_session()
        try:
            request_orm = self.request_orm(**request_do.model_dump())
            session.add(request_orm)
            session.commit()
            return request_orm.id
        finally:
            session.close()

    def update_request(self, request_do: RequestDO):
        """Update the request data with same request id as the given
        RequestDO."""
        session = self.get_session()
        try:
            db_request_do = session.query(self.request_orm).filter(
                self.request_orm.request_id == request_do.request_id).first()
            if db_request_do:
                update_data = request_do.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_request_do, key, value)
                session.commit()
                session.refresh(db_request_do)
        finally:
            session.close()

    def update_gmt_modified(self, request_id: str):
        """Update the request task latest active time."""
        session = self.get_session()
        try:
            db_request_do = session.query(self.request_orm).filter(
                self.request_orm.request_id == request_id).first()
            if db_request_do:
                setattr(db_request_do, "gmt_modified", datetime.datetime.now())
                session.commit()
                session.refresh(db_request_do)
        finally:
            session.close()

    def __request_orm_to_do(self, request_orm) -> RequestDO:
        """Transfer a RequestORM to RequestDO."""
        request_obj = RequestDO(
            request_id='',
            session_id="",
            query='',
            state='',
            result=dict(),
            steps=[],
            additional_args=dict(),
            gmt_create=datetime.datetime.now(),
            gmt_modified=datetime.datetime.now(),
        )
        for column in request_orm.__table__.columns:
            setattr(request_obj, column.name,
                    getattr(request_orm, column.name))
        return request_obj
