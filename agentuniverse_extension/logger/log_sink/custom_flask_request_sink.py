# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/10 17:07
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: custom_flask_request_sink.py
from agentuniverse.base.util.logging.log_sink.flask_request_log_sink import \
    FlaskRequestLogSink


class CustomFlaskRequestSink(FlaskRequestLogSink):
    """Custom flask request log sink that formats the incoming request into a log string.
    """
    def generate_log(self, flask_request) -> str:
        """Format the flask request method, path, headers and body into a log string.

        Args:
            flask_request: The flask request object.

        Returns:
            str: The formatted request log string.
        """
        log_string = (f"Request: {flask_request.method} {flask_request.path} "
                      f"Headers: {dict(flask_request.headers)}")
        if flask_request.data:
            try:
                log_string += f" Body: {flask_request.get_data(as_text=True)}"
            except Exception as e:
                pass

        return log_string
