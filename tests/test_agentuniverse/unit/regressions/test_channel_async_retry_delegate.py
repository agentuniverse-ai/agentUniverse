import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from agentuniverse.llm.llm_channel.langchain_instance import default_channel_langchain_instance as module


def test_non_v1_async_retry_uses_channel_delegate(monkeypatch):
    acall = AsyncMock(return_value="ok")
    adapter = SimpleNamespace(llm_channel=SimpleNamespace(acall=acall))
    monkeypatch.setattr(module, "is_openai_v1", lambda: False)
    monkeypatch.setattr(module, "_create_retry_decorator", lambda *args, **kwargs: (lambda fn: fn))

    result = asyncio.run(
        module.DefaultChannelLangchainInstance.acompletion_with_retry(
            None, adapter, messages=[{"role": "user", "content": "hi"}]
        )
    )

    assert result == "ok"
    acall.assert_awaited_once()
