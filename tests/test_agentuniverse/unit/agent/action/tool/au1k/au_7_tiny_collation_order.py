"""Known-answer and discipline tests for TinyCollationOrderTool (au1k #7)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_7_tiny_collation_order import TinyCollationOrderTool


class TestTinyCollationOrderTool(unittest.TestCase):
    def _tool(self):
        return TinyCollationOrderTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['item10', 'Item2', 'item1'])["result"], {'policy': 'casefold', 'items': 3, 'order': ['item10', 'Item2', 'item1'], 'first': 'item10', 'last': 'item1', 'inversions': 0, 'adjacent_ordered': 2, 'duplicate_groups': [{'key': 'item10', 'count': 3}], 'sorted_ratio': 1.0, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'policy': 'casefold', 'items': 10, 'order': ['cat', 'cat', 'fast', 'mat', 'on', 'ran', 'sat', 'the', 'the', 'the'], 'first': 'cat', 'last': 'the', 'inversions': 25, 'adjacent_ordered': 9, 'duplicate_groups': [{'key': 'cat', 'count': 2}, {'key': 'the', 'count': 3}], 'sorted_ratio': 0.4444, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['item10', 'Item2', 'item1'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'policy': 'casefold', 'items': 3, 'order': ['item10', 'item1', 'Item2'], 'first': 'item10', 'last': 'Item2', 'inversions': 1, 'adjacent_ordered': 2, 'duplicate_groups': [{'key': 'item10', 'count': 2}], 'sorted_ratio': 0.6667, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 7)
        self.assertEqual(meta["algo"], 'au_algo_007')
        self.assertEqual(meta["params"], {'p1': 4, 'p2': 20, 'p3': True, 'p4': 'casefold'})
        self.assertEqual(meta["semantic"], 'tiny_collation_order')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['item10', 'Item2', 'item1'], p1=4, p2=20, p3=True, p4='casefold')["result"], {'policy': 'casefold', 'items': 3, 'order': ['item10', 'Item2', 'item1'], 'first': 'item10', 'last': 'item1', 'inversions': 0, 'adjacent_ordered': 2, 'duplicate_groups': [{'key': 'item10', 'count': 3}], 'sorted_ratio': 1.0, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['item10', 'Item2', 'item1'])["result"]
        two = tool.execute(action="run", x=['item10', 'Item2', 'item1'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['item10', 'Item2', 'item1'])


if __name__ == "__main__":
    unittest.main()
