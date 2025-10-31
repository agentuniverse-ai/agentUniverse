# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: test_startup_context.py

import pytest
from pathlib import Path

from agentuniverse.base.startup.startup_context import StartupContext
from agentuniverse.base.startup.startup_phase import StartupPhaseEnum


class TestStartupContext:
    """Test cases for StartupContext."""

    def test_context_initialization(self):
        """Test context initialization with parameters."""
        context = StartupContext(config_path="/test/config.toml", core_mode=True)

        assert context.config_path == "/test/config.toml"
        assert context.core_mode is True
        assert context.project_root_path is None
        assert len(context.get_completed_phases()) == 0

    def test_context_initialization_defaults(self):
        """Test context initialization with default values."""
        context = StartupContext()

        assert context.config_path is None
        assert context.core_mode is False

    def test_mark_phase_completed(self):
        """Test marking phases as completed."""
        context = StartupContext()

        context.mark_phase_completed(StartupPhaseEnum.CONFIG)
        assert context.is_phase_completed(StartupPhaseEnum.CONFIG)
        assert not context.is_phase_completed(StartupPhaseEnum.LOGGING)

    def test_multiple_phases_completed(self):
        """Test marking multiple phases as completed."""
        context = StartupContext()

        context.mark_phase_completed(StartupPhaseEnum.CONFIG)
        context.mark_phase_completed(StartupPhaseEnum.LOGGING)
        context.mark_phase_completed(StartupPhaseEnum.TELEMETRY)

        completed = context.get_completed_phases()
        assert len(completed) == 3
        assert StartupPhaseEnum.CONFIG in completed
        assert StartupPhaseEnum.LOGGING in completed
        assert StartupPhaseEnum.TELEMETRY in completed

    def test_data_storage(self):
        """Test storing and retrieving arbitrary data."""
        context = StartupContext()

        context.set_data("test_key", "test_value")
        assert context.get_data("test_key") == "test_value"
        assert context.has_data("test_key")

    def test_data_default_value(self):
        """Test retrieving non-existent data with default."""
        context = StartupContext()

        assert context.get_data("nonexistent", "default") == "default"
        assert not context.has_data("nonexistent")

    def test_clear_phase_data(self):
        """Test clearing phase completion data."""
        context = StartupContext()

        context.mark_phase_completed(StartupPhaseEnum.CONFIG)
        context.mark_phase_completed(StartupPhaseEnum.LOGGING)
        assert len(context.get_completed_phases()) == 2

        context.clear_phase_data()
        assert len(context.get_completed_phases()) == 0

    def test_context_repr(self):
        """Test string representation of context."""
        context = StartupContext(config_path="/test/config.toml", core_mode=True)
        context.mark_phase_completed(StartupPhaseEnum.CONFIG)

        repr_str = repr(context)
        assert "StartupContext" in repr_str
        assert "/test/config.toml" in repr_str
        assert "core_mode=True" in repr_str
        assert "completed_phases=1" in repr_str
