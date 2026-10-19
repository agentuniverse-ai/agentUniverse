"""Known-answer and discipline tests for TinyRomanNumeralTool (au1k #23)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_23_tiny_roman_numeral import TinyRomanNumeralTool


class TestTinyRomanNumeralTool(unittest.TestCase):
    def _tool(self):
        return TinyRomanNumeralTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='XLII')["result"], {'style': 'canonical', 'strict': True, 'numerals': 1, 'results': [{'input': 'XLII', 'value': 42, 'roman': 'XLII'}], 'total': 42, 'largest': 42, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='XLII')["result"], {'style': 'canonical', 'strict': True, 'numerals': 1, 'results': [{'input': 'XLII', 'value': 42, 'roman': 'XLII'}], 'total': 42, 'largest': 42, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='XLII')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'style': 'canonical', 'strict': True, 'numerals': 1, 'results': [{'input': 'XLII', 'value': 42, 'roman': 'XLII'}], 'total': 42, 'largest': 42, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 23)
        self.assertEqual(meta["algo"], 'au_algo_023')
        self.assertEqual(meta["params"], {'p1': 100, 'p2': 5, 'p3': True, 'p4': 'canonical'})
        self.assertEqual(meta["semantic"], 'tiny_roman_numeral')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='XLII', p1=100, p2=5, p3=True, p4='canonical')["result"], {'style': 'canonical', 'strict': True, 'numerals': 1, 'results': [{'input': 'XLII', 'value': 42, 'roman': 'XLII'}], 'total': 42, 'largest': 42, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='XLII')["result"]
        two = tool.execute(action="run", x='XLII')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x=1000000000)

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='XLII')


if __name__ == "__main__":
    unittest.main()
