"""Known-answer and discipline tests for TinyRhymeClusterTool (au1k #6)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_6_tiny_rhyme_cluster import TinyRhymeClusterTool


class TestTinyRhymeClusterTool(unittest.TestCase):
    def _tool(self):
        return TinyRhymeClusterTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['cat', 'hat', 'bat', 'dog'])["result"], {'mode': 'plain', 'suffix': 1, 'items': 4, 'clusters': 2, 'rhyme_density': 0.5, 'perfect_groups': [{'key': 't', 'size': 3, 'members': ['cat', 'hat', 'bat']}, {'key': 'g', 'size': 1, 'members': ['dog']}], 'near_pairs': [], 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'mode': 'plain', 'suffix': 1, 'items': 10, 'clusters': 3, 'rhyme_density': 1.0, 'perfect_groups': [{'key': 't', 'size': 5, 'members': ['cat', 'sat', 'mat', 'cat', 'fast']}, {'key': 'e', 'size': 3, 'members': ['the', 'the', 'the']}, {'key': 'n', 'size': 2, 'members': ['on', 'ran']}], 'near_pairs': [], 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['cat', 'hat', 'bat', 'dog'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'mode': 'plain', 'suffix': 2, 'items': 4, 'clusters': 2, 'rhyme_density': 0.5, 'perfect_groups': [{'key': 'at', 'size': 3, 'members': ['cat', 'hat', 'bat']}, {'key': 'og', 'size': 1, 'members': ['dog']}], 'near_pairs': [], 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 6)
        self.assertEqual(meta["algo"], 'au_algo_006')
        self.assertEqual(meta["params"], {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'plain'})
        self.assertEqual(meta["semantic"], 'tiny_rhyme_cluster')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['cat', 'hat', 'bat', 'dog'], p1=1, p2=10, p3=True, p4='plain')["result"], {'mode': 'plain', 'suffix': 1, 'items': 4, 'clusters': 2, 'rhyme_density': 0.5, 'perfect_groups': [{'key': 't', 'size': 3, 'members': ['cat', 'hat', 'bat']}, {'key': 'g', 'size': 1, 'members': ['dog']}], 'near_pairs': [], 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['cat', 'hat', 'bat', 'dog'])["result"]
        two = tool.execute(action="run", x=['cat', 'hat', 'bat', 'dog'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['cat', 'hat', 'bat', 'dog'])


if __name__ == "__main__":
    unittest.main()
