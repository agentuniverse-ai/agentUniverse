from types import SimpleNamespace

from agentuniverse.base.util.reasoning_output_parse import ReasoningOutputParser


def test_parser_accepts_plain_generation_without_message():
    result = ReasoningOutputParser().parse_result([SimpleNamespace(text="answer")])

    assert result == {"text": "answer"}


def test_parser_keeps_reasoning_content_from_message_metadata():
    generation = SimpleNamespace(
        text="answer",
        message=SimpleNamespace(additional_kwargs={"reasoning_content": "thoughts"}),
    )

    assert ReasoningOutputParser().parse_result([generation]) == {
        "text": "answer",
        "reasoning_content": "thoughts",
    }
