# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: __init__.py

"""Startup phases for AgentUniverse framework initialization."""

from agentuniverse.base.startup.phases.config_phase import ConfigPhase
from agentuniverse.base.startup.phases.logging_phase import LoggingPhase
from agentuniverse.base.startup.phases.telemetry_phase import TelemetryPhase
from agentuniverse.base.startup.phases.web_phase import WebPhase
from agentuniverse.base.startup.phases.component_phase import ComponentPhase

__all__ = [
    'ConfigPhase',
    'LoggingPhase',
    'TelemetryPhase',
    'WebPhase',
    'ComponentPhase',
]
