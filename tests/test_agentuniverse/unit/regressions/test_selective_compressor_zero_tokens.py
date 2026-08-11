"""Regression tests for selective-compressor loss estimates."""

import pytest

from agentuniverse.agent.context.compressor.selective_compressor import (
    SelectiveCompressor,
)
from agentuniverse.agent.context.context_model import (
    ContextPriority,
    ContextSegment,
    ContextType,
)


def test_information_loss_handles_zero_token_segments():
    compressor = SelectiveCompressor(name="selective")
    segment = ContextSegment(
        id="empty",
        type=ContextType.CONVERSATION,
        priority=ContextPriority.MEDIUM,
        content="",
        tokens=0,
    )

    loss = compressor.estimate_information_loss([segment], [])

    assert loss == pytest.approx(0.1)
