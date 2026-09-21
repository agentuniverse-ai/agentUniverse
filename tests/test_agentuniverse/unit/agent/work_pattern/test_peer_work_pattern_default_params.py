# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/9/21
# @FileName: test_peer_work_pattern_default_params.py
import asyncio
import unittest

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.reviewing_agent_template import \
    ReviewingAgentTemplate
from agentuniverse.agent.work_pattern.peer_work_pattern import PeerWorkPattern


class FakeReviewAgent(ReviewingAgentTemplate):
    """Reviewing agent stub returning a configurable score."""

    score: int = 0

    def __init__(self, score=0):
        super().__init__()
        self.score = score

    def run(self, **kwargs):
        return OutputObject({'score': self.score, 'output': 'review'})

    async def async_run(self, **kwargs):
        return self.run()


class TestPeerWorkPatternDefaultParams(unittest.TestCase):
    """work_pattern_input may carry None values (yaml nulls or user kwargs
    injected through parse_input), so the loop parameters must tolerate
    None like GRRWorkPattern's defaults do."""

    def _pattern(self):
        return PeerWorkPattern()

    def test_invoke_none_retry_count_runs_default_rounds(self):
        pattern = self._pattern()
        pattern.reviewing = FakeReviewAgent()
        result = pattern.invoke(InputObject({'input': 'x'}),
                                {'input': 'x', 'retry_count': None,
                                 'jump_step': None, 'eval_threshold': None})
        rounds = len(result['result'])
        self.assertGreaterEqual(rounds, 1)
        self.assertLessEqual(rounds, 2)

    def test_invoke_missing_retry_count_runs_default_rounds(self):
        pattern = self._pattern()
        pattern.reviewing = FakeReviewAgent()
        result = pattern.invoke(InputObject({'input': 'x'}), {'input': 'x'})
        self.assertGreaterEqual(len(result['result']), 1)

    def test_invoke_returns_when_score_meets_threshold(self):
        pattern = self._pattern()
        pattern.reviewing = FakeReviewAgent(score=99)
        result = pattern.invoke(InputObject({'input': 'x'}),
                                {'input': 'x', 'retry_count': 3,
                                 'jump_step': None, 'eval_threshold': 60})
        self.assertEqual(1, len(result['result']))

    def test_async_invoke_none_retry_count_runs_default_rounds(self):
        pattern = self._pattern()
        pattern.reviewing = FakeReviewAgent()
        result = asyncio.run(pattern.async_invoke(
            InputObject({'input': 'x'}),
            {'input': 'x', 'retry_count': None, 'jump_step': None,
             'eval_threshold': None}))
        self.assertGreaterEqual(len(result['result']), 1)


if __name__ == '__main__':
    unittest.main()
