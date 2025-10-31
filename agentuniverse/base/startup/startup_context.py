# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: startup_context.py

from pathlib import Path
from typing import Any, Optional
from agentuniverse.base.startup.startup_phase import StartupPhaseEnum


class StartupContext:
    """Context object that holds shared data during startup process.

    This context is passed between startup phases to share configuration,
    instances, and state information.
    """

    def __init__(self, config_path: Optional[str] = None, core_mode: bool = False):
        """Initialize the startup context.

        Args:
            config_path: Path to the main configuration file
            core_mode: Whether to run in core mode
        """
        self.config_path = config_path
        self.core_mode = core_mode
        self.project_root_path: Optional[Path] = None

        # Phase completion tracking (list to preserve order)
        self._completed_phases: list[StartupPhaseEnum] = []

        # Shared data storage
        self._data: dict[str, Any] = {}

        # Configuration objects
        self.configer: Optional[Any] = None
        self.app_configer: Optional[Any] = None
        self.custom_key_configer: Optional[Any] = None
        self.default_llm_configer: Optional[Any] = None

        # Manager instances
        self.config_container: Optional[Any] = None
        self.application_container: Optional[Any] = None

        # Paths
        self.log_config_path: Optional[str] = None
        self.custom_key_configer_path: Optional[str] = None
        self.gunicorn_config_path: Optional[str] = None

    def mark_phase_completed(self, phase: StartupPhaseEnum) -> None:
        """Mark a phase as completed.

        Args:
            phase: The phase that has completed
        """
        if phase not in self._completed_phases:
            self._completed_phases.append(phase)

    def is_phase_completed(self, phase: StartupPhaseEnum) -> bool:
        """Check if a phase has been completed.

        Args:
            phase: The phase to check

        Returns:
            True if the phase has completed
        """
        return phase in self._completed_phases

    def get_completed_phases(self) -> list[StartupPhaseEnum]:
        """Get list of all completed phases in order.

        Returns:
            List of completed phase enums in the order they were completed
        """
        return self._completed_phases.copy()

    def set_data(self, key: str, value: Any) -> None:
        """Store arbitrary data in the context.

        Args:
            key: The data key
            value: The data value
        """
        self._data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """Retrieve data from the context.

        Args:
            key: The data key
            default: Default value if key not found

        Returns:
            The stored value or default
        """
        return self._data.get(key, default)

    def has_data(self, key: str) -> bool:
        """Check if data exists in the context.

        Args:
            key: The data key

        Returns:
            True if the key exists
        """
        return key in self._data

    def clear_phase_data(self) -> None:
        """Clear all phase completion tracking (for testing/reset)."""
        self._completed_phases.clear()

    def __repr__(self) -> str:
        """Return string representation of the context."""
        return (f"StartupContext(config_path={self.config_path}, "
                f"core_mode={self.core_mode}, "
                f"completed_phases={len(self._completed_phases)})")
