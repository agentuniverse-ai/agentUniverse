# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_query_paraphraser.py
"""Unit tests for the QueryParaphraser base component."""

import pytest

from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser import \
    QueryParaphraser
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class _EchoParaphraser(QueryParaphraser):
    """Concrete paraphraser used by the tests; tags the query with a keyword."""

    def query_paraphrase(self, origin_query: Query) -> Query:
        origin_query.keywords.add("_echo_")
        return origin_query


class TestQueryParaphraser:
    """Test the abstract base class behavior of QueryParaphraser."""

    @pytest.fixture
    def paraphraser(self):
        """Create a concrete QueryParaphraser instance."""
        return _EchoParaphraser()

    def test_abstract_class_cannot_be_instantiated(self):
        """QueryParaphraser keeps query_paraphrase abstract."""
        with pytest.raises(TypeError):
            QueryParaphraser()

    def test_component_defaults(self, paraphraser):
        """Defaults: QUERY_PARAPHRASER type with unset name/description."""
        assert paraphraser.component_type == ComponentEnum.QUERY_PARAPHRASER
        assert paraphraser.name is None
        assert paraphraser.description is None
        assert paraphraser.default_symbol is False
        assert paraphraser.is_default_object() is False

    def test_query_paraphrase_dispatches_to_concrete(self, paraphraser):
        """query_paraphrase runs the concrete implementation on the query."""
        origin = Query(query_str="what is agentuniverse")
        result = paraphraser.query_paraphrase(origin)

        assert result is origin
        assert "_echo_" in origin.keywords
        assert origin.query_str == "what is agentuniverse"

    def test_initialize_sets_name_and_description(self, paraphraser):
        """Configer metadata is copied onto the component and self is returned."""
        configer = ComponentConfiger()
        configer.name = "demo_paraphraser"
        configer.description = "A demo paraphraser"

        returned = paraphraser.initialize_by_component_configer(configer)

        assert returned is paraphraser
        assert paraphraser.name == "demo_paraphraser"
        assert paraphraser.description == "A demo paraphraser"

    def test_initialize_keeps_values_when_configer_fields_empty(self, paraphraser):
        """Empty configer metadata never overwrites existing values."""
        paraphraser.name = "existing_name"
        paraphraser.description = "existing description"

        configer = ComponentConfiger()
        configer.name = None
        configer.description = None
        paraphraser.initialize_by_component_configer(configer)

        assert paraphraser.name == "existing_name"
        assert paraphraser.description == "existing description"

    def test_initialize_sets_default_symbol(self, paraphraser):
        """The default_symbol flag is propagated from the configer."""
        configer = ComponentConfiger()
        configer.name = "demo"
        configer.description = "demo"
        configer.default_symbol = True

        paraphraser.initialize_by_component_configer(configer)

        assert paraphraser.default_symbol is True
        assert paraphraser.is_default_object() is True
