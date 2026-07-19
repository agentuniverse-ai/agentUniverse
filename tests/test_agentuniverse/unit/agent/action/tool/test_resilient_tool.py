#!/usr/bin/env python3
"""Tests for the resilient tool wrapper."""

import asyncio
import time
import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.resilient_tool import CircuitOpenError, ResilientTool, ToolTimeoutError
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class SequenceTool:
    def __init__(self, responses=None, delay=0):
        self.responses = list(responses or [])
        self.delay = delay
        self.calls = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        if self.delay:
            time.sleep(self.delay)
        response = self.responses.pop(0) if self.responses else "ok"
        if isinstance(response, Exception):
            raise response
        return response

    async def async_run(self, **kwargs):
        self.calls.append(kwargs)
        if self.delay:
            await asyncio.sleep(self.delay)
        response = self.responses.pop(0) if self.responses else "ok"
        if isinstance(response, Exception):
            raise response
        return response


class FakeManager:
    def __init__(self, tools):
        self.tools = tools

    def __call__(self):
        return self

    def get_instance_obj(self, name, new_instance=False):
        self.new_instance = new_instance
        return self.tools.get(name)


class ResilientTestCase(unittest.TestCase):
    def wrapper(self, target=None, **kwargs):
        tool = target or SequenceTool()
        options = {"timeout_seconds": None, "initial_delay_seconds": 0, "jitter_seconds": 0}
        options.update(kwargs)
        wrapper = ResilientTool(
            name="resilient",
            target_tool="target",
            **options,
        )
        manager = FakeManager({"target": tool})
        context = patch("agentuniverse.agent.action.tool.resilient_tool.ToolManager", new=manager)
        return wrapper, tool, context


class TestRetryPolicies(ResilientTestCase):
    def test_non_idempotent_tool_does_not_retry_by_default(self):
        wrapper, target, context = self.wrapper(SequenceTool([ValueError("fail"), "ok"]), max_attempts=3)
        with context, self.assertRaisesRegex(ValueError, "fail"):
            wrapper.execute(value=1)
        self.assertEqual(len(target.calls), 1)

    def test_idempotent_tool_retries_then_succeeds(self):
        wrapper, target, context = self.wrapper(
            SequenceTool([ConnectionError("one"), TimeoutError("two"), "ok"]),
            max_attempts=3,
            idempotent=True,
        )
        with context, patch("agentuniverse.agent.action.tool.resilient_tool.time.sleep") as sleep:
            result = wrapper.execute(query="hello")
        self.assertEqual(result, "ok")
        self.assertEqual(len(target.calls), 3)
        self.assertEqual(wrapper.resilience_state()["retries"], 2)
        self.assertEqual(sleep.call_count, 2)

    def test_retry_exception_allowlist(self):
        wrapper, target, context = self.wrapper(
            SequenceTool([ValueError("not retryable"), "ok"]),
            max_attempts=3,
            idempotent=True,
            retry_exception_names=["ConnectionError"],
        )
        with context, self.assertRaises(ValueError):
            wrapper.execute()
        self.assertEqual(len(target.calls), 1)

    def test_base_exception_name_matches_subclass(self):
        wrapper, target, context = self.wrapper(
            SequenceTool([ConnectionError("retry"), "ok"]),
            max_attempts=2,
            idempotent=True,
            retry_exception_names=["OSError"],
        )
        with context:
            self.assertEqual(wrapper.execute(), "ok")
        self.assertEqual(len(target.calls), 2)

    def test_structured_error_result_can_be_retried(self):
        wrapper, target, context = self.wrapper(
            SequenceTool([{"status": "error", "error": "temporary"}, {"status": "success"}]),
            max_attempts=2,
            idempotent=True,
            retry_on_error_result=True,
        )
        with context:
            self.assertEqual(wrapper.execute(), {"status": "success"})
        self.assertEqual(len(target.calls), 2)

    def test_final_structured_error_is_returned(self):
        error = {"status": "error", "error": "still failing"}
        wrapper, _target, context = self.wrapper(
            SequenceTool([error]), max_attempts=1, idempotent=True, retry_on_error_result=True
        )
        with context:
            self.assertIs(wrapper.execute(), error)
        self.assertEqual(wrapper.resilience_state()["failures"], 1)

    def test_explicit_non_idempotent_retry_override(self):
        wrapper, target, context = self.wrapper(
            SequenceTool([RuntimeError("first"), "ok"]),
            max_attempts=2,
            allow_retry_non_idempotent=True,
        )
        with context:
            self.assertEqual(wrapper.execute(), "ok")
        self.assertEqual(len(target.calls), 2)

    def test_exponential_delay_is_capped(self):
        wrapper, _target, _context = self.wrapper(
            initial_delay_seconds=2,
            backoff_multiplier=3,
            max_delay_seconds=5,
        )
        self.assertEqual(wrapper._delay(1), 2)
        self.assertEqual(wrapper._delay(2), 5)
        self.assertEqual(wrapper._delay(5), 5)


