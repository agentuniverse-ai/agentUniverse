"""Basic summary fallback must include its marker in its character allowance."""
from types import SimpleNamespace

import pytest

from agentuniverse.agent.context.compressor.summarize_compressor import SummarizeCompressor
from agentuniverse.agent.context.context_model import ContextSegment, ContextType, ContextPriority


def segment(content='x' * 1000):
    return ContextSegment(type=ContextType.BACKGROUND, priority=ContextPriority.MEDIUM,
                          content=content, tokens=len(content) // 4, session_id='test')


def unavailable(*args, **kwargs):
    raise RuntimeError('LLM unavailable')


@pytest.mark.parametrize('target', [11, 20, 64])
@pytest.mark.parametrize('llm', [SimpleNamespace(call=unavailable), SimpleNamespace()])
def test_public_fallback_fits_estimated_budget(target, llm):
    compressor = SummarizeCompressor()
    compressor._llm = llm
    source = segment()
    result, metrics = compressor.compress([source], target)
    assert len(result) == 1
    summary = result[0]
    assert len(summary.content) <= target * 4
    assert summary.tokens == len(summary.content) // 4
    assert metrics.compressed_tokens == summary.tokens
    assert summary.related_ids == [source.id]
    assert source.content == 'x' * 1000


@pytest.mark.parametrize('target', [1, 2, 3])
def test_small_basic_allowance_never_uses_negative_slice(target):
    compressor = SummarizeCompressor()
    text = compressor._basic_summarization([segment()], target)
    assert len(text) <= target * 4


def test_short_basic_summary_is_unchanged():
    compressor = SummarizeCompressor()
    assert compressor._basic_summarization([segment('short text')], 20) == 'short text'


def test_fallback_retains_marker_when_it_fits():
    compressor = SummarizeCompressor()
    text = compressor._basic_summarization([segment()], 20)
    assert text.endswith('... [summarized]')
