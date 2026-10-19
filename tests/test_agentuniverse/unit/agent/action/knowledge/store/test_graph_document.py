# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_graph_document.py

"""Unit tests for GraphDocument, a Document subclass holding graph data."""

import pandas as pd
import pytest

from agentuniverse.agent.action.knowledge.store.graph_document import \
    GraphDocument


@pytest.fixture
def graph_frame():
    return pd.DataFrame({"name": ["Alice", "Bob"],
                         "age": [30, 25]})


class TestGraphDocument:
    """Test GraphDocument construction, ids and conversions."""

    def test_default_graph_data_is_none(self):
        doc = GraphDocument(text="query result")
        assert doc.graph_data is None

    def test_graph_data_roundtrip(self, graph_frame):
        doc = GraphDocument(text="query result", graph_data=graph_frame)
        assert doc.graph_data.equals(graph_frame)

    def test_document_fields_defaults(self, graph_frame):
        doc = GraphDocument(text="query result", graph_data=graph_frame)
        assert doc.text == "query result"
        assert doc.metadata is None
        assert doc.keywords == set()
        assert doc.embedding == []

    def test_deterministic_id_from_text(self):
        first = GraphDocument(text="same text")
        second = GraphDocument(text="same text")
        assert first.id == second.id

    def test_distinct_text_yields_distinct_id(self):
        assert (GraphDocument(text="text one").id
                != GraphDocument(text="text two").id)

    def test_metadata_can_be_set(self):
        doc = GraphDocument(text="text", metadata={"source": "neo4j"})
        assert doc.metadata == {"source": "neo4j"}

    def test_as_langchain_returns_langchain_document(self, graph_frame):
        doc = GraphDocument(text="payload", graph_data=graph_frame,
                            metadata={"source": "neo4j"})
        lc_doc = doc.as_langchain()
        assert lc_doc.page_content == "payload"
        assert lc_doc.metadata == {"source": "neo4j"}
