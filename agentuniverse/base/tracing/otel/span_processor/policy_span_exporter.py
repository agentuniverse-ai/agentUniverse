"""Opt-in, allowlisted export views of completed OpenTelemetry spans."""

import math
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Event, ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.trace import SpanContext, Status


@dataclass(frozen=True)
class ExportField:
    """Accept one exact scalar type, optionally a bounded homogeneous sequence.

    Oversized values are omitted, never partially exported. ``values`` can
    restrict string values (useful for exporter routing attributes).
    """

    kind: type
    max_length: int = 128
    max_items: int = 0
    values: frozenset[str] | None = None

    def __post_init__(self):
        if self.kind not in (str, bool, int, float):
            raise ValueError("kind must be str, bool, int, or float")
        for value in (self.max_length, self.max_items):
            if type(value) is not int or value < 0:
                raise ValueError("limits must be nonnegative integers")
        if self.values is not None:
            if self.kind is not str or any(type(v) is not str for v in self.values):
                raise ValueError("values requires a collection of strings")
            object.__setattr__(self, "values", frozenset(self.values))

    def accepts(self, value):
        """Return whether the value satisfies this field's export contract."""
        if isinstance(value, (tuple, list)):
            return 0 < len(value) <= self.max_items and all(self._scalar(v) for v in value)
        return self._scalar(value)

    def _scalar(self, value):
        if type(value) is not self.kind:
            return False
        if self.kind is str:
            return len(value) <= self.max_length and (self.values is None or value in self.values)
        if self.kind is int:
            return -(2**63) <= value < 2**63
        return self.kind is not float or math.isfinite(value)


@dataclass(frozen=True)
class SpanExportPolicy:
    """Explicit field rules; all free text and payload surfaces default closed.

    Names must match literal approved names. Events not present in ``events``
    are dropped. Resource rules are separate from span attribute rules.
    """

    attributes: Mapping[str, ExportField] = field(default_factory=dict)
    resources: Mapping[str, ExportField] = field(default_factory=dict)
    events: Mapping[str, Mapping[str, ExportField]] = field(default_factory=dict)
    span_names: frozenset[str] = frozenset()
    max_events: int = 16

    def __post_init__(self):
        def rules(mapping):
            if any(type(k) is not str or not isinstance(v, ExportField) for k, v in mapping.items()):
                raise ValueError("field rules must map strings to ExportField")
            return MappingProxyType(dict(mapping))

        if type(self.max_events) is not int or self.max_events < 0:
            raise ValueError("max_events must be a nonnegative integer")
        if any(type(n) is not str for n in self.span_names):
            raise ValueError("span_names must contain strings")
        if any(type(n) is not str for n in self.events):
            raise ValueError("event names must be strings")
        object.__setattr__(self, "attributes", rules(self.attributes))
        object.__setattr__(self, "resources", rules(self.resources))
        object.__setattr__(
            self, "events", MappingProxyType({name: rules(attrs) for name, attrs in self.events.items()})
        )
        object.__setattr__(self, "span_names", frozenset(self.span_names))

    @staticmethod
    def _filter(attributes, rules):
        return {
            key: tuple(value) if isinstance(value, (list, tuple)) else value
            for key, value in (attributes or {}).items()
            if key in rules and rules[key].accepts(value)
        }

    @staticmethod
    def _context(context):
        if context is None:
            return None
        # Trace state can contain vendor-controlled text; preserve only IDs/flags.
        return SpanContext(context.trace_id, context.span_id, context.is_remote, context.trace_flags)

    def project(self, span: ReadableSpan) -> ReadableSpan:
        """Build a fresh export view without mutating the original span."""
        events = []
        for event in span.events:
            if len(events) >= self.max_events:
                break
            if event.name in self.events:
                events.append(
                    Event(event.name, self._filter(event.attributes, self.events[event.name]), event.timestamp)
                )
        return ReadableSpan(
            name=span.name if span.name in self.span_names else "span",
            context=self._context(span.context),
            parent=self._context(span.parent),
            resource=Resource(self._filter(span.resource.attributes, self.resources)),
            attributes=self._filter(span.attributes, self.attributes),
            events=events,
            links=(),
            kind=span.kind,
            status=Status(span.status.status_code),
            start_time=span.start_time,
            end_time=span.end_time,
            instrumentation_scope=InstrumentationScope("agentuniverse.export_policy"),
        )


class PolicySpanExporter(SpanExporter):
    """Apply a policy before calling exactly one downstream exporter.

    Install this wrapper on every exporting processor. Other exporters,
    instrumentation logs, and metrics are outside this boundary. Failures never
    retry with original spans. Shutdown/flush belong to the wrapped exporter.
    """

    def __init__(self, exporter: SpanExporter, policy: SpanExportPolicy | None = None):
        self.exporter = exporter
        self.policy = policy if policy is not None else SpanExportPolicy()

    def export(self, spans):
        try:
            projected = tuple(self.policy.project(span) for span in spans)
            return self.exporter.export(projected)
        except Exception:
            return SpanExportResult.FAILURE

    def force_flush(self, timeout_millis=30000):
        return self.exporter.force_flush(timeout_millis=timeout_millis)

    def shutdown(self):
        return self.exporter.shutdown()
