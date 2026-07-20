# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/12 00:45
# @Author  : Cursor Agent
# @FileName: __init__.py
"""
Rate limiting module for agentUniverse.

This module provides concurrency control and rate limiting capabilities
for agents in the agentUniverse framework.

Main Components:
- RateLimiter: Base class for rate limiting with semaphore-based concurrency control
- ThreadRateLimiter: Thread-safe rate limiter for synchronous operations
- AsyncRateLimiter: Async-native rate limiter for asynchronous operations
- AgentConcurrencyController: Centralized controller for agent concurrency management
- AgentConcurrencyManager: Singleton manager for accessing the concurrency controller
- ConcurrencyContext: Context manager for automatic permit acquisition and release

Usage Example:
    from agentuniverse.base.util.rate_limiter import (
        AgentConcurrencyManager,
        AgentConcurrencyConfig,
        ConcurrencyStrategy,
        ConcurrencyContext
    )

    # Get the singleton manager
    manager = AgentConcurrencyManager()

    # Register an agent with concurrency limits
    config = AgentConcurrencyConfig(
        max_concurrent=5,
        timeout=30.0,
        strategy=ConcurrencyStrategy.REJECT
    )
    manager.register_agent("my_agent", config)

    # Use context manager for automatic permit handling
    with ConcurrencyContext(manager, "my_agent") as ctx:
        if ctx.acquired:
            # Execute agent
            pass
        else:
            # Handle rejection
            print(f"Rejected: {ctx.rejection_reason}")

    # Or manually acquire/release permits
    acquired, exec_id = manager.acquire_permit("my_agent")
    if acquired:
        # Execute agent
        manager.release_permit(exec_id)

    # Get statistics
    stats = manager.get_stats()
"""

from agentuniverse.base.util.rate_limiter.rate_limiter import (
    RateLimiter,
    ThreadRateLimiter,
    AsyncRateLimiter,
    rate_limited,
    rate_limited_async,
)

from agentuniverse.base.util.rate_limiter.agent_concurrency_controller import (
    ConcurrencyStrategy,
    AgentConcurrencyConfig,
    AgentExecutionContext,
    AgentConcurrencyController,
    AgentConcurrencyManager,
    ConcurrencyContext,
)

__all__ = [
    # Rate limiter classes
    "RateLimiter",
    "ThreadRateLimiter",
    "AsyncRateLimiter",
    # Decorators
    "rate_limited",
    "rate_limited_async",
    # Concurrency controller
    "ConcurrencyStrategy",
    "AgentConcurrencyConfig",
    "AgentExecutionContext",
    "AgentConcurrencyController",
    "AgentConcurrencyManager",
    "ConcurrencyContext",
]
