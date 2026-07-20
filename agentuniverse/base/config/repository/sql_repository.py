"""Versioned database-backed component configuration repository."""
# ruff: noqa: TRY003
from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    and_,
    create_engine,
    func,
    select,
)
from sqlalchemy.engine import Engine

from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.repository.base import ConfigRecord


class ConfigConflictError(RuntimeError):
    pass


class ConfigNotFoundError(KeyError):
    pass


_SENSITIVE = ("password", "secret", "token", "api_key", "private_key", "credential")
_REFERENCE_PREFIXES = ("env://", "secret://", "vault://", "kms://")


def _is_secret_reference(value: Any) -> bool:
    if isinstance(value, dict):
        reference = value.get("secret_ref")
        return isinstance(reference, str) and (
            "://" in reference or reference.startswith("${")
        )
    if isinstance(value, str):
        return ((value.startswith("${") and value.endswith("}"))
                or value.startswith(_REFERENCE_PREFIXES))
    return False


def _is_sensitive_key(key: Any) -> bool:
    normalized = str(key).lower().replace("-", "_")
    return any(normalized == marker or normalized.endswith(f"_{marker}")
               for marker in _SENSITIVE)


def validate_secret_references(value: Any, path: str = "config") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "secret_ref":
                if not _is_secret_reference({"secret_ref": child}):
                    raise ValueError(f"{path}.secret_ref must be a URI-like reference")
                continue
            if _is_sensitive_key(key):
                if not _is_secret_reference(child):
                    raise ValueError(f"{path}.{key} must contain a secret_ref instead of a raw value")
                continue
            validate_secret_references(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_secret_references(child, f"{path}[{index}]")


class SQLConfigRepository:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.metadata = MetaData()
        self.configs = Table(
            "au_component_config", self.metadata,
            Column("component_type", String(64), primary_key=True),
            Column("name", String(255), primary_key=True),
            Column("environment", String(64), primary_key=True),
            Column("value", JSON, nullable=False),
            Column("revision", Integer, nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
            Column("updated_by", String(255), nullable=False),
        )
        self.audit = Table(
            "au_component_config_audit", self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("component_type", String(64), nullable=False),
            Column("name", String(255), nullable=False),
            Column("environment", String(64), nullable=False),
            Column("value", JSON, nullable=False),
            Column("revision", Integer, nullable=False),
            Column("action", String(32), nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
            Column("updated_by", String(255), nullable=False),
        )
        self.metadata.create_all(engine)

    @classmethod
    def from_uri(cls, uri: str) -> SQLConfigRepository:
        return cls(create_engine(uri))

    @classmethod
    def from_sqldb_wrapper(cls, wrapper) -> SQLConfigRepository:
        return cls(wrapper.sql_database._engine)

    @staticmethod
    def _record(row) -> ConfigRecord:
        data = row._mapping
        updated = data["updated_at"]
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        return ConfigRecord(data["component_type"], data["name"], data["environment"],
                            copy.deepcopy(data["value"]), data["revision"], updated, data["updated_by"])

    def get(self, component_type: str, name: str, environment: str = "default") -> ConfigRecord:
        query = select(self.configs).where(and_(
            self.configs.c.component_type == component_type,
            self.configs.c.name == name,
            self.configs.c.environment == environment,
        ))
        with self.engine.begin() as connection:
            row = connection.execute(query).first()
        if row is None:
            raise ConfigNotFoundError((component_type, name, environment))
        return self._record(row)

    def put(self, component_type: str, name: str, value: dict, *, environment: str = "default",
            expected_revision: int | None = None, updated_by: str = "system") -> ConfigRecord:
        if not component_type.strip() or not name.strip() or not environment.strip():
            raise ValueError("component_type, name and environment are required")
        if not isinstance(value, dict):
            raise TypeError("configuration value must be a dictionary")
        validate_secret_references(value)
        now = datetime.now(timezone.utc)
        key = and_(self.configs.c.component_type == component_type,
                   self.configs.c.name == name, self.configs.c.environment == environment)
        with self.engine.begin() as connection:
            current = connection.execute(select(self.configs).where(key)).first()
            if current is None:
                if expected_revision not in (None, 0):
                    raise ConfigConflictError("configuration does not exist at expected revision")
                last_revision = connection.execute(
                    select(func.max(self.audit.c.revision)).where(and_(
                        self.audit.c.component_type == component_type,
                        self.audit.c.name == name,
                        self.audit.c.environment == environment,
                    ))
                ).scalar_one_or_none() or 0
                revision = last_revision + 1
                action = "create" if last_revision == 0 else "recreate"
                connection.execute(self.configs.insert().values(
                    component_type=component_type, name=name, environment=environment,
                    value=copy.deepcopy(value), revision=revision, updated_at=now, updated_by=updated_by,
                ))
            else:
                actual = current._mapping["revision"]
                if expected_revision is not None and expected_revision != actual:
                    raise ConfigConflictError(f"expected revision {expected_revision}, found {actual}")
                revision, action = actual + 1, "update"
                result = connection.execute(self.configs.update().where(and_(key, self.configs.c.revision == actual)).values(
                    value=copy.deepcopy(value), revision=revision, updated_at=now, updated_by=updated_by,
                ))
                if result.rowcount != 1:
                    raise ConfigConflictError("configuration changed concurrently")
            connection.execute(self.audit.insert().values(
                component_type=component_type, name=name, environment=environment,
                value=copy.deepcopy(value), revision=revision, action=action,
                updated_at=now, updated_by=updated_by,
            ))
        return self.get(component_type, name, environment)

    def list(self, component_type: str | None = None,
             environment: str = "default") -> list[ConfigRecord]:
        """List one environment's current records in deterministic order."""
        query = select(self.configs).where(self.configs.c.environment == environment)
        if component_type is not None:
            query = query.where(self.configs.c.component_type == component_type)
        query = query.order_by(self.configs.c.component_type, self.configs.c.name)
        with self.engine.begin() as connection:
            rows = connection.execute(query).all()
        return [self._record(row) for row in rows]

    def delete(self, component_type: str, name: str, *, environment: str = "default",
               expected_revision: int | None = None,
               updated_by: str = "system") -> None:
        """Delete a record while retaining its last value in the audit log."""
        key = and_(self.configs.c.component_type == component_type,
                   self.configs.c.name == name,
                   self.configs.c.environment == environment)
        now = datetime.now(timezone.utc)
        with self.engine.begin() as connection:
            current = connection.execute(select(self.configs).where(key)).first()
            if current is None:
                raise ConfigNotFoundError((component_type, name, environment))
            data = current._mapping
            actual = data["revision"]
            if expected_revision is not None and expected_revision != actual:
                raise ConfigConflictError(
                    f"expected revision {expected_revision}, found {actual}"
                )
            connection.execute(self.audit.insert().values(
                component_type=component_type, name=name, environment=environment,
                value=copy.deepcopy(data["value"]), revision=actual + 1,
                action="delete", updated_at=now, updated_by=updated_by,
            ))
            result = connection.execute(
                self.configs.delete().where(and_(key, self.configs.c.revision == actual))
            )
            if result.rowcount != 1:
                raise ConfigConflictError("configuration changed concurrently")

    def history(self, component_type: str, name: str, environment: str = "default") -> list[ConfigRecord]:
        query = select(self.audit).where(and_(
            self.audit.c.component_type == component_type, self.audit.c.name == name,
            self.audit.c.environment == environment,
        )).order_by(self.audit.c.revision)
        with self.engine.begin() as connection:
            rows = connection.execute(query).all()
        return [self._record(row) for row in rows]

    def rollback(self, component_type: str, name: str, revision: int, *, environment: str = "default",
                 expected_revision: int | None = None, updated_by: str = "system") -> ConfigRecord:
        history = self.history(component_type, name, environment)
        target = next((item for item in history if item.revision == revision), None)
        if target is None:
            raise ConfigNotFoundError((component_type, name, environment, revision))
        return self.put(component_type, name, target.value, environment=environment,
                        expected_revision=expected_revision, updated_by=updated_by)

    def export(self, environment: str | None = None) -> list[dict]:
        query = select(self.configs)
        if environment:
            query = query.where(self.configs.c.environment == environment)
        query = query.order_by(self.configs.c.component_type, self.configs.c.name, self.configs.c.environment)
        with self.engine.begin() as connection:
            rows = connection.execute(query).all()
        return [{**self._record(row).__dict__} for row in rows]

    def as_configer(self, component_type: str, name: str, environment: str = "default") -> Configer:
        return self.get(component_type, name, environment).as_configer()
