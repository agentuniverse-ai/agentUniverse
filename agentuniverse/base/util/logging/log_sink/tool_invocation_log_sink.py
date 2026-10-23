# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/17 17:13
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: tool_invocation_log_sink.py

from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.util.monitor.monitor import Monitor


class ToolInvocationLogSink(BaseFileLogSink):
    log_type: LogTypeEnum = LogTypeEnum.tool_invocation

    def process_record(self, record):
        record["message"] = self.generate_log(
            cost_time=record['extra'].get('cost_time'),
            tool_output=record['extra'].get('tool_output')
        )

    def generate_log(self, cost_time: float, tool_output) -> str:
        log_str = f" Tool cost {cost_time:.2f} seconds"
        return Monitor.get_invocation_chain_str() + log_str + f" Tool output is {tool_output}"