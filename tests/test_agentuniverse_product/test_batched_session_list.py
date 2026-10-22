"""Session list should use one bounded session query and one message query."""

import ast
import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import List
from unittest.mock import Mock

from sqlalchemy import Column, DateTime, Index, Integer, JSON, String, asc, create_engine, desc, event
from sqlalchemy.orm import Session, declarative_base

from agentuniverse_product.dal.model.message_do import MessageDO
from agentuniverse_product.dal.model.session_do import SessionDO


ROOT = Path(__file__).resolve().parents[2]


def load_libraries(engine):
    base = declarative_base()
    scope = {"Base": base, "Column": Column, "DateTime": DateTime, "Index": Index,
             "Integer": Integer, "JSON": JSON, "String": String, "asc": asc, "desc": desc,
             "datetime": datetime, "MESSAGE_TABLE_NAME": "message", "SESSION_TABLE_NAME": "session",
             "MessageDO": MessageDO, "SessionDO": SessionDO}
    for module_name, orm_name, methods in (
        ("session_library", "SessionORM", {"get_session_list", "__session_orm_to_do"}),
        ("message_library", "MessageORM", {"get_messages_for_sessions", "__message_orm_to_do"}),
    ):
        source = ROOT / "agentuniverse_product/dal" / f"{module_name}.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        orm = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == orm_name)
        library = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name.endswith("Library"))
        selected = [node for node in library.body if isinstance(node, ast.FunctionDef) and node.name in methods]
        cls = ast.ClassDef(name=f"{orm_name}Library", bases=[], keywords=[], body=selected, decorator_list=[])
        exec(compile(ast.fix_missing_locations(ast.Module(body=[orm, cls], type_ignores=[])), str(source), "exec"), scope)
        scope[cls.name].get_db_session = staticmethod(lambda: Session(engine))
    base.metadata.create_all(engine)
    return scope["SessionORM"], scope["MessageORM"], scope["SessionORMLibrary"](), scope["MessageORMLibrary"]()


def test_bounded_sessions_and_batch_messages_use_two_queries():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    session_orm, message_orm, sessions, messages = load_libraries(engine)
    with Session(engine) as db:
        for index in range(15):
            sid = f"session-{index}"
            db.add(session_orm(session_id=sid, agent_id="agent",
                               gmt_modified=datetime.datetime(2024, 1, 1, 0, index)))
            db.add(message_orm(session_id=sid, content=f"message-{index}"))
        db.add(session_orm(session_id="foreign", agent_id="other"))
        db.add(message_orm(session_id="foreign", content="secret"))
        db.commit()

    selects = []
    def record(_conn, _cursor, statement, _params, _context, _many):
        if statement.lstrip().upper().startswith("SELECT"):
            selects.append(statement)
    event.listen(engine, "before_cursor_execute", record)
    try:
        recent = sessions.get_session_list("agent", limit=10)
        grouped = messages.get_messages_for_sessions([item.session_id for item in recent])
    finally:
        event.remove(engine, "before_cursor_execute", record)

    assert [item.session_id for item in recent] == [f"session-{index}" for index in range(14, 4, -1)]
    assert len(selects) == 2
    assert "LIMIT" in selects[0].upper() and " IN " in selects[1].upper()
    assert set(grouped) == {item.session_id for item in recent}
    assert grouped["session-14"][0].content == "message-14"
    assert "foreign" not in grouped
    assert messages.get_messages_for_sessions([]) == {}
    assert messages.get_messages_for_sessions(["missing"]) == {"missing": []}


def test_service_uses_batch_method_once():
    source = ROOT / "agentuniverse_product/service/session_service/session_service.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "get_session_list")
    sessions = Mock()
    sessions.get_session_list.return_value = [SimpleNamespace(session_id="session-1")]
    messages = Mock()
    messages.get_messages_for_sessions.return_value = {"session-1": []}
    service = Mock()
    service.convert_to_session_dto.return_value = ["result"]
    scope = {"List": List, "SessionDTO": object, "SessionDO": object, "MessageDO": object,
             "SessionLibrary": lambda: sessions, "MessageLibrary": lambda: messages,
             "SessionService": lambda: service}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(source), "exec"), scope)

    assert scope["get_session_list"]("agent") == ["result"]
    sessions.get_session_list.assert_called_once_with("agent", limit=10)
    messages.get_messages_for_sessions.assert_called_once_with(["session-1"])
