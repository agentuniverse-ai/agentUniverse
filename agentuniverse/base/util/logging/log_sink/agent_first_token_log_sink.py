# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/17 14:50
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: agent_first_token_log_sink.py

from typing import Union

from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.util.monitor.monitor import Monitor


class AgentFirstTokenLogSink(BaseFileLogSink):
    """Log sink that records the agent first-token latency to a file log."""

    log_type: LogTypeEnum = LogTypeEnum.agent_first_token

    def process_record(self, record):
        """Rewrite the record message with the generated first-token log.

        Args:
            record: The log record dict being processed.
        """
        record["message"] = self.generate_log(
            cost_time=record['extra'].get('cost_time')
        )

    def generate_log(self, cost_time) -> str:
        """Build the first-token cost log message.

        Args:
            cost_time: The elapsed time in seconds before the first token.

        Returns:
            str: The invocation chain prefix followed by the cost text.
        """
        return Monitor.get_invocation_chain_str() + f" Agent first token cost {cost_time:.2f} seconds."
