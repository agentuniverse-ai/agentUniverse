#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

import requests

from agentuniverse.agent.action.tool.common_tool.github_tool import GitHubTool


class GitHubToolTest(unittest.TestCase):
    def test_make_request_handles_http_error_without_response(self):
        tool = GitHubTool(api_key=None)

        with patch(
            'agentuniverse.agent.action.tool.common_tool.github_tool.requests.get',
            side_effect=requests.HTTPError('connection failed')
        ):
            result = tool._make_request('https://api.github.com/search/repositories')

        self.assertIn('error', result)
        self.assertIn('HTTP Error', result['error'])
        self.assertIn('connection failed', result['error'])


if __name__ == '__main__':
    unittest.main()
