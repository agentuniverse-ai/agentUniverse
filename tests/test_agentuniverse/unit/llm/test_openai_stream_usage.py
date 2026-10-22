from agentuniverse.llm.openai_llm import OpenAILLM
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class StreamChunk:
    def __init__(self, payload):
        self.payload = payload

    def dict(self):
        return self.payload

    def model_dump(self):
        return self.payload


def test_openai_parser_preserves_usage_only_stream_chunk():
    chunk = StreamChunk({
        "choices": [],
        "usage": {"prompt_tokens": 3, "completion_tokens": 2},
    })

    output = OpenAILLM.parse_result(chunk)

    assert output is not None
    assert output.text == ""
    assert output.usage.prompt_tokens == 3
    assert output.usage.completion_tokens == 2


def test_openai_style_parser_preserves_stream_usage():
    chunk = StreamChunk({
        "choices": [{"delta": {"content": "hello"}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 1},
    })

    output = OpenAIStyleLLM.parse_result(chunk)

    assert output.text == "hello"
    assert output.usage.prompt_tokens == 5
    assert output.usage.completion_tokens == 1
