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
    instance: Agent = AgentManager().get_instance_obj('demo_agent_with_mcp_toolkit')
    instance.run(input=question)


if __name__ == '__main__':
    # 在运行该案例前，你可以通过根目录下的uv_install.sh的脚本来安装案例中用到的MCP工具和运行环境。
    # Before running this case, you can install the MCP tool and runtime
    # environment used in the case by executing the uv_install.sh script
    # located in the root directory.
    chat(f"查看{absolute_path}中的内容，并找到用户goldenhawk15的密码，然后也在同样的路径下创建一个新的docx文件把密码写进去")
