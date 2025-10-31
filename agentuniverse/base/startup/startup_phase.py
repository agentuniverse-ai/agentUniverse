# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: startup_phase.py

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class StartupPhaseEnum(Enum):
    """Enumeration of startup phases in execution order."""
    CONFIG = "config"
    LOGGING = "logging"
    TELEMETRY = "telemetry"
    WEB = "web"
    COMPONENTS = "components"
    POST_INIT = "post_init"


class StartupPhase(ABC):
    """Abstract base class for startup phases.

    Each phase represents a distinct initialization step with clear
    responsibilities, dependencies, and rollback capabilities.
    """

    def __init__(self, phase_type: StartupPhaseEnum):
        """Initialize the startup phase.

        Args:
            phase_type: The type of this startup phase
        """
        self.phase_type = phase_type
        self._completed = False
        self._error: Optional[Exception] = None

    @property
    def name(self) -> str:
        """Return the human-readable name of this phase."""
        return self.phase_type.value

    @property
    def completed(self) -> bool:
        """Check if this phase has completed successfully."""
        return self._completed

    @property
    def error(self) -> Optional[Exception]:
        """Return the error that occurred during execution, if any."""
        return self._error

    @abstractmethod
    def execute(self, context: 'StartupContext') -> None:
        """Execute this startup phase.

        Args:
            context: The startup context containing shared data

        Raises:
            Exception: If the phase execution fails
        """
        pass

    @abstractmethod
    def rollback(self, context: 'StartupContext') -> None:
        """Rollback this phase if execution fails.

        Args:
            context: The startup context containing shared data
        """
        pass

    @abstractmethod
    def get_dependencies(self) -> list[StartupPhaseEnum]:
        """Return the list of phases this phase depends on.

        Returns:
            List of phase types that must complete before this phase
        """
        pass

    def _mark_completed(self) -> None:
        """Mark this phase as completed."""
        self._completed = True

    def _mark_failed(self, error: Exception) -> None:
        """Mark this phase as failed.

        Args:
            error: The exception that caused the failure
        """
        self._error = error
        self._completed = False

    def can_execute(self, context: 'StartupContext') -> bool:
        """Check if this phase can be executed.

        Args:
            context: The startup context

        Returns:
            True if all dependencies are satisfied
        """
        dependencies = self.get_dependencies()
        for dep in dependencies:
            if not context.is_phase_completed(dep):
                return False
        return True
