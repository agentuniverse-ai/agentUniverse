"""Exercise opt-in mapping on real SDK spans and actual instrumented calls."""

import asyncio
import os
import subprocess
import time
from typing import Any

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.tracing.otel.instrumentation.gen_ai_semconv import GenAIAttributeAdapter, GenAIIdentity
from agentuniverse.base.tracing.otel.instrumentation.llm.llm_instrumentor import LLMInstrumentor
from agentuniverse.base.tracing.otel.instrumentation.tool.tool_instrumentor import ToolInstrumentor
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput, TokenUsage


class LocalLLM(LLM):
    supplied: Any = None
    failure: Any = None

    def get_num_tokens(self, text):
        return 99  # legacy Monitor estimate must never become GenAI usage

    def _call(self, *, streaming=False, **kwargs):
        if not streaming:
            if self.failure:
                raise self.failure
            return LLMOutput(text="local", usage=self.supplied, finish_reason="stop")

        def generate():
            yield LLMOutput(text="lo", usage=self.supplied)
            if self.failure:
                raise self.failure
            yield LLMOutput(text="cal", usage=self.supplied, finish_reason="stop")

        return generate()

    async def _acall(self, *, streaming=False, **kwargs):
        if not streaming:
            return self._call(streaming=False, **kwargs)

        async def generate():
            for chunk in self._call(streaming=True, **kwargs):
                await asyncio.sleep(0)
                yield chunk

        return generate()


class LocalTool(Tool):
    def execute(self, **kwargs):
        return LocalLLM(name="local", model_name="model").call(messages=[]).text

    async def async_execute(self, **kwargs):
        return (await LocalLLM(name="local", model_name="model").acall(messages=[])).text


@pytest.fixture
def telemetry(monkeypatch):
    monkeypatch.setattr(ApplicationConfigManager(), "_ApplicationConfigManager__app_configer", AppConfiger())
    sink = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(sink))
    adapter = GenAIAttributeAdapter(
        lambda llm, kwargs: GenAIIdentity("local-test", kwargs.get("model", llm.model_name))
    )
    llm_inst = LLMInstrumentor()
    tool_inst = ToolInstrumentor()
    adapter._test_instrumentor = llm_inst
    llm_inst.instrument(tracer_provider=provider, gen_ai_adapter=adapter)
    tool_inst.instrument(tracer_provider=provider, gen_ai_adapter=adapter)
    try:
        yield provider, sink, adapter
    finally:
        tool_inst.uninstrument()
        llm_inst.uninstrument()
        provider.shutdown()


def run(llm, mode):
    args = {"messages": [{"role": "user", "content": "synthetic"}], "model": "override"}
    if mode == "call":
        return llm.call(**args)
    if mode == "stream":
        return list(llm.call(streaming=True, **args))

    async def invoke():
        if mode == "acall":
            return await llm.acall(**args)
        return [chunk async for chunk in await llm.acall(streaming=True, **args)]

    return asyncio.run(invoke())


@pytest.mark.parametrize("mode", ["call", "acall", "stream", "astream"])
@pytest.mark.parametrize(
    "supplied", [None, TokenUsage(), TokenUsage(text_in=0, text_out=0), TokenUsage(text_in=3, text_out=2)]
)
def test_actual_calls_map_identity_and_only_supplied_usage(telemetry, mode, supplied):
    provider, sink, _ = telemetry
    with provider.get_tracer("test").start_as_current_span("parent") as parent:
        run(LocalLLM(name="local", model_name="configured", supplied=supplied), mode)
        assert trace.get_current_span().get_span_context().span_id == parent.get_span_context().span_id
    spans = sink.get_finished_spans()
    child = next(span for span in spans if span.name.startswith("au.llm"))
    assert child.parent.span_id == parent.get_span_context().span_id
    attrs = child.attributes
    assert attrs["au.gen_ai.semconv.version"] == "1.37.0"
    assert attrs["gen_ai.provider.name"] == "local-test"
    assert attrs["gen_ai.request.model"] == "override"
    assert attrs["gen_ai.operation.name"] == "chat"
    assert attrs["gen_ai.response.finish_reasons"] == ("stop",)
    if supplied is None or not supplied.model_fields_set:
        assert attrs["au.gen_ai.usage.status"] == "unknown"
        assert "gen_ai.usage.input_tokens" not in attrs
        assert "gen_ai.usage.output_tokens" not in attrs
    else:
        assert attrs["au.gen_ai.usage.status"] == "provided"
        assert attrs["gen_ai.usage.input_tokens"] == supplied.prompt_tokens
        assert attrs["gen_ai.usage.output_tokens"] == supplied.completion_tokens


@pytest.mark.parametrize("mode", ["call", "acall", "stream", "astream"])
@pytest.mark.parametrize("error", [ValueError("synthetic"), asyncio.CancelledError()])
def test_errors_and_cancellation_end_one_span(telemetry, mode, error):
    _, sink, _ = telemetry
    with pytest.raises(type(error)):
        run(LocalLLM(name="local", failure=error), mode)
    spans = sink.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].attributes["error.type"] == type(error).__name__
    assert spans[0].status.status_code.name == "ERROR"


