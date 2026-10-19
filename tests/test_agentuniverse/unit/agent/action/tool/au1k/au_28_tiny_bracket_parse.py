"""Known-answer and discipline tests for TinyBracketParseTool (au1k #28)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_28_tiny_bracket_parse import TinyBracketParseTool


class TestTinyBracketParseTool(unittest.TestCase):
    def _tool(self):
        return TinyBracketParseTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='(a[b]{c})')["result"], {'alphabet': 'round', 'ok': True, 'pairs': 1, 'max_depth': 1, 'over_depth': False, 'first_error': None, 'unclosed': [], 'depth_profile': [1, 0], 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'alphabet': 'round', 'ok': True, 'pairs': 0, 'max_depth': 0, 'over_depth': False, 'first_error': None, 'unclosed': [], 'depth_profile': [], 'truncated': True})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='(a[b]{c})')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'alphabet': 'round', 'ok': True, 'pairs': 1, 'max_depth': 1, 'over_depth': False, 'first_error': None, 'unclosed': [], 'depth_profile': [1, 0], 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 28)
        self.assertEqual(meta["algo"], 'au_algo_028')
        self.assertEqual(meta["params"], {'p1': 3, 'p2': 20, 'p3': True, 'p4': 'round'})
        self.assertEqual(meta["semantic"], 'tiny_bracket_parse')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='(a[b]{c})', p1=3, p2=20, p3=True, p4='round')["result"], {'alphabet': 'round', 'ok': True, 'pairs': 1, 'max_depth': 1, 'over_depth': False, 'first_error': None, 'unclosed': [], 'depth_profile': [1, 0], 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='(a[b]{c})')["result"]
        two = tool.execute(action="run", x='(a[b]{c})')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='(a[b]{c})')


if __name__ == "__main__":
    unittest.main()
