# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: prompt_generator_demo.py
"""Prompt Generator Demo.

This demo script shows how to use the prompt generator to create different types of agent prompts.
Suitable for learning and understanding how to use the prompt generator.
"""
import sys
from pathlib import Path

# Add project root directory to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.third_party_examples.apps.prompt_generator_app.prompt_generator_helper import (
    PromptTemplateHelper,
    generate_prompt_config
)


def demo_prompt_generation():
    """Demo prompt generation functionality."""
    print("Prompt Generator Demo")
    print("=" * 50)

    # Demo 1: ReAct Agent Prompt
    demo_react_agent_prompt()

    # Demo 2: RAG Agent Prompt
    demo_rag_agent_prompt()

    # Demo 3: Custom Scenario
    demo_custom_scenario()

    # Demo 4: Supported Agent Types
    demo_supported_types()


def demo_react_agent_prompt():
    """Demo ReAct agent prompt generation."""
    print("\nDemo 1: ReAct Agent Prompt Generation")
    print("-" * 40)

    task_description = "Intelligent customer service assistant for e-commerce platform"
    scenario = "online shopping support"

    try:
        config = generate_prompt_config(
            task_description=task_description,
            agent_type="react",
            scenario=scenario,
            output_file=None
        )

        print(f"Successfully generated ReAct agent prompt")
        print(f"Task: {task_description}")
        print(f"Scenario: {scenario}")
        print(f"Agent Type: react")

        # Check if config is string (YAML) or dict
        if isinstance(config, str):
            print(f"Generated YAML configuration")
            print(f"Preview:\n{config[:200]}...")
        else:
            print(f"Generated sections: {list(config.keys())}")
            # Display introduction preview
            if 'introduction' in config:
                intro_preview = config['introduction'][:100] + "..." if len(config['introduction']) > 100 else config['introduction']
                print(f"Introduction Preview: {intro_preview}")

    except Exception as e:
        print(f"Error generating ReAct prompt: {str(e)}")


def demo_rag_agent_prompt():
    """Demo RAG agent prompt generation."""
    print("\nDemo 2: RAG Agent Prompt Generation")
    print("-" * 40)

    task_description = "Medical consultation expert for online healthcare platform"
    scenario = "medical advice and diagnosis support"

    try:
        config = generate_prompt_config(
            task_description=task_description,
            agent_type="rag",
            scenario=scenario,
            output_file=None
        )

        print(f"Successfully generated RAG agent prompt")
        print(f"Task: {task_description}")
        print(f"Scenario: {scenario}")
        print(f"Agent Type: rag")

        # Check if config is string (YAML) or dict
        if isinstance(config, str):
            print(f"Generated YAML configuration")
            print(f"Preview:\n{config[:200]}...")
        else:
            print(f"Generated sections: {list(config.keys())}")
            # Display target preview
            if 'target' in config:
                target_preview = config['target'][:100] + "..." if len(config['target']) > 100 else config['target']
                print(f"Target Preview: {target_preview}")

    except Exception as e:
        print(f"Error generating RAG prompt: {str(e)}")


def demo_custom_scenario():
    """Demo custom scenario prompt generation."""
    print("\nDemo 3: Custom Scenario Prompt Generation")
    print("-" * 40)

    task_description = "Financial advisor for investment portfolio management"
    scenario = "wealth management and investment consultation"

    try:
        config = generate_prompt_config(
            task_description=task_description,
            agent_type="planning",
            scenario=scenario,
            output_file=None
        )

        print(f"Successfully generated Planning agent prompt")
        print(f"Task: {task_description}")
        print(f"Scenario: {scenario}")
        print(f"Agent Type: planning")

        # Check if config is string (YAML) or dict
        if isinstance(config, str):
            print(f"Generated YAML configuration")
            print(f"Preview:\n{config[:200]}...")
        else:
            print(f"Generated sections: {list(config.keys())}")
            # Display instruction preview
            if 'instruction' in config:
                instruction_preview = config['instruction'][:150] + "..." if len(config['instruction']) > 150 else config['instruction']
                print(f"Instruction Preview: {instruction_preview}")

    except Exception as e:
        print(f"Error generating Planning prompt: {str(e)}")


def demo_supported_types():
    """Demo supported agent types listing."""
    print("\nDemo 4: Supported Agent Types")
    print("-" * 40)

    try:
        supported_types = list(PromptTemplateHelper.AGENT_TEMPLATES.keys())

        print(f"Available agent types ({len(supported_types)}):")
        for i, agent_type in enumerate(supported_types, 1):
            template_info = PromptTemplateHelper.AGENT_TEMPLATES[agent_type]
            name = template_info.get('name', agent_type)
            print(f"  {i}. {agent_type} - {name}")

    except Exception as e:
        print(f"Error listing agent types: {str(e)}")


def main():
    """Main function to run all demos."""
    try:
        demo_prompt_generation()
        print("\nDemo completed successfully!")
        print("\nNext steps:")
        print("• Try generating prompts with different agent types")
        print("• Experiment with various scenarios and tasks")
        print("• Use the CLI tool: python scripts/generate_prompt.py")

    except Exception as e:
        print(f"\nDemo failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
