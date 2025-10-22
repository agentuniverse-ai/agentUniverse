# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 12:30
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: test_scenario_analyzer.py
"""Unit tests for scenario analyzer module."""

import unittest
from unittest.mock import Mock, patch
from agentuniverse.prompt.scenario_analyzer import (
    ScenarioAnalyzer,
    ContextType,
    AnalysisConfidence,
    ExtractedContext,
    ScenarioAnalysisResult
)
from agentuniverse.prompt.prompt_generator import PromptScenario, PromptComplexity
from agentuniverse.prompt.prompt_model import AgentPromptModel


class TestScenarioAnalyzer(unittest.TestCase):
    """Test cases for ScenarioAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ScenarioAnalyzer()
        self.sample_content = "我需要一个编程助手来帮助我写Python代码"
        self.sample_additional_context = {
            "domain": "技术",
            "user_role": "开发者",
            "target_audience": "初学者"
        }
    
    def test_analyze_scenario_basic(self):
        """Test basic scenario analysis."""
        result = self.analyzer.analyze_scenario(self.sample_content)
        
        self.assertIsInstance(result, ScenarioAnalysisResult)
        self.assertIsInstance(result.recommended_scenario, PromptScenario)
        self.assertIsInstance(result.extracted_contexts, list)
        self.assertIsInstance(result.confidence_score, float)
        self.assertGreaterEqual(result.confidence_score, 0.0)
        self.assertLessEqual(result.confidence_score, 1.0)
        self.assertIsInstance(result.suggestions, list)
        self.assertIsInstance(result.complexity_level, PromptComplexity)
    
    def test_analyze_scenario_with_additional_context(self):
        """Test scenario analysis with additional context."""
        result = self.analyzer.analyze_scenario(
            self.sample_content,
            self.sample_additional_context
        )
        
        self.assertIsInstance(result, ScenarioAnalysisResult)
        self.assertIsInstance(result.recommended_scenario, PromptScenario)
    
    def test_extract_context_from_content(self):
        """Test context extraction from content."""
        context = self.analyzer.extract_context_from_content(self.sample_content)
        
        self.assertIsInstance(context.domain, str)
        self.assertIsInstance(context.user_role, str)
        self.assertIsInstance(context.target_audience, str)
        self.assertIsInstance(context.constraints, list)
        self.assertIsInstance(context.examples, list)
        self.assertIsInstance(context.tone, str)
    
    def test_extract_domain(self):
        """Test domain extraction."""
        # Test technical domain
        content = "我需要一个编程助手"
        context = self.analyzer._extract_domain(content)
        
        if context:
            self.assertIsInstance(context, ExtractedContext)
            self.assertEqual(context.context_type, ContextType.DOMAIN)
            self.assertIsInstance(context.value, str)
            self.assertIsInstance(context.confidence, AnalysisConfidence)
            self.assertIsInstance(context.source, str)
            self.assertIsInstance(context.suggestions, list)
    
    def test_extract_user_role(self):
        """Test user role extraction."""
        content = "我是一个学生，需要学习编程"
        context = self.analyzer._extract_user_role(content)
        
        if context:
            self.assertIsInstance(context, ExtractedContext)
            self.assertEqual(context.context_type, ContextType.USER_ROLE)
            self.assertIsInstance(context.value, str)
            self.assertIsInstance(context.confidence, AnalysisConfidence)
    
    def test_extract_target_audience(self):
        """Test target audience extraction."""
        content = "我需要为初学者设计一个教程"
        context = self.analyzer._extract_target_audience(content)
        
        if context:
            self.assertIsInstance(context, ExtractedContext)
            self.assertEqual(context.context_type, ContextType.TARGET_AUDIENCE)
            self.assertIsInstance(context.value, str)
            self.assertIsInstance(context.confidence, AnalysisConfidence)
    
    def test_extract_tone(self):
        """Test tone extraction."""
        content = "请用友好的语气回答"
        context = self.analyzer._extract_tone(content)
        
        if context:
            self.assertIsInstance(context, ExtractedContext)
            self.assertEqual(context.context_type, ContextType.TONE)
            self.assertIsInstance(context.value, str)
            self.assertIsInstance(context.confidence, AnalysisConfidence)
    
    def test_extract_constraints(self):
        """Test constraint extraction."""
        content = "必须使用中文回答，不能超过100字"
        contexts = self.analyzer._extract_constraints(content)
        
        self.assertIsInstance(contexts, list)
        for context in contexts:
            self.assertIsInstance(context, ExtractedContext)
            self.assertEqual(context.context_type, ContextType.CONSTRAINTS)
            self.assertIsInstance(context.value, str)
            self.assertIsInstance(context.confidence, AnalysisConfidence)
    
    def test_extract_examples(self):
        """Test example extraction."""
        content = "例如：输入'你好'，输出'Hello'"
        contexts = self.analyzer._extract_examples(content)
        
        self.assertIsInstance(contexts, list)
        for context in contexts:
            self.assertIsInstance(context, ExtractedContext)
            self.assertEqual(context.context_type, ContextType.EXAMPLES)
            self.assertIsInstance(context.value, str)
            self.assertIsInstance(context.confidence, AnalysisConfidence)
    
    
    def test_determine_complexity(self):
        """Test complexity determination."""
        # Test simple complexity
        content = "简单的问题"
        complexity = self.analyzer._determine_complexity(content, [])
        self.assertEqual(complexity, PromptComplexity.SIMPLE)
        
        # Test complex complexity
        content = "复杂的高级系统"
        complexity = self.analyzer._determine_complexity(content, [])
        self.assertEqual(complexity, PromptComplexity.COMPLEX)
        
        # Test medium complexity (default)
        content = "普通的问题"
        complexity = self.analyzer._determine_complexity(content, [])
        self.assertEqual(complexity, PromptComplexity.MEDIUM)
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # Test with empty contexts
        score = self.analyzer._calculate_confidence_score([])
        self.assertEqual(score, 0.3)
        
        # Test with high confidence contexts
        contexts = [
            ExtractedContext(
                context_type=ContextType.DOMAIN,
                value="技术",
                confidence=AnalysisConfidence.HIGH,
                source="编程",
                suggestions=[]
            )
        ]
        score = self.analyzer._calculate_confidence_score(contexts)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_generate_suggestions(self):
        """Test suggestions generation."""
        contexts = [
            ExtractedContext(
                context_type=ContextType.DOMAIN,
                value="技术",
                confidence=AnalysisConfidence.MEDIUM,
                source="编程",
                suggestions=["添加更多技术术语"]
            )
        ]
        
        suggestions = self.analyzer._generate_suggestions(contexts, 0.4)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        self.assertIn("添加更多技术术语", suggestions)
    
    def test_get_context_value(self):
        """Test context value retrieval."""
        contexts = [
            ExtractedContext(
                context_type=ContextType.DOMAIN,
                value="技术",
                confidence=AnalysisConfidence.HIGH,
                source="编程",
                suggestions=[]
            )
        ]
        
        # Test existing context
        value = self.analyzer._get_context_value(
            contexts, 
            ContextType.DOMAIN, 
            "默认"
        )
        self.assertEqual(value, "技术")
        
        # Test non-existing context
        value = self.analyzer._get_context_value(
            contexts, 
            ContextType.USER_ROLE, 
            "默认"
        )
        self.assertEqual(value, "默认")
    
    def test_domain_patterns_initialization(self):
        """Test domain patterns initialization."""
        patterns = self.analyzer._domain_patterns
        
        self.assertIsInstance(patterns, dict)
        self.assertGreater(len(patterns), 0)
        
        for domain, keyword_list in patterns.items():
            self.assertIsInstance(domain, str)
            self.assertIsInstance(keyword_list, list)
            self.assertGreater(len(keyword_list), 0)
    
    def test_role_patterns_initialization(self):
        """Test role patterns initialization."""
        patterns = self.analyzer._role_patterns
        
        self.assertIsInstance(patterns, dict)
        self.assertGreater(len(patterns), 0)
        
        for role, keyword_list in patterns.items():
            self.assertIsInstance(role, str)
            self.assertIsInstance(keyword_list, list)
            self.assertGreater(len(keyword_list), 0)
    
    def test_audience_patterns_initialization(self):
        """Test audience patterns initialization."""
        patterns = self.analyzer._audience_patterns
        
        self.assertIsInstance(patterns, dict)
        self.assertGreater(len(patterns), 0)
        
        for audience, keyword_list in patterns.items():
            self.assertIsInstance(audience, str)
            self.assertIsInstance(keyword_list, list)
            self.assertGreater(len(keyword_list), 0)
    
    def test_tone_patterns_initialization(self):
        """Test tone patterns initialization."""
        patterns = self.analyzer._tone_patterns
        
        self.assertIsInstance(patterns, dict)
        self.assertGreater(len(patterns), 0)
        
        for tone, keyword_list in patterns.items():
            self.assertIsInstance(tone, str)
            self.assertIsInstance(keyword_list, list)
            self.assertGreater(len(keyword_list), 0)
    
    def test_complexity_indicators_initialization(self):
        """Test complexity indicators initialization."""
        indicators = self.analyzer._complexity_indicators
        
        self.assertIsInstance(indicators, dict)
        self.assertGreater(len(indicators), 0)
        
        for complexity, indicator_list in indicators.items():
            self.assertIsInstance(complexity, str)
            self.assertIsInstance(indicator_list, list)
            self.assertGreater(len(indicator_list), 0)
    
    def test_constraint_patterns_initialization(self):
        """Test constraint patterns initialization."""
        patterns = self.analyzer._constraint_patterns
        
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0)
        
        for pattern in patterns:
            self.assertIsInstance(pattern, str)
    
    def test_example_patterns_initialization(self):
        """Test example patterns initialization."""
        patterns = self.analyzer._example_patterns
        
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0)
        
        for pattern in patterns:
            self.assertIsInstance(pattern, str)


if __name__ == '__main__':
    unittest.main()
