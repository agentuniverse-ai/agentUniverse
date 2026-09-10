"""Regression tests for non-blocking OpenTelemetry failure paths."""

import unittest
from unittest.mock import MagicMock, patch

from opentelemetry.context.context import Context

from agentuniverse.base.tracing.otel.instrumentation.llm import llm_instrumentor as llm_instrumentor_module
from agentuniverse.base.tracing.otel.instrumentation.llm.llm_instrumentor import LLMSpanManager
from agentuniverse.base.tracing.otel.propagator import au_session_propagator as session_propagator_module
from agentuniverse.base.tracing.otel.propagator.au_session_propagator import AUSessionPropagator

_SESSION_LOGGER = "agentuniverse.base.tracing.otel.propagator.au_session_propagator"
_LLM_LOGGER = "agentuniverse.base.tracing.otel.instrumentation.llm.llm_instrumentor"


class TestNonCriticalOtelFailureLogging(unittest.TestCase):
    """Tracing failures are visible without interrupting application work."""

    def test_session_attribute_failure_is_logged_and_extracts_context(self) -> None:
        propagator = AUSessionPropagator()
        getter = MagicMock()
        getter.get.return_value = ["session-123"]
        span = MagicMock()
        span.set_attribute.side_effect = RuntimeError("attribute unavailable")

        with (
            patch.object(session_propagator_module.trace, "get_current_span", return_value=span),
            patch.object(session_propagator_module, "set_session_id"),
            self.assertLogs(_SESSION_LOGGER, level="DEBUG") as logs,
        ):
            context = propagator.extract({}, getter=getter)

        self.assertIsInstance(context, Context)
        span.set_attribute.assert_called_once_with(session_propagator_module.SPAN_SESSION_ID_KEY, "session-123")
        self.assertTrue(any("set session ID span attribute" in record for record in logs.output))

    def test_token_usage_failure_is_logged_and_cleanup_completes(self) -> None:
        span = MagicMock()
        span.context.span_id = 101
        span.parent.span_id = 100
        usage = MagicMock()
        manager = LLMSpanManager(MagicMock(), "test-llm")
        manager.span = span

        with (
            patch.object(llm_instrumentor_module, "get_current_token_usage", return_value=usage),
            patch.object(
                llm_instrumentor_module,
                "add_current_token_usage_to_parent",
                side_effect=RuntimeError("parent unavailable"),
            ) as add_to_parent,
            patch.object(llm_instrumentor_module.Monitor, "pop_invocation_chain"),
            self.assertLogs(_LLM_LOGGER, level="DEBUG") as logs,
        ):
            manager.cleanup()

        add_to_parent.assert_called_once_with(usage, 100)
        span.end.assert_called_once_with()
        self.assertIsNone(manager.span)
        self.assertTrue(any("propagate token usage to parent span" in record for record in logs.output))


if __name__ == "__main__":
    unittest.main()
