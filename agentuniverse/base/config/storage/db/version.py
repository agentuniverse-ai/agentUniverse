# -*- coding:utf-8 -*-
"""
版本控制逻辑
"""

import hashlib
import json

from sqlalchemy import and_

from .audit import AuditObserver
from .models import Config, ConfigVersion


class ConfigVersionManager:
    def __init__(self, session_maker):
        """
        session_maker: sqlalchemy.orm.sessionmaker 实例
        """
        self.session_maker = session_maker
        self._observers = []

    def register_observer(self, observer: AuditObserver):
        self._observers.append(observer)

    def _notify_observers(self, action: str, config: Config, operator: str, detail: str = None):
        for obs in self._observers:
            obs.notify(action, config, operator, detail)


    def load_config(self, tenant_id: int, name: str, namespace: str, config_type: str,
                    is_gray: int = 0, gray_name: str = None, version: int = None) -> dict:
        session = self.session_maker()
        try:
            filters = [
                Config.tenant_id == tenant_id,
                Config.name == name,
                Config.namespace == namespace,
                Config.config_type == config_type,
                Config.is_gray == is_gray,
                Config.is_deleted == 0
            ]
            if gray_name:
                filters.append(Config.gray_name == gray_name)
            if version is None:
                config = session.query(Config).filter(and_(*filters)).first()
                return config.content if config else None
            else:
                config_main = session.query(Config).filter(and_(*filters)).first()
                if not config_main:
                    return {}
                config_ver = session.query(ConfigVersion).filter(
                    and_(
                        ConfigVersion.config_id == config_main.id,
                        ConfigVersion.version == version
                    )
                ).first()
                return config_ver.content if config_ver else {}
        finally:
            session.close()


    def _calc_md5(self, content) -> str:
        """
        支持str和dict，dict时先json序列化。
        """
        if content is None:
            return None
        if isinstance(content, dict):
            content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        else:
            content_str = str(content)
        return hashlib.md5(content_str.encode('utf-8')).hexdigest()

    ## TODO: 需要考虑灰度发布的逻辑、需考虑加密

    def save_config(self, tenant_id: int, name: str, namespace: str, config_type: str,
                    content: dict, is_gray: int = 0, gray_name: str = None,
                    gray_rule: str = None, description: str = None, encrypted_data_key: str = None):
        session = self.session_maker()
        try:
            filters = [
                Config.tenant_id == tenant_id,
                Config.name == name,
                Config.namespace == namespace,
                Config.is_gray == is_gray,
                Config.is_deleted == 0
            ]
            if gray_name:
                filters.append(Config.gray_name == gray_name)
            config = session.query(Config).filter(and_(*filters)).first()
            new_md5 = self._calc_md5(content)
            operator = str(tenant_id)
            if config:
                if config.md5 == new_md5:
                    self._notify_observers('noop', config, operator, detail='内容未变，无需更新')
                    return
                config_version = ConfigVersion(
                    config_id=config.id,
                    tenant_id=tenant_id,
                    namespace=namespace,
                    version=config.version,
                    content=config.content,
                    md5=config.md5,
                    encrypted_data_key=config.encrypted_data_key,
                    is_gray=config.is_gray,
                    gray_name=config.gray_name,
                    gray_rule=config.gray_rule,
                    operator=operator,
                    operation_type='update'
                )
                session.add(config_version)
                config.content = content
                config.md5 = new_md5
                config.encrypted_data_key = encrypted_data_key
                config.gray_rule = gray_rule
                config.description = description
                config.version = config.version + 1
                self._notify_observers('update', config, operator, detail='配置更新')
            else:
                config = Config(
                    tenant_id=tenant_id,
                    name=name,
                    namespace=namespace,
                    config_type=config_type,
                    content=content,
                    md5=new_md5,
                    encrypted_data_key=encrypted_data_key,
                    is_gray=is_gray,
                    gray_name=gray_name,
                    gray_rule=gray_rule,
                    description=description,
                    version=1,
                    is_deleted=0
                )
                session.add(config)
                session.flush()
                config_version = ConfigVersion(
                    config_id=config.id,
                    tenant_id=tenant_id,
                    namespace=namespace,
                    version=1,
                    content=content,
                    md5=new_md5,
                    encrypted_data_key=encrypted_data_key,
                    is_gray=is_gray,
                    gray_name=gray_name,
                    gray_rule=gray_rule,
                    operator=operator,
                    operation_type='create'
                )
                session.add(config_version)
                self._notify_observers('create', config, operator, detail='新建配置')
            session.commit()
        finally:
            session.close()

    def delete_config(self, param):
        pass
