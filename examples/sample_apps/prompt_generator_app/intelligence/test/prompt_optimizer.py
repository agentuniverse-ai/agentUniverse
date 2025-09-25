# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: prompt_optimizer_demo.py

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agentuniverse.prompt.prompt_generator_helper import optimize_existing_prompt


def demo_basic_prompt_optimization():
    """Demonstrate basic prompt optimization functionality."""
    print("Basic Prompt Optimization Demo")
    print("-" * 50)

    basic_prompts = [
        {
            "original": "You are an AI assistant.",
            "goal": "Improve professionalism and detail",
            "type": "react"
        },
        {
            "original": "Help me analyze data.",
            "goal": "Enhance analysis structure and depth",
            "type": "rag"
        },
        {
            "original": "Write an article.",
            "goal": "Provide clearer writing guidance framework",
            "type": "expressing"
        }
    ]

    for i, example in enumerate(basic_prompts, 1):
        print(f"\nExample {i}:")
        print(f"Original Prompt: {example['original']}")
        print(f"Optimization Goal: {example['goal']}")
        print(f"Agent Type: {example['type']}")

        try:
            optimized = optimize_existing_prompt(
                existing_prompt_text=example['original'],
                optimization_goal=example['goal'],
                agent_type=example['type']
            )
            print(f"Optimization Result:")
            print(f"  Role Definition: {optimized.introduction}")
            print(f"  Target Setting: {optimized.target}")
            print(f"  Instruction Content: {optimized.instruction[:100]}...")
            print()
        except Exception as e:
            print(f"Optimization Failed: {e}\n")


def demo_advanced_prompt_optimization():
    """Demonstrate advanced prompt optimization functionality."""
    print("Advanced Prompt Optimization Demo")
    print("-" * 50)

    advanced_examples = [
        {
            "original": """You are a customer service representative. Answer customer questions. Be polite.""",
            "goal": "Enhance professional service capabilities and improve problem-solving efficiency",
            "scenario": "E-commerce platform",
            "type": "react"
        },
        {
            "original": """Answer questions based on documentation. Be accurate.""",
            "goal": "Improve answer quality and enhance citation standards",
            "scenario": "Technical documentation query",
            "type": "rag"
        }
    ]

    for i, example in enumerate(advanced_examples, 1):
        print(f"\nAdvanced Example {i}:")
        print(f"Original Prompt: {example['original']}")
        print(f"Optimization Goal: {example['goal']}")
        print(f"Application Scenario: {example['scenario']}")

        try:
            optimized = optimize_existing_prompt(
                existing_prompt_text=example['original'],
                optimization_goal=example['goal'],
                agent_type=example['type'],
                scenario=example['scenario']
            )
            print(f"Optimization Result:")
            print(f"  Role Definition: {optimized.introduction}")
            print(f"  Target Setting: {optimized.target}")
            print(f"  Instruction Framework: {optimized.instruction[:150]}...")
            print()
        except Exception as e:
            print(f"Optimization Failed: {e}\n")


def demo_yaml_prompt_optimization():
    """Demonstrate YAML format prompt optimization."""
    print("YAML Format Prompt Optimization Demo")
    print("-" * 50)

    yaml_prompt = """
introduction: You are an assistant
target: Help users
instruction: |
  Answer questions
metadata:
  type: 'PROMPT'
  version: 'v1'
"""

    print("Original YAML Prompt:")
    print(yaml_prompt)

    try:
        optimized = optimize_existing_prompt(
            existing_prompt_text=yaml_prompt,
            optimization_goal="Improve prompt structure and enhance instruction clarity",
            agent_type="react"
        )

        print("Optimized Content:")
        print(f"Role Definition: {optimized.introduction}")
        print(f"Target Setting: {optimized.target}")
        print(f"Instruction Content: {optimized.instruction[:200]}...")

    except Exception as e:
        print(f"Optimization Failed: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("agentUniverse Prompt Optimizer Demonstration")
    print("=" * 60)

    demo_basic_prompt_optimization()
    print("\n" + "=" * 60)
    demo_advanced_prompt_optimization()
    print("\n" + "=" * 60)
    demo_yaml_prompt_optimization()

    print("\nPrompt optimization demonstration completed successfully!")
