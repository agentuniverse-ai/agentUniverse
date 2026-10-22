"""Known-answer and discipline tests for TinyTopSelectTool (au1k #29)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_29_tiny_top_select import TinyTopSelectTool


class TestTinyTopSelectTool(unittest.TestCase):
    def _tool(self):
        return TinyTopSelectTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['a=1', 'b=3', 'c=3', 'd=2'])["result"], {'descending': True, 'k': 1, 'items': 4, 'selected': [{'name': 'b', 'score': 3.0, 'rank': 1}], 'cut_score': 3.0, 'cut_tie': True, 'dropped': 3, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=[1, 2, 3, 5, 4, 3, 2, 9, 9, 10])["result"], {'descending': True, 'k': 1, 'items': 10, 'selected': [{'name': '10', 'score': 10.0, 'rank': 1}], 'cut_score': 10.0, 'cut_tie': False, 'dropped': 9, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['a=1', 'b=3', 'c=3', 'd=2'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'descending': True, 'k': 2, 'items': 4, 'selected': [{'name': 'b', 'score': 3.0, 'rank': 1}, {'name': 'c', 'score': 3.0, 'rank': 2}], 'cut_score': 3.0, 'cut_tie': False, 'dropped': 2, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 29)
        self.assertEqual(meta["algo"], 'au_algo_029')
        self.assertEqual(meta["params"], {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'first'})
        self.assertEqual(meta["semantic"], 'tiny_top_select')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['a=1', 'b=3', 'c=3', 'd=2'], p1=1, p2=10, p3=True, p4='first')["result"], {'descending': True, 'k': 1, 'items': 4, 'selected': [{'name': 'b', 'score': 3.0, 'rank': 1}], 'cut_score': 3.0, 'cut_tie': True, 'dropped': 3, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['a=1', 'b=3', 'c=3', 'd=2'])["result"]
        two = tool.execute(action="run", x=['a=1', 'b=3', 'c=3', 'd=2'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['a=1', 'b=3', 'c=3', 'd=2'])


if __name__ == "__main__":
    unittest.main()
