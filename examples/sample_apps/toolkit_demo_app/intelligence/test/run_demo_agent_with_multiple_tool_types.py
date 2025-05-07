# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager


AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)
file_path = "./test_doc.docx"
absolute_path = os.path.abspath(file_path)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('demo_agent_with_multiple_tool_types')
    instance.run(input=question)


if __name__ == '__main__':
    # 在运行该案例前，你可以通过根目录下的uv_install.sh的脚本来安装案例中用到的MCP工具和运行环境。
    # Before running this case, you can install the MCP tool and runtime
    # environment used in the case by executing the uv_install.sh script
    # located in the root directory.

    chat(f"帮我查一查五一假期适合游玩的城市或景点（不少于10个），分别给出对应城市或景点的详细介绍（100字左右）、推荐理由、参考资料地址，"
         f"请排除与旅行无关的信息并将上述内容写成报告，并放置{absolute_path}路径下。")
