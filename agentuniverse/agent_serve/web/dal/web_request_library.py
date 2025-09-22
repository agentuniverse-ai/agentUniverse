#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: webrequest_library.py
import datetime

from sqlalchemy import JSON, Integer, String, DateTime, Text, Column, select
from sqlalchemy.orm import declarative_base, sessionmaker

from agentuniverse.base.util.system_util import get_project_root_path
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import \
    SQLDBWrapperConfiger
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

Base = declarative_base()


class WebRequestORM(Base):
    """Web请求ORM类"""
    __tablename__ = 'web_service_requests'
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


@singleton
class WebRequestLibrary:
    """Web请求数据库访问类"""

    def __init__(self, configer: Configer = None):
        """初始化数据库连接"""
        system_db_uri = None
        if configer:
            system_db_uri = configer.get('DB', {}).get('system_db_uri')
            if not system_db_uri:
                system_db_uri = configer.get('DB', {}).get('mysql_uri')

        if system_db_uri and system_db_uri.strip():
            pass
        else:
            db_path = get_project_root_path() / 'intelligence' / 'db' / 'agent_universe_web.db'
            db_path.parent.mkdir(parents=True, exist_ok=True)
            system_db_uri = f'sqlite:///{db_path}'

        self.update_interval = configer.get('DB', {}).get('update_interval', 5) if configer else 5
        self.request_table_name = 'web_service_requests'

        # 创建独立的数据库连接
        _configer = SQLDBWrapperConfiger()
        _configer.db_uri = system_db_uri
        self.sqldb_wrapper = SQLDBWrapper(
            name="__web_system_db__",
            db_wrapper_configer=_configer
        )
        SQLDBWrapperManager().register(self.sqldb_wrapper.get_instance_code(),
                                       self.sqldb_wrapper)

        self.session = None
        self.__init_request_table()

    def __init_request_table(self):
        """初始化数据库表"""
        with self.sqldb_wrapper.sql_database._engine.connect() as conn:
            if not conn.dialect.has_table(conn, self.request_table_name):
                Base.metadata.create_all(self.sqldb_wrapper.sql_database._engine)

    def get_session(self):
        """获取数据库会话"""
        if not self.session:
            self.session = self.sqldb_wrapper.get_session()
        return self.session()

    def query_request_by_request_id(self, request_id: str):
        """根据request_id查询请求"""
        session = self.get_session()
        try:
            result = session.execute(
                select(WebRequestORM).where(WebRequestORM.request_id == request_id)
            ).scalars().first()
            if not result:
                return None
            return self.__request_orm_to_do(result)
        finally:
            session.close()

    def add_request(self, request_do):
        """添加请求到数据库"""
        session = self.get_session()
        try:
            request_orm = WebRequestORM(**request_do.model_dump())
            session.add(request_orm)
            session.commit()
            return request_orm.id
        finally:
            session.close()

    def update_request(self, request_do):
        """更新请求数据"""
        session = self.get_session()
        try:
            db_request_do = session.query(WebRequestORM).filter(
                WebRequestORM.request_id == request_do.request_id).first()
            if db_request_do:
                update_data = request_do.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_request_do, key, value)
                session.commit()
                session.refresh(db_request_do)
        finally:
            session.close()

    def update_gmt_modified(self, request_id: str):
        """更新最后修改时间"""
        session = self.get_session()
        try:
            db_request_do = session.query(WebRequestORM).filter(
                WebRequestORM.request_id == request_id).first()
            if db_request_do:
                setattr(db_request_do, "gmt_modified", datetime.datetime.now())
                session.commit()
                session.refresh(db_request_do)
        finally:
            session.close()

    def __request_orm_to_do(self, request_orm):
        """ORM对象转换为DO对象"""
        from .entity.webrequest_do import WebRequestDO
        return WebRequestDO(
            id=request_orm.id,
            request_id=request_orm.request_id,
            session_id=request_orm.session_id,
            query=request_orm.query,
            state=request_orm.state,
            result=request_orm.result or {},
            steps=request_orm.steps or [],
            additional_args=request_orm.additional_args or {},
            gmt_create=request_orm.gmt_create,
            gmt_modified=request_orm.gmt_modified
        )
