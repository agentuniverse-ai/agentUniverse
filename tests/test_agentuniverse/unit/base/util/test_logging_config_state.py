from agentuniverse.base.util.logging.logging_config import LoggingConfig


def test_logging_config_does_not_leak_custom_values_to_next_instance(tmp_path):
    config_path = tmp_path / "logging.toml"
    config_path.write_text(
        "[LOG_CONFIG.BASIC_CONFIG]\n"
        "log_level = 'DEBUG'\n"
        "log_path = '/tmp/custom-au-logs'\n",
        encoding="utf-8",
    )

    LoggingConfig(str(config_path))
    assert LoggingConfig.log_level == "DEBUG"
    assert LoggingConfig.log_path == "/tmp/custom-au-logs"

    LoggingConfig()
    assert LoggingConfig.log_level == "INFO"
    assert LoggingConfig.log_path is None
    assert LoggingConfig.log_rotation == "10 MB"
    assert LoggingConfig.sls_log_send_interval == 3.0
