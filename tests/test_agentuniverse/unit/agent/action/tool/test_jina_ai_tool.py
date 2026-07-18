# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for JinaAITool TLS verification behaviour."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

import requests

import agentuniverse.agent.action.tool.common_tool.jina_ai_tool as jina_module
from agentuniverse.agent.action.tool.common_tool.jina_ai_tool import JinaAITool


class JinaAIToolTLSTest(unittest.TestCase):
    """TLS verification must be on by default, not hardcoded off."""

    def _mock_ok_response(self) -> MagicMock:
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.json.return_value = {"code": 200, "data": {"content": "ok"}}
        return resp

    def test_verify_tls_true_by_default(self) -> None:
        tool = JinaAITool()
        self.assertTrue(tool.verify_tls)
        with patch.object(jina_module.requests, "get") as mock_get:
            mock_get.return_value = self._mock_ok_response()
            tool._make_api_request("https://r.jina.ai/https://x", 10, "err")
            _, kwargs = mock_get.call_args
            # Secure default: certificates are verified.
            self.assertIs(kwargs.get("verify"), True)

    def test_verify_tls_can_be_disabled_via_config(self) -> None:
        tool = JinaAITool(verify_tls=False)
        with patch.object(jina_module.requests, "get") as mock_get:
            mock_get.return_value = self._mock_ok_response()
            tool._make_api_request("https://r.jina.ai/https://x", 10, "err")
            _, kwargs = mock_get.call_args
            self.assertIs(kwargs.get("verify"), False)

    def test_non_200_logs_warning_without_writing_stdout(self) -> None:
        tool = JinaAITool()
        with patch.object(jina_module.requests, "get") as mock_get:
            resp = MagicMock()
            resp.raise_for_status.return_value = None
            resp.json.return_value = {"code": 401}
            mock_get.return_value = resp
            out = io.StringIO()
            with redirect_stdout(out):
                result = tool._make_api_request(
                    "https://r.jina.ai/https://x", 10, "err")
        self.assertIsNone(result)
        # The failure is reported through the logger, never printed to stdout.
        self.assertEqual(out.getvalue(), "")

    def test_make_api_request_handles_http_error_without_response(self) -> None:
        tool = JinaAITool()
        with patch.object(
            jina_module.requests,
            "get",
            side_effect=requests.HTTPError("connection failed"),
        ), patch.object(jina_module.time, "sleep"):
            result = tool._make_api_request(
                "https://r.jina.ai/https://example.com",
                timeout=1,
                error_prefix="Error reading URL",
            )

        self.assertIn("HTTP Error", result)
        self.assertIn("connection failed", result)


if __name__ == "__main__":
    unittest.main()
