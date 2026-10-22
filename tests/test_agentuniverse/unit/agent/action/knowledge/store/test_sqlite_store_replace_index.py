import sqlite3

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


def test_insert_document_replaces_stale_inverted_index_terms():
    store = SQLiteStore()
    store.conn = sqlite3.connect(":memory:")
    store._create_tables()
    store._get_document_keyword = lambda document: document.keywords

    store.insert_document([Document(id="doc-1", text="old", keywords={"old-term"})])
    store.insert_document([Document(id="doc-1", text="new", keywords={"new-term"})])

    old_terms = store.conn.execute(
        "SELECT term FROM inverted_index WHERE doc_id = ?", ("doc-1",)
    ).fetchall()

    assert old_terms == [("new-term",)]
