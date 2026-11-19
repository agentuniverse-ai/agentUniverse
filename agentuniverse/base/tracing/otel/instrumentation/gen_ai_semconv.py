"""Opt-in attribute adapter pinned to OpenTelemetry GenAI semconv v1.37.0.

This supplements existing aU spans. It does not create/export spans or replace
their lifecycle, and deliberately does not claim full semconv conformance.
"""

from dataclasses import dataclass

from opentelemetry.trace import Status, StatusCode

from agentuniverse.llm.llm_output import TokenUsage

SEMCONV_VERSION = "1.37.0"
SPEC_URL = "https://github.com/open-telemetry/semantic-conventions/blob/v1.37.0/docs/gen-ai/gen-ai-spans.md"


@dataclass(frozen=True)
class GenAIIdentity:
    """Provider identity known to the application at the actual call boundary."""

    provider: str
    model: str | None = None
    operation: str = "chat"

    def __post_init__(self):
        if not isinstance(self.provider, str) or not self.provider.strip():
            raise ValueError("provider must be known, nonempty text")
        if self.model is not None and (not isinstance(self.model, str) or not self.model.strip()):
            raise ValueError("model must be nonempty text or None")
        if self.operation not in ("chat", "text_completion", "generate_content"):
            raise ValueError("unsupported inference operation")


class GenAIAttributeAdapter:
    """Resolve actual configured identity and annotate existing spans.

    ``identity_resolver(llm, kwargs)`` returns GenAIIdentity or None. Do not infer
    a provider from an OpenAI-compatible class or registration name: proxies,
    channels and endpoint overrides can change it. Resolver failures are marked
    unavailable without affecting business calls. No prompts are read/exported.
    """

    def __init__(self, identity_resolver):
        if not callable(identity_resolver):
            raise TypeError("identity_resolver must be callable")
        self.identity_resolver = identity_resolver

    def begin_llm(self, span, llm, kwargs):
        span.set_attribute("au.gen_ai.semconv.version", SEMCONV_VERSION)
        span.set_attribute("au.gen_ai.usage.status", "unknown")
        try:
            identity = self.identity_resolver(llm, dict(kwargs))
        except Exception:
            identity = None
        if not isinstance(identity, GenAIIdentity):
            span.set_attribute("au.gen_ai.identity.status", "unknown")
            return
        span.set_attribute("au.gen_ai.identity.status", "configured")
        span.set_attribute("gen_ai.operation.name", identity.operation)
        span.set_attribute("gen_ai.provider.name", identity.provider)
        if identity.model is not None:
            span.set_attribute("gen_ai.request.model", identity.model)

    def observe_usage(self, span, usage):
        """Copy explicitly supplied usage before legacy Monitor can estimate it.

        Empty default TokenUsage is unknown, not a reported zero. Values already
        normalized by the provider are retained; no tokenizer is called here.
        Streaming uses the last reported aggregate, never sums cumulative usage.
        """
        if not isinstance(usage, TokenUsage) or not usage.model_fields_set:
            return
        fields = usage.model_fields_set
        if any(type(value) is not int or value < 0 for value in usage.model_dump().values()):
            span.set_attribute("au.gen_ai.usage.status", "invalid")
            return
        provided = 0
        for direction, suffix, value in (
            ("input", "_in", usage.prompt_tokens),
            ("output", "_out", usage.completion_tokens),
        ):
            if not any(name.endswith(suffix) for name in fields):
                continue
            if type(value) is not int or not 0 <= value < 2**63:
                span.set_attribute("au.gen_ai.usage.status", "invalid")
                return
            span.set_attribute(f"gen_ai.usage.{direction}_tokens", value)
            provided += 1
        span.set_attribute("au.gen_ai.usage.status", "provided" if provided == 2 else "partial")

    def observe_result(self, span, result):
        self.observe_usage(span, getattr(result, "usage", None))
        reason = getattr(result, "finish_reason", None)
        if isinstance(reason, str) and reason:
            span.set_attribute("gen_ai.response.finish_reasons", [reason])

    @staticmethod
    def begin_tool(span, name):
        span.set_attribute("au.gen_ai.semconv.version", SEMCONV_VERSION)
        span.set_attribute("gen_ai.operation.name", "execute_tool")
        span.set_attribute("gen_ai.tool.name", name)

    @staticmethod
    def error(span, error):
        if span is not None:
            span.set_attribute("error.type", type(error).__name__)
            span.set_status(Status(StatusCode.ERROR))
