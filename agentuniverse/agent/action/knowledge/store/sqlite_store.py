# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/8 14:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: sqlite_store.py
import sqlite3
import json
import math
from typing import List, Optional, Set
from collections import Counter

import jieba

from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class SQLiteStore(Store):
    db_path: str = 'sqlite_store.db'
    conn: Optional[sqlite3.Connection] = None
    k1: float = 1.5
    b: float = 0.75
    keyword_extractor: Optional[str] = None
    similarity_top_k: int = 10

    def _new_client(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    word_count INT,
                    metadata TEXT
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS inverted_index (
                    term TEXT,
                    doc_id TEXT,
                    FOREIGN KEY (doc_id) REFERENCES documents (id)
                )
            ''')

    def _initialize_by_component_configer(self,
                                          sqlite_store_configer: ComponentConfiger) -> 'DocProcessor':
        super()._initialize_by_component_configer(sqlite_store_configer)
        if hasattr(sqlite_store_configer, "db_path"):
            self.db_path = sqlite_store_configer.db_path
        if hasattr(sqlite_store_configer, "k1"):
            self.k1 = sqlite_store_configer.k1
        if hasattr(sqlite_store_configer, "b"):
            self.b = sqlite_store_configer.b
        if hasattr(sqlite_store_configer, "keyword_extractor"):
            self.keyword_extractor = sqlite_store_configer.keyword_extractor
        if hasattr(sqlite_store_configer, "similarity_top_k"):
            self.similarity_top_k = sqlite_store_configer.similarity_top_k
        return self


    def _get_all_docs_count(self) -> int:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM documents')
            count = cursor.fetchone()[0]
            cursor.close()
        return count

    def _get_all_docs_words_count(self) -> int:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT SUM(word_count) FROM documents')
            total_word_count = cursor.fetchone()[0]
            cursor.close()
        return total_word_count if total_word_count is not None else 0

    def compute_bm25(self, query_text, doc_text, inverted_index,
                     total_doc_count, total_word_count):
        k1 = self.k1
        b = self.b
        query_words = jieba.lcut(query_text)
        doc_words = jieba.lcut(doc_text)
        doc_length = len(doc_words)
        avg_doc_length = total_word_count / total_doc_count
        bm25_score = 0

        doc_counter = Counter(doc_words)

        for term in query_words:
            if term in inverted_index:
                term_freq = doc_counter[term]
                num_docs_with_term = len(inverted_index[term])
                idf = math.log((total_doc_count - num_docs_with_term + 0.5) / (
                        num_docs_with_term + 0.5) + 1)
                bm25_term_score = idf * (term_freq * (k1 + 1)) / (
                        term_freq + k1 * (
                        1 - b + b * (doc_length / avg_doc_length)))
                bm25_score += bm25_term_score

        return bm25_score


    def _get_document_keyword(self, document: Document) -> Set[str]:
        if not self.keyword_extractor:
            raise Exception(
                "You must specify a keyword extractor in sqlite store query")
        else:
            _doc = DocProcessorManager().get_instance_obj(
                self.keyword_extractor) \
                .process_docs([document])
            return _doc[0].keywords

    def insert_document(self, documents: List[Document], **kwargs):
        with self.conn:
            for document in documents:
                metadata = json.dumps(
                    document.metadata) if document.metadata else None
                self.conn.execute(
                    'INSERT OR REPLACE INTO documents (id, text, word_count, metadata) VALUES (?, ?, ?, ?)',
                    (document.id, document.text, len(jieba.lcut(document.text)), metadata)
                )
                # Clear any stale inverted-index rows for this id so a re-insert
                # of the same id (e.g. re-running ingest) does not accumulate
                # old keywords alongside the new ones. Matches upsert_document
                # semantics; without this the BM25 term-frequency / IDF counts
                # get polluted and stale keywords keep recalling the document.
                self.conn.execute(
                    'DELETE FROM inverted_index WHERE doc_id = ?',
                    (document.id,)
                )
                self._get_document_keyword(document)
                for term in set(document.keywords):
                    self.conn.execute(
                        'INSERT INTO inverted_index (term, doc_id) VALUES (?, ?)',
                        (term, document.id)
                    )

    def delete_document(self, document_id: int):
        with self.conn:
            self.conn.execute(
                'DELETE FROM documents WHERE id = ?',
                (document_id,)
            )
            self.conn.execute(
                'DELETE FROM inverted_index WHERE doc_id = ?',
                (document_id,)
            )

    def upsert_document(self, documents: List[Document], **kwargs):
        with self.conn:
            for document in documents:
                metadata = json.dumps(
                    document.metadata) if document.metadata else None
                self.conn.execute(
                    'INSERT OR REPLACE INTO documents (id, text, word_count, metadata) VALUES (?, ?, ?, ?)',
                    (
                    document.id, document.text, len(jieba.lcut(document.text)),
                    metadata)
                )
                self.conn.execute(
                    'DELETE FROM inverted_index WHERE doc_id = ?',
                    (document.id,)
                )
                self._get_document_keyword(document)
                for term in set(document.keywords):
                    self.conn.execute(
                        'INSERT INTO inverted_index (term, doc_id) VALUES (?, ?)',
                        (term, document.id)
                    )

    def query(self, query: Query, **kwargs) -> List[Document]:
        if len(query.keywords) > 0:
            query_terms = query.keywords
        else:
            query_terms = self._get_document_keyword(Document(text=query.query_str))
            query.keywords = query_terms

        # Get doc_id from inverted index.
        relevant_docs = set()
        inverted_index = {}
        with self.conn:
            for keyword in query_terms:
                cursor = self.conn.cursor()
                cursor.execute(
                    'SELECT doc_id FROM inverted_index WHERE term = ?',
                    (keyword,))
                docs_with_keyword = [row[0] for row in cursor.fetchall()]
                inverted_index[keyword] = docs_with_keyword
                relevant_docs.update(docs_with_keyword)
                cursor.close()

        # Count every document's bm25.
        doc_scores = []
        total_doc_count = self._get_all_docs_count()
        total_word_count = self._get_all_docs_words_count()
        for doc_id in relevant_docs:
            cursor = self.conn.cursor()
            cursor.execute('SELECT text FROM documents WHERE id = ?',
                           (doc_id,))
            row = cursor.fetchone()
            cursor.close()
            # The inverted index can reference a doc_id whose row was since
            # replaced or removed (INSERT OR REPLACE does not touch the index,
            # and a stale entry should not crash the whole query).
            if row is None:
                continue
            doc_text = row[0]

            bm25_score = self.compute_bm25(query.query_str, doc_text,
                                           inverted_index, total_doc_count, total_word_count)
            doc_scores.append((doc_id, bm25_score))

        # Order the docs with bm25, and return top k. Honour the per-query
        # similarity_top_k when the caller supplied one; otherwise fall back to
        # the store default. The previous code always used the store default,
        # silently truncating caller-requested recall.
        top_k = query.similarity_top_k if query.similarity_top_k else self.similarity_top_k
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        top_docs = doc_scores[:top_k]
        results = []
        for doc_id, score in top_docs:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE id = ?',
                           (doc_id,))
            doc_row = cursor.fetchone()
            cursor.close()
            if doc_row is None:
                continue

            # metadata is stored as JSON or NULL; json.loads(None) would raise
            # TypeError, so guard it explicitly.
            raw_metadata = doc_row[3]
            metadata = json.loads(raw_metadata) if raw_metadata else None
            document = Document(id=doc_row[0], text=doc_row[1],
                                word_count=doc_row[2],
                                metadata=metadata)
            results.append(document)

        return results

    @staticmethod
    def to_documents(query_result) -> List[Document]:
        """Convert rows from the documents table to aU Documents.

        Accepts either a Chroma-style dict (``{'ids': [[...]], 'documents': [[...]],
        'metadatas': [[...]]}``) for cross-store compatibility, or a list of
        tuples shaped like ``(id, text, word_count, metadata_json)`` as produced
        by the SQLiteStore query path. Returns an empty list for ``None`` or an
        unrecognised shape, rather than crashing on a missing key.
        """
        if query_result is None:
            return []

        documents: List[Document] = []

        # Chroma-style nested-list-of-lists dict.
        if isinstance(query_result, dict) and 'ids' in query_result:
            ids = query_result.get('ids') or [[]]
            texts = query_result.get('documents') or [[]]
            metadatas = query_result.get('metadatas') or [[]]
            if not ids or not isinstance(ids[0], list):
                return []
            for i, doc_id in enumerate(ids[0]):
                text = texts[0][i] if texts and len(texts[0]) > i else ''
                meta = metadatas[0][i] if metadatas and len(metadatas[0]) > i else None
                documents.append(Document(id=doc_id, text=text, embedding=[],
                                          metadata=meta if isinstance(meta, dict) else None))
            return documents

        # SQLite row tuples: (id, text, word_count, metadata_json).
        if isinstance(query_result, list):
            for row in query_result:
                if not row or len(row) < 2:
                    continue
                raw_metadata = row[3] if len(row) > 3 else None
                try:
                    metadata = json.loads(raw_metadata) if raw_metadata else None
                except (TypeError, ValueError):
                    metadata = None
                documents.append(Document(id=row[0], text=row[1], embedding=[],
                                          metadata=metadata))
        return documents
