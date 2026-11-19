"""Known-answer and discipline tests for TinyRunBagTool (au1k #15)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_15_tiny_run_bag import TinyRunBagTool


class TestTinyRunBagTool(unittest.TestCase):
    def _tool(self):
        return TinyRunBagTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['a', 'a', 'b', 'c', 'c', 'c'])["result"], {'mode': 'encode', 'merged': True, 'tokens': 6, 'segments': 3, 'runs': [{'token': 'a', 'count': 2}, {'token': 'b', 'count': 1}, {'token': 'c', 'count': 3}], 'longest_run': 3, 'distinct': 3, 'repeat_ratio': 0.8333, 'run_histogram': {}, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'mode': 'encode', 'merged': True, 'tokens': 10, 'segments': 10, 'runs': [{'token': 'the', 'count': 1}, {'token': 'cat', 'count': 1}, {'token': 'sat', 'count': 1}, {'token': 'on', 'count': 1}, {'token': 'the', 'count': 1}, {'token': 'mat', 'count': 1}, {'token': 'the', 'count': 1}, {'token': 'cat', 'count': 1}, {'token': 'ran', 'count': 1}, {'token': 'fast', 'count': 1}], 'longest_run': 1, 'distinct': 7, 'repeat_ratio': 0.0, 'run_histogram': {}, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['a', 'a', 'b', 'c', 'c', 'c'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'mode': 'encode', 'merged': True, 'tokens': 6, 'segments': 3, 'runs': [{'token': 'a', 'count': 2}, {'token': 'c', 'count': 3}], 'longest_run': 3, 'distinct': 3, 'repeat_ratio': 0.8333, 'run_histogram': {}, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 15)
        self.assertEqual(meta["algo"], 'au_algo_015')
        self.assertEqual(meta["params"], {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'encode'})
        self.assertEqual(meta["semantic"], 'tiny_run_bag')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['a', 'a', 'b', 'c', 'c', 'c'], p1=1, p2=10, p3=True, p4='encode')["result"], {'mode': 'encode', 'merged': True, 'tokens': 6, 'segments': 3, 'runs': [{'token': 'a', 'count': 2}, {'token': 'b', 'count': 1}, {'token': 'c', 'count': 3}], 'longest_run': 3, 'distinct': 3, 'repeat_ratio': 0.8333, 'run_histogram': {}, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['a', 'a', 'b', 'c', 'c', 'c'])["result"]
        two = tool.execute(action="run", x=['a', 'a', 'b', 'c', 'c', 'c'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['a', 'a', 'b', 'c', 'c', 'c'])


if __name__ == "__main__":
    unittest.main()
