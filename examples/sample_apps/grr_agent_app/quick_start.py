#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Quick start script for GRR Agent App

This script demonstrates how to use the GRR (Generate-Review-Rewrite) pattern
for content generation tasks.

@Time    : 2025/12/01
@Author  : kaichuan
"""

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


def main():
    """Main function to demonstrate GRR agent usage."""

    # Start AgentUniverse
    print("🚀 Starting AgentUniverse...")
    AgentUniverse().start(config_path='config/config.toml')
    print("✅ AgentUniverse started successfully!\n")

    # Get GRR agent instance
    print("📦 Loading GRR agent...")
    grr_agent: Agent = AgentManager().get_instance_obj('demo_grr_agent')
    print("✅ GRR agent loaded successfully!\n")

    # Example 1: AI in Healthcare
    print("=" * 60)
    print("Example 1: Writing about AI in Healthcare")
    print("=" * 60)
    result1 = grr_agent.run(input='写一篇关于人工智能在医疗领域应用的短文，约200字')
    print("\n📝 Generated Content:")
    print(result1.get('output', ''))
    print("\n")

    # Example 2: Product Introduction
    print("=" * 60)
    print("Example 2: Product Introduction")
    print("=" * 60)
    result2 = grr_agent.run(input='为一家智能家居公司撰写产品介绍，突出科技感和便利性，约150字')
    print("\n📝 Generated Content:")
    print(result2.get('output', ''))
    print("\n")

    # Example 3: Creative Story
    print("=" * 60)
    print("Example 3: Creative Story Opening")
    print("=" * 60)
    result3 = grr_agent.run(input='写一个关于时间旅行者的故事开头，约100字')
    print("\n📝 Generated Content:")
    print(result3.get('output', ''))
    print("\n")

    print("=" * 60)
    print("🎉 All examples completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("\nPlease make sure:")
        print("1. You have configured your API keys in config/custom_key.toml")
        print("2. All dependencies are installed")
        print("3. The config path is correct")
        raise
