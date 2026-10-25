"""Known-answer and discipline tests for TinyIsoCalendarTool (au1k #20)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_20_tiny_iso_calendar import TinyIsoCalendarTool


class TestTinyIsoCalendarTool(unittest.TestCase):
    def _tool(self):
        return TinyIsoCalendarTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['2024-03-01', '2024-12-31'])["result"], {'target': 'iso_week', 'dates': 2, 'records': [{'date': '2024-12-31', 'iso_year': 2025, 'iso_week': 1, 'weekday': 1, 'weekday_name': 'Tuesday', 'quarter': 4, 'day_of_year': 366}, {'date': '2024-03-01', 'iso_year': 2024, 'iso_week': 9, 'weekday': 4, 'weekday_name': 'Friday', 'quarter': 1, 'day_of_year': 61}], 'distribution': {'1': 1, '9': 1}, 'dominant': '1', 'first': '2024-12-31', 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x=['2024-03-01', '2024-12-31'])["result"], {'target': 'iso_week', 'dates': 2, 'records': [{'date': '2024-12-31', 'iso_year': 2025, 'iso_week': 1, 'weekday': 1, 'weekday_name': 'Tuesday', 'quarter': 4, 'day_of_year': 366}, {'date': '2024-03-01', 'iso_year': 2024, 'iso_week': 9, 'weekday': 4, 'weekday_name': 'Friday', 'quarter': 1, 'day_of_year': 61}], 'distribution': {'1': 1, '9': 1}, 'dominant': '1', 'first': '2024-12-31', 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['2024-03-01', '2024-12-31'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'target': 'iso_week', 'dates': 2, 'records': [{'date': '2024-12-31', 'iso_year': 2025, 'iso_week': 1, 'weekday': 1, 'weekday_name': 'Tuesday', 'quarter': 4, 'day_of_year': 366}, {'date': '2024-03-01', 'iso_year': 2024, 'iso_week': 9, 'weekday': 4, 'weekday_name': 'Friday', 'quarter': 1, 'day_of_year': 61}], 'distribution': {'1': 1, '9': 1}, 'dominant': '1', 'first': '2024-12-31', 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 20)
        self.assertEqual(meta["algo"], 'au_algo_020')
        self.assertEqual(meta["params"], {'p1': 10, 'p2': 0, 'p3': True, 'p4': 'iso_week'})
        self.assertEqual(meta["semantic"], 'tiny_iso_calendar')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['2024-03-01', '2024-12-31'], p1=10, p2=0, p3=True, p4='iso_week')["result"], {'target': 'iso_week', 'dates': 2, 'records': [{'date': '2024-12-31', 'iso_year': 2025, 'iso_week': 1, 'weekday': 1, 'weekday_name': 'Tuesday', 'quarter': 4, 'day_of_year': 366}, {'date': '2024-03-01', 'iso_year': 2024, 'iso_week': 9, 'weekday': 4, 'weekday_name': 'Friday', 'quarter': 1, 'day_of_year': 61}], 'distribution': {'1': 1, '9': 1}, 'dominant': '1', 'first': '2024-12-31', 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['2024-03-01', '2024-12-31'])["result"]
        two = tool.execute(action="run", x=['2024-03-01', '2024-12-31'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['2024-03-01', '2024-12-31'])


if __name__ == "__main__":
    unittest.main()
