# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/05 09:30
# @Author  : Yue Wang
# @FileName: test_summarize_compressor.py
"""Unit tests for SummarizeCompressor without real LLM dependencies."""

import pytest
from agentuniverse.agent.context.compressor.summarize_compressor import SummarizeCompressor
from agentuniverse.agent.context.context_model import ContextSegment, ContextType, ContextPriority


class _FakeLLM:
    """Deterministic stand-in LLM returning a fixed summary."""

    def call(self, prompt):
        return {"content": "summary text here ok"}


def _seg(content, tokens, type_=ContextType.BACKGROUND, priority=ContextPriority.MEDIUM):
    return ContextSegment(type=type_, priority=priority, content=content, tokens=tokens)


CRITICAL = _seg("system prompt keep", 30, ContextType.SYSTEM, ContextPriority.CRITICAL)
BG_MEDIUM = _seg("A" * 400, 100)
BG_LOW = _seg("B" * 200, 80, priority=ContextPriority.LOW)


class TestSummarizeCompressor:
    """Test the summarization strategy with pure behavior only."""

    @pytest.fixture
    def compressor(self):
        """SummarizeCompressor with no LLM attached."""
        return SummarizeCompressor()

    def test_default_configuration(self, compressor):
        assert compressor.llm_name == "default_llm"
        assert compressor.summary_ratio == 0.3
        assert compressor.batch_size == 5
        assert compressor.preserve_structure is True
        assert compressor._llm is None
        assert [t.value for t in compressor.summarize_types] == ["background", "reference", "conversation"]

    def test_compress_validation(self, compressor):
        tiny = _seg("x", 5, ContextType.CONVERSATION)
        with pytest.raises(ValueError, match="empty"):
            compressor.compress([], 100)
        with pytest.raises(ValueError, match="target_tokens"):
            compressor.compress([tiny], 0)
        with pytest.raises(RuntimeError, match="LLM"):
            compressor.compress([tiny], 100)

    def test_compress_with_fake_llm(self, compressor):
        compressor._llm = _FakeLLM()
        result, metrics = compressor.compress([CRITICAL, BG_MEDIUM, BG_LOW], 150)
        assert len(result) == 3
        assert result[0].id == CRITICAL.id
        assert result[0].content == "system prompt keep"
        assert all(seg.metadata.compressed and seg.metadata.source_type == "llm_summary"
                   for seg in result[1:])
        assert metrics.original_tokens == 210
        assert metrics.segments_compressed == 2
        assert metrics.strategy_used == "summarize"

    def test_group_for_summarization(self, compressor):
        segments = [_seg("a", 5), _seg("c", 5, ContextType.SYSTEM, ContextPriority.CRITICAL)]
        groups = compressor._group_for_summarization(segments)
        assert list(groups.keys()) == ["background_medium"]
        assert groups["background_medium"] == [segments[0]]

    def test_prompt_and_basic_summarization(self, compressor):
        prompt = compressor._build_summary_prompt([_seg("facts", 10)], 25)
        assert "TARGET TOKEN COUNT: Approximately 25 tokens" in prompt
        assert "[BACKGROUND] facts" in prompt
        assert compressor._basic_summarization([_seg("abc def", 5)], 100) == "abc def"
        summary = compressor._basic_summarization([BG_MEDIUM], 20)
        assert summary.endswith("... [summarized]") and len(summary) < len(BG_MEDIUM.content)

    def test_estimate_information_loss(self, compressor):
        originals = [_seg("a", 100), _seg("b", 100)]
        summary = [ContextSegment(type=ContextType.SUMMARY, priority=ContextPriority.MEDIUM, content="s", tokens=60)]
        assert compressor.estimate_information_loss(originals, summary) == pytest.approx(0.12)
        assert compressor.estimate_information_loss([_seg("", 0)], summary) == 0.0

    def test_basic_summary_segment_fallback(self, compressor):
        fallback = compressor._basic_summarization_segment([BG_MEDIUM], 50)
        assert fallback.metadata.compressed and fallback.metadata.source_type == "basic_summary"
        assert fallback.related_ids == [BG_MEDIUM.id] and fallback.tokens == 50
