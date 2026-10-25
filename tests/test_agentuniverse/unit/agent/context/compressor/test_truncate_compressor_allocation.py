"""An even split of an exact multiple of min_segment_tokens must survive.

`_truncate_segments()` allocated each segment

    int((importance / total_importance) * target_tokens)

and then dropped the segment if that was below `min_segment_tokens` (10 by
default). Six segments with equal importance and `target_tokens=60` are each
entitled to exactly 10 tokens, but `total_importance` is a sum of floats:

    sum of six equal importances == 29.9999999989294
    (5.0 / 29.9999999989294) * 60 == 9.999999...
    int(...)                       == 9      -> below the minimum -> dropped

so a budget that fits the input exactly produced a single segment instead of
six:

    target=  59 -> 0 segment(s)     (below the minimum for every slot)
    target=  60 -> 1 segment(s)     <- should be 6
    target=  61 -> 6 segment(s)

The allocation is now rounded up, so a slot that is entitled to the minimum
keeps it.
"""

import pytest

from agentuniverse.agent.context.compressor.truncate_compressor import (
    TruncateCompressor,
)
from agentuniverse.agent.context.context_model import (
    ContextPriority,
    ContextSegment,
    ContextType,
)


def _segment(index, tokens=20, priority=ContextPriority.HIGH):
    return ContextSegment(
        id=f"s{index}",
        type=ContextType.CONVERSATION,
        priority=priority,
        content=f"message {index} " + "word " * 20,
        tokens=tokens,
    )


def _segments(count=6):
    return [_segment(i) for i in range(count)]


@pytest.fixture()
def compressor():
    return TruncateCompressor()


def test_the_premise_importances_are_nearly_but_not_exactly_equal(compressor):
    """The cause: decay makes nominally equal segments differ in the 10th decimal.

    If this ever holds exactly, the ceiling would no longer be load-bearing.
    """
    segments = _segments()
    importances = [compressor._calculate_importance(s) for s in segments]

    assert len(set(importances)) > 1, "importances became exactly equal"
    assert max(importances) - min(importances) < 1e-6, importances

    # The sum lands just below (or above) the nominal total, which is what
    # pushes an exact share off the integer boundary.
    nominal = sum(importances) / len(importances) * len(importances)
    assert abs(sum(importances) - nominal) < 1e-6


def test_an_exact_multiple_of_the_minimum_keeps_every_segment(compressor):
    """6 segments x 20 tokens, budget 60 -> each slot is entitled to 10."""
    segments = _segments()
    total_minimum = compressor.min_segment_tokens * len(segments)

    kept, _ = compressor.compress(segments, target_tokens=total_minimum)

    assert len(kept) == len(segments)


def test_a_budget_below_the_minimum_per_slot_drops_nothing_it_cannot_fill(
    compressor,
):
    """With 59 tokens, one slot cannot reach the minimum and is dropped.

    The point is that the outcome is monotone: a larger budget never keeps
    fewer segments.
    """
    segments = _segments()
    counts = []
    for target in (59, 60, 61, 100, 120):
        kept, _ = compressor.compress(segments, target_tokens=target)
        counts.append((target, len(kept)))

    kept_counts = [count for _, count in counts]
    assert kept_counts == sorted(kept_counts), counts


def test_the_result_never_exceeds_the_budget(compressor):
    segments = _segments()
    for target in (30, 60, 90, 120):
        kept, _ = compressor.compress(segments, target_tokens=target)
        assert sum(segment.tokens for segment in kept) <= target, target


def test_a_budget_that_fits_the_input_returns_it_untouched(compressor):
    segments = _segments()
    original_tokens = sum(segment.tokens for segment in segments)

    kept, _ = compressor.compress(segments, target_tokens=original_tokens)

    assert len(kept) == len(segments)
    assert sum(segment.tokens for segment in kept) == original_tokens


def test_a_single_segment_list_still_works(compressor):
    kept, _ = compressor.compress([_segment(0)], target_tokens=10)

    assert len(kept) == 1


def test_critical_segments_are_kept_ahead_of_others(compressor):
    segments = [
        _segment(0, priority=ContextPriority.CRITICAL),
        _segment(1),
        _segment(2),
    ]

    kept, _ = compressor.compress(segments, target_tokens=25)

    assert any(segment.priority == ContextPriority.CRITICAL for segment in kept)
