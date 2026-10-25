"""Known-answer and discipline tests for TinyEditNeighborhoodTool (au1k #12)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_12_tiny_edit_neighborhood import TinyEditNeighborhoodTool


class TestTinyEditNeighborhoodTool(unittest.TestCase):
    def _tool(self):
        return TinyEditNeighborhoodTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['colour', 'color', 'kalor', 'green'])["result"], {'metric': 'levenshtein', 'pivot': 'colour', 'items': 4, 'within': 0, 'ratio': 0.0, 'histogram': {'1': 3}, 'neighbours': [], 'max_distance': 1, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'metric': 'levenshtein', 'pivot': 'the', 'items': 10, 'within': 2, 'ratio': 0.2222, 'histogram': {'1': 7, '0': 2}, 'neighbours': [{'token': 'the', 'distance': 0}, {'token': 'the', 'distance': 0}], 'max_distance': 1, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['colour', 'color', 'kalor', 'green'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'metric': 'levenshtein', 'pivot': 'colour', 'items': 4, 'within': 1, 'ratio': 0.3333, 'histogram': {'1': 1, '2': 2}, 'neighbours': [{'token': 'color', 'distance': 1}], 'max_distance': 2, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 12)
        self.assertEqual(meta["algo"], 'au_algo_012')
        self.assertEqual(meta["params"], {'p1': 0, 'p2': 10, 'p3': True, 'p4': 'levenshtein'})
        self.assertEqual(meta["semantic"], 'tiny_edit_neighborhood')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['colour', 'color', 'kalor', 'green'], p1=0, p2=10, p3=True, p4='levenshtein')["result"], {'metric': 'levenshtein', 'pivot': 'colour', 'items': 4, 'within': 0, 'ratio': 0.0, 'histogram': {'1': 3}, 'neighbours': [], 'max_distance': 1, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['colour', 'color', 'kalor', 'green'])["result"]
        two = tool.execute(action="run", x=['colour', 'color', 'kalor', 'green'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['colour', 'color', 'kalor', 'green'])


if __name__ == "__main__":
    unittest.main()
