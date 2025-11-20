import os
import unittest
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.fred_api_tool import FredApiTool, SearchMode  # 替换为实际模块路径



from unittest.mock import patch, MagicMock
# FredApiTool(api_key="4de038fe793a491ffbebbd0ee21c3e05")

# 初始化工具
tool = FredApiTool(api_key="4de038fe793a491ffbebbd0ee21c3e05")

# 高级搜索
tool_input = ToolInput({
    'input': 'GDP',
    'mode': SearchMode.SEARCH.value,
    'params': {
        'limit': 5,
        'sort_order': 'desc',
        'filter_variable': 'frequency',
        'filter_value': 'Annual'

    }
})
print("高级搜索")
print(tool.execute(tool_input))



# 获取带时间范围的数据
tool_input = ToolInput({
    'input': 'SP500',
    'mode': SearchMode.DETAIL.value,
    'params': {
        'observation_start': '2024-04-01',
        'observation_end': '2024-04-05',
        # 'realtime_start': '2014-04-01',
        # 'realtime_end': '2014-04-07',
        # 'limit': 10
    }
})
print("获取带时间范围的数据")
print(tool.execute(tool_input))

