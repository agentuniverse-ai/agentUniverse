"""Caller-approved, sequential failover across registered LLM instances."""

import asyncio
from copy import deepcopy
from dataclasses import dataclass

from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.llm.llm_output import LLMOutput


@dataclass(frozen=True)
class LLMAttempt:
    """A provider attempt without prompts, credentials or error messages."""

    provider: str
    error_type: str | None = None


@dataclass(frozen=True)
class FailoverOutput:
    """Original provider output plus registered provider and attempt provenance."""

    output: LLMOutput
    provider: str
    attempts: tuple[LLMAttempt, ...]


class LLMFailoverExhausted(RuntimeError):
    """Every approved provider failed with an explicitly retryable error."""

    def __init__(self, attempts):
        super().__init__("all approved LLM providers failed")
        self.attempts = tuple(attempts)


class RegisteredLLMFailover:
    """Invoke each approved registered LLM at most once, in declared order.

    This is a caller-side API, not a new provider or implicit routing rule.
    Provider-internal retries/timeouts remain provider configuration. Only
    observed exceptions trigger failover; there is no thread deadline that
    could leave an attempt running. Cancellation is always propagated.
    """

    def __init__(self, providers, *, retry_errors=(ConnectionError, TimeoutError, asyncio.TimeoutError), appname=None):
        if isinstance(providers, str):
            raise ValueError("providers must be an ordered collection of names")
        self.providers = tuple(providers)
        if (
            not 1 <= len(self.providers) <= 8
            or any(type(p) is not str or not p.strip() for p in self.providers)
            or len(set(self.providers)) != len(self.providers)
        ):
            raise ValueError("provide 1 to 8 unique registered LLM names")
        self.retry_errors = tuple(retry_errors)
        for error in self.retry_errors:
            if not isinstance(error, type) or not issubclass(error, Exception) or error in (Exception, BaseException):
                raise ValueError("retry_errors must contain specific Exception types")
        self.appname = appname

    def _targets(self):
        targets = []
        for name in self.providers:
            target = LLMManager().get_instance_obj(name, appname=self.appname)
            if not isinstance(target, LLM):
                raise ValueError(f"registered LLM not found: {name}")
            targets.append((name, target))
        return targets

    @staticmethod
    def _kwargs(kwargs, streaming):
        if "stream" in kwargs or "streaming" in kwargs:
            raise ValueError("use call/acall for outputs and stream/astream for chunks")
        return {**deepcopy(kwargs), "streaming": streaming}

    @staticmethod
    def _output(value, name, attempts):
        if not isinstance(value, LLMOutput):
            raise TypeError("provider must return LLMOutput")
        return FailoverOutput(value, name, tuple(attempts) + (LLMAttempt(name),))

    def call(self, **kwargs) -> FailoverOutput:
        """Call registered LLM.call; business/unsupported-parameter errors propagate."""
        params = self._kwargs(kwargs, False)
        attempts = []
        for name, target in self._targets():
            try:
                value = target.call(**deepcopy(params))
            except self.retry_errors as error:
                attempts.append(LLMAttempt(name, type(error).__name__))
                last_error = error
                continue
            return self._output(value, name, attempts)
        raise LLMFailoverExhausted(attempts) from last_error

    async def acall(self, **kwargs) -> FailoverOutput:
        """Call registered LLM.acall; cancellation never starts another provider."""
        params = self._kwargs(kwargs, False)
        attempts = []
        for name, target in self._targets():
            try:
                value = await target.acall(**deepcopy(params))
            except asyncio.CancelledError:
                raise
            except self.retry_errors as error:
                attempts.append(LLMAttempt(name, type(error).__name__))
                last_error = error
                continue
            return self._output(value, name, attempts)
        raise LLMFailoverExhausted(attempts) from last_error

    def stream(self, **kwargs):
        """Yield provenance-bearing chunks; never switch after any emitted chunk.

        Even empty/role-only chunks commit to a provider. Empty successful
        streams are accepted. Close the returned generator when abandoning it.
        """
        params = self._kwargs(kwargs, True)
        attempts = []
        for name, target in self._targets():
            stream = None
            emitted = False
            try:
                try:
                    stream = target.call(**deepcopy(params))
                    for chunk in stream:
                        result = self._output(chunk, name, attempts)
                        emitted = True
                        yield result
                    return
                except self.retry_errors as error:
                    if emitted:
                        raise
                    attempts.append(LLMAttempt(name, type(error).__name__))
                    last_error = error
            finally:
                close = getattr(stream, "close", None)
                if close is not None:
                    close()
        raise LLMFailoverExhausted(attempts) from last_error

    async def astream(self, **kwargs):
        """Async streaming counterpart; close returned generators on early exit."""
        params = self._kwargs(kwargs, True)
        attempts = []
        for name, target in self._targets():
            stream = None
            emitted = False
            try:
                try:
                    stream = await target.acall(**deepcopy(params))
                    async for chunk in stream:
                        result = self._output(chunk, name, attempts)
                        emitted = True
                        yield result
                    return
                except asyncio.CancelledError:
                    raise
                except self.retry_errors as error:
                    if emitted:
                        raise
                    attempts.append(LLMAttempt(name, type(error).__name__))
                    last_error = error
            finally:
                close = getattr(stream, "aclose", None)
                if close is not None:
                    await close()
        raise LLMFailoverExhausted(attempts) from last_error
