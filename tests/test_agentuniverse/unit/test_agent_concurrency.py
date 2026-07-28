# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/13
# @Author  : Cursor Agent
# @FileName: test_agent_concurrency.py
"""Tests for Agent-level concurrency control and timeout behavior."""
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from unittest import TestCase


class SimpleAgent(Agent):
    def __init__(self, delay: float = 0.0):
        super().__init__()
        self._delay = delay

    def input_keys(self) -> list[str]:
        return ["input"]

    def output_keys(self) -> list[str]:
        return ["output"]

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {"output": agent_result.get("output", "")}


class FakeAgentModel:
    def __init__(self, name: str = "fake"):
        self.info: Dict[str, Any] = {"name": name}
        self.profile: Dict[str, Any] = {}
        self.plan: Dict[str, Any] = {"planner": {"name": "fake_planner"}}
        self.memory: Dict[str, Any] = {}
        self.action: Dict[str, Any] = {}


class TestAgentConcurrency(TestCase):
    def setUp(self):
        self.agent = SimpleAgent(delay=0.05)
        self.agent.agent_model = FakeAgentModel(name="test_agent")

    def test_concurrency_limit_enforced(self):
        """Only up to max_concurrent runs should execute in parallel."""
        self.agent.set_concurrency_config(enabled=True, max_concurrent=2, timeout=0.5)

        results = []
        count_lock = threading.Lock()

        def run_agent():
            try:
                result = self.agent.run(input="x")
                with count_lock:
                    results.append(result.get_data("output"))
            except Exception as e:
                with count_lock:
                    results.append(f"error:{type(e).__name__}")

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(run_agent) for _ in range(4)]
            for future in as_completed(futures):
                future.result()

        success_count = sum(1 for item in results if not str(item).startswith("error"))
        self.assertEqual(success_count, 2)

    def test_timeout_raises_exception(self):
        """When timeout is reached, concurrency limit should raise."""
        self.agent.set_concurrency_config(enabled=True, max_concurrent=1, timeout=0.05)

        self.agent.run(input="first")
        start = time.time()
        with self.assertRaises(Exception) as context:
            self.agent.run(input="second")

        self.assertEqual(type(context.exception).__name__, "ConcurrencyLimitExceededException")
        self.assertLess(time.time() - start, 0.5)

    def test_current_concurrent_reflects_active_executions(self):
        """current_concurrent should track active executions."""
        self.agent.set_concurrency_config(enabled=True, max_concurrent=2, timeout=0.5)

        active_measurements = []
        measure_lock = threading.Lock()
        barrier = threading.Barrier(2)

        def run_agent():
            self.agent.run(input="x")
            with measure_lock:
                active_measurements.append(self.agent.current_concurrent)

        threads = [threading.Thread(target=run_agent), threading.Thread(target=run_agent)]
        threads[0].start()
        threads[1].start()
        barrier.wait()
        threads[0].join()
        threads[1].join()

        self.assertEqual(max(active_measurements), 2)


if __name__ == '__main__':
    import unittest
    unittest.main()
