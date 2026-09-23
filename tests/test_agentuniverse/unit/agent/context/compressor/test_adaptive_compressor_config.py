# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/05 10:00
# @Author  : kaichuan
# @FileName: test_adaptive_compressor_config.py
"""Configuration and fallback tests for AdaptiveCompressor.

AdaptiveCompressor has two construction paths: the yaml driven path used by the
framework bootstrap (``initialize_by_component_configer``) and the direct
constructor used by ``ContextManager`` and by callers that build the component
in code.  Both used to leave the compressor unusable, either with
``NameError: name 'kwargs' is not defined`` or with ``None`` sub compressors,
so both paths are covered below together with the strategy fallbacks.
"""

from pathlib import Path

import pytest

from agentuniverse.agent.context.compressor.adaptive_compressor import (
    AdaptiveCompressor,
    CompressionStrategy,
)
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextPriority,
    ContextType,
)
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)
from agentuniverse.base.config.configer import Configer

# tests/test_agentuniverse/unit/agent/context/compressor/<this file>
REPO_ROOT = Path(__file__).resolve().parents[6]
ADAPTIVE_CONFIG_PATH = (
    REPO_ROOT / "examples" / "context_engineering" / "adaptive_compressor.yaml"
)


def _load_adaptive_configer() -> ComponentConfiger:
    """Load the adaptive compressor example config the way bootstrap does."""
    configer = Configer(path=str(ADAPTIVE_CONFIG_PATH)).load()
    return ComponentConfiger().load_by_configer(configer)


def _make_segments(
    count: int = 10,
    context_type: ContextType = ContextType.BACKGROUND,
    priority: ContextPriority = ContextPriority.MEDIUM,
) -> list:
    """Build segments whose total token count exceeds a typical target.

    Ten segments of 100 tokens give 1000 tokens in total, which is well above
    the targets used below and pushes the strategy selection towards the
    quality oriented strategies (SUMMARIZE/HYBRID).
    """
    return [
        ContextSegment(
            type=context_type,
            priority=priority,
            content=f"Background knowledge chunk number {i}",
            tokens=100,
            session_id="compressor_config_test",
        )
        for i in range(count)
    ]


class _StubLLM:
    """Minimal LLM stand in.

    ``SummarizeCompressor`` only needs a non ``None`` object: an LLM without a
    ``call`` method makes it use its local summarization, which keeps these
    tests hermetic (no network access and no model configuration required).
    """

    def __init__(self, name="default_llm"):
        self.name = name


class _StubLLMManager:
    """Stands in for the LLM manager and records the names it was asked for."""

    def __init__(self):
        self.requested = []

    def get_instance_obj(self, name, **kwargs):
        self.requested.append(name)
        return _StubLLM(name)


@pytest.fixture
def stub_llm_manager(monkeypatch):
    """Replace the LLM lookup so no real LLM has to be configured.

    Patching the module level hook keeps the test independent of the optional
    dependencies that ``agentuniverse.llm.llm_manager`` imports.
    """
    stub = _StubLLMManager()
    monkeypatch.setattr(
        "agentuniverse.agent.context.compressor.adaptive_compressor._load_llm",
        stub.get_instance_obj,
    )
    return stub


class TestAdaptiveCompressorConfiguration:
    """Tests for the yaml driven construction path."""

    def test_initialize_from_example_yaml_does_not_raise(self, stub_llm_manager):
        """Loading the shipped example config must not raise NameError."""
        compressor = AdaptiveCompressor(name="config_test")

        result = compressor.initialize_by_component_configer(_load_adaptive_configer())

        assert result is compressor

    def test_example_yaml_values_are_applied(self, stub_llm_manager):
        """Scalar settings and strategy weights are read from the yaml."""
        compressor = AdaptiveCompressor(name="config_test")
        compressor.initialize_by_component_configer(_load_adaptive_configer())

        assert compressor.name == "adaptive_compressor"
        assert compressor.description == "Intelligent compression strategy selector"
        assert compressor.compression_ratio == 0.6
        assert compressor.quality_threshold == 0.9
        assert compressor.enable_hybrid is True
        assert compressor.truncate_weight == 0.3
        assert compressor.selective_weight == 1.0
        assert compressor.summarize_weight == 0.8

    def test_all_sub_compressors_are_built(self, stub_llm_manager):
        """Every delegate dereferenced by ``_execute_strategy`` must exist."""
        compressor = AdaptiveCompressor(name="config_test")
        compressor.initialize_by_component_configer(_load_adaptive_configer())

        assert compressor._truncate_compressor is not None
        assert compressor._selective_compressor is not None
        assert compressor._summarize_compressor is not None

    def test_summarize_llm_is_wired(self, stub_llm_manager):
        """The summarize delegate must receive an LLM instance."""
        compressor = AdaptiveCompressor(name="config_test", llm_name="default_llm")
        compressor.initialize_by_component_configer(_load_adaptive_configer())

        assert compressor._summarize_compressor._llm is not None
        assert stub_llm_manager.requested == ["default_llm"]

    def test_direct_construction_builds_sub_compressors(self):
        """A directly constructed compressor is usable without any yaml."""
        compressor = AdaptiveCompressor(name="config_test")

        assert compressor.name == "config_test"
        assert compressor._truncate_compressor is not None
        assert compressor._selective_compressor is not None
        assert compressor._summarize_compressor is not None

    def test_configer_without_compressor_keys_keeps_defaults(self, stub_llm_manager):
        """A configer that carries none of our keys must not wipe settings."""
        compressor = AdaptiveCompressor(
            name="config_test", compression_ratio=0.4, enable_hybrid=False
        )
        compressor.initialize_by_component_configer(ComponentConfiger())

        assert compressor.name == "config_test"
        assert compressor.compression_ratio == 0.4
        assert compressor.enable_hybrid is False
        assert compressor._selective_compressor is not None


