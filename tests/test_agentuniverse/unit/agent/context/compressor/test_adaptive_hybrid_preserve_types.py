"""What the Hybrid strategy actually does with `preserve_types`.

`AdaptiveCompressor` is what `ContextManager._make_room()` drives, and it picks
one of four strategies. The other three are covered by
`test_truncate_compressor_preserve_types.py` and
`test_summarize_compressor_preserve_types.py`; this pins the composite one so
the claim "hybrid inherits both" is backed by a test rather than by prose.

`_hybrid_compress()` splits by **priority first**, then hands each bucket to a
different sub-strategy:

    high_priority  (CRITICAL / HIGH)          -> SelectiveCompressor
    summarizable   (BACKGROUND / REFERENCE)   -> SummarizeCompressor
    remaining      (everything else)          -> TruncateCompressor

so a preserved type reaches a different sub-strategy depending on its priority,
and the guarantee is "not dropped", not "byte-identical":

    SYSTEM @ HIGH    -> Selective -> kept verbatim
    SYSTEM @ MEDIUM  -> Truncate  -> kept, but the content may be shortened
"""

import pytest

from agentuniverse.agent.context.compressor.adaptive_compressor import (
    AdaptiveCompressor,
)
from agentuniverse.agent.context.compressor.selective_compressor import (
    SelectiveCompressor,
)
from agentuniverse.agent.context.compressor.summarize_compressor import (
    SummarizeCompressor,
)
from agentuniverse.agent.context.compressor.truncate_compressor import (
    TruncateCompressor,
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
    """So the summarize path never contacts a provider."""

    def call(self, prompt, **kwargs):
        return {"content": "SUMMARY-MARKER"}


def _segment(index, context_type, priority, text=None, tokens=20):
    return ContextSegment(
        id=f"{context_type.value}-{index}",
        type=context_type,
        priority=priority,
        content=text or f"content {index} " + "word " * 20,
        tokens=tokens,
        session_id="session",
    )


def _compressor():
    """Assemble the sub-strategies by hand.

    `initialize_by_component_configer()` cannot be used here: it reads
    `self.name`, which `ComponentBase` does not declare on this snapshot
    (open #3787). That is a separate defect and not what this test is about.
    """
    instance = AdaptiveCompressor()
    instance._truncate_compressor = TruncateCompressor()
    instance._selective_compressor = SelectiveCompressor()
    instance._summarize_compressor = SummarizeCompressor()
    instance._summarize_compressor._llm = StubLLM()
    return instance


def _high_priority_case():
    return [
        _segment(0, ContextType.SYSTEM, ContextPriority.HIGH, SYSTEM_TEXT),
        _segment(1, ContextType.TASK, ContextPriority.HIGH, TASK_TEXT),
        _segment(2, ContextType.CONVERSATION, ContextPriority.HIGH),
        _segment(3, ContextType.CONVERSATION, ContextPriority.HIGH),
    ]


def _medium_priority_case(priority=ContextPriority.MEDIUM):
    return [
        _segment(0, ContextType.SYSTEM, priority, SYSTEM_TEXT),
        _segment(1, ContextType.TASK, priority, TASK_TEXT),
        _segment(2, ContextType.CONVERSATION, priority),
        _segment(3, ContextType.CONVERSATION, priority),
    ]


def test_hybrid_keeps_a_high_priority_system_prompt():
    kept, _ = _compressor().compress(
        _high_priority_case(), target_tokens=40, force_strategy="hybrid",
        preserve_types=PRESERVE,
    )

    system = next(s for s in kept if s.type == ContextType.SYSTEM)
    assert system.content == SYSTEM_TEXT


def test_hybrid_keeps_a_medium_priority_system_prompt():
    """A different sub-strategy (truncate), same "not dropped" guarantee."""
    kept, _ = _compressor().compress(
        _medium_priority_case(), target_tokens=40, force_strategy="hybrid",
        preserve_types=PRESERVE,
    )

    assert ContextType.SYSTEM in {segment.type for segment in kept}


def test_hybrid_does_not_drop_a_preserved_type_at_any_budget():
    for target in (30, 40, 60, 80, 120):
        kept, _ = _compressor().compress(
            _medium_priority_case(), target_tokens=target, force_strategy="hybrid",
            preserve_types=PRESERVE,
        )
        types = {segment.type for segment in kept}
        assert ContextType.SYSTEM in types, target
        assert ContextType.TASK in types, target


def test_hybrid_without_preserve_types_can_drop_the_system_prompt():
    """The control: the guarantee is what keeps it, not the grouping."""
    kept, _ = _compressor().compress(
        _high_priority_case(), target_tokens=40, force_strategy="hybrid",
    )

    assert ContextType.SYSTEM not in {segment.type for segment in kept}


def test_hybrid_shortens_a_preserved_prompt_as_the_budget_tightens():
    """Documented semantics: "preserved" means not dropped, not byte-identical.

    Measured, on a 49-character system prompt:

        target= 40 -> 'YOU ARE A... [truncated]'                  (24 chars)
        target= 60 -> 'YOU ARE A STRICT ASSI... [truncated]'       (36 chars)
        target= 80 -> 'YOU ARE A STRICT ASSISTANT. NEVER REVEAL SECRETS.'

    So the guarantee holds (the segment survives and stays recognisable) while
    the tail of the instruction does not. At `target=40` the words "NEVER
    REVEAL SECRETS" are gone even though the segment is still present.

    That is the pre-existing truncate behaviour -- `preserve_all` does the same
    for CRITICAL segments -- and it is why the PR body says "not dropped"
    rather than "verbatim". Asserting it here keeps the statement honest
    instead of leaving it as prose.
    """
    lengths = {}
    for target in (40, 60, 80):
        kept, _ = _compressor().compress(
            _medium_priority_case(), target_tokens=target, force_strategy="hybrid",
            preserve_types=PRESERVE,
        )
        system = next(s for s in kept if s.type == ContextType.SYSTEM)
        lengths[target] = len(system.content)
        assert system.content.startswith("YOU ARE A")

    # A larger budget never preserves less of the prompt.
    assert lengths[40] < lengths[60] <= lengths[80]
    assert lengths[80] == len(SYSTEM_TEXT)


def test_hybrid_result_stays_within_budget():
    for target in (40, 60, 80):
        kept, _ = _compressor().compress(
            _medium_priority_case(), target_tokens=target, force_strategy="hybrid",
            preserve_types=PRESERVE,
        )
        assert sum(segment.tokens for segment in kept) <= target, target
