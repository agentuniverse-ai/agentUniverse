"""Known-answer and discipline tests for TinySetContainmentTool (au1k #16)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_16_tiny_set_containment import TinySetContainmentTool


class TestTinySetContainmentTool(unittest.TestCase):
    def _tool(self):
        return TinySetContainmentTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='alpha beta || beta gamma')["result"], {'metric': 'jaccard', 'a_size': 2, 'b_size': 2, 'intersection': 1, 'union': 3, 'score': 0.3333, 'only_a': ['alpha'], 'only_b': ['gamma'], 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=['alpha', 'alps', 'beta', 'betamax'])["result"], {'metric': 'jaccard', 'a_size': 2, 'b_size': 2, 'intersection': 0, 'union': 4, 'score': 0.0, 'only_a': ['alpha', 'alps'], 'only_b': ['beta', 'betamax'], 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='alpha beta || beta gamma')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'metric': 'jaccard', 'a_size': 2, 'b_size': 2, 'intersection': 1, 'union': 3, 'score': 0.3333, 'only_a': ['alpha'], 'only_b': ['gamma'], 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 16)
        self.assertEqual(meta["algo"], 'au_algo_016')
        self.assertEqual(meta["params"], {'p1': 1, 'p2': 5, 'p3': True, 'p4': 'jaccard'})
        self.assertEqual(meta["semantic"], 'tiny_set_containment')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='alpha beta || beta gamma', p1=1, p2=5, p3=True, p4='jaccard')["result"], {'metric': 'jaccard', 'a_size': 2, 'b_size': 2, 'intersection': 1, 'union': 3, 'score': 0.3333, 'only_a': ['alpha'], 'only_b': ['gamma'], 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='alpha beta || beta gamma')["result"]
        two = tool.execute(action="run", x='alpha beta || beta gamma')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='alpha beta || beta gamma')


if __name__ == "__main__":
    unittest.main()
