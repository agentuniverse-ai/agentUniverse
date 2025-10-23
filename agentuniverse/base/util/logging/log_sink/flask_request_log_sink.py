# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/9 18:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: flask_request_log_sink.py

from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class FlaskRequestLogSink(BaseFileLogSink):
    log_type: LogTypeEnum = LogTypeEnum.flask_request

    def process_record(self, record):
        record["message"] = self.generate_log(flask_request=record["extra"]["flask_request"])
        record["extra"].pop("flask_request", None)

    def generate_log(self, flask_request) -> str:
        pass
