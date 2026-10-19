# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_telemetry_manager.py
"""Unit tests for TelemetryManager."""

from unittest.mock import Mock, patch

import pytest

from agentuniverse.base.tracing.otel import telemetry_manager
from agentuniverse.base.tracing.otel.telemetry_manager import (
    DEFAULT_SPAN_PROCESSORS,
    DEFAULT_TRACE_PROPAGATORS,
    TelemetryManager,
)


class TestTelemetryManager:
    """Test the OTEL pipeline factory helpers."""

    def test_import_class_dot_form(self):
        """_import_class resolves a dotted module.Class path."""
        cls = TelemetryManager._import_class(
            "agentuniverse.base.tracing.otel.telemetry_manager.TelemetryManager"
        )
        assert cls is TelemetryManager

    def test_import_class_colon_form(self):
        """_import_class resolves a module:Class path."""
        cls = TelemetryManager._import_class(
            "agentuniverse.base.tracing.otel.telemetry_manager:TelemetryManager"
        )
        assert cls is TelemetryManager

    @pytest.mark.parametrize("conf", [{}, {"activate": "false"}, {"activate": False}])
    def test_inactive_config_is_noop(self, conf):
        """Empty or deactivate configs leave the instance uninitialized."""
        manager = TelemetryManager()
        manager.init_from_config(conf)
        assert manager._initialized is False

    def test_second_init_on_same_instance_is_noop(self):
        """After a successful init, later calls skip the pipeline steps."""
        manager = TelemetryManager()
        with patch.object(TelemetryManager, "_build_tracer_provider") as build, \
                patch.object(TelemetryManager, "_setup_propagator") as prop, \
                patch.object(TelemetryManager, "_setup_metrics") as metrics, \
                patch.object(TelemetryManager, "_instrument") as inst, \
                patch("agentuniverse.base.tracing.otel.telemetry_manager.trace.set_tracer_provider"):
            manager.init_from_config({"service_name": "x"})
            manager.init_from_config({"service_name": "y"})
        for mock in (build, prop, metrics, inst):
            assert mock.call_count == 1

    def test_force_flush_propagates_timeout(self):
        """force_flush forwards the timeout to tracer and meter providers."""
        tracer = Mock()
        meter = Mock()
        with patch.object(telemetry_manager.trace, "get_tracer_provider", return_value=tracer), \
                patch.object(telemetry_manager.metrics, "get_meter_provider", return_value=meter):
            TelemetryManager.force_flush(timeout_ms=123)
        tracer.force_flush.assert_called_once_with(timeout_millis=123)
        tracer.shutdown.assert_called_once_with()
        meter.force_flush.assert_called_once_with(timeout_millis=123)
        meter.shutdown.assert_called_once_with()

    def test_default_processor_and_propagator_lists(self):
        """Default span processor and propagator entries point at AU classes."""
        assert DEFAULT_SPAN_PROCESSORS == [{
            "class": "agentuniverse.base.tracing.otel.span_processor."
                     "session_span_processor.SessionSpanProcessor"
        }]
        assert DEFAULT_TRACE_PROPAGATORS == [
            "agentuniverse.base.tracing.otel.propagator."
            "au_session_propagator.AUSessionPropagator"
        ]
