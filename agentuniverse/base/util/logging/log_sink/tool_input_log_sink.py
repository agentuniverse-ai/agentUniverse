# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/17 16:33
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: tool_input_log_sink.py

from typing import Union

from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.util.monitor.monitor import Monitor


class ToolInputLogSink(BaseFileLogSink):
    """Log sink that records the tool input of a tool invocation to a log file."""

    log_type: LogTypeEnum = LogTypeEnum.tool_input

    def process_record(self, record):
        """Fill the log record message with the generated tool-input log.

        Args:
            record: the loguru log record being processed.
        """
        record["message"] = self.generate_log(
            tool_input=record['extra'].get('tool_input')
        )

    def generate_log(self, tool_input: Union[str, dict]) -> str:
        """Generate the log text for the given tool input.

        Args:
            tool_input (Union[str, dict]): the input passed to the tool.

        Returns:
            str: the invocation chain prefix followed by the tool input text.
        """
        return Monitor.get_invocation_chain_str() + f" Tool input is {tool_input}"
