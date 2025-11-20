import os
import unittest
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.fred_api_tool import FredApiTool, SearchMode  # 替换为实际模块路径



from unittest.mock import patch, MagicMock


# # 初始化工具
# tool = FredApiTool(api_key="your_api_key")

# # 高级搜索
# tool_input = ToolInput({
#     'input': 'GDP',
#     'mode': SearchMode.SEARCH.value,
#     'params': {
#         'limit': 5,
#         'sort_order': 'desc',
#         'filter_variable': 'frequency',
#         'filter_value': 'Annual'

#     }
# })
# print("高级搜索")
# print(tool.execute(tool_input))



# # 获取带时间范围的数据
# tool_input = ToolInput({
#     'input': 'SP500',
#     'mode': SearchMode.DETAIL.value,
#     'params': {
#         'observation_start': '2024-04-01',
#         'observation_end': '2024-04-05',
#         # 'realtime_start': '2014-04-01',
#         # 'realtime_end': '2014-04-07',
#         # 'limit': 10
#     }
# })
# print("获取带时间范围的数据")
# print(tool.execute(tool_input))

import os
import unittest
from unittest.mock import patch, MagicMock
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.fred_api_tool import FredApiTool, SearchMode  # 替换为实际模块路径

class FredApiToolTest(unittest.TestCase):
    """Fred API工具单元测试类"""

    @patch('agentuniverse.agent.action.tool.common_tool.fred_api_tool.FredApiTool')
    def setUp(self, mock_fred):
        """初始化测试环境"""
        # 创建mock fred客户端
        self.mock_fred_instance = mock_fred.return_value
        self.tool = FredApiTool(api_key="your_api_key") ##fill up your api key

        # 设置默认mock返回值
        self.mock_fred_instance.search.return_value = MagicMock(empty=True)
        self.mock_fred_instance.get_series.return_value = MagicMock(empty=True)
        self.mock_fred_instance.get_series_info.return_value = None




    def test_missing_api_key(self):
        """测试未提供API密钥时的初始化失败"""
        with self.assertRaises(ValueError):
            FredApiTool(api_key=None)

    def test_search_datasets_success(self):
        """测试宏观经济数据集搜索功能成功场景"""
        # 模拟搜索结果
        mock_result = MagicMock()
        mock_result.empty = False
        mock_result.iterrows.return_value = [(0, {
            'title': 'GDP',
            'id': 'GDP',
            'frequency': 'Monthly',
            'units': 'Index',
            'notes': 'Test description'
        })]
        self.mock_fred_instance.search.return_value = mock_result

        tool_input = ToolInput({
            'input': 'GDP',
            'mode': SearchMode.SEARCH.value,
            'params': {
                'limit': 5,
                'filter_variable': 'frequency'
            }
        })
        result = self.tool.execute(tool_input)
        print('sucess result1',result)
        self.assertIn("GDP", result)

    def test_get_series_data_success(self):
        """测试时间序列数据获取功能成功场景"""
        # 模拟时间序列数据
        mock_data = MagicMock()
        mock_data.empty = False
        mock_data.items.return_value = [('2025-01-01')]
        self.mock_fred_instance.get_series.return_value = mock_data

        tool_input = ToolInput({
            'input': 'SP500',
            'mode': SearchMode.DETAIL.value,
            'params': {
                'observation_start': '2025-01-01',
                'observation_end': '2025-12-31'
            }
        })
        result = self.tool.execute(tool_input)
        
        print('sucess result2',result)
        self.assertIn("SP500", result)
        self.assertIn("2025-01-01", result)


    def test_invalid_mode(self):
        """测试无效模式参数的异常处理"""
        tool_input = ToolInput({
            'input': 'test',
            'mode': 'invalid_mode'
        })
        with self.assertRaises(ValueError):
            self.tool.execute(tool_input)

    def test_invalid_series_id(self):
        """测试无效序列ID的错误处理"""
        tool_input = ToolInput({
            'input': 'INVALID_ID',
            'mode': SearchMode.DETAIL.value
        })
        result = self.tool.execute(tool_input)
        # print('无效序列IDresult',result)
        self.assertIn("Invalid value", result)

    def test_query_length_limit(self):
        """测试超长查询字符串的截断处理"""
        long_query = 'A' * 400  # 超过默认300字符限制
        tool_input = ToolInput({
            'input': long_query,
            'mode': SearchMode.SEARCH.value
        })
        processed_query = self.tool._process_query(long_query)
        self.assertLessEqual(len(processed_query), 300)
        # print('processed_query',processed_query)
        self.assertTrue(processed_query.endswith('A'))

    def test_cache_initialization(self):
        """测试缓存机制初始化"""
        self.assertTrue(hasattr(self.tool, '_get_series_data'))
        self.assertTrue(hasattr(self.tool, '_search_datasets'))

    def test_error_handling_on_api_failure(self):
        """测试API调用失败时的错误处理"""
        # 模拟API调用抛出异常
        self.mock_fred_instance.search.side_effect = Exception("API Error")
        
        tool_input = ToolInput({
            'input': 'error_test',
            'mode': SearchMode.SEARCH.value
        })
        result = self.tool.execute(tool_input)
        # print('API调用失败result',result)
        self.assertIn("No datasets found", result)
        # self.assertIn("API Error", result)

    def test_missing_params_handling(self):
        """测试缺少参数时的默认行为"""
        tool_input = ToolInput({
            'input': 'test',
            'mode': SearchMode.SEARCH.value
        })
        result = self.tool.execute(tool_input)
        self.assertIn("datasets for 'test'", result)

    

if __name__ == '__main__':
    unittest.main()
