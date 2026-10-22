"""Known-answer and discipline tests for TinyBalancePointTool (au1k #8)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_8_tiny_balance_point import TinyBalancePointTool


class TestTinyBalancePointTool(unittest.TestCase):
    def _tool(self):
        return TinyBalancePointTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='alpha beta gamma delta')["result"], {'metric': 'len', 'index': 11, 'found': True, 'left_mass': 11, 'right_mass': 11, 'imbalance': 0.0, 'candidates': 1, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'metric': 'len', 'index': -1, 'found': False, 'left_mass': 0, 'right_mass': 39, 'imbalance': 100.0, 'candidates': 0, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='alpha beta gamma delta')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'metric': 'len', 'index': 11, 'found': True, 'left_mass': 11, 'right_mass': 11, 'imbalance': 0.0, 'candidates': 1, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 8)
        self.assertEqual(meta["algo"], 'au_algo_008')
        self.assertEqual(meta["params"], {'p1': 50, 'p2': 2, 'p3': True, 'p4': 'len'})
        self.assertEqual(meta["semantic"], 'tiny_balance_point')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='alpha beta gamma delta', p1=50, p2=2, p3=True, p4='len')["result"], {'metric': 'len', 'index': 11, 'found': True, 'left_mass': 11, 'right_mass': 11, 'imbalance': 0.0, 'candidates': 1, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='alpha beta gamma delta')["result"]
        two = tool.execute(action="run", x='alpha beta gamma delta')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='alpha beta gamma delta')


if __name__ == "__main__":
    unittest.main()
