#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Simple example demonstrating GRR Agent usage

This is a minimal example showing how to use the GRR pattern for content generation.

@Time    : 2025/12/01
@Author  : Claude Code
"""

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


def simple_example():
    """Run a simple GRR agent example."""

    # Step 1: Start AgentUniverse
    AgentUniverse().start(config_path='config/config.toml')

    # Step 2: Get GRR agent instance
    agent: Agent = AgentManager().get_instance_obj('demo_grr_agent')

    # Step 3: Run the agent with your input
    result = agent.run(input='写一篇关于人工智能的短文，约150字')

    # Step 4: Get the output
    output = result.get('output', '')
    print(output)


if __name__ == '__main__':
    simple_example()
