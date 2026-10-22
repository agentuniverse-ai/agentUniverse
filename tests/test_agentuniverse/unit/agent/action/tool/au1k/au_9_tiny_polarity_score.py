"""Known-answer and discipline tests for TinyPolarityScoreTool (au1k #9)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_9_tiny_polarity_score import TinyPolarityScoreTool


class TestTinyPolarityScoreTool(unittest.TestCase):
    def _tool(self):
        return TinyPolarityScoreTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='the good tool is fast but the docs are broken')["result"], {'lexicon': 'posneg', 'tokens': 10, 'positive': 2, 'negative': 1, 'score': 0.1, 'label': 'positive', 'hits': [{'token': 'good', 'polarity': 1}, {'token': 'fast', 'polarity': 1}, {'token': 'broken', 'polarity': -1}], 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'lexicon': 'posneg', 'tokens': 10, 'positive': 1, 'negative': 0, 'score': 0.1, 'label': 'positive', 'hits': [{'token': 'fast', 'polarity': 1}], 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='the good tool is fast but the docs are broken')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'lexicon': 'posneg', 'tokens': 10, 'positive': 2, 'negative': 1, 'score': 0.1, 'label': 'positive', 'hits': [{'token': 'good', 'polarity': 1}, {'token': 'fast', 'polarity': 1}, {'token': 'broken', 'polarity': -1}], 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 9)
        self.assertEqual(meta["algo"], 'au_algo_009')
        self.assertEqual(meta["params"], {'p1': 20, 'p2': 1, 'p3': True, 'p4': 'posneg'})
        self.assertEqual(meta["semantic"], 'tiny_polarity_score')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='the good tool is fast but the docs are broken', p1=20, p2=1, p3=True, p4='posneg')["result"], {'lexicon': 'posneg', 'tokens': 10, 'positive': 2, 'negative': 1, 'score': 0.1, 'label': 'positive', 'hits': [{'token': 'good', 'polarity': 1}, {'token': 'fast', 'polarity': 1}, {'token': 'broken', 'polarity': -1}], 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='the good tool is fast but the docs are broken')["result"]
        two = tool.execute(action="run", x='the good tool is fast but the docs are broken')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='the good tool is fast but the docs are broken')


if __name__ == "__main__":
    unittest.main()
