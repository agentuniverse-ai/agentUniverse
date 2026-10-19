# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the PromptGenerator demo module."""

import pytest

from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_generator import (
    PromptComplexity,
    PromptGenerator,
    PromptScenario,
    ScenarioContext,
)


@pytest.fixture
def generator():
    return PromptGenerator()


@pytest.fixture
def context():
    return ScenarioContext(domain="education", user_role="student",
                           target_audience="student",
                           constraints=["none"], examples=[])


class TestPromptGenerator:
    """Test prompt generation pure behaviors."""

    def test_invalid_scenario_raises(self, generator, context):
        with pytest.raises(ValueError, match="Invalid scenario"):
            generator.generate_prompt("bogus", context=context)

    def test_invalid_context_raises(self, generator):
        with pytest.raises(ValueError, match="Invalid context"):
            generator.generate_prompt(PromptScenario.CONVERSATIONAL,
                                      context="not-a-context")

    def test_generate_prompt_returns_model(self, generator, context):
        model = generator.generate_prompt(
            PromptScenario.CONVERSATIONAL, context=context,
            complexity=PromptComplexity.MEDIUM)
        assert model.introduction
        assert model.target
        assert model.instruction

    def test_generate_prompt_with_custom_requirements(self, generator,
                                                      context):
        model = generator.generate_prompt(
            PromptScenario.TASK_ORIENTED, context=context,
            custom_requirements="keep it simple")
        assert model.instruction

    def test_optimize_prompt_returns_result(self, generator, context):
        model = generator.generate_prompt(PromptScenario.CONVERSATIONAL,
                                          context=context)
        result = generator.optimize_prompt(model)
        assert result.optimized_prompt
        assert result.confidence_score >= 0.0
