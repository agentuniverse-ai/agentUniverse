# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/16 15:12
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: agent_input_log_sink.py
from typing import Union

from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.util.monitor.monitor import Monitor


class AgentInputLogSink(BaseFileLogSink):
    """Log sink that records the agent invocation input to a file log."""

    log_type: LogTypeEnum = LogTypeEnum.agent_input

    def process_record(self, record):
        """Rewrite the record message with the generated agent input log.

        Args:
            record: The log record dict being processed.
        """
        record["message"] = self.generate_log(
            agent_input=record['extra'].get('agent_input')
        )

    def generate_log(self, agent_input: Union[str, dict]) -> str:
        """Build the agent input log message.

        Args:
            agent_input: The agent input, either a plain string or a dict.

        Returns:
            str: The invocation chain prefix followed by the agent input text.
        """
        return Monitor.get_invocation_chain_str() + f" Agent input is {agent_input}"
