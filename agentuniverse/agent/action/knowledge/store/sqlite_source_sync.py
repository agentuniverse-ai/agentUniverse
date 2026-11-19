"""Opt-in atomic source replacement for an initialized, file-backed SQLiteStore."""
import hashlib
import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path

import jieba

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


class SourceRevisionConflict(ValueError):
    """The caller's expected source revision is no longer current."""


class SourceIndexDrift(ValueError):
    """Managed rows changed outside the synchronizer; do not overwrite blindly."""


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":"))


def _digest(text, word_count, metadata, terms):
    return hashlib.sha256(_json([text, word_count, metadata, terms]).encode("utf-8")).hexdigest()


class SQLiteSourceSynchronizer:
    """Replace a source snapshot atomically without adopting unrelated rows.

    Keyword extraction happens before the write transaction on detached copies.
    SQLite BEGIN IMMEDIATE serializes competing writers. Each operation owns and
    closes its own connection, never commits or rolls back the Store connection.
    This class does not implement distributed transactions or a filesystem crawler.
    """

    def __init__(self, store, *, max_documents=10_000, max_payload_chars=10_000_000,
                 timeout=5.0):
        if not isinstance(store, SQLiteStore):
            raise TypeError("store must be a SQLiteStore")
        for value, name in ((max_documents, "max_documents"), (max_payload_chars, "max_payload_chars")):
            if type(value) is not int or value < 1:
                raise ValueError(name + " must be a positive integer")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 <= timeout <= 60:
            raise ValueError("timeout must be finite and between 0 and 60 seconds")
        if store.db_path == ":memory:" or str(store.db_path).startswith("file:"):
            raise ValueError("source sync requires a normal file-backed database path")
        self.store = store
        self.path = Path(store.db_path).resolve(strict=True)
        self.max_documents = max_documents
        self.max_payload_chars = max_payload_chars
        self.timeout = timeout

    def _connect(self):
        connection = sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True,
                                     timeout=self.timeout)
        return connection

    @staticmethod
    def _source(source):
        if not isinstance(source, str) or not source.strip() or len(source) > 1024:
            raise ValueError("source must be a nonblank string of at most 1024 characters")

    @staticmethod
    def _schema(connection):
        # Existing SQLiteStore tables must be present; do not initialize an
        # arbitrary database or silently invent its schema.
        connection.execute("SELECT id,text,word_count,metadata FROM documents LIMIT 0")
        connection.execute("SELECT term,doc_id FROM inverted_index LIMIT 0")
        connection.execute("""CREATE TABLE IF NOT EXISTS au_source_state_v1 (
            source TEXT PRIMARY KEY, revision INTEGER NOT NULL, pipeline_revision TEXT NOT NULL)""")
        connection.execute("""CREATE TABLE IF NOT EXISTS au_source_members_v1 (
            source TEXT NOT NULL, doc_id TEXT PRIMARY KEY, original_id TEXT NOT NULL,
            digest TEXT NOT NULL)""")
        connection.execute("CREATE INDEX IF NOT EXISTS au_source_members_source_v1 ON au_source_members_v1(source)")

    def _prepare(self, source, documents):
        if not isinstance(documents, list) or len(documents) > self.max_documents:
            raise ValueError("documents must be a list within max_documents")
        result = {}
        payload_chars = 0
        for document in documents:
            if not isinstance(document, Document) or not isinstance(document.id, str) or not document.id:
                raise ValueError("documents require nonempty string IDs")
            if not isinstance(document.text, str):
                raise ValueError("document text must be a string")
            identity = "au-sync-" + hashlib.sha256(_json([source, document.id]).encode("utf-8")).hexdigest()
            if identity in result:
                raise ValueError("duplicate document IDs within source")
            metadata = _json(document.metadata)
            payload_chars += len(document.id) + len(document.text) + len(metadata)
            if payload_chars > self.max_payload_chars:
                raise ValueError("snapshot exceeds max_payload_chars")
            detached = document.model_copy(deep=True)
            detached.keywords = set()
            terms = self.store._get_document_keyword(detached)
            if not isinstance(terms, (set, list, tuple)) or any(not isinstance(term, str) or not term for term in terms):
                raise ValueError("keyword extractor must return nonempty string terms")
            terms = sorted(set(terms))
            payload_chars += sum(len(term) for term in terms)
            if payload_chars > self.max_payload_chars:
                raise ValueError("snapshot exceeds max_payload_chars")
            word_count = len(jieba.lcut(document.text))
            result[identity] = {"original_id": document.id, "text": document.text,
                                "metadata": metadata, "terms": terms, "word_count": word_count,
                                "digest": _digest(document.text, word_count, metadata, terms)}
        return result

    @staticmethod
    def _read(connection, source):
        state = connection.execute("SELECT revision,pipeline_revision FROM au_source_state_v1 WHERE source=?", (source,)).fetchone()
        members = dict(connection.execute("SELECT doc_id,digest FROM au_source_members_v1 WHERE source=?", (source,)))
        drift = []
        for identity, expected in members.items():
            row = connection.execute("SELECT text,word_count,metadata FROM documents WHERE id=?", (identity,)).fetchone()
            terms = [term[0] for term in connection.execute(
                "SELECT term FROM inverted_index WHERE doc_id=? ORDER BY term", (identity,))]
            if row is None or _digest(*row, terms) != expected:
                drift.append(identity)
        return state, members, sorted(drift)

    def inspect_source(self, source):
        """Read a consistent manifest/row/index snapshot without creating tables."""
        self._source(source)
        with closing(self._connect()) as connection:
            connection.execute("BEGIN")
            try:
                tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if "au_source_state_v1" not in tables and "au_source_members_v1" not in tables:
                    return {"source": source, "revision": 0, "document_count": 0, "drift_ids": []}
                state, members, drift = self._read(connection, source)
                return {"source": source, "revision": state[0] if state else 0,
                        "document_count": len(members), "drift_ids": drift}
            finally:
                connection.rollback()

    def sync(self, source, documents, *, expected_revision, pipeline_revision,
             allow_empty=False):
        """Apply the complete desired source snapshot, returning persisted IDs.

        Empty snapshots require explicit allow_empty=True. expected_revision is
        mandatory: use zero for a new source, otherwise inspect_source's revision.
        Increment pipeline_revision when preprocessing configuration changes.
        Provider side effects are outside rollback; database writes are atomic.
        """
        self._source(source)
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError("expected_revision must be a nonnegative integer")
        if not isinstance(pipeline_revision, str) or not pipeline_revision.strip() or len(pipeline_revision) > 1024:
            raise ValueError("pipeline_revision must be a nonblank string of at most 1024 characters")
        if type(allow_empty) is not bool:
            raise ValueError("allow_empty must be a boolean")
        if documents == [] and not allow_empty:
            raise ValueError("empty snapshot requires allow_empty=True")
        prepared = self._prepare(source, documents)
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                self._schema(connection)
                state, current, drift = self._read(connection, source)
                revision = state[0] if state else 0
                if revision != expected_revision:
                    raise SourceRevisionConflict("source revision changed; inspect and recompute")
                if drift:
                    raise SourceIndexDrift("managed documents/index differ from manifest; inspect_source before repair")
                added = sorted(prepared.keys() - current.keys())
                removed = sorted(current.keys() - prepared.keys())
                changed = sorted(identity for identity in prepared.keys() & current.keys()
                                 if prepared[identity]["digest"] != current[identity])
                for identity in added:
                    if connection.execute("SELECT 1 FROM documents WHERE id=?", (identity,)).fetchone() or connection.execute(
                            "SELECT 1 FROM inverted_index WHERE doc_id=?", (identity,)).fetchone() or connection.execute(
                            "SELECT 1 FROM au_source_members_v1 WHERE doc_id=?", (identity,)).fetchone():
                        raise SourceIndexDrift("new managed ID collides with existing data")
                for identity in removed + changed:
                    connection.execute("DELETE FROM inverted_index WHERE doc_id=?", (identity,))
                    connection.execute("DELETE FROM documents WHERE id=?", (identity,))
                    connection.execute("DELETE FROM au_source_members_v1 WHERE doc_id=? AND source=?", (identity, source))
                for identity in added + changed:
                    item = prepared[identity]
                    connection.execute("INSERT INTO documents(id,text,word_count,metadata) VALUES (?,?,?,?)",
                                       (identity, item["text"], item["word_count"], item["metadata"]))
                    connection.executemany("INSERT INTO inverted_index(term,doc_id) VALUES (?,?)",
                                           [(term, identity) for term in item["terms"]])
                    connection.execute("INSERT INTO au_source_members_v1(source,doc_id,original_id,digest) VALUES (?,?,?,?)",
                                       (source, identity, item["original_id"], item["digest"]))
                updated = bool(added or removed or changed or state is None or state[1] != pipeline_revision)
                if updated:
                    revision += 1
                    connection.execute("INSERT OR REPLACE INTO au_source_state_v1(source,revision,pipeline_revision) VALUES (?,?,?)",
                                       (source, revision, pipeline_revision))
                connection.commit()
                return {"source": source, "revision": revision, "inserted": len(added),
                        "updated": len(changed), "deleted": len(removed),
                        "unchanged": len(prepared) - len(added) - len(changed),
                        "document_ids": {item["original_id"]: identity for identity, item in prepared.items()}}
            except BaseException:
                connection.rollback()
                raise
