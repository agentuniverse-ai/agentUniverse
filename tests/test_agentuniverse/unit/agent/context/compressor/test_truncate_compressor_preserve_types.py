"""`preserve_types` must be honoured by every compressor, not just one.

`ContextManager._make_room()` calls whichever compressor is configured with

    self._compressor.compress(
        segments, target_tokens,
        time_limit_ms=500, min_quality=0.9,
        preserve_types=[ContextType.SYSTEM, ContextType.TASK]   # Never compress these
    )

and `AdaptiveCompressor._execute_strategy()` forwards those kwargs to the chosen
sub-strategy. `SelectiveCompressor` reads `preserve_types`; `TruncateCompressor`
did not read it at all, so under the truncate strategy the system prompt and the
task instruction were dropped exactly when the budget got tight -- the case the
guarantee exists for.

Measured on six 20-token segments, two of them SYSTEM and TASK:

    target  TruncateCompressor (before)   SelectiveCompressor
     120    kept both                   kept both
      60    kept both                   kept both
      40    0 segments, both DROPPED     kept both
      30    0 segments, both DROPPED     kept both
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

PRESERVE = [ContextType.SYSTEM, ContextType.TASK]


def _segment(index, context_type, tokens=20):
    return ContextSegment(
        id=f"{context_type.value}-{index}",
        type=context_type,
        priority=ContextPriority.HIGH,
        content=f"content {index} " + "word " * 20,
        tokens=tokens,
    )


def _segments():
    return (
        [_segment(0, ContextType.SYSTEM), _segment(1, ContextType.TASK)]
        + [_segment(i, ContextType.CONVERSATION) for i in range(2, 6)]
    )


@pytest.fixture()
def compressor():
    return TruncateCompressor()


@pytest.mark.parametrize("target", [120, 80, 60, 40, 30])
def test_preserved_types_survive_every_budget(compressor, target):
    kept, _ = compressor.compress(
        _segments(), target_tokens=target, preserve_types=PRESERVE
    )

    types = {segment.type for segment in kept}
    assert ContextType.SYSTEM in types, (target, [s.type for s in kept])
    assert ContextType.TASK in types, (target, [s.type for s in kept])


def test_a_tight_budget_used_to_drop_everything(compressor):
    """The regression, stated as a count rather than a type check."""
    kept, _ = compressor.compress(
        _segments(), target_tokens=40, preserve_types=PRESERVE
    )

    assert len(kept) >= 2


def test_without_preserve_types_the_old_behaviour_is_kept(compressor):
    """Callers that pass nothing must still get plain truncation."""
    kept, _ = compressor.compress(_segments(), target_tokens=40)

    assert len(kept) == 0


def test_a_preserved_type_is_not_dropped_but_may_be_shortened(compressor):
    """`preserve` means "not dropped", the same as for CRITICAL segments."""
    kept, _ = compressor.compress(
        _segments(), target_tokens=40, preserve_types=PRESERVE
    )

    system = next(s for s in kept if s.type == ContextType.SYSTEM)
    assert system.tokens <= 20


def test_critical_segments_keep_working_alongside_preserve_types(compressor):
    segments = _segments()
    segments.append(_segment(9, ContextType.CONVERSATION))
    segments[-1].priority = ContextPriority.CRITICAL

    kept, _ = compressor.compress(
        segments, target_tokens=40, preserve_types=PRESERVE
    )

    types = {segment.type for segment in kept}
    assert ContextType.SYSTEM in types
    assert ContextType.TASK in types


def test_an_unrelated_preserve_types_list_changes_nothing(compressor):
    kept, _ = compressor.compress(
        _segments(), target_tokens=40, preserve_types=[ContextType.BACKGROUND]
    )

    assert len(kept) == 0


def test_preserve_types_is_accepted_as_a_tuple(compressor):
    """Callers may pass any iterable; membership must still work."""
    kept, _ = compressor.compress(
        _segments(), target_tokens=40, preserve_types=(ContextType.SYSTEM,)
    )

    assert [segment.type for segment in kept] == [ContextType.SYSTEM]
