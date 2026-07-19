#!/usr/bin/env python3
"""Configurable retry, timeout, fallback, and circuit-breaker tool wrapper."""

# Policy validation intentionally uses concise built-in exceptions.
# ruff: noqa: C901, S311, TRY003, TRY300, TRY301

import asyncio
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Any

from pydantic import Field, PrivateAttr

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger


class CircuitOpenError(RuntimeError):
    """Raised when a wrapped tool's circuit breaker is open."""


class ToolTimeoutError(TimeoutError):
    """Raised when a wrapped tool call exceeds its policy timeout."""


class _ToolResultError(RuntimeError):
    def __init__(self, result: Any):
        super().__init__("wrapped tool returned an error result")
        self.result = result


class ResilientTool(Tool):
    """Delegate to another registered tool through resilience policies."""

    target_tool: str = ""
    max_attempts: int = 3
    timeout_seconds: float | None = 30.0
    initial_delay_seconds: float = 0.25
    backoff_multiplier: float = 2.0
    max_delay_seconds: float = 5.0
    jitter_seconds: float = 0.0
    idempotent: bool = False
    allow_retry_non_idempotent: bool = False
    retry_exception_names: list[str] = Field(default_factory=list)
    retry_on_error_result: bool = False
    circuit_failure_threshold: int = 5
    circuit_recovery_seconds: float = 30.0
    fallback_enabled: bool = False
    fallback_value: Any = None

    _state: dict[str, Any] = PrivateAttr(
        default_factory=lambda: {
            "circuit": "closed",
            "consecutive_failures": 0,
            "opened_at": None,
            "half_open_in_flight": False,
            "calls": 0,
            "successes": 0,
            "failures": 0,
            "retries": 0,
            "timeouts": 0,
            "fallbacks": 0,
            "circuit_rejections": 0,
            "last_error": None,
        }
    )
    _state_lock: threading.RLock = PrivateAttr(default_factory=threading.RLock)

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> "ResilientTool":
        super().initialize_by_component_configer(component_configer)
        self._validate_policy()
        return self

    def execute(self, **kwargs: Any) -> Any:
        """Synchronously invoke the target tool with resilience policies."""
        self._validate_policy()
        target = self._target()
        allowed = self._begin_call()
        if not allowed:
            return self._reject_open_circuit()
        attempts = self._attempt_count()
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                result = self._sync_attempt(target, kwargs)
                if self.retry_on_error_result and self._is_error_result(result):
                    raise _ToolResultError(result)
                self._record_success()
                return result
            except Exception as exc:
                last_error = exc
                if isinstance(exc, ToolTimeoutError):
                    self._increment("timeouts")
                if attempt < attempts and self._retryable(exc):
                    self._increment("retries")
                    time.sleep(self._delay(attempt))
                    continue
                self._record_failure(exc)
                if self.fallback_enabled:
                    self._increment("fallbacks")
                    return self.fallback_value
                if isinstance(exc, _ToolResultError):
                    return exc.result
                raise
        raise last_error or RuntimeError("resilient tool failed without an error")

    async def async_execute(self, **kwargs: Any) -> Any:
        """Asynchronously invoke the target tool with cancellable timeouts."""
        self._validate_policy()
        target = self._target()
        allowed = self._begin_call()
        if not allowed:
            return self._reject_open_circuit()
        attempts = self._attempt_count()
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                result = await self._async_attempt(target, kwargs)
                if self.retry_on_error_result and self._is_error_result(result):
                    raise _ToolResultError(result)
                self._record_success()
                return result
            except Exception as exc:
                last_error = exc
                if isinstance(exc, ToolTimeoutError):
                    self._increment("timeouts")
                if attempt < attempts and self._retryable(exc):
                    self._increment("retries")
                    await asyncio.sleep(self._delay(attempt))
                    continue
                self._record_failure(exc)
                if self.fallback_enabled:
                    self._increment("fallbacks")
                    return self.fallback_value
                if isinstance(exc, _ToolResultError):
                    return exc.result
                raise
        raise last_error or RuntimeError("resilient tool failed without an error")

    def _validate_policy(self) -> None:
        if not isinstance(self.target_tool, str) or not self.target_tool.strip():
            raise ValueError("target_tool must be a non-empty string")
        if self.name and self.target_tool == self.name:
            raise ValueError("target_tool must not reference the resilient wrapper itself")
        for name in ("max_attempts", "circuit_failure_threshold"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name in (
            "initial_delay_seconds",
            "max_delay_seconds",
            "jitter_seconds",
            "circuit_recovery_seconds",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"{name} must be a non-negative number")
        if (
            isinstance(self.backoff_multiplier, bool)
            or not isinstance(self.backoff_multiplier, (int, float))
            or self.backoff_multiplier < 1
        ):
            raise ValueError("backoff_multiplier must be at least 1")
        if self.timeout_seconds is not None and (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or self.timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be null or a positive number")
        for name in (
            "idempotent",
            "allow_retry_non_idempotent",
            "retry_on_error_result",
            "fallback_enabled",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a boolean")
        if not isinstance(self.retry_exception_names, list) or any(
            not isinstance(name, str) or not name.isidentifier() for name in self.retry_exception_names
        ):
            raise ValueError("retry_exception_names must contain simple exception class names")

    def _target(self) -> Tool:
        target = ToolManager().get_instance_obj(self.target_tool, new_instance=False)
        if target is None:
            raise ValueError(f"target tool is not registered: {self.target_tool}")
        if target is self or (isinstance(target, ResilientTool) and target.target_tool == self.name):
            raise ValueError("resilient tool configuration contains a delegation cycle")
        return target

    def _attempt_count(self) -> int:
        return self.max_attempts if self.idempotent or self.allow_retry_non_idempotent else 1

    def _sync_attempt(self, target: Tool, kwargs: dict[str, Any]) -> Any:
        if self.timeout_seconds is None:
            return target.run(**kwargs)
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="au-resilient-tool")
        future = executor.submit(target.run, **kwargs)
        try:
            return future.result(timeout=self.timeout_seconds)
        except FutureTimeoutError as exc:
            future.cancel()
            raise ToolTimeoutError(
                f"tool {self.target_tool} exceeded timeout_seconds ({self.timeout_seconds})"
            ) from exc
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    async def _async_attempt(self, target: Tool, kwargs: dict[str, Any]) -> Any:
        operation = target.async_run(**kwargs)
        if self.timeout_seconds is None:
            return await operation
        try:
            return await asyncio.wait_for(operation, timeout=self.timeout_seconds)
        except TimeoutError as exc:
            raise ToolTimeoutError(
                f"tool {self.target_tool} exceeded timeout_seconds ({self.timeout_seconds})"
            ) from exc

    def _begin_call(self) -> bool:
        now = time.monotonic()
        with self._state_lock:
            self._state["calls"] += 1
            if self._state["circuit"] == "open":
                opened_at = self._state["opened_at"] or now
                if now - opened_at < self.circuit_recovery_seconds:
                    self._state["circuit_rejections"] += 1
                    return False
                self._state["circuit"] = "half_open"
                self._state["half_open_in_flight"] = False
            if self._state["circuit"] == "half_open":
                if self._state["half_open_in_flight"]:
                    self._state["circuit_rejections"] += 1
                    return False
                self._state["half_open_in_flight"] = True
            return True

    def _reject_open_circuit(self) -> Any:
        error = CircuitOpenError(f"circuit is open for target tool: {self.target_tool}")
        if self.fallback_enabled:
            self._increment("fallbacks")
            return self.fallback_value
        raise error

    def _record_success(self) -> None:
        with self._state_lock:
            self._state["successes"] += 1
            self._state["consecutive_failures"] = 0
            self._state["circuit"] = "closed"
            self._state["opened_at"] = None
            self._state["half_open_in_flight"] = False
            self._state["last_error"] = None

    def _record_failure(self, error: Exception) -> None:
        with self._state_lock:
            self._state["failures"] += 1
            self._state["consecutive_failures"] += 1
            self._state["last_error"] = f"{type(error).__name__}: {error}"
            half_open = self._state["circuit"] == "half_open"
            if half_open or self._state["consecutive_failures"] >= self.circuit_failure_threshold:
                self._state["circuit"] = "open"
                self._state["opened_at"] = time.monotonic()
            self._state["half_open_in_flight"] = False

    def _retryable(self, error: Exception) -> bool:
        if not self.retry_exception_names:
            return True
        names = {cls.__name__ for cls in type(error).mro()}
        return bool(names.intersection(self.retry_exception_names))

    def _delay(self, failed_attempt: int) -> float:
        base = min(
            self.max_delay_seconds,
            self.initial_delay_seconds * self.backoff_multiplier ** max(0, failed_attempt - 1),
        )
        return base + (random.uniform(0, self.jitter_seconds) if self.jitter_seconds else 0.0)

    @staticmethod
    def _is_error_result(result: Any) -> bool:
        return isinstance(result, dict) and result.get("status") == "error"

    def _increment(self, field: str) -> None:
        with self._state_lock:
            self._state[field] += 1

    def resilience_state(self) -> dict[str, Any]:
        """Return a snapshot of circuit and invocation counters."""
        with self._state_lock:
            return dict(self._state)

    def reset_resilience_state(self) -> None:
        """Close the circuit and reset all invocation counters."""
        with self._state_lock:
            self._state.update(
                {
                    "circuit": "closed",
                    "consecutive_failures": 0,
                    "opened_at": None,
                    "half_open_in_flight": False,
                    "calls": 0,
                    "successes": 0,
                    "failures": 0,
                    "retries": 0,
                    "timeouts": 0,
                    "fallbacks": 0,
                    "circuit_rejections": 0,
                    "last_error": None,
                }
            )
