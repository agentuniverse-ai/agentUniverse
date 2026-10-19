"""Known-answer and discipline tests for TinyIntervalNameTool (au1k #24)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_24_tiny_interval_name import TinyIntervalNameTool


class TestTinyIntervalNameTool(unittest.TestCase):
    def _tool(self):
        return TinyIntervalNameTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=[0, 3, 7, 11])["result"], {'style': 'classic', 'items': 4, 'results': [{'semitones': 0, 'name': 'unison', 'quality': 'perfect', 'inversion': 0, 'compound': False}, {'semitones': 3, 'name': 'minor 3rd', 'quality': 'minor', 'inversion': 9, 'compound': False}, {'semitones': 7, 'name': 'perfect 5th', 'quality': 'perfect', 'inversion': 5, 'compound': False}, {'semitones': 11, 'name': 'major 7th', 'quality': 'major', 'inversion': 1, 'compound': False}], 'quality_counts': {'perfect': 2, 'minor': 1, 'major': 1}, 'compound_count': 0, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])["result"], {'style': 'classic', 'items': 5, 'results': [{'semitones': 1, 'name': 'minor 2nd', 'quality': 'minor', 'inversion': 11, 'compound': False}, {'semitones': 2, 'name': 'major 2nd', 'quality': 'major', 'inversion': 10, 'compound': False}, {'semitones': 3, 'name': 'minor 3rd', 'quality': 'minor', 'inversion': 9, 'compound': False}, {'semitones': 5, 'name': 'perfect 4th', 'quality': 'perfect', 'inversion': 7, 'compound': False}, {'semitones': 4, 'name': 'major 3rd', 'quality': 'major', 'inversion': 8, 'compound': False}], 'quality_counts': {'minor': 2, 'major': 2, 'perfect': 1}, 'compound_count': 0, 'truncated': True})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=[0, 3, 7, 11])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'style': 'classic', 'items': 4, 'results': [{'semitones': 0, 'name': 'unison', 'quality': 'perfect', 'inversion': 0, 'compound': False}, {'semitones': 3, 'name': 'minor 3rd', 'quality': 'minor', 'inversion': 9, 'compound': False}, {'semitones': 7, 'name': 'perfect 5th', 'quality': 'perfect', 'inversion': 5, 'compound': False}, {'semitones': 11, 'name': 'major 7th', 'quality': 'major', 'inversion': 1, 'compound': False}], 'quality_counts': {'perfect': 2, 'minor': 1, 'major': 1}, 'compound_count': 0, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 24)
        self.assertEqual(meta["algo"], 'au_algo_024')
        self.assertEqual(meta["params"], {'p1': 12, 'p2': 5, 'p3': True, 'p4': 'classic'})
        self.assertEqual(meta["semantic"], 'tiny_interval_name')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=[0, 3, 7, 11], p1=12, p2=5, p3=True, p4='classic')["result"], {'style': 'classic', 'items': 4, 'results': [{'semitones': 0, 'name': 'unison', 'quality': 'perfect', 'inversion': 0, 'compound': False}, {'semitones': 3, 'name': 'minor 3rd', 'quality': 'minor', 'inversion': 9, 'compound': False}, {'semitones': 7, 'name': 'perfect 5th', 'quality': 'perfect', 'inversion': 5, 'compound': False}, {'semitones': 11, 'name': 'major 7th', 'quality': 'major', 'inversion': 1, 'compound': False}], 'quality_counts': {'perfect': 2, 'minor': 1, 'major': 1}, 'compound_count': 0, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=[0, 3, 7, 11])["result"]
        two = tool.execute(action="run", x=[0, 3, 7, 11])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=[0, 3, 7, 11])


if __name__ == "__main__":
    unittest.main()
