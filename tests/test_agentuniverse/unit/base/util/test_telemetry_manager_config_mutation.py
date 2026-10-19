# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from opentelemetry.sdk.resources import Resource

from agentuniverse.base.tracing.otel.telemetry_manager import TelemetryManager

SESSION_SPAN_PROCESSOR = {
    "class": "agentuniverse.base.tracing.otel.span_processor."
             "session_span_processor.SessionSpanProcessor"
}


def test_build_tracer_provider_does_not_mutate_caller_processors():
    conf = {"processors": [dict(SESSION_SPAN_PROCESSOR)]}

    TelemetryManager()._build_tracer_provider(conf, Resource.create())

    assert conf["processors"] == [SESSION_SPAN_PROCESSOR]


def test_setup_propagator_does_not_mutate_caller_propagators():
    conf = {"propagators": []}

    TelemetryManager()._setup_propagator(conf)

    assert conf["propagators"] == []
