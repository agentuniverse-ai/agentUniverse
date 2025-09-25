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
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class SQLiteStore(Store):
    db_path: str = "sqlite_store.db"
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
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    word_count INT,
                    metadata TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS inverted_index (
                    term TEXT,
                    doc_id TEXT,
                    FOREIGN KEY (doc_id) REFERENCES documents (id)
                )
            """)

    def _initialize_by_component_configer(self, sqlite_store_configer: ComponentConfiger) -> "DocProcessor":
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
            cursor.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            cursor.close()
        return count

    def _get_all_docs_words_count(self) -> int:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT SUM(word_count) FROM documents")
            total_word_count = cursor.fetchone()[0]
            cursor.close()
        return total_word_count if total_word_count is not None else 0

    def compute_bm25(self, query_text, doc_text, inverted_index, total_doc_count, total_word_count):
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
                idf = math.log((total_doc_count - num_docs_with_term + 0.5) / (num_docs_with_term + 0.5) + 1)
                bm25_term_score = (
                    idf * (term_freq * (k1 + 1)) / (term_freq + k1 * (1 - b + b * (doc_length / avg_doc_length)))
                )
                bm25_score += bm25_term_score

        return bm25_score

    def _get_document_keyword(self, document: Document) -> Set[str]:
        if not self.keyword_extractor:
            raise Exception("You must specify a keyword extractor in sqlite store query")
        else:
            _doc = DocProcessorManager().get_instance_obj(self.keyword_extractor).process_docs([document])
            return _doc[0].keywords

    def insert_document(self, documents: List[Document], **kwargs):
        with self.conn:
            for document in documents:
                metadata = json.dumps(document.metadata) if document.metadata else None
                self.conn.execute(
                    "INSERT OR REPLACE INTO documents (id, text, word_count, metadata) VALUES (?, ?, ?, ?)",
                    (document.id, document.text, len(jieba.lcut(document.text)), metadata),
                )
                self._get_document_keyword(document)
                for term in set(document.keywords):
                    self.conn.execute("INSERT INTO inverted_index (term, doc_id) VALUES (?, ?)", (term, document.id))

    def delete_document(self, document_id: int):
        with self.conn:
            self.conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            self.conn.execute("DELETE FROM inverted_index WHERE doc_id = ?", (document_id,))

    def upsert_document(self, documents: List[Document], **kwargs):
        with self.conn:
            for document in documents:
                metadata = json.dumps(document.metadata) if document.metadata else None
                self.conn.execute(
                    "INSERT OR REPLACE INTO documents (id, text, word_count, metadata) VALUES (?, ?, ?, ?)",
                    (document.id, document.text, len(jieba.lcut(document.text)), metadata),
                )
                self.conn.execute("DELETE FROM inverted_index WHERE doc_id = ?", (document.id,))
                self._get_document_keyword(document)
                for term in set(document.keywords):
                    self.conn.execute("INSERT INTO inverted_index (term, doc_id) VALUES (?, ?)", (term, document.id))

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
                cursor.execute("SELECT doc_id FROM inverted_index WHERE term = ?", (keyword,))
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
            cursor.execute("SELECT text FROM documents WHERE id = ?", (doc_id,))
            doc_text = cursor.fetchone()[0]
            cursor.close()

            bm25_score = self.compute_bm25(query.query_str, doc_text, inverted_index, total_doc_count, total_word_count)
            doc_scores.append((doc_id, bm25_score))

        # Order the docs with bm25, and return top k.
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        top_docs = doc_scores[: self.similarity_top_k]
        results = []
        for doc_id, score in top_docs:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            doc_row = cursor.fetchone()
            cursor.close()

            document = Document(id=doc_row[0], text=doc_row[1], word_count=doc_row[2], metadata=json.loads(doc_row[3]))
            results.append(document)

        return results

    @staticmethod
    def to_documents(query_result) -> List[Document]:
        """Convert the query results of sqlite to the agentUniverse(aU) document format."""

        if query_result is None:
            return []
        documents = []
        for i in range(len(query_result["ids"][0])):
            documents.append(
                Document(
                    id=query_result["ids"][0][i],
                    text=query_result["documents"][0][i],
                    embedding=[],
                    metadata=json.loads(query_result[2]) if query_result[2] else None,
                )
            )
        return documents
