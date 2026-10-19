# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: custom_flask_request_sink.py

from agentuniverse.base.util.logging.log_sink.flask_request_log_sink import \
    FlaskRequestLogSink


class CustomFlaskRequestSink(FlaskRequestLogSink):
    """Log sink that formats a Flask request into a single log line.

    The method, path, headers and optional body are collected so each
    incoming request can be traced in the log output.
    """

    def generate_log(self, flask_request) -> str:
        """Render a Flask request object into a log message string.

        Args:
            flask_request: The Flask request whose method, path, headers
                and body should be logged.

        Returns:
            The formatted log line for the request.
        """
        log_string = (f"Request: {flask_request.method} {flask_request.path} "
                      f"Headers: {dict(flask_request.headers)}")
        if flask_request.data:
            try:
                log_string += f" Body: {flask_request.get_data(as_text=True)}"
            except Exception as e:
                pass

        return log_string
