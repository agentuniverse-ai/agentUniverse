# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_google_search_tool.py

import unittest
import os
import sys

# 添加项目根目录到Python路径
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.agentuniverse import AgentUniverse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

AgentUniverse().start(config_path='../../config/config.toml')


class GoogleSearchToolTest(unittest.TestCase):
    """Google搜索工具测试类"""

    def setUp(self):
        """测试前准备"""
        self.search_tool = ToolManager().get_instance_obj("google_search_tool")
        self.scholar_tool = ToolManager().get_instance_obj("google_scholar_search_tool")

    def test_google_search_tool_creation(self):
        """测试Google搜索工具创建"""
        self.assertIsNotNone(self.search_tool)
        self.assertEqual(self.search_tool.name, 'google_search_tool')

    def test_google_scholar_tool_creation(self):
        """测试Google学术搜索工具创建"""
        self.assertIsNotNone(self.scholar_tool)
        self.assertEqual(self.scholar_tool.name, 'google_scholar_search_tool')

    def test_google_search_mock_mode(self):
        """测试Google搜索工具模拟模式"""
        # 不设置API密钥，测试模拟模式
        result = self.search_tool.execute(query="测试查询")
        self.assertIsInstance(result, str)
        expected_texts = ["Google 搜索模拟结果", "Google Search 搜索结果"]
        self.assertTrue(any(text in result for text in expected_texts))
        self.assertIn("测试查询", result)

    def test_google_search_with_parameters(self):
        """测试Google搜索工具参数"""
        result = self.search_tool.execute(
            query="人工智能",
            search_type="news",
            k=5,
            gl="cn",
            hl="zh"
        )
        self.assertIsInstance(result, str)
        self.assertIn("人工智能", result)

    def test_google_scholar_search_mock_mode(self):
        """测试Google学术搜索工具模拟模式"""
        result = self.scholar_tool.execute(query="机器学习")
        self.assertIsInstance(result, str)
        expected_texts = ["Google学术搜索模拟结果", "Google学术搜索结果"]
        self.assertTrue(any(text in result for text in expected_texts))
        self.assertIn("机器学习", result)

    def test_google_scholar_search_with_filters(self):
        """测试Google学术搜索工具筛选功能"""
        result = self.scholar_tool.execute(
            query="深度学习",
            year="2020..2024",
            author="Geoffrey Hinton",
            journal="Nature"
        )
        self.assertIsInstance(result, str)
        self.assertIn("深度学习", result)

    def test_scholar_query_building(self):
        """测试学术搜索查询构建"""
        query = self.scholar_tool._build_scholar_query(
            "神经网络",
            year="2020..2024",
            author="Yann LeCun",
            journal="ICML"
        )
        self.assertIn("site:scholar.google.com", query)
        self.assertIn("神经网络", query)
        self.assertIn("2020..2024", query)
        self.assertIn("Yann LeCun", query)
        self.assertIn("ICML", query)

    def test_search_result_formatting(self):
        """测试搜索结果格式化"""
        mock_result = '[{"title": "测试标题", "link": "https://example.com", "snippet": "测试描述"}]'
        formatted = self.search_tool._format_search_result(mock_result, "测试查询", "search")
        self.assertIn("Google Search 搜索结果", formatted)
        self.assertIn("测试标题", formatted)
        self.assertIn("https://example.com", formatted)

    def test_scholar_result_formatting(self):
        """测试学术搜索结果格式化"""
        mock_result = '[{"title": "学术论文", "link": "https://scholar.google.com", "snippet": "论文摘要"}]'
        formatted = self.scholar_tool._format_scholar_result(mock_result, "机器学习", "site:scholar.google.com 机器学习")
        self.assertIn("Google学术搜索结果", formatted)
        self.assertIn("学术论文", formatted)
        self.assertIn("https://scholar.google.com", formatted)

    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效的JSON结果
        invalid_result = "invalid json result"
        formatted = self.search_tool._format_search_result(invalid_result, "测试", "search")
        self.assertIn("Google Search 搜索结果", formatted)
        self.assertIn("invalid json result", formatted)

    def test_tool_input_keys(self):
        """测试工具输入键"""
        self.assertEqual(self.search_tool.input_keys, ['input'])
        self.assertEqual(self.scholar_tool.input_keys, ['input'])

    def test_tool_type(self):
        """测试工具类型"""
        self.assertEqual(self.search_tool.tool_type.value, 'func')
        self.assertEqual(self.scholar_tool.tool_type.value, 'func')


if __name__ == '__main__':
    unittest.main()
