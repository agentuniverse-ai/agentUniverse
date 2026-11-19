"""Tests for LLM-based context summarization."""

from agentuniverse.agent.context.compressor.summarize_compressor import (
    SummarizeCompressor,
)
from agentuniverse.agent.context.context_model import (
    ContextPriority,
    ContextSegment,
    ContextType,
)


def test_compress_preserves_types_not_configured_for_summarization():
    compressor = SummarizeCompressor()
    compressor._llm = object()
    tool_result = ContextSegment(
        type=ContextType.TOOL_RESULT,
        priority=ContextPriority.MEDIUM,
        content="tool output",
        tokens=10,
    )
    background = ContextSegment(
        type=ContextType.BACKGROUND,
        priority=ContextPriority.MEDIUM,
        content="background " * 100,
        tokens=100,
    )

    compressed, _ = compressor.compress(
        [tool_result, background],
        target_tokens=50,
    )

    assert any(segment.id == tool_result.id for segment in compressed)
