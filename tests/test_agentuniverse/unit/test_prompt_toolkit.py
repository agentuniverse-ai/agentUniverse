# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 12:45
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: test_prompt_toolkit.py
"""Unit tests for prompt toolkit module."""

import unittest
from unittest.mock import Mock, patch
from agentuniverse.prompt.prompt_toolkit import (
    PromptToolkit,
    PromptToolkitConfig,
    PromptGenerationRequest,
    PromptToolkitResult
)
from agentuniverse.prompt.prompt_generator import PromptScenario, PromptComplexity
from agentuniverse.prompt.prompt_optimizer import OptimizationStrategy
from agentuniverse.prompt.prompt_model import AgentPromptModel


class TestPromptToolkit(unittest.TestCase):
    """Test cases for PromptToolkit class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = PromptToolkitConfig()
        self.toolkit = PromptToolkit(self.config)
        self.sample_request = PromptGenerationRequest(
            scenario_description="我需要一个编程助手",
            content="帮助我写Python代码",
            target_audience="初学者",
            domain="技术",
            constraints=["必须使用中文"],
            examples=[{"input": "如何写函数", "output": "def function():\n    pass"}],
            tone="友好"
        )
    
    def test_initialization(self):
        """Test toolkit initialization."""
        self.assertIsNotNone(self.toolkit.config)
        self.assertIsNotNone(self.toolkit.generator)
        self.assertIsNotNone(self.toolkit.optimizer)
        self.assertIsNotNone(self.toolkit.analyzer)
    
    def test_initialization_with_config(self):
        """Test toolkit initialization with custom config."""
        custom_config = PromptToolkitConfig(
            enable_auto_optimization=False,
            default_scenario=PromptScenario.CREATIVE
        )
        toolkit = PromptToolkit(custom_config)
        
        self.assertEqual(toolkit.config.enable_auto_optimization, False)
        self.assertEqual(toolkit.config.default_scenario, PromptScenario.CREATIVE)
    
    def test_generate_prompt_from_request(self):
        """Test prompt generation from request."""
        result = self.toolkit.generate_prompt_from_request(self.sample_request)
        
        self.assertIsInstance(result, PromptToolkitResult)
        self.assertIsInstance(result.generated_prompt, AgentPromptModel)
        self.assertIsNotNone(result.analysis_result)
        self.assertIsInstance(result.recommendations, list)
        self.assertIsInstance(result.confidence_score, float)
        self.assertGreaterEqual(result.confidence_score, 0.0)
        self.assertLessEqual(result.confidence_score, 1.0)
        self.assertIsInstance(result.metadata, dict)
    
    def test_generate_prompt_from_request_with_optimization(self):
        """Test prompt generation with optimization enabled."""
        result = self.toolkit.generate_prompt_from_request(self.sample_request)
        
        # Should have optimization result since it's enabled by default
        if self.config.enable_auto_optimization:
            self.assertIsNotNone(result.optimization_result)
    
    def test_generate_prompt_from_request_without_optimization(self):
        """Test prompt generation without optimization."""
        config = PromptToolkitConfig(enable_auto_optimization=False)
        toolkit = PromptToolkit(config)
        
        result = toolkit.generate_prompt_from_request(self.sample_request)
        
        self.assertIsInstance(result, PromptToolkitResult)
        self.assertIsNone(result.optimization_result)
    
    def test_optimize_existing_prompt(self):
        """Test optimization of existing prompt."""
        prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        result = self.toolkit.optimize_existing_prompt(prompt)
        
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.original_prompt)
        self.assertIsNotNone(result.optimized_prompt)
        self.assertIsInstance(result.improvements, list)
        self.assertIsInstance(result.confidence_score, float)
    
    def test_optimize_existing_prompt_with_strategies(self):
        """Test optimization with specific strategies."""
        prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        strategies = [OptimizationStrategy.CLARITY, OptimizationStrategy.STRUCTURE]
        result = self.toolkit.optimize_existing_prompt(prompt, strategies)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.optimization_strategies, strategies)
    
    def test_analyze_prompt_quality(self):
        """Test prompt quality analysis."""
        prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        result = self.toolkit.analyze_prompt_quality(prompt)
        
        self.assertIsInstance(result, dict)
        self.assertIn("quality_scores", result)
        self.assertIn("overall_score", result)
        self.assertIn("recommendations", result)
        
        self.assertIsInstance(result["quality_scores"], list)
        self.assertIsInstance(result["overall_score"], float)
        self.assertIsInstance(result["recommendations"], list)
    
    def test_batch_generate_prompts(self):
        """Test batch prompt generation."""
        requests = [
            PromptGenerationRequest(
                scenario_description="编程助手",
                domain="技术"
            ),
            PromptGenerationRequest(
                scenario_description="客服助手",
                domain="商业"
            )
        ]
        
        results = self.toolkit.batch_generate_prompts(requests)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        
        for result in results:
            self.assertIsInstance(result, PromptToolkitResult)
            self.assertIsInstance(result.generated_prompt, AgentPromptModel)
    
    def test_batch_generate_prompts_with_error(self):
        """Test batch generation with error handling."""
        # Create a request that might cause an error
        requests = [
            PromptGenerationRequest(
                scenario_description="",  # Empty description might cause issues
                domain="技术"
            )
        ]
        
        results = self.toolkit.batch_generate_prompts(requests)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        
        # Should handle errors gracefully
        result = results[0]
        self.assertIsInstance(result, PromptToolkitResult)
    
    def test_compare_prompts(self):
        """Test prompt comparison."""
        prompt1 = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        prompt2 = AgentPromptModel(
            introduction="你是一个专业助手",
            target="帮助用户解决问题",
            instruction="请按照以下步骤回答问题：1. 理解问题 2. 分析问题 3. 提供解决方案"
        )
        
        result = self.toolkit.compare_prompts(prompt1, prompt2)
        
        self.assertIsInstance(result, dict)
        self.assertIn("prompt1_score", result)
        self.assertIn("prompt2_score", result)
        self.assertIn("better_prompt", result)
        self.assertIn("score_difference", result)
        self.assertIn("detailed_comparison", result)
        
        self.assertIsInstance(result["prompt1_score"], float)
        self.assertIsInstance(result["prompt2_score"], float)
        self.assertIn(result["better_prompt"], ["prompt1", "prompt2"])
        self.assertIsInstance(result["score_difference"], float)
        self.assertIsInstance(result["detailed_comparison"], dict)
    
    def test_export_prompt_config_yaml(self):
        """Test prompt export as YAML."""
        prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        yaml_config = self.toolkit.export_prompt_config(prompt, "yaml")
        
        self.assertIsInstance(yaml_config, str)
        self.assertIn("introduction:", yaml_config)
        self.assertIn("target:", yaml_config)
        self.assertIn("instruction:", yaml_config)
        self.assertIn("metadata:", yaml_config)
    
    def test_export_prompt_config_json(self):
        """Test prompt export as JSON."""
        prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        json_config = self.toolkit.export_prompt_config(prompt, "json")
        
        self.assertIsInstance(json_config, str)
        self.assertIn("introduction", json_config)
        self.assertIn("target", json_config)
        self.assertIn("instruction", json_config)
        self.assertIn("metadata", json_config)
    
    def test_export_prompt_config_unsupported_format(self):
        """Test export with unsupported format."""
        prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        with self.assertRaises(ValueError):
            self.toolkit.export_prompt_config(prompt, "xml")
    
    def test_generate_recommendations(self):
        """Test recommendations generation."""
        # Mock analysis result
        analysis_result = Mock()
        analysis_result.confidence_score = 0.4
        analysis_result.suggestions = ["建议1", "建议2"]
        
        # Mock optimization result
        optimization_result = Mock()
        optimization_result.suggestions = ["优化建议1", "优化建议2"]
        
        prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        recommendations = self.toolkit._generate_recommendations(
            analysis_result,
            optimization_result,
            prompt
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
    
    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation."""
        # Mock analysis result
        analysis_result = Mock()
        analysis_result.confidence_score = 0.8
        
        # Mock optimization result
        optimization_result = Mock()
        optimization_result.confidence_score = 0.9
        
        confidence = self.toolkit._calculate_overall_confidence(
            analysis_result,
            optimization_result
        )
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_calculate_overall_confidence_without_optimization(self):
        """Test confidence calculation without optimization."""
        # Mock analysis result
        analysis_result = Mock()
        analysis_result.confidence_score = 0.8
        
        confidence = self.toolkit._calculate_overall_confidence(
            analysis_result,
            None
        )
        
        self.assertEqual(confidence, 0.8)
    
    def test_export_as_yaml(self):
        """Test YAML export functionality."""
        prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        yaml_content = self.toolkit._export_as_yaml(prompt)
        
        self.assertIsInstance(yaml_content, str)
        self.assertIn("introduction:", yaml_content)
        self.assertIn("target:", yaml_content)
        self.assertIn("instruction:", yaml_content)
        self.assertIn("metadata:", yaml_content)
    
    def test_export_as_json(self):
        """Test JSON export functionality."""
        prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户",
            instruction="回答问题"
        )
        
        json_content = self.toolkit._export_as_json(prompt)
        
        self.assertIsInstance(json_content, str)
        self.assertIn("introduction", json_content)
        self.assertIn("target", json_content)
        self.assertIn("instruction", json_content)
        self.assertIn("metadata", json_content)
    
    def test_prompt_toolkit_config_defaults(self):
        """Test default configuration values."""
        config = PromptToolkitConfig()
        
        self.assertTrue(config.enable_auto_optimization)
        self.assertEqual(config.default_scenario, PromptScenario.CONVERSATIONAL)
        self.assertEqual(config.default_complexity, PromptComplexity.MEDIUM)
        self.assertIsNotNone(config.optimization_strategies)
        self.assertEqual(config.confidence_threshold, 0.6)
    
    def test_prompt_generation_request_defaults(self):
        """Test default request values."""
        request = PromptGenerationRequest(
            scenario_description="测试场景"
        )
        
        self.assertEqual(request.scenario_description, "测试场景")
        self.assertIsNone(request.content)
        self.assertIsNone(request.target_audience)
        self.assertIsNone(request.domain)
        self.assertIsNone(request.constraints)
        self.assertIsNone(request.examples)
        self.assertIsNone(request.tone)
        self.assertIsNone(request.complexity)
        self.assertIsNone(request.custom_requirements)


if __name__ == '__main__':
    unittest.main()
