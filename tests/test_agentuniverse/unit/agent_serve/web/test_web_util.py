# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_web_util.py

"""Unit tests for web_util helpers (request_param, responses, manager)."""

import json

import pytest
from flask import Flask

from agentuniverse.agent_serve.web.web_util import (
    FlaskServerManager,
    make_standard_response,
    request_param,
)

APP = Flask(__name__)


class TestFlaskServerManager:
    """Test the FlaskServerManager singleton."""

    def test_singleton_identity(self):
        assert FlaskServerManager() is FlaskServerManager()

    def test_sync_service_timeout_default_and_setter(self):
        manager = FlaskServerManager()
        assert manager.sync_service_timeout == 30
        manager.sync_service_timeout = 45
        assert manager.sync_service_timeout == 45
        manager.sync_service_timeout = 30


class TestRequestParam:
    """Test the request_param flask decorator."""

    def test_get_params_mapped_to_typed_argument(self):
        @request_param
        def handler(name: str = ""):
            return name

        with APP.test_request_context("/?name=alice", method="GET"):
            assert handler() == "alice"

    def test_get_missing_param_uses_default(self):
        @request_param
        def handler(name: str = "default_name"):
            return name

        with APP.test_request_context("/", method="GET"):
            assert handler() == "default_name"

    def test_post_json_body_mapped(self):
        @request_param
        def handler(value: str = ""):
            return value

        with APP.test_request_context("/", method="POST", data=json.dumps(
                {"value": "from-json"}), content_type="application/json"):
            assert handler() == "from-json"

    def test_kwargs_param_receives_request_data(self):
        @request_param
        def handler(**kwargs):
            return kwargs

        with APP.test_request_context("/?a=1&b=2", method="GET"):
            assert handler() == {"a": "1", "b": "2"}

    def test_session_id_reads_header(self):
        @request_param
        def handler(session_id=None):
            return session_id

        with APP.test_request_context(
                "/", method="GET",
                headers={"X-Session-Id": "sess-123"}):
            assert handler() == "sess-123"


class TestMakeStandardResponse:
    """Test make_standard_response."""

    def test_response_payload_and_status(self):
        with APP.test_request_context("/"):
            response = make_standard_response(
                True, result={"k": "v"}, message="ok",
                request_id="req-1", status_code=201)
        assert response.status_code == 201
        payload = json.loads(response.get_data(as_text=True))
        assert payload == {"success": True, "result": {"k": "v"},
                           "message": "ok", "request_id": "req-1"}
