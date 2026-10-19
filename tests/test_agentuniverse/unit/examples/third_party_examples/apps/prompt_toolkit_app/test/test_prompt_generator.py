# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests mirroring the prompt generator test module of the example app."""

import pytest

from agentuniverse.prompt.prompt_model import AgentPromptModel
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_generator import (
    PromptComplexity,
    PromptGenerator,
    PromptScenario,
    ScenarioContext,
)


def _make_context():
    return ScenarioContext(
        domain='技术',
        user_role='开发者',
        target_audience='初学者',
        constraints=['必须使用中文'],
        examples=[{'input': '如何写函数', 'output': 'def function():\n    pass'}],
        tone='友好',
    )


class TestPromptGeneratorMirror:
    def test_analyze_scenario_code_generation(self):
        generator = PromptGenerator()
        scenario = generator.analyze_scenario('我需要一个编程助手来帮助我写Python代码', _make_context())
        assert scenario == PromptScenario.CODE_GENERATION

    def test_analyze_scenario_analytical_and_research(self):
        generator = PromptGenerator()
        context = _make_context()
        assert generator.analyze_scenario('我需要分析数据并生成报告', context) == PromptScenario.ANALYTICAL
        assert generator.analyze_scenario('我需要研究人工智能技术', context) == PromptScenario.RESEARCH

    def test_analyze_scenario_default_conversational(self):
        generator = PromptGenerator()
        scenario = generator.analyze_scenario('我需要一个普通的对话助手', _make_context())
        assert scenario == PromptScenario.CONVERSATIONAL

    def test_generate_prompt_returns_model_with_sections(self):
        generator = PromptGenerator()
        prompt = generator.generate_prompt(
            scenario=PromptScenario.CODE_GENERATION,
            context=_make_context(),
            complexity=PromptComplexity.MEDIUM,
        )
        assert isinstance(prompt, AgentPromptModel)
        assert prompt.introduction
        assert prompt.target
        assert prompt.instruction

    def test_generate_prompt_invalid_scenario_raises(self):
        generator = PromptGenerator()
        with pytest.raises(ValueError, match='Invalid scenario'):
            generator.generate_prompt(scenario='invalid_scenario', context=_make_context())

    def test_generate_prompt_invalid_context_raises(self):
        generator = PromptGenerator()
        with pytest.raises(ValueError, match='Invalid context'):
            generator.generate_prompt(scenario=PromptScenario.CONVERSATIONAL, context='invalid')

    def test_generate_prompt_includes_custom_requirements(self):
        generator = PromptGenerator()
        prompt = generator.generate_prompt(
            scenario=PromptScenario.CODE_GENERATION,
            context=_make_context(),
            custom_requirements='请确保回答包含具体的代码示例',
        )
        assert '代码示例' in prompt.instruction

    def test_format_prompt_markers(self):
        generator = PromptGenerator()
        prompt = generator.generate_prompt(scenario=PromptScenario.CONVERSATIONAL, context=_make_context())
        formatted = generator._format_prompt(prompt)
        assert '介绍：' in formatted
        assert '目标：' in formatted
        assert '指令：' in formatted
