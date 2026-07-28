# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/12 00:50
# @Author  : Cursor Agent
# @FileName: example_usage.py
"""
Example usage of agent concurrency control feature.

This example demonstrates how to:
1. Enable and configure concurrency control for agents
2. Handle concurrency limit exceeded scenarios
3. Monitor concurrency statistics
4. Use the global concurrency controller
"""
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from agentuniverse.agent.agent import Agent, ConcurrencyLimitExceededException
from agentuniverse.base.util.rate_limiter import (
    AgentConcurrencyManager,
    AgentConcurrencyConfig,
    ConcurrencyStrategy,
    ConcurrencyContext,
    ThreadRateLimiter,
)


def example_basic_agent_concurrency():
    """Example: Basic agent concurrency control."""

    class SimpleAgent(Agent):
        """A simple test agent."""

        def __init__(self):
            super().__init__()
            self.set_concurrency_config(enabled=True, max_concurrent=2, timeout=5.0)

        def input_keys(self) -> list:
            return ["query"]

        def output_keys(self) -> list:
            return ["response"]

        def parse_input(self, input_object, agent_input: dict) -> dict:
            agent_input["query"] = input_object.get_data("query")
            return agent_input

        def parse_result(self, agent_result: dict) -> dict:
            return {"response": agent_result.get("output", "")}

        def execute(self, input_object, agent_input: dict) -> dict:
            # Simulate some processing time
            query = agent_input.get("query", "")
            time.sleep(0.5)  # Simulate LLM call
            return {"output": f"Processed: {query}"}

    # Create agent
    agent = SimpleAgent()

    # Test concurrent executions
    print("\n=== Test: Basic Agent Concurrency ===")
    results = []
    errors = []

    def run_agent(i):
        try:
            result = agent.run(query=f"Task {i}")
            return f"Task {i}: {result.get_data('response')}"
        except ConcurrencyLimitExceededException as e:
            return f"Task {i}: REJECTED - {e.message}"

    # Run 5 tasks concurrently (agent limit is 2)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_agent, i) for i in range(5)]
        for future in as_completed(futures):
            print(f"  {future.result()}")

    print(f"  Current concurrent: {agent.current_concurrent}")


def example_global_concurrency_controller():
    """Example: Using the global concurrency controller."""

    print("\n=== Test: Global Concurrency Controller ===")

    # Get the singleton manager
    manager = AgentConcurrencyManager()

    # Set global limit
    manager.set_global_limit(max_concurrent=3, timeout=10.0)

    # Register agents with specific limits
    manager.register_agent("agent_alpha", AgentConcurrencyConfig(
        max_concurrent=2,
        timeout=5.0,
        strategy=ConcurrencyStrategy.REJECT
    ))

    manager.register_agent("agent_beta", AgentConcurrencyConfig(
        max_concurrent=1,
        timeout=3.0,
        strategy=ConcurrencyStrategy.REJECT
    ))

    # Use context manager for automatic permit handling
    print("  Testing concurrent executions with context manager:")

    results = []
    errors = []

    def simulate_agent_execution(agent_name: str, task_id: int):
        with ConcurrencyContext(manager, agent_name) as ctx:
            if ctx.acquired:
                print(f"    [{agent_name}] Task {task_id} started (exec_id={ctx.execution_id})")
                time.sleep(0.3)
                results.append(f"{agent_name}-Task {task_id}")
                return f"SUCCESS: {agent_name}-Task {task_id}"
            else:
                errors.append(f"{agent_name}-Task {task_id}")
                return f"REJECTED: {agent_name}-Task {task_id}"

    # Simulate concurrent executions
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = []
        # Mix of agents
        for i in range(3):
            futures.append(executor.submit(simulate_agent_execution, "agent_alpha", i))
        for i in range(3):
            futures.append(executor.submit(simulate_agent_execution, "agent_beta", i))

        for future in as_completed(futures):
            print(f"    Result: {future.result()}")

    # Print statistics
    stats = manager.get_stats()
    print(f"\n  Statistics:")
    print(f"    Total executions: {stats['total_executions']}")
    print(f"    Total rejections: {stats['total_rejections']}")
    print(f"    Rejection rate: {stats['rejection_rate']:.2%}")
    print(f"    Active executions: {stats['active_executions']}")


def example_decorator_rate_limiting():
    """Example: Using rate limiting decorators."""

    from agentuniverse.base.util.rate_limiter import rate_limited, rate_limited_async

    print("\n=== Test: Rate Limiting Decorators ===")

    # Synchronous rate limiting
    @rate_limited(max_concurrent=2, timeout=2.0)
    def rate_limited_function(task_id: int) -> str:
        print(f"    [Sync] Task {task_id} executing...")
        time.sleep(0.2)
        return f"Task {task_id} completed"

    # Run concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(rate_limited_function, i) for i in range(4)]
        for future in as_completed(futures):
            try:
                print(f"    {future.result()}")
            except RuntimeError as e:
                print(f"    [Rejected] {e}")


async def example_async_rate_limiting():
    """Example: Using async rate limiting."""

    from agentuniverse.base.util.rate_limiter import rate_limited_async

    print("\n=== Test: Async Rate Limiting ===")

    @rate_limited_async(max_concurrent=2, timeout=2.0)
    async def async_rate_limited_function(task_id: int) -> str:
        print(f"    [Async] Task {task_id} starting...")
        await asyncio.sleep(0.3)
        return f"Task {task_id} completed"

    import asyncio

    # Run concurrently
    tasks = [async_rate_limited_function(i) for i in range(4)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            print(f"    [Error/Rejected] {result}")
        else:
            print(f"    {result}")


def example_stats_monitoring():
    """Example: Monitoring concurrency statistics."""

    print("\n=== Test: Statistics Monitoring ===")

    manager = AgentConcurrencyManager()

    # Register some agents
    manager.register_agent("monitored_agent_1", AgentConcurrencyConfig(
        max_concurrent=5,
        timeout=10.0
    ))
    manager.register_agent("monitored_agent_2", AgentConcurrencyConfig(
        max_concurrent=3,
        timeout=5.0
    ))

    # Simulate some executions
    def run_tasks(agent_name: str, count: int):
        for i in range(count):
            acquired, exec_id = manager.acquire_permit(agent_name)
            if acquired:
                time.sleep(0.1)
                manager.release_permit(exec_id)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(run_tasks, "monitored_agent_1", 10),
            executor.submit(run_tasks, "monitored_agent_2", 5),
        ]
        for future in as_completed(futures):
            future.result()

    # Get detailed stats
    print("\n  Global Stats:")
    global_stats = manager.get_stats()
    for key, value in global_stats.items():
        if key != 'agents':
            print(f"    {key}: {value}")

    print("\n  Per-Agent Stats:")
    for agent_name, stats in global_stats.get('agents', {}).items():
        print(f"\n    Agent: {agent_name}")
        for key, value in stats.items():
            print(f"      {key}: {value}")


def main():
    """Run all examples."""

    print("=" * 60)
    print("Agent Concurrency Control Examples")
    print("=" * 60)

    try:
        example_basic_agent_concurrency()
        example_global_concurrency_controller()
        example_decorator_rate_limiting()
        example_stats_monitoring()

        # Run async example
        import asyncio
        asyncio.run(example_async_rate_limiting())

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError in examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
