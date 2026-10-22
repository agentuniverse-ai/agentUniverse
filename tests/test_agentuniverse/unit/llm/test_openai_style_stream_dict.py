from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


def test_parse_result_accepts_dict_stream_chunks():
    chunk = {
        "choices": [{"delta": {"content": "hello"}, "finish_reason": None}],
        "id": "chunk-1",
    }

    result = OpenAIStyleLLM.parse_result(chunk)

    assert result.text == "hello"
    assert result.raw == chunk
