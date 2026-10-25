"""Known-answer and discipline tests for TinyMonotoneRunTool (au1k #11)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_11_tiny_monotone_run import TinyMonotoneRunTool


class TestTinyMonotoneRunTool(unittest.TestCase):
    def _tool(self):
        return TinyMonotoneRunTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])["result"], {'direction': 'up', 'values': 10, 'runs': [{'start': 0, 'end': 3, 'length': 4, 'trend': 'up'}, {'start': 6, 'end': 9, 'length': 4, 'trend': 'up'}], 'run_count': 2, 'longest_run': 4, 'coverage': 0.8, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])["result"], {'direction': 'up', 'values': 10, 'runs': [{'start': 0, 'end': 3, 'length': 4, 'trend': 'up'}, {'start': 6, 'end': 9, 'length': 4, 'trend': 'up'}], 'run_count': 2, 'longest_run': 4, 'coverage': 0.8, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'direction': 'up', 'values': 10, 'runs': [{'start': 0, 'end': 3, 'length': 4, 'trend': 'up'}, {'start': 6, 'end': 9, 'length': 4, 'trend': 'up'}], 'run_count': 2, 'longest_run': 4, 'coverage': 0.8, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 11)
        self.assertEqual(meta["algo"], 'au_algo_011')
        self.assertEqual(meta["params"], {'p1': 2, 'p2': 10, 'p3': True, 'p4': 'up'})
        self.assertEqual(meta["semantic"], 'tiny_monotone_run')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10], p1=2, p2=10, p3=True, p4='up')["result"], {'direction': 'up', 'values': 10, 'runs': [{'start': 0, 'end': 3, 'length': 4, 'trend': 'up'}, {'start': 6, 'end': 9, 'length': 4, 'trend': 'up'}], 'run_count': 2, 'longest_run': 4, 'coverage': 0.8, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])["result"]
        two = tool.execute(action="run", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])


if __name__ == "__main__":
    unittest.main()