class TestAdaptiveCompressorFallbacks:
    """Tests for strategy execution on a partially wired compressor."""

    def test_summarize_runs_when_an_llm_is_available(self, stub_llm_manager):
        """With an LLM wired through the config the summarize path executes."""
        compressor = AdaptiveCompressor(name="config_test")
        compressor.initialize_by_component_configer(_load_adaptive_configer())

        compressed, metrics = compressor.compress(
            _make_segments(), 400, force_strategy=CompressionStrategy.SUMMARIZE
        )

        assert metrics.strategy_used == "adaptive_summarize"
        assert metrics.original_tokens == 1000
        assert len(compressed) > 0

    def test_forced_summarize_without_llm_falls_back(self):
        """Forcing SUMMARIZE without an LLM degrades to SELECTIVE."""
        compressor = AdaptiveCompressor(name="config_test")

        compressed, metrics = compressor.compress(
            _make_segments(), 400, force_strategy=CompressionStrategy.SUMMARIZE
        )

        assert metrics.strategy_used == "adaptive_selective_fallback"
        assert len(compressed) > 0
        assert sum(seg.tokens for seg in compressed) <= 400

    def test_forced_hybrid_with_llm_runs_hybrid(self, stub_llm_manager):
        """Hybrid over BACKGROUND/REFERENCE content uses the wired LLM."""
        compressor = AdaptiveCompressor(name="config_test")
        compressor.initialize_by_component_configer(_load_adaptive_configer())

        compressed, metrics = compressor.compress(
            _make_segments(), 400, force_strategy=CompressionStrategy.HYBRID
        )

        assert metrics.strategy_used == "adaptive_hybrid"
        assert len(compressed) > 0

    def test_forced_hybrid_without_llm_falls_back(self):
        """Hybrid that would summarize without an LLM is downgraded."""
        compressor = AdaptiveCompressor(name="config_test")

        compressed, metrics = compressor.compress(
            _make_segments(), 400, force_strategy=CompressionStrategy.HYBRID
        )

        assert metrics.strategy_used == "adaptive_selective_fallback"
        assert len(compressed) > 0

    def test_hybrid_without_summarizable_segments_needs_no_llm(self):
        """Hybrid only needs the LLM for BACKGROUND/REFERENCE content."""
        compressor = AdaptiveCompressor(name="config_test")

        compressed, metrics = compressor.compress(
            _make_segments(context_type=ContextType.CONVERSATION),
            400,
            force_strategy=CompressionStrategy.HYBRID,
        )

        assert metrics.strategy_used == "adaptive_hybrid"
        assert len(compressed) > 0

    def test_default_selection_stays_runnable(self):
        """The default quality settings pick SUMMARIZE, which must not raise."""
        compressor = AdaptiveCompressor(name="config_test")

        compressed, metrics = compressor.compress(_make_segments(), 400)

        assert metrics.strategy_used == "adaptive_selective_fallback"
        assert len(compressed) > 0
        assert sum(seg.tokens for seg in compressed) <= 400

    def test_repeated_compression_is_deterministic(self):
        """Running the same compression twice gives the same strategy."""
        compressor = AdaptiveCompressor(name="config_test")
        segments = _make_segments()

        _, first = compressor.compress(segments, 400)
        _, second = compressor.compress(segments, 400)

        assert first.strategy_used == second.strategy_used
        assert first.compressed_tokens == second.compressed_tokens

    def test_estimate_information_loss_without_delegates(self):
        """The estimate must not crash when the delegates are gone."""
        compressor = AdaptiveCompressor(name="config_test")
        compressor._selective_compressor = None
        segments = _make_segments(count=2)

        loss = compressor.estimate_information_loss(segments, segments[:1])

        assert 0.0 <= loss <= 1.0
