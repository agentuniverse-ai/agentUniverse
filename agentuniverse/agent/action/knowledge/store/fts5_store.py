"""File-backed SQLite FTS5 full-text store with transactional index maintenance."""
import asyncio
import json
import math
import re
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path

from pydantic import Field, StrictFloat, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def _json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


class SQLiteFTS5Store(Store):
    """An independent backend; never migrate the existing SQLiteStore implicitly.

    Each operation owns its connection. FTS5 Unicode61 indexes all text, without
    Jieba keyword truncation. Query syntax is generated from quoted literal terms.
    """
    db_path: StrictStr = ""
    tokenizer: StrictStr = "unicode61"
    similarity_top_k: StrictInt = Field(default=10, ge=1, le=1000)
    max_batch_documents: StrictInt = Field(default=1000, ge=1)
    max_document_chars: StrictInt = Field(default=1_000_000, ge=1)
    max_batch_chars: StrictInt = Field(default=10_000_000, ge=1)
    max_query_chars: StrictInt = Field(default=4096, ge=1)
    max_query_terms: StrictInt = Field(default=64, ge=1, le=256)
    max_result_chars: StrictInt = Field(default=4_000_000, ge=1)
    max_seconds: StrictFloat = Field(default=5.0, gt=0, le=60)
    max_vm_steps: StrictInt = Field(default=5_000_000, ge=1000)

    def _options(self):
        if type(self.db_path) is not str or not self.db_path.strip() or self.db_path == ":memory:" or self.db_path.startswith("file:"):
            raise ValueError("db_path must be a local file path, not memory or a SQLite URI")
        if self.tokenizer not in ("unicode61", "trigram"):
            raise ValueError("tokenizer must be unicode61 or trigram")
        for name in ("similarity_top_k", "max_batch_documents", "max_document_chars", "max_batch_chars", "max_query_chars", "max_query_terms", "max_result_chars", "max_vm_steps"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(name + " must be a positive integer")
        if self.similarity_top_k > 1000 or self.max_query_terms > 256 or self.max_vm_steps < 1000:
            raise ValueError("query/VM bounds are outside supported limits")
        if isinstance(self.max_seconds, bool) or not isinstance(self.max_seconds, (int, float)) or not math.isfinite(self.max_seconds) or not 0 < self.max_seconds <= 60:
            raise ValueError("max_seconds must be finite and in (0, 60]")
        return Path(self.db_path).resolve()

    @contextmanager
    def _connection(self, *, create=False, cancel=None):
        path = self._options()
        connection = sqlite3.connect(path.as_uri() + ("?mode=rwc" if create else "?mode=rw"), uri=True, timeout=self.max_seconds)
        start, steps = time.monotonic(), [0]
        def progress():
            steps[0] += 1000
            return bool((cancel is not None and cancel.is_set()) or steps[0] > self.max_vm_steps or time.monotonic() - start > self.max_seconds)
        connection.set_progress_handler(progress, 1000)
        try:
            if cancel is not None and cancel.is_set():
                raise InterruptedError("FTS5 operation cancelled before execution")
            if not create:
                tokenizer = {"unicode61": "unicode61 remove_diacritics 2", "trigram": "trigram"}[self.tokenizer]
                if connection.execute("SELECT version,tokenizer FROM au_fts_schema").fetchall() != [(1, tokenizer)]:
                    raise ValueError("incompatible FTS5 store schema/tokenizer; use the configured database tokenizer")
            yield connection
        finally:
            connection.set_progress_handler(None, 0)
            connection.close()

    def _new_client(self):
        """Create/check the dedicated v1 schema transactionally; no shared client."""
        with self._connection(create=True) as connection:
            try:
                tokenizer = {"unicode61": "unicode61 remove_diacritics 2", "trigram": "trigram"}[self.tokenizer]
                connection.execute("BEGIN IMMEDIATE")
                connection.execute("SELECT json_valid('{}')")
                existing = connection.execute("SELECT name FROM sqlite_master WHERE name GLOB 'au_fts_*'").fetchall()
                if existing:
                    version = connection.execute("SELECT version,tokenizer FROM au_fts_schema").fetchall()
                    if version != [(1, tokenizer)]:
                        raise ValueError("incompatible FTS5 store schema")
                    # Fail on missing/incompatible core columns rather than overwrite data.
                    connection.execute("SELECT id,text,metadata,embedding,keywords FROM au_fts_docs LIMIT 0")
                    connection.execute("SELECT rowid,text FROM au_fts_index LIMIT 0")
                    names = {row[0] for row in existing}
                    if not {"au_fts_insert", "au_fts_delete", "au_fts_update"}.issubset(names):
                        raise ValueError("FTS5 index triggers are missing; explicit repair is required")
                else:
                    connection.execute("CREATE TABLE au_fts_schema(version INTEGER NOT NULL, tokenizer TEXT NOT NULL)")
                    connection.execute("INSERT INTO au_fts_schema VALUES (1,?)", (tokenizer,))
                    connection.execute("CREATE TABLE au_fts_docs(rowid INTEGER PRIMARY KEY, id TEXT UNIQUE NOT NULL, text TEXT NOT NULL, metadata TEXT NOT NULL, embedding TEXT NOT NULL, keywords TEXT NOT NULL)")
                    connection.execute("CREATE VIRTUAL TABLE au_fts_index USING fts5(text,content='au_fts_docs',content_rowid='rowid',tokenize='" + tokenizer + "')")
                    connection.execute("CREATE TRIGGER au_fts_insert AFTER INSERT ON au_fts_docs BEGIN INSERT INTO au_fts_index(rowid,text) VALUES(new.rowid,new.text); END")
                    connection.execute("CREATE TRIGGER au_fts_delete AFTER DELETE ON au_fts_docs BEGIN INSERT INTO au_fts_index(au_fts_index,rowid,text) VALUES('delete',old.rowid,old.text); END")
                    connection.execute("CREATE TRIGGER au_fts_update AFTER UPDATE ON au_fts_docs BEGIN INSERT INTO au_fts_index(au_fts_index,rowid,text) VALUES('delete',old.rowid,old.text); INSERT INTO au_fts_index(rowid,text) VALUES(new.rowid,new.text); END")
                connection.commit()
            except sqlite3.OperationalError as error:
                connection.rollback()
                if "no such module: fts5" in str(error):
                    raise RuntimeError("This Python SQLite build lacks FTS5; use an FTS5-enabled SQLite build") from error
                if "no such function: json_valid" in str(error):
                    raise RuntimeError("This Python SQLite build lacks JSON functions required for metadata filtering") from error
                if "no such tokenizer: trigram" in str(error):
                    raise RuntimeError("This SQLite build lacks the trigram tokenizer; use SQLite 3.34+ with FTS5") from error
                raise
            except BaseException:
                connection.rollback()
                raise

    def _documents(self, documents):
        self._options()
        if not isinstance(documents, list) or len(documents) > self.max_batch_documents:
            raise ValueError("documents must be a bounded list")
        output, identities, size = [], set(), 0
        for doc in documents:
            if not isinstance(doc, Document) or type(doc.id) is not str or not doc.id or len(doc.id) > 1024:
                raise ValueError("each Document needs a nonempty id up to 1024 characters")
            if doc.id in identities:
                raise ValueError("duplicate IDs within one batch are ambiguous")
            identities.add(doc.id)
            if type(doc.text) is not str:
                raise ValueError("document text must be a string")
            if doc.metadata is not None and (type(doc.metadata) is not dict or "__fts5" in doc.metadata):
                raise ValueError("metadata must be an object without reserved __fts5")
            row = (doc.id, doc.text, _json(doc.metadata), _json(doc.embedding), _json(sorted(doc.keywords)))
            length = sum(len(value) for value in row)
            size += length
            if length > self.max_document_chars or size > self.max_batch_chars:
                raise ValueError("document/batch character budget exceeded")
            output.append(row)
        return output

    def _write_rows(self, rows, mode, cancel=None):
        with self._connection(cancel=cancel) as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                for row in rows:
                    if cancel is not None and cancel.is_set():
                        raise InterruptedError("FTS5 write cancelled")
                    if mode == "insert":
                        connection.execute("INSERT INTO au_fts_docs(id,text,metadata,embedding,keywords) VALUES (?,?,?,?,?)", row)
                    elif mode == "upsert":
                        connection.execute("INSERT INTO au_fts_docs(id,text,metadata,embedding,keywords) VALUES (?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET text=excluded.text,metadata=excluded.metadata,embedding=excluded.embedding,keywords=excluded.keywords", row)
                    else:
                        cursor = connection.execute("UPDATE au_fts_docs SET text=?,metadata=?,embedding=?,keywords=? WHERE id=?", row[1:] + row[:1])
                        if cursor.rowcount != 1:
                            raise KeyError("cannot update missing document: " + row[0])
                if cancel is not None and cancel.is_set():
                    raise InterruptedError("FTS5 write cancelled before commit")
                connection.commit()
            except BaseException:
                connection.rollback()
                raise

    def insert_document(self, documents, **kwargs):
        if kwargs:
            raise ValueError("unexpected insert options")
        self._write_rows(self._documents(documents), "insert")

    def upsert_document(self, documents, **kwargs):
        if kwargs:
            raise ValueError("unexpected upsert options")
        self._write_rows(self._documents(documents), "upsert")

    def update_document(self, documents, **kwargs):
        if kwargs:
            raise ValueError("unexpected update options")
        self._write_rows(self._documents(documents), "update")

    def _delete(self, document_id, cancel=None):
        if type(document_id) is not str or not document_id or len(document_id) > 1024:
            raise ValueError("document_id must be a nonempty string up to 1024 characters")
        with self._connection(cancel=cancel) as connection, connection:
            connection.execute("DELETE FROM au_fts_docs WHERE id=?", (document_id,))
            if cancel is not None and cancel.is_set():
                raise InterruptedError("FTS5 delete cancelled")

    def delete_document(self, document_id, **kwargs):
        if kwargs:
            raise ValueError("unexpected delete options")
        self._delete(document_id)

    def _query_options(self, query):
        self._options()
        if not isinstance(query, Query) or type(query.query_str) is not str:
            raise ValueError("FTS5 requires query_str text")
        if query.embeddings or query.query_image_bundles or query.query_text_bundles:
            raise ValueError("FTS5 does not implement vector/image/bundled queries")
        limit = self.similarity_top_k if query.similarity_top_k is None else query.similarity_top_k
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("similarity_top_k must be an integer in [1,1000]")
        text = query.query_str
        if len(text) > self.max_query_chars or "\x00" in text:
            raise ValueError("query text exceeds budget or contains NUL")
        options = query.ext_info.get("fts5", {})
        if type(options) is not dict or set(options) - {"match_mode", "metadata_equals"}:
            raise ValueError("unknown FTS5 query options")
        if len(_json(options)) + len(text) > self.max_query_chars:
            raise ValueError("query and filter options exceed character budget")
        mode = options.get("match_mode", "any")
        if mode not in ("any", "all", "phrase"):
            raise ValueError("match_mode must be any, all or phrase")
        terms = [text] if mode == "phrase" else text.split()
        if len(terms) > self.max_query_terms:
            raise ValueError("query exceeds term budget")
        terms = [term for term in terms if term.strip()]
        if self.tokenizer == "trigram" and any(len(term.strip()) < 3 for term in terms):
            raise ValueError("trigram query terms must contain at least three Unicode characters")
        expression = (" AND " if mode == "all" else " OR ").join('"' + term.replace('"', '""') + '"' for term in terms)
        filters = options.get("metadata_equals", {})
        if type(filters) is not dict or len(filters) > 16:
            raise ValueError("metadata_equals must be an object with at most 16 fields")
        clauses, values = [], []
        kinds = {str: "text", int: "integer", float: "real", bool: None, type(None): "null"}
        for key, value in filters.items():
            if type(key) is not str or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", key) or type(value) not in kinds:
                raise ValueError("metadata equality requires simple keys and JSON scalar values")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("metadata equality cannot use non-finite numbers")
            if type(value) is int and not -(2 ** 63) <= value < 2 ** 63:
                raise ValueError("integer equality requires SQLite signed 64-bit values")
            kind = ("true" if value else "false") if type(value) is bool else kinds[type(value)]
            clauses.append("json_type(d.metadata,?)=?")
            values.extend(["$." + key, kind])
            if value is not None:
                clauses.append("json_extract(d.metadata,?)=?")
                values.extend(["$." + key, value])
        return expression, clauses, values, limit, mode

    def _query(self, prepared, cancel=None):
        expression, clauses, values, limit, mode = prepared
        if not expression:
            return []
        sql = "SELECT d.id,d.text,d.metadata,d.embedding,d.keywords,bm25(au_fts_index) AS score FROM au_fts_index JOIN au_fts_docs d ON d.rowid=au_fts_index.rowid WHERE au_fts_index MATCH ?"
        if clauses:
            sql += " AND " + " AND ".join(clauses)
        sql += " ORDER BY score ASC,d.id ASC LIMIT ?"
        output, size = [], 0
        with self._connection(cancel=cancel) as connection:
            for identity, text, metadata, embedding, keywords, score in connection.execute(sql, [expression, *values, limit]):
                if cancel is not None and cancel.is_set():
                    raise InterruptedError("FTS5 query cancelled")
                info = json.loads(metadata) or {}
                info["__fts5"] = {"bm25": score, "match_mode": mode, "lower_is_better": True}
                size += len(identity) + len(text) + len(_json(info)) + len(embedding) + len(keywords)
                if size > self.max_result_chars:
                    raise ValueError("query exceeds max_result_chars")
                output.append(Document(id=identity, text=text, metadata=info, embedding=json.loads(embedding), keywords=set(json.loads(keywords))))
        return output

    def query(self, query, **kwargs):
        if kwargs:
            raise ValueError("use query.ext_info['fts5'] for FTS5 query options")
        return self._query(self._query_options(query))

    async def _async(self, function, *args):
        cancel = threading.Event()
        task = asyncio.create_task(asyncio.to_thread(function, *args, cancel=cancel))
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            cancel.set()
            # Own the worker until it releases its connection, even on repeated cancellation.
            while not task.done():
                try:
                    await asyncio.shield(task)
                except asyncio.CancelledError:
                    continue
                except Exception:
                    break
            if task.done() and not task.cancelled():
                task.exception()
            raise

    async def async_query(self, query, **kwargs):
        if kwargs:
            raise ValueError("unexpected query options")
        return await self._async(self._query, self._query_options(query))

    async def async_insert_document(self, documents, **kwargs):
        if kwargs:
            raise ValueError("unexpected insert options")
        return await self._async(self._write_rows, self._documents(documents), "insert")

    async def async_upsert_document(self, documents, **kwargs):
        if kwargs:
            raise ValueError("unexpected upsert options")
        return await self._async(self._write_rows, self._documents(documents), "upsert")

    async def async_update_document(self, documents, **kwargs):
        if kwargs:
            raise ValueError("unexpected update options")
        return await self._async(self._write_rows, self._documents(documents), "update")

    async def async_delete_document(self, document_id, **kwargs):
        if kwargs:
            raise ValueError("unexpected delete options")
        return await self._async(self._delete, document_id)

    def _initialize_by_component_configer(self, config):
        names = ("db_path", "tokenizer", "similarity_top_k", "max_batch_documents", "max_document_chars", "max_batch_chars",
                 "max_query_chars", "max_query_terms", "max_result_chars", "max_seconds", "max_vm_steps")
        checked = SQLiteFTS5Store(**{name: getattr(config, name, getattr(self, name)) for name in names})
        checked._options()
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(checked, name))
        return self
