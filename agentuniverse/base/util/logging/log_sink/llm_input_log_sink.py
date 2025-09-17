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
    log_type: LogTypeEnum = LogTypeEnum.llm_input

    def process_record(self, record):
        record["message"] = self.generate_log(llm_input=record["extra"].get("llm_input"))

    def generate_log(self, llm_input: Union[str, dict]) -> str:
        return Monitor.get_invocation_chain_str() + f" LLM get an input."
