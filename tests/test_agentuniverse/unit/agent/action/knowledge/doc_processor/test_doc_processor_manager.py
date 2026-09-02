# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_doc_processor_manager.py
"""Unit tests for the DocProcessorManager singleton."""

from typing import List

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.\
    doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_enum import ComponentEnum

_APP_CODE = "test_app.doc_processor.splitter"


class _FakeDocProcessor(DocProcessor):
    """A minimal DocProcessor used to exercise manager registration."""

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        return origin_docs


class TestDocProcessorManager:
    """Singleton identity and pool registration, never needing app config."""

    @pytest.fixture
    def manager(self):
        """The shared DocProcessorManager singleton."""
        return DocProcessorManager()

    @pytest.fixture(autouse=True)
    def restore_pool(self, manager):
        """Snapshot and restore the shared pool around every test."""
        saved = dict(manager._instance_obj_map)
        yield
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(saved)

    def test_singleton_identity(self, manager):
        assert manager is DocProcessorManager()
        assert manager._component_type is ComponentEnum.DOC_PROCESSOR

    def test_register_then_get_returns_independent_copy(self, manager):
        processor = _FakeDocProcessor(name="splitter")
        manager.register(_APP_CODE, processor)
        got = manager.get_instance_obj("splitter", appname="test_app")
        assert got is not processor
        assert got.name == "splitter"

    def test_get_with_new_instance_false_returns_registered_object(self,
                                                                   manager):
        processor = _FakeDocProcessor(name="splitter")
        manager.register(_APP_CODE, processor)
        raw = manager.get_instance_obj("splitter", appname="test_app",
                                       new_instance=False)
        assert raw is processor

    def test_unregister_removes_component(self, manager):
        manager.register(_APP_CODE, _FakeDocProcessor(name="splitter"))
        manager.unregister(_APP_CODE)
        assert manager.get_instance_name_list() == []
        assert manager.get_instance_obj("splitter", appname="test_app") is None

    def test_duplicate_register_keeps_original(self, manager):
        first = _FakeDocProcessor(name="splitter")
        manager.register(_APP_CODE, first)
        manager.register(_APP_CODE, _FakeDocProcessor(name="splitter"))
        assert manager.get_instance_name_list() == [_APP_CODE]
        assert manager.get_instance_obj("splitter", appname="test_app",
                                        new_instance=False) is first

    def test_unregistered_lookup_returns_none(self, manager):
        assert manager.get_instance_obj("missing", appname="test_app") is None

    def test_default_symbol_registers_default_instance(self, manager):
        processor = _FakeDocProcessor(name="splitter", default_symbol=True)
        manager.register(_APP_CODE, processor)
        assert "__default_instance__" in manager.get_instance_name_list()
        assert manager.get_default_instance() is processor


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
