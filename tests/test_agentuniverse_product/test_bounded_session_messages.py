"""Recent chat history should be bounded in SQL, not sliced after loading."""

import ast
import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from sqlalchemy import Column, DateTime, Index, Integer, JSON, String, asc, create_engine, desc, event
from sqlalchemy.orm import Session, declarative_base

from agentuniverse_product.dal.model.message_do import MessageDO


ROOT = Path(__file__).resolve().parents[2]


def load_message_library(engine):
    source = ROOT / "agentuniverse_product/dal/message_library.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    orm = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MessageORM")
    library = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MessageLibrary")
    methods = [node for node in library.body if isinstance(node, ast.FunctionDef)
               and node.name in {"get_messages", "__message_orm_to_do"}]
    cls = ast.ClassDef(name="Library", bases=[], keywords=[], body=methods, decorator_list=[])
    base = declarative_base()
    scope = {"Base": base, "Column": Column, "DateTime": DateTime, "Index": Index,
             "Integer": Integer, "JSON": JSON, "String": String, "asc": asc, "desc": desc,
             "datetime": datetime, "MESSAGE_TABLE_NAME": "message", "MessageDO": MessageDO}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[orm, cls], type_ignores=[])), str(source), "exec"), scope)
    base.metadata.create_all(engine)
    scope["Library"].get_db_session = staticmethod(lambda: Session(engine))
    return scope["MessageORM"], scope["Library"]()


def test_recent_messages_use_sql_limit_and_keep_chronological_order():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    orm, library = load_message_library(engine)
    with Session(engine) as session:
        for index in range(20):
            session.add(orm(session_id="target", content=str(index),
                            gmt_modified=datetime.datetime(2024, 1, 1)))
        session.add(orm(session_id="other", content="ignore"))
        session.commit()

    selects = []
    def record_select(_conn, _cursor, statement, _params, _context, _many):
        if statement.lstrip().upper().startswith("SELECT"):
            selects.append(statement)
    event.listen(engine, "before_cursor_execute", record_select)
    try:
        messages = library.get_messages("target", top_k=3)
    finally:
        event.remove(engine, "before_cursor_execute", record_select)

    assert [message.content for message in messages] == ["17", "18", "19"]
    assert len(selects) == 1 and "LIMIT" in selects[0].upper()
    assert len(library.get_messages("target", top_k=0)) == 20
    with pytest.raises(ValueError):
        library.get_messages("target", top_k=-1)


def test_session_detail_passes_limit_to_message_dal():
    source = ROOT / "agentuniverse_product/service/session_service/session_service.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "get_session_detail")
    session_library = Mock()
    session_library.get_session_detail.return_value = Mock(session_id="target")
    message_library = Mock()
    service = Mock()
    service.convert_to_session_dto.return_value = ["detail"]
    scope = {"SessionDTO": object, "SessionDO": object, "MessageDO": object,
             "SessionLibrary": lambda: session_library, "MessageLibrary": lambda: message_library,
             "SessionService": lambda: service}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(source), "exec"), scope)

    assert scope["get_session_detail"]("target", top_k=5) == "detail"
    message_library.get_messages.assert_called_once_with("target", top_k=5)
