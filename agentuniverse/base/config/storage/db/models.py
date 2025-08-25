# -*- coding:utf-8 -*-
"""
ORM模型定义
"""


from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
import datetime
import json
from sqlalchemy.types import TypeDecorator

class JSONText(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, str):
                return value
            return json.dumps(value, ensure_ascii=False)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                return json.loads(value)
            except Exception:
                return value
        return None


Base = declarative_base()

class Tenant(Base):
    __tablename__ = 'tenant'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(256))
    create_source = Column(String(32))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'), index=True)
    name = Column(String(255), nullable=False)
    namespace = Column(String(64), nullable=False)
    config_type = Column(String(50), nullable=False)
    content = Column(JSONText)
    md5 = Column(String(32), index=True)
    encrypted_data_key = Column(String(1024))
    is_gray = Column(Integer, default=0)
    gray_name = Column(String(128))
    gray_rule = Column(Text)
    description = Column(Text)
    version = Column(Integer, default=1)
    is_deleted = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class ConfigVersion(Base):
    __tablename__ = 'config_version'
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey('config.id'), index=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'), index=True)
    namespace = Column(String(64), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(JSONText)
    md5 = Column(String(32))
    encrypted_data_key = Column(String(1024))
    is_gray = Column(Integer, default=0)
    gray_name = Column(String(128))
    gray_rule = Column(Text)
    operator = Column(String(64))
    operation_type = Column(String(32))
    created_at = Column(DateTime, server_default=func.current_timestamp())

class ConfigTag(Base):
    __tablename__ = 'config_tag'
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey('config.id'), index=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'), index=True)
    namespace = Column(String(64), nullable=False)
    tag = Column(String(64), nullable=False, index=True)

class ConfigAuditLog(Base):
    __tablename__ = 'config_audit_log'
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey('config.id'), index=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'), index=True)
    namespace = Column(String(64), nullable=False)
    operator = Column(String(64))
    src_ip = Column(String(50))
    action = Column(String(32))
    detail = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
