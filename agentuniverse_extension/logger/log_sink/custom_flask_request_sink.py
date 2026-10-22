# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/10 17:07
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: custom_flask_request_sink.py
from agentuniverse.base.util.logging.log_sink.flask_request_log_sink import \
    FlaskRequestLogSink


class CustomFlaskRequestSink(FlaskRequestLogSink):
    def generate_log(self, flask_request) -> str:
        # A route template preserves useful endpoint information without
        # logging user-controlled path segments, query strings, or credentials.
        route = getattr(getattr(flask_request, "url_rule", None), "rule", None)
        return f"Request: {flask_request.method} {route or '[unmatched route]'}"
