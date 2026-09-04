# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_rpc_server.py

"""Unit tests for the rpc server glue functions (dependencies mocked)."""

import json
from types import SimpleNamespace
from unittest.mock import patch

import agentuniverse.agent_serve.web.rpc.rpc_server as rpc_module
from agentuniverse.agent_serve.web.rpc.rpc_server import (
    service_run,
    service_run_async,
    service_run_result,
)


class FakeRequestTask:
    """Stand-in for RequestTask recording constructor arguments."""

    def __init__(self, func, saved=True, **kwargs):
        self.func = func
        self.saved = saved
        self.kwargs = kwargs
        self.request_id = "rid-123"
        self.result_value = "service result"

    def run(self):
        return self.result_value

    def async_run(self):
        self.ran_async = True



def make_task(*args, **kwargs):
    return FakeRequestTask(*args, **kwargs)


class TestServiceRun:
    """Test the sync rpc entry point."""

    def test_service_run_parses_json_params(self):
        with patch.object(rpc_module, "ServiceInstance") as service_cls, \
                patch.object(rpc_module, "RequestTask",
                             side_effect=make_task) as task_cls:
            result = service_run(False, '{"a": 1}', "svc1")
        assert task_cls.call_args.args[1] is False
        assert task_cls.call_args.kwargs == {"a": 1}
        assert result == {"success": True, "result": "service result",
                          "message": None, "request_id": "rid-123"}

    def test_service_run_empty_params(self):
        with patch.object(rpc_module, "ServiceInstance") as service_cls, \
                patch.object(rpc_module, "RequestTask",
                             side_effect=make_task) as task_cls:
            result = service_run(False, "   ", "svc1")
        assert task_cls.call_args.kwargs == {}
        assert result["success"] is True

    def test_service_run_passes_run_as_function(self):
        with patch.object(rpc_module, "ServiceInstance",
                          return_value=SimpleNamespace(
                              run=lambda: "x")) as service_cls, \
                patch.object(rpc_module, "RequestTask",
                             side_effect=make_task) as task_cls:
            service_run(True, "", "svc1")
        func_arg = task_cls.call_args.args[0]
        assert func_arg() == "x"


class TestServiceRunResult:
    """Test the async-result rpc entry point."""

    def test_result_found(self):
        data = {"state": "finished", "result": {"k": 1}, "steps": []}
        with patch.object(rpc_module.RequestTask, "query_request_state",
                          staticmethod(lambda rid: data)):
            result = service_run_result("rid-123")
        assert result["success"] is True
        assert json.loads(result["result"]) == data
        assert result["request_id"] == "rid-123"

    def test_result_not_found(self):
        with patch.object(rpc_module.RequestTask, "query_request_state",
                          staticmethod(lambda rid: None)):
            result = service_run_result("missing")
        assert result["success"] is False
        assert "missing" in result["message"]
