# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio

from agentuniverse.base.util.logging.log_sink.log_sink import LogSink
from agentuniverse.base.util.logging.logging_config import LoggingConfig
from agentuniverse.base.util.logging.logging_util import \
    is_in_coroutine_context
from loguru import logger


# @Time    : 2025/11/5 10:51
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: base_sls_log_sink.py


class BaseSLSLogSink(LogSink):
    """Loguru sink that ships records to Alibaba Cloud SLS.

    Subclasses implement :meth:`process_record` to serialize a single record.
    """

    def process_record(self, record):
        """Process a single log record.

        Args:
            record: The loguru log record to process.
        """
        raise NotImplementedError("Subclasses must implement process_record.")

    def filter(self, record):
        """Keep and process only records matching this sink's log type.

        Args:
            record: The loguru log record being filtered.

        Returns:
            bool: True when the record belongs to this sink's log type.
        """
        if not record['extra'].get('log_type') == self.log_type:
            return False
        self.process_record(record)
        return True

    def register_sink(self):
        """Register this sink with the loguru logger when SLS logging is enabled.

        Uses the async SLS sender inside a coroutine context and the sync
        sender otherwise; the loguru sink is added only once (sink_id == -1).
        """
        if LoggingConfig.log_extend_module_switch["sls_log"]:
            print(
                f"biz_logger_is_in_coroutine_context={is_in_coroutine_context()}")
            if is_in_coroutine_context():
                from agentuniverse_extension.logger.sls_sink import \
                    AsyncSlsSender, AsyncSlsSink
                sls_sender = AsyncSlsSender(LoggingConfig.sls_project,
                                            LoggingConfig.sls_log_store,
                                            LoggingConfig.sls_endpoint,
                                            LoggingConfig.access_key_id,
                                            LoggingConfig.access_key_secret,
                                            LoggingConfig.sls_log_queue_max_size,
                                            LoggingConfig.sls_log_send_interval)
                loop = asyncio.get_event_loop_policy().get_event_loop()
                loop.create_task(sls_sender.start())

                if self.sink_id == -1:
                    self.sink_id = logger.add(
                        sink=AsyncSlsSink(sls_sender),
                        format=LoggingConfig.log_format,
                        filter=self.filter,
                        level=LoggingConfig.log_level,
                        enqueue=False
                    )
            else:
                from agentuniverse_extension.logger.sls_sink import SlsSink, \
                    SlsSender
                sls_sender = SlsSender(LoggingConfig.sls_project,
                                       LoggingConfig.sls_log_store,
                                       LoggingConfig.sls_endpoint,
                                       LoggingConfig.access_key_id,
                                       LoggingConfig.access_key_secret,
                                       LoggingConfig.sls_log_queue_max_size,
                                       LoggingConfig.sls_log_send_interval)
                sls_sender.start_batch_send_thread()

                if self.sink_id == -1:
                    self.sink_id = logger.add(
                        sink=SlsSink(sls_sender),
                        format=LoggingConfig.log_format,
                        filter=self.filter,
                        level=LoggingConfig.log_level,
                        enqueue=self.enqueue
                    )

