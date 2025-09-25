from typing import Dict, Any

from agentuniverse.base.config.configer import Configer
from agentuniverse.base.storage.db.models import Base
from agentuniverse.base.storage.db.version import ConfigVersionManager
from agentuniverse.base.storage.loader.base_config_loader import BaseConfigLoader
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker, scoped_session

from agentuniverse.base.storage.storage_context import StorageContext


class DBConfigLoader(BaseConfigLoader):
    def __init__(self, configer: Configer):
        super().__init__(configer)
        config_storage_cfg = configer.value.get("CONFIG_STORAGE", {})
        db_uri: str = config_storage_cfg.get("db_uri", "sqlite:///:memory:")
        engine_args: Dict[str, Any] = config_storage_cfg.get("engine_args", {})
        self.engine = create_engine(db_uri, **engine_args)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self.namespace: str = config_storage_cfg.get("namespace", "dev")
        self.version_manager = ConfigVersionManager(self.Session)
        self._init_schema()

    def load(self, ctx: StorageContext):
        key = self._get_key(ctx.instance_code, ctx.configer_type.value)
        value = self.version_manager.load_config(**key)
        if value:
            configer = Configer(path=value["config_path"])
            configer.value = value["content"]
            ctx.configer = configer

    def save(self, ctx: StorageContext):
        if ctx.trimmed_path is None:
            return
        key = self._get_key(ctx.instance_code, ctx.configer_type.value)
        self.version_manager.save_config(**key, content=ctx.configer.value, config_path=ctx.trimmed_path)

    def delete(self, ctx: StorageContext):
        key = self._get_key(ctx.instance_code, ctx.configer_type.value)
        self.version_manager.delete_config(**key)

    def _get_key(self, name, config_type):
        return {"name": name, "namespace": self.namespace, "config_type": config_type}

    def _init_schema(self) -> None:
        """
        Initialize database schema if not present.
        """
        inspector = inspect(self.engine)
        if not inspector.get_table_names():
            Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a SQLAlchemy session."""
        return self.Session()

    def get_engine(self):
        """Get the SQLAlchemy engine."""
        return self.engine
