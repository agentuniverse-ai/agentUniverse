"""Known-answer and discipline tests for TinyDurationSpanTool (au1k #19)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_19_tiny_duration_span import TinyDurationSpanTool


class TestTinyDurationSpanTool(unittest.TestCase):
    def _tool(self):
        return TinyDurationSpanTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['2024-01-01/2024-01-10', '2024-01-05/2024-01-20'])["result"], {'unit': 'days', 'spans': 2, 'records': [{'start': '2024-01-01', 'end': '2024-01-10', 'days': 10, 'weeks': 1, 'months': 0, 'weekday': 'Monday'}, {'start': '2024-01-05', 'end': '2024-01-20', 'days': 16, 'weeks': 2, 'months': 0, 'weekday': 'Friday'}], 'total_days': 26, 'overlaps': 1, 'longest_days': 16, 'total': 26, 'weekday_counts': {'Monday': 1, 'Friday': 1}, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=['2024-01-01/2024-01-10', '2024-01-05/2024-01-20'])["result"], {'unit': 'days', 'spans': 2, 'records': [{'start': '2024-01-01', 'end': '2024-01-10', 'days': 10, 'weeks': 1, 'months': 0, 'weekday': 'Monday'}, {'start': '2024-01-05', 'end': '2024-01-20', 'days': 16, 'weeks': 2, 'months': 0, 'weekday': 'Friday'}], 'total_days': 26, 'overlaps': 1, 'longest_days': 16, 'total': 26, 'weekday_counts': {'Monday': 1, 'Friday': 1}, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['2024-01-01/2024-01-10', '2024-01-05/2024-01-20'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'unit': 'days', 'spans': 2, 'records': [{'start': '2024-01-01', 'end': '2024-01-10', 'days': 10, 'weeks': 1, 'months': 0, 'weekday': 'Monday'}, {'start': '2024-01-05', 'end': '2024-01-20', 'days': 16, 'weeks': 2, 'months': 0, 'weekday': 'Friday'}], 'total_days': 26, 'overlaps': 1, 'longest_days': 16, 'total': 26, 'weekday_counts': {'Monday': 1, 'Friday': 1}, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 19)
        self.assertEqual(meta["algo"], 'au_algo_019')
        self.assertEqual(meta["params"], {'p1': 5, 'p2': 0, 'p3': True, 'p4': 'days'})
        self.assertEqual(meta["semantic"], 'tiny_duration_span')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['2024-01-01/2024-01-10', '2024-01-05/2024-01-20'], p1=5, p2=0, p3=True, p4='days')["result"], {'unit': 'days', 'spans': 2, 'records': [{'start': '2024-01-01', 'end': '2024-01-10', 'days': 10, 'weeks': 1, 'months': 0, 'weekday': 'Monday'}, {'start': '2024-01-05', 'end': '2024-01-20', 'days': 16, 'weeks': 2, 'months': 0, 'weekday': 'Friday'}], 'total_days': 26, 'overlaps': 1, 'longest_days': 16, 'total': 26, 'weekday_counts': {'Monday': 1, 'Friday': 1}, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['2024-01-01/2024-01-10', '2024-01-05/2024-01-20'])["result"]
        two = tool.execute(action="run", x=['2024-01-01/2024-01-10', '2024-01-05/2024-01-20'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['2024-01-01/2024-01-10', '2024-01-05/2024-01-20'])


if __name__ == "__main__":
    unittest.main()
