# -*- coding: utf-8 -*-
"""Unit tests for agentuniverse.base.util.prompt_util."""

from agentuniverse.base.util.prompt_util import (
    generate_template,
    split_text_on_tokens,
)


class _StubPromptModel:
    """Minimal stub exposing the attributes used by generate_template."""

    system = "sys-content"
    background = None
    user = "user-content"


class TestSplitTextOnTokens:
    """Tests for the deterministic text splitting helper."""

    def test_returns_single_chunk_for_short_text(self):
        assert split_text_on_tokens(text="hello", text_token=5) == ["hello"]

    def test_empty_text_returns_single_empty_chunk(self):
        assert split_text_on_tokens(text="", text_token=1) == [""]

    def test_splits_long_text_into_expected_chunks(self):
        text = "abcdefghij" * 10
        chunks = split_text_on_tokens(
            text=text, text_token=10, chunk_size=3, chunk_overlap=1)
        assert len(chunks) == 5
        assert chunks[0] == text[:30]
        assert chunks[1] == text[20:50]
        assert chunks[-1] == text[80:]

    def test_chunk_lengths_respect_chunk_size(self):
        text = "abcdefghij" * 10
        chunks = split_text_on_tokens(
            text=text, text_token=10, chunk_size=3, chunk_overlap=1)
        assert all(len(chunk) <= 30 for chunk in chunks)

    def test_overlap_makes_chunks_longer_than_source(self):
        text = "abcdefghij" * 10
        chunks = split_text_on_tokens(
            text=text, text_token=10, chunk_size=3, chunk_overlap=1)
        assert sum(len(chunk) for chunk in chunks) > len(text)

    def test_reassembles_text_when_no_overlap(self):
        text = "abcdefghij" * 10
        chunks = split_text_on_tokens(
            text=text, text_token=10, chunk_size=3, chunk_overlap=0)
        assert "".join(chunks) == text

    def test_output_is_deterministic(self):
        text = "abcdefghij" * 10
        first = split_text_on_tokens(
            text=text, text_token=10, chunk_size=3, chunk_overlap=1)
        second = split_text_on_tokens(
            text=text, text_token=10, chunk_size=3, chunk_overlap=1)
        assert first == second


class TestGenerateTemplate:
    """Tests for the generate_template helper."""

    def test_concatenates_only_present_attributes(self):
        model = _StubPromptModel()
        assert generate_template(model, ["system", "user"]) == "sys-content\nuser-content"

    def test_skips_missing_or_none_attributes(self):
        model = _StubPromptModel()
        result = generate_template(model, ["system", "background", "unknown"])
        assert result == "sys-content"

    def test_empty_order_returns_empty_string(self):
        assert generate_template(_StubPromptModel(), []) == ""
