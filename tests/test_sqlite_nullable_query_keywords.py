"""Nullable Query -> actual SQLiteStore keyword selection, stopping before SQL.

No database connection is created. One managed-extractor boundary deliberately
raises after receiving the real Document; query construction, dispatch and
SQLiteStore._get_document_keyword execute unmodified production methods.
"""
import unittest
import sys
import types
import importlib.util
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
# Tokenization is outside this pre-database dispatch regression.  Keep an
# absent optional tokenizer import explicit and fail if it is ever called.
if importlib.util.find_spec("jieba") is None:
    tokenizer_boundary = types.ModuleType("jieba")

    def no_tokenization(*args, **kwargs):
        raise AssertionError("Tokenization must not run before keyword dispatch")

    tokenizer_boundary.lcut = no_tokenization
    tokenizer_boundary.cut = no_tokenization
    sys.modules["jieba"] = tokenizer_boundary
    try:
        from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    finally:
        # Restore only the boundary import; retain normally imported framework
        # modules rather than unloading/re-registering Pydantic validators.
        del sys.modules["jieba"]
else:
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager


class ExtractorBoundaryReached(Exception):
    pass


class RecordingExtractor:
    def __init__(self, failure):
        self.failure = failure
        self.documents = []

    def process_docs(self, documents):
        self.documents.extend(documents)
        raise self.failure


class NullableQueryKeywordTests(unittest.TestCase):
    def test_null_keywords_reach_the_existing_missing_extractor_diagnostic(self):
        store = SQLiteStore()
        query = Query(query_str="alpha", keywords=None)
        self.assertIsNone(query.keywords)
        with self.assertRaises(Exception) as caught:
            store.query(query)
        self.assertEqual(str(caught.exception), "You must specify a keyword extractor in sqlite store query")
        self.assertNotIsInstance(caught.exception, TypeError)
        self.assertIsNone(store.conn)

    def test_nullable_keywords_reach_configured_extractor_before_database(self):
        store = SQLiteStore(keyword_extractor="offline-extractor-boundary")
        query = Query(query_str="你好 alpha", keywords=None)
        failure = ExtractorBoundaryReached("stop before database access")
        extractor = RecordingExtractor(failure)
        with patch.object(DocProcessorManager(), "get_instance_obj", return_value=extractor) as lookup:
            with self.assertRaises(ExtractorBoundaryReached) as caught:
                store.query(query)
        self.assertIs(caught.exception, failure)
        lookup.assert_called_once_with("offline-extractor-boundary")
        self.assertEqual(len(extractor.documents), 1)
        self.assertIsInstance(extractor.documents[0], Document)
        self.assertEqual(extractor.documents[0].text, query.query_str)
        self.assertIsNone(query.keywords)
        self.assertIsNone(store.conn)

    def test_default_and_explicit_empty_keywords_keep_the_existing_path(self):
        for query in (Query(query_str="alpha"), Query(query_str="alpha", keywords=set())):
            with self.subTest(query=query):
                store = SQLiteStore()
                self.assertEqual(query.keywords, set())
                with self.assertRaises(Exception) as caught:
                    store.query(query)
                self.assertEqual(str(caught.exception), "You must specify a keyword extractor in sqlite store query")
                self.assertIsNone(store.conn)

    def test_empty_keywords_already_reach_configured_extractor(self):
        store = SQLiteStore(keyword_extractor="offline-extractor-boundary")
        failure = ExtractorBoundaryReached("stop before SQL")
        extractor = RecordingExtractor(failure)
        with patch.object(DocProcessorManager(), "get_instance_obj", return_value=extractor):
            with self.assertRaises(ExtractorBoundaryReached) as caught:
                store.query(Query(query_str="alpha", keywords=set()))
        self.assertIs(caught.exception, failure)
        self.assertEqual(extractor.documents[0].text, "alpha")
        self.assertIsNone(store.conn)


if __name__ == "__main__":
    unittest.main()
