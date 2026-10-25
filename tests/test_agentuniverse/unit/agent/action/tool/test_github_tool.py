#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

import requests

from agentuniverse.agent.action.tool.common_tool.github_tool import GitHubTool


class GitHubToolTest(unittest.TestCase):
    @staticmethod
    def _response(status_code, body, headers=None):
        response = requests.Response()
        response.status_code = status_code
        response.headers.update(headers or {})
        response._content = body.encode("utf-8")
        response.url = "https://api.github.com/test"
        return response

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

    def test_permission_denied_403_preserves_github_message(self):
        response = self._response(
            403,
            '{"message":"Resource not accessible by integration"}',
            {"x-ratelimit-remaining": "4999"},
        )

        with patch(
            'agentuniverse.agent.action.tool.common_tool.github_tool.requests.get',
            return_value=response,
        ):
            result = GitHubTool(api_key=None)._make_request(response.url)

        self.assertEqual(
            result["error"],
            'HTTP Error 403: {"message":"Resource not accessible by integration"}',
        )

    def test_rate_limited_403_keeps_rate_limit_message(self):
        response = self._response(
            403,
            '{"message":"Forbidden"}',
            {"x-ratelimit-remaining": "0"},
        )

        with patch(
            'agentuniverse.agent.action.tool.common_tool.github_tool.requests.get',
            return_value=response,
        ):
            result = GitHubTool(api_key=None)._make_request(response.url)

        self.assertIn("API rate limit exceeded", result["error"])

    def test_malformed_forbidden_body_stays_an_http_error(self):
        response = self._response(403, "upstream returned HTML", {"x-ratelimit-remaining": "4999"})

        with patch(
            'agentuniverse.agent.action.tool.common_tool.github_tool.requests.get',
            return_value=response,
        ):
            result = GitHubTool(api_key=None)._make_request(response.url)

        self.assertEqual(result["error"], "HTTP Error 403: upstream returned HTML")


if __name__ == '__main__':
    unittest.main()
