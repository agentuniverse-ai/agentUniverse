# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/9 18:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: flask_request_log_sink.py

from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class FlaskRequestLogSink(BaseFileLogSink):
    """File-based log sink dedicated to flask request records filtered by the flask_request log type.
    """
    log_type: LogTypeEnum = LogTypeEnum.flask_request


    def process_record(self, record):
        """Generate the sink message from the flask_request extra field and remove the field afterwards.

        Args:
            record: The loguru log record to process.
        """
        record["message"] = self.generate_log(
            flask_request=record['extra']['flask_request']
        )
        record['extra'].pop('flask_request', None)


    def generate_log(self, flask_request) -> str:
        """Placeholder generation hook that receives the flask request.

        Args:
            flask_request: The flask request object.
        """
        pass
