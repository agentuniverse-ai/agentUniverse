# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 15:50
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: test_logging_config.py

import os
import time

import loguru
import pytest

from agentuniverse.base.config.configer import Configer
from agentuniverse.base.util.logging.logging_config import (
    LoggingConfig,
    init_log_config,
)
from agentuniverse.base.util.logging import logging_util
from agentuniverse.base.util.logging.logging_util import (
    LOGGER,
    LOG_FILE_PREFIX,
    init_loggers,
)

# ``log_config.toml`` lives next to the agent unit tests and enables no
# extension module, which makes it a convenient fixture for the happy path.
_FIXTURE_CONFIG_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "agent", "log_config.toml"))

# Class level attributes that ``LoggingConfig`` mutates while parsing a file.
_CONFIG_ATTRS = (
    "log_level",
    "log_path",
    "log_rotation",
    "log_retention",
    "log_compression",
    "sls_endpoint",
    "sls_project",
    "sls_log_store",
    "access_key_id",
    "access_key_secret",
    "sls_log_queue_max_size",
    "sls_log_send_interval",
)


@pytest.fixture()
def restore_logging_config():
    """Restore the class level state mutated by ``LoggingConfig``.

    ``LoggingConfig`` keeps its parsed values on the class itself, so a test
    that loads a configuration file would otherwise leak state (log level,
    log path, extension switches, ...) into every following test.
    """
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


def _assert_all_extend_modules_disabled():
    """Every optional extension module has to be switched off."""
    assert LoggingConfig.log_extend_module_switch
    for log_module in LoggingConfig.log_extend_module_list:
        assert LoggingConfig.log_extend_module_switch[log_module] is False


def _assert_defaults_restored():
    """Every class level setting is back to its documented default."""
    for name, expected in _DOCUMENTED_DEFAULTS.items():
        actual = getattr(LoggingConfig, name)
        assert actual == expected, f"{name}: {actual!r} != {expected!r}"
    _assert_all_extend_modules_disabled()


def _seed_non_default_settings():
    """Seed every mutable setting with a value that is *not* the default.

    A fallback only proves it resets the class level state if there is
    something to reset, so each fallback test starts from a fully populated -
    and completely wrong - configuration.
    """
    LoggingConfig.log_level = "TRACE"
    LoggingConfig.log_path = "./leaked_from_previous_config"
    LoggingConfig.log_rotation = "1 MB"
    LoggingConfig.log_retention = "99 days"
    LoggingConfig.log_compression = "tar"
    LoggingConfig.sls_endpoint = "leaked_endpoint"
    LoggingConfig.sls_project = "leaked_project"
    LoggingConfig.sls_log_store = "leaked_log_store"
    LoggingConfig.access_key_id = "leaked_key_id"
    LoggingConfig.access_key_secret = "leaked_key_secret"
    LoggingConfig.sls_log_queue_max_size = 17
    LoggingConfig.sls_log_send_interval = 42.0
    for log_module in LoggingConfig.log_extend_module_list:
        LoggingConfig.log_extend_module_switch[log_module] = True


def test_logging_config_without_path_uses_defaults(restore_logging_config):
    """``LoggingConfig()`` must not raise when no path is supplied.

    Regression test for the ``AttributeError: 'NoneType' object has no
    attribute 'split'`` that ``Configer.load_by_path(None)`` used to raise.
    """
    _seed_non_default_settings()

    LoggingConfig()

    _assert_defaults_restored()


def test_logging_config_empty_path_uses_defaults(restore_logging_config):
    """An empty path is equivalent to no path at all."""
    _seed_non_default_settings()

    LoggingConfig("")

    _assert_defaults_restored()


def test_logging_config_missing_file_uses_defaults(restore_logging_config,
                                                   tmp_path):
    """A path pointing to a file that does not exist falls back to defaults."""
    _seed_non_default_settings()

    LoggingConfig(str(tmp_path / "not_created" / "log_config.toml"))

    _assert_defaults_restored()


