"""Explicit, optimistic retention plans for the default SQL memory schema."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256

from sqlalchemy import delete, select

from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import (
    DefaultMemoryConverter,
    SqlAlchemyMemoryStorage,
)


class StaleRetentionPlan(ValueError):
    """A selected row changed or disappeared; the entire execution rolled back."""


@dataclass(frozen=True)
class RetentionPlan:
    """A bounded preview; no message content is included in its representation."""

    session_id: str
    agent_id: str
    before: datetime | None
    keep_last: int
    candidate_ids: tuple[int, ...]
    _fingerprints: tuple[str, ...] = field(repr=False)
    _owner: object = field(repr=False, compare=False)


@dataclass(frozen=True)
class RetentionReceipt:
    """IDs deleted in one committed transaction, scoped to one session/agent."""

    session_id: str
    agent_id: str
    deleted_ids: tuple[int, ...]


class SQLMemoryRetention:
    """Preview then explicitly execute retention on default SQL memory rows.

    No scheduler, background deletion or global scope is installed. Stored
    naive timestamps are interpreted as UTC; configure the DB accordingly.
    Plans belong to this service instance and cannot be reused after success.
    """

    def __init__(self, storage: SqlAlchemyMemoryStorage):
        if not isinstance(storage, SqlAlchemyMemoryStorage):
            raise TypeError("storage must be SqlAlchemyMemoryStorage")
        if type(storage.memory_converter) is not DefaultMemoryConverter:
            raise ValueError("retention requires the default memory converter")
        if storage._sqldb_wrapper is None:
            storage._init_db()
        self._sessions = storage._sqldb_wrapper.get_session()
        self._model = storage.memory_converter.get_sql_model_class()
        self._plans = {}

    @staticmethod
    def _scope(value):
        if type(value) is not str or not value.strip() or len(value) > 100:
            raise ValueError("session_id and agent_id must be explicit nonempty strings")

    @staticmethod
    def _integer(value, name, minimum):
        if type(value) is not int or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")

    @staticmethod
    def _fingerprint(row):
        return sha256(
            json.dumps(
                [
                    row.id,
                    row.session_id,
                    row.agent_id,
                    row.source,
                    row.message,
                    row.gmt_created.isoformat() if row.gmt_created else None,
                ],
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()

    def preview(
        self,
        *,
        session_id: str,
        agent_id: str,
        before: datetime | None = None,
        keep_last: int = 0,
        max_rows: int = 10000,
        max_candidates: int = 1000,
    ) -> RetentionPlan:
        """Select old rows outside the newest ``keep_last`` without deleting.

        If supplied, ``before`` must be timezone-aware and is exclusive. Both
        age and keep-last constraints must hold. At least one constraint is
        required. Equal timestamps are ordered by ascending integer row ID.
        Over-budget scopes fail instead of returning a misleading partial plan.
        """
        self._scope(session_id)
        self._scope(agent_id)
        self._integer(keep_last, "keep_last", 0)
        self._integer(max_rows, "max_rows", 1)
        self._integer(max_candidates, "max_candidates", 1)
        if before is None and keep_last == 0:
            raise ValueError("provide before or a positive keep_last")
        if before is not None:
            if not isinstance(before, datetime) or before.utcoffset() is None:
                raise ValueError("before must be a timezone-aware datetime")
            before = before.astimezone(timezone.utc).replace(tzinfo=None)
        model = self._model
        with self._sessions() as session:
            rows = (
                session.execute(
                    select(model)
                    .where(
                        model.session_id == session_id,
                        model.agent_id == agent_id,
                    )
                    .order_by(model.gmt_created.desc(), model.id.desc())
                    .limit(max_rows + 1)
                )
                .scalars()
                .all()
            )
            if len(rows) > max_rows:
                raise ValueError("scope exceeds max_rows")
            if any(row.gmt_created is None for row in rows):
                raise ValueError("scope contains unknown timestamps")
            selected = [row for row in rows[keep_last:] if before is None or row.gmt_created < before]
            if len(selected) > max_candidates:
                raise ValueError("selection exceeds max_candidates")
            selected.reverse()
            owner = object()
            plan = RetentionPlan(
                session_id,
                agent_id,
                before,
                keep_last,
                tuple(row.id for row in selected),
                tuple(self._fingerprint(row) for row in selected),
                owner,
            )
            self._plans[owner] = plan
            return plan

    def discard(self, plan: RetentionPlan) -> None:
        """Release a preview that will not be executed."""
        if self._plans.get(plan._owner) is not plan:
            raise ValueError("unknown or consumed retention plan")
        del self._plans[plan._owner]

    def execute(self, plan: RetentionPlan) -> RetentionReceipt:
        """Delete exactly the previewed, unchanged rows in one transaction.

        New rows are never selected during execution. Any missing or changed
        candidate aborts the whole transaction. SQL errors also roll back;
        there is no automatic retry. A plan is consumed on every attempt.
        """
        if not isinstance(plan, RetentionPlan) or self._plans.get(plan._owner) is not plan:
            raise ValueError("unknown or consumed retention plan")
        del self._plans[plan._owner]
        model = self._model
        with self._sessions.begin() as session:
            for row_id, fingerprint in zip(plan.candidate_ids, plan._fingerprints):
                row = session.execute(
                    select(model)
                    .where(
                        model.id == row_id,
                        model.session_id == plan.session_id,
                        model.agent_id == plan.agent_id,
                    )
                    .with_for_update()
                ).scalar_one_or_none()
                if row is None or self._fingerprint(row) != fingerprint:
                    raise StaleRetentionPlan("candidate changed; preview again")
                # Atomic compare-and-delete also protects SQLite, whose dialect
                # does not implement SELECT FOR UPDATE.
                result = session.execute(
                    delete(model)
                    .where(
                        model.id == row_id,
                        model.session_id == plan.session_id,
                        model.agent_id == plan.agent_id,
                        model.message == row.message,
                        model.source == row.source,
                        model.gmt_created == row.gmt_created,
                    )
                    .execution_options(synchronize_session=False)
                )
                if result.rowcount != 1:
                    raise StaleRetentionPlan("candidate changed; preview again")
        return RetentionReceipt(plan.session_id, plan.agent_id, plan.candidate_ids)
