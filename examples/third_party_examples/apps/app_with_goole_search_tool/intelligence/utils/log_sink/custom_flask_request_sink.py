# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: custom_flask_request_sink.py

from agentuniverse.base.util.logging.log_sink.flask_request_log_sink import \
    FlaskRequestLogSink


class CustomFlaskRequestSink(FlaskRequestLogSink):
    """Custom log sink that formats a Flask request into a log line."""

    def generate_log(self, flask_request) -> str:
        """Build a log string describing a Flask request.

        Args:
            flask_request: The Flask request object.

        Returns:
            str: A formatted log line with the request method, path, headers
            and, when available, the request body.
        """
        log_string = (f"Request: {flask_request.method} {flask_request.path} "
                      f"Headers: {dict(flask_request.headers)}")
        if flask_request.data:
            try:
                log_string += f" Body: {flask_request.get_data(as_text=True)}"
            except Exception as e:
                pass

        return log_string
