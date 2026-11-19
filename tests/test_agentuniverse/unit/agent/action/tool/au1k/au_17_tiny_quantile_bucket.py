"""Known-answer and discipline tests for TinyQuantileBucketTool (au1k #17)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_17_tiny_quantile_bucket import TinyQuantileBucketTool


class TestTinyQuantileBucketTool(unittest.TestCase):
    def _tool(self):
        return TinyQuantileBucketTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=[1, 2, 2, 3, 5, 8, 13, 21])["result"], {'bins': 2, 'method': 'linear', 'count': 8, 'edges': [1.0, 4.0, 21.0], 'counts': [4, 4], 'labels': ['q0-q1', 'q1-q2'], 'median': 4.0, 'iqr': 7.0, 'empty_bins': 0, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])["result"], {'bins': 2, 'method': 'linear', 'count': 10, 'edges': [1.0, 4.0, 10.0], 'counts': [5, 5], 'labels': ['q0-q1', 'q1-q2'], 'median': 4.0, 'iqr': 6.0, 'empty_bins': 0, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=[1, 2, 2, 3, 5, 8, 13, 21])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'bins': 3, 'method': 'linear', 'count': 8, 'edges': [1.0, 2.0, 7.0, 21.0], 'counts': [3, 2, 3], 'labels': ['q0-q1', 'q1-q2', 'q2-q3'], 'median': 4.0, 'iqr': 7.0, 'empty_bins': 0, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 17)
        self.assertEqual(meta["algo"], 'au_algo_017')
        self.assertEqual(meta["params"], {'p1': 2, 'p2': 0, 'p3': True, 'p4': 'linear'})
        self.assertEqual(meta["semantic"], 'tiny_quantile_bucket')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=[1, 2, 2, 3, 5, 8, 13, 21], p1=2, p2=0, p3=True, p4='linear')["result"], {'bins': 2, 'method': 'linear', 'count': 8, 'edges': [1.0, 4.0, 21.0], 'counts': [4, 4], 'labels': ['q0-q1', 'q1-q2'], 'median': 4.0, 'iqr': 7.0, 'empty_bins': 0, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=[1, 2, 2, 3, 5, 8, 13, 21])["result"]
        two = tool.execute(action="run", x=[1, 2, 2, 3, 5, 8, 13, 21])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=[1, 2, 2, 3, 5, 8, 13, 21])


if __name__ == "__main__":
    unittest.main()
