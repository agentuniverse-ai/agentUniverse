# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_flask_server.py

"""Unit tests for the flask web server endpoints and helpers."""

import json
import time

from agentuniverse.agent_serve.web.flask_server import (
    SerializableRequest,
    app,
    timed_generator,
)
from agentuniverse.agent_serve.web.web_util import FlaskServerManager


class TestFlaskEndpoints:
    """Test basic registered flask endpoints with the test client."""

    def test_echo_endpoint(self):
        response = app.test_client().get("/echo")
        assert response.status_code == 200
        assert response.get_data(as_text=True) == "Welcome to agentUniverse!!!"

    def test_liveness_endpoint(self):
        response = app.test_client().get("/liveness")
        assert response.status_code == 200
        payload = json.loads(response.get_data(as_text=True))
        assert payload["success"] is True
        assert payload["result"] == "liveness health check pass!"

    def test_unknown_route_returns_404(self):
        assert app.test_client().get("/not-a-route").status_code == 404


class TestFlaskHelpers:
    """Test small helpers defined in the flask server module."""

    def test_flask_server_manager_timeout(self):
        manager = FlaskServerManager()
        assert FlaskServerManager() is manager
        assert manager.sync_service_timeout == 30
        manager.sync_service_timeout = 60
        assert FlaskServerManager().sync_service_timeout == 60
        manager.sync_service_timeout = 30

    def test_serializable_request_repr(self):
        req = SerializableRequest("POST", "/echo", {}, {}, {})
        assert "POST" in repr(req)
        assert "/echo" in repr(req)

    def test_timed_generator_passes_data_through(self):
        generator = timed_generator((x for x in [1, 2, 3]), time.time(),
                                    "ctx")
        assert list(generator) == [1, 2, 3]

    def test_timed_generator_terminates_on_close(self):
        generator = timed_generator((x for x in range(1000)), time.time(),
                                    "ctx")
        assert next(generator) == 0
