# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_grpc_server_booster.py

"""Unit tests for grpc server booster (config + service delegation)."""

from types import SimpleNamespace
from unittest.mock import patch

import agentuniverse.agent_serve.web.rpc.grpc.grpc_server_booster \
    as booster_module
from agentuniverse.agent_serve.web.rpc.grpc import \
    agentuniverse_service_pb2 as pb2
from agentuniverse.agent_serve.web.rpc.grpc.grpc_server_booster import (
    GRPC_CONFIG,
    AgentUniverseService,
    set_grpc_config,
)

EMPTY_CONFIG = {"server_port": 50051, "max_workers": 10}


class TestGrpcConfig:
    """Test set_grpc_config defaults and overrides."""

    def test_defaults_when_no_grpc_section(self):
        GRPC_CONFIG.clear()
        set_grpc_config(SimpleNamespace(value={}))
        assert GRPC_CONFIG == {"server_port": 50051, "max_workers": 10}

    def test_overrides_from_config(self):
        GRPC_CONFIG.clear()
        set_grpc_config(SimpleNamespace(value={"GRPC": {
            "server_port": 9090, "max_workers": 8}}))
        assert GRPC_CONFIG == {"server_port": 9090, "max_workers": 8}


class TestAgentUniverseService:
    """Test grpc service method delegation and response mapping."""

    def test_service_run_delegates_and_maps_response(self):
        def fake_service_run(saved, params, service_id):
            assert saved is True
            assert params == '{"a": 1}'
            assert service_id == "svc1"
            return {"result": "r1", "request_id": "rid1",
                    "success": True, "message": "m1"}

        request = pb2.AgentServiceRequest(saved=True, params='{"a": 1}',
                                          service_id="svc1")
        with patch.object(booster_module, "service_run",
                          side_effect=fake_service_run):
            response = AgentUniverseService().service_run(request, None)
        assert response.success is True
        assert response.result == "r1"
        assert response.request_id == "rid1"
        assert response.message == "m1"

    def test_service_run_async_delegates(self):
        def fake_service_run_async(saved, params, service_id):
            return {"result": None, "request_id": "rid2",
                    "success": True, "message": "m2"}

        request = pb2.AgentServiceRequest(saved=False, params="",
                                          service_id="svc2")
        with patch.object(booster_module, "service_run_async",
                          side_effect=fake_service_run_async):
            response = AgentUniverseService().service_run_async(request,
                                                                None)
        assert response.success is True
        assert response.request_id == "rid2"

    def test_service_run_result_delegates(self):
        def fake_service_run_result(request_id):
            assert request_id == "rid3"
            return {"result": '{"state": "ok"}', "request_id": "rid3",
                    "success": True, "message": "m3"}

        request = pb2.AgentResultRequest(request_id="rid3")
        with patch.object(booster_module, "service_run_result",
                          side_effect=fake_service_run_result):
            response = AgentUniverseService().service_run_result(request,
                                                                None)
        assert response.success is True
        assert response.result == '{"state": "ok"}'
        assert response.request_id == "rid3"
