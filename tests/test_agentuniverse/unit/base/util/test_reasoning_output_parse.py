# -*- coding: utf-8 -*-
"""Unit tests for agentuniverse.base.util.reasoning_output_parse."""

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration

from agentuniverse.base.util.reasoning_output_parse import ReasoningOutputParser


class TestReasoningOutputParser:
    """Tests for the ReasoningOutputParser.parse_result method."""

    def _parse(self, *generations, partial=False):
        parser = ReasoningOutputParser()
        return parser.parse_result(list(generations), partial=partial)

    def test_empty_result_returns_empty_string(self):
        assert self._parse() == ""

    def test_with_reasoning_content(self):
        generation = ChatGeneration(message=AIMessage(
            content="final answer",
            additional_kwargs={"reasoning_content": "chain of thought"}))
        assert self._parse(generation) == {
            "text": "final answer",
            "reasoning_content": "chain of thought",
        }

    def test_without_additional_kwargs(self):
        generation = ChatGeneration(message=AIMessage(content="plain answer"))
        assert self._parse(generation) == {"text": "plain answer"}

    def test_with_empty_additional_kwargs(self):
        generation = ChatGeneration(message=AIMessage(
            content="plain answer", additional_kwargs={}))
        assert self._parse(generation) == {"text": "plain answer"}

    def test_additional_kwargs_without_reasoning_content(self):
        generation = ChatGeneration(message=AIMessage(
            content="answer", additional_kwargs={"finish_reason": "stop"}))
        assert self._parse(generation) == {"text": "answer", "reasoning_content": ""}

    def test_partial_flag_is_supported(self):
        generation = ChatGeneration(message=AIMessage(content="answer"))
        assert self._parse(generation, partial=True) == {"text": "answer"}
