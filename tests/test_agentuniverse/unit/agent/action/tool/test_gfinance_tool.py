import unittest
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.google_finance_tool import GoogleFinanceTool, SearchMode  

class GoogleFinanceToolTest(unittest.TestCase):
    """
    Google Finance工具单元测试类
    """

    def setUp(self) -> None:
        """初始化测试环境"""
        self.tool = GoogleFinanceTool()

    def test_real_time_quote(self) -> None:
        """测试实时报价查询功能"""
        tool_input = ToolInput({
            'input': 'AAPL',  # 使用苹果公司股票代码进行测试
            'mode': SearchMode.SEARCH.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue("实时报价" in result, "未找到报价标题")
        self.assertTrue("价格" in result, "未找到价格字段")
        self.assertTrue("变动" in result, "未找到变动字段")
        self.assertTrue("$" in result, "价格格式异常")
        self.assertTrue("%" in result, "变动百分比格式异常")

    def test_company_info(self) -> None:
        """测试公司信息查询功能"""
        tool_input = ToolInput({
            'input': 'MSFT',  # 使用微软股票代码进行测试
            'mode': SearchMode.DETAIL.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue("公司信息" in result, "未找到公司信息标题")
        self.assertTrue("交易所" in result, "未找到交易所字段")
        self.assertTrue("行业" in result, "未找到行业字段")
        self.assertTrue("市值" in result, "未找到市值字段")
        self.assertTrue("52周范围" in result, "未找到52周范围字段")

    def test_invalid_mode(self) -> None:
        """测试无效模式参数的异常处理"""
        tool_input = ToolInput({
            'input': 'test',
            'mode': 'invalid_mode'
        })
        with self.assertRaises(ValueError, msg="未正确抛出无效模式异常"):
            self.tool.execute(tool_input)

    def test_invalid_stock_code(self) -> None:
        """测试无效股票代码的处理"""
        tool_input = ToolInput({
            'input': 'INVALID_CODE',
            'mode': SearchMode.SEARCH.value
        })
        result = self.tool.execute(tool_input)
        self.assertTrue("No data found" in result or "失败" in result, 
                      "无效股票代码未正确处理")

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
