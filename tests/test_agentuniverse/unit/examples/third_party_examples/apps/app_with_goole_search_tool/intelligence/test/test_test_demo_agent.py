# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_test_demo_agent.py

"""Unit tests for the DemoAgentTest example module."""

import queue
import unittest

import examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.test.test_demo_agent as demo_agent_module

EOF_MARKER = '{"type": "EOF"}'


class TestDemoAgentTestStructure:
    """Structural checks for DemoAgentTest."""

    def test_class_is_unittest_test_case(self):
        """DemoAgentTest should subclass unittest.TestCase."""
        demo_agent_test = demo_agent_module.DemoAgentTest
        assert issubclass(demo_agent_test, unittest.TestCase)

    def test_declares_stream_test_method(self):
        """DemoAgentTest should declare its agent stream test method."""
        assert callable(getattr(demo_agent_module.DemoAgentTest,
                                'test_demo_agent_stream', None))

    def test_declares_read_output_helper(self):
        """DemoAgentTest should declare the read_output helper."""
        assert callable(getattr(demo_agent_module.DemoAgentTest,
                                'read_output', None))


class TestDemoAgentReadOutput:
    """Behavioral checks for DemoAgentTest.read_output."""

    def setup_method(self):
        """Build a fresh DemoAgentTest instance and output queue."""
        self.demo = demo_agent_module.DemoAgentTest()
        self.output_stream = queue.Queue()

    def test_read_output_returns_none_on_eof_only(self):
        """read_output should return cleanly when only the EOF marker is queued."""
        self.output_stream.put(EOF_MARKER)
        result = self.demo.read_output(self.output_stream)
        assert result is None

    def test_read_output_drains_messages_until_eof(self):
        """read_output should consume queued messages until the EOF marker."""
        self.output_stream.put('message one')
        self.output_stream.put('message two')
        self.output_stream.put(EOF_MARKER)
        self.demo.read_output(self.output_stream)
        assert self.output_stream.empty()

    def test_read_output_stops_at_eof_marker(self):
        """read_output should stop as soon as the EOF marker is read."""
        self.output_stream.put(EOF_MARKER)
        self.output_stream.put('message after eof')
        self.demo.read_output(self.output_stream)
        # The loop breaks on EOF, so anything queued behind it stays untouched.
        assert not self.output_stream.empty()
        assert self.output_stream.get() == 'message after eof'

    def test_read_output_consumes_eof_marker(self):
        """read_output should remove the EOF marker from the queue."""
        self.output_stream.put('ping')
        self.output_stream.put(EOF_MARKER)
        self.demo.read_output(self.output_stream)
        assert self.output_stream.empty()
