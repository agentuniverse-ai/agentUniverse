#!/usr/bin/env python3
"""Provenance-aware context records for long-running agents."""

import copy
import hashlib
import json
import uuid
from contextvars import ContextVar, Token
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum, IntEnum
from typing import Any

from agentuniverse.base.annotation.singleton import singleton

# Public validation intentionally uses built-in exceptions with actionable text.
# ruff: noqa: TRY003


class ContextSource(str, Enum):
    USER = "user"
    SYSTEM = "system"
    AGENT = "agent"
    TOOL = "tool"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"


class ContextScope(IntEnum):
    TURN = 0
    TASK = 1
    SESSION = 2
    GLOBAL = 3


class AuthorityLevel(IntEnum):
    UNVERIFIED = 0
    AGENT = 10
    TOOL = 20
    USER = 30
    SYSTEM = 40


class ContextStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ContextRecord:
    """Immutable context value plus its origin, authority, and lifecycle."""

    id: str
    key: str
    value: Any
    source: ContextSource
    scope: ContextScope
    authority: AuthorityLevel
    observed_at: datetime
    confidence: float = 1.0
    actor_id: str | None = None
    expires_at: datetime | None = None
    status: ContextStatus = ContextStatus.ACTIVE
    supersedes: tuple[str, ...] = ()
    parent_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_active(self, at: datetime | None = None) -> bool:
        point = at or datetime.now(timezone.utc)
        return (
            self.status == ContextStatus.ACTIVE
            and self.observed_at <= point
            and (self.expires_at is None or self.expires_at > point)
        )

    @property
    def value_hash(self) -> str:
        try:
            payload = json.dumps(self.value, sort_keys=True, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            payload = repr(self.value)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@singleton
class ContextProvenanceManager:
    """Manage immutable provenance records in the current async context."""

    def __init__(self) -> None:
        self._records: ContextVar[tuple[ContextRecord, ...]] = ContextVar("context_provenance_records", default=())

    def add(
        self,
        key: str,
        value: Any,
        source: ContextSource | str,
        scope: ContextScope | int = ContextScope.TURN,
        authority: AuthorityLevel | int = AuthorityLevel.UNVERIFIED,
        confidence: float = 1.0,
        actor_id: str | None = None,
        observed_at: datetime | None = None,
        expires_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        supersede: bool = True,
    ) -> ContextRecord:
        """Add a record and supersede same-scope records of no greater authority."""
        normalized_key = self._key(key)
        normalized_source = self._enum(ContextSource, source, "source")
        normalized_scope = self._enum(ContextScope, scope, "scope")
        normalized_authority = self._enum(AuthorityLevel, authority, "authority")
        confidence = self._confidence(confidence)
        observed = self._datetime(observed_at or datetime.now(timezone.utc), "observed_at")
        expiry = self._datetime(expires_at, "expires_at") if expires_at is not None else None
        if expiry is not None and expiry <= observed:
            raise ValueError("expires_at must be later than observed_at")
        if actor_id is not None and (not isinstance(actor_id, str) or not actor_id.strip()):
            raise ValueError("actor_id must be a non-empty string")
        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("metadata must be an object")

        records = list(self._records.get())
        superseded_ids = []
        if supersede:
            for index, existing in enumerate(records):
                if (
                    existing.key == normalized_key
                    and existing.scope == normalized_scope
                    and existing.is_active(observed)
                    and existing.authority <= normalized_authority
                ):
                    superseded_ids.append(existing.id)
                    records[index] = replace(existing, status=ContextStatus.SUPERSEDED)
        record = ContextRecord(
            id=str(uuid.uuid4()),
            key=normalized_key,
            value=copy.deepcopy(value),
            source=normalized_source,
            scope=normalized_scope,
            authority=normalized_authority,
            observed_at=observed,
            confidence=confidence,
            actor_id=actor_id,
            expires_at=expiry,
            supersedes=tuple(superseded_ids),
            metadata=copy.deepcopy(metadata or {}),
        )
        records.append(record)
        self._records.set(tuple(records))
        return record

    def resolve(
        self,
        key: str,
        scope: ContextScope | int | None = None,
        at: datetime | None = None,
        default: Any = None,
    ) -> Any:
        """Resolve the best active value by authority, confidence, and recency."""
        records = self.active(key, scope=scope, at=at)
        if not records:
            return default
        winner = max(
            records, key=lambda item: (int(item.authority), item.confidence, item.observed_at, int(item.scope))
        )
        return copy.deepcopy(winner.value)

    def active(
        self,
        key: str | None = None,
        scope: ContextScope | int | None = None,
        at: datetime | None = None,
    ) -> list[ContextRecord]:
        normalized_key = self._key(key) if key is not None else None
        normalized_scope = self._enum(ContextScope, scope, "scope") if scope is not None else None
        point = self._datetime(at or datetime.now(timezone.utc), "at")
        return [
            item
            for item in self._records.get()
            if item.is_active(point)
            and (normalized_key is None or item.key == normalized_key)
            and (normalized_scope is None or item.scope == normalized_scope)
        ]

    def history(self, key: str | None = None) -> list[ContextRecord]:
        normalized = self._key(key) if key is not None else None
        return [item for item in self._records.get() if normalized is None or item.key == normalized]

    def conflicts(self, key: str, scope: ContextScope | int | None = None) -> list[ContextRecord]:
        records = self.active(key, scope=scope)
        return records if len({record.value_hash for record in records}) > 1 else []

    def promote(
        self,
        record_id: str,
        target_scope: ContextScope | int,
        authority: AuthorityLevel | int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ContextRecord:
        """Copy a record into a wider scope without escalating authority."""
        source_record = self.get(record_id)
        if not source_record.is_active():
            raise ValueError("only active records can be promoted")
        target = self._enum(ContextScope, target_scope, "target_scope")
        if target <= source_record.scope:
            raise ValueError("target_scope must be wider than the source scope")
        target_authority = (
            source_record.authority if authority is None else self._enum(AuthorityLevel, authority, "authority")
        )
        if target_authority > source_record.authority:
            raise ValueError("promotion cannot increase authority")
        combined_metadata = copy.deepcopy(source_record.metadata)
        combined_metadata.update(metadata or {})
        promoted = self.add(
            key=source_record.key,
            value=source_record.value,
            source=source_record.source,
            scope=target,
            authority=target_authority,
            confidence=source_record.confidence,
            actor_id=source_record.actor_id,
            observed_at=datetime.now(timezone.utc),
            expires_at=source_record.expires_at,
            metadata=combined_metadata,
        )
        updated = replace(promoted, parent_id=source_record.id)
        self._replace(updated)
        return updated

    def set_status(self, record_id: str, status: ContextStatus | str) -> ContextRecord:
        normalized = self._enum(ContextStatus, status, "status")
        record = self.get(record_id)
        if record.status != ContextStatus.ACTIVE and normalized != record.status:
            raise ValueError("terminal context records cannot change status")
        updated = replace(record, status=normalized)
        self._replace(updated)
        return updated

    def get(self, record_id: str) -> ContextRecord:
        if not isinstance(record_id, str) or not record_id:
            raise ValueError("record_id must be a non-empty string")
        for record in self._records.get():
            if record.id == record_id:
                return record
        raise KeyError(f"context provenance record not found: {record_id}")

    def snapshot(self) -> tuple[ContextRecord, ...]:
        return copy.deepcopy(self._records.get())

    def restore(self, snapshot: tuple[ContextRecord, ...]) -> Token:
        if not isinstance(snapshot, tuple) or any(not isinstance(item, ContextRecord) for item in snapshot):
            raise TypeError("snapshot must be a tuple of ContextRecord objects")
        return self._records.set(copy.deepcopy(snapshot))

    def reset(self, token: Token) -> None:
        self._records.reset(token)

    def clear(self) -> None:
        self._records.set(())

    def export(self) -> list[dict[str, Any]]:
        result = []
        for record in self._records.get():
            item = asdict(record)
            item.update(
                source=record.source.value,
                scope=record.scope.name.lower(),
                authority=record.authority.name.lower(),
                status=record.status.value,
                observed_at=record.observed_at.isoformat(),
                expires_at=record.expires_at.isoformat() if record.expires_at else None,
            )
            result.append(item)
        return result

    def _replace(self, updated: ContextRecord) -> None:
        records = list(self._records.get())
        for index, record in enumerate(records):
            if record.id == updated.id:
                records[index] = updated
                self._records.set(tuple(records))
                return
        raise KeyError(updated.id)

    @staticmethod
    def _key(value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("key must be a non-empty string")
        return value.strip()

    @staticmethod
    def _confidence(value: Any) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
            raise ValueError("confidence must be between 0 and 1")
        return float(value)

    @staticmethod
    def _datetime(value: Any, field_name: str) -> datetime:
        if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} must be a timezone-aware datetime")
        return value

    @staticmethod
    def _enum(enum_type: Any, value: Any, field_name: str) -> Any:
        try:
            if isinstance(value, str) and issubclass(enum_type, IntEnum):
                return enum_type[value.upper()]
            return enum_type(value)
        except (KeyError, TypeError, ValueError) as exc:
            choices = ", ".join(str(item.value) for item in enum_type)
            raise ValueError(f"{field_name} must be one of: {choices}") from exc