class TestTimeoutAndFallback(ResilientTestCase):
    def test_sync_timeout(self):
        wrapper, _target, context = self.wrapper(SequenceTool(delay=0.03), timeout_seconds=0.005)
        with context, self.assertRaises(ToolTimeoutError):
            wrapper.execute()
        self.assertEqual(wrapper.resilience_state()["timeouts"], 1)

    def test_async_timeout(self):
        wrapper, _target, context = self.wrapper(SequenceTool(delay=0.03), timeout_seconds=0.005)

        async def run():
            with context:
                return await wrapper.async_execute()

        with self.assertRaises(ToolTimeoutError):
            asyncio.run(run())
        self.assertEqual(wrapper.resilience_state()["timeouts"], 1)

    def test_async_retry(self):
        wrapper, target, context = self.wrapper(
            SequenceTool([ConnectionError("temporary"), "async ok"]),
            max_attempts=2,
            idempotent=True,
        )

        async def run():
            with context:
                return await wrapper.async_execute(value=1)

        self.assertEqual(asyncio.run(run()), "async ok")
        self.assertEqual(len(target.calls), 2)

    def test_fallback_on_exception(self):
        wrapper, _target, context = self.wrapper(
            SequenceTool([RuntimeError("failed")]), fallback_enabled=True, fallback_value={"cached": True}
        )
        with context:
            self.assertEqual(wrapper.execute(), {"cached": True})
        self.assertEqual(wrapper.resilience_state()["fallbacks"], 1)

    def test_timeout_can_be_disabled(self):
        wrapper, _target, context = self.wrapper(SequenceTool(delay=0.005), timeout_seconds=None)
        with context:
            self.assertEqual(wrapper.execute(), "ok")


class TestCircuitBreaker(ResilientTestCase):
    def test_circuit_opens_and_rejects_calls(self):
        wrapper, target, context = self.wrapper(
            SequenceTool([RuntimeError("one"), RuntimeError("two"), "unused"]),
            circuit_failure_threshold=2,
        )
        with context:
            for _ in range(2):
                with self.assertRaises(RuntimeError):
                    wrapper.execute()
            with self.assertRaises(CircuitOpenError):
                wrapper.execute()
        self.assertEqual(len(target.calls), 2)
        self.assertEqual(wrapper.resilience_state()["circuit"], "open")
        self.assertEqual(wrapper.resilience_state()["circuit_rejections"], 1)

    def test_half_open_success_closes_circuit(self):
        wrapper, _target, context = self.wrapper(
            SequenceTool([RuntimeError("open"), "recovered"]),
            circuit_failure_threshold=1,
            circuit_recovery_seconds=1,
        )
        with context:
            with self.assertRaises(RuntimeError):
                wrapper.execute()
            wrapper._state["opened_at"] = time.monotonic() - 2
            self.assertEqual(wrapper.execute(), "recovered")
        self.assertEqual(wrapper.resilience_state()["circuit"], "closed")

    def test_half_open_failure_reopens_circuit(self):
        wrapper, _target, context = self.wrapper(
            SequenceTool([RuntimeError("open"), RuntimeError("probe")]),
            circuit_failure_threshold=1,
            circuit_recovery_seconds=1,
        )
        with context:
            with self.assertRaises(RuntimeError):
                wrapper.execute()
            wrapper._state["opened_at"] = time.monotonic() - 2
            with self.assertRaisesRegex(RuntimeError, "probe"):
                wrapper.execute()
        self.assertEqual(wrapper.resilience_state()["circuit"], "open")

    def test_open_circuit_uses_fallback(self):
        wrapper, _target, context = self.wrapper(
            SequenceTool([RuntimeError("open")]),
            circuit_failure_threshold=1,
            fallback_enabled=True,
            fallback_value="fallback",
        )
        with context:
            self.assertEqual(wrapper.execute(), "fallback")
            self.assertEqual(wrapper.execute(), "fallback")
        self.assertEqual(wrapper.resilience_state()["fallbacks"], 2)

    def test_reset_state(self):
        wrapper, _target, context = self.wrapper(SequenceTool([RuntimeError("fail")]))
        with context, self.assertRaises(RuntimeError):
            wrapper.execute()
        wrapper.reset_resilience_state()
        state = wrapper.resilience_state()
        self.assertEqual(state["calls"], 0)
        self.assertEqual(state["circuit"], "closed")
        self.assertIsNone(state["last_error"])

    def test_tool_copies_share_circuit_state(self):
        wrapper, _target, _context = self.wrapper(SequenceTool([]))
        copied = wrapper.create_copy()
        self.assertIs(copied._state, wrapper._state)
        self.assertIs(copied._state_lock, wrapper._state_lock)


class TestResilientValidation(ResilientTestCase):
    def test_target_is_required(self):
        with self.assertRaisesRegex(ValueError, "target_tool"):
            ResilientTool().execute()

    def test_missing_target_is_descriptive(self):
        wrapper = ResilientTool(name="wrapper", target_tool="missing", timeout_seconds=None)
        with (
            patch("agentuniverse.agent.action.tool.resilient_tool.ToolManager", new=FakeManager({})),
            self.assertRaisesRegex(ValueError, "not registered"),
        ):
            wrapper.execute()

    def test_self_reference_is_rejected(self):
        wrapper = ResilientTool(name="same", target_tool="same")
        with self.assertRaisesRegex(ValueError, "must not reference"):
            wrapper.execute()

    def test_invalid_policy_values(self):
        for kwargs, message in (
            ({"max_attempts": 0}, "max_attempts"),
            ({"timeout_seconds": 0}, "timeout_seconds"),
            ({"backoff_multiplier": 0.5}, "backoff_multiplier"),
            ({"retry_exception_names": ["bad.name"]}, "retry_exception_names"),
        ):
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, message):
                ResilientTool(target_tool="target", **kwargs).execute()

    def test_component_schema(self):
        config = Configer()
        config.value = {
            "name": "resilient_search",
            "target_tool": "search",
            "metadata": {
                "type": "TOOL",
                "module": "agentuniverse.agent.action.tool.resilient_tool",
                "class": "ResilientTool",
            },
        }
        component = ComponentConfiger().load_by_configer(config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "ResilientTool")


if __name__ == "__main__":
    unittest.main()
