"""Known-answer and discipline tests for TinyCyclicShiftTool (au1k #13)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_13_tiny_cyclic_shift import TinyCyclicShiftTool


class TestTinyCyclicShiftTool(unittest.TestCase):
    def _tool(self):
        return TinyCyclicShiftTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='abcabcabc')["result"], {'map': 'identity', 'length': 9, 'max_shift': 2, 'tested': 2, 'fixed_points': 2, 'periodic_shifts': 0, 'min_period': 3, 'samples': [{'shift': 1, 'text': 'bcabcabca', 'fixed': True}, {'shift': 2, 'text': 'cabcabcab', 'fixed': True}], 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'map': 'identity', 'length': 12, 'max_shift': 2, 'tested': 2, 'fixed_points': 2, 'periodic_shifts': 0, 'min_period': 12, 'samples': [{'shift': 1, 'text': 'he cat sat t', 'fixed': True}, {'shift': 2, 'text': 'e cat sat th', 'fixed': True}], 'truncated': True})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='abcabcabc')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'map': 'identity', 'length': 9, 'max_shift': 3, 'tested': 3, 'fixed_points': 3, 'periodic_shifts': 1, 'min_period': 3, 'samples': [{'shift': 1, 'text': 'bcabcabca', 'fixed': True}, {'shift': 2, 'text': 'cabcabcab', 'fixed': True}, {'shift': 3, 'text': 'abcabcabc', 'fixed': True}], 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 13)
        self.assertEqual(meta["algo"], 'au_algo_013')
        self.assertEqual(meta["params"], {'p1': 2, 'p2': 12, 'p3': True, 'p4': 'identity'})
        self.assertEqual(meta["semantic"], 'tiny_cyclic_shift')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='abcabcabc', p1=2, p2=12, p3=True, p4='identity')["result"], {'map': 'identity', 'length': 9, 'max_shift': 2, 'tested': 2, 'fixed_points': 2, 'periodic_shifts': 0, 'min_period': 3, 'samples': [{'shift': 1, 'text': 'bcabcabca', 'fixed': True}, {'shift': 2, 'text': 'cabcabcab', 'fixed': True}], 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='abcabcabc')["result"]
        two = tool.execute(action="run", x='abcabcabc')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='abcabcabc')


if __name__ == "__main__":
    unittest.main()
