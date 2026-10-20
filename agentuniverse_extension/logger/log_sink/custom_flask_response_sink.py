
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/10 17:07
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: custom_flask_response_sink.py
from agentuniverse.base.util.logging.log_sink.flask_response_log_sink import FlaskResponseLogSink


class CustomFlaskResponseSink(FlaskResponseLogSink):
    def generate_log(self, flask_response, elapsed_time) -> str:
        if isinstance(flask_response, str):
            return f"Response: [string response] Duration: {elapsed_time:.3f}s"
        return (f"Response: {flask_response.status_code} {flask_response.content_type} "
                f"Duration: {elapsed_time:.3f}s")
