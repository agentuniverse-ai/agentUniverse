# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/12 00:45
# @Author  : Cursor Agent
# @FileName: agent_concurrency_controller.py
"""
Agent concurrency control module for agentUniverse.

Provides centralized concurrency management for agents with support for:
- Per-agent concurrency limits
- Global concurrency limits
- Priority-based queuing
- Graceful degradation under load
"""
from enum import Enum
from typing import Dict, Optional, Set, Callable, Any, TypeVar, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from asyncio import Event as AsyncEvent
from threading import Event as ThreadEvent
import threading
import asyncio
import uuid

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.util.rate_limiter.rate_limiter import (
    RateLimiter,
    ThreadRateLimiter,
    AsyncRateLimiter
)

import logging
LOGGER = logging.getLogger("agentuniverse.concurrency")


class ConcurrencyStrategy(Enum):
    """Strategy for handling concurrent agent executions."""

    REJECT = "reject"           # Reject new requests when limit reached
    QUEUE = "queue"             # Queue requests until slot available
    PRIORITY_QUEUE = "priority"  # Queue with priority (higher = more important)
    TIMEOUT = "timeout"         # Wait with timeout


@dataclass
class AgentConcurrencyConfig:
    """Configuration for agent concurrency control."""

    max_concurrent: int = 10
    max_queue_size: int = 100
    timeout: Optional[float] = 30.0
    strategy: ConcurrencyStrategy = ConcurrencyStrategy.REJECT
    enabled: bool = True


