"""Known-answer and discipline tests for TinyZipfRankTool (au1k #4)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_4_tiny_zipf_rank import TinyZipfRankTool


class TestTinyZipfRankTool(unittest.TestCase):
    def _tool(self):
        return TinyZipfRankTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='alpha beta beta gamma gamma gamma')["result"], {'tokens': 6, 'distinct': 3, 'top_tokens': [{'token': 'gamma', 'count': 3, 'rank': 1}], 'zipf_slope': 0.0, 'fit_error': 0.0, 'hapax_ratio': 0.3333, 'monotone_decay': True, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'tokens': 10, 'distinct': 7, 'top_tokens': [{'token': 'the', 'count': 3, 'rank': 1}], 'zipf_slope': 0.0, 'fit_error': 0.0, 'hapax_ratio': 0.7143, 'monotone_decay': True, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='alpha beta beta gamma gamma gamma')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'tokens': 6, 'distinct': 3, 'top_tokens': [{'token': 'gamma', 'count': 3, 'rank': 1}, {'token': 'beta', 'count': 2, 'rank': 2}], 'zipf_slope': -0.585, 'fit_error': 0.1667, 'hapax_ratio': 0.3333, 'monotone_decay': True, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 4)
        self.assertEqual(meta["algo"], 'au_algo_004')
        self.assertEqual(meta["params"], {'p1': 1, 'p2': 1, 'p3': True, 'p4': 'word'})
        self.assertEqual(meta["semantic"], 'tiny_zipf_rank')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='alpha beta beta gamma gamma gamma', p1=1, p2=1, p3=True, p4='word')["result"], {'tokens': 6, 'distinct': 3, 'top_tokens': [{'token': 'gamma', 'count': 3, 'rank': 1}], 'zipf_slope': 0.0, 'fit_error': 0.0, 'hapax_ratio': 0.3333, 'monotone_decay': True, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='alpha beta beta gamma gamma gamma')["result"]
        two = tool.execute(action="run", x='alpha beta beta gamma gamma gamma')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='alpha beta beta gamma gamma gamma')


if __name__ == "__main__":
    unittest.main()
