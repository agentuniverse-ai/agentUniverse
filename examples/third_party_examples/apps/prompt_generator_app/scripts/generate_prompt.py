# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: generate_prompt.py

"""agentUniverse Prompt Generator - Command Line Tool.

A comprehensive command-line interface for generating and optimizing prompt
configurations for agentUniverse agents. Supports multiple agent types and
provides flexible configuration options.
"""

import argparse
import sys
from pathlib import Path

# Add project root directory to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from examples.third_party_examples.apps.prompt_generator_app.prompt_generator_helper import (
    PromptTemplateHelper,
    generate_prompt_config
)


def main():
    """Main function for the command line interface."""
    parser = argparse.ArgumentParser(
        description="agentUniverse Prompt Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
    # Generate ReAct agent prompt
    python scripts/generate_prompt.py "Customer service assistant" --type react --scenario "e-commerce"

    # Generate RAG agent prompt and save to file
    python scripts/generate_prompt.py "Insurance consultant" --type rag --output insurance.yaml

    # Generate planning agent prompt
    python scripts/generate_prompt.py "Project management assistant" --type planning --requirements "Must follow agile development process"

  # View supported agent types
  python scripts/generate_prompt.py --list-types
        """
    )

    # Positional arguments
    parser.add_argument('task', nargs='?', help='Task description')

    # Optional arguments
    parser.add_argument('--type', '-t',
                       choices=list(PromptTemplateHelper.get_supported_agent_types().keys()),
                       default='react', help='Agent type (default: react)')
    parser.add_argument('--scenario', '-s', help='Application scenario description')
    parser.add_argument('--requirements', '-r', help='Specific requirements description')
    parser.add_argument('--version', '-v', help='Version name')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--list-types', action='store_true', help='List supported agent types')

    args = parser.parse_args()

    # List agent types
    if args.list_types:
        print("Supported agent types:")
        print("-" * 50)
        for agent_type, name in PromptTemplateHelper.get_supported_agent_types().items():
            print(f"  {agent_type:12} - {name}")
        return

    # Check required parameters
    if not args.task:
        print("Error: Task description is required")
        parser.print_help()
        sys.exit(1)

    print(f"Generating {args.type} agent prompt...")
    print(f"   Task: {args.task}")
    if args.scenario:
        print(f"   Scenario: {args.scenario}")
    if args.requirements:
        print(f"   Requirements: {args.requirements}")

    try:
        # Generate prompt configuration
        yaml_config = generate_prompt_config(
            task_description=args.task,
            agent_type=args.type,
            scenario=args.scenario,
            specific_requirements=args.requirements,
            version_name=args.version,
            output_file=args.output
        )

        # Print to console if no output file specified
        if not args.output:
            print("\n" + "="*60)
            print("Generated Prompt Configuration:")
            print("="*60)
            print(yaml_config)

            # Ask whether to save
            save = input("\nSave to file? (y/N): ").strip().lower()
            if save in ['y', 'yes']:
                filename = f"{args.type}_prompt.yaml"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(yaml_config)
                print(f"Saved to: {filename}")

        print("\nPrompt generation completed successfully!")
        print("\nUsage instructions:")
        print("1. Place the generated YAML file in intelligence/agentic/prompt/ directory")
        print("2. Reference it in agent configuration via prompt_version")
        print("3. Adjust and optimize prompt content as needed")

    except Exception as e:
        print(f"Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
