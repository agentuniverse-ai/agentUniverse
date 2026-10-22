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
    log_type: LogTypeEnum = LogTypeEnum.agent_first_token

    def process_record(self, record):
        record["message"] = self.generate_log(
            cost_time=record['extra'].get('cost_time')
        )

    def generate_log(self, cost_time) -> str:
        return Monitor.get_invocation_chain_str() + f" Agent first token cost {cost_time:.2f} seconds."
