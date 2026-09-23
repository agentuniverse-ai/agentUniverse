"""Guard agent chat history against cross-agent session reuse."""

import ast
import asyncio
import datetime as datetime_module
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Iterator, List, Tuple
from unittest.mock import Mock

import pytest
from sqlalchemy import Column, DateTime, Index, Integer, JSON, String, create_engine, event, select
from sqlalchemy.orm import Session, declarative_base


ROOT = Path(__file__).resolve().parents[2]


def load_service_method(service, method, namespace):
    source = ROOT / "agentuniverse_product" / "service" / service / f"{service}.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    function = next(node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method)
    module = ast.Module(body=[ast.ClassDef(name="Service", bases=[], keywords=[], body=[function], decorator_list=[])], type_ignores=[])
    scope = {"datetime": datetime, "Iterator": Iterator, "AsyncIterator": AsyncIterator, "Tuple": Tuple,
             "List": List, **namespace}
    exec(compile(ast.fix_missing_locations(module), str(source), "exec"), scope)
    return getattr(scope["Service"], method)


def make_session_library(engine):
    """Execute the real DAL update against SQLite without importing app integrations."""
    source = ROOT / "agentuniverse_product/dal/session_library.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    orm_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SessionORM")
    library_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SessionLibrary")
    update_method = next(node for node in library_class.body if isinstance(node, ast.FunctionDef) and node.name == "update_session")
    base = declarative_base()
    namespace = {"Base": base, "SESSION_TABLE_NAME": "session", "Column": Column,
                 "Integer": Integer, "String": String, "DateTime": DateTime, "JSON": JSON,
                 "Index": Index, "datetime": datetime_module, "SessionDO": object}
    module = ast.Module(body=[orm_class,
                              ast.ClassDef(name="Library", bases=[], keywords=[], body=[update_method], decorator_list=[])],
                        type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(source), "exec"), namespace)
    base.metadata.create_all(engine)
    namespace["Library"].get_db_session = staticmethod(lambda: Session(engine))
    return namespace["SessionORM"], namespace["Library"]()


@pytest.mark.parametrize("owner", [None, "other-agent"])
def test_session_affinity_rejects_missing_or_foreign_session(owner):
    library = Mock()
    library.get_session_detail.return_value = None if owner is None else Mock(agent_id=owner)
    validate = load_service_method("session_service", "validate_agent_session", {
        "SessionLibrary": lambda: library,
    })
    with pytest.raises(ValueError):
        validate("agent-1", "session-1")


def test_session_affinity_accepts_owner():
    library = Mock()
    library.get_session_detail.return_value = Mock(agent_id="agent-1")
    validate = load_service_method("session_service", "validate_agent_session", {
        "SessionLibrary": lambda: library,
    })
    validate("agent-1", "session-1")
    library.get_session_detail.assert_called_once_with("session-1")


@pytest.mark.parametrize("method", ["chat", "stream_chat", "async_stream_chat", "add_agent_chat_history"])
def test_agent_entrypoints_validate_before_using_session(method):
    sessions = Mock()
    sessions.validate_agent_session.side_effect = ValueError("foreign session")
    manager = Mock()
    messages = Mock()
    callback = load_service_method("agent_service", method, {
        "AgentManager": lambda: manager,
        "SessionService": lambda: sessions,
        "MessageService": lambda: messages,
        "AgentService": Mock(),
        "Agent": object,
        "OutputObject": object,
        "RequestTask": Mock(),
        "validate_and_assemble_agent_input": Mock(),
    })
    args = ("agent-1", "session-1", "hi")
    if method == "add_agent_chat_history":
        args += ("answer", datetime.now())
    with pytest.raises(ValueError, match="foreign session"):
        result = callback(*args)
        if method == "stream_chat":
            next(result)
        elif method == "async_stream_chat":
            asyncio.run(anext(result))
    sessions.validate_agent_session.assert_called_once_with("agent-1", "session-1")
    manager.get_instance_obj.assert_not_called()
    messages.add_message.assert_not_called()


def test_direct_update_cannot_reassign_session_owner():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    orm, library = make_session_library(engine)
    original = datetime(2024, 1, 1)
    with Session(engine) as session:
        session.add(orm(session_id="session-1", agent_id="owner", ext_info={"keep": True},
                        gmt_modified=original))
        session.commit()

    attempted = Mock(session_id="session-1", agent_id="other", gmt_modified=datetime(2024, 2, 1),
                     model_dump=Mock(return_value={"agent_id": "other", "gmt_modified": datetime(2024, 2, 1)}))
    with pytest.raises(ValueError):
        library.update_session(attempted)

    with Session(engine) as session:
        row = session.scalar(select(orm).where(orm.session_id == "session-1"))
        assert row.agent_id == "owner"
        assert row.gmt_modified == original
        assert row.ext_info == {"keep": True}


def test_update_checks_owner_in_atomic_sql_predicate():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    orm, library = make_session_library(engine)
    with Session(engine) as session:
        session.add(orm(session_id="session-1", agent_id="owner", ext_info={"keep": True}))
        session.commit()

    # Simulate owner changing after service prevalidation but before DAL update.
    with Session(engine) as session:
        session.execute(orm.__table__.update().where(orm.session_id == "session-1").values(agent_id="other"))
        session.commit()
    statements = []
    def record_update(_conn, _cursor, statement, _params, _context, _many):
        if statement.lstrip().upper().startswith("UPDATE"):
            statements.append(statement)
    event.listen(engine, "before_cursor_execute", record_update)
    try:
        with pytest.raises(ValueError):
            library.update_session(Mock(session_id="session-1", agent_id="owner",
                                        gmt_modified=datetime(2024, 2, 1),
                                        model_dump=Mock(return_value={"agent_id": "owner",
                                                                              "gmt_modified": datetime(2024, 2, 1)})))
    finally:
        event.remove(engine, "before_cursor_execute", record_update)

    assert statements and "agent_id" in statements[0].split("WHERE", 1)[1]
    with Session(engine) as session:
        assert session.scalar(select(orm).where(orm.session_id == "session-1")).agent_id == "other"


def test_owner_update_changes_timestamp_but_not_other_session_fields():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    orm, library = make_session_library(engine)
    original = datetime(2024, 1, 1)
    updated = datetime(2024, 2, 1)
    with Session(engine) as session:
        session.add(orm(session_id="session-1", agent_id="owner", ext_info={"keep": True},
                        gmt_modified=original))
        session.commit()

    update = Mock(session_id="session-1", agent_id="owner", gmt_modified=updated,
                  model_dump=Mock(return_value={"agent_id": "wrong", "ext_info": {"keep": False}}))
    assert library.update_session(update) == "session-1"

    with Session(engine) as session:
        row = session.scalar(select(orm).where(orm.session_id == "session-1"))
        assert row.agent_id == "owner"
        assert row.gmt_modified == updated
        assert row.ext_info == {"keep": True}
