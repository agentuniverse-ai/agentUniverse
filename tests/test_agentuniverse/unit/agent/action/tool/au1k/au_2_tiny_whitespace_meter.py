"""Known-answer and discipline tests for TinyWhitespaceMeterTool (au1k #2)."""

import unittest

from agentuniverse.agent.action.tool.common_tool.au_2_tiny_whitespace_meter import TinyWhitespaceMeterTool


class TestTinyWhitespaceMeterTool(unittest.TestCase):
    def _tool(self):
        return TinyWhitespaceMeterTool()

    def test_run_matches_frozen_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='a\n  b \n\tc')["result"], {'lines': 3, 'blank_lines': 0, 'trailing_lines': 1, 'tab_lines': 1, 'max_indent': 2, 'max_indent_units': 1, 'irregular_indents': 0, 'policy': 'strict', 'policy_offenders': [{'line': 2, 'kind': 'trailing_space'}], 'clean_ratio': 0.6667, 'truncated': False})  # a
        self.assertEqual(tool.execute(action="run", x='the cat sat on the mat the cat ran fast')["result"], {'lines': 1, 'blank_lines': 0, 'trailing_lines': 0, 'tab_lines': 0, 'max_indent': 0, 'max_indent_units': 0, 'irregular_indents': 0, 'policy': 'strict', 'policy_offenders': [], 'clean_ratio': 1.0, 'truncated': False})  # b

    def test_alt_action_runs_and_matches_canned_answer(self):
        tool = self._tool()
        got = tool.execute(action="alt", x='a\n  b \n\tc')
        self.assertIsInstance(got["result"], dict)
        self.assertEqual(got["action"], "alt")
        self.assertEqual(got["result"], {'lines': 3, 'blank_lines': 0, 'trailing_lines': 1, 'tab_lines': 1, 'max_indent': 2, 'max_indent_units': 1, 'irregular_indents': 0, 'policy': 'strict', 'policy_offenders': [{'line': 2, 'kind': 'trailing_space'}], 'clean_ratio': 0.6667, 'truncated': False})

    def test_meta_provenance(self):
        meta = self._tool().execute(action="meta", x=None)
        self.assertEqual(meta["series"], "au1k")
        self.assertEqual(meta["index"], 2)
        self.assertEqual(meta["algo"], 'au_algo_002')
        self.assertEqual(meta["params"], {'p1': 4, 'p2': 2, 'p3': True, 'p4': 'strict'})
        self.assertEqual(meta["semantic"], 'tiny_whitespace_meter')

    def test_explicit_same_param_override_is_noop(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="run", x='a\n  b \n\tc', p1=4, p2=2, p3=True, p4='strict')["result"], {'lines': 3, 'blank_lines': 0, 'trailing_lines': 1, 'tab_lines': 1, 'max_indent': 2, 'max_indent_units': 1, 'irregular_indents': 0, 'policy': 'strict', 'policy_offenders': [{'line': 2, 'kind': 'trailing_space'}], 'clean_ratio': 0.6667, 'truncated': False})

    def test_repeat_determinism(self):
        tool = self._tool()
        one = tool.execute(action="run", x='a\n  b \n\tc')["result"]
        two = tool.execute(action="run", x='a\n  b \n\tc')["result"]
        self.assertEqual(one, two)

    def test_malformed_2_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="run", x={})

    def test_unknown_action_raises(self):
        tool = self._tool()
        with self.assertRaises(ValueError):
            tool.execute(action="nope", x='a\n  b \n\tc')


if __name__ == "__main__":
    unittest.main()
