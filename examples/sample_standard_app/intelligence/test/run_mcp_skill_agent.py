# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/27
# @FileName: run_mcp_skill_agent.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str, session_id=None):
    """Run the MCP skill agent with a question."""
    instance: Agent = AgentManager().get_instance_obj('mcp_skill_agent')
    output_object = instance.run(input=question, session_id=session_id)
    res_info = f"\nMCP Skill Agent result:\n"
    res_info += str(output_object.get_data('output'))
    print(res_info)


if __name__ == '__main__':
    chat(
        question="帮我用 Python 写一个集成 GitHub API 的 MCP server",
        session_id="mcp-test-01"
    )
