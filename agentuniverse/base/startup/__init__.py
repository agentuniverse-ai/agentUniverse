# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: __init__.py

"""Startup framework for AgentUniverse.

This package provides a phased startup approach that:
- Eliminates duplicate configuration loading
- Provides clear dependency management between phases
- Supports error recovery and rollback
- Makes the startup process extensible and testable
"""

from agentuniverse.base.startup.startup_phase import StartupPhase, StartupPhaseEnum
from agentuniverse.base.startup.startup_context import StartupContext
from agentuniverse.base.startup.startup_orchestrator import StartupOrchestrator

__all__ = [
    'StartupPhase',
    'StartupPhaseEnum',
    'StartupContext',
    'StartupOrchestrator',
]