@pytest.mark.parametrize("asynchronous", [False, True])
def test_tool_and_llm_parent_relationships(telemetry, asynchronous):
    _, sink, _ = telemetry
    tool = LocalTool(name="local-tool")
    if asynchronous:
        asyncio.run(tool.async_run())
    else:
        tool.run()
    spans = sink.get_finished_spans()
    llm = next(span for span in spans if span.name.startswith("au.llm"))
    tool_span = next(span for span in spans if span.name.startswith("au.tool"))
    assert llm.parent.span_id == tool_span.context.span_id
    assert tool_span.attributes["gen_ai.operation.name"] == "execute_tool"
    assert tool_span.attributes["gen_ai.tool.name"] == "local-tool"


def test_partial_usage_does_not_invent_other_direction(telemetry):
    provider, sink, adapter = telemetry
    with provider.get_tracer("test").start_as_current_span("partial") as span:
        adapter.observe_usage(span, TokenUsage(text_out=2))
    attrs = sink.get_finished_spans()[0].attributes
    assert attrs["gen_ai.usage.output_tokens"] == 2
    assert "gen_ai.usage.input_tokens" not in attrs
    assert attrs["au.gen_ai.usage.status"] == "partial"


def test_unknown_identity_and_resolver_failure_do_not_guess(telemetry):
    provider, sink, _ = telemetry

    def broken(llm, kwargs):
        raise ValueError("synthetic")

    for resolver in [lambda llm, kwargs: None, broken]:
        with provider.get_tracer("test").start_as_current_span("unknown") as span:
            GenAIAttributeAdapter(resolver).begin_llm(span, None, {})
    for span in sink.get_finished_spans():
        assert span.attributes["au.gen_ai.identity.status"] == "unknown"
        assert "gen_ai.provider.name" not in span.attributes


def test_invalid_usage_is_not_exported(telemetry):
    provider, sink, adapter = telemetry
    with provider.get_tracer("test").start_as_current_span("invalid") as span:
        adapter.observe_usage(span, TokenUsage(text_in=-1, text_out=2))
    attrs = sink.get_finished_spans()[0].attributes
    assert attrs["au.gen_ai.usage.status"] == "invalid"
    assert "gen_ai.usage.input_tokens" not in attrs


def test_default_instrumentation_does_not_emit_genai(telemetry):
    provider, sink, adapter = telemetry
    instrumentor = adapter._test_instrumentor
    instrumentor.uninstrument()
    instrumentor.instrument(tracer_provider=provider)
    LocalLLM(name="local").call(messages=[])
    attrs = sink.get_finished_spans()[0].attributes
    assert not any(key.startswith(("gen_ai.", "au.gen_ai.")) for key in attrs)


def test_real_task_cancellation_exports_and_restores_context(telemetry):
    provider, sink, _ = telemetry

    class WaitingLLM(LocalLLM):
        async def _acall(self, **kwargs):
            await asyncio.sleep(3600)

    async def invoke():
        with provider.get_tracer("test").start_as_current_span("parent") as parent:
            task = asyncio.create_task(WaitingLLM(name="local").acall(messages=[]))
            await asyncio.sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert trace.get_current_span().get_span_context() == parent.get_span_context()

    asyncio.run(invoke())
    spans = sink.get_finished_spans()
    assert len(spans) == 2
    assert spans[0].attributes["error.type"] == "CancelledError"


@pytest.mark.skipif(not os.getenv("AU_GENAI_COLLECTOR_CONTAINER"), reason="requires dedicated local collector")
def test_actual_otlp_collector_receives_mapped_span(telemetry):
    import requests
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    provider, sink, _ = telemetry
    # The opt-in integration test is restricted to this loopback test endpoint.
    session = requests.Session()
    session.trust_env = False
    exporter = OTLPSpanExporter(endpoint="http://127.0.0.1:14328/v1/traces", session=session)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    LocalLLM(name="local", model_name="collector-model", supplied=TokenUsage(text_in=7, text_out=4)).call(messages=[])
    assert provider.force_flush()
    span_id = f"{sink.get_finished_spans()[0].context.span_id:016x}"
    for _ in range(20):
        result = subprocess.run(
            ["docker", "logs", os.environ["AU_GENAI_COLLECTOR_CONTAINER"]], capture_output=True, text=True, check=True
        )
        logs = result.stdout + result.stderr
        if span_id in logs:
            break
        time.sleep(0.1)
    assert span_id in logs
    # Isolate this span's debug-export record, not an older successful request.
    record = logs.split(span_id, 1)[1].split("\nSpan #", 1)[0]
    assert "gen_ai.provider.name: Str(local-test)" in record
    assert "gen_ai.request.model: Str(collector-model)" in record
    assert "gen_ai.usage.input_tokens: Int(7)" in record
    assert "gen_ai.usage.output_tokens: Int(4)" in record
