
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: custom_flask_response_sink.py

from agentuniverse.base.util.logging.log_sink.flask_response_log_sink import FlaskResponseLogSink


class CustomFlaskResponseSink(FlaskResponseLogSink):
    """Log sink that formats a Flask response into a single log line.

    The response is rendered together with its elapsed time so that every
    request/response cycle can be traced in the log output.
    """

    def generate_log(self, flask_response, elapsed_time) -> str:
        """Render a Flask response object into a log message string.

        Args:
            flask_response: The Flask response, either as a plain string body
                or a full response object with status code and content type.
            elapsed_time: The processing duration of the request in seconds.

        Returns:
            The formatted log line for the response.
        """
        if isinstance(flask_response, str):
            response_str = (f"Response: {flask_response} "
                            f"Duration: {elapsed_time:.3f}s")
        else:
            response_str = (f"Response: {flask_response.status_code} {flask_response.content_type} "
                            f"Duration: {elapsed_time:.3f}s")


            if flask_response.data:  # 记录响应体
                try:
                    response_str += f' Data:{flask_response.get_data(as_text=True)}'
                except Exception as e:
                    pass
        return response_str