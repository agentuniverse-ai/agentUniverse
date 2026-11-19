# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest import mock

from agentuniverse.agent_serve.web.rpc import rpc_server


class TestServiceRunParamsGuard(unittest.TestCase):
    def test_invalid_json_returns_error(self):
        result = rpc_server.service_run(False, "{not valid json", "svc-1")
        self.assertFalse(result["success"])
        self.assertIsNone(result["request_id"])
        self.assertIn("invalid params", result["message"])

    def test_non_object_json_returns_error(self):
        result = rpc_server.service_run(False, "[1, 2, 3]", "svc-1")
        self.assertFalse(result["success"])
        self.assertIn("json must be an object", result["message"])

    def test_valid_json_succeeds(self):
        with mock.patch.object(rpc_server, "ServiceInstance") as mock_si, \
                mock.patch.object(rpc_server, "RequestTask") as mock_rt:
            instance = mock_si.return_value
            instance.run = mock.MagicMock()
            task = mock_rt.return_value
            task.run.return_value = {"ok": True}
            task.request_id = "req-1"

            result = rpc_server.service_run(False, '{"a": 1}', "svc-1")

            self.assertTrue(result["success"])
            self.assertEqual(result["request_id"], "req-1")

    def test_empty_params_uses_default_dict(self):
        with mock.patch.object(rpc_server, "ServiceInstance") as mock_si, \
                mock.patch.object(rpc_server, "RequestTask") as mock_rt:
            instance = mock_si.return_value
            instance.run = mock.MagicMock()
            task = mock_rt.return_value
            task.run.return_value = {"ok": True}
            task.request_id = "req-2"

            result = rpc_server.service_run(False, "", "svc-2")

            self.assertTrue(result["success"])


class TestServiceRunAsyncParamsGuard(unittest.TestCase):
    def test_invalid_json_returns_error(self):
        with mock.patch.object(rpc_server, "service_run_queue"):
            result = rpc_server.service_run_async(False, "{bad", "svc-3")
            self.assertFalse(result["success"])
            self.assertIn("invalid params", result["message"])

    def test_valid_json_succeeds(self):
        with mock.patch.object(rpc_server, "service_run_queue") as mock_queue, \
                mock.patch.object(rpc_server, "RequestTask") as mock_rt:
            task = mock_rt.return_value
            task.async_run.return_value = None
            task.request_id = "req-3"

            result = rpc_server.service_run_async(False, '{"a": 1}', "svc-3")

            self.assertTrue(result["success"])
            self.assertEqual(result["request_id"], "req-3")
            mock_queue.assert_called_once()


if __name__ == "__main__":
    unittest.main()
