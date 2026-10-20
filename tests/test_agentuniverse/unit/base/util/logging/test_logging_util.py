# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 15:50
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: test_logging_util.py

import os
import shutil
import time
import pytest

from agentuniverse.base.config.configer import Configer
from agentuniverse.base.context.framework_context import FrameworkContext
from agentuniverse.base.util.logging import logging_util
from agentuniverse.base.util.logging.logging_config import LoggingConfig
from agentuniverse.base.util.logging.logging_util import LOGGER, init_loggers, LOG_FILE_PREFIX

test_context = {"LOG_CONTEXT": {"REQUEST_ID": "1111-2222-3333",
                                "AGENT_ID": "TEST_AGENT"}}


def test_logging_config_without_path_uses_defaults(monkeypatch):
    monkeypatch.setattr(LoggingConfig, "log_extend_module_switch", {"sls_log": True})

    def fail_load_by_path(*args, **kwargs):
        raise AssertionError("Configer.load_by_path should not be called without a config path")

    monkeypatch.setattr(Configer, "load_by_path", fail_load_by_path)

    LoggingConfig()

    assert LoggingConfig.log_extend_module_switch == {"sls_log": False}


def test_logging_util(tmp_path, monkeypatch):
    # Without a log config file ``init_loggers()`` resets every class level
    # setting to its documented default, so ``log_path`` can no longer be
    # seeded from the outside. Point the project root at a temporary directory
    # and assert the documented default location instead.
    monkeypatch.setattr(logging_util, "get_project_root_path", lambda: tmp_path)

    init_loggers()
    test_log_path = tmp_path / logging_util.LOG_SUB_DIR
    with FrameworkContext(test_context):
        test_logger = LOGGER
        test_logger.info("test info log")
        test_logger.error("test error log")
        time.sleep(0.01)
        with open(os.path.join(str(test_log_path), LOG_FILE_PREFIX+"_all.log"), 'r') as file:
            first_line = file.readline().strip()
            second_line = file.readline().strip()
            assert "test info log" in first_line
            assert "test error log" in second_line
        with open(os.path.join(str(test_log_path), LOG_FILE_PREFIX+"_error.log"), 'r') as file:
            first_line = file.readline().strip()
            assert "test error log" in first_line

        # delete test logs
        try:
            shutil.rmtree(test_log_path)
            print(f"The directory {test_log_path} has been deleted.")
        except OSError as e:
            print(f"Error: {e.strerror}")


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
