"""Known-answer and discipline tests for TinyDegreeMapTool (au1k #27)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_27_tiny_degree_map import TinyDegreeMapTool


class TestTinyDegreeMapTool(unittest.TestCase):
    def _tool(self):
        return TinyDegreeMapTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['a->b', 'b->c', 'c->a', 'd->a'])["result"], {'metric': 'out', 'edges': 4, 'nodes': 4, 'self_loops': 0, 'degree_map': [{'node': 'a', 'degree': 3}], 'hub': 'a', 'sources': [], 'sinks': [], 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=['a->b', 'b->c', 'c->a', 'd->a'])["result"], {'metric': 'out', 'edges': 4, 'nodes': 4, 'self_loops': 0, 'degree_map': [{'node': 'a', 'degree': 3}], 'hub': 'a', 'sources': [], 'sinks': [], 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['a->b', 'b->c', 'c->a', 'd->a'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'metric': 'out', 'edges': 4, 'nodes': 4, 'self_loops': 0, 'degree_map': [{'node': 'a', 'degree': 3}, {'node': 'b', 'degree': 2}], 'hub': 'a', 'sources': [], 'sinks': [], 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 27)
        self.assertEqual(meta["algo"], 'au_algo_027')
        self.assertEqual(meta["params"], {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'out'})
        self.assertEqual(meta["semantic"], 'tiny_degree_map')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['a->b', 'b->c', 'c->a', 'd->a'], p1=1, p2=10, p3=True, p4='out')["result"], {'metric': 'out', 'edges': 4, 'nodes': 4, 'self_loops': 0, 'degree_map': [{'node': 'a', 'degree': 3}], 'hub': 'a', 'sources': [], 'sinks': [], 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['a->b', 'b->c', 'c->a', 'd->a'])["result"]
        two = tool.execute(action="run", x=['a->b', 'b->c', 'c->a', 'd->a'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['a->b', 'b->c', 'c->a', 'd->a'])


if __name__ == "__main__":
    unittest.main()
