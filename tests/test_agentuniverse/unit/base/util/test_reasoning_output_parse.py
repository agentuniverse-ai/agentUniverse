# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/15 12:30
# @Author  : Yue Wang
# @FileName: test_reasoning_output_parse.py
"""Unit tests for ReasoningOutputParser."""

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration
from pytest import fixture

from agentuniverse.base.util.reasoning_output_parse import ReasoningOutputParser


@fixture
def parser():
    """Create a ReasoningOutputParser instance."""
    return ReasoningOutputParser()


def _generation(content="answer", additional_kwargs=None):
    """Build a ChatGeneration wrapping an AIMessage."""
    message = AIMessage(content=content, additional_kwargs=additional_kwargs or {})
    return ChatGeneration(text=content, message=message)


class TestReasoningOutputParser:
    """Test ReasoningOutputParser.parse_result behavior."""

    def test_empty_result_returns_empty_string(self, parser):
        """An empty result list yields an empty string."""
        assert parser.parse_result([]) == ""

    def test_returns_text_without_additional_kwargs(self, parser):
        """Without additional kwargs only the text is returned."""
        result = parser.parse_result([_generation("hello")])
        assert result == {"text": "hello"}
        assert "reasoning_content" not in result

    def test_returns_reasoning_content_when_present(self, parser):
        """reasoning_content from additional kwargs is exposed in the result."""
        generation = _generation("answer", {"reasoning_content": "thinking"})
        result = parser.parse_result([generation])
        assert result == {"text": "answer", "reasoning_content": "thinking"}

    def test_returns_empty_reasoning_for_other_kwargs(self, parser):
        """Other additional kwargs still yield an empty reasoning_content key."""
        generation = _generation("answer", {"other": 1})
        result = parser.parse_result([generation])
        assert result == {"text": "answer", "reasoning_content": ""}

    def test_uses_first_generation_text(self, parser):
        """The text of the first generation is used for the result."""
        generations = [_generation("first"), _generation("second")]
        result = parser.parse_result(generations)
        assert result["text"] == "first"
