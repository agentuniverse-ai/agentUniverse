# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/8 11:41
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: run_demo_agent_with_mcp_tool.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('demo_agent_with_mcp_tool')
    instance.run(input=question)


if __name__ == '__main__':
    # 在运行该案例前，你可以通过根目录下的uv_install.sh的脚本来安装案例中用到的MCP工具和运行环境。
    # Before running this case, you can install the MCP tool and runtime
    # environment used in the case by executing the uv_install.sh script
    # located in the root directory.
    chat("帮我查一查2025年支付宝联动的游戏有哪些")
