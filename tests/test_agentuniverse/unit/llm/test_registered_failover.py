"""Registered controlled providers exercised through actual LLM.call/acall."""

import asyncio
from typing import Any

import pytest
from pydantic import Field

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.registered_failover import LLMFailoverExhausted, RegisteredLLMFailover


class ControlledLLM(LLM):
    failure: Any = None
    after_chunk: bool = False
    empty: bool = False
    calls: list = Field(default_factory=list)

    def get_num_tokens(self, text):
        raise NotImplementedError("test provider does not estimate tokens")

    def _call(self, *, messages, streaming=False, **kwargs):
        self.calls.append((messages[0]["content"], streaming))
        messages[0]["content"] = "mutated by provider"
        if not streaming:
            if self.failure:
                raise self.failure
            return LLMOutput(text=self.name)

        def generate():
            if self.after_chunk:
                yield LLMOutput(text="")
            if self.failure:
                raise self.failure
            if not self.empty:
                yield LLMOutput(text=self.name)

        return generate()

    async def _acall(self, *, messages, streaming=False, **kwargs):
        if not streaming:
            return self._call(messages=messages, streaming=False, **kwargs)

        async def generate():
            for chunk in self._call(messages=messages, streaming=True, **kwargs):
                await asyncio.sleep(0)
                yield chunk

        return generate()


@pytest.fixture
def registered(monkeypatch):
    monkeypatch.setattr(ApplicationConfigManager(), "_ApplicationConfigManager__app_configer", AppConfiger())
    monkeypatch.setattr(LLMManager(), "_instance_obj_map", {})
    first = ControlledLLM(name="first")
    second = ControlledLLM(name="second")
    for instance in [first, second]:
        LLMManager().register(f"failover.llm.{instance.name}", instance)
    return first, second, RegisteredLLMFailover(["first", "second"], appname="failover")


def invoke(chain, mode):
    kwargs = {"messages": [{"role": "user", "content": "original"}]}
    if mode == "call":
        return [chain.call(**kwargs)]
    if mode == "stream":
        return list(chain.stream(**kwargs))

    async def run():
        if mode == "acall":
            return [await chain.acall(**kwargs)]
        return [chunk async for chunk in chain.astream(**kwargs)]

    return asyncio.run(run())


@pytest.mark.parametrize("mode", ["call", "acall", "stream", "astream"])
@pytest.mark.parametrize(
    "error", [ConnectionError("synthetic"), TimeoutError("synthetic"), asyncio.TimeoutError("async timeout")]
)
def test_approved_failure_switches_once_and_preserves_input(registered, mode, error):
    first, second, chain = registered
    first.failure = error
    result = invoke(chain, mode)[0]
    assert result.output.text == "second" and result.provider == "second"
    assert [(a.provider, a.error_type) for a in result.attempts] == [("first", type(error).__name__), ("second", None)]
    assert len(first.calls) == len(second.calls) == 1
    assert second.calls[0][0] == "original"


@pytest.mark.parametrize("mode", ["call", "acall", "stream", "astream"])
@pytest.mark.parametrize("error", [ValueError("business"), TypeError("unsupported parameter")])
def test_business_errors_never_switch(registered, mode, error):
    first, second, chain = registered
    first.failure = error
    with pytest.raises(type(error)):
        invoke(chain, mode)
    assert not second.calls


@pytest.mark.parametrize("mode", ["stream", "astream"])
def test_even_empty_first_chunk_prevents_switch(registered, mode):
    first, second, chain = registered
    first.after_chunk = True
    first.failure = ConnectionError("partial")
    with pytest.raises(ConnectionError):
        invoke(chain, mode)
    assert not second.calls


@pytest.mark.parametrize("mode", ["acall", "astream"])
def test_cancellation_never_switches(registered, mode):
    first, second, chain = registered
    first.failure = asyncio.CancelledError()
    with pytest.raises(asyncio.CancelledError):
        invoke(chain, mode)
    assert not second.calls


@pytest.mark.parametrize("mode", ["call", "acall", "stream", "astream"])
def test_exhausted_attempts_and_cause(registered, mode):
    first, second, chain = registered
    first.failure = ConnectionError("one")
    second.failure = TimeoutError("two")
    with pytest.raises(LLMFailoverExhausted) as caught:
        invoke(chain, mode)
    assert [a.provider for a in caught.value.attempts] == ["first", "second"]
    assert isinstance(caught.value.__cause__, TimeoutError)


@pytest.mark.parametrize("mode", ["stream", "astream"])
def test_empty_successful_stream_does_not_switch(registered, mode):
    first, second, chain = registered
    first.empty = True
    assert invoke(chain, mode) == []
    assert not second.calls


@pytest.mark.parametrize("names", [[], ["first", "first"], [""], "first", list(map(str, range(9)))])
def test_invalid_chains(names):
    with pytest.raises(ValueError):
        RegisteredLLMFailover(names)


def test_missing_provider_preflight_and_stream_flag(registered):
    first, _, chain = registered
    with pytest.raises(ValueError, match="not found"):
        RegisteredLLMFailover(["first", "missing"], appname="failover").call(messages=[])
    assert not first.calls
    for key in ["stream", "streaming"]:
        with pytest.raises(ValueError):
            chain.call(**{key: True})


@pytest.mark.parametrize("errors", [(Exception,), (BaseException,), (asyncio.CancelledError,), ("TimeoutError",)])
def test_reject_broad_or_nonexception_policies(errors):
    with pytest.raises(ValueError):
        RegisteredLLMFailover(["first"], retry_errors=errors)


def test_caller_messages_unchanged_and_new_invocation_attempts(registered):
    first, _, chain = registered
    first.failure = ConnectionError()
    messages = [{"role": "user", "content": "original"}]
    chain.call(messages=messages)
    assert messages[0]["content"] == "original"
    first.failure = None
    result = chain.call(messages=messages)
    assert len(result.attempts) == 1 and result.provider == "first"


def test_real_task_cancel_during_provider_wait(registered):
    first, second, chain = registered

    class WaitingLLM(ControlledLLM):
        async def _acall(self, **kwargs):
            await asyncio.sleep(3600)

    LLMManager().unregister("failover.llm.first")
    LLMManager().register("failover.llm.first", WaitingLLM(name="first"))

    async def run():
        task = asyncio.create_task(chain.acall(messages=[]))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert not second.calls


def test_consumer_close_does_not_start_another_provider(registered):
    first, second, chain = registered
    first.after_chunk = True
    first.failure = ConnectionError("after close")
    stream = chain.stream(messages=[{"content": "original"}])
    next(stream)
    stream.close()
    assert not second.calls


def test_async_consumer_close_does_not_start_another_provider(registered):
    first, second, chain = registered
    first.after_chunk = True
    first.failure = ConnectionError("after close")

    async def run():
        stream = chain.astream(messages=[{"content": "original"}])
        await stream.__anext__()
        await stream.aclose()

    asyncio.run(run())
    assert not second.calls
