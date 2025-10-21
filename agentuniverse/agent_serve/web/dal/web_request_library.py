#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: webrequest_library.py
import datetime

from sqlalchemy import JSON, Integer, String, DateTime, Text, Column
from sqlalchemy import select
from sqlalchemy.orm import declarative_base

from .entity.web_request_do import WebRequestDO
from agentuniverse.base.util.system_util import get_project_root_path
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import \
    SQLDBWrapperConfiger
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

# 使用正确的表名
REQUEST_TABLE_NAME = 'request_task'
Base = declarative_base()


@singleton
class WebRequestLibrary:
    """Web请求数据库访问类"""

    def __init__(self, configer: Configer = None):
        """初始化数据库连接，使用配置文件中的uri或默认使用sqlite"""
        system_db_uri = None
        if configer:
            system_db_uri = configer.get('DB', {}).get('system_db_uri')
            if not system_db_uri:
                system_db_uri = configer.get('DB', {}).get('mysql_uri')
        if system_db_uri and system_db_uri.strip():
            pass
        else:
            # 使用独立的web数据库文件
            db_path = get_project_root_path() / 'intelligence' / 'db' / 'agent_universe_web.db'
            db_path.parent.mkdir(parents=True, exist_ok=True)
            system_db_uri = f'sqlite:///{db_path}'

        self.update_interval = configer.get('DB', {}).get('update_interval', 5) if configer else 5

        # 定义系统表名
        request_table_name = configer.get('DB', {}).get('request_table_name', REQUEST_TABLE_NAME)
        self.request_table_name = request_table_name

        class WebRequestORM(Base):
            """SQLAlchemy ORM Model for WebRequestDO."""
            __tablename__ = request_table_name
            id = Column(Integer, primary_key=True, autoincrement=True)
            request_id = Column(String(50), nullable=False)
            query = Column(Text)
            session_id = Column(String(50))
            service_id = Column(String(50))
            title = Column(Text)
            state = Column(String(20))
            result = Column(JSON)
            steps = Column(JSON)
            additional_args = Column(JSON)
            gmt_create = Column(DateTime, default=datetime.datetime.now)
            gmt_modified = Column(DateTime, default=datetime.datetime.now,
                                  onupdate=datetime.datetime.now)

        self.request_orm = WebRequestORM

        self.session = None
        # 创建sqldb_wrapper实例
        _configer = SQLDBWrapperConfiger()
        _configer.db_uri = system_db_uri
        self.sqldb_wrapper = SQLDBWrapper(
            name="__web_system_db__",
            db_wrapper_configer=_configer
        )
        SQLDBWrapperManager().register(self.sqldb_wrapper.get_instance_code(),
                                       self.sqldb_wrapper)

    def __init_request_table(self):
        """初始化数据库表"""
        with self.sqldb_wrapper.sql_database._engine.connect() as conn:
            if not conn.dialect.has_table(conn, self.request_table_name):
                Base.metadata.create_all(self.sqldb_wrapper.sql_database._engine)

    def get_session(self):
        """获取数据库会话"""
        if not self.session:
            self.__init_request_table()
            self.session = self.sqldb_wrapper.get_session()
        return self.session()

    def query_request_by_request_id(self, request_id: str) -> WebRequestDO | None:
        """根据request_id查询请求

        Args:
            request_id(`str`): 请求的唯一ID

        Return:
            目标WebRequestDO或None（如果不存在）
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

    def add_request(self, request_do: WebRequestDO) -> int:
        """添加请求到数据库

        Args:
            request_do(`WebRequestDO`): 要添加的新WebRequestDO

        Return:
            表中唯一的数据ID
        """
        session = self.get_session()
        try:
            request_orm = self.request_orm(**request_do.model_dump())
            session.add(request_orm)
            session.commit()
            return request_orm.id
        finally:
            session.close()

    def update_request(self, request_do: WebRequestDO):
        """使用给定的WebRequestDO更新具有相同request_id的请求数据"""
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
        """更新请求任务的最新活动时间"""
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

    def __request_orm_to_do(self, request_orm) -> WebRequestDO:
        """将WebRequestORM转换为WebRequestDO"""
        request_obj = WebRequestDO(
            request_id='',
            session_id="",
            service_id="",
            title="",
            query='',
            state='',
            result=dict(),
            steps=[],
            additional_args=dict(),
            gmt_create=datetime.datetime.now(),
            gmt_modified=datetime.datetime.now(),
        )
        for column in request_orm.__table__.columns:
            setattr(request_obj, column.name, getattr(request_orm, column.name))
        return request_obj