"""Known-answer and discipline tests for TinyChessMoveTool (au1k #26)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_26_tiny_chess_move import TinyChessMoveTool


class TestTinyChessMoveTool(unittest.TestCase):
    def _tool(self):
        return TinyChessMoveTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='N../.../..N')["result"], {'piece': 'N', 'board_size': 3, 'occupied': 2, 'total_moves': 4, 'pieces': [{'square': 'a3', 'moves': 2, 'colour': 'white'}, {'square': 'c1', 'moves': 2, 'colour': 'white'}], 'moves': ['a3->b1', 'a3->c2', 'c1->b3', 'c1->a2'], 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='.N./.../N..')["result"], {'piece': 'N', 'board_size': 3, 'occupied': 2, 'total_moves': 4, 'pieces': [{'square': 'b3', 'moves': 2, 'colour': 'white'}, {'square': 'a1', 'moves': 2, 'colour': 'white'}], 'moves': ['b3->c1', 'b3->a1', 'a1->b3', 'a1->c2'], 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='N../.../..N')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'piece': 'N', 'board_size': 3, 'occupied': 2, 'total_moves': 4, 'pieces': [{'square': 'a3', 'moves': 2, 'colour': 'white'}, {'square': 'c1', 'moves': 2, 'colour': 'white'}], 'moves': ['a3->b1', 'a3->c2', 'c1->b3', 'c1->a2'], 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 26)
        self.assertEqual(meta["algo"], 'au_algo_026')
        self.assertEqual(meta["params"], {'p1': 3, 'p2': 5, 'p3': True, 'p4': 'N'})
        self.assertEqual(meta["semantic"], 'tiny_chess_move')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='N../.../..N', p1=3, p2=5, p3=True, p4='N')["result"], {'piece': 'N', 'board_size': 3, 'occupied': 2, 'total_moves': 4, 'pieces': [{'square': 'a3', 'moves': 2, 'colour': 'white'}, {'square': 'c1', 'moves': 2, 'colour': 'white'}], 'moves': ['a3->b1', 'a3->c2', 'c1->b3', 'c1->a2'], 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='N../.../..N')["result"]
        two = tool.execute(action="run", x='N../.../..N')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='N../.../..N')


if __name__ == "__main__":
    unittest.main()
