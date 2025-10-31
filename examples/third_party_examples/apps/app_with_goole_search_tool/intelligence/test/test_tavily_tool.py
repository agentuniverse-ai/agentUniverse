import os
import unittest
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.util.env_util import get_from_env

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 设置工作目录为脚本所在目录
os.chdir(script_dir)

AgentUniverse().start(config_path='../../config/config.toml')

class TavilyToolTest(unittest.TestCase):
    """
    Tavily工具的测试用例
    """
    # 从环境变量获取API密钥，如果没有则使用占位符
    #api_key = get_from_env("TAVILY_API_KEY") or "your_tavily_api_key_here"
    api_key = "tvly-xxxxxxxxxxxxxxxxxx"
    # 测试查询
    test_query = "The latest developments of DeepSeek"
    test_url = "https://mp.weixin.qq.com/s/lK-lWeS0cyAobEof8CsQWQ"

    def test_tavily_tool(self):
        """测试Tavily工具的搜索模式和提取模式"""
        # 跳过测试如果没有有效的API密钥
        if self.api_key == "your_tavily_api_key_here":
            self.skipTest("未提供Tavily API密钥，跳过测试")
            
        tavily_tool = ToolManager().get_instance_obj("tavily_tool")
        
        print("\n-------------测试Tavily工具(搜索模式)---------------")
        result = tavily_tool.run(input=self.test_query, api_key=self.api_key, mode="search")
        print(f"搜索结果: {result}")
        
        # 验证搜索结果
        self.assertIn("results", result)
        if len(result["results"]) > 0:
            print(f"搜索结果数量: {len(result['results'])}")
            print(f"第一条结果标题: {result['results'][0]['title']}")
            print(f"第一条结果URL: {result['results'][0]['url']}")
        
        print("\n-------------测试Tavily工具(提取模式)---------------")
        result = tavily_tool.run(input=self.test_url, api_key=self.api_key, mode="extract", include_images=False)
        print(f"提取结果: {result}")
        
        # 验证提取结果
        self.assertIn("results", result)
        if len(result["results"]) > 0:
            print(f"成功提取URL数量: {len(result['results'])}")
            print(f"第一个URL: {result['results'][0]['url']}")
            print(f"提取内容前200字符: {result['results'][0]['raw_content'][:200]}...")
        
        if "failed_results" in result and len(result["failed_results"]) > 0:
            print(f"提取失败URL数量: {len(result['failed_results'])}")
            for failed in result["failed_results"]:
                print(f"失败URL: {failed['url']}, 错误: {failed['error']}")

if __name__ == '__main__':
    unittest.main()
