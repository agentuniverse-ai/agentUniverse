# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/12 15:48
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: logging_util.py

import os
import sys
from typing import Optional
from pathlib import Path
from typing_extensions import deprecated

import loguru

from .general_logger import GeneralLogger, LOG_LEVEL
from .logging_config import LoggingConfig, init_log_config
from ..system_util import get_project_root_path
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum

_module_logger_dict = {}
STANDARD_LOG_SUFFIX = 'all'
ERROR_LOG_SUFFIX = 'error'
LOG_FILE_PREFIX = "au"
LOG_SUB_DIR = 'logs'
LOGGER = GeneralLogger(STANDARD_LOG_SUFFIX, "", "", "", "", add_handler=False)


def _standard_filter(record):
    return record["extra"].get('log_type') == LogTypeEnum.default


def _get_log_file_path(log_suffix: str) -> str:
    """Get full log file path by contacting log save path and log file name.
    If log path is not specified, create a subdir to save logs under project
    root dir.

    Args:
        log_suffix (`str`):
            Suffix of the log file name.

    Returns:
        Full log file path string.
    """
    if LoggingConfig.log_path:
        project_log_dir = Path(LoggingConfig.log_path)
    else:
        project_path = get_project_root_path()
        project_log_dir = project_path / LOG_SUB_DIR
    project_log_filename = f'{LOG_FILE_PREFIX}_{log_suffix}.log'
    project_log_path = project_log_dir / project_log_filename
    return str(project_log_path)


def _add_standard_logger():
    """Add a standard loguru handler."""

    LOGGER.update_properties(
        log_path=_get_log_file_path(STANDARD_LOG_SUFFIX),
        log_format=LoggingConfig.log_format,
        log_rotation=LoggingConfig.log_rotation,
        log_retention=LoggingConfig.log_retention)
    loguru.logger.add(
        sink=_get_log_file_path(STANDARD_LOG_SUFFIX),
        level=LoggingConfig.log_level,
        format=LoggingConfig.log_format,
        filter=_standard_filter,
        rotation=LoggingConfig.log_rotation,
        retention=LoggingConfig.log_retention,
        compression=LoggingConfig.log_compression if LoggingConfig.log_compression else None,
        encoding="utf-8",
        enqueue=True
    )


def _add_std_out_handler():
    """Add a loguru handler send logs to std out."""
    loguru.logger.add(
        sink=sys.stdout,
        level=LoggingConfig.log_level,
        format=LoggingConfig.log_format,
        filter=_standard_filter,
        enqueue=True
    )


def _add_error_log_handler():
    """Add a loguru handler to record all error level message."""
    loguru.logger.add(
        sink=_get_log_file_path(ERROR_LOG_SUFFIX),
        level="ERROR",
        format=LoggingConfig.log_format,
        rotation=LoggingConfig.log_rotation,
        retention=LoggingConfig.log_retention,
        compression='zip',
        encoding="utf-8",
        enqueue=True,
    )


def _add_sls_log_handler():
    """Add a handler to record all """
    from agentuniverse_extension.logger.sls_sink import SlsSink, SlsSender
    sls_sender = SlsSender(LoggingConfig.sls_project,
                           LoggingConfig.sls_log_store,
                           LoggingConfig.sls_endpoint,
                           LoggingConfig.access_key_id,
                           LoggingConfig.access_key_secret,
                           LoggingConfig.sls_log_queue_max_size,
                           LoggingConfig.sls_log_send_interval)
    sls_sender.start_batch_send_thread()

    def _sls_filter(record):
        return record["extra"].get('log_type') == LogTypeEnum.default or record["extra"].get('log_type') == LogTypeEnum.sls
    loguru.logger.add(
        sink=SlsSink(sls_sender),
        format=LoggingConfig.log_format,
        filter=_sls_filter,
        level=LoggingConfig.log_level,
        enqueue=True
    )


def get_module_logger(module_name: str,
                      log_level: Optional[LOG_LEVEL] = None) -> GeneralLogger:
    """Get a module dedicated logger.

    Args:
        module_name (`str`):
            Name of the module, also used in log file name.
        log_level (`LOG_LEVEL`, defaults to `None`):
            Log level, values should be in LOG_LEVEL. If log_level is none,
            use log level in logging config as default value.

    Returns:
        Return a logger used to record specify module log.
    """
    if module_name in _module_logger_dict:
        return _module_logger_dict.get(module_name)
    if not log_level:
        log_level = LoggingConfig.log_level
    new_logger = GeneralLogger(module_name,
                               _get_log_file_path(module_name),
                               LoggingConfig.log_format,
                               LoggingConfig.log_rotation,
                               LoggingConfig.log_retention,
                               log_level)
    _module_logger_dict[module_name] = new_logger
    return new_logger


@deprecated('Deleted in future, use LogSink to register a new sink instead.')
def add_sink(sink, log_level: Optional[LOG_LEVEL] = None) -> bool:
    """Validate the given sink and add it to the loguru logger if valid.

    Args:
        sink :
            A filepath (str), file object, object with `write` method,
            or callable function with only one param named message.
        log_level (`LOG_LEVEL`, defaults to `None`):
            Log level, values should be in LOG_LEVEL. If log_level is none,
            use log level in logging config as default value.
    Return:
        True if the sink was successfully added, False otherwise.
    """
    valid_sink = False

    if isinstance(sink, str):
        # If the sink is a string, assume it's a file path
        valid_sink = True

    elif hasattr(sink, 'write') and callable(getattr(sink, 'write')):
        # An object with a write method (like file objects or class instances)
        valid_sink = True

    elif callable(sink):
        # A callable object, such as a function or a lambda
        valid_sink = True

    if valid_sink:
        try:
            loguru.logger.add(
                sink=sink,
                format=LoggingConfig.log_format,
                level=log_level or LoggingConfig.log_level,
                enqueue=True
            )
            return True
        except Exception as e:
            print(f"Failed to add log sink due to error: {e}")

    print(
        f"The provided sink type {type(sink)} is not supported "
        f"or caused an error.")
    return False


def init_loggers(config_path: Optional[str] = None):
    """Parse config and initialize all loggers and handlers.

    Args:
        config_path (`str`):
            Path of the log config file.
    """
    init_log_config(config_path)
    loguru.logger.remove()
    _add_std_out_handler()
    _add_error_log_handler()
    if LoggingConfig.log_extend_module_switch["sls_log"]:
        _add_sls_log_handler()
    _add_standard_logger()
