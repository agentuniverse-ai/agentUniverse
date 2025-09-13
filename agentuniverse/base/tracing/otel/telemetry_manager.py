# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/28 17:49
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: TelemetryManager.py

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import importlib
from typing import Any, Dict, List, Optional

from opentelemetry import metrics, propagate, trace
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

__all__ = ["TelemetryManager"]

DEFAULT_SPAN_PROCESSORS = [
    {"class": "agentuniverse.base.tracing.otel.span_processor.session_span_processor.SessionSpanProcessor"}
]
DEFAULT_TRACE_PROPAGATORS = [
    "agentuniverse.base.tracing.otel.propagator.au_session_propagator.AUSessionPropagator"
]


class TelemetryManager:
    """One‑shot factory that wires OTEL trace / metric pipeline from a dict."""

    _initialized: bool = False

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def init_from_config(self, otel_conf: Dict[str, Any]) -> None:  # noqa: C901
        """Initialize OpenTelemetry according to *otel_conf*.

        Subsequent calls are *no‑ops*.
        """
        if not otel_conf or self._initialized:
            return

        # ---- activate ------
        activate = otel_conf.get("activate", True)
        if isinstance(activate, str) and activate.lower() == "false":
            return

        if not activate:
            return

        # 0. ----- Resource -------------------
        resource = Resource.create(
            {
                "service.name": otel_conf.get("service_name", "agentUniverse"),
                **otel_conf.get("resource", {}),
            }
        )

        # 1. ----- Tracer provider  ----------------------------------------
        tracer_provider = self._build_tracer_provider(otel_conf, resource)

        # 2. ----- Global propagator  --------------------------------------
        self._setup_propagator(otel_conf)

        # 3. ----- Meter provider  -----------------------------------------
        self._setup_metrics(otel_conf, resource)

        # 4. ----- Activate & Instrument  ----------------------------------
        trace.set_tracer_provider(tracer_provider)
        self._instrument(otel_conf.get("instrumentations", []))

        self._initialized = True

    @staticmethod
    def force_flush(timeout_ms: int = 5_000) -> None:
        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, "force_flush"):
            tracer_provider.force_flush(timeout_millis=timeout_ms)
        if hasattr(tracer_provider, "shutdown"):
            tracer_provider.shutdown()

        meter_provider = metrics.get_meter_provider()
        if hasattr(meter_provider, "force_flush"):
            meter_provider.force_flush(timeout_millis=timeout_ms)
        if hasattr(meter_provider, "shutdown"):
            meter_provider.shutdown()

    # -------- Trace helpers ---------------------------------------------
    def _build_tracer_provider(
        self, otel_conf: Dict[str, Any], resource: Resource
    ) -> TracerProvider:
        provider_cls = self._import_class(
            otel_conf.get(
                "provider_class", "opentelemetry.sdk.trace.TracerProvider"
            )
        )
        provider_kwargs: Dict[str, Any] = {"resource": resource}

        id_gen_path = otel_conf.get("id_generator_class")
        if id_gen_path:
            provider_kwargs["id_generator"] = self._import_class(id_gen_path)()

        tracer_provider: TracerProvider = provider_cls(**provider_kwargs)

        processors = otel_conf.get("processors", [])
        processors.extend(DEFAULT_SPAN_PROCESSORS)
        self._attach_span_processors(
            tracer_provider, processors
        )
        return tracer_provider

    def _attach_span_processors(
        self,
        provider: TracerProvider,
        processors_conf: List[Dict[str, Any]],
    ) -> None:
        """Attach *processors* to the given *provider*."""

        for proc_conf in processors_conf:
            proc_cls = self._import_class(proc_conf["class"])
            proc_args = dict(proc_conf.get("args", {}))

            exporter_conf = proc_conf.get("exporter")
            if exporter_conf:
                exporter_cls = self._import_class(exporter_conf["class"])
                exporter = exporter_cls(**exporter_conf.get("args", {}))
                span_processor = proc_cls(exporter, **proc_args)
            else:
                span_processor = proc_cls(**proc_args)

            provider.add_span_processor(span_processor)

    # -------- Propagator -------------------------------------------------
    def _setup_propagator(self, otel_conf: Dict[str, Any]) -> None:
        """Setup context propagators"""
        propagators_conf = otel_conf.get("propagators", [])
        propagators_conf.extend(DEFAULT_TRACE_PROPAGATORS)

        propagators = []
        for prop_conf in propagators_conf:
            if isinstance(prop_conf, str):
                # Simple class path
                prop_cls = self._import_class(prop_conf)
                propagators.append(prop_cls())
            elif isinstance(prop_conf, dict):
                # With configuration
                prop_cls = self._import_class(prop_conf["class"])
                propagators.append(prop_cls(**prop_conf.get("args", {})))

        # Set composite propagator
        composite = CompositePropagator(propagators)
        propagate.set_global_textmap(composite)

    # -------- Metric helpers --------------------------------------------
    def _setup_metrics(
        self, otel_conf: Dict[str, Any], resource: Resource
    ) -> Optional[MeterProvider]:
        readers_conf: List[Dict[str, Any]] = otel_conf.get("metric_readers", [])
        if not readers_conf:
            return None  # metrics disabled

        meter_provider_cls = self._import_class(
            otel_conf.get(
                "metric_provider_class", "opentelemetry.sdk.metrics.MeterProvider"
            )
        )

        readers = []
        for reader_conf in readers_conf:
            reader_cls = self._import_class(reader_conf["class"])
            reader_args = dict(reader_conf.get("args", {}))

            exporter_conf = reader_conf.get("exporter")
            if exporter_conf:
                exporter_cls = self._import_class(exporter_conf["class"])
                exporter = exporter_cls(**exporter_conf.get("args", {}))
                reader = reader_cls(exporter, **reader_args)
            else:
                reader = reader_cls(**reader_args)
            readers.append(reader)

        meter_provider = meter_provider_cls(
            resource=resource, metric_readers=readers
        )
        metrics.set_meter_provider(meter_provider)
        return meter_provider

    # -------- Instrumentation -------------------------------------------
    def _instrument(self, inst_paths: List[str]) -> None:
        for inst_path in inst_paths:
            inst_cls = self._import_class(inst_path)
            if hasattr(inst_cls, "instrument"):
                inst_cls().instrument()

    @staticmethod
    def _import_class(path: str):
        """Import ``path`` like ``pkg.mod:Class`` or ``pkg.mod.Class``."""
        if ":" in path:
            mod_path, cls_name = path.split(":", 1)
        else:
            mod_path, _, cls_name = path.rpartition(".")
        module = importlib.import_module(mod_path)
        return getattr(module, cls_name)
