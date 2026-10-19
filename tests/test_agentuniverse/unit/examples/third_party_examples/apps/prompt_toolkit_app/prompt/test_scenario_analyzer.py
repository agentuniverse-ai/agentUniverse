# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the ScenarioAnalyzer demo module."""

from examples.third_party_examples.apps.prompt_toolkit_app.prompt.scenario_analyzer import (
    PromptComplexity,
    PromptScenario,
    ScenarioAnalysisResult,
    ScenarioAnalyzer,
)


class TestScenarioAnalyzer:
    """Test scenario analysis pure behaviors."""

    def test_analyze_returns_result(self):
        analyzer = ScenarioAnalyzer()
        result = analyzer.analyze_scenario("学生需要在手机上练习英语口语")
        assert isinstance(result, ScenarioAnalysisResult)
        assert isinstance(result.recommended_scenario, PromptScenario)
        assert isinstance(result.complexity_level, PromptComplexity)
        assert 0.0 <= result.confidence_score <= 1.0

    def test_analyze_empty_content(self):
        result = ScenarioAnalyzer().analyze_scenario("")
        assert isinstance(result.extracted_contexts, list)

    def test_extract_context_returns_fields(self):
        context = ScenarioAnalyzer().extract_context_from_content(
            "我是一名小学语文老师，需要设计课堂活动")
        assert context.domain
        assert context.user_role
