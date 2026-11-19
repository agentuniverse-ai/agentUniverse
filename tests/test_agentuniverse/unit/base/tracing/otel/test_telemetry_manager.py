# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/02/10 10:00
# @Author  : Yue Wang
# @FileName: test_telemetry_manager.py
"""Unit tests for TelemetryManager config/import helpers."""

import json

import pytest

from agentuniverse.base.tracing.otel.telemetry_manager import TelemetryManager


class TestTelemetryManager:
    """Test TelemetryManager no-op paths and import helpers."""

    @pytest.fixture
    def manager(self):
        """Create a fresh TelemetryManager instance."""
        return TelemetryManager()

    def test_init_none_is_noop(self, manager):
        """A None config must not initialize anything."""
        assert manager.init_from_config(None) is None
        assert manager._initialized is False

    def test_init_empty_config_is_noop(self, manager):
        """An empty config must not initialize anything."""
        assert manager.init_from_config({}) is None
        assert manager._initialized is False

    def test_init_activate_false_bool_is_noop(self, manager):
        """activate=False must short-circuit before any OTEL setup."""
        assert manager.init_from_config({"activate": False}) is None
        assert manager._initialized is False

    def test_init_activate_false_string_is_noop(self, manager):
        """activate='false' (lower-case string) must also short-circuit."""
        assert manager.init_from_config({"activate": "false"}) is None
        assert manager._initialized is False

    def test_import_class_colon_notation(self, manager):
        """pkg.mod:Class notation must resolve to the class."""
        cls = manager._import_class("json:JSONDecoder")
        assert cls is json.JSONDecoder

    def test_import_class_dotted_notation(self, manager):
        """pkg.mod.Class notation must resolve to the class."""
        cls = manager._import_class("json.JSONDecoder")
        assert cls is json.JSONDecoder

    def test_import_class_missing_attr_raises(self, manager):
        """A missing attribute must raise AttributeError."""
        with pytest.raises(AttributeError):
            manager._import_class("json.NoSuchDecoder")

    def test_import_class_missing_module_raises(self, manager):
        """A missing module must raise ModuleNotFoundError."""
        with pytest.raises(ModuleNotFoundError):
            manager._import_class("no_such_module.Decoder")

    def test_setup_metrics_disabled_without_readers(self, manager):
        """No metric_readers configured means metrics are disabled (None)."""
        assert manager._setup_metrics({"metric_readers": []}, None) is None
        assert manager._setup_metrics({}, None) is None

    def test_instrument_empty_list_is_noop(self, manager):
        """An empty instrumentation list must not raise."""
        assert manager._instrument([]) is None
