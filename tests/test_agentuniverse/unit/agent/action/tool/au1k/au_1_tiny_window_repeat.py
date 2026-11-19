"""Known-answer and discipline tests for TinyWindowRepeatTool (au1k #1)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_1_tiny_window_repeat import TinyWindowRepeatTool


class TestTinyWindowRepeatTool(unittest.TestCase):
    def _tool(self):
        return TinyWindowRepeatTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'mode': 'word', 'window': 3, 'units': 10, 'windows': 8, 'distinct_windows': 8, 'repeated_windows': 0, 'repeat_ratio': 0.0, 'top_repeated': [], 'casefolded': True, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'mode': 'word', 'window': 3, 'units': 10, 'windows': 8, 'distinct_windows': 8, 'repeated_windows': 0, 'repeat_ratio': 0.0, 'top_repeated': [], 'casefolded': True, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='the cat sat on the mat the cat ran fast')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'mode': 'word', 'window': 4, 'units': 10, 'windows': 7, 'distinct_windows': 7, 'repeated_windows': 0, 'repeat_ratio': 0.0, 'top_repeated': [], 'casefolded': True, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 1)
        self.assertEqual(meta["algo"], 'au_algo_001')
        self.assertEqual(meta["params"], {'p1': 3, 'p2': 60, 'p3': True, 'p4': 'word'})
        self.assertEqual(meta["semantic"], 'tiny_window_repeat')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast', p1=3, p2=60, p3=True, p4='word')["result"], {'mode': 'word', 'window': 3, 'units': 10, 'windows': 8, 'distinct_windows': 8, 'repeated_windows': 0, 'repeat_ratio': 0.0, 'top_repeated': [], 'casefolded': True, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"]
        two = tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='the cat sat on the mat the cat ran fast')


if __name__ == "__main__":
    unittest.main()
