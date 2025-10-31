# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025-10-31
# @Author  : SaladDay
# @Email   : fanjing.luo@zju.edu.cn
# @FileName: test_startup_phase.py

import pytest

from agentuniverse.base.startup.startup_phase import StartupPhase, StartupPhaseEnum
from agentuniverse.base.startup.startup_context import StartupContext


class MockPhase(StartupPhase):
    """Mock phase for testing."""

    def __init__(self, phase_type=StartupPhaseEnum.CONFIG, dependencies=None):
        super().__init__(phase_type)
        self._dependencies = dependencies or []
        self.executed = False
        self.rolled_back = False

    def execute(self, context: StartupContext) -> None:
        self.executed = True
        self._mark_completed()

    def rollback(self, context: StartupContext) -> None:
        self.rolled_back = True

    def get_dependencies(self) -> list[StartupPhaseEnum]:
        return self._dependencies


class FailingPhase(StartupPhase):
    """Phase that always fails for testing."""

    def __init__(self):
        super().__init__(StartupPhaseEnum.LOGGING)

    def execute(self, context: StartupContext) -> None:
        error = RuntimeError("Test failure")
        self._mark_failed(error)
        raise error

    def rollback(self, context: StartupContext) -> None:
        pass

    def get_dependencies(self) -> list[StartupPhaseEnum]:
        return [StartupPhaseEnum.CONFIG]


class TestStartupPhase:
    """Test cases for StartupPhase."""

    def test_phase_initialization(self):
        """Test phase initialization."""
        phase = MockPhase(StartupPhaseEnum.CONFIG)

        assert phase.phase_type == StartupPhaseEnum.CONFIG
        assert phase.name == "config"
        assert not phase.completed
        assert phase.error is None

    def test_phase_execution(self):
        """Test successful phase execution."""
        phase = MockPhase()
        context = StartupContext()

        phase.execute(context)

        assert phase.executed
        assert phase.completed
        assert phase.error is None

    def test_phase_failure(self):
        """Test phase failure handling."""
        phase = FailingPhase()
        context = StartupContext()

        with pytest.raises(RuntimeError, match="Test failure"):
            phase.execute(context)

        assert not phase.completed
        assert phase.error is not None
        assert isinstance(phase.error, RuntimeError)

    def test_phase_rollback(self):
        """Test phase rollback."""
        phase = MockPhase()
        context = StartupContext()

        phase.rollback(context)

        assert phase.rolled_back

    def test_phase_dependencies(self):
        """Test phase dependency declaration."""
        phase = MockPhase(
            phase_type=StartupPhaseEnum.LOGGING,
            dependencies=[StartupPhaseEnum.CONFIG]
        )

        deps = phase.get_dependencies()
        assert len(deps) == 1
        assert StartupPhaseEnum.CONFIG in deps

    def test_can_execute_with_satisfied_dependencies(self):
        """Test can_execute when dependencies are satisfied."""
        phase = MockPhase(
            phase_type=StartupPhaseEnum.LOGGING,
            dependencies=[StartupPhaseEnum.CONFIG]
        )
        context = StartupContext()
        context.mark_phase_completed(StartupPhaseEnum.CONFIG)

        assert phase.can_execute(context)

    def test_can_execute_with_unsatisfied_dependencies(self):
        """Test can_execute when dependencies are not satisfied."""
        phase = MockPhase(
            phase_type=StartupPhaseEnum.LOGGING,
            dependencies=[StartupPhaseEnum.CONFIG]
        )
        context = StartupContext()

        assert not phase.can_execute(context)

    def test_can_execute_with_no_dependencies(self):
        """Test can_execute when phase has no dependencies."""
        phase = MockPhase(phase_type=StartupPhaseEnum.CONFIG, dependencies=[])
        context = StartupContext()

        assert phase.can_execute(context)

    def test_can_execute_with_multiple_dependencies(self):
        """Test can_execute with multiple dependencies."""
        phase = MockPhase(
            phase_type=StartupPhaseEnum.WEB,
            dependencies=[
                StartupPhaseEnum.CONFIG,
                StartupPhaseEnum.LOGGING,
                StartupPhaseEnum.TELEMETRY
            ]
        )
        context = StartupContext()

        # No dependencies satisfied
        assert not phase.can_execute(context)

        # Partial dependencies satisfied
        context.mark_phase_completed(StartupPhaseEnum.CONFIG)
        assert not phase.can_execute(context)

        # All dependencies satisfied
        context.mark_phase_completed(StartupPhaseEnum.LOGGING)
        context.mark_phase_completed(StartupPhaseEnum.TELEMETRY)
        assert phase.can_execute(context)
