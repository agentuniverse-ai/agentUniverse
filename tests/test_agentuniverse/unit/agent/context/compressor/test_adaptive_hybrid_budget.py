#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from unittest.mock import Mock

from agentuniverse.agent.context.compressor.adaptive_compressor import (
    AdaptiveCompressor,
)
from agentuniverse.agent.context.context_model import (
    ContextPriority,
    ContextSegment,
    ContextType,
)


def test_hybrid_gives_summarization_its_own_budget():
    compressor = AdaptiveCompressor(name="adaptive")
    high = ContextSegment(
        type=ContextType.TASK,
        priority=ContextPriority.HIGH,
        content="important",
        tokens=20,
    )
    background = ContextSegment(
        type=ContextType.BACKGROUND,
        priority=ContextPriority.MEDIUM,
        content="background",
        tokens=60,
    )

    compressor._selective_compressor = Mock()
    compressor._selective_compressor.compress.return_value = ([high], None)
    compressor._selective_compressor.estimate_information_loss.return_value = 0.0
    compressor._summarize_compressor = Mock()
    compressor._summarize_compressor.compress.return_value = ([background], None)
    compressor._truncate_compressor = Mock()

    compressor._hybrid_compress([high, background], 100, {})

    assert compressor._summarize_compressor.compress.call_args.args[1] == 40
