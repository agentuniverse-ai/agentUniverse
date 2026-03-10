# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/27
# @FileName: run_art_skill_agent.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str, session_id=None):
    """Run the art skill agent with a question."""
    instance: Agent = AgentManager().get_instance_obj('art_skill_agent')
    output_object = instance.run(input=question, session_id=session_id)
    res_info = f"\nArt Skill Agent result:\n"
    res_info += str(output_object.get_data('output'))
    print(res_info)


if __name__ == '__main__':
    chat(
        question="帮我创作一个以'星空漩涡'为主题的生成艺术作品",
        session_id="art-test-01"
    )
