# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/29 20:54
# @FileName: test_logging_config.py
"""Regression tests for resetting the log configuration on fallback.

``LoggingConfig`` keeps the parsed values on the class itself. When a config
file cannot be used, the fallback must therefore undo the previous load as a
whole. Resetting only the extension switches used to leave the previous log
path, level, rotation policy and Aliyun SLS credentials in place.
"""

import os

import pytest

from agentuniverse.base.config.configer import Configer
from agentuniverse.base.util.logging.logging_config import (
    LoggingConfig,
    init_log_config,
)

# ``log_config.toml`` lives next to the agent unit tests and enables no
# extension module, which makes it a convenient fixture for the happy path.
_FIXTURE_CONFIG_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "agent", "log_config.toml"))

# Class level attributes that ``LoggingConfig`` mutates while parsing a file.
_CONFIG_ATTRS = tuple(LoggingConfig._MUTABLE_SETTING_NAMES)


@pytest.fixture()
def restore_logging_config():
    """Restore the class level state mutated by ``LoggingConfig``."""
    snapshot = {name: getattr(LoggingConfig, name) for name in _CONFIG_ATTRS}
    switch_snapshot = dict(LoggingConfig.log_extend_module_switch)
    yield
    for name, value in snapshot.items():
        setattr(LoggingConfig, name, value)
    LoggingConfig.log_extend_module_switch.clear()
    LoggingConfig.log_extend_module_switch.update(switch_snapshot)


# Documented defaults, spelled out here on purpose: the point of these tests is
# to pin the values down, so changing one has to be a deliberate edit in both
# ``LoggingConfig`` and this table.
_DOCUMENTED_DEFAULTS = {
    "log_level": "INFO",
    "log_path": None,
    "log_rotation": "10 MB",
    "log_retention": "3 days",
    "log_compression": "zip",
    "sls_endpoint": "",
    "sls_project": "",
    "sls_log_store": "",
    "access_key_id": "",
    "access_key_secret": "",
    "sls_log_queue_max_size": 1000,
    "sls_log_send_interval": 3.0,
}


def _assert_defaults_restored():
    """Every class level setting is back to its documented default."""
    assert set(_DOCUMENTED_DEFAULTS) == set(_CONFIG_ATTRS)
    for name, expected in _DOCUMENTED_DEFAULTS.items():
        actual = getattr(LoggingConfig, name)
        assert actual == expected, f"{name}: {actual!r} != {expected!r}"
    assert LoggingConfig.log_extend_module_switch
    for log_module in LoggingConfig.log_extend_module_list:
        assert LoggingConfig.log_extend_module_switch[log_module] is False


def _seed_non_default_settings():
    """Seed every mutable setting with a value that is *not* the default."""
    LoggingConfig.log_level = "TRACE"
    LoggingConfig.log_path = "./leaked_from_previous_config"
    LoggingConfig.log_rotation = "1 MB"
    LoggingConfig.log_retention = "99 days"
    LoggingConfig.log_compression = "tar"
    LoggingConfig.sls_endpoint = "leaked_endpoint"
    LoggingConfig.sls_project = "leaked_project"
    LoggingConfig.sls_log_store = "leaked_log_store"
    LoggingConfig.access_key_id = "leaked_key_id"
    LoggingConfig.access_key_secret = "leaked_key_secret"  # noqa: S105
    LoggingConfig.sls_log_queue_max_size = 17
    LoggingConfig.sls_log_send_interval = 42.0
    for log_module in LoggingConfig.log_extend_module_list:
        LoggingConfig.log_extend_module_switch[log_module] = True


def test_logging_config_without_path_resets_all_settings(restore_logging_config):
    """``LoggingConfig()`` restores the defaults, including the log level."""
    _seed_non_default_settings()

    LoggingConfig()

    # ``TRACE`` is not the default; the fallback must return to ``INFO``.
    assert LoggingConfig.log_level == "INFO"
    _assert_defaults_restored()


