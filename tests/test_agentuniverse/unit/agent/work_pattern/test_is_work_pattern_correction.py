# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""The IS supervision loop must keep the correction it computes."""

import asyncio
import unittest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.implementation_agent_template import ImplementationAgentTemplate
from agentuniverse.agent.template.is_agent_template import ISAgentTemplate
from agentuniverse.agent.template.supervision_agent_template import SupervisionAgentTemplate
from agentuniverse.agent.work_pattern.is_work_pattern import ISWorkPattern


class ScriptedImplementation(ImplementationAgentTemplate):
    """Implementation agent that returns queued outputs without calling an LLM."""

    def __init__(self, outputs):
        super().__init__()
        object.__setattr__(self, "outputs", list(outputs))
        object.__setattr__(self, "calls", [])

    def run(self, **kwargs):
        self.calls.append(kwargs)
        output = self.outputs.pop(0)
        return OutputObject({"output": output, "checkpoint_output": output})

    async def async_run(self, **kwargs):
        return self.run(**kwargs)


class ScriptedSupervision(SupervisionAgentTemplate):
    """Supervision agent that returns queued decisions without calling an LLM."""

    def __init__(self, decisions):
        super().__init__()
        object.__setattr__(self, "decisions", list(decisions))

    def run(self, **kwargs):
        return OutputObject(self.decisions.pop(0))

    async def async_run(self, **kwargs):
        return self.run(**kwargs)


class ISWorkPatternCorrectionTest(unittest.TestCase):
    def _pattern(self, outputs, decisions):
        pattern = ISWorkPattern()
        pattern.implementation = ScriptedImplementation(outputs)
        pattern.supervision = ScriptedSupervision(decisions)
        return pattern

    def test_correction_feeds_next_checkpoint(self):
        pattern = self._pattern(
            ["draft", "corrected draft", "final"],
            [
                {"needs_correction": True, "feedback": "revise the draft", "score": 1},
                {"needs_correction": False, "feedback": "", "score": 5},
            ],
        )
        result = pattern.invoke(
            InputObject({"input": "write the report"}),
            {"input": "write the report", "checkpoint_count": 2, "max_corrections": 2},
        )

        history = result["execution_context"]["checkpoint_history"]
        self.assertEqual(result["execution_context"]["corrections_made"], 1)
        self.assertEqual(history[0]["implementation"]["checkpoint_output"], "corrected draft")
        self.assertTrue(history[0]["corrected"])
        self.assertEqual(
            result["result"][0]["implementation_result"]["checkpoint_output"],
            "corrected draft",
        )
        self.assertEqual(
            result["result"][0]["correction_result"]["checkpoint_output"],
            "corrected draft",
        )

        next_context = pattern.implementation.calls[2]["execution_context"]
        self.assertEqual(
            next_context["checkpoint_history"][0]["implementation"]["checkpoint_output"],
            "corrected draft",
        )
        self.assertTrue(pattern.implementation.calls[1]["correction_mode"])
        self.assertFalse(pattern.implementation.calls[2].get("correction_mode", False))

    def test_correction_is_not_counted_when_limit_is_reached(self):
        pattern = self._pattern(
            ["draft"],
            [{"needs_correction": True, "feedback": "revise", "score": 1}],
        )
        result = pattern.invoke(
            InputObject({"input": "write the report"}),
            {"input": "write the report", "checkpoint_count": 1, "max_corrections": 0},
        )

        history = result["execution_context"]["checkpoint_history"]
        self.assertEqual(result["execution_context"]["corrections_made"], 0)
        self.assertEqual(history[0]["implementation"]["checkpoint_output"], "draft")
        self.assertFalse(history[0]["corrected"])
        self.assertNotIn("correction_result", result["result"][0])
        self.assertEqual(len(pattern.implementation.calls), 1)

    def test_async_correction_feeds_next_checkpoint(self):
        pattern = self._pattern(
            ["draft", "corrected draft"],
            [{"needs_correction": True, "feedback": "revise", "score": 1}],
        )
        result = asyncio.run(pattern.async_invoke(
            InputObject({"input": "write the report"}),
            {"input": "write the report", "checkpoint_count": 1, "max_corrections": 1},
        ))

        self.assertEqual(
            result["result"][0]["implementation_result"]["checkpoint_output"],
            "corrected draft",
        )
        self.assertEqual(result["execution_context"]["corrections_made"], 1)
        self.assertTrue(result["execution_context"]["checkpoint_history"][0]["corrected"])

    def test_final_output_uses_correction(self):
        parsed = ISAgentTemplate().parse_result({
            "result": [{
                "implementation_result": {"checkpoint_output": "draft"},
                "correction_result": {"checkpoint_output": "corrected draft"},
                "supervision_result": {
                    "needs_correction": True,
                    "feedback": "revise",
                    "score": 1,
                },
            }],
            "execution_context": {"corrections_made": 1},
        })
        self.assertEqual(parsed["output"], "corrected draft")


if __name__ == "__main__":
    unittest.main()
