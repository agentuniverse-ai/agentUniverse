
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