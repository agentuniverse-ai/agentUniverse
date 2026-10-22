from types import SimpleNamespace

from agentuniverse.llm.openai_style_langchain_instance import (
    LangchainOpenAIStyleInstance,
)


def test_openai_style_adapter_preserves_zero_temperature():
    llm = SimpleNamespace(
        model_name="demo",
        temperature=0.0,
        request_timeout=30,
        max_tokens=10,
        max_retries=2,
        streaming=False,
        api_key="test-key",
        organization=None,
        api_base=None,
        proxy=None,
    )

    adapter = LangchainOpenAIStyleInstance(llm)

    assert adapter.temperature == 0.0
