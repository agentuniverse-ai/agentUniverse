# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: test_duplicate_remover.py

"""
Unit tests for DuplicateRemover.

The remover is pure Python and dependency-free, so the suite is deterministic
and runs offline. It covers: basic dedup, the keep_first / keep_last policies,
order preservation, SHA-256 determinism, the hash_key / text_field identity
sources, whitespace/case normalization, metadata stat stamping, config loading
through ComponentConfiger (as the YAML loader does), and edge cases.
"""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.duplicate_remover import \
    DuplicateRemover
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer


class TestBasicDedup(unittest.TestCase):
    """Core dedup behaviour and the keep_first policy."""

    def setUp(self) -> None:
        self.r = DuplicateRemover()

    def test_removes_exact_duplicates(self) -> None:
        docs = [
            Document(text="alpha"),
            Document(text="beta"),
            Document(text="alpha"),   # dup of first
            Document(text="gamma"),
            Document(text="beta"),    # dup of second
        ]
        result = self.r._process_docs(docs)
        self.assertEqual([d.text for d in result], ["alpha", "beta", "gamma"])

    def test_keeps_first_occurrence_by_default(self) -> None:
        # The first "alpha" carries metadata that lets us tell them apart.
        docs = [
            Document(text="alpha", metadata={"order": 1}),
            Document(text="alpha", metadata={"order": 2}),
            Document(text="alpha", metadata={"order": 3}),
        ]
        result = self.r._process_docs(docs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata["order"], 1)

    def test_keep_last_occurrence(self) -> None:
        self.r.keep_first = False
        docs = [
            Document(text="alpha", metadata={"order": 1}),
            Document(text="alpha", metadata={"order": 2}),
            Document(text="alpha", metadata={"order": 3}),
        ]
        result = self.r._process_docs(docs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].metadata["order"], 3)

    def test_no_duplicates_pass_through(self) -> None:
        docs = [Document(text="a"), Document(text="b"), Document(text="c")]
        result = self.r._process_docs(docs)
        self.assertEqual([d.text for d in result], ["a", "b", "c"])

    def test_empty_input_returns_empty(self) -> None:
        self.assertEqual(self.r._process_docs([]), [])


class TestOrdering(unittest.TestCase):
    """Order preservation for both keep policies."""

    def test_keep_first_preserves_input_order(self) -> None:
        r = DuplicateRemover()
        docs = [
            Document(text="c"), Document(text="a"), Document(text="b"),
            Document(text="a"),  # dup
        ]
        result = r._process_docs(docs)
        self.assertEqual([d.text for d in result], ["c", "a", "b"])

    def test_keep_last_preserves_input_order_of_last_occurrences(self) -> None:
        r = DuplicateRemover()
        r.keep_first = False
        docs = [
            Document(text="a", metadata={"i": 0}),
            Document(text="b", metadata={"i": 1}),
            Document(text="a", metadata={"i": 2}),  # last 'a'
        ]
        result = r._process_docs(docs)
        # last 'a' (i=2) is kept, and 'b' (i=1); input-relative order is b, a.
        texts = [d.metadata["i"] for d in result]
        self.assertEqual(texts, [1, 2])


class TestIdentitySources(unittest.TestCase):
    """hash_key and text_field identity resolution."""

    def test_hash_is_sha256_of_text(self) -> None:
        import hashlib
        r = DuplicateRemover()
        expected = hashlib.sha256("hello".encode("utf-8")).hexdigest()
        doc = Document(text="hello")
        self.assertEqual(r._identity(doc), expected)

    def test_identity_is_deterministic(self) -> None:
        r = DuplicateRemover()
        d1 = Document(text="same content")
        d2 = Document(text="same content")
        self.assertEqual(r._identity(d1), r._identity(d2))

    def test_hash_key_metadata_used_when_configured(self) -> None:
        r = DuplicateRemover()
        r.hash_key = "precomputed_hash"
        docs = [
            Document(text="different text", metadata={"precomputed_hash": "H1"}),
            Document(text="also different", metadata={"precomputed_hash": "H1"}),
            Document(text="unique", metadata={"precomputed_hash": "H2"}),
        ]
        result = r._process_docs(docs)
        self.assertEqual(len(result), 2)

    def test_text_field_metadata_fallback(self) -> None:
        r = DuplicateRemover()
        r.text_field = "canonical"
        docs = [
            Document(text="", metadata={"canonical": "x"}),
            Document(text="", metadata={"canonical": "x"}),  # dup
            Document(text="", metadata={"canonical": "y"}),
        ]
        result = r._process_docs(docs)
        self.assertEqual(len(result), 2)


