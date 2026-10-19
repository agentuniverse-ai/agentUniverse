# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/9 18:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: flask_response_log_sink.py

from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class FlaskResponseLogSink(BaseFileLogSink):
    """Log sink that records Flask response events to a log file."""

    log_type: LogTypeEnum = LogTypeEnum.flask_response

      
    def process_record(self, record):
        """Fill the log record message with the generated Flask response log.

        The flask_response entry is removed from the record extra fields after
        the message is generated.

        Args:
            record: the loguru log record being processed.
        """
        record["message"] = self.generate_log(
            flask_response=record['extra'].get('flask_response'),
            elapsed_time=record['extra']['elapsed_time']
        )
        record['extra'].pop('flask_response', None)

    def generate_log(self, flask_response, elapsed_time) -> str:
        """Generate the log text for a Flask response event.

        The base implementation is a placeholder; concrete subclasses override
        this method to build the response log line.

        Args:
            flask_response: the Flask response object or text being logged.
            elapsed_time: the elapsed time of the request in seconds.
        """
        pass
