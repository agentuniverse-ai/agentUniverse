# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_log_sink_manager.py

"""Unit tests for the singleton LogSinkManager registry."""

import pytest

from agentuniverse.base.util.logging.log_sink.log_sink import LogSink
from agentuniverse.base.util.logging.log_sink.log_sink_manager import     LogSinkManager
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    return LogSinkManager()


@pytest.fixture
def sink():
    return LogSink(name="test_sink")


@pytest.fixture(autouse=True)
def clean_manager(manager):
    baseline = set(manager.get_instance_name_list())
    yield
    for name in list(manager.get_instance_name_list()):
        if name not in baseline:
            manager.unregister(name)


class TestLogSinkManager:
    """Test LogSinkManager registry semantics."""

    def test_singleton_identity(self):
        assert LogSinkManager() is LogSinkManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.LOG_SINK

    def test_register_and_list(self, manager, sink):
        manager.register("sink1", sink)
        manager.register("sink2", LogSink(name="other"))
        assert manager.get_instance_name_list() == ["sink1", "sink2"]

    def test_duplicate_register_keeps_first(self, manager, sink):
        manager.register("sink1", sink)
        manager.register("sink1", LogSink(name="replacement"))
        assert manager.get_instance_name_list() == ["sink1"]
        assert manager.get_instance_obj_list()[0] is sink

    def test_unregister_removes_instance(self, manager, sink):
        manager.register("sink1", sink)
        manager.unregister("sink1")
        assert manager.get_instance_name_list() == []

    def test_default_symbol_registers_default_instance(self, manager):
        default = LogSink(name="default_sink", default_symbol=True)
        manager.register("sink1", default)
        assert "__default_instance__" in manager.get_instance_name_list()
        assert manager.get_default_instance() is default

    def test_non_default_symbol_skips_default_instance(self, manager, sink):
        manager.register("sink1", sink)
        assert "__default_instance__" not in manager.get_instance_name_list()
