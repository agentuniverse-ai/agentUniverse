# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests mirroring the prompt toolkit test module of the example app."""

import pytest

from agentuniverse.prompt.prompt_model import AgentPromptModel
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_generator import PromptScenario
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_toolkit import (
    PromptGenerationRequest,
    PromptToolkit,
    PromptToolkitConfig,
    PromptToolkitResult,
)


class TestPromptToolkitMirror:
    def test_config_defaults(self):
        config = PromptToolkitConfig()
        assert config.enable_auto_optimization is True
        assert config.confidence_threshold == 0.6
        assert config.optimization_strategies is not None

    def test_request_defaults(self):
        request = PromptGenerationRequest(scenario_description='测试场景')
        assert request.scenario_description == '测试场景'
        assert request.content is None
        assert request.domain is None
        assert request.tone is None

    def test_generate_prompt_from_request(self):
        toolkit = PromptToolkit()
        request = PromptGenerationRequest(scenario_description='我需要一个编程助手来帮助我写Python代码')
        result = toolkit.generate_prompt_from_request(request)
        assert isinstance(result, PromptToolkitResult)
        assert isinstance(result.generated_prompt, AgentPromptModel)
        assert 0.0 <= result.confidence_score <= 1.0
        assert isinstance(result.recommendations, list)

    def test_generate_without_optimization(self):
        config = PromptToolkitConfig(enable_auto_optimization=False)
        toolkit = PromptToolkit(config)
        request = PromptGenerationRequest(scenario_description='编程助手', domain='技术')
        result = toolkit.generate_prompt_from_request(request)
        assert result.optimization_result is None

    def test_analyze_prompt_quality_keys(self):
        toolkit = PromptToolkit()
        prompt = AgentPromptModel(introduction='你是一个助手', target='帮助用户', instruction='回答问题')
        analysis = toolkit.analyze_prompt_quality(prompt)
        assert set(analysis.keys()) == {'quality_scores', 'overall_score', 'recommendations'}
        assert isinstance(analysis['overall_score'], float)

    def test_export_prompt_config_formats(self):
        toolkit = PromptToolkit()
        prompt = AgentPromptModel(introduction='你是一个助手', target='帮助用户', instruction='回答问题')
        yaml_config = toolkit.export_prompt_config(prompt, 'yaml')
        assert 'introduction:' in yaml_config
        assert 'metadata:' in yaml_config
        json_config = toolkit.export_prompt_config(prompt, 'json')
        assert '"introduction"' in json_config
        assert '"metadata"' in json_config

    def test_export_prompt_config_unsupported_format(self):
        toolkit = PromptToolkit()
        prompt = AgentPromptModel(introduction='你是一个助手', target='帮助用户', instruction='回答问题')
        with pytest.raises(ValueError, match='Unsupported format'):
            toolkit.export_prompt_config(prompt, 'xml')

    def test_compare_prompts(self):
        toolkit = PromptToolkit()
        prompt1 = AgentPromptModel(introduction='你是一个助手', target='帮助用户', instruction='回答问题')
        prompt2 = AgentPromptModel(
            introduction='你是一个专业助手',
            target='帮助用户解决问题',
            instruction='请按照以下步骤回答问题：1. 理解问题 2. 分析问题',
        )
        comparison = toolkit.compare_prompts(prompt1, prompt2)
        assert 'prompt1_score' in comparison and 'prompt2_score' in comparison
        assert comparison['better_prompt'] in ('prompt1', 'prompt2')
        assert comparison['score_difference'] >= 0.0
