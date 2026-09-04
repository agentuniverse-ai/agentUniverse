# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_demo_search_tool.py
"""Unit tests for the DemoSearchTool example tool.

The tool itself performs real Google searches through the Serper API, so only
its deterministic configuration contract is tested here: the ``serper_api_key``
field must be resolved from the ``SERPER_API_KEY`` environment variable when an
instance is created. No network call is made.
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[9]))

from agentuniverse.agent.action.tool.tool import Tool
from examples.sample_standard_app.intelligence.agentic.tool.custom.demo_search_tool import \
    DemoSearchTool

SERPER_KEY_ENV = "SERPER_API_KEY"


class TestDemoSearchTool:
    """Test the DemoSearchTool example tool configuration contract."""

    def test_is_tool_subclass(self):
        assert issubclass(DemoSearchTool, Tool)

    def test_serper_api_key_field_exists(self):
        assert "serper_api_key" in DemoSearchTool.model_fields

    def test_serper_api_key_none_when_env_missing(self, monkeypatch):
        monkeypatch.delenv(SERPER_KEY_ENV, raising=False)
        tool = DemoSearchTool()
        assert tool.serper_api_key is None

    def test_serper_api_key_none_when_env_empty(self, monkeypatch):
        monkeypatch.setenv(SERPER_KEY_ENV, "")
        tool = DemoSearchTool()
        assert tool.serper_api_key is None

    def test_serper_api_key_reads_env(self, monkeypatch):
        monkeypatch.setenv(SERPER_KEY_ENV, "sk-demo-key-1")
        tool = DemoSearchTool()
        assert tool.serper_api_key == "sk-demo-key-1"

    def test_serper_api_key_reflects_current_env(self, monkeypatch):
        monkeypatch.setenv(SERPER_KEY_ENV, "sk-first")
        assert DemoSearchTool().serper_api_key == "sk-first"
        monkeypatch.setenv(SERPER_KEY_ENV, "sk-second")
        assert DemoSearchTool().serper_api_key == "sk-second"

    def test_serper_api_key_is_optional(self):
        assert DemoSearchTool.model_fields["serper_api_key"].is_required() is False
