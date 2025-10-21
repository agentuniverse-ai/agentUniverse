import hashlib
import json
from typing import Optional, Dict, Any

from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

from .models import Config, ConfigVersion


class ConfigVersionManager:
    """Manager class for handling configuration version control."""

    def __init__(self, session_maker: sessionmaker):
        """
        Initialize ConfigVersionManager.

        Args:
            session_maker (sessionmaker): SQLAlchemy sessionmaker instance.
        """
        self.session_maker = session_maker

    def load_config(
            self,
            name: str,
            namespace: str,
            config_type: str,
            version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load configuration by name, namespace, type, and optional version.

        Returns:
            dict | None: {
                "content": dict,
                "config_path": str
            } or None if not found.
        """
        session = self.session_maker()
        try:
            filters = [
                Config.name == name,
                Config.namespace == namespace,
                Config.config_type == config_type,
                Config.is_deleted == 0
            ]
            config_main = session.query(Config).filter(and_(*filters)).first()
            if not config_main:
                return None

            if version is None:
                return {
                    "content": config_main.content,
                    "config_path": config_main.config_path,
                }

            config_ver = (
                session.query(ConfigVersion)
                .filter(
                    ConfigVersion.config_id == config_main.id,
                    ConfigVersion.version == version,
                )
                .first()
            )
            if not config_ver:
                return None

            return {
                "content": config_ver.content,
                "config_path": config_ver.config_path,
            }
        finally:
            session.close()

    @staticmethod
    def _calc_md5(content: Any) -> Optional[str]:
        """
        Calculate MD5 hash of given content.

        Args:
            content (str | dict | Any): Content to calculate MD5.

        Returns:
            str | None: MD5 string, or None if content is None.
        """
        if content is None:
            return None
        if isinstance(content, dict):
            content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        else:
            content_str = str(content)
        return hashlib.md5(content_str.encode("utf-8")).hexdigest()

    def save_config(
            self,
            name: str,
            namespace: str,
            config_type: str,
            config_path: str,
            content: Dict[str, Any],
            description: Optional[str] = None,
    ) -> None:
        """
        Save or update configuration with versioning.

        If config exists and content is different, create a new version.
        Otherwise, insert a new config record.

        Args:
            name (str): Config name.
            namespace (str): Config namespace.
            config_type (str): Config type.
            config_path (str): Path of config file or source.
            content (dict): Configuration content.
            description (str, optional): Description for the config.
        """
        session = self.session_maker()
        try:
            filters = [
                Config.name == name,
                Config.namespace == namespace,
                Config.is_deleted == 0,
            ]
            config = session.query(Config).filter(and_(*filters)).first()
            new_md5 = self._calc_md5(content)

            if config:
                # Check if content is unchanged
                if config.md5 == new_md5:
                    return

                # Save previous version
                config_version = ConfigVersion(
                    config_id=config.id,
                    namespace=namespace,
                    name=config.name,
                    version=config.version,
                    content=config.content,
                    config_path=config.config_path,
                    config_type=config.config_type,
                    md5=config.md5,
                    operation_type="update",
                )
                session.add(config_version)

                # Update main config
                config.content = content
                config.md5 = new_md5
                config.description = description
                config.version += 1

            else:
                # Create new config
                config = Config(
                    name=name,
                    namespace=namespace,
                    config_type=config_type,
                    config_path=config_path,
                    content=content,
                    md5=new_md5,
                    description=description,
                    version=1,
                    is_deleted=0,
                )
                session.add(config)
                session.flush()  # Ensure config.id is available

                # Save version record
                # config_version = ConfigVersion(
                #     config_id=config.id,
                #     namespace=namespace,
                #     name=name,
                #     config_type=config_type,
                #     config_path=config_path,
                #     version=1,
                #     content=content,
                #     md5=new_md5,
                #     operation_type="create",
                # )
                # session.add(config_version)

            session.commit()
        finally:
            session.close()

    def delete_config(self, param: Any) -> None:
        """
        Delete configuration (to be implemented).

        Args:
            param (Any): Delete parameters (e.g., id, name, or condition).
        """
        pass
