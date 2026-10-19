# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/9 18:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: log_sink.py
from typing import Optional
from loguru import logger

from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.util.logging.logging_config import LoggingConfig
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger



class LogSink(ComponentBase):
    """The basic class for log sink.
    """

    component_type: ComponentEnum = ComponentEnum.LOG_SINK
    name: Optional[str] = None
    description: Optional[str] = None
    level: str = "INFO"
    format: str = LoggingConfig.log_format
    sink_id: int = -1
    log_type: LogTypeEnum = LogTypeEnum.default
    enqueue: bool = True

    class Config:
        """Pydantic model configuration for this component, allowing arbitrary types.
        """
        arbitrary_types_allowed = True

    def get_inheritance_depth(self):
        """
        return the depth to base Logger
        """
        return self.__class__.__mro__.index(LogSink)

    def __call__(self, message):
        """Invoke the sink on a log message.

        Args:
            message: The loguru message whose ``record`` is dispatched to process_record.
        """
        self.process_record(message.record)

    def process_record(self, record):
        """Process a single log record.

        Args:
            record: The loguru log record to process.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement process_record.")

    def filter(self, record):
        """Filter log records by their log type.

        Args:
            record: The loguru log record to inspect.

        Returns:
            True if the record log type matches this sink log type, False otherwise.
        """
        if not record['extra'].get('log_type') == self.log_type:
            return False
        return True

    def register_sink(self):
        """Register this sink with the loguru logger when it has not been registered yet (sink_id is -1).
        """
        if self.sink_id == -1:
            self.sink_id = logger.add(
                self,
                level=self.level,
                format=self.format,
                filter=self.filter,
                enqueue=self.enqueue
            )

    def initialize_by_component_configer(self,
                                          log_sink_configer: ComponentConfiger) -> 'LogSink':
        """Initialize the log sink from a component configer.

        Args:
            log_sink_configer(ComponentConfiger): The configer containing the sink settings.

        Returns:
            LogSink: The initialized sink instance.
        """
        self.name = log_sink_configer.name
        self.description = log_sink_configer.description
        if hasattr(log_sink_configer, "level"):
            self.level = log_sink_configer.level
        if hasattr(log_sink_configer, "format"):
            self.format = log_sink_configer.format
        if hasattr(log_sink_configer, "enqueue"):
            self.enqueue = log_sink_configer.enqueue

        self._initialize_by_component_configer(log_sink_configer)

        self.register_sink()
        return self
