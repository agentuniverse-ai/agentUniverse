# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_reader.py
"""Unit tests for the Reader base class."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_base import ComponentEnum


class _DummyReader(Reader):
    """Concrete Reader subclass used to exercise base-class behaviour."""

    def _load_data(self, *args, **kwargs):
        """Turn the first positional argument into a Document."""
        text = str(args[0]) if args else ""
        return [Document(text=text, metadata=dict(kwargs))]


class TestReader:
    """Test the Reader base class."""

    @pytest.fixture
    def reader(self):
        """Create a concrete reader instance for testing."""
        return _DummyReader()

    def test_component_type_is_reader(self, reader):
        """The reader component type should be READER."""
        assert reader.component_type == ComponentEnum.READER

    def test_default_name_and_description_are_none(self, reader):
        """Name and description should default to None."""
        assert reader.name is None
        assert reader.description is None

    def test_reader_is_abstract(self):
        """The abstract Reader class cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Reader()

    def test_load_data_delegates_to_load_data(self, reader):
        """load_data should delegate to the private _load_data method."""
        docs = reader.load_data("sample.txt")
        assert len(docs) == 1
        assert isinstance(docs[0], Document)
        assert docs[0].text == "sample.txt"

    def test_load_data_forwards_kwargs(self, reader):
        """Keyword arguments should reach the private _load_data method."""
        docs = reader.load_data("f.txt", ext_info={"chapter": 1})
        assert docs[0].metadata == {"ext_info": {"chapter": 1}}

    def test_load_data_without_arguments(self, reader):
        """Calling load_data without arguments should not raise."""
        docs = reader.load_data()
        assert len(docs) == 1
        assert docs[0].text == ""

    def test_initialize_by_component_configer(self, reader):
        """Initialization should copy name and description from configer."""
        configer = SimpleNamespace(name="csv_reader", description="reads csv")
        result = reader._initialize_by_component_configer(configer)
        assert result is reader
        assert reader.name == "csv_reader"
        assert reader.description == "reads csv"
