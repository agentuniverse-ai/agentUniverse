# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_log_sink_manager.py
"""Unit tests for LogSinkManager."""

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.logging.log_sink.log_sink import LogSink
from agentuniverse.base.util.logging.log_sink.log_sink_manager import LogSinkManager

APP = "test_app"


def _code(name: str) -> str:
    """Build the full instance code the manager resolves internally."""
    return f"{APP}.log_sink.{name}"


class TestLogSinkManager:
    """Test LogSinkManager registration and lookup behavior."""

    @pytest.fixture
    def manager(self):
        """Return the singleton with its instance map reset for isolation."""
        m = LogSinkManager()
        m._instance_obj_map = {}
        yield m

    def test_singleton_identity(self):
        """The manager is a singleton returning the same instance."""
        assert LogSinkManager() is LogSinkManager()

    def test_component_type_is_log_sink(self, manager):
        """The manager is bound to the LOG_SINK component type."""
        assert manager._component_type == ComponentEnum.LOG_SINK

    def test_register_then_get_same_instance(self, manager):
        """A registered instance is returned unchanged when new_instance=False."""
        obj = LogSink(name="s1")
        manager.register(_code("s1"), obj)
        assert manager.get_instance_obj("s1", appname=APP, new_instance=False) is obj

    def test_get_instance_obj_returns_independent_copy(self, manager):
        """new_instance=True returns a distinct object of the same type."""
        obj = LogSink(name="s2")
        manager.register(_code("s2"), obj)
        copy = manager.get_instance_obj("s2", appname=APP, new_instance=True)
        assert copy is not obj
        assert type(copy) is type(obj)
        assert copy.name == "s2"

    def test_get_instance_obj_missing_returns_none(self, manager):
        """A missing component returns None when strict is False."""
        assert manager.get_instance_obj("ghost", appname=APP, new_instance=False) is None

    def test_get_instance_obj_missing_strict_raises(self, manager):
        """A missing component raises ValueError when strict is True."""
        with pytest.raises(ValueError):
            manager.get_instance_obj("ghost", appname=APP, strict=True)

    def test_register_default_symbol_exposes_default(self, manager):
        """Registering a default_symbol instance exposes it as the default."""
        obj = LogSink(name="s3")
        obj.default_symbol = True
        manager.register(_code("s3"), obj)
        assert manager.get_default_instance() is obj

    def test_unregister_removes_named_instance(self, manager):
        """After unregister, the named instance is no longer resolvable."""
        obj = LogSink(name="s4")
        manager.register(_code("s4"), obj)
        manager.unregister(_code("s4"))
        assert manager.get_instance_obj("s4", appname=APP, new_instance=False) is None