class TestNormalization(unittest.TestCase):
    """Optional whitespace / case normalization before hashing."""

    def test_default_treats_whitespace_diff_as_distinct(self) -> None:
        r = DuplicateRemover()
        docs = [Document(text="a b"), Document(text="a  b")]
        self.assertEqual(len(r._process_docs(docs)), 2)

    def test_normalize_whitespace_collapses_runs(self) -> None:
        r = DuplicateRemover()
        r.normalize_whitespace = True
        docs = [Document(text="a b"), Document(text="a  b"), Document(text=" a b ")]
        self.assertEqual(len(r._process_docs(docs)), 1)

    def test_ignore_case(self) -> None:
        r = DuplicateRemover()
        r.ignore_case = True
        docs = [Document(text="Hello"), Document(text="HELLO")]
        self.assertEqual(len(r._process_docs(docs)), 1)


class TestMetadataAndQuery(unittest.TestCase):
    """Metadata stat stamping and query-argument handling."""

    def test_stats_stamped_with_group_size(self) -> None:
        r = DuplicateRemover()
        docs = [
            Document(text="alpha"), Document(text="alpha"), Document(text="alpha"),
        ]
        result = r._process_docs(docs)
        self.assertEqual(result[0].metadata["duplicate_stats"]["duplicate_group_size"], 3)

    def test_stats_key_disabled(self) -> None:
        r = DuplicateRemover()
        r.record_stats_key = None
        docs = [Document(text="alpha"), Document(text="alpha")]
        result = r._process_docs(docs)
        # No stats are written, so metadata is left untouched (None for a doc
        # that never had any).
        self.assertNotIn(
            "duplicate_stats", result[0].metadata or {})

    def test_query_argument_ignored(self) -> None:
        r = DuplicateRemover()
        docs = [Document(text="a"), Document(text="a")]
        result = r._process_docs(docs, query=Query(query_str="anything"))
        self.assertEqual(len(result), 1)


class TestConfiguration(unittest.TestCase):
    """Loading parameters through ComponentConfiger (as the YAML loader does)."""

    def _configer(self, config: dict) -> ComponentConfiger:
        cfg = Configer()
        cfg.value = config
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        if not hasattr(configer, "name"):
            configer.name = config.get("name", "duplicate_remover")
        if not hasattr(configer, "description"):
            configer.description = config.get("description", "")
        return configer

    def test_load_valid_config(self) -> None:
        configer = self._configer({
            "name": "duplicate_remover",
            "hash_key": "doc_hash",
            "keep_first": False,
            "normalize_whitespace": True,
            "ignore_case": True,
        })
        r = DuplicateRemover()
        r._initialize_by_component_configer(configer)
        self.assertEqual(r.hash_key, "doc_hash")
        self.assertFalse(r.keep_first)
        self.assertTrue(r.normalize_whitespace)
        self.assertTrue(r.ignore_case)

    def test_keep_first_string_coerced_to_bool(self) -> None:
        # YAML loaders sometimes hand back strings; bool() must handle it.
        configer = self._configer({"keep_first": "false"})
        r = DuplicateRemover()
        r._initialize_by_component_configer(configer)
        self.assertFalse(r.keep_first)


if __name__ == "__main__":
    unittest.main()
