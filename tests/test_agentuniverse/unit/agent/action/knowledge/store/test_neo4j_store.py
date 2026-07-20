# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for Neo4jStore node_ids_query construction.

These tests cover the Cypher-injection fix: node ids are bound as a query
parameter instead of interpolated into the query text, and the parsed payload
is validated as a list of integers.

neo4j_store imports the optional ``neo4j`` package at module load. The methods
under test are pure (they never touch the driver), so when ``neo4j`` is not
installed we stub it merely to make the module importable.
"""

import sys
import unittest
from unittest.mock import MagicMock

try:
    import neo4j  # noqa: F401
    _NEO4J_INSTALLED = True
except ImportError:
    _NEO4J_INSTALLED = False
    sys.modules.setdefault("neo4j", MagicMock())

from agentuniverse.agent.action.knowledge.store.neo4j_store import Neo4jStore


class TestNeo4jNodeIdsQuery(unittest.TestCase):
    """node_ids_query must parameterize ids and reject non-integer payloads."""

    def setUp(self):
        # No connection is made; the methods under test are pure.
        self.store = Neo4jStore()

    def test_build_node_ids_query_is_parameterized(self):
        query, params = self.store._build_node_ids_query([1, 2, 3])
        self.assertEqual(query, "MATCH (n) WHERE id(n) IN $au_node_ids RETURN n")
        # No id value is interpolated into the query text.
        self.assertNotIn("1", query.replace("$au_node_ids", ""))
        self.assertEqual(params, {"au_node_ids": [1, 2, 3]})

    def test_parse_node_ids_accepts_int_list(self):
        self.assertEqual(self.store._parse_node_ids("[1, 2, 3]"), [1, 2, 3])

    def test_parse_node_ids_rejects_injection_payload(self):
        # A payload that would inject Cypher if string-interpolated is rejected.
        with self.assertRaises(ValueError):
            self.store._parse_node_ids('["1) OR 1=1 OR id(n) IN (1"]')

    def test_parse_node_ids_rejects_non_list(self):
        with self.assertRaises(ValueError):
            self.store._parse_node_ids('"not a list"')
        with self.assertRaises(ValueError):
            self.store._parse_node_ids("42")

    def test_parse_node_ids_rejects_bool_float_and_empty(self):
        with self.assertRaises(ValueError):  # bool is an int subclass
            self.store._parse_node_ids("[true, 1]")
        with self.assertRaises(ValueError):  # floats are not node ids
            self.store._parse_node_ids("[1.5]")
        with self.assertRaises(ValueError):
            self.store._parse_node_ids("[]")

    def test_parse_node_ids_rejects_invalid_json(self):
        with self.assertRaises(ValueError):
            self.store._parse_node_ids("not json")


if __name__ == "__main__":
    unittest.main()
