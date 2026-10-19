# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_query.py

"""Unit tests for the Query knowledge-query model."""

import pytest

from agentuniverse.agent.action.knowledge.store.query import Query


class TestQuery:
    """Test Query defaults and field behavior."""

    def test_default_values(self):
        query = Query()
        assert query.query_str is None
        assert query.query_text_bundles == []
        assert query.query_image_bundles == []
        assert query.keywords == set()
        assert query.embeddings == []
        assert query.ext_info == {}
        assert query.similarity_top_k is None

    def test_construction_from_kwargs(self):
        query = Query(
            query_str="what is agent universe?",
            query_text_bundles=["what is agent universe?"],
            keywords={"agent", "universe"},
            embeddings=[[0.1, 0.2]],
            similarity_top_k=5,
        )
        assert query.query_str == "what is agent universe?"
        assert query.query_text_bundles == ["what is agent universe?"]
        assert query.keywords == {"agent", "universe"}
        assert query.embeddings == [[0.1, 0.2]]
        assert query.similarity_top_k == 5

    def test_ext_info_not_shared_between_instances(self):
        first = Query()
        first.ext_info["source"] = "user"
        second = Query()
        assert second.ext_info == {}
        assert second.ext_info is not first.ext_info

    def test_keywords_are_independent_sets(self):
        first = Query(keywords={"a"})
        first.keywords.add("b")
        second = Query(keywords={"a"})
        assert second.keywords == {"a"}

    def test_extra_fields_are_ignored(self):
        query = Query(query_str="x", unexpected_field=1)
        assert query.query_str == "x"
        with pytest.raises(AttributeError):
            query.unexpected_field

    def test_equality_between_equivalent_queries(self):
        assert Query(query_str="same") == Query(query_str="same")
        assert Query(query_str="same") != Query(query_str="other")
