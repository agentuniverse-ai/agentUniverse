# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: test_prompt_optimizer.py

import unittest
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agentuniverse.prompt.prompt_generator_helper import (
    optimize_existing_prompt,
    _analyze_existing_prompt,
    _generate_improvement_suggestions,
    _apply_optimizations
)


class PromptOptimizerTest(unittest.TestCase):
    """
    Prompt optimizer functionality test class.
    """

    def test_basic_prompt_optimization(self):
        """Test basic prompt optimization functionality."""
        original_prompt = "你是一个AI助手，帮助用户回答问题。"
        optimization_goal = "提高专业性和准确性"

        result = optimize_existing_prompt(
            existing_prompt_text=original_prompt,
            optimization_goal=optimization_goal
        )

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.introduction)
        self.assertIsNotNone(result.target)
        self.assertIsNotNone(result.instruction)

        # Ensure optimized content is more detailed
        self.assertGreater(len(result.introduction), len("你是一个AI助手"))

        print(f"\nBasic optimization test results:")
        print(f"Original: {original_prompt}")
        print(f"Optimized introduction: {result.introduction}")

    def test_typed_prompt_optimization(self):
        """Test type-specific prompt optimization."""
        original_prompt = "你是客服，回答用户问题。"
        optimization_goal = "增强服务质量"
        agent_type = "react"

        result = optimize_existing_prompt(
            existing_prompt_text=original_prompt,
            optimization_goal=optimization_goal,
            agent_type=agent_type
        )

        self.assertIsNotNone(result)
        # ReAct type optimization should generate reasonable content
        combined_content = f"{result.introduction} {result.target} {result.instruction}".lower()
        self.assertTrue(any(keyword in combined_content for keyword in ["工具", "专业", "智能", "助手", "服务"]))

        print(f"\nType-specific optimization test results:")
        print(f"Type: {agent_type}")
        print(f"Optimized instruction includes tools: {'工具' in result.instruction}")

    def test_scenario_prompt_optimization(self):
        """Test scenario-based prompt optimization."""
        original_prompt = "分析数据"
        optimization_goal = "提升分析深度"
        scenario = "电商业务分析"

        result = optimize_existing_prompt(
            existing_prompt_text=original_prompt,
            optimization_goal=optimization_goal,
            scenario=scenario
        )

        self.assertIsNotNone(result)
        # Scenario-based optimization should reflect scenario-related information in content
        combined_content = f"{result.introduction} {result.target} {result.instruction}".lower()
        # Scenario-based optimization should include relevant keywords
        self.assertTrue(any(keyword in combined_content for keyword in ["分析", "数据", "专业", "智能", "助手", "服务", "业务"]))

        print(f"\nScenario-based optimization test results:")
        print(f"Scenario: {scenario}")
        print(f"Optimized content includes analysis elements: {'分析' in combined_content}")

    def test_yaml_format_optimization(self):
        """Test YAML format prompt optimization."""
        yaml_prompt = """
introduction: 你是助手
target: 帮助用户
instruction: |
  回答问题
metadata:
  type: 'PROMPT'
  version: 'v1'
"""

        result = optimize_existing_prompt(
            existing_prompt_text=yaml_prompt,
            optimization_goal="完善prompt结构"
        )

        self.assertIsNotNone(result)
        self.assertNotEqual(result.introduction, "你是助手")  # Should be optimized
        self.assertNotEqual(result.target, "帮助用户")  # Should be optimized
        self.assertGreater(len(result.instruction), 10)  # Instructions should be more detailed

        print(f"\nYAML format optimization test results:")
        print(f"Original instruction length: {len('回答问题')}")
        print(f"Optimized instruction length: {len(result.instruction)}")

    def test_optimization_error_handling(self):
        """Test error handling in optimization process."""
        # Test handling of empty prompt (should return reasonable result without throwing exception)
        result = optimize_existing_prompt(
            existing_prompt_text="",
            optimization_goal="优化空prompt"
        )
        self.assertIsNotNone(result)
        # Empty input should generate basic prompt structure
        self.assertTrue(len(result.introduction) > 0 or len(result.target) > 0)

        # Test invalid optimization goals
        result = optimize_existing_prompt(
            existing_prompt_text="你是助手",
            optimization_goal=""  # Empty optimization goal
        )
        # Even with empty goal, should return basic optimization result
        self.assertIsNotNone(result)

        print(f"\nError handling test passed")

    def test_multiple_optimizations_consistency(self):
        """Test consistency of multiple optimizations."""
        original_prompt = "你是分析师"
        optimization_goal = "提升专业能力"

        # Perform two identical optimizations
        result1 = optimize_existing_prompt(
            existing_prompt_text=original_prompt,
            optimization_goal=optimization_goal
        )

        result2 = optimize_existing_prompt(
            existing_prompt_text=original_prompt,
            optimization_goal=optimization_goal
        )

        # Results should be structurally consistent (although specific content may differ)
        self.assertIsNotNone(result1.introduction)
        self.assertIsNotNone(result2.introduction)
        self.assertIsNotNone(result1.target)
        self.assertIsNotNone(result2.target)

        print(f"\nConsistency test:")
        print(f"Both optimizations successfully generated complete structures")


if __name__ == '__main__':
    unittest.main()
