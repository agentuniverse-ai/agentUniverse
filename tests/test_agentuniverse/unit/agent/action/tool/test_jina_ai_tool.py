#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

import requests

from agentuniverse.agent.action.tool.common_tool.jina_ai_tool import JinaAITool


class JinaAIToolTest(unittest.TestCase):
    def test_make_api_request_verifies_ssl_by_default(self):
        tool = JinaAITool()

        with patch(
            'agentuniverse.agent.action.tool.common_tool.jina_ai_tool.requests.get',
            side_effect=requests.Timeout()
        ) as get_mock, patch(
            'agentuniverse.agent.action.tool.common_tool.jina_ai_tool.time.sleep'
        ):
            tool._make_api_request(
                'https://r.jina.ai/https://example.com',
                timeout=1,
                error_prefix='Error reading URL'
            )

        self.assertTrue(get_mock.call_args.kwargs["verify"])

    def test_execute_can_disable_ssl_verification_explicitly(self):
        tool = JinaAITool()

        with patch.object(tool, "read_url", return_value="ok"):
            result = tool.execute("https://example.com", verify_ssl=False)

        self.assertEqual(result, "ok")
        self.assertFalse(tool.verify_ssl)

    def test_make_api_request_handles_http_error_without_response(self):
        tool = JinaAITool()

        with patch(
            'agentuniverse.agent.action.tool.common_tool.jina_ai_tool.requests.get',
            side_effect=requests.HTTPError('connection failed')
        ), patch(
            'agentuniverse.agent.action.tool.common_tool.jina_ai_tool.time.sleep'
        ):
            result = tool._make_api_request(
                'https://r.jina.ai/https://example.com',
                timeout=1,
                error_prefix='Error reading URL'
            )

        self.assertIn('HTTP Error', result)
        self.assertIn('connection failed', result)


if __name__ == '__main__':
    unittest.main()
