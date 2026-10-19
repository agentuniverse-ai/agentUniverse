"""Known-answer and discipline tests for TinyWaypointPathTool (au1k #14)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_14_tiny_waypoint_path import TinyWaypointPathTool


class TestTinyWaypointPathTool(unittest.TestCase):
    def _tool(self):
        return TinyWaypointPathTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['0,0', '1,0.1', '2,0', '3,5', '4,0'])["result"], {'metric': 'euclid', 'input_points': 5, 'kept_points': 5, 'dropped': 0, 'compression': 1.0, 'path_before': 12.208, 'path_after': 12.208, 'kept': [[0.0, 0.0], [1.0, 0.1], [2.0, 0.0], [3.0, 5.0], [4.0, 0.0]], 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=['0,0', '1,0.1', '2,0', '3,5', '4,0'])["result"], {'metric': 'euclid', 'input_points': 5, 'kept_points': 5, 'dropped': 0, 'compression': 1.0, 'path_before': 12.208, 'path_after': 12.208, 'kept': [[0.0, 0.0], [1.0, 0.1], [2.0, 0.0], [3.0, 5.0], [4.0, 0.0]], 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['0,0', '1,0.1', '2,0', '3,5', '4,0'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'metric': 'euclid', 'input_points': 5, 'kept_points': 4, 'dropped': 1, 'compression': 0.8, 'path_before': 12.208, 'path_after': 12.198, 'kept': [[0.0, 0.0], [2.0, 0.0], [3.0, 5.0], [4.0, 0.0]], 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 14)
        self.assertEqual(meta["algo"], 'au_algo_014')
        self.assertEqual(meta["params"], {'p1': 0, 'p2': 5, 'p3': True, 'p4': 'euclid'})
        self.assertEqual(meta["semantic"], 'tiny_waypoint_path')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['0,0', '1,0.1', '2,0', '3,5', '4,0'], p1=0, p2=5, p3=True, p4='euclid')["result"], {'metric': 'euclid', 'input_points': 5, 'kept_points': 5, 'dropped': 0, 'compression': 1.0, 'path_before': 12.208, 'path_after': 12.208, 'kept': [[0.0, 0.0], [1.0, 0.1], [2.0, 0.0], [3.0, 5.0], [4.0, 0.0]], 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['0,0', '1,0.1', '2,0', '3,5', '4,0'])["result"]
        two = tool.execute(action="run", x=['0,0', '1,0.1', '2,0', '3,5', '4,0'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['0,0', '1,0.1', '2,0', '3,5', '4,0'])


if __name__ == "__main__":
    unittest.main()
