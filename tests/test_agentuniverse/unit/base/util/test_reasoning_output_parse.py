# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Regression coverage for reasoning and ordinary LangChain generations."""

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.outputs import (
    ChatGeneration,
    ChatGenerationChunk,
    Generation,
    GenerationChunk,
)

from agentuniverse.base.util.reasoning_output_parse import ReasoningOutputParser


@pytest.mark.parametrize("generation_type", [Generation, GenerationChunk])
@pytest.mark.parametrize("partial", [False, True])
def test_text_generations(generation_type, partial):
    """Text generations need no chat message to produce the text mapping."""
    generation = generation_type(text="answer")

    assert ReasoningOutputParser().parse_result([generation], partial=partial) == {
        "text": "answer"
    }


@pytest.mark.parametrize(
    "generation_type,message_type",
    [(ChatGeneration, AIMessage), (ChatGenerationChunk, AIMessageChunk)],
)
@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({}, {"text": "answer"}),
        ({"reasoning_content": "thinking"},
         {"text": "answer", "reasoning_content": "thinking"}),
        ({"provider_metadata": "value"},
         {"text": "answer", "reasoning_content": ""}),
        ({"reasoning_content": None},
         {"text": "answer", "reasoning_content": None}),
    ],
)
def test_chat_generations(generation_type, message_type, kwargs, expected):
    """Preserve reasoning and existing additional-kwargs output semantics."""
    generation = generation_type(
        message=message_type(content="answer", additional_kwargs=kwargs)
    )

    assert ReasoningOutputParser().parse_result([generation]) == expected


def test_empty_results():
    """An empty result list keeps the parser's existing empty-string output."""
    assert ReasoningOutputParser().parse_result([]) == ""


def test_first_generation_is_selected():
    """Only the first candidate contributes to the parsed output."""
    generations = [Generation(text="first"), Generation(text="second")]

    assert ReasoningOutputParser().parse_result(generations) == {"text": "first"}


def test_invoke_accepts_text():
    """Runnable invocation also supports a plain text model response."""
    assert ReasoningOutputParser().invoke("answer") == {"text": "answer"}
