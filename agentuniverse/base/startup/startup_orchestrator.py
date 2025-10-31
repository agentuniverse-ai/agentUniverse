# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: startup_orchestrator.py

from typing import Callable, Optional, List

from agentuniverse.base.startup.startup_phase import StartupPhase, StartupPhaseEnum
from agentuniverse.base.startup.startup_context import StartupContext
from agentuniverse.base.util.logging.logging_util import LOGGER


class StartupOrchestrator:
    """Orchestrates the execution of startup phases.

    This class manages the startup process by:
    1. Executing phases in dependency order
    2. Handling phase failures and rollback
    3. Providing progress callbacks
    4. Ensuring all dependencies are satisfied
    """

    def __init__(self):
        """Initialize the startup orchestrator."""
        self._phases: List[StartupPhase] = []
        self._progress_callback: Optional[Callable[[StartupPhase, StartupContext], None]] = None

    def add_phase(self, phase: StartupPhase) -> 'StartupOrchestrator':
        """Add a startup phase to the orchestrator.

        Args:
            phase: The startup phase to add

        Returns:
            Self for method chaining
        """
        self._phases.append(phase)
        return self

    def set_progress_callback(self, callback: Callable[[StartupPhase, StartupContext], None]) -> 'StartupOrchestrator':
        """Set a callback to be called after each phase completes.

        Args:
            callback: Function that takes (phase, context) as arguments

        Returns:
            Self for method chaining
        """
        self._progress_callback = callback
        return self

    def execute(self, context: StartupContext) -> None:
        """Execute all startup phases in dependency order.

        Args:
            context: The startup context

        Raises:
            Exception: If any phase fails to execute
        """
        # Sort phases by dependencies (topological sort)
        sorted_phases = self._topological_sort()

        executed_phases: List[StartupPhase] = []

        try:
            for phase in sorted_phases:
                # Check if phase can execute (all dependencies satisfied)
                if not phase.can_execute(context):
                    raise RuntimeError(
                        f"Phase {phase.name} cannot execute: dependencies not satisfied"
                    )

                # Execute the phase
                LOGGER.info(f"Starting phase: {phase.name}")
                phase.execute(context)
                context.mark_phase_completed(phase.phase_type)
                executed_phases.append(phase)
                LOGGER.info(f"Completed phase: {phase.name}")

                # Call progress callback if set
                if self._progress_callback:
                    self._progress_callback(phase, context)

        except Exception as e:
            LOGGER.error(f"Startup failed during phase: {executed_phases[-1].name if executed_phases else 'unknown'}")
            LOGGER.error(f"Error: {str(e)}")

            # Rollback executed phases in reverse order
            self._rollback(executed_phases, context)

            # Re-raise the exception
            raise

    def _topological_sort(self) -> List[StartupPhase]:
        """Sort phases by their dependencies using topological sort.

        Returns:
            List of phases in execution order

        Raises:
            RuntimeError: If circular dependencies are detected
        """
        # Build dependency graph
        graph = {phase.phase_type: phase.get_dependencies() for phase in self._phases}
        phase_map = {phase.phase_type: phase for phase in self._phases}

        # Kahn's algorithm for topological sort
        # in_degree[A] = number of dependencies A has (how many phases A depends on)
        in_degree = {phase_type: len(dependencies) for phase_type, dependencies in graph.items()}

        # Find phases with no dependencies (in_degree == 0)
        queue = [phase_type for phase_type, degree in in_degree.items() if degree == 0]
        sorted_phase_types = []

        while queue:
            # Remove a phase with no dependencies
            current = queue.pop(0)
            sorted_phase_types.append(current)

            # For each phase that depends on current, reduce its in-degree
            for phase_type, dependencies in graph.items():
                if current in dependencies:
                    in_degree[phase_type] -= 1
                    if in_degree[phase_type] == 0:
                        queue.append(phase_type)

        # Check for circular dependencies
        if len(sorted_phase_types) != len(self._phases):
            raise RuntimeError("Circular dependencies detected in startup phases")

        # Convert phase types back to phase objects
        return [phase_map[phase_type] for phase_type in sorted_phase_types]

    def _rollback(self, executed_phases: List[StartupPhase], context: StartupContext) -> None:
        """Rollback executed phases in reverse order.

        Args:
            executed_phases: List of phases that were executed
            context: The startup context
        """
        LOGGER.info("Rolling back executed phases...")

        for phase in reversed(executed_phases):
            try:
                LOGGER.info(f"Rolling back phase: {phase.name}")
                phase.rollback(context)
                LOGGER.info(f"Rolled back phase: {phase.name}")
            except Exception as rollback_error:
                # Log rollback errors but continue rolling back other phases
                LOGGER.error(f"Error rolling back phase {phase.name}: {str(rollback_error)}")

        LOGGER.info("Rollback completed")

    def get_phases(self) -> List[StartupPhase]:
        """Get the list of registered phases.

        Returns:
            List of startup phases
        """
        return self._phases.copy()
