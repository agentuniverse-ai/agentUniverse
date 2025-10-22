# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: test_prompt_generator_helper.py

"""Test cases for PromptTemplateHelper.

This test file provides comprehensive test cases for the prompt generation helper tool,
ensuring all functionality works correctly and generated configurations comply with
agentUniverse standards.
"""

import os
import tempfile
import unittest

from agentuniverse.prompt.prompt_generator_helper import (
    PromptTemplateHelper,
    generate_prompt_config,
    optimize_existing_prompt
)


class TestPromptTemplateHelper(unittest.TestCase):
    """Test cases for PromptTemplateHelper class."""

    def test_generate_prompt_template_react(self):
        """Test generating ReAct agent prompt template."""
        prompt_model = PromptTemplateHelper.generate_prompt_template(
            task_description="智能客服助手，处理用户咨询和订单问题",
            agent_type="react",
            scenario="电商平台"
        )

        self.assertIsNotNone(prompt_model.introduction)
        self.assertIsNotNone(prompt_model.target)
        self.assertIsNotNone(prompt_model.instruction)
        # Check if the generated prompt contains relevant content
        combined_text = f"{prompt_model.introduction} {prompt_model.target} {prompt_model.instruction}".lower()
        self.assertTrue(any(keyword in combined_text for keyword in ["客服", "服务", "service", "咨询", "assistant"]))
        self.assertTrue(any(keyword in combined_text for keyword in ["电商", "平台", "platform", "商务"]))
        self.assertIn("工具", prompt_model.instruction.lower())

    def test_generate_prompt_template_rag(self):
        """Test generating RAG agent prompt template."""
        prompt_model = PromptTemplateHelper.generate_prompt_template(
            task_description="医疗咨询专家，基于医疗知识库回答用户问题",
            agent_type="rag",
            scenario="在线医疗"
        )

        self.assertIsNotNone(prompt_model.introduction)
        self.assertIsNotNone(prompt_model.target)
        self.assertIsNotNone(prompt_model.instruction)
        # Check if the generated prompt contains relevant domain context
        combined_text = f"{prompt_model.introduction} {prompt_model.target} {prompt_model.instruction}".lower()
        self.assertTrue(any(keyword in combined_text for keyword in ["医疗", "医疗知识", "healthcare", "analysis", "information", "expert", "professional"]))
        self.assertIn("医疗", prompt_model.target.lower())

    def test_generate_yaml_config(self):
        """Test generating YAML configuration."""
        prompt_model = PromptTemplateHelper.generate_prompt_template(
            task_description="Test agent",
            agent_type="react"
        )

        yaml_config = PromptTemplateHelper.generate_yaml_config(
            prompt_model,
            version_name="test.cn"
        )

        self.assertIn("introduction:", yaml_config)
        self.assertIn("target:", yaml_config)
        self.assertIn("instruction:", yaml_config)
        self.assertIn("metadata:", yaml_config)
        self.assertIn("type: 'PROMPT'", yaml_config)
        self.assertIn("version: 'test.cn'", yaml_config)

    def test_get_supported_agent_types(self):
        """Test retrieving supported agent types."""
        types = PromptTemplateHelper.get_supported_agent_types()

        self.assertIn("react", types)
        self.assertIn("rag", types)
        self.assertIn("planning", types)
        self.assertIn("executing", types)
        self.assertIn("expressing", types)
        self.assertIn("reviewing", types)
        self.assertIn("workflow", types)

    def test_extract_domain(self):
        """Test domain extraction functionality."""
        # Test financial domain recognition
        domain = PromptTemplateHelper._extract_domain("Intelligent stock analysis assistant")
        self.assertEqual(domain, "financial")

        # Test medical domain recognition
        domain = PromptTemplateHelper._extract_domain("Medical diagnosis assistant")
        self.assertEqual(domain, "medical")

        # Test customer service domain recognition
        domain = PromptTemplateHelper._extract_domain("Intelligent customer service system")
        self.assertEqual(domain, "service")


class TestPromptOptimization(unittest.TestCase):
    """Prompt optimization functionality tests."""

    def test_optimize_existing_prompt(self):
        """Test optimizing existing prompt."""
        original_prompt = "You are an AI assistant that helps users answer questions."

        optimized_prompt = optimize_existing_prompt(
            existing_prompt_text=original_prompt,
            optimization_goal="Improve professionalism",
            agent_type="react",
            scenario="Technical support"
        )

        self.assertIsNotNone(optimized_prompt.introduction)
        self.assertIsNotNone(optimized_prompt.target)
        self.assertIsNotNone(optimized_prompt.instruction)
        # The optimized prompt should be more professional than the original prompt
        self.assertIn("professional", optimized_prompt.introduction.lower())


class TestPromptConfigGeneration(unittest.TestCase):
    """Prompt configuration generation functionality tests."""

    def setUp(self):
        """Set up temporary directory."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_prompt_config(self):
        """Test generating prompt configuration."""
        output_file = os.path.join(self.temp_dir, "test_prompt.yaml")

        yaml_config = generate_prompt_config(
            task_description="Test agent",
            agent_type="react",
            scenario="Test scenario",
            version_name="test.cn",
            output_file=output_file
        )

        # Check returned configuration content
        self.assertIn("introduction:", yaml_config)
        self.assertIn("target:", yaml_config)
        self.assertIn("instruction:", yaml_config)
        self.assertIn("metadata:", yaml_config)

        # Check if file is generated
        self.assertTrue(os.path.exists(output_file))

        # Check file content
        with open(output_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
            self.assertEqual(file_content, yaml_config)

    def test_generate_different_agent_types(self):
        """Test generating different types of agent configurations."""
        agent_types = ['react', 'rag', 'planning', 'executing', 'expressing']

        for agent_type in agent_types:
            with self.subTest(agent_type=agent_type):
                yaml_config = generate_prompt_config(
                    task_description=f"Test {agent_type} agent",
                    agent_type=agent_type,
                    scenario="Test scenario"
                )

                self.assertIn("introduction:", yaml_config)
                self.assertIn("target:", yaml_config)
                self.assertIn("instruction:", yaml_config)
                self.assertIn("metadata:", yaml_config)
                self.assertIn(f"type: 'PROMPT'", yaml_config)


class TestPromptConfigIntegration(unittest.TestCase):
    """Prompt configuration integration tests."""

    def test_generated_config_format(self):
        """Test whether the generated configuration format meets PromptConfiger requirements."""
        yaml_config = generate_prompt_config(
            task_description="Integration test agent",
            agent_type="react",
            version_name="integration_test.cn"
        )

        # Check required YAML structure
        lines = yaml_config.strip().split('\n')

        # Check if required fields are included
        config_dict = {}
        current_key = None
        current_value = []

        for line in lines:
            if line.startswith('  ') or line.startswith('\t'):
                # This is part of a multi-line value
                current_value.append(line)
            elif ':' in line and not line.strip().startswith('#'):
                # New key-value pair
                if current_key:
                    config_dict[current_key] = '\n'.join(current_value)
                key_part = line.split(':', 1)[0].strip()
                current_key = key_part
                current_value = [line]
            else:
                current_value.append(line)

        if current_key:
            config_dict[current_key] = '\n'.join(current_value)

        # Verify required fields exist
        self.assertIn('introduction', config_dict)
        self.assertIn('target', config_dict)
        self.assertIn('instruction', config_dict)
        self.assertIn('metadata', config_dict)


if __name__ == '__main__':
    unittest.main(verbosity=2)
