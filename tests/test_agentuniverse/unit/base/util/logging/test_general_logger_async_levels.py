# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import asyncio

import loguru
import pytest

from agentuniverse.base.util.logging.general_logger import GeneralLogger


@pytest.fixture
def captured_records():
    records = []
    handler_id = loguru.logger.add(
        lambda message: records.append(message), level="TRACE")
    yield records
    loguru.logger.remove(handler_id)


@pytest.mark.parametrize("async_method,expected_level", [
    ("awarn", "WARNING"),
    ("ainfo", "INFO"),
    ("aerror", "ERROR"),
    ("acritical", "CRITICAL"),
    ("atrace", "TRACE"),
    ("adebug", "DEBUG"),
])
def test_async_log_methods_delegate_to_namesake_level(
        captured_records, async_method, expected_level):
    logger = GeneralLogger("unit_test_module", "", "", "", "",
                           add_handler=False)
    asyncio.run(getattr(logger, async_method)("message under test"))

    assert captured_records, f"{async_method} produced no log record"
    assert captured_records[-1].record["level"].name == expected_level
