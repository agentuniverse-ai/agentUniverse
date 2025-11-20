import os
import unittest
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.fred_api_tool import FredApiTool, SearchMode  # 替换为实际模块路径

class FredApiToolTest(unittest.TestCase):
    """
    Fred API工具单元测试类
    """

    def setUp(self) -> None:
        """初始化测试环境"""
        # 从环境变量获取API密钥（测试时需要预先配置）
        api_key = os.getenv("FRED_API_KEY", "4de038fe793a491ffbebbd0ee21c3e05")
        print(api_key, ":api_key")
        self.tool = FredApiTool(api_key=api_key)

    def test_search_datasets(self) -> None:
        """测试宏观经济数据集搜索功能"""
        tool_input = ToolInput({
            'input': 'unemployment',  # 测试关键词
            'mode': SearchMode.SEARCH.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue("datasets for 'unemployment'" in result, "未找到数据集标题")
        self.assertTrue("ID:" in result, "未找到数据集ID字段")
        self.assertTrue("Frequency:" in result, "未找到频率字段")
        self.assertTrue("Description:" in result, "未找到描述字段")

    def test_get_series_data(self) -> None:
        """测试时间序列数据获取功能（使用美国失业率基准数据）"""
        tool_input = ToolInput({
            'input': 'UNRATE',  # 美国失业率标准代码
            'mode': SearchMode.DETAIL.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue("Latest data for UNRATE" in result, "未找到数据标题")
        self.assertTrue(":" in result, "未找到数据分隔符")
        self.assertTrue("20" in result or "NA" in result, "数据格式异常")

    def test_invalid_mode(self) -> None:
        """测试无效模式参数的异常处理"""
        tool_input = ToolInput({
            'input': 'test',
            'mode': 'invalid_mode'
        })
        with self.assertRaises(ValueError, msg="未正确抛出无效模式异常"):
            self.tool.execute(tool_input)

    def test_invalid_series_id(self) -> None:
        """测试无效序列ID的错误处理"""
        tool_input = ToolInput({
            'input': 'INVALID_SERIES_ID',
            'mode': SearchMode.DETAIL.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue("No data found" in result or "Error" in result, 
                      "无效序列ID未正确处理")

    def test_query_length_limit(self) -> None:
        """测试超长查询字符串的截断处理"""
        long_query = 'A' * 400  # 超过默认300字符限制
        tool_input = ToolInput({
            'input': long_query,
            'mode': SearchMode.SEARCH.value
        })
        processed_query = self.tool._process_query(long_query)
        self.assertLessEqual(len(processed_query), 300, 
                           "查询字符串长度限制失效")
        self.assertTrue(processed_query.endswith('A'), 
                      "查询字符串截断处理异常")

if __name__ == '__main__':
    unittest.main()
