#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Simple example demonstrating IS Agent usage

This is a minimal example showing how to use the IS pattern for supervised task execution.

@Time    : 2025/12/01
@Author  : kaichuan
"""

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


def simple_example():
    """Run a simple IS agent example."""

    # Step 1: Start AgentUniverse
    AgentUniverse().start(config_path='config/config.toml')

    # Step 2: Get IS agent instance
    agent: Agent = AgentManager().get_instance_obj('demo_is_agent')

    # Step 3: Run the agent with your input
    result = agent.run(
        input='编写一个Python函数，实现快速排序算法，要求包含完整的文档和注释',
        checkpoint_count=3,
        max_corrections=2
    )

    # Step 4: Get the output
    result_dict = result.to_dict()
    output = result_dict.get('output', '')
    print("\n=== Final Output ===")
    print(output)

    # Step 5: View full execution details (optional)
    full_output = result_dict.get('full_output', '')
    print("\n=== Full Execution Details ===")
    print(full_output)


if __name__ == '__main__':
    simple_example()
