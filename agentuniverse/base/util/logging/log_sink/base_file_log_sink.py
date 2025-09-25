# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/9 18:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: base_file_log_sink.py
from loguru import logger

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.logging.log_sink.log_sink import LogSink
from agentuniverse.base.util.logging.logging_config import LoggingConfig
from agentuniverse.base.util.logging.logging_util import _get_log_file_path


class BaseFileLogSink(LogSink):
    file_prefix: str = None
    log_rotation: str = LoggingConfig.log_rotation
    log_retention: str = LoggingConfig.log_retention
    compression: str = None

    def process_record(self, record):
        raise NotImplementedError("Subclasses must implement process_record.")

    def filter(self, record):
        if not record["extra"].get("log_type") == self.log_type:
            return False
        self.process_record(record)
        return True

    def register_sink(self):
        if self.sink_id == -1:
            self.sink_id = logger.add(
                sink=_get_log_file_path(self.file_prefix),
                level=self.level,
                format=self.format,
                filter=self.filter,
                rotation=self.log_rotation,
                retention=self.log_retention,
                compression=self.compression,
                encoding="utf-8",
                enqueue=self.enqueue,
            )

    def _initialize_by_component_configer(self, log_sink_configer: ComponentConfiger) -> "LogSink":
        if hasattr(log_sink_configer, "file_prefix"):
            self.file_prefix = log_sink_configer.file_prefix
        if hasattr(log_sink_configer, "log_rotation"):
            self.log_rotation = log_sink_configer.log_rotation
        if hasattr(log_sink_configer, "log_retention"):
            self.log_retention = log_sink_configer.log_retention
        if hasattr(log_sink_configer, "compression"):
            self.compression = log_sink_configer.compression
        return self
