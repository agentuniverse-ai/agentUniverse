# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_server_application.py

"""Unit tests for the ServerApplication bootstrap entry point."""

from unittest.mock import Mock, patch

import examples.third_party_examples.apps.app_with_goole_search_tool.bootstrap.intelligence.server_application as server_app


class TestServerApplication:
    """Unit tests for ServerApplication."""

    def test_start_is_classmethod(self):
        """start() should be exposed as a classmethod on ServerApplication."""
        start_method = server_app.ServerApplication.__dict__.get('start')
        assert start_method is not None
        assert isinstance(start_method, classmethod)

    def test_start_initializes_agent_universe(self):
        """start() should bootstrap the AgentUniverse framework."""
        with patch.object(server_app, 'AgentUniverse') as mock_au, \
                patch.object(server_app, 'start_web_server'):
            server_app.ServerApplication.start()
            mock_au.return_value.start.assert_called_once()

    def test_start_launches_web_server(self):
        """start() should launch the web server after framework startup."""
        with patch.object(server_app, 'AgentUniverse'), \
                patch.object(server_app, 'start_web_server') as mock_ws:
            server_app.ServerApplication.start()
            mock_ws.assert_called_once()

    def test_start_invokes_framework_before_web_server(self):
        """The framework must be started before the web server is launched."""
        order = []

        def record(label):
            order.append(label)

        class FakeAgentUniverse:
            def start(self):
                record('agent_universe')

        with patch.object(server_app, 'AgentUniverse', FakeAgentUniverse), \
                patch.object(server_app, 'start_web_server',
                             Mock(side_effect=lambda: record('web_server'))):
            server_app.ServerApplication.start()
        assert order == ['agent_universe', 'web_server']

    def test_start_returns_none(self):
        """start() should not return any value."""
        with patch.object(server_app, 'AgentUniverse'), \
                patch.object(server_app, 'start_web_server'):
            result = server_app.ServerApplication.start()
            assert result is None
