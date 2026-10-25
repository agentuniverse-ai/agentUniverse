"""Known-answer and discipline tests for TinyOrdinalSuffixTool (au1k #25)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_25_tiny_ordinal_suffix import TinyOrdinalSuffixTool


class TestTinyOrdinalSuffixTool(unittest.TestCase):
    def _tool(self):
        return TinyOrdinalSuffixTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=[1, 2, 3, 11, 12, 13, 21])["result"], {'style': 'short', 'items': 7, 'formatted': ['1st', '2nd', '3rd', '11th', '12th', '13th', '21st'], 'suffix_counts': {'st': 2, 'nd': 1, 'rd': 1, 'th': 3}, 'teen_exceptions': 3, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])["result"], {'style': 'short', 'items': 10, 'formatted': ['1st', '2nd', '3rd', '5th', '4th', '3rd', '2nd', '9th', '9th', '10th'], 'suffix_counts': {'st': 1, 'nd': 2, 'rd': 2, 'th': 5}, 'teen_exceptions': 0, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=[1, 2, 3, 11, 12, 13, 21])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'style': 'short', 'items': 7, 'formatted': ['1st', '2nd', '3rd', '11th', '12th', '13th', '21st'], 'suffix_counts': {'st': 2, 'nd': 1, 'rd': 1, 'th': 3}, 'teen_exceptions': 3, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 25)
        self.assertEqual(meta["algo"], 'au_algo_025')
        self.assertEqual(meta["params"], {'p1': 100, 'p2': 10, 'p3': True, 'p4': 'short'})
        self.assertEqual(meta["semantic"], 'tiny_ordinal_suffix')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=[1, 2, 3, 11, 12, 13, 21], p1=100, p2=10, p3=True, p4='short')["result"], {'style': 'short', 'items': 7, 'formatted': ['1st', '2nd', '3rd', '11th', '12th', '13th', '21st'], 'suffix_counts': {'st': 2, 'nd': 1, 'rd': 1, 'th': 3}, 'teen_exceptions': 3, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=[1, 2, 3, 11, 12, 13, 21])["result"]
        two = tool.execute(action="run", x=[1, 2, 3, 11, 12, 13, 21])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=[1, 2, 3, 11, 12, 13, 21])


if __name__ == "__main__":
    unittest.main()
