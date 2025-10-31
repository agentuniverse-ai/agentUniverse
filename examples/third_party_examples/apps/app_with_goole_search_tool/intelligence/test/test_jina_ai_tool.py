import unittest
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.agentuniverse import AgentUniverse

import os

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 设置工作目录为脚本所在目录
os.chdir(script_dir)

AgentUniverse().start(config_path='../../config/config.toml')


class JinaAIToolTest(unittest.TestCase):
    """
    Test cases for the jina ai tool
    """
    api_key = "jina_xxxxxxxxxxx"
    url = "https://github.com/antgroup/agentUniverse"

    def test_jina_ai_tool(self):
        jina_ai_tool = ToolManager().get_instance_obj("jina_ai_tool")

        print("\n-------------read url---------------")
        print(jina_ai_tool.run(input=self.url, max_content_length=5000))

        '''
        # search和check_fact模式需要填写api_key

        print("\n-------------search---------------")
        print(jina_ai_tool.run(input=f"When was Jina AI founded?",api_key=self.api_key,mode="search"))
        
        print("\n-------------check fact---------------")
        print(jina_ai_tool.run(input=f"In 2012, President Barack Hussein Obama repealed the Smith-Mundt act, which had been in place in 1948. The law prevented the government from putting its propaganda on TV and Radio.",api_key=self.api_key,mode="check_fact"))
        '''


if __name__ == '__main__':
    unittest.main()
