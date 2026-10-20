"""Native database initialization under controlled first-access interleavings."""

import copy
import pickle
import sqlite3
import threading

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import SQLDBWrapperConfiger
from agentuniverse.database import sqldb_wrapper as module


def config(**database_args):
    settings = SQLDBWrapperConfiger()
    settings.db_uri = "sqlite://"
    settings.engine_args = {"poolclass": StaticPool,
                            "connect_args": {"check_same_thread": False}}
    settings.sql_database_args = {"sample_rows_in_table_info": 0, **database_args}
    return settings


@pytest.fixture
def databases(monkeypatch):
    """Observe delegated native construction and dispose every actual engine."""
    created = []
    original = module.SQLDatabase.from_uri

    def observe(*args, **kwargs):
        database = original(*args, **kwargs)
        created.append(database)
        return database

    monkeypatch.setattr(module.SQLDatabase, "from_uri", staticmethod(observe))
    try:
        yield created
    finally:
        for database in created:
            database._engine.dispose()


def scheduled_wrapper(settings, watched):
    """Gate the first real None cache read in each thread, without changing it."""
    gate = threading.Barrier(2)
    seen = threading.local()

    def arrive(value):
        if value is None and not getattr(seen, "arrived", False):
            seen.arrived = True
            gate.wait(timeout=5)
        return value

    class ScheduledWrapper(module.SQLDBWrapper):
        def __getattribute__(self, name):
            value = super().__getattribute__(name)
            if name == watched == "db_session":
                return arrive(value)
            return value

        def __getattr__(self, name):
            value = super().__getattr__(name)
            if name == watched == "_SQLDBWrapper__sql_database":
                return arrive(value)
            return value

    return ScheduledWrapper(db_wrapper_configer=settings)


def parallel(*operations):
    """Run native threads with bounded joins, including on a lock regression."""
    results = [None] * len(operations)
    errors = []

    def execute(index, operation):
        try:
            results[index] = operation()
        except BaseException as error:
            errors.append(error)

    threads = [threading.Thread(target=execute, args=(index, operation), daemon=True)
               for index, operation in enumerate(operations)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=8)
    assert not any(thread.is_alive() for thread in threads), "initialization did not finish"
    if errors:
        raise errors[0]
    return results


def test_concurrent_database_access_creates_one_native_engine(databases):
    wrapper = scheduled_wrapper(config(), "_SQLDBWrapper__sql_database")
    returned = parallel(lambda: wrapper.sql_database, lambda: wrapper.sql_database)
    assert len(databases) == 1
    assert returned[0] is returned[1] is wrapper.sql_database
    assert wrapper.get_session().kw["bind"] is returned[0]._engine

    with returned[0]._engine.begin() as connection:
        connection.execute(text("CREATE TABLE request_marker (value TEXT)"))
        connection.execute(text("INSERT INTO request_marker VALUES ('same database')"))
    assert wrapper.run("SELECT value FROM request_marker") == [{"value": "same database"}]


@pytest.mark.parametrize("warm_database", [False, True])
def test_concurrent_session_access_creates_one_native_factory(
        databases, monkeypatch, warm_database):
    wrapper = scheduled_wrapper(config(), "db_session")
    if warm_database:
        wrapper.sql_database
    factories = []
    original = module.sessionmaker

    def observe(*args, **kwargs):
        factory = original(*args, **kwargs)
        factories.append(factory)
        return factory

    monkeypatch.setattr(module, "sessionmaker", observe)
    returned = parallel(wrapper.get_session, wrapper.get_session)
    assert len(factories) == 1
    assert returned[0] is returned[1] is wrapper.get_session()
    assert len(databases) == 1
    assert returned[0].kw["bind"] is wrapper.sql_database._engine
    with returned[0]() as session:
        assert session.execute(text("SELECT 1")).scalar_one() == 1


def test_provided_session_factory_avoids_database_initialization(databases):
    engine = create_engine("sqlite://")
    try:
        provided = sessionmaker(bind=engine)
        wrapper = module.SQLDBWrapper(db_session=provided)
        assert wrapper.get_session() is provided
        with wrapper.get_session()() as session:
            assert session.execute(text("SELECT 2")).scalar_one() == 2
        assert databases == []
    finally:
        engine.dispose()


def test_failed_native_initialization_can_be_retried(databases):
    attempts = []

    def connect():
        attempts.append(None)
        if len(attempts) == 1:
            raise RuntimeError("first connection failed")
        return sqlite3.connect(":memory:", check_same_thread=False)

    settings = config()
    settings.engine_args["creator"] = connect
    wrapper = module.SQLDBWrapper(db_wrapper_configer=settings)
    with pytest.raises(RuntimeError, match="first connection failed"):
        wrapper.get_session()
    factory = wrapper.get_session()
    assert factory is wrapper.get_session()
    assert len(attempts) == 2
    assert len(databases) == 1
    with factory() as session:
        assert session.execute(text("SELECT 3")).scalar_one() == 3


@pytest.mark.parametrize("method", ["component", "deepcopy", "pickle"])
def test_uninitialized_wrapper_copies_keep_configuration_independent(databases, method):
    wrapper = module.SQLDBWrapper(db_wrapper_configer=config(max_string_length=17))
    if method == "component":
        cloned = wrapper.create_copy()
    elif method == "deepcopy":
        cloned = copy.deepcopy(wrapper)
    else:
        cloned = pickle.loads(pickle.dumps(wrapper))

    assert databases == []
    assert cloned.db_wrapper_configer is not wrapper.db_wrapper_configer
    cloned.db_wrapper_configer.engine_args["connect_args"]["timeout"] = 1
    assert "timeout" not in wrapper.db_wrapper_configer.engine_args["connect_args"]
    assert cloned.run("SELECT 'abcdefghijklmnopqrstuv' AS value") == [
        {"value": "abcdefghijklmnopqrstuv"}]
    assert "abcdefghijklmn..." in cloned.run_with_str_return(
        "SELECT 'abcdefghijklmnopqrstuv' AS value")
    assert len(databases) == 1
    assert cloned.sql_database is not wrapper.sql_database


def test_separate_copied_wrappers_can_initialize_in_parallel(databases):
    gate = threading.Barrier(2)

    def connect():
        gate.wait(timeout=5)
        return sqlite3.connect(":memory:", check_same_thread=False)

    settings = config()
    settings.engine_args["creator"] = connect
    wrapper = module.SQLDBWrapper(db_wrapper_configer=settings)
    cloned = wrapper.create_copy()
    assert cloned.db_wrapper_configer is not wrapper.db_wrapper_configer
    returned = parallel(lambda: wrapper.sql_database, lambda: cloned.sql_database)
    assert len(databases) == 2
    assert returned[0] is wrapper.sql_database
    assert returned[1] is cloned.sql_database
    assert returned[0] is not returned[1]


def test_sequential_cache_and_default_unlimited_string_results(databases):
    wrapper = module.SQLDBWrapper(db_wrapper_configer=config())
    assert databases == []
    first = wrapper.sql_database
    assert first is wrapper.sql_database
    assert wrapper.get_session() is wrapper.get_session()
    value = "a long non-ASCII string "+"汉字" * 20
    assert wrapper.run_with_str_return("SELECT '" + value + "'") == str([(value,)])
    assert wrapper.run("SELECT 4 AS value") == [{"value": 4}]
    assert len(databases) == 1
