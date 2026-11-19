
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/10 17:07
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: custom_flask_response_sink.py
from agentuniverse.base.util.logging.log_sink.flask_response_log_sink import FlaskResponseLogSink


class CustomFlaskResponseSink(FlaskResponseLogSink):
    """Custom flask response log sink that formats the response and its duration into a log string.
    """
    def generate_log(self, flask_response, elapsed_time) -> str:
        """Format the flask response and elapsed time into a log string.

        Args:
            flask_response: The flask response object or string.
            elapsed_time: The response elapsed time in seconds.

        Returns:
            str: The formatted response log string.
        """
        if isinstance(flask_response, str):
            return f"Response: [string response] Duration: {elapsed_time:.3f}s"
        return (f"Response: {flask_response.status_code} {flask_response.content_type} "
                f"Duration: {elapsed_time:.3f}s")
