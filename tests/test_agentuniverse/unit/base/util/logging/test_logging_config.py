# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_logging_config.py

"""Unit tests for LoggingConfig defaults and toml file loading."""

import os
import tempfile

from agentuniverse.base.util.logging.logging_config import \
    LoggingConfig


class TestLoggingConfigDefaults:
    """Test class-level default configuration values."""

    def test_default_values(self):
        assert LoggingConfig.log_level == "INFO"
        assert "YYYY-MM-DD" in LoggingConfig.log_format
        assert LoggingConfig.log_extend_module_list == ["sls_log"]
        assert LoggingConfig.log_path is None
        assert LoggingConfig.log_rotation == "10 MB"
        assert LoggingConfig.log_retention == "3 days"
        assert LoggingConfig.log_compression == "zip"
        assert LoggingConfig.sls_log_queue_max_size == 1000
        assert LoggingConfig.sls_log_send_interval == 3.0
        assert LoggingConfig.sls_endpoint == ""


class TestLoggingConfigFileLoad:
    """Test loading configuration from a toml file."""

    def test_valid_toml_updates_config(self):
        toml_text = """[LOG_CONFIG]
[LOG_CONFIG.BASIC_CONFIG]
log_level="debug"
log_path="logs/"
log_rotation="1 MB"
log_retention="1 day"
log_compression="gz"
[LOG_CONFIG.EXTEND_MODULE]
sls_log="false"
"""
        with tempfile.NamedTemporaryFile("w", suffix=".toml",
                                         delete=False) as f:
            f.write(toml_text)
            path = f.name
        try:
            LoggingConfig(path)
        finally:
            os.unlink(path)
        assert LoggingConfig.log_level == "DEBUG"
        assert LoggingConfig.log_path == "logs/"
        assert LoggingConfig.log_rotation == "1 MB"
        assert LoggingConfig.log_retention == "1 day"
        assert LoggingConfig.log_compression == "gz"
        assert LoggingConfig.log_extend_module_switch["sls_log"] is False

    def test_missing_file_falls_back_to_defaults(self, capsys):
        LoggingConfig("/tmp/definitely_missing_au_config.toml")
        captured = capsys.readouterr()
        assert "default config" in captured.out

    def test_sls_config_loaded_when_enabled(self):
        toml_text = """[LOG_CONFIG]
[LOG_CONFIG.BASIC_CONFIG]
log_level="info"
[LOG_CONFIG.EXTEND_MODULE]
sls_log="true"
[LOG_CONFIG.ALIYUN_SLS_CONFIG]
sls_endpoint="http://sls.example.com"
sls_project="proj"
sls_log_store="store"
access_key_id="ak"
access_key_secret="sk"
sls_log_queue_max_size="2000"
sls_log_send_interval="1.5"
"""
        with tempfile.NamedTemporaryFile("w", suffix=".toml",
                                         delete=False) as f:
            f.write(toml_text)
            path = f.name
        try:
            LoggingConfig(path)
        finally:
            os.unlink(path)
        assert LoggingConfig.log_extend_module_switch["sls_log"] is True
        assert LoggingConfig.sls_endpoint == "http://sls.example.com"
        assert LoggingConfig.sls_project == "proj"
        assert LoggingConfig.sls_log_queue_max_size == 2000
        assert LoggingConfig.sls_log_send_interval == 1.5
