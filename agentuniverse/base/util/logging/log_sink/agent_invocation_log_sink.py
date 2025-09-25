# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/16 16:23
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: agent_invocation_log_sink.py
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.util.logging.log_sink.base_file_log_sink import BaseFileLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse.base.util.monitor.monitor import Monitor


class AgentInvocationLogSink(BaseFileLogSink):
    log_type: LogTypeEnum = LogTypeEnum.agent_invocation

    def process_record(self, record):
        record["message"] = self.generate_log(
            cost_time=record["extra"].get("cost_time"), agent_output=record["extra"].get("agent_output")
        )

    def generate_log(self, cost_time: float, agent_output: OutputObject) -> str:
        log_str = f" Agent cost {cost_time:.2f} seconds"
        return Monitor.get_invocation_chain_str() + log_str + f" Agent output is {agent_output.to_json_str()}"
