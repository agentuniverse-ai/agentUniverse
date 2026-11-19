"""Known-answer and discipline tests for TinyDedupeSketchTool (au1k #10)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_10_tiny_dedupe_sketch import TinyDedupeSketchTool


class TestTinyDedupeSketchTool(unittest.TestCase):
    def _tool(self):
        return TinyDedupeSketchTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='a b c\n\na b c\n\nx y z')["result"], {'mode': 'shingle', 'paragraphs': 3, 'kept': 2, 'duplicates': 1, 'duplicate_ratio': 0.3333, 'groups': [{'kept': 1, 'drop': 2, 'overlap': 1.0}], 'signatures': ['a b c', 'x y z'], 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'mode': 'shingle', 'paragraphs': 1, 'kept': 1, 'duplicates': 0, 'duplicate_ratio': 0.0, 'groups': [], 'signatures': ['the cat sat on the mat the cat ran fast'], 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='a b c\n\na b c\n\nx y z')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'mode': 'shingle', 'paragraphs': 3, 'kept': 2, 'duplicates': 1, 'duplicate_ratio': 0.3333, 'groups': [{'kept': 1, 'drop': 2, 'overlap': 1.0}], 'signatures': ['a b c', 'x y z'], 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 10)
        self.assertEqual(meta["algo"], 'au_algo_010')
        self.assertEqual(meta["params"], {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'shingle'})
        self.assertEqual(meta["semantic"], 'tiny_dedupe_sketch')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='a b c\n\na b c\n\nx y z', p1=1, p2=10, p3=True, p4='shingle')["result"], {'mode': 'shingle', 'paragraphs': 3, 'kept': 2, 'duplicates': 1, 'duplicate_ratio': 0.3333, 'groups': [{'kept': 1, 'drop': 2, 'overlap': 1.0}], 'signatures': ['a b c', 'x y z'], 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='a b c\n\na b c\n\nx y z')["result"]
        two = tool.execute(action="run", x='a b c\n\na b c\n\nx y z')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='a b c\n\na b c\n\nx y z')


if __name__ == "__main__":
    unittest.main()
