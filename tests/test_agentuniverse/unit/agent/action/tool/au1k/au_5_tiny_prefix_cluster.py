"""Known-answer and discipline tests for TinyPrefixClusterTool (au1k #5)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_5_tiny_prefix_cluster import TinyPrefixClusterTool


class TestTinyPrefixClusterTool(unittest.TestCase):
    def _tool(self):
        return TinyPrefixClusterTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['alpha', 'alps', 'beta', 'betamax'])["result"], {'prefix': 1, 'items': 4, 'clusters': 2, 'cluster_list': [{'key': 'a', 'size': 2, 'members': ['alpha', 'alps']}, {'key': 'b', 'size': 2, 'members': ['beta', 'betamax']}], 'largest': {'key': 'a', 'size': 2, 'members': ['alpha', 'alps']}, 'singleton_ratio': 0.0, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'prefix': 1, 'items': 10, 'clusters': 7, 'cluster_list': [{'key': 'c', 'size': 2, 'members': ['cat', 'cat']}, {'key': 'f', 'size': 1, 'members': ['fast']}, {'key': 'm', 'size': 1, 'members': ['mat']}, {'key': 'o', 'size': 1, 'members': ['on']}, {'key': 'r', 'size': 1, 'members': ['ran']}, {'key': 's', 'size': 1, 'members': ['sat']}, {'key': 't', 'size': 3, 'members': ['the', 'the', 'the']}], 'largest': {'key': 'c', 'size': 2, 'members': ['cat', 'cat']}, 'singleton_ratio': 0.7143, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['alpha', 'alps', 'beta', 'betamax'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'prefix': 2, 'items': 4, 'clusters': 2, 'cluster_list': [{'key': 'al', 'size': 2, 'members': ['alpha', 'alps']}, {'key': 'be', 'size': 2, 'members': ['beta', 'betamax']}], 'largest': {'key': 'al', 'size': 2, 'members': ['alpha', 'alps']}, 'singleton_ratio': 0.0, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 5)
        self.assertEqual(meta["algo"], 'au_algo_005')
        self.assertEqual(meta["params"], {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'lex'})
        self.assertEqual(meta["semantic"], 'tiny_prefix_cluster')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['alpha', 'alps', 'beta', 'betamax'], p1=1, p2=10, p3=True, p4='lex')["result"], {'prefix': 1, 'items': 4, 'clusters': 2, 'cluster_list': [{'key': 'a', 'size': 2, 'members': ['alpha', 'alps']}, {'key': 'b', 'size': 2, 'members': ['beta', 'betamax']}], 'largest': {'key': 'a', 'size': 2, 'members': ['alpha', 'alps']}, 'singleton_ratio': 0.0, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['alpha', 'alps', 'beta', 'betamax'])["result"]
        two = tool.execute(action="run", x=['alpha', 'alps', 'beta', 'betamax'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['alpha', 'alps', 'beta', 'betamax'])


if __name__ == "__main__":
    unittest.main()
