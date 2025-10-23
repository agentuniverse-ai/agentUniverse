# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/11 16:14
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: general_logger.py

from abc import ABC, abstractmethod
import json
from typing import Literal
import loguru

from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.tracing.au_trace_manager import AuTraceManager

LOG_LEVEL = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


def get_context_prefix() -> str:
    """Get a dict contains log prefix info from current context and format it
    to a log prefix string."""
    trace_dict = AuTraceManager().get_trace_dict()
    log_context = FrameworkContextManager().get_context("LOG_CONTEXT")
    if log_context and isinstance(log_context, dict):
        trace_dict.update(log_context)
    if trace_dict:
        json_str = json.dumps(trace_dict)
        format_context_prefix = "[" + json_str[1:-1] + "]"
        return format_context_prefix
    else:
        return "[default]"


def _get_source_filter(source: str) -> callable:
    """Create a function to filter out specific messages that need to be
    recorded in target loguru sink.

    Args:
        source (`str`):
            Name of the log source, only message from the same source will be
            recorded.

    Returns:
        A callable filter func returns bool value indicating whether the
        message should be logged.
    """

    def source_filter(record) -> bool:
        return record["extra"].get("log_type") == LogTypeEnum.default and record["extra"].get("source") == source

    return source_filter


class Logger(ABC):
    """The basic class of all logger, define all level log functions."""

    def get_inheritance_depth(self):
        """
        return the depth to base Logger
        """
        return self.__class__.__mro__.index(Logger)

    @property
    def _logger(self):
        """Logger field"""
        return loguru.logger

    @abstractmethod
    def warn(self, msg, *args, **kwargs):
        """Log warn level message."""
        raise NotImplementedError

    @abstractmethod
    def info(self, msg, *args, **kwargs):
        """Log info level message."""
        raise NotImplementedError

    @abstractmethod
    def error(self, msg, *args, **kwargs):
        """Log error level message."""
        raise NotImplementedError

    @abstractmethod
    def critical(self, msg, *args, **kwargs):
        """Log critical level message."""
        raise NotImplementedError

    @abstractmethod
    def trace(self, msg, *args, **kwargs):
        """Log trace level message."""
        raise NotImplementedError

    @abstractmethod
    def debug(self, msg, *args, **kwargs):
        """Log debug level message."""
        raise NotImplementedError


class GeneralLogger(Logger):
    """General logger class, create a logger with config from config file for
    separate module."""

    def __init__(
        self,
        module_name: str,
        log_path: str,
        log_format: str,
        log_rotation: str,
        log_retention: str,
        log_level: LOG_LEVEL = "INFO",
        add_handler: bool = True,
    ):
        """Create a new logger instance used by a specific module.

        Args:
            module_name (`str`):
                Name of the module, also used in log file name.
            log_path (`str`):
                Path of the log file.
            log_format (`str`):
                Format of recorded logs.
            log_rotation (`str`):
                Specifies the log rotation policy, controlling when a new log
                file is created. It can be a time period (e.g., "1 week",
                "10 days"), a file size (e.g., "100 MB"), or a function
                returning True when rotation should occur.
            log_retention (`str`):
                Specifies the duration to keep old log files. It can be a time
                span (e.g., "30 days") or a function to filter the files to be
                retained. Files outside this policy are purged.
            log_level (`LOG_LEVEL`, defaults to `"INFO"`):
                Log level, values should be in LOG_LEVEL.
            add_handler (`bool`, defaults to `True`):
                Whether to add a new loguru handler only used to handle log
                recorded by this instance.
        """
        self.module_name = module_name
        self.log_path = log_path
        self.log_format = log_format
        self.log_rotation = log_rotation
        self.log_retention = log_retention
        if add_handler:
            self._add_handler(log_level)

    def update_properties(self, **kwargs):
        """Update logger properties."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"{self.__class__.__name__} has no attribute '{key}'")

    def warn(self, msg, *args, **kwargs):
        self._logger.opt(depth=self.get_inheritance_depth()).bind(
            log_type=LogTypeEnum.default, source=self.module_name, context_prefix=get_context_prefix()
        ).warning(msg, *args, **kwargs)

    async def awarn(self, msg, *args, **kwargs):
        self.warn(msg, *args, **kwargs)
        await self._logger.complete()

    def info(self, msg, *args, **kwargs):
        self._logger.opt(depth=self.get_inheritance_depth()).bind(
            log_type=LogTypeEnum.default, source=self.module_name, context_prefix=get_context_prefix()
        ).info(msg, *args, **kwargs)

    async def ainfo(self, msg, *args, **kwargs):
        self.info(msg, *args, **kwargs)
        await self._logger.complete()

    def error(self, msg, *args, **kwargs):
        self._logger.opt(depth=self.get_inheritance_depth()).bind(
            log_type=LogTypeEnum.default, source=self.module_name, context_prefix=get_context_prefix()
        ).error(msg, *args, **kwargs)

    async def aerror(self, msg, *args, **kwargs):
        self.error(msg, *args, **kwargs)
        await self._logger.complete()

    def critical(self, msg, *args, **kwargs):
        self._logger.opt(depth=self.get_inheritance_depth()).bind(
            log_type=LogTypeEnum.default, source=self.module_name, context_prefix=get_context_prefix()
        ).critical(msg, *args, **kwargs)

    async def acritical(self, msg, *args, **kwargs):
        self.error(msg, *args, **kwargs)
        await self._logger.complete()

    def trace(self, msg, *args, **kwargs):
        self._logger.opt(depth=self.get_inheritance_depth()).bind(
            log_type=LogTypeEnum.default, source=self.module_name, context_prefix=get_context_prefix()
        ).trace(msg, *args, **kwargs)

    async def atrace(self, msg, *args, **kwargs):
        self.trace(msg, *args, **kwargs)
        await self._logger.complete()

    def debug(self, msg, *args, **kwargs):
        self._logger.opt(depth=self.get_inheritance_depth()).bind(
            log_type=LogTypeEnum.default, source=self.module_name, context_prefix=get_context_prefix()
        ).debug(msg, *args, **kwargs)

    async def adebug(self, msg, *args, **kwargs):
        self.debug(msg, *args, **kwargs)
        await self._logger.complete()

    def _add_handler(self, log_level: LOG_LEVEL = "INFO"):
        """Add a new loguru log handler, use instance module name to filter out
        message recorded by this instance.

        Args:
            log_level (`str`, defaults to `"INFO"`):
                Log level, values should be in LOG_LEVEL.
        """
        self._logger.add(
            sink=self.log_path,
            level=log_level,
            format=self.log_format,
            rotation=self.log_rotation,
            retention=self.log_retention,
            compression="zip",
            encoding="utf-8",
            enqueue=True,
            filter=_get_source_filter(self.module_name),
        )
