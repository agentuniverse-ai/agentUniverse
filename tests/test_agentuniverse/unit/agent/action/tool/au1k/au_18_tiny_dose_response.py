"""Known-answer and discipline tests for TinyDoseResponseTool (au1k #18)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_18_tiny_dose_response import TinyDoseResponseTool


class TestTinyDoseResponseTool(unittest.TestCase):
    def _tool(self):
        return TinyDoseResponseTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['1:10', '2:25', '4:60', '8:90'])["result"], {'method': 'linear', 'points': 4, 'curve': [{'dose': 1.0, 'response': 10.0}, {'dose': 2.0, 'response': 18.0}, {'dose': 2.0, 'response': 25.0}, {'dose': 3.0, 'response': 42.0}], 'max_response': 90.0, 'max_dose': 8.0, 'half_max_dose': 4.0, 'monotone': True, 'clamped': 1, 'truncated': True})  # a
        self.assertEqual(tool.execute(action="run", x=['0,0', '1,0.1', '2,0', '3,5', '4,0'])["result"], {'method': 'linear', 'points': 5, 'curve': [{'dose': 0.0, 'response': 0.0}, {'dose': 0.0, 'response': 0.0}, {'dose': 1.0, 'response': 0.0}, {'dose': 2.0, 'response': 0.0}], 'max_response': 5.0, 'max_dose': 3.0, 'half_max_dose': 3.0, 'monotone': False, 'clamped': 1, 'truncated': True})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x=['1:10', '2:25', '4:60', '8:90'])
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'method': 'linear', 'points': 4, 'curve': [{'dose': 1.0, 'response': 10.0}, {'dose': 2.0, 'response': 18.0}, {'dose': 2.0, 'response': 25.0}, {'dose': 3.0, 'response': 42.0}, {'dose': 4.0, 'response': 60.0}], 'max_response': 90.0, 'max_dose': 8.0, 'half_max_dose': 4.0, 'monotone': True, 'clamped': 1, 'truncated': True})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 18)
        self.assertEqual(meta["algo"], 'au_algo_018')
        self.assertEqual(meta["params"], {'p1': 4, 'p2': 0, 'p3': True, 'p4': 'linear'})
        self.assertEqual(meta["semantic"], 'tiny_dose_response')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x=['1:10', '2:25', '4:60', '8:90'], p1=4, p2=0, p3=True, p4='linear')["result"], {'method': 'linear', 'points': 4, 'curve': [{'dose': 1.0, 'response': 10.0}, {'dose': 2.0, 'response': 18.0}, {'dose': 2.0, 'response': 25.0}, {'dose': 3.0, 'response': 42.0}], 'max_response': 90.0, 'max_dose': 8.0, 'half_max_dose': 4.0, 'monotone': True, 'clamped': 1, 'truncated': True})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x=['1:10', '2:25', '4:60', '8:90'])["result"]
        two = tool.execute(action="run", x=['1:10', '2:25', '4:60', '8:90'])["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x=['1:10', '2:25', '4:60', '8:90'])


if __name__ == "__main__":
    unittest.main()
