# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/22
# @Author  : Zzzzzmeow
# @FileName: test_is_work_pattern.py
"""Unit tests for the IS work pattern correction loop.

Covers two behaviours of ISWorkPattern.invoke / async_invoke:
- a computed correction is fed back into the loop (the next implementation and
  supervision round build on the corrected content, not the discarded one);
- the `corrected` flag in checkpoint_history reports whether a correction
  actually ran, instead of echoing needs_correction.
"""

import asyncio
import unittest
from typing import ClassVar

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.implementation_agent_template import ImplementationAgentTemplate
from agentuniverse.agent.template.supervision_agent_template import SupervisionAgentTemplate
from agentuniverse.agent.work_pattern.is_work_pattern import ISWorkPattern


class ScriptedImplementationAgent(ImplementationAgentTemplate):
    """Implementation mock: echoes the implementation_result it received."""

    def run(self, **kwargs) -> OutputObject:
        return OutputObject(self._result(kwargs))

    async def async_run(self, **kwargs) -> OutputObject:
        return OutputObject(self._result(kwargs))

    @staticmethod
    def _result(kwargs: dict) -> dict:
        if kwargs.get('correction_mode'):
            return {'output': 'CORRECTED', 'checkpoint_output': 'CORRECTED'}
        previous = kwargs.get('implementation_result')
        previous_output = None
        if previous is not None and hasattr(previous, 'get_data'):
            previous_output = previous.get_data('output')
        idx = kwargs.get('checkpoint_index', 0)
        base = f'IMPL_{idx}_on_{previous_output}' if previous_output else f'IMPL_{idx}'
        return {'output': base, 'checkpoint_output': base}


class ScriptedSupervisionAgent(SupervisionAgentTemplate):
    """Supervision mock: scripted needs_correction per checkpoint, echoes reviewed content."""

    correction_plan: ClassVar[list] = []

    def run(self, **kwargs) -> OutputObject:
        return OutputObject(self._result(kwargs))

    async def async_run(self, **kwargs) -> OutputObject:
        return OutputObject(self._result(kwargs))

    @staticmethod
    def _result(kwargs: dict) -> dict:
        idx = kwargs.get('checkpoint_index', 0)
        plan = ScriptedSupervisionAgent.correction_plan
        needs_correction = plan[idx] if idx < len(plan) else False
        reviewed = kwargs.get('implementation_result')
        reviewed_output = 'NONE'
        if reviewed is not None and hasattr(reviewed, 'get_data'):
            reviewed_output = reviewed.get_data('output')
        return {
            'needs_correction': needs_correction,
            'feedback': f'review:{reviewed_output}',
            'score': 0.5,
        }


class TestISWorkPatternCorrectionLoop(unittest.TestCase):
    """Test corrections are applied and reported truthfully."""

    def setUp(self):
        ScriptedSupervisionAgent.correction_plan = []
        self.pattern = ISWorkPattern()
        self.pattern.implementation = ScriptedImplementationAgent()
        self.pattern.supervision = ScriptedSupervisionAgent()

    def _invoke(self, checkpoint_count, max_corrections, plan):
        ScriptedSupervisionAgent.correction_plan = plan
        input_object = InputObject({'input': 'build the thing'})
        work_pattern_input = {
            'input': 'build the thing',
            'checkpoint_count': checkpoint_count,
            'max_corrections': max_corrections,
        }
        return self.pattern.invoke(input_object, work_pattern_input)

    def _async_invoke(self, checkpoint_count, max_corrections, plan):
        ScriptedSupervisionAgent.correction_plan = plan
        input_object = InputObject({'input': 'build the thing'})
        work_pattern_input = {
            'input': 'build the thing',
            'checkpoint_count': checkpoint_count,
            'max_corrections': max_corrections,
        }
        return asyncio.run(self.pattern.async_invoke(input_object, work_pattern_input))

    def test_correction_feeds_next_checkpoint(self):
        """The corrected content must reach the next implementation and supervision round."""
        result = self._invoke(checkpoint_count=2, max_corrections=2, plan=[True, False])

        results = result['result']
        history = result['execution_context']['checkpoint_history']

        # Checkpoint 0: implementation, review, correction.
        self.assertEqual(results[0]['implementation_result']['output'], 'IMPL_0')
        self.assertEqual(results[0]['supervision_result']['feedback'], 'review:IMPL_0')
        self.assertEqual(results[0]['correction_result']['output'], 'CORRECTED')

        # Checkpoint 1 must build on the corrected content, not on IMPL_0.
        self.assertEqual(results[1]['implementation_result']['output'], 'IMPL_1_on_CORRECTED')
        self.assertEqual(results[1]['supervision_result']['feedback'], 'review:IMPL_1_on_CORRECTED')

        # History reflects the corrected checkpoint state.
        self.assertTrue(history[0]['corrected'])
        self.assertEqual(history[0]['implementation']['output'], 'CORRECTED')
        self.assertFalse(history[1]['corrected'])
        self.assertEqual(history[1]['implementation']['output'], 'IMPL_1_on_CORRECTED')
        self.assertEqual(result['execution_context']['corrections_made'], 1)

    def test_correction_feeds_next_checkpoint_async(self):
        """async_invoke must behave identically to invoke."""
        result = self._async_invoke(checkpoint_count=2, max_corrections=2, plan=[True, False])

        self.assertEqual(result['result'][0]['correction_result']['output'], 'CORRECTED')
        self.assertEqual(result['result'][1]['implementation_result']['output'], 'IMPL_1_on_CORRECTED')
        self.assertTrue(result['execution_context']['checkpoint_history'][0]['corrected'])
        self.assertFalse(result['execution_context']['checkpoint_history'][1]['corrected'])

    def test_corrected_flag_false_when_budget_exhausted(self):
        """When the correction budget is exhausted the checkpoint must not report corrected=True."""
        result = self._invoke(checkpoint_count=3, max_corrections=1, plan=[True, True, True])

        history = result['execution_context']['checkpoint_history']
        self.assertEqual(result['execution_context']['corrections_made'], 1)
        self.assertTrue(history[0]['corrected'])
        self.assertFalse(history[1]['corrected'])
        self.assertFalse(history[2]['corrected'])
        # No correction actually ran after the budget was spent.
        self.assertNotIn('correction_result', result['result'][1])
        self.assertNotIn('correction_result', result['result'][2])

    def test_corrected_flag_false_when_budget_exhausted_async(self):
        """async_invoke must also report corrections truthfully under budget exhaustion."""
        result = self._async_invoke(checkpoint_count=3, max_corrections=1, plan=[True, True, True])

        history = result['execution_context']['checkpoint_history']
        self.assertEqual(result['execution_context']['corrections_made'], 1)
        self.assertTrue(history[0]['corrected'])
        self.assertFalse(history[1]['corrected'])
        self.assertFalse(history[2]['corrected'])

    def test_no_correction_flow(self):
        """Without supervision requests nothing is corrected and nothing is reported as corrected."""
        result = self._invoke(checkpoint_count=2, max_corrections=2, plan=[False, False])

        history = result['execution_context']['checkpoint_history']
        self.assertEqual(result['execution_context']['corrections_made'], 0)
        self.assertFalse(any(entry['corrected'] for entry in history))
        for checkpoint_result in result['result']:
            self.assertNotIn('correction_result', checkpoint_result)


if __name__ == "__main__":
    unittest.main()
