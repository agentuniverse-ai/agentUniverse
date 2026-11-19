# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for the generated gRPC module agentuniverse_service_pb2_grpc.

The module defines the stub and servicer classes for the agentuniverse gRPC
service: AgentUniverseServiceStub, AgentUniverseServiceServicer and the
add_AgentUniverseServiceServicer_to_server registration helper.  The tests
below exercise their deterministic behaviors with lightweight fakes instead
of a real gRPC channel.
"""

import grpc
import pytest

from agentuniverse.agent_serve.web.rpc.grpc import agentuniverse_service_pb2_grpc as pb2_grpc


class FakeContext:
    """Minimal stand-in for a grpc.ServicerContext."""

    def __init__(self):
        self.code = None
        self.details = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details


class FakeChannel:
    """Records unary_unary registration calls made by a stub."""

    def __init__(self):
        self.paths = []

    def unary_unary(self, path, request_serializer=None, response_deserializer=None):
        self.paths.append(path)

        def invoke(request, timeout=None, metadata=None, credentials=None):
            return None

        return invoke


class TestAgentUniverseServiceServicer:
    """Tests for the servicer's RPC method handlers."""

    @pytest.fixture
    def servicer(self):
        return pb2_grpc.AgentUniverseServiceServicer()

    def test_service_run_is_unimplemented(self, servicer):
        context = FakeContext()
        with pytest.raises(NotImplementedError):
            servicer.service_run(None, context)
        assert context.code == grpc.StatusCode.UNIMPLEMENTED
        assert context.details == "Method not implemented!"

    def test_service_run_async_is_unimplemented(self, servicer):
        context = FakeContext()
        with pytest.raises(NotImplementedError):
            servicer.service_run_async(None, context)
        assert context.code == grpc.StatusCode.UNIMPLEMENTED

    def test_service_run_result_is_unimplemented(self, servicer):
        context = FakeContext()
        with pytest.raises(NotImplementedError):
            servicer.service_run_result(None, context)
        assert context.code == grpc.StatusCode.UNIMPLEMENTED


class TestAgentUniverseServiceStub:
    """Tests for the client-side stub."""

    def test_stub_registers_three_rpc_paths(self):
        channel = FakeChannel()
        pb2_grpc.AgentUniverseServiceStub(channel)
        assert channel.paths == [
            "/agentuniverse.AgentUniverseService/service_run",
            "/agentuniverse.AgentUniverseService/service_run_async",
            "/agentuniverse.AgentUniverseService/service_run_result",
        ]

    def test_stub_exposes_rpc_attributes(self):
        channel = FakeChannel()
        stub = pb2_grpc.AgentUniverseServiceStub(channel)
        assert callable(stub.service_run)
        assert callable(stub.service_run_async)
        assert callable(stub.service_run_result)


class TestServiceRegistration:
    """Tests for the add_AgentUniverseServiceServicer_to_server helper."""

    def _registered_handlers(self):
        captured = []

        class FakeServer:
            def add_generic_rpc_handlers(self, handlers):
                captured.extend(handlers)

        server = FakeServer()
        pb2_grpc.add_AgentUniverseServiceServicer_to_server(
            pb2_grpc.AgentUniverseServiceServicer(), server
        )
        return captured

    def test_registration_adds_one_generic_handler(self):
        handlers = self._registered_handlers()
        assert len(handlers) == 1
        assert handlers[0].service_name() == "agentuniverse.AgentUniverseService"

    def test_registered_handler_exposes_service_name(self):
        handlers = self._registered_handlers()
        assert handlers[0].service_name() == "agentuniverse.AgentUniverseService"


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
