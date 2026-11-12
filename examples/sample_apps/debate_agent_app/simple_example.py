#!/usr/bin/env python3

"""
Simple example demonstrating Debate Agent usage

This is a minimal example showing how to use the Debate pattern for
consensus-driven problem solving through proposal, critique and judgment.

@Time    : 2026/10/18
@Author  : lljjcc426
"""

# Chinese example input intentionally uses full-width punctuation.
# ruff: noqa: RUF001

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


def simple_example():
    """Run a simple Debate agent example."""

    # Step 1: Start AgentUniverse
    AgentUniverse().start(config_path="config/config.toml")

    # Step 2: Get Debate agent instance
    agent: Agent = AgentManager().get_instance_obj("demo_debate_agent")

    # Step 3: Run the agent with your input
    result = agent.run(
        input="设计一个高并发场景下的短链接生成服务，要求给出核心架构、关键数据结构与容错方案",
        debate_rounds=3,
        consensus_threshold=80,
    )

    # Step 4: Get the output
    result_dict = result.to_dict()
    output = result_dict.get("output", "")
    print("\n=== Final Output ===")
    print(output)

    # Step 5: View full execution details (optional)
    full_output = result_dict.get("full_output", "")
    print("\n=== Full Execution Details ===")
    print(full_output)


if __name__ == "__main__":
    simple_example()
