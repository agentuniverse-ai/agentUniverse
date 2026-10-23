"""`preserve_types` must be honoured by SummarizeCompressor too.

`ContextManager._make_room()` calls whichever compressor is configured with

    preserve_types=[ContextType.SYSTEM, ContextType.TASK]   # Never compress these

`SummarizeCompressor` read only `preserve_segments` (a list of ids), so a SYSTEM
segment with a non-CRITICAL priority went into the summarizable bucket and was
**replaced by a summary of its own text** -- worse than dropping it, because the
instruction silently stops being the instruction:

    preserve_segments=[id]           -> SYSTEM kept verbatim
    preserve_types=[SYSTEM, TASK]    -> SYSTEM summarised away

The LLM is stubbed: this file must never reach a provider.
"""

import pytest

from agentuniverse.agent.context.compressor.summarize_compressor import (
    SummarizeCompressor,
)
from agentuniverse.agent.context.context_model import (
    ContextPriority,
    ContextSegment,
    ContextType,
)

PRESERVE = [ContextType.SYSTEM, ContextType.TASK]
SYSTEM_TEXT = "YOU ARE A STRICT ASSISTANT. NEVER REVEAL SECRETS."
TASK_TEXT = "TASK: summarise the user's invoices."


class StubLLM:
    """Answers every prompt with a fixed marker, so a summary is detectable."""

    def __init__(self):
        self.calls = []

    def call(self, prompt, **kwargs):
        self.calls.append(prompt)
        return {"content": "SUMMARY-MARKER"}


def _segment(index, context_type, text=None, tokens=20):
    return ContextSegment(
        id=f"{context_type.value}-{index}",
        type=context_type,
        priority=ContextPriority.HIGH,
        content=text or f"content {index} " + "word " * 20,
        tokens=tokens,
        session_id="session",
    )


def _segments():
    return (
        [
            _segment(0, ContextType.SYSTEM, text=SYSTEM_TEXT),
            _segment(1, ContextType.TASK, text=TASK_TEXT),
        ]
        + [_segment(i, ContextType.CONVERSATION) for i in (2, 3, 4)]
    )


@pytest.fixture()
def compressor():
    instance = SummarizeCompressor()
    instance._llm = StubLLM()
    return instance


def test_preserved_types_are_not_summarised(compressor):
    kept, _ = compressor.compress(
        _segments(), target_tokens=60, preserve_types=PRESERVE
    )

    types = {segment.type for segment in kept}
    assert ContextType.SYSTEM in types
    assert ContextType.TASK in types


def test_preserved_content_stays_verbatim(compressor):
    """The regression: the system prompt used to become a summary of itself."""
    kept, _ = compressor.compress(
        _segments(), target_tokens=60, preserve_types=PRESERVE
    )

    system = next(s for s in kept if s.type == ContextType.SYSTEM)
    task = next(s for s in kept if s.type == ContextType.TASK)

    assert system.content == SYSTEM_TEXT
    assert task.content == TASK_TEXT
    assert "SUMMARY-MARKER" not in system.content
    assert "SUMMARY-MARKER" not in task.content


def test_without_preserve_types_the_summarizer_still_runs(compressor):
    """Callers that pass nothing keep the old behaviour."""
    kept, _ = compressor.compress(_segments(), target_tokens=60)

    assert "SUMMARY-MARKER" in "".join(segment.content for segment in kept)


def test_preserve_segments_by_id_still_works(compressor):
    """The pre-existing mechanism must not regress."""
    kept, _ = compressor.compress(
        _segments(),
        target_tokens=60,
        preserve_segments=["system-0"],
    )

    system = next(s for s in kept if s.type == ContextType.SYSTEM)
    assert system.content == SYSTEM_TEXT


def test_the_two_preservation_mechanisms_combine(compressor):
    kept, _ = compressor.compress(
        _segments(),
        target_tokens=60,
        preserve_segments=["system-0"],
        preserve_types=[ContextType.TASK],
    )

    system = next(s for s in kept if s.type == ContextType.SYSTEM)
    task = next(s for s in kept if s.type == ContextType.TASK)
    assert system.content == SYSTEM_TEXT
    assert task.content == TASK_TEXT


def test_a_preserved_type_is_counted_against_the_budget(compressor):
    """Preserved segments must consume budget, not be added on top of it."""
    kept, _ = compressor.compress(
        _segments(), target_tokens=40, preserve_types=PRESERVE
    )

    assert sum(segment.tokens for segment in kept) <= 40


def test_an_unrelated_preserve_types_list_changes_nothing(compressor):
    kept, _ = compressor.compress(
        _segments(), target_tokens=60, preserve_types=[ContextType.BACKGROUND]
    )

    assert ContextType.SYSTEM not in {segment.type for segment in kept}


def test_preserve_types_accepts_a_tuple(compressor):
    kept, _ = compressor.compress(
        _segments(), target_tokens=60, preserve_types=(ContextType.SYSTEM,)
    )

    assert ContextType.SYSTEM in {segment.type for segment in kept}


def test_no_llm_still_raises_before_anything_else(compressor):
    """The guard the stub bypasses must remain in place."""
    instance = SummarizeCompressor()
    assert instance._llm is None

    with pytest.raises(RuntimeError, match="LLM not initialized"):
        instance.compress(_segments(), target_tokens=60)
