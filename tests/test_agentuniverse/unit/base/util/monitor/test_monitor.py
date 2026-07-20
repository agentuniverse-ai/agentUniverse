from copy import deepcopy

from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.llm_output import LLMOutput


class _StubLLM:
    @staticmethod
    def get_num_tokens(text: str) -> int:
        return len(text)


def test_get_llm_token_usage_preserves_llm_input():
    llm_input = {
        "kwargs": {
            "messages": [
                {"role": "user", "content": "hello"},
            ]
        }
    }
    original_input = deepcopy(llm_input)

    usage = Monitor.get_llm_token_usage(
        _StubLLM(),
        llm_input,
        LLMOutput(text="response"),
    )

    assert usage["total_tokens"] > 0
    assert llm_input == original_input
