# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/9 18:06
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: log_sink_manager.py
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.base.util.logging.log_sink.log_sink import LogSink


@singleton
class LogSinkManager(ComponentManagerBase[LogSink]):
    """A singleton manager class of the DocProcessor."""

    def __init__(self):
        super().__init__(ComponentEnum.LOG_SINK)
