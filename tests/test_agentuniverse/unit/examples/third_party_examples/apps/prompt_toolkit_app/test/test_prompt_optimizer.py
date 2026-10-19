# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests mirroring the prompt optimizer test module of the example app."""

import pytest
from agentuniverse.prompt.prompt_model import AgentPromptModel
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_optimizer import (
    OptimizationResult,
    OptimizationRule,
    OptimizationStrategy,
    PromptOptimizer,
    PromptQualityMetric,
    QualityScore,
)


def _make_prompt():
    return AgentPromptModel(
        introduction='你是一个助手',
        target='帮助用户解决问题',
        instruction='请按照以下步骤回答问题：1. 理解问题 2. 分析问题 3. 提供解决方案',
    )


class TestPromptOptimizerMirror:
    def test_optimize_prompt_basic(self):
        optimizer = PromptOptimizer()
        result = optimizer.optimize_prompt(_make_prompt())
        assert isinstance(result, OptimizationResult)
        assert result.original_prompt
        assert result.optimized_prompt
        assert isinstance(result.improvements, list)
        assert isinstance(result.suggestions, list)
        assert 0.0 <= result.confidence_score <= 1.0

    def test_optimize_prompt_with_strategies(self):
        optimizer = PromptOptimizer()
        strategies = [OptimizationStrategy.CLARITY, OptimizationStrategy.STRUCTURE]
        result = optimizer.optimize_prompt(_make_prompt(), strategies=strategies)
        assert result.optimization_strategies == strategies

    def test_optimize_prompt_with_custom_rules(self):
        optimizer = PromptOptimizer()
        custom_rule = OptimizationRule(
            name='test_rule',
            pattern=r'助手',
            replacement='专业助手',
            description='Test rule',
            priority=5,
        )
        result = optimizer.optimize_prompt(_make_prompt(), custom_rules=[custom_rule])
        assert '专业助手' in result.optimized_prompt

    def test_analyze_prompt_quality(self):
        optimizer = PromptOptimizer()
        quality_scores = optimizer.analyze_prompt_quality(_make_prompt())
        assert len(quality_scores) > 0
        for score in quality_scores:
            assert isinstance(score, QualityScore)
            assert isinstance(score.metric, PromptQualityMetric)
            assert 0.0 <= score.score <= 1.0
            assert isinstance(score.suggestions, list)

    def test_calculate_metric_score(self):
        optimizer = PromptOptimizer()
        patterns = {'positive_patterns': [r'助手', r'帮助'], 'negative_patterns': [r'不好', r'错误']}
        positive = optimizer._calculate_metric_score('你是一个助手，帮助用户', patterns)
        negative = optimizer._calculate_metric_score('这是一个不好的错误', patterns)
        assert positive > 0.5
        assert negative < 0.5

    def test_generate_feedback(self):
        optimizer = PromptOptimizer()
        high = optimizer._generate_feedback(PromptQualityMetric.CLARITY, 0.9)
        low = optimizer._generate_feedback(PromptQualityMetric.CLARITY, 0.3)
        assert '优秀' in high
        assert '较差' in low

    def test_component_configs_initialized(self):
        optimizer = PromptOptimizer()
        rules = optimizer._optimization_rules
        assert isinstance(rules, list) and len(rules) > 0
        assert all(isinstance(rule, OptimizationRule) for rule in rules)
        patterns = optimizer._quality_patterns
        assert isinstance(patterns, dict) and len(patterns) > 0
        for metric, pattern_data in patterns.items():
            assert isinstance(metric, PromptQualityMetric)
            assert 'positive_patterns' in pattern_data
            assert 'weight' in pattern_data
