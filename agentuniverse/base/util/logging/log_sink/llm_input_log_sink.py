# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/17 10:40
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: llm_input_log_sink.py

from typing import Union

from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.util.monitor.monitor import Monitor


class LLMInputLogSink(BaseFileLogSink):
    """Log sink that records the input received by an LLM call to a log file."""

    log_type: LogTypeEnum = LogTypeEnum.llm_input

    def process_record(self, record):
        """Fill the log record message with the generated LLM-input log.

        Args:
            record: the loguru log record being processed.
        """
        record["message"] = self.generate_log(
            llm_input=record['extra'].get('llm_input')
        )

    def generate_log(self, llm_input: Union[str, dict]) -> str:
        """Generate the log text for an LLM input event.

        Args:
            llm_input (Union[str, dict]): the input payload sent to the LLM.

        Returns:
            str: the invocation chain prefix followed by the LLM-input notice.
        """
        return Monitor.get_invocation_chain_str() + f" LLM get an input."
