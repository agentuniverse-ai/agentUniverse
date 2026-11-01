"""Same retention contract against real SQLite and opt-in temporary PostgreSQL."""

import os
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import event, select, update

from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import (
    DefaultMemoryConverter,
    SqlAlchemyMemoryStorage,
)
from agentuniverse.agent.memory.memory_storage.sql_memory_retention import (
    SQLMemoryRetention,
    StaleRetentionPlan,
)
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import SQLDBWrapperConfiger
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper


@pytest.fixture(params=["sqlite", "postgres"] if os.getenv("AU_RETENTION_TEST_POSTGRES") else ["sqlite"])
def database(request, tmp_path):
    config = SQLDBWrapperConfiger()
    config.db_uri = (
        os.environ["AU_RETENTION_TEST_POSTGRES"]
        if request.param == "postgres"
        else f"sqlite:///{tmp_path / 'memory.db'}"
    )
    wrapper = SQLDBWrapper(db_wrapper_configer=config)
    engine = wrapper.sql_database._engine
    schema = "retention_" + uuid4().hex
    if request.param == "postgres":
        with engine.begin() as connection:
            connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        engine = engine.execution_options(schema_translate_map={None: schema})
        from sqlalchemy.orm import sessionmaker

        wrapper.db_session = sessionmaker(bind=engine)
    converter = DefaultMemoryConverter("memory")
    converter.model_class.metadata.create_all(engine)
    storage = SqlAlchemyMemoryStorage(memory_converter=converter)
    storage._sqldb_wrapper = wrapper
    try:
        yield storage, engine
    finally:
        converter.model_class.metadata.drop_all(engine)
        if request.param == "postgres":
            with engine.begin() as connection:
                connection.exec_driver_sql(f'DROP SCHEMA "{schema}"')
        engine.dispose()


def seed(storage):
    for session, agent in [("s", "a"), ("other", "a"), ("s", "other")]:
        storage.add([Message(type="human", content=str(i)) for i in range(4)], session_id=session, agent_id=agent)
    model = storage.memory_converter.model_class
    with storage._sqldb_wrapper.get_session().begin() as session:
        rows = session.execute(select(model).order_by(model.id)).scalars().all()
        for i, row in enumerate(rows):
            row.gmt_created = datetime(2026, 1, 1) + timedelta(days=i % 4)
    return model


def ids(storage):
    model = storage.memory_converter.model_class
    with storage._sqldb_wrapper.get_session()() as session:
        return tuple(session.scalars(select(model.id).order_by(model.id)))


def test_preview_execute_scope_boundary_and_storage_readback(database):
    storage, _ = database
    seed(storage)
    service = SQLMemoryRetention(storage)
    plan = service.preview(session_id="s", agent_id="a", before=datetime(2026, 1, 3, tzinfo=timezone.utc), keep_last=1)
    assert plan.candidate_ids == (1, 2)
    assert ids(storage) == tuple(range(1, 13))
    receipt = service.execute(plan)
    assert receipt.deleted_ids == (1, 2)
    assert [m.content for m in storage.get(session_id="s", agent_id="a")] == ["2", "3"]
    assert len(storage.get(session_id="other", agent_id="a")) == 4
    assert len(storage.get(session_id="s", agent_id="other")) == 4
    with pytest.raises(ValueError, match="consumed"):
        service.execute(plan)


def test_concurrent_insert_is_excluded_even_when_backdated(database):
    storage, _ = database
    model = seed(storage)
    service = SQLMemoryRetention(storage)
    plan = service.preview(session_id="s", agent_id="a", keep_last=1)
    storage.add([Message(content="new")], session_id="s", agent_id="a")
    with storage._sqldb_wrapper.get_session().begin() as session:
        session.execute(update(model).where(model.id == 13).values(gmt_created=datetime(2000, 1, 1)))
    assert service.execute(plan).deleted_ids == (1, 2, 3)
    assert 13 in ids(storage)


@pytest.mark.parametrize("mutation", ["message", "scope", "delete"])
def test_stale_last_candidate_rolls_back_earlier_deletes(database, mutation):
    storage, _ = database
    model = seed(storage)
    service = SQLMemoryRetention(storage)
    plan = service.preview(session_id="s", agent_id="a", keep_last=1)
    with storage._sqldb_wrapper.get_session().begin() as session:
        row = session.get(model, 3)
        if mutation == "message":
            row.message = '{"content":"changed"}'
        elif mutation == "scope":
            row.session_id = "moved"
        else:
            session.delete(row)
    with pytest.raises(StaleRetentionPlan):
        service.execute(plan)
    assert {1, 2}.issubset(ids(storage))


def test_database_failure_rolls_back_whole_plan(database):
    storage, engine = database
    seed(storage)
    service = SQLMemoryRetention(storage)
    plan = service.preview(session_id="s", agent_id="a", keep_last=1)
    count = 0

    def fail_second(conn, cursor, statement, parameters, context, executemany):
        nonlocal count
        if statement.startswith("DELETE"):
            count += 1
            if count == 2:
                raise RuntimeError("injected transport failure")

    event.listen(engine, "before_cursor_execute", fail_second)
    try:
        with pytest.raises(RuntimeError):
            service.execute(plan)
    finally:
        event.remove(engine, "before_cursor_execute", fail_second)
    assert ids(storage) == tuple(range(1, 13))


@pytest.mark.parametrize(
    "extra",
    [
        {"session_id": ""},
        {"agent_id": None},
        {"keep_last": True},
        {"before": datetime(2026, 1, 1)},
        {"max_rows": 0},
        {"max_candidates": -1},
    ],
)
def test_invalid_scope_and_policy_rejected(database, extra):
    storage, _ = database
    seed(storage)
    args = {"session_id": "s", "agent_id": "a", "keep_last": 1}
    args.update(extra)
    with pytest.raises(ValueError):
        SQLMemoryRetention(storage).preview(**args)
    assert len(ids(storage)) == 12


def test_budgets_and_missing_policy_do_not_delete(database):
    storage, _ = database
    seed(storage)
    service = SQLMemoryRetention(storage)
    for args in [{}, {"keep_last": 1, "max_rows": 3}, {"keep_last": 1, "max_candidates": 2}]:
        with pytest.raises(ValueError):
            service.preview(session_id="s", agent_id="a", **args)
    assert len(ids(storage)) == 12


def test_plan_cannot_be_retargeted_or_used_on_another_service(database):
    storage, _ = database
    seed(storage)
    service = SQLMemoryRetention(storage)
    plan = service.preview(session_id="s", agent_id="a", keep_last=1)
    with pytest.raises(ValueError):
        service.execute(replace(plan, session_id="other"))
    with pytest.raises(ValueError):
        SQLMemoryRetention(storage).execute(plan)
    service.discard(plan)
    with pytest.raises(ValueError):
        service.execute(plan)


def test_equal_timestamp_tie_break_timezone_and_empty_plan(database):
    storage, _ = database
    model = seed(storage)
    with storage._sqldb_wrapper.get_session().begin() as session:
        session.execute(update(model).values(gmt_created=datetime(2026, 1, 1)))
    service = SQLMemoryRetention(storage)
    plan = service.preview(session_id="s", agent_id="a", keep_last=2)
    assert plan.candidate_ids == (1, 2)
    cutoff = datetime(2026, 1, 1, 8, tzinfo=timezone(timedelta(hours=8)))
    empty = service.preview(session_id="s", agent_id="a", before=cutoff)
    assert service.execute(empty).deleted_ids == ()
