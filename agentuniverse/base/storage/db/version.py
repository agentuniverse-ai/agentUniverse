# -*- coding:utf-8 -*-
"""
版本控制逻辑
"""

import hashlib
import json

from sqlalchemy import and_

from .models import Config, ConfigVersion


class ConfigVersionManager:
    def __init__(self, session_maker):
        """
        session_maker: sqlalchemy.orm.sessionmaker 实例
        """
        self.session_maker = session_maker

    def load_config(self,  name: str, namespace: str, config_type: str,
                     version: int = None) -> dict:
        session = self.session_maker()
        try:
            filters = [
                Config.name == name,
                Config.namespace == namespace,
                Config.config_type == config_type,
                Config.is_deleted == 0
            ]
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

    def save_config(self, name: str, namespace: str, config_type: str,
                    content: dict, description: str = None):
        session = self.session_maker()
        try:
            filters = [
                Config.name == name,
                Config.namespace == namespace,
                Config.is_deleted == 0
            ]

            config = session.query(Config).filter(and_(*filters)).first()
            new_md5 = self._calc_md5(content)
            if config:
                if config.md5 == new_md5:
                    return
                config_version = ConfigVersion(
                    config_id=config.id,
                    namespace=namespace,
                    version=config.version,
                    content=config.content,
                    md5=config.md5,
                    operation_type='update'
                )
                session.add(config_version)
                config.content = content
                config.md5 = new_md5
                config.description = description
                config.version = config.version + 1
            else:
                config = Config(
                    name=name,
                    namespace=namespace,
                    config_type=config_type,
                    content=content,
                    md5=new_md5,
                    description=description,
                    version=1,
                    is_deleted=0
                )
                session.add(config)
                session.flush()
                config_version = ConfigVersion(
                    config_id=config.id,
                    namespace=namespace,
                    version=1,
                    content=content,
                    md5=new_md5,
                    operation_type='create'
                )
                session.add(config_version)
            session.commit()
        finally:
            session.close()

    def delete_config(self, param):
        pass