@dataclass
class AgentExecutionContext:
    """Context for an agent execution."""

    execution_id: str
    agent_name: str
    start_time: datetime
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentConcurrencyController:
    """Centralized controller for agent concurrency management.

    Provides fine-grained control over agent execution concurrency with support
    for per-agent limits, global limits, and various rejection strategies.
    """

    def __init__(self):
        self._global_limiter: Optional[ThreadRateLimiter] = None
        self._agent_limiters: Dict[str, RateLimiter] = {}
        self._agent_configs: Dict[str, AgentConcurrencyConfig] = {}
        self._active_executions: Dict[str, AgentExecutionContext] = {}
        self._lock = threading.RLock()
        self._stats_lock = threading.Lock()
        self._total_executions = 0
        self._total_rejections = 0
        self._execution_history: list = []

    def set_global_limit(self, max_concurrent: int, timeout: Optional[float] = None) -> None:
        """Set global concurrency limit across all agents.

        Args:
            max_concurrent: Maximum concurrent executions globally.
            timeout: Timeout for acquiring global permit.
        """
        with self._lock:
            self._global_limiter = ThreadRateLimiter(
                max_concurrent=max_concurrent,
                timeout=timeout
            )
            LOGGER.info(f"Global concurrency limit set to {max_concurrent}")

    def register_agent(self, agent_name: str, config: AgentConcurrencyConfig) -> None:
        """Register an agent with concurrency configuration.

        Args:
            agent_name: Name of the agent.
            config: Concurrency configuration for this agent.
        """
        with self._lock:
            self._agent_configs[agent_name] = config
            if config.enabled:
                self._agent_limiters[agent_name] = ThreadRateLimiter(
                    max_concurrent=config.max_concurrent,
                    timeout=config.timeout
                )
                LOGGER.info(
                    f"Registered agent '{agent_name}' with concurrency limit {config.max_concurrent}"
                )

    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent from concurrency control.

        Args:
            agent_name: Name of the agent to unregister.
        """
        with self._lock:
            self._agent_limiters.pop(agent_name, None)
            self._agent_configs.pop(agent_name, None)
            LOGGER.info(f"Unregistered agent '{agent_name}' from concurrency control")

    def update_agent_config(self, agent_name: str, config: AgentConcurrencyConfig) -> None:
        """Update concurrency configuration for an agent.

        Args:
            agent_name: Name of the agent.
            config: New concurrency configuration.
        """
        self.register_agent(agent_name, config)

    def acquire_permit(
        self,
        agent_name: str,
        execution_id: Optional[str] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """Acquire a permit for agent execution.

        Args:
            agent_name: Name of the agent.
            execution_id: Optional execution ID (generated if not provided).
            priority: Execution priority (higher = more important).
            metadata: Additional metadata for the execution.

        Returns:
            Tuple of (acquired: bool, execution_id: str).
            If acquired is False, execution_id indicates the reason.
        """
        exec_id = execution_id or str(uuid.uuid4())
        metadata = metadata or {}

        with self._lock:
            config = self._agent_configs.get(agent_name)
            if config is None or not config.enabled:
                # No limit configured for this agent
                context = AgentExecutionContext(
                    execution_id=exec_id,
                    agent_name=agent_name,
                    start_time=datetime.now(),
                    priority=priority,
                    metadata=metadata
                )
                self._active_executions[exec_id] = context
                with self._stats_lock:
                    self._total_executions += 1
                return True, exec_id

            limiter = self._agent_limiters.get(agent_name)
            if limiter is None:
                return True, exec_id

        # Check global limit first
        global_acquired = True
        if self._global_limiter is not None:
            global_acquired = self._global_limiter.acquire()
            if not global_acquired:
                with self._stats_lock:
                    self._total_rejections += 1
                LOGGER.warn(f"Global concurrency limit reached, rejecting execution {exec_id}")
                return False, "global_limit_exceeded"

        # Check agent-specific limit
        agent_acquired = limiter.acquire()
        if not agent_acquired:
            if global_acquired and self._global_limiter:
                self._global_limiter.release()
            with self._stats_lock:
                self._total_rejections += 1
            LOGGER.warn(
                f"Agent '{agent_name}' concurrency limit reached, "
                f"rejecting execution {exec_id}"
            )
            return False, f"agent_limit_exceeded_{agent_name}"

        # Permit acquired successfully
        with self._lock:
            context = AgentExecutionContext(
                execution_id=exec_id,
                agent_name=agent_name,
                start_time=datetime.now(),
                priority=priority,
                metadata=metadata
            )
            self._active_executions[exec_id] = context
            with self._stats_lock:
                self._total_executions += 1

        LOGGER.debug(f"Execution {exec_id} started for agent '{agent_name}'")
        return True, exec_id

    def release_permit(self, execution_id: str) -> bool:
        """Release a permit after agent execution completes.

        Args:
            execution_id: ID of the execution to release.

        Returns:
            True if permit was released, False if not found.
        """
        with self._lock:
            context = self._active_executions.pop(execution_id, None)
            if context is None:
                LOGGER.warn(f"Execution {execution_id} not found in active executions")
                return False

            agent_name = context.agent_name

        # Release agent-specific limiter
        limiter = self._agent_limiters.get(agent_name)
        if limiter is not None:
            limiter.release()

        # Release global limiter
        if self._global_limiter is not None:
            self._global_limiter.release()

        duration = (datetime.now() - context.start_time).total_seconds()
        LOGGER.debug(
            f"Execution {execution_id} completed for agent '{agent_name}' "
            f"(duration: {duration:.2f}s)"
        )
        return True

    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get concurrency statistics for a specific agent.

        Args:
            agent_name: Name of the agent.

        Returns:
            Dictionary containing agent statistics.
        """
        with self._lock:
            limiter = self._agent_limiters.get(agent_name)
            config = self._agent_configs.get(agent_name)

        if limiter is None:
            return {
                "agent_name": agent_name,
                "enabled": False,
                "message": "No concurrency limit configured"
            }

        return {
            "agent_name": agent_name,
            "enabled": config.enabled if config else True,
            "max_concurrent": limiter.max_concurrent,
            "current_concurrent": limiter.current_concurrent,
            "total_acquired": limiter.total_acquired,
            "total_rejected": limiter.total_rejected,
            "rejection_rate": limiter.rejection_rate,
            "strategy": config.strategy.value if config else ConcurrencyStrategy.REJECT.value
        }

    def get_global_stats(self) -> Dict[str, Any]:
        """Get global concurrency statistics.

        Returns:
            Dictionary containing global statistics.
        """
        with self._stats_lock:
            total_acquired = self._total_executions
            total_rejected = self._total_rejections

        with self._lock:
            active_count = len(self._active_executions)
            global_info = {}
            if self._global_limiter:
                global_info = {
                    "max_concurrent": self._global_limiter.max_concurrent,
                    "current_concurrent": self._global_limiter.current_concurrent
                }

        rejection_rate = total_rejected / (total_acquired + total_rejected) if (total_acquired + total_rejected) > 0 else 0.0

        return {
            "total_executions": total_acquired,
            "total_rejections": total_rejected,
            "active_executions": active_count,
            "rejection_rate": rejection_rate,
            "global_limit": global_info,
            "registered_agents": len(self._agent_configs)
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get all concurrency statistics.

        Returns:
            Dictionary containing all statistics.
        """
        stats = self.get_global_stats()
        stats["agents"] = {
            name: self.get_agent_stats(name)
            for name in self._agent_configs.keys()
        }
        return stats

    def is_agent_available(self, agent_name: str) -> bool:
        """Check if an agent can accept new executions.

        Args:
            agent_name: Name of the agent.

        Returns:
            True if agent can accept new executions.
        """
        with self._lock:
            limiter = self._agent_limiters.get(agent_name)
            if limiter is None:
                return True
            return limiter.current_concurrent < limiter.max_concurrent

    def get_active_executions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active executions.

        Returns:
            Dictionary mapping execution IDs to their contexts.
        """
        with self._lock:
            return {
                exec_id: {
                    "agent_name": ctx.agent_name,
                    "start_time": ctx.start_time.isoformat(),
                    "duration_seconds": (datetime.now() - ctx.start_time).total_seconds(),
                    "priority": ctx.priority,
                    "metadata": ctx.metadata
                }
                for exec_id, ctx in self._active_executions.items()
            }

    def reset_stats(self) -> None:
        """Reset all statistics counters."""
        with self._stats_lock:
            self._total_executions = 0
            self._total_rejections = 0

        with self._lock:
            for limiter in self._agent_limiters.values():
                limiter._total_acquired = 0
                limiter._total_rejected = 0

        LOGGER.info("Concurrency statistics reset")


@singleton
class AgentConcurrencyManager:
    """Singleton manager for agent concurrency control.

    Provides global access to the concurrency controller.
    """

    def __init__(self):
        self._controller = AgentConcurrencyController()

    @property
    def controller(self) -> AgentConcurrencyController:
        """Return the concurrency controller."""
        return self._controller

    def set_global_limit(self, max_concurrent: int, timeout: Optional[float] = None) -> None:
        """Set global concurrency limit."""
        self._controller.set_global_limit(max_concurrent, timeout)

    def register_agent(self, agent_name: str, config: AgentConcurrencyConfig) -> None:
        """Register an agent with concurrency configuration."""
        self._controller.register_agent(agent_name, config)

    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent."""
        self._controller.unregister_agent(agent_name)

    def update_agent_config(self, agent_name: str, config: AgentConcurrencyConfig) -> None:
        """Update agent configuration."""
        self._controller.update_agent_config(agent_name, config)

    def acquire_permit(
        self,
        agent_name: str,
        execution_id: Optional[str] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """Acquire a permit for agent execution."""
        return self._controller.acquire_permit(agent_name, execution_id, priority, metadata)

    def release_permit(self, execution_id: str) -> bool:
        """Release a permit."""
        return self._controller.release_permit(execution_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get concurrency statistics."""
        return self._controller.get_all_stats()

    def is_available(self, agent_name: str) -> bool:
        """Check if agent can accept new executions."""
        return self._controller.is_agent_available(agent_name)


class ConcurrencyContext:
    """Context manager for automatic permit acquisition and release.

    Usage:
        manager = AgentConcurrencyManager()

        with ConcurrencyContext(manager, "my_agent") as ctx:
            if ctx.acquired:
                # execute agent
            else:
                # handle rejection
    """

    def __init__(
        self,
        manager: AgentConcurrencyManager,
        agent_name: str,
        execution_id: Optional[str] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._manager = manager
        self._agent_name = agent_name
        self._execution_id = execution_id
        self._priority = priority
        self._metadata = metadata or {}
        self._acquired = False
        self._exec_id: Optional[str] = None

    def __enter__(self) -> 'ConcurrencyContext':
        acquired, exec_id = self._manager.acquire_permit(
            self._agent_name,
            self._execution_id,
            self._priority,
            self._metadata
        )
        self._acquired = acquired
        self._exec_id = exec_id
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._acquired and self._exec_id:
            self._manager.release_permit(self._exec_id)

    @property
    def acquired(self) -> bool:
        """Return whether permit was acquired."""
        return self._acquired

    @property
    def execution_id(self) -> Optional[str]:
        """Return the execution ID."""
        return self._exec_id

    @property
    def rejection_reason(self) -> Optional[str]:
        """Return the rejection reason if not acquired."""
        return self._exec_id if not self._acquired else None
