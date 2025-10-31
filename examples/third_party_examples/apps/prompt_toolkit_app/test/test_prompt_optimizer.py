# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 12:15
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: test_prompt_optimizer.py
"""Unit tests for prompt optimizer module."""

import unittest
from agentuniverse.prompt.prompt_model import AgentPromptModel
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_optimizer import PromptOptimizer, \
    OptimizationResult, OptimizationStrategy, OptimizationRule, QualityScore, PromptQualityMetric


class TestPromptOptimizer(unittest.TestCase):
    """Test cases for PromptOptimizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = PromptOptimizer()
        self.sample_prompt = AgentPromptModel(
            introduction="你是一个助手",
            target="帮助用户解决问题",
            instruction="请按照以下步骤回答问题：1. 理解问题 2. 分析问题 3. 提供解决方案"
        )
    
    def test_optimize_prompt_basic(self):
        """Test basic prompt optimization."""
        result = self.optimizer.optimize_prompt(self.sample_prompt)
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertIsNotNone(result.original_prompt)
        self.assertIsNotNone(result.optimized_prompt)
        self.assertIsInstance(result.quality_scores, list)
        self.assertIsInstance(result.improvements, list)
        self.assertIsInstance(result.confidence_score, float)
        self.assertGreaterEqual(result.confidence_score, 0.0)
        self.assertLessEqual(result.confidence_score, 1.0)
        self.assertIsInstance(result.suggestions, list)
        self.assertIsInstance(result.optimization_strategies, list)
    
    def test_optimize_prompt_with_strategies(self):
        """Test prompt optimization with specific strategies."""
        strategies = [OptimizationStrategy.CLARITY, OptimizationStrategy.STRUCTURE]
        
        result = self.optimizer.optimize_prompt(
            self.sample_prompt,
            strategies=strategies
        )
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_strategies, strategies)
    
    def test_optimize_prompt_with_custom_rules(self):
        """Test prompt optimization with custom rules."""
        custom_rule = OptimizationRule(
            name="test_rule",
            pattern=r"助手",
            replacement="专业助手",
            description="Test rule",
            priority=5
        )
        
        result = self.optimizer.optimize_prompt(
            self.sample_prompt,
            custom_rules=[custom_rule]
        )
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertIn("专业助手", result.optimized_prompt)
    
    def test_analyze_prompt_quality(self):
        """Test prompt quality analysis."""
        quality_scores = self.optimizer.analyze_prompt_quality(self.sample_prompt)
        
        self.assertIsInstance(quality_scores, list)
        self.assertGreater(len(quality_scores), 0)
        
        for score in quality_scores:
            self.assertIsInstance(score, QualityScore)
            self.assertIsInstance(score.metric, PromptQualityMetric)
            self.assertIsInstance(score.score, float)
            self.assertGreaterEqual(score.score, 0.0)
            self.assertLessEqual(score.score, 1.0)
            self.assertIsInstance(score.feedback, str)
            self.assertIsInstance(score.suggestions, list)
    
    def test_suggest_improvements(self):
        """Test improvement suggestions."""
        suggestions = self.optimizer.suggest_improvements(self.sample_prompt)
        
        self.assertIsInstance(suggestions, list)
        # Suggestions should be strings
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, str)
    
    
    
    def test_get_applicable_rules(self):
        """Test getting applicable rules."""
        strategies = [OptimizationStrategy.CLARITY]
        rules = self.optimizer._get_applicable_rules(strategies, None)
        
        self.assertIsInstance(rules, list)
        # Should have some rules for clarity strategy
        self.assertGreater(len(rules), 0)
    
    def test_get_applicable_rules_with_custom(self):
        """Test getting applicable rules with custom rules."""
        custom_rule = OptimizationRule(
            name="custom_rule",
            pattern=r"test",
            replacement="optimized",
            description="Custom rule",
            priority=10
        )
        
        strategies = [OptimizationStrategy.CLARITY]
        rules = self.optimizer._get_applicable_rules(
            strategies, 
            [custom_rule]
        )
        
        self.assertIsInstance(rules, list)
        # Should include custom rule
        self.assertIn(custom_rule, rules)
    
    
    def test_calculate_metric_score(self):
        """Test metric score calculation."""
        patterns = {
            "positive_patterns": [r"助手", r"帮助"],
            "negative_patterns": [r"不好", r"错误"]
        }
        
        # Test with positive content
        score = self.optimizer._calculate_metric_score(
            "你是一个助手，帮助用户", 
            patterns
        )
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0.5)  # Should be positive
        
        # Test with negative content
        score = self.optimizer._calculate_metric_score(
            "这是一个不好的错误", 
            patterns
        )
        self.assertIsInstance(score, float)
        self.assertLess(score, 0.5)  # Should be negative
    
    def test_generate_feedback(self):
        """Test feedback generation."""
        # Test high score
        feedback = self.optimizer._generate_feedback(
            PromptQualityMetric.CLARITY, 
            0.9
        )
        self.assertIsInstance(feedback, str)
        self.assertIn("优秀", feedback)
        
        # Test low score
        feedback = self.optimizer._generate_feedback(
            PromptQualityMetric.CLARITY, 
            0.3
        )
        self.assertIsInstance(feedback, str)
        self.assertIn("较差", feedback)
    
    def test_generate_suggestions_for_metric(self):
        """Test suggestions generation for metrics."""
        # Test clarity suggestions
        suggestions = self.optimizer._generate_suggestions_for_metric(
            PromptQualityMetric.CLARITY, 
            0.5
        )
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Test high score (should have fewer suggestions)
        suggestions_high = self.optimizer._generate_suggestions_for_metric(
            PromptQualityMetric.CLARITY, 
            0.9
        )
        self.assertIsInstance(suggestions_high, list)
        self.assertLessEqual(len(suggestions_high), len(suggestions))
    
    def test_generate_improvements(self):
        """Test improvements generation."""
        improvements = self.optimizer._generate_improvements(
            self.sample_prompt,
            "优化介绍",
            "优化目标", 
            "优化指令"
        )
        
        self.assertIsInstance(improvements, list)
        # Should have improvements since we changed all sections
        self.assertGreater(len(improvements), 0)
    
    def test_generate_suggestions(self):
        """Test suggestions generation."""
        quality_scores = [
            QualityScore(
                metric=PromptQualityMetric.CLARITY,
                score=0.5,
                feedback="需要改进",
                suggestions=["使用更清晰的语言"]
            )
        ]
        
        suggestions = self.optimizer._generate_suggestions(
            quality_scores,
            [OptimizationStrategy.CLARITY]
        )
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        quality_scores = [
            QualityScore(
                metric=PromptQualityMetric.CLARITY,
                score=0.8,
                feedback="表现良好",
                suggestions=[]
            )
        ]
        
        score = self.optimizer._calculate_confidence_score(
            quality_scores,
            ["改进1", "改进2"]
        )
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_format_prompt(self):
        """Test prompt formatting."""
        formatted = self.optimizer._format_prompt(self.sample_prompt)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("介绍：", formatted)
        self.assertIn("目标：", formatted)
        self.assertIn("指令：", formatted)
    
    def test_format_optimized_prompt(self):
        """Test optimized prompt formatting."""
        formatted = self.optimizer._format_optimized_prompt(
            "优化介绍",
            "优化目标",
            "优化指令"
        )
        
        self.assertIsInstance(formatted, str)
        self.assertIn("介绍：", formatted)
        self.assertIn("目标：", formatted)
        self.assertIn("指令：", formatted)
    
    def test_optimization_rules_initialization(self):
        """Test optimization rules initialization."""
        rules = self.optimizer._optimization_rules
        
        self.assertIsInstance(rules, list)
        self.assertGreater(len(rules), 0)
        
        for rule in rules:
            self.assertIsInstance(rule, OptimizationRule)
            self.assertIsInstance(rule.name, str)
            self.assertIsInstance(rule.pattern, str)
            self.assertIsInstance(rule.replacement, str)
            self.assertIsInstance(rule.description, str)
            self.assertIsInstance(rule.priority, int)
    
    def test_quality_patterns_initialization(self):
        """Test quality patterns initialization."""
        patterns = self.optimizer._quality_patterns
        
        self.assertIsInstance(patterns, dict)
        self.assertGreater(len(patterns), 0)
        
        for metric, pattern_data in patterns.items():
            self.assertIsInstance(metric, PromptQualityMetric)
            self.assertIsInstance(pattern_data, dict)
            self.assertIn("positive_patterns", pattern_data)
            self.assertIn("negative_patterns", pattern_data)
            self.assertIn("weight", pattern_data)
    
    def test_context_keywords_initialization(self):
        """Test context keywords initialization."""
        keywords = self.optimizer._context_keywords
        
        self.assertIsInstance(keywords, dict)
        self.assertGreater(len(keywords), 0)
        
        for context_type, keyword_list in keywords.items():
            self.assertIsInstance(context_type, str)
            self.assertIsInstance(keyword_list, list)
            self.assertGreater(len(keyword_list), 0)


if __name__ == '__main__':
    unittest.main()
