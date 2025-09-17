# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import Union

# @Time    : 2025/1/17 12:03
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: llm_invocation_log_sink.py

from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.util.monitor.monitor import Monitor


class LLMInvocationLogSink(BaseFileLogSink):
    log_type: LogTypeEnum = LogTypeEnum.llm_invocation

    def process_record(self, record):
        record["message"] = self.generate_log(
            used_token=record["extra"].get("used_token"),
            cost_time=record["extra"].get("cost_time"),
            llm_output=record["extra"].get("llm_output"),
        )

    def generate_log(self, used_token: int, cost_time: float, llm_output: Union[str, dict]) -> str:
        log_str = f" LLM cost {cost_time:.2f} seconds"
        if used_token:
            log_str += f", token usage: {used_token}"
        return Monitor.get_invocation_chain_str() + log_str + f" LLM output finished."
