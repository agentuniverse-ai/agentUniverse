"""Known-answer and discipline tests for TinyQuoteSpanTool (au1k #3)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_3_tiny_quote_span import TinyQuoteSpanTool


class TestTinyQuoteSpanTool(unittest.TestCase):
    def _tool(self):
        return TinyQuoteSpanTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='he said \'hi there\' and "ok now"')["result"], {'quote': 'single', 'spans': [{'text': 'hi there', 'length': 8, 'start': 9, 'end': 17}], 'span_count': 1, 'unterminated': 0, 'quote_histogram': {"'": 1}, 'min_length': 0, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'quote': 'single', 'spans': [], 'span_count': 0, 'unterminated': 0, 'quote_histogram': {}, 'min_length': 0, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='he said \'hi there\' and "ok now"')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'quote': 'single', 'spans': [{'text': 'hi there', 'length': 8, 'start': 9, 'end': 17}], 'span_count': 1, 'unterminated': 0, 'quote_histogram': {"'": 1}, 'min_length': 1, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 3)
        self.assertEqual(meta["algo"], 'au_algo_003')
        self.assertEqual(meta["params"], {'p1': 0, 'p2': 5, 'p3': True, 'p4': 'single'})
        self.assertEqual(meta["semantic"], 'tiny_quote_span')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='he said \'hi there\' and "ok now"', p1=0, p2=5, p3=True, p4='single')["result"], {'quote': 'single', 'spans': [{'text': 'hi there', 'length': 8, 'start': 9, 'end': 17}], 'span_count': 1, 'unterminated': 0, 'quote_histogram': {"'": 1}, 'min_length': 0, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='he said \'hi there\' and "ok now"')["result"]
        two = tool.execute(action="run", x='he said \'hi there\' and "ok now"')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='he said \'hi there\' and "ok now"')


if __name__ == "__main__":
    unittest.main()
