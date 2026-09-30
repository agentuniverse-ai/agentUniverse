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
    """Log sink that records tool invocation events to a log file."""

    log_type: LogTypeEnum = LogTypeEnum.tool_invocation

    def process_record(self, record):
        """Fill the log record message with the generated tool invocation log.

        Args:
            record: the loguru log record being processed.
        """
        record["message"] = self.generate_log(
            cost_time=record['extra'].get('cost_time'),
            tool_output=record['extra'].get('tool_output')
        )

    def generate_log(self, cost_time: float, tool_output) -> str:
        """Generate the log text for a tool invocation event.

        Args:
            cost_time (float): the elapsed time of the tool invocation.
            tool_output: the output produced by the tool.

        Returns:
            str: the invocation chain prefix followed by the cost and output.
        """
        log_str = f" Tool cost {cost_time:.2f} seconds"
        return Monitor.get_invocation_chain_str() + log_str + f" Tool output is {tool_output}"