def test_logging_config_invalid_toml_uses_defaults(restore_logging_config,
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


def test_logging_config_valid_config_then_no_path_resets_all_settings(
        restore_logging_config):
    """A fallback after a successful load must reset *all* settings.

    ``LoggingConfig`` stores its parsed values on the class, so a fallback that
    only switched the extension modules off kept the previous file's code
    ``log_path``, level, rotation, retention, compression and Aliyun SLS
    credentials.  ``LoggingConfig()`` - and therefore the ``init_loggers()``
    call that follows - silently logged to the old directory with the old
    policy instead of the documented defaults.
    """
    LoggingConfig(_FIXTURE_CONFIG_PATH)
    assert LoggingConfig.log_path == "./.test_log_dir"
    assert LoggingConfig.log_rotation == "100 MB"
    assert LoggingConfig.log_retention == "7 days"

    LoggingConfig()

    _assert_defaults_restored()


def test_init_log_config_without_path(restore_logging_config):
    """``init_log_config`` keeps working without an explicit config path."""
    init_log_config()

    assert "sls_log" in LoggingConfig.log_extend_module_switch
    assert LoggingConfig.log_extend_module_switch["sls_log"] is False


def test_init_loggers_without_path(restore_logging_config, tmp_path,
                                   monkeypatch):
    """``init_loggers()`` installs the default handlers without a config file.

    With no config file the documented default applies: the file handlers are
    registered under ``<project root>/logs``.  The project root is patched to a
    temporary directory instead of pre-seeding ``LoggingConfig.log_path``,
    because a fallback now deliberately clears any leaked path.
    """
    log_dir = tmp_path / "logs"
    monkeypatch.setattr(logging_util, "get_project_root_path",
                        lambda: tmp_path)

    init_loggers()
    try:
        LOGGER.info("default config info log")
        LOGGER.error("default config error log")
        # The handlers use ``enqueue=True``, give the sink thread a moment to
        # flush the queued records before reading the files back.
        time.sleep(0.3)

        all_log_file = log_dir / f"{LOG_FILE_PREFIX}_all.log"
        error_log_file = log_dir / f"{LOG_FILE_PREFIX}_error.log"
        assert all_log_file.exists()
        assert error_log_file.exists()

        all_log_content = all_log_file.read_text(encoding="utf-8")
        assert "default config info log" in all_log_content
        assert "default config error log" in all_log_content
        assert "default config error log" in error_log_file.read_text(
            encoding="utf-8")
    finally:
        # Drop the handlers created above so that later tests are not affected
        # by the temporary log directory used here.
        loguru.logger.remove()


def test_configer_load_by_path_rejects_none():
    """A missing path raises a descriptive error instead of AttributeError."""
    with pytest.raises(ValueError, match="non-empty string"):
        Configer().load_by_path(None)


def test_configer_load_by_path_rejects_empty_string():
    with pytest.raises(ValueError, match="non-empty string"):
        Configer().load_by_path("")


def test_configer_load_by_path_rejects_blank_string():
    with pytest.raises(ValueError, match="non-empty string"):
        Configer().load_by_path("   ")


def test_configer_load_by_path_rejects_non_string():
    with pytest.raises(ValueError, match="non-empty string"):
        Configer().load_by_path(123)


def test_configer_load_by_path_rejects_unsupported_format(tmp_path):
    unsupported_config = tmp_path / "log_config.ini"
    unsupported_config.write_text("[LOG_CONFIG]", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file format"):
        Configer().load_by_path(str(unsupported_config))


def test_configer_load_by_path_still_loads_valid_toml():
    """The new guard must not break loading a well formed configuration."""
    configer = Configer().load_by_path(_FIXTURE_CONFIG_PATH)

    assert configer.value["LOG_CONFIG"]["BASIC_CONFIG"]["log_level"] == "INFO"
