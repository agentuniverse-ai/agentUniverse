"""Session deletion must not leave message rows behind."""

import ast
import datetime
from pathlib import Path

import pytest
from sqlalchemy import Column, DateTime, Index, Integer, JSON, String, create_engine, event, select
from sqlalchemy.orm import Session, declarative_base


ROOT = Path(__file__).resolve().parents[2]


def load_dal(engine):
    """Run production DAL methods against SQLite without loading app integrations."""
    base = declarative_base()
    scope = {"Base": base, "Column": Column, "DateTime": DateTime, "Index": Index,
             "Integer": Integer, "JSON": JSON, "String": String, "datetime": datetime,
             "SESSION_TABLE_NAME": "session", "MESSAGE_TABLE_NAME": "message"}
    for name, orm_name in (("message_library", "MessageORM"), ("session_library", "SessionORM")):
        source = ROOT / "agentuniverse_product/dal" / f"{name}.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        orm_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == orm_name)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[orm_class], type_ignores=[])), str(source), "exec"), scope)
        if name == "session_library":
            library_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SessionLibrary")
            delete = next(node for node in library_class.body if isinstance(node, ast.FunctionDef) and node.name == "delete_session")
            class_node = ast.ClassDef(name="Library", bases=[], keywords=[], body=[delete], decorator_list=[])
            exec(compile(ast.fix_missing_locations(ast.Module(body=[class_node], type_ignores=[])), str(source), "exec"), scope)
    base.metadata.create_all(engine)
    scope["Library"].get_db_session = staticmethod(lambda: Session(engine))
    return scope["SessionORM"], scope["MessageORM"], scope["Library"]()


def seed(engine, session_orm, message_orm):
    with Session(engine) as session:
        session.add(session_orm(session_id="target", agent_id="agent"))
        session.add(message_orm(session_id="target", content="hello"))
        session.add(message_orm(session_id="other", content="keep"))
        session.commit()


def test_delete_session_and_its_messages_in_one_operation():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    session_orm, message_orm, library = load_dal(engine)
    seed(engine, session_orm, message_orm)

    assert library.delete_session("target") == "target"

    with Session(engine) as session:
        assert session.scalars(select(session_orm)).all() == []
        assert [row.session_id for row in session.scalars(select(message_orm)).all()] == ["other"]


def test_delete_failure_rolls_back_message_removal():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    session_orm, message_orm, library = load_dal(engine)
    seed(engine, session_orm, message_orm)

    def fail_session_delete(_conn, _cursor, statement, _params, _context, _many):
        if statement.lstrip().upper().startswith("DELETE FROM SESSION"):
            raise RuntimeError("simulated session delete failure")

    event.listen(engine, "before_cursor_execute", fail_session_delete)
    try:
        with pytest.raises(RuntimeError, match="simulated"):
            library.delete_session("target")
    finally:
        event.remove(engine, "before_cursor_execute", fail_session_delete)

    with Session(engine) as session:
        assert [row.session_id for row in session.scalars(select(session_orm)).all()] == ["target"]
        assert {row.session_id for row in session.scalars(select(message_orm)).all()} == {"target", "other"}
