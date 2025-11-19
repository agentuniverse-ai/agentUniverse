#!/usr/bin/env python3

# @Time    : 2025/11/3 19:58
# @Author  : sunhailin.shl
# @Email   : sunhailin.shl@antgroup.com
# @FileName: test_sqlalchemy_reader.py

"""
Unit test for SQLAlchemyReader.
"""

import pytest

from sqlalchemy import Column, Integer, String

from agentuniverse.agent.action.knowledge.reader.database.sqlalchemy_reader import SQLAlchemyReader
from agentuniverse.agent.action.knowledge.store.document import Document


class DummyDocument(Document):
    """for unit test"""
    def __init__(self, text, metadata):
        self.text = text
        self.metadata = metadata


@pytest.fixture
def sqlite_reader(monkeypatch):
    # mock Document
    monkeypatch.setattr(
        "agentuniverse.agent.action.knowledge.store.document.Document", DummyDocument
    )
    # use memory SQLite to test
    reader = SQLAlchemyReader()
    reader.initialize_connection("sqlite:///:memory:", echo=False)
    return reader


def test_detect_db_type():
    r2 = SQLAlchemyReader()
    r2.initialize_connection("clickhouse://user:pwd@localhost/db")
    assert r2._db_type == "clickhouse"

    r4 = SQLAlchemyReader()
    r4.initialize_connection("sqlite:///:memory:")
    assert r4._db_type == "generic"


def test_create_table_and_insert(sqlite_reader):
    # create test model ORM
    User = sqlite_reader.create_table_model(
        table_name="users",
        columns={
            "id": Column(Integer, primary_key=True),
            "name": Column(String),
            "email": Column(String)
        }
    )

    # create table
    sqlite_reader._Base.metadata.create_all(sqlite_reader._engine)

    # insert test data
    session = sqlite_reader._session_factory()
    session.add(User(id=1, name="Alice", email="alice@example.com"))
    session.add(User(id=2, name="Bob", email="bob@example.com"))
    session.commit()
    session.close()

    # load all data
    docs = sqlite_reader.load_data(table_cls=User)
    assert len(docs) == 2
    assert any("Alice" in d.text for d in docs)

    # filter by name
    docs_filtered = sqlite_reader.load_data(
        table_cls=User,
        filters={"name": "Bob"}
    )
    assert len(docs_filtered) == 1
    assert docs_filtered[0].metadata["name"] == "Bob"

    # page test
    docs_page = sqlite_reader.load_data(table_cls=User, limit=1, offset=1)
    assert len(docs_page) == 1
