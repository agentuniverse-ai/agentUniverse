# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: telemetry_phase.py

from agentuniverse.base.startup.startup_phase import StartupPhase, StartupPhaseEnum
from agentuniverse.base.startup.startup_context import StartupContext
from agentuniverse.base.tracing.otel.telemetry_manager import TelemetryManager
from agentuniverse.base.util.monitor.monitor import Monitor


class TelemetryPhase(StartupPhase):
    """Telemetry and monitoring initialization phase.

    This phase initializes:
    1. OpenTelemetry (OTEL) for distributed tracing
    2. Monitoring system

    It depends on CONFIG and LOGGING phases.
    """

    def __init__(self):
        """Initialize the telemetry phase."""
        super().__init__(StartupPhaseEnum.TELEMETRY)

    def execute(self, context: StartupContext) -> None:
        """Execute the telemetry initialization phase.

        Args:
            context: The startup context

        Raises:
            Exception: If telemetry initialization fails
        """
        try:
            # Initialize OpenTelemetry
            otel_config = context.configer.value.get('OTEL', {})
            TelemetryManager().init_from_config(otel_config)

            # Initialize monitoring module
            Monitor(configer=context.configer)

            # Mark phase as completed
            self._mark_completed()

        except Exception as e:
            self._mark_failed(e)
            raise

    def rollback(self, context: StartupContext) -> None:
        """Rollback the telemetry phase.

        Args:
            context: The startup context

        Note:
            Telemetry cleanup is handled by the respective managers.
            This is a no-op for safety.
        """
        pass

    def get_dependencies(self) -> list[StartupPhaseEnum]:
        """Return the list of phases this phase depends on.

        Returns:
            List containing CONFIG and LOGGING phases
        """
        return [StartupPhaseEnum.CONFIG, StartupPhaseEnum.LOGGING]
