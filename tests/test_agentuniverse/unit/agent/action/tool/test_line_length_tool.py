import os
import unittest

from agentuniverse.agent.action.tool.common_tool import line_length_tool as line_length_module
from agentuniverse.agent.action.tool.common_tool.line_length_tool import LineLengthTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(line_length_module.__file__), "line_length_tool.yaml")

# Five lines of lengths 5, 25, 45, 85, 200 joined with \n plus a trailing \n:
# the trailing terminator must not produce a sixth (empty) line.
SAMPLE = "short\n" + "x" * 25 + "\n" + "y" * 45 + "\n" + "z" * 85 + "\n" + "w" * 200 + "\n"


class LineLengthToolTest(unittest.TestCase):
    """Unit tests for LineLengthTool audit/find/stats_only/wrap_preview modes."""

    def setUp(self):
        """Create a default-configured tool instance."""
        self.tool = LineLengthTool()

    def test_audit_ground_truth(self):
        """Verify the audit report against hand-computed stats, histogram, and offenders."""
        result = self.tool.execute(mode="audit", text=SAMPLE, limit=80)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "audit")
        self.assertEqual(result["measure"], "codepoints")
        self.assertEqual(result["limit"], 80)
        self.assertEqual(result["total_lines"], 5)
        # lengths 5, 25, 45, 85, 200: min 5, max 200, sum 360, mean 72.0, median 45
        self.assertEqual(result["stats"], {"min": 5, "mean": 72.0, "median": 45, "max": 200})
        self.assertEqual(
            result["histogram"],
            {
                "0-20": 1,
                "21-40": 1,
                "41-60": 1,
                "61-80": 0,
                "81-100": 1,
                "101-120": 0,
                "121-160": 0,
                "161+": 1,
            },
        )
        self.assertEqual(result["over_limit"], 2)
        self.assertEqual(
            result["over_limit_lines"],
            [
                {"line_no": 4, "length": 85, "preview": "z" * 60 + "..."},
                {"line_no": 5, "length": 200, "preview": "w" * 60 + "..."},
            ],
        )
        self.assertFalse(result["over_limit_truncated"])
        self.assertEqual(result["longest_line"], {"line_no": 5, "length": 200, "preview": "w" * 60 + "..."})

    def test_audit_default_limit_is_80(self):
        """Verify omitting limit uses the documented default of 80."""
        result = self.tool.execute(mode="audit", text="a" * 81)
        self.assertEqual(result["limit"], 80)
        self.assertEqual(result["over_limit"], 1)

    def test_bucket_boundaries(self):
        """Verify every bucket edge lands in the hand-assigned bucket."""
        lengths = [20, 21, 40, 41, 60, 61, 80, 81, 100, 101, 120, 121, 160, 161, 162]
        result = self.tool.execute(mode="stats_only", text="\n".join("a" * n for n in lengths))
        self.assertEqual(
            result["histogram"],
            {
                "0-20": 1,
                "21-40": 2,
                "41-60": 2,
                "61-80": 2,
                "81-100": 2,
                "101-120": 2,
                "121-160": 2,
                "161+": 2,
            },
        )

    def test_even_median_and_repeating_mean(self):
        """Verify median averages the middle pair and mean rounds to 2 decimals."""
        # lengths 10, 20, 30, 40: median (20+30)/2 = 25.0, mean 100/4 = 25.0
        result = self.tool.execute(mode="stats_only", text="a" * 10 + "\n" + "b" * 20 + "\n" + "c" * 30 + "\n" + "d" * 40)
        self.assertEqual(result["stats"], {"min": 10, "mean": 25.0, "median": 25.0, "max": 40})
        # lengths 10, 10, 11: mean 31/3 = 10.333... -> 10.33, median 10
        result = self.tool.execute(mode="stats_only", text="a" * 10 + "\n" + "b" * 10 + "\n" + "c" * 11)
        self.assertEqual(result["stats"], {"min": 10, "mean": 10.33, "median": 10, "max": 11})

    def test_longest_line_tie_returns_first(self):
        """Verify the longest-line report keeps the first occurrence on ties."""
        result = self.tool.execute(mode="stats_only", text="a" * 50 + "\n" + "b" * 50)
        self.assertEqual(result["longest_line"], {"line_no": 1, "length": 50, "preview": "a" * 50})

    def test_crlf_lengths_exclude_terminator(self):
        """Verify CRLF terminators are split off and excluded from the length."""
        result = self.tool.execute(mode="stats_only", text="abc\r\ndef\r\n")
        self.assertEqual(result["total_lines"], 2)
        self.assertEqual(result["stats"], {"min": 3, "mean": 3.0, "median": 3.0, "max": 3})
        # mixed \r\n, \r, and \n terminators all split the same way
        mixed = self.tool.execute(mode="stats_only", text="a\r\nb\rc\nd")
        self.assertEqual(mixed["total_lines"], 4)
        self.assertEqual(mixed["stats"]["max"], 1)

    def test_trailing_newline_convention(self):
        """Verify a trailing terminator does not create a final empty line."""
        self.assertEqual(self.tool.execute(mode="stats_only", text="a\nb\n")["total_lines"], 2)
        self.assertEqual(self.tool.execute(mode="stats_only", text="a\nb")["total_lines"], 2)
        self.assertEqual(self.tool.execute(mode="stats_only", text="\n")["total_lines"], 1)

    def test_empty_lines_counted(self):
        """Verify empty lines count toward total_lines and the 0-20 bucket."""
        result = self.tool.execute(mode="stats_only", text="x" * 30 + "\n\n\n")
        self.assertEqual(result["total_lines"], 3)
        self.assertEqual(result["histogram"]["0-20"], 2)
        self.assertEqual(result["histogram"]["21-40"], 1)

    def test_stats_on_empty_text(self):
        """Verify the empty-text convention: zero lines and all-zero stats."""
        result = self.tool.execute(mode="stats_only", text="")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_lines"], 0)
        self.assertEqual(result["stats"], {"min": 0, "mean": 0, "median": 0, "max": 0})
        self.assertTrue(all(count == 0 for count in result["histogram"].values()))
        self.assertIsNone(result["longest_line"])

    def test_stats_only_has_no_limit_fields(self):
        """Verify stats_only works without a limit and omits over-limit reporting."""
        result = self.tool.execute(mode="stats_only", text=SAMPLE)
        self.assertNotIn("limit", result)
        self.assertNotIn("over_limit", result)
        self.assertNotIn("over_limit_lines", result)
        audit = self.tool.execute(mode="audit", text=SAMPLE, limit=80)
        self.assertEqual(result["stats"], audit["stats"])
        self.assertEqual(result["histogram"], audit["histogram"])

    def test_preview_truncation_boundary(self):
        """Verify previews keep 60 chars and only append ellipsis beyond that."""
        result = self.tool.execute(mode="audit", text="a" * 60 + "\n" + "b" * 61, limit=10)
        self.assertEqual(result["over_limit_lines"][0]["preview"], "a" * 60)
        self.assertEqual(result["over_limit_lines"][1]["preview"], "b" * 60 + "...")

    def test_offending_lines_cap(self):
        """Verify audit reports at most 50 offending lines with a truncation flag."""
        text = "\n".join("a" * 90 for _ in range(51))
        result = self.tool.execute(mode="audit", text=text, limit=80)
        self.assertEqual(result["over_limit"], 51)
        self.assertEqual(len(result["over_limit_lines"]), 50)
        self.assertTrue(result["over_limit_truncated"])
        self.assertEqual(result["over_limit_lines"][-1]["line_no"], 50)

    def test_find_over_limit(self):
        """Verify find direction=over returns positions of lines beyond the limit."""
        result = self.tool.execute(mode="find", text=SAMPLE, limit=80, direction="over")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["direction"], "over")
        self.assertIsNone(result["min_length"])
        self.assertEqual(result["match_count"], 2)
        self.assertEqual(
            result["matches"],
            [
                {"line_no": 4, "length": 85, "preview": "z" * 60 + "..."},
                {"line_no": 5, "length": 200, "preview": "w" * 60 + "..."},
            ],
        )
        self.assertFalse(result["truncated"])

    def test_find_under_with_min_length(self):
        """Verify find direction=under returns lines in [min_length, limit)."""
        # lengths 5, 25, 45, 85, 200 with min_length=20, limit=80 -> lines 2 (25) and 3 (45)
        result = self.tool.execute(mode="find", text=SAMPLE, limit=80, direction="under", min_length=20)
        self.assertEqual(result["min_length"], 20)
        self.assertEqual(result["match_count"], 2)
        self.assertEqual([m["line_no"] for m in result["matches"]], [2, 3])
        self.assertEqual([m["length"] for m in result["matches"]], [25, 45])
        # min_length boundary is inclusive, the limit boundary exclusive
        edge = self.tool.execute(mode="find", text="a" * 20 + "\n" + "b" * 19 + "\n" + "c" * 80, limit=80, direction="under", min_length=20)
        self.assertEqual([m["line_no"] for m in edge["matches"]], [1])

    def test_find_result_cap(self):
        """Verify find caps matches at 100 while reporting the true count."""
        text = "\n".join("a" * 90 for _ in range(120))
        result = self.tool.execute(mode="find", text=text, limit=80)
        self.assertEqual(result["match_count"], 120)
        self.assertEqual(len(result["matches"]), 100)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["matches"][0]["line_no"], 1)
        self.assertEqual(result["matches"][-1]["line_no"], 100)

    def test_wrap_preview_counts_without_wrapping(self):
        """Verify wrap_preview counts reflowable lines and never returns wrapped text."""
        result = self.tool.execute(mode="wrap_preview", text=SAMPLE, limit=80)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["lines_over_limit"], 2)
        self.assertTrue(result["wrap_required"])
        self.assertEqual(result["over_limit_line_nos"], [4, 5])
        self.assertIn("TextWrapTool", result["note"])
        self.assertIn("does not", result["note"])
        self.assertNotIn("wrapped_text", result)
        clean = self.tool.execute(mode="wrap_preview", text="a" * 80 + "\n" + "b" * 79, limit=80)
        self.assertEqual(clean["lines_over_limit"], 0)
        self.assertFalse(clean["wrap_required"])
        self.assertEqual(clean["over_limit_line_nos"], [])

    def test_cjk_display_width_vs_codepoints(self):
        """Verify display_width measures CJK lines in columns, not code points."""
        line = "你好abc"  # 5 code points; 2 wide chars (4 columns) + 3 ascii = 7 columns
        columns = self.tool.execute(mode="stats_only", text=line, display_width=True)
        self.assertEqual(columns["measure"], "display_columns")
        self.assertEqual(columns["stats"], {"min": 7, "mean": 7.0, "median": 7, "max": 7})
        codepoints = self.tool.execute(mode="stats_only", text=line, display_width=False)
        self.assertEqual(codepoints["measure"], "codepoints")
        self.assertEqual(codepoints["stats"]["max"], 5)
        # the same line crosses limit=5 only in display-column mode
        over_columns = self.tool.execute(mode="audit", text=line, limit=5, display_width=True)
        self.assertEqual(over_columns["over_limit"], 1)
        over_codepoints = self.tool.execute(mode="audit", text=line, limit=5, display_width=False)
        self.assertEqual(over_codepoints["over_limit"], 0)
        # fullwidth punctuation counts as 2 columns too
        fullwidth = self.tool.execute(mode="stats_only", text="！！", display_width=True)
        self.assertEqual(fullwidth["stats"]["max"], 4)

    def test_error_matrix(self):
        """Verify invalid inputs return structured validation errors."""
        cases = [
            ({"mode": "rewrite", "text": "a"}, "mode must be audit, find, stats_only, or wrap_preview"),
            ({"mode": "audit", "text": None}, "text must be a string"),
            ({"mode": "audit", "text": 123}, "text must be a string"),
            ({"mode": "audit", "text": "a", "limit": 0}, "limit must be between 1 and 10000"),
            ({"mode": "audit", "text": "a", "limit": 10001}, "limit must be between 1 and 10000"),
            ({"mode": "audit", "text": "a", "limit": "80"}, "limit must be an integer"),
            ({"mode": "audit", "text": "a", "limit": True}, "limit must be an integer"),
            ({"mode": "find", "text": "a", "direction": "sideways"}, "direction must be over or under"),
            ({"mode": "find", "text": "a", "limit": 80, "min_length": 10}, "min_length is only valid when direction is under"),
            ({"mode": "audit", "text": "a", "min_length": 10}, "min_length is only valid in find mode"),
            ({"mode": "find", "text": "a", "direction": "under", "min_length": 80}, "min_length must be between 0 and 79"),
            ({"mode": "find", "text": "a", "direction": "under", "min_length": -1}, "min_length must be between 0 and 79"),
            ({"mode": "find", "text": "a", "direction": "under", "min_length": "10"}, "min_length must be an integer"),
            ({"mode": "audit", "text": "a", "display_width": "yes"}, "display_width must be a boolean"),
        ]
        for kwargs, fragment in cases:
            result = self.tool.execute(**kwargs)
            self.assertEqual(result["status"], "error", msg=str(kwargs))
            self.assertEqual(result["error_type"], "validation_error")
            self.assertIn(fragment, result["error"], msg=str(kwargs))

    def test_line_and_text_caps(self):
        """Verify the 100k-line default cap and configurable text-size cap."""
        capped = LineLengthTool(max_lines=2)
        result = capped.execute(mode="stats_only", text="a\nb\nc")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_lines", result["error"])
        sized = LineLengthTool(max_text_chars=4)
        result = sized.execute(mode="stats_only", text="abcdef")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_text_chars", result["error"])
        # the defaults themselves stay generous
        self.assertEqual(self.tool.max_lines, 100_000)
        self.assertEqual(self.tool.max_text_chars, 10_000_000)


class LineLengthRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped line_length_tool.yaml as a tool component."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the current app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component exposing the LineLengthTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "LineLengthTool")

    def test_manager(self):
        """Verify the LineLengthTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, LineLengthTool)
        self.assertEqual(tool.input_keys, ["mode", "text"])


if __name__ == "__main__":
    unittest.main()
