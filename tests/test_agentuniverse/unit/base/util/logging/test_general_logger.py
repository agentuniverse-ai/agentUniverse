# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_general_logger.py

"""Unit tests for the general_logger helpers."""

import pytest

import agentuniverse.base.util.logging.general_logger as gl_module
from agentuniverse.base.util.logging.general_logger import (
    GeneralLogger,
    Logger,
    _get_source_filter,
    get_context_prefix,
)
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestContextPrefix:
    """Test get_context_prefix formatting."""

    def test_empty_context_returns_default(self):
        class FakeTrace:
            def get_trace_dict(self):
                return {}

        class FakeCtx:
            def get_context(self, key):
                return None

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(gl_module, "AuTraceManager",
                       lambda: FakeTrace())
            mp.setattr(gl_module, "FrameworkContextManager",
                       lambda: FakeCtx())
            assert get_context_prefix() == "[default]"

    def test_returns_bracketed_string(self):
        prefix = get_context_prefix()
        assert prefix.startswith("[")
        assert prefix.endswith("]")


class TestSourceFilter:
    """Test the _get_source_filter helper."""

    def test_matching_record_passes(self):
        record = {"extra": {"log_type": LogTypeEnum.default,
                            "source": "mod1"}}
        assert _get_source_filter("mod1")(record) is True

    def test_wrong_source_fails(self):
        record = {"extra": {"log_type": LogTypeEnum.default,
                            "source": "mod2"}}
        assert _get_source_filter("mod1")(record) is False

    def test_wrong_log_type_fails(self):
        record = {"extra": {"log_type": LogTypeEnum.agent_input,
                            "source": "mod1"}}
        assert _get_source_filter("mod1")(record) is False


class TestLoggerClasses:
    """Test Logger abstraction and GeneralLogger."""

    def test_logger_is_abstract(self):
        with pytest.raises(TypeError):
            Logger()

    def test_general_logger_fields(self):
        logger = GeneralLogger("mod1", "logs/x.log", "{message}",
                               "10 MB", "3 days", add_handler=False)
        assert logger.module_name == "mod1"
        assert logger.log_path == "logs/x.log"
        assert logger.log_rotation == "10 MB"

    def test_update_properties(self):
        logger = GeneralLogger("mod1", "logs/x.log", "{message}",
                               "10 MB", "3 days", add_handler=False)
        logger.update_properties(log_rotation="20 MB")
        assert logger.log_rotation == "20 MB"

    def test_update_properties_unknown_key_raises(self):
        logger = GeneralLogger("mod1", "logs/x.log", "{message}",
                               "10 MB", "3 days", add_handler=False)
        with pytest.raises(AttributeError, match="no attribute"):
            logger.update_properties(nope=1)
