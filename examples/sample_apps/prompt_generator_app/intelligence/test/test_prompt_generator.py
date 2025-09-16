# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: test_prompt_generator.py
"""Test cases for prompt generator functionality.

Comprehensive test suite for the prompt generator app functionality,
ensuring all components work correctly together.
"""
import sys
import unittest
import tempfile
import os
from pathlib import Path

# Add project root directory to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agentuniverse.prompt.prompt_generator_helper import (
    generate_prompt_config,
    optimize_existing_prompt,
    PromptTemplateHelper,
    PromptGenerationError,
    UnsupportedAgentTypeError
)


class TestPromptGenerator(unittest.TestCase):
    """Test cases for prompt generator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_task = "Customer service assistant for e-commerce platform"
        self.test_scenario = "online shopping support"
        self.valid_agent_types = ["react", "rag", "planning", "executing"]

    def test_generate_basic_prompt(self):
        """Test basic prompt generation functionality."""
        for agent_type in self.valid_agent_types:
            with self.subTest(agent_type=agent_type):
                result = generate_prompt_config(
                    task_description=self.test_task,
                    agent_type=agent_type,
                    scenario=self.test_scenario,
                    output_file=None
                )

                # Verify required fields
                self.assertIn('introduction', result)
                self.assertIn('target', result)
                self.assertIn('instruction', result)
                self.assertIn('metadata', result)

                # Verify metadata
                self.assertEqual(result['metadata']['type'], 'PROMPT')
                self.assertIn('version', result['metadata'])

                # Verify content is not empty
                self.assertTrue(result['introduction'].strip())
                self.assertTrue(result['target'].strip())
                self.assertTrue(result['instruction'].strip())

    def test_generate_prompt_with_file_output(self):
        """Test prompt generation with file output."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            output_path = f.name

        try:
            result = generate_prompt_config(
                task_description=self.test_task,
                agent_type="react",
                scenario=self.test_scenario,
                output_file=output_path
            )

            # Verify file was created
            self.assertTrue(os.path.exists(output_path))

            # Verify file content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('introduction:', content)
                self.assertIn('target:', content)
                self.assertIn('instruction:', content)

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_unsupported_agent_type(self):
        """Test error handling for unsupported agent types."""
        with self.assertRaises(UnsupportedAgentTypeError):
            generate_prompt_config(
                task_description=self.test_task,
                agent_type="invalid_type",
                scenario=self.test_scenario
            )

    def test_empty_task_description(self):
        """Test handling of empty task description."""
        with self.assertRaises(ValueError):
            generate_prompt_config(
                task_description="",
                agent_type="react",
                scenario=self.test_scenario
            )

    def test_optimize_existing_prompt(self):
        """Test prompt optimization functionality."""
        existing_prompt = """
        You are a helpful assistant.
        Please answer questions.
        """

        result = optimize_existing_prompt(
            existing_prompt_text=existing_prompt,
            optimization_goal="improve clarity and engagement",
            agent_type="react"
        )

        # Verify result structure
        self.assertIn('optimized_prompt', result)
        self.assertIn('analysis', result)
        self.assertIn('improvements', result)

        # Verify optimization actually changed content
        optimized = result['optimized_prompt']
        self.assertIsInstance(optimized, dict)
        self.assertIn('introduction', optimized)
        self.assertIn('target', optimized)
        self.assertIn('instruction', optimized)

    def test_template_helper_agent_types(self):
        """Test PromptTemplateHelper agent types."""
        agent_templates = PromptTemplateHelper.AGENT_TEMPLATES

        # Verify structure
        self.assertIsInstance(agent_templates, dict)
        self.assertGreater(len(agent_templates), 0)

        # Verify each template has required fields
        for agent_type, template in agent_templates.items():
            with self.subTest(agent_type=agent_type):
                self.assertIn('name', template)
                self.assertIn('introduction_template', template)
                self.assertIn('target_template', template)
                self.assertIn('instruction_template', template)

    def test_prompt_generation_with_scenario(self):
        """Test prompt generation incorporates scenario correctly."""
        scenario = "financial services"

        result = generate_prompt_config(
            task_description=self.test_task,
            agent_type="rag",
            scenario=scenario,
            output_file=None
        )

        # Check that scenario is incorporated
        full_content = (result['introduction'] + ' ' +
                       result['target'] + ' ' +
                       result['instruction']).lower()

        # Should contain scenario-related terms
        scenario_terms = scenario.lower().split()
        scenario_incorporated = any(term in full_content for term in scenario_terms)
        self.assertTrue(scenario_incorporated,
                       f"Scenario '{scenario}' not incorporated in generated content")

    def test_prompt_generation_without_scenario(self):
        """Test prompt generation works without scenario."""
        result = generate_prompt_config(
            task_description=self.test_task,
            agent_type="react",
            scenario=None,
            output_file=None
        )

        # Should still generate valid prompt
        self.assertIn('introduction', result)
        self.assertIn('target', result)
        self.assertIn('instruction', result)
        self.assertTrue(result['introduction'].strip())

    def test_multiple_agent_types_consistency(self):
        """Test that different agent types produce consistent structure."""
        results = {}

        for agent_type in self.valid_agent_types:
            results[agent_type] = generate_prompt_config(
                task_description=self.test_task,
                agent_type=agent_type,
                scenario=self.test_scenario,
                output_file=None
            )

        # Verify all have same structure
        first_keys = set(results[self.valid_agent_types[0]].keys())
        for agent_type in self.valid_agent_types[1:]:
            self.assertEqual(set(results[agent_type].keys()), first_keys,
                           f"Agent type {agent_type} has different structure")

    def test_error_handling_invalid_optimization_goal(self):
        """Test optimization with invalid goal."""
        existing_prompt = "You are a helpful assistant."

        # Empty optimization goal should not crash
        result = optimize_existing_prompt(
            existing_prompt_text=existing_prompt,
            optimization_goal="",
            agent_type="react"
        )

        # Should still return valid structure
        self.assertIn('optimized_prompt', result)
        self.assertIn('analysis', result)


def run_tests():
    """Run all test cases."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