def test_logging_config_empty_path_resets_all_settings(restore_logging_config,
                                                       monkeypatch):
    """An empty path is treated like an omitted one, not parsed as a file."""
    _seed_non_default_settings()

    def fail_load_by_path(*args, **kwargs):
        raise AssertionError("an empty config path must not reach Configer")

    monkeypatch.setattr(Configer, "load_by_path", fail_load_by_path)

    LoggingConfig("")

    _assert_defaults_restored()


def test_logging_config_missing_file_resets_all_settings(restore_logging_config,
                                                         tmp_path):
    """A path pointing to a file that does not exist falls back to defaults."""
    _seed_non_default_settings()

    LoggingConfig(str(tmp_path / "not_created" / "log_config.toml"))

    _assert_defaults_restored()


def test_logging_config_invalid_toml_resets_all_settings(restore_logging_config,
                                                         tmp_path):
    """A corrupt toml file must not prevent the loggers from starting."""
    invalid_config = tmp_path / "invalid.toml"
    invalid_config.write_text("this is not valid toml", encoding="utf-8")
    _seed_non_default_settings()

    LoggingConfig(str(invalid_config))

    _assert_defaults_restored()


def test_logging_config_valid_file_overrides_defaults(restore_logging_config):
    """A valid file is still parsed and its values take effect."""
    assert os.path.exists(_FIXTURE_CONFIG_PATH), _FIXTURE_CONFIG_PATH

    LoggingConfig(_FIXTURE_CONFIG_PATH)

    assert LoggingConfig.log_level == "INFO"
    assert LoggingConfig.log_path == "./.test_log_dir"
    assert LoggingConfig.log_rotation == "100 MB"
    assert LoggingConfig.log_retention == "7 days"
    assert LoggingConfig.log_extend_module_switch["sls_log"] is False


def test_valid_config_then_no_path_resets_all_settings(restore_logging_config):
    """A fallback after a successful load must reset *all* settings."""
    LoggingConfig(_FIXTURE_CONFIG_PATH)
    assert LoggingConfig.log_path == "./.test_log_dir"
    assert LoggingConfig.log_rotation == "100 MB"
    assert LoggingConfig.log_retention == "7 days"

    LoggingConfig()

    _assert_defaults_restored()


def test_sls_config_then_no_path_resets_parsed_values(restore_logging_config,
                                                     tmp_path):
    """Values parsed from a real file are discarded by a later fallback."""
    config = tmp_path / "sls_log_config.toml"
    config.write_text(
        "[LOG_CONFIG.BASIC_CONFIG]\n"
        'log_level = "TRACE"\n'
        'log_path = "./parsed_log_dir"\n'
        'log_rotation = "1 MB"\n'
        'log_retention = "99 days"\n'
        'log_compression = "tar"\n'
        "[LOG_CONFIG.EXTEND_MODULE]\n"
        'sls_log = "True"\n'
        "[LOG_CONFIG.ALIYUN_SLS_CONFIG]\n"
        'sls_endpoint = "parsed_endpoint"\n'
        'sls_project = "parsed_project"\n'
        'sls_log_store = "parsed_log_store"\n'
        'access_key_id = "parsed_key_id"\n'
        'access_key_secret = "parsed_key_secret"\n'
        "sls_log_queue_max_size = 7\n"
        "sls_log_send_interval = 9.0\n",
        encoding="utf-8",
    )

    LoggingConfig(str(config))

    assert LoggingConfig.log_level == "TRACE"
    assert LoggingConfig.log_path == "./parsed_log_dir"
    assert LoggingConfig.log_extend_module_switch["sls_log"] is True
    assert LoggingConfig.sls_endpoint == "parsed_endpoint"
    assert LoggingConfig.access_key_secret == "parsed_key_secret"  # noqa: S105

    LoggingConfig()

    _assert_defaults_restored()


def test_init_log_config_without_path_resets_all_settings(
        restore_logging_config):
    """``init_log_config`` uses the same fallback path."""
    _seed_non_default_settings()

    init_log_config()

    _assert_defaults_restored()
