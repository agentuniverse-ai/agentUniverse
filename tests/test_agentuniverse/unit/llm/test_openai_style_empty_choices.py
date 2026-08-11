from pathlib import Path


SOURCE = Path(
    "agentuniverse/llm/openai_style_llm.py"
).read_text(encoding="utf-8")


def test_openai_style_non_streaming_calls_handle_empty_choices():
    assert SOURCE.count("if not getattr(chat_completion, 'choices', None):") == 2
    assert 'return LLMOutput(text="", raw=raw_response)' in SOURCE
