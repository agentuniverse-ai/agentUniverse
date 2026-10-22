"""Session propagation contracts exercised with the real OpenTelemetry API."""

from concurrent.futures import ThreadPoolExecutor

import pytest
from opentelemetry import trace
from opentelemetry.baggage import get_baggage, set_baggage
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.context import Context
from opentelemetry.propagators import textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.sdk.trace import TracerProvider

from agentuniverse.base.tracing.au_trace_manager import (
    AuTraceManager, get_session_id, set_session_id,
)
from agentuniverse.base.tracing.otel.consts import (
    HTTP_HEADER_SESSION_ID_KEY, SESSION_ID_KEY, SPAN_SESSION_ID_KEY,
)
from agentuniverse.base.tracing.otel.propagator.au_session_propagator import (
    AUSessionPropagator,
)

KEYS = [HTTP_HEADER_SESSION_ID_KEY, SESSION_ID_KEY]


@pytest.fixture(autouse=True)
def isolated_session():
    manager = AuTraceManager()
    token = manager.context_instance.set(None)
    yield
    manager.context_instance.reset(token)


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("value", ["session-example", ["session-example", "second"]])
def test_extract_stores_first_value_as_scalar(key, value):
    initial = set_baggage("unrelated", "keep", Context())
    extracted = AUSessionPropagator().extract({key: value}, initial)
    assert get_baggage(key, extracted) == "session-example"
    assert get_baggage("unrelated", extracted) == "keep"
    assert get_baggage(key, initial) is None
    assert get_session_id() == "session-example"


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("reverse", [False, True])
def test_w3c_composite_round_trip_preserves_session(key, reverse):
    processors = [AUSessionPropagator(), W3CBaggagePropagator()]
    composite = CompositePropagator(processors[::-1] if reverse else processors)
    extracted = composite.extract({key: "session-example"})
    carrier = {}
    composite.inject(carrier, extracted)
    restored = W3CBaggagePropagator().extract(carrier)
    assert get_baggage(key, restored) == "session-example"
    assert carrier[HTTP_HEADER_SESSION_ID_KEY] == "session-example"
    assert carrier[SESSION_ID_KEY] == "session-example"


@pytest.mark.parametrize("key", KEYS)
def test_explicit_context_overrides_ambient_without_mutating_it(key):
    set_session_id("ambient-session")
    explicit = set_baggage(key, "explicit-session", Context())
    carrier = {}
    AUSessionPropagator().inject(carrier, explicit)
    assert carrier == dict.fromkeys(KEYS, "explicit-session")
    assert get_session_id() == "ambient-session"


def test_explicit_context_header_key_takes_precedence():
    explicit = set_baggage(SESSION_ID_KEY, "plain", Context())
    explicit = set_baggage(HTTP_HEADER_SESSION_ID_KEY, "header", explicit)
    carrier = {}
    AUSessionPropagator().inject(carrier, explicit)
    assert carrier == dict.fromkeys(KEYS, "header")


@pytest.mark.parametrize("value", ["", ["legacy-list"]])
def test_present_unusable_header_key_does_not_substitute_plain_key(value):
    explicit = set_baggage(SESSION_ID_KEY, "plain", Context())
    explicit = set_baggage(HTTP_HEADER_SESSION_ID_KEY, value, explicit)
    carrier = {}
    AUSessionPropagator().inject(carrier, explicit)
    assert carrier == {}


@pytest.mark.parametrize("value", [None, "", ["legacy-list"], 123])
def test_explicit_missing_or_non_string_session_never_uses_ambient(value):
    set_session_id("ambient-session")
    explicit = Context() if value is None else set_baggage(SESSION_ID_KEY, value, Context())
    carrier = {"unrelated": "keep"}
    AUSessionPropagator().inject(carrier, explicit)
    assert carrier == {"unrelated": "keep"}


@pytest.mark.parametrize("value", [None, "ambient-session"])
def test_omitted_context_preserves_ambient_behavior(value):
    set_session_id(value)
    carrier = {}
    AUSessionPropagator().inject(carrier)
    assert carrier == (dict.fromkeys(KEYS, value) if value else {})


def test_extract_header_precedence_and_span_attribute():
    provider = TracerProvider(shutdown_on_exit=False)
    try:
        with provider.get_tracer(__name__).start_span("example") as span:
            initial = trace.set_span_in_context(span, Context())
            extracted = AUSessionPropagator().extract({
                HTTP_HEADER_SESSION_ID_KEY: "header",
                SESSION_ID_KEY: "plain",
            }, initial)
            assert get_baggage(HTTP_HEADER_SESSION_ID_KEY, extracted) == "header"
            assert get_session_id() == "header"
            assert span.attributes[SPAN_SESSION_ID_KEY] == "header"
    finally:
        provider.shutdown()


def test_empty_carrier_preserves_supplied_context_and_session():
    set_session_id("existing")
    initial = set_baggage("unrelated", "keep", Context())
    assert AUSessionPropagator().extract({}, initial) is initial
    assert get_session_id() == "existing"


def test_custom_getter_and_setter():
    class PairGetter(textmap.Getter):
        def get(self, carrier, key):
            return [value for name, value in carrier if name == key] or None

        def keys(self, carrier):
            return [name for name, _ in carrier]

    class PairSetter(textmap.Setter):
        def set(self, carrier, key, value):
            carrier.append((key, value))

    propagator = AUSessionPropagator()
    extracted = propagator.extract([(SESSION_ID_KEY, "pair-session")], getter=PairGetter())
    carrier = []
    propagator.inject(carrier, extracted, PairSetter())
    assert carrier == [(key, "pair-session") for key in KEYS]


def test_parallel_explicit_contexts_stay_independent():
    def inject_session(number):
        manager = AuTraceManager()
        token = manager.context_instance.set(None)
        try:
            set_session_id("ambient")
            explicit = set_baggage(SESSION_ID_KEY, str(number), Context())
            carrier = {}
            AUSessionPropagator().inject(carrier, explicit)
            return carrier
        finally:
            manager.context_instance.reset(token)

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(inject_session, range(20)))
    assert results == [dict.fromkeys(KEYS, str(number)) for number in range(20)]
