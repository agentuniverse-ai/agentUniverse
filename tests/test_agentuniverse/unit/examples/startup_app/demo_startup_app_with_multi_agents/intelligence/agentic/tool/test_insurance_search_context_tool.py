# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the insurance search context tool example.

The tool performs an in-memory mocked knowledge search through ``MockAPI`` and
assembles the retrieved records into a natural-language context string.  These
tests cover the mock request/response helpers and the deterministic context
assembly logic of ``SearchContextTool.execute`` (no network involved).
"""

import unittest

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.agentic.tool.insurance_search_context_tool import (
    MockAPI,
    MockResponse,
    SearchContextTool,
)


class MockResponseTest(unittest.TestCase):
    def test_json_returns_payload(self):
        payload = {"result": {"recallResultTuples": []}}
        response = MockResponse(payload)
        self.assertEqual(response.json(), payload)


class MockAPITest(unittest.TestCase):
    def test_post_returns_mock_response_with_recall_tuples(self):
        response = MockAPI().post("http://www.xxxx.com/query_knowledge", headers={}, data="{}")
        result = response.json()["result"]
        self.assertEqual(len(result["recallResultTuples"]), 3)
        for recall in result["recallResultTuples"]:
            self.assertIn("knowledgeTitle", recall)
            self.assertIn("content", recall)


class SearchContextToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = SearchContextTool()

    def test_execute_with_default_top_k_returns_question_and_two_hits(self):
        context = self.tool.execute("什么是保险产品A的升级规则?")
        self.assertIn("提出的问题是:什么是保险产品A的升级规则?", context)
        self.assertEqual(context.count("knowledgeContent:"), 2)

    def test_execute_with_zero_top_k_returns_header_only(self):
        context = self.tool.execute("什么是保险产品A的升级规则?", top_k=0)
        self.assertNotIn("knowledgeTitle", context)
        self.assertIn("这个问题检索到的答案相关内容是", context)

    def test_execute_with_large_top_k_returns_all_hits(self):
        context = self.tool.execute("什么是保险产品A的升级规则?", top_k=10)
        self.assertEqual(context.count("knowledgeContent:"), 3)
        self.assertIn("保险产品A在保障期间暂不支持升级", context)

    def test_execute_keeps_recall_content_order(self):
        context = self.tool.execute("什么是保险产品A的升级规则?", top_k=10)
        first = context.find("保险产品A在保障期间暂不支持升级")
        second = context.find("保险产品A是免费体验版")
        third = context.find("保险产品A保障期限12个月")
        self.assertTrue(first < second < third)


if __name__ == "__main__":
    unittest.main()
