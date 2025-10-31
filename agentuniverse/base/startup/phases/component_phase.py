# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: component_phase.py

from agentuniverse.base.startup.startup_phase import StartupPhase, StartupPhaseEnum
from agentuniverse.base.startup.startup_context import StartupContext
from agentuniverse.agent_serve.web.post_fork_queue import POST_FORK_QUEUE


class ComponentPhase(StartupPhase):
    """Component scanning and registration phase.

    This phase handles:
    1. Scanning all component packages
    2. Registering components with their respective managers
    3. Executing post-fork queue tasks (if in core mode)

    This is the final and most complex phase, depending on all previous phases.
    The actual scanning and registration logic is delegated to the AgentUniverse
    instance to maintain backward compatibility.
    """

    def __init__(self, agent_universe_instance):
        """Initialize the component phase.

        Args:
            agent_universe_instance: The AgentUniverse instance that contains
                                    the scan and register methods
        """
        super().__init__(StartupPhaseEnum.COMPONENTS)
        self._agent_universe = agent_universe_instance

    def execute(self, context: StartupContext) -> None:
        """Execute the component scanning and registration phase.

        Args:
            context: The startup context

        Raises:
            Exception: If component scanning or registration fails
        """
        try:
            # Delegate to the existing scan_and_register method
            # This maintains backward compatibility with the existing implementation
            self._agent_universe._AgentUniverse__scan_and_register(context.app_configer)

            # Execute post-fork queue tasks if in core mode
            if context.core_mode:
                for _func, args, kwargs in POST_FORK_QUEUE:
                    _func(*args, **kwargs)

            # Mark phase as completed
            self._mark_completed()

        except Exception as e:
            self._mark_failed(e)
            raise

    def rollback(self, context: StartupContext) -> None:
        """Rollback the component phase.

        Args:
            context: The startup context

        Note:
            Component unregistration is complex and typically not needed
            during startup failures. This is a no-op for safety.
        """
        pass

    def get_dependencies(self) -> list[StartupPhaseEnum]:
        """Return the list of phases this phase depends on.

        Returns:
            List containing all previous phases
        """
        return [
            StartupPhaseEnum.CONFIG,
            StartupPhaseEnum.LOGGING,
            StartupPhaseEnum.TELEMETRY,
            StartupPhaseEnum.WEB
        ]
