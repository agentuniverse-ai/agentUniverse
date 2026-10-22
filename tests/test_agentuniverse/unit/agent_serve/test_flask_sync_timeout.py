# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/9/20 20:10
# @FileName: test_flask_sync_timeout.py
import time
from unittest.mock import patch

import pytest

from agentuniverse.agent_serve.web.flask_server import app
from agentuniverse.agent_serve.web.web_util import FlaskServerManager


class _FakeServiceInstance:
    """Replace ServiceInstance with a controllable, slow service."""

    sleep_seconds = 3.0

    def __init__(self, service_code):
        self.service_code = service_code

    def run(self, **kwargs):
        time.sleep(_FakeServiceInstance.sleep_seconds)
        return {"answer": "ok"}


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def short_timeout():
    manager = FlaskServerManager()
    original = manager.sync_service_timeout
    manager.sync_service_timeout = 0.5
    yield
    manager.sync_service_timeout = original


def _post_and_time(client, url, payload):
    start = time.time()
    response = client.post(url, json=payload)
    return response, time.time() - start


def test_service_run_timeout_does_not_wait_for_the_service(client, short_timeout):
    with patch('agentuniverse.agent_serve.web.flask_server.ServiceInstance', _FakeServiceInstance):
        response, elapsed = _post_and_time(client, '/service_run',
                                           {"service_id": "svc", "params": {}})

    assert response.status_code == 504
    assert response.get_json()['success'] is False
    assert response.get_json()['message'] == "AU sync service timeout"
    assert elapsed < _FakeServiceInstance.sleep_seconds - 0.5


def test_openai_chat_timeout_does_not_wait_for_the_service(client, short_timeout):
    payload = {
        "model": "svc",
        "messages": [{"role": "user", "content": "hello"}],
        "stream": False,
    }
    with patch('agentuniverse.agent_serve.web.flask_server.ServiceInstance', _FakeServiceInstance):
        response, elapsed = _post_and_time(client, '/chat/completions', payload)

    assert response.status_code == 504
    assert elapsed < _FakeServiceInstance.sleep_seconds - 0.5


def test_service_run_success_is_unchanged(client):
    original_sleep = _FakeServiceInstance.sleep_seconds
    _FakeServiceInstance.sleep_seconds = 0
    try:
        with patch('agentuniverse.agent_serve.web.flask_server.ServiceInstance', _FakeServiceInstance):
            response, elapsed = _post_and_time(client, '/service_run',
                                               {"service_id": "svc", "params": {}})
    finally:
        _FakeServiceInstance.sleep_seconds = original_sleep

    assert response.status_code == 200
    body = response.get_json()
    assert body['success'] is True
    assert body['result'] == {"answer": "ok"}
    assert body['request_id']
