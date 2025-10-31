# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: test_startup_orchestrator.py

import pytest

from agentuniverse.base.startup.startup_orchestrator import StartupOrchestrator
from agentuniverse.base.startup.startup_phase import StartupPhase, StartupPhaseEnum
from agentuniverse.base.startup.startup_context import StartupContext


class MockPhase(StartupPhase):
    """Mock phase for testing."""

    def __init__(self, phase_type, dependencies=None, should_fail=False):
        super().__init__(phase_type)
        self._dependencies = dependencies or []
        self.should_fail = should_fail
        self.executed = False
        self.rolled_back = False

    def execute(self, context: StartupContext) -> None:
        if self.should_fail:
            error = RuntimeError(f"Phase {self.name} failed")
            self._mark_failed(error)
            raise error
        self.executed = True
        self._mark_completed()

    def rollback(self, context: StartupContext) -> None:
        self.rolled_back = True

    def get_dependencies(self) -> list[StartupPhaseEnum]:
        return self._dependencies


class TestStartupOrchestrator:
    """Test cases for StartupOrchestrator."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = StartupOrchestrator()
        assert len(orchestrator.get_phases()) == 0

    def test_add_phase(self):
        """Test adding phases to orchestrator."""
        orchestrator = StartupOrchestrator()
        phase1 = MockPhase(StartupPhaseEnum.CONFIG)
        phase2 = MockPhase(StartupPhaseEnum.LOGGING)

        orchestrator.add_phase(phase1).add_phase(phase2)

        phases = orchestrator.get_phases()
        assert len(phases) == 2
        assert phase1 in phases
        assert phase2 in phases

    def test_execute_single_phase(self):
        """Test executing a single phase."""
        orchestrator = StartupOrchestrator()
        phase = MockPhase(StartupPhaseEnum.CONFIG)
        orchestrator.add_phase(phase)

        context = StartupContext()
        orchestrator.execute(context)

        assert phase.executed
        assert context.is_phase_completed(StartupPhaseEnum.CONFIG)

    def test_execute_phases_in_dependency_order(self):
        """Test phases are executed in dependency order."""
        orchestrator = StartupOrchestrator()

        # Create phases with dependencies
        config_phase = MockPhase(StartupPhaseEnum.CONFIG, dependencies=[])
        logging_phase = MockPhase(
            StartupPhaseEnum.LOGGING,
            dependencies=[StartupPhaseEnum.CONFIG]
        )
        telemetry_phase = MockPhase(
            StartupPhaseEnum.TELEMETRY,
            dependencies=[StartupPhaseEnum.CONFIG, StartupPhaseEnum.LOGGING]
        )

        # Add in reverse order to test sorting
        orchestrator.add_phase(telemetry_phase)
        orchestrator.add_phase(logging_phase)
        orchestrator.add_phase(config_phase)

        context = StartupContext()
        orchestrator.execute(context)

        # All phases should be executed
        assert config_phase.executed
        assert logging_phase.executed
        assert telemetry_phase.executed

        # Check execution order via context
        completed = context.get_completed_phases()
        config_idx = completed.index(StartupPhaseEnum.CONFIG)
        logging_idx = completed.index(StartupPhaseEnum.LOGGING)
        telemetry_idx = completed.index(StartupPhaseEnum.TELEMETRY)

        assert config_idx < logging_idx < telemetry_idx

    def test_execute_with_failure_triggers_rollback(self):
        """Test that phase failure triggers rollback of completed phases."""
        orchestrator = StartupOrchestrator()

        phase1 = MockPhase(StartupPhaseEnum.CONFIG)
        phase2 = MockPhase(
            StartupPhaseEnum.LOGGING,
            dependencies=[StartupPhaseEnum.CONFIG],
            should_fail=True
        )

        orchestrator.add_phase(phase1).add_phase(phase2)

        context = StartupContext()

        with pytest.raises(RuntimeError, match="Phase logging failed"):
            orchestrator.execute(context)

        # First phase should be executed and rolled back
        assert phase1.executed
        assert phase1.rolled_back

        # Second phase should not be marked as completed
        assert not context.is_phase_completed(StartupPhaseEnum.LOGGING)

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        orchestrator = StartupOrchestrator()

        # This would create a circular dependency if both were added
        # For this test, we'll create a simpler case
        phase1 = MockPhase(
            StartupPhaseEnum.CONFIG,
            dependencies=[StartupPhaseEnum.LOGGING]
        )
        phase2 = MockPhase(
            StartupPhaseEnum.LOGGING,
            dependencies=[StartupPhaseEnum.CONFIG]
        )

        orchestrator.add_phase(phase1).add_phase(phase2)

        context = StartupContext()

        with pytest.raises(RuntimeError, match="Circular dependencies detected"):
            orchestrator.execute(context)

    def test_progress_callback(self):
        """Test progress callback is called after each phase."""
        orchestrator = StartupOrchestrator()
        phase1 = MockPhase(StartupPhaseEnum.CONFIG)
        phase2 = MockPhase(
            StartupPhaseEnum.LOGGING,
            dependencies=[StartupPhaseEnum.CONFIG]
        )

        orchestrator.add_phase(phase1).add_phase(phase2)

        # Track callback invocations
        callback_phases = []

        def progress_callback(phase, ctx):
            callback_phases.append(phase.phase_type)

        orchestrator.set_progress_callback(progress_callback)

        context = StartupContext()
        orchestrator.execute(context)

        # Callback should be called for each phase
        assert len(callback_phases) == 2
        assert StartupPhaseEnum.CONFIG in callback_phases
        assert StartupPhaseEnum.LOGGING in callback_phases

    def test_rollback_continues_on_error(self):
        """Test rollback continues even if a phase rollback fails."""
        orchestrator = StartupOrchestrator()

        class FailingRollbackPhase(MockPhase):
            def rollback(self, context: StartupContext) -> None:
                super().rollback(context)
                raise RuntimeError("Rollback failed")

        phase1 = FailingRollbackPhase(StartupPhaseEnum.CONFIG)
        phase2 = MockPhase(
            StartupPhaseEnum.LOGGING,
            dependencies=[StartupPhaseEnum.CONFIG],
            should_fail=True
        )

        orchestrator.add_phase(phase1).add_phase(phase2)

        context = StartupContext()

        # Should still raise the original error, not the rollback error
        with pytest.raises(RuntimeError, match="Phase logging failed"):
            orchestrator.execute(context)

        # Both phases should have attempted rollback
        assert phase1.rolled_back

    def test_empty_orchestrator(self):
        """Test executing orchestrator with no phases."""
        orchestrator = StartupOrchestrator()
        context = StartupContext()

        # Should not raise any errors
        orchestrator.execute(context)

        assert len(context.get_completed_phases()) == 0
