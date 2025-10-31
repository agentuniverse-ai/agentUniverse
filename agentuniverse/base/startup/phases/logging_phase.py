# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: logging_phase.py

from agentuniverse.base.startup.startup_phase import StartupPhase, StartupPhaseEnum
from agentuniverse.base.startup.startup_context import StartupContext
from agentuniverse.base.util.logging.logging_util import init_loggers


class LoggingPhase(StartupPhase):
    """Logging initialization phase.

    This phase initializes the logging system using loguru.
    It depends on the CONFIG phase to get the log configuration path.
    """

    def __init__(self):
        """Initialize the logging phase."""
        super().__init__(StartupPhaseEnum.LOGGING)

    def execute(self, context: StartupContext) -> None:
        """Execute the logging initialization phase.

        Args:
            context: The startup context

        Raises:
            Exception: If logging initialization fails
        """
        try:
            # Initialize loguru loggers with the configuration
            init_loggers(context.log_config_path)

            # Mark phase as completed
            self._mark_completed()

        except Exception as e:
            self._mark_failed(e)
            raise

    def rollback(self, context: StartupContext) -> None:
        """Rollback the logging phase.

        Args:
            context: The startup context

        Note:
            Logging rollback is typically not needed as loguru handles
            cleanup automatically. This is a no-op for safety.
        """
        pass

    def get_dependencies(self) -> list[StartupPhaseEnum]:
        """Return the list of phases this phase depends on.

        Returns:
            List containing CONFIG phase
        """
        return [StartupPhaseEnum.CONFIG]
