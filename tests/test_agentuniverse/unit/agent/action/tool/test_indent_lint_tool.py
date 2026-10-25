"""Oracle tests for IndentLintTool: compile battery, tokenize battery,
conversion round-trips, real-file battery, and component registration.

The oracles are:

(a) compile-oracle: 600 seeded sources (real repo files, generated sources,
    and seeded indent mutations of both). Every IndentationError/TabError the
    real interpreter raises must be mirrored by an error finding on the same
    line; every verdict without error findings must correspond to a source
    that compiles; non-indentation SyntaxErrors must surface as
    W_OTHER_SYNTAX so a clean verdict always implies compilation.
(b) tokenize-oracle: for 300 valid sources, the tool's per-line indent
    classification counts equal an independent recount that combines raw
    lines with independently computed multi-line-string spans, and every
    INDENT token's row agrees with the raw leading whitespace of its line.
(c) conversion round-trip: for the same 300 sources, convert to spaces (and
    to tabs where applicable) never changes semantics -- when the tool
    accepts a conversion the ast.dump of original and converted are equal;
    when it refuses, the original text is returned. Pure-tab sources survive
    tab -> space -> tab unchanged.
(d) real-file battery: 20 actual repository files lint with no error
    findings and produce sane statistics.
"""

import ast
import glob
import io
import os
import random
import tokenize
import unittest

from agentuniverse.agent.action.tool.common_tool import indent_lint_tool as indent_module
from agentuniverse.agent.action.tool.common_tool.indent_lint_tool import IndentLintTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(indent_module.__file__), "indent_lint_tool.yaml")

def _find_repo_root(start):
    """Walk up until a directory containing both ``agentuniverse`` and ``tests``.

    Counting ``os.pardir`` levels is brittle: it depends on where the package
    happens to live (editable checkout vs site-packages), and an incorrect count
    silently yields a root with no ``agentuniverse/`` or ``tests/`` below it, so
    the corpus helpers collect nothing and the assertions fail for the wrong
    reason.
    """
    current = os.path.abspath(start)
    for _ in range(12):
        if os.path.isdir(os.path.join(current, "agentuniverse")) and os.path.isdir(
            os.path.join(current, "tests")
        ):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    raise RuntimeError(f"repository root not found above {start!r}")


ROOT = _find_repo_root(os.path.dirname(os.path.abspath(indent_module.__file__)))

_STRING_TYPES = (tokenize.STRING,) + tuple(
    getattr(tokenize, name)
    for name in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END")
    if hasattr(tokenize, name)
)


def error_codes(result):
    """Error-severity finding codes of a lint/convert result."""
    return [f["code"] for f in result.get("findings", []) if f["severity"] == "error"]


def compile_or_none(source):
    """Return the SyntaxError raised by compile(), or None on success."""
    try:
        compile(source, "<oracle>", "exec")
        return None
    except SyntaxError as exc:  # IndentationError and TabError included
        return exc


# ---------------------------------------------------------------------------
# Corpus: real repository files, generated sources, seeded mutations.
# ---------------------------------------------------------------------------


def repo_python_files(limit):
    """Deterministic list of compiling repository .py files."""
    seen = set()
    chosen = []
    for pattern in ("agentuniverse/**/*.py", "tests/**/*.py"):
        for path in sorted(glob.glob(os.path.join(ROOT, pattern), recursive=True)):
            if path in seen:
                continue
            seen.add(path)
            try:
                with open(path, encoding="utf-8") as handle:
                    text = handle.read()
                if not text.strip():
                    continue
                compile(text, path, "exec")
            except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
                continue
            chosen.append(text)
            if len(chosen) >= limit:
                return chosen
    return chosen


_NAME_POOL = ("alpha", "beta", "gamma", "delta", "omega", "value", "item", "total", "count", "result")


class _Generator:
    """Deterministic random Python source generator (always valid code)."""

    def __init__(self, rng):
        self.rng = rng
        self.counter = 0

    def _name(self):
        self.counter += 1
        return _NAME_POOL[self.counter % len(_NAME_POOL)] + str(self.counter)

    def simple_statement(self):
        name = self._name()
        pick = self.rng.randrange(4)
        if pick == 0:
            return f"{name} = {self.rng.randrange(100)}"
        if pick == 1:
            return f"{name} = {self._name()} + {self.rng.randrange(10)}"
        if pick == 2:
            return f"print({name!r})"
        return f"{name} = [{self.rng.randrange(9)}, {self.rng.randrange(9)}]"

    def multiline_string(self, indent):
        opener = self._name()
        return [
            f"{indent}{opener} = \"\"\"",
            f"\t{self._name()} text line",
            f"    {self._name()} more",
            f"{indent}\"\"\"",
        ]

    def continuation(self, indent):
        name = self._name()
        style = self.rng.randrange(2)
        if style == 0:
            return [
                f"{indent}{name} = [",
                f"{indent}\t{self.rng.randrange(50)},",
                f"{indent}    {self.rng.randrange(50)},",
                f"{indent}]",
            ]
        return [
            f"{indent}{name} = 1 + \\",
            f"{indent}\t2 + \\",
            f"{indent}    3",
        ]

    def block(self, depth, budget, indent_unit):
        """Emit statements at the given depth; return list of lines."""
        lines = []
        while budget > 0 and len(lines) < 40:
            budget -= 1
            pick = self.rng.randrange(10)
            prefix = indent_unit * depth
            if pick <= 3:
                lines.append(prefix + self.simple_statement())
            elif pick == 4:
                lines.append("")  # blank separator
            elif pick == 5:
                lines.append(f"{prefix}# comment {self._name()}")
            elif pick == 6 and depth >= 1:
                lines.extend(self.continuation(prefix))
            elif pick == 7 and depth >= 1:
                lines.extend(self.multiline_string(prefix))
            elif pick == 8 and depth < 4 and budget >= 2:
                head = self._name()
                kind = self.rng.randrange(3)
                if kind == 0:
                    lines.append(f"{prefix}if {head} > 0:")
                elif kind == 1:
                    lines.append(f"{prefix}for {head} in range(3):")
                else:
                    lines.append(f"{prefix}def {head}():")
                lines.append(f"{prefix}    pass")
                lines.extend(self.block(depth + 1, budget - 1, indent_unit))
                budget -= 1
            else:
                if depth > 0:
                    lines.append(prefix + "pass" if self.rng.randrange(2) else prefix + self.simple_statement())
        return lines

    def source(self):
        step = self.rng.choice([2, 4, 8])
        style = self.rng.choice(["spaces", "tabs"])
        if style == "spaces":
            unit = " " * step
        else:
            unit = "\t"
        head = self._name()
        lines = [f"def {head}():"]
        lines.extend(self.block(1, 14, unit))
        lines.append("")
        lines.append(f"{head}()")
        return "\n".join(lines) + "\n"


def generated_sources(count, seed=2520):
    rng = random.Random(seed)
    maker = _Generator(rng)
    sources = []
    guard = 0
    while len(sources) < count and guard < count * 10:
        guard += 1
        text = maker.source()
        if compile_or_none(text) is None:
            sources.append(text)
    return sources


def mutate(source, rng):
    """Apply one seeded indentation mutation; None when impossible."""
    lines = source.split("\n")
    indented = [i for i, line in enumerate(lines) if line[:1] in (" ", "\t")]
    if not indented:
        return None
    index = rng.choice(indented)
    line = lines[index]
    lead = line[: len(line) - len(line.lstrip(" \t\f\v"))]
    body = line[len(lead) :]
    kind = rng.randrange(7)
    if kind == 0 and " " in lead:  # swap one indent space for a tab
        new_lead = lead.replace(" ", "\t", 1)
    elif kind == 1 and len(lead) >= 2:  # dedent to a wrong intermediate level
        new_lead = " " * max(1, len(lead) - rng.randrange(1, 4))
    elif kind == 2:  # same visual width rewritten in tabs
        new_lead = "\t" * max(1, len(lead) // 4)
    elif kind == 3:  # extra unexpected indent
        new_lead = lead + " " * rng.randrange(1, 3)
    elif kind == 4:  # strip the entire indent
        new_lead = ""
    elif kind == 5:  # form feed after the indent inside a block
        new_lead = lead + "\f"
    else:  # copy-paste twin line indented with a single tab
        twin = "\t" + body
        lines.insert(index + 1, twin)
        return "\n".join(lines)
    lines[index] = new_lead + body
    return "\n".join(lines)


def mutated_sources(pool, count, seed=2521):
    rng = random.Random(seed)
    outputs = []
    guard = 0
    while len(outputs) < count and guard < count * 20:
        guard += 1
        text = mutate(rng.choice(pool), rng)
        if text is not None:
            outputs.append(text)
    return outputs


def pure_tab_sources(count):
    """Deterministic clean tab-indented sources (no space indents at all)."""
    outputs = []
    for index in range(count):
        depth = 1 + (index % 4)
        lines = ["def tab_function():"]
        for level in range(1, depth):
            lines.append("\t" * level + f"value_{level} = {level}")
            lines.append("\t" * level + f"if value_{level}:")
        lines.append("\t" * depth + f"final = {depth}")
        lines.append("\t" * depth + "if final:")
        lines.append("\t" * (depth + 1) + "pass")
        lines.append("\treturn 0")
        outputs.append("\n".join(lines) + "\n")
    return outputs


# ---------------------------------------------------------------------------
# (a) compile oracle
# ---------------------------------------------------------------------------


class CompileOracleTest(unittest.TestCase):
    """600 seeded sources against the real interpreter verdict."""

    @classmethod
    def setUpClass(cls):
        cls.tool = IndentLintTool()
        cls.repo = repo_python_files(60)
        cls.generated = generated_sources(240)
        cls.valid = cls.repo + cls.generated
        cls.mutated = mutated_sources(cls.valid, 300)

    def _assert_oracle(self, source):
        exc = compile_or_none(source)
        result = self.tool.execute(mode="lint", source=source)
        self.assertEqual(result["status"], "success")
        errors = [f for f in result["findings"] if f["severity"] == "error"]
        if exc is None:
            self.assertEqual(
                errors,
                [],
                f"clean compile but errors reported for:\n{source[:400]}",
            )
            return
        if isinstance(exc, (IndentationError, TabError)):
            matching = [f for f in errors if f["line"] == exc.lineno]
            self.assertTrue(
                matching,
                f"interpreter rejected line {exc.lineno} ({exc.msg}) but no matching "
                f"error finding in {[ (f['code'], f['line']) for f in result['findings'] ]}:\n{source[:400]}",
            )
            self.assertEqual(matching[0]["message"], exc.msg)
            self.assertEqual(matching[0].get("col"), exc.offset)
        else:
            self.assertIn(
                "W_OTHER_SYNTAX",
                [f["code"] for f in result["findings"]],
                "non-indentation SyntaxError must surface as W_OTHER_SYNTAX",
            )

    def test_valid_corpus_matches_compiler(self):
        """240 generated + 60 repository files agree with compile()."""
        self.assertEqual(len(self.valid), 300)
        for source in self.valid:
            self._assert_oracle(source)

    def test_mutated_corpus_matches_compiler(self):
        """300 seeded indent mutations agree with compile()."""
        self.assertEqual(len(self.mutated), 300)
        for source in self.mutated:
            self._assert_oracle(source)

    def test_mutations_actually_broke_something(self):
        """The mutation battery is meaningful: many mutants fail compile."""
        broken = sum(1 for src in self.mutated if compile_or_none(src) is not None)
        self.assertGreater(broken, 100)


# ---------------------------------------------------------------------------
# (b) tokenize oracle
# ---------------------------------------------------------------------------


def independent_string_rows(source):
    rows = set()
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type in _STRING_TYPES and token.end[0] > token.start[0]:
            rows.update(range(token.start[0] + 1, token.end[0] + 1))
    return rows


def independent_counts(source):
    """Classify each raw line exactly as documented (string rows excluded)."""
    skip = independent_string_rows(source)
    lines = source.split("\n")
    if source.endswith("\n"):
        lines = lines[:-1]
    counts = {"tabs": 0, "spaces": 0, "mixed": 0, "blank": 0, "none": 0, "total": 0}
    for number, line in enumerate(lines, start=1):
        if number in skip:
            continue
        counts["total"] += 1
        lead = line[: len(line) - len(line.lstrip(" \t\f\v"))]
        if line.strip(" \t\f\v") == "":
            counts["blank"] += 1
        elif lead == "":
            counts["none"] += 1
        elif "\t" in lead and " " in lead:
            counts["mixed"] += 1
        elif "\t" in lead:
            counts["tabs"] += 1
        else:
            counts["spaces"] += 1
    return counts


class TokenizeOracleTest(unittest.TestCase):
    """300 valid sources: line classification vs tokenizer + raw analysis."""

    @classmethod
    def setUpClass(cls):
        cls.tool = IndentLintTool()
        cls.sources = repo_python_files(60) + generated_sources(240)

    def test_counts_match_independent_recount(self):
        for source in self.sources:
            expected = independent_counts(source)
            result = self.tool.execute(mode="stats", source=source)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["tab_lines"], expected["tabs"])
            self.assertEqual(result["space_lines"], expected["spaces"])
            self.assertEqual(result["mixed_lines"], expected["mixed"])
            self.assertEqual(
                result["blank_lines"],
                expected["blank"],
                f"blank mismatch for:\n{source[:300]}",
            )

    def test_indent_tokens_agree_with_raw_lines(self):
        """Every INDENT token's row and indent string match the raw line."""
        for source in self.sources:
            lines = source.split("\n")
            tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
            result = self.tool.execute(mode="stats", source=source)
            self.assertEqual(result["status"], "success")
            indents = [t for t in tokens if t.type == tokenize.INDENT]
            for token in indents:
                row = token.start[0]
                line = lines[row - 1]
                lead = line[: len(line) - len(line.lstrip(" \t\f\v"))]
                self.assertTrue(line.strip(), f"INDENT on blank line {row}")
                self.assertEqual(
                    ("\t" in lead, " " in lead),
                    ("\t" in token.string, " " in token.string),
                    f"INDENT string {token.string!r} vs lead {lead!r} at line {row}",
                )
            if result["depth_histogram"]:
                self.assertEqual(
                    max(int(key) for key in result["depth_histogram"]),
                    result["max_depth"],
                )
            # Every histogram starts at depth 0 (files with logical lines).
            depths = sorted(int(key) for key in result["depth_histogram"])
            if depths:
                self.assertEqual(depths[0], 0)

    def test_depth_histogram_totals_logical_lines(self):
        for source in self.sources:
            result = self.tool.execute(mode="stats", source=source)
            tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
            logical = sum(1 for t in tokens if t.type == tokenize.NEWLINE)
            self.assertEqual(sum(result["depth_histogram"].values()), logical)


# ---------------------------------------------------------------------------
# (c) conversion round-trip oracle
# ---------------------------------------------------------------------------


class ConversionOracleTest(unittest.TestCase):
    """300 valid sources: semantics-preserving conversion, both directions."""

    @classmethod
    def setUpClass(cls):
        cls.tool = IndentLintTool()
        cls.sources = repo_python_files(60) + generated_sources(240)

    def test_spaces_conversion_preserves_ast(self):
        for source in self.sources:
            result = self.tool.execute(mode="convert", source=source, target="spaces", tab_width=4)
            self.assertEqual(result["status"], "success")
            if result["refused"]:
                self.assertEqual(result["converted"], source)
                self.assertEqual(result["changed_lines"], 0)
                continue
            before = ast.dump(ast.parse(source))
            after = ast.dump(ast.parse(result["converted"]))
            self.assertEqual(before, after)

    def test_tabs_conversion_preserves_ast_or_refuses(self):
        for source in self.sources:
            result = self.tool.execute(mode="convert", source=source, target="tabs", tab_width=4)
            self.assertEqual(result["status"], "success")
            if result["refused"]:
                self.assertEqual(result["converted"], source)
                continue
            self.assertEqual(
                ast.dump(ast.parse(source)),
                ast.dump(ast.parse(result["converted"])),
            )

    def test_tab_space_tab_round_trip_is_stable(self):
        """Pure-tab inputs come back byte-identical after a full round trip."""
        stable = 0
        candidates = self.sources + pure_tab_sources(25)
        for source in candidates:
            leading = {line[: len(line) - len(line.lstrip(" \t"))] for line in source.split("\n")}
            if not leading or not any(lead for lead in leading):
                continue
            if any(" " in lead for lead in leading if lead):
                continue  # not a pure-tab file
            to_spaces = self.tool.execute(mode="convert", source=source, target="spaces", tab_width=4)
            self.assertFalse(to_spaces["refused"])
            back = self.tool.execute(
                mode="convert", source=to_spaces["converted"], target="tabs", tab_width=4
            )
            self.assertFalse(back["refused"])
            self.assertEqual(back["converted"], source)
            stable += 1
        self.assertGreaterEqual(stable, 25)


# ---------------------------------------------------------------------------
# (d) real-file battery
# ---------------------------------------------------------------------------


class RealFileBatteryTest(unittest.TestCase):
    """20 actual repository files lint clean and report sane statistics."""

    @classmethod
    def setUpClass(cls):
        cls.tool = IndentLintTool()
        cls.files = repo_python_files(20)

    def test_lint_clean_and_stats_sane(self):
        self.assertGreaterEqual(len(self.files), 20)
        checked = 0
        for source in self.files:
            linted = self.tool.execute(mode="lint", source=source)
            self.assertEqual(linted["status"], "success")
            self.assertEqual(
                error_codes(linted),
                [],
                f"repository file reported errors: {linted['findings'][:3]}",
            )
            self.assertEqual(linted["compile"], "ok")
            stats = self.tool.execute(mode="stats", source=source)
            self.assertEqual(stats["status"], "success")
            self.assertEqual(stats["total_lines"], len(source.split("\n")) - (1 if source.endswith("\n") else 0))
            self.assertIn(stats["inferred_style"], ("spaces", "tabs", "mixed", None))
            if stats["inferred_style"] == "spaces":
                self.assertIn(stats["inferred_step"], (2, 4, 8))
            self.assertGreaterEqual(stats["max_depth"], 0)
            if stats["depth_histogram"]:
                self.assertEqual(
                    max(int(key) for key in stats["depth_histogram"]),
                    stats["max_depth"],
                )
            for entry in stats["per_function"]:
                self.assertGreaterEqual(entry["max_nesting"], 0)
                self.assertGreaterEqual(entry["line"], 1)
            checked += 1
        self.assertEqual(checked, 20)


# ---------------------------------------------------------------------------
# Focused behavior tests
# ---------------------------------------------------------------------------


class LintBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.tool = IndentLintTool()

    def codes(self, source, **kwargs):
        result = self.tool.execute(mode="lint", source=source, **kwargs)
        self.assertEqual(result["status"], "success")
        return [(f["code"], f["line"]) for f in result["findings"]]

    def test_expected_indent_mirrors_interpreter(self):
        finding = self.tool.execute(mode="lint", source="def f():\nx = 1\n")["findings"][0]
        self.assertEqual(finding["code"], "E_EXPECTED_INDENT")
        self.assertEqual(finding["line"], 2)
        self.assertEqual(finding["col"], 1)
        self.assertIn("after function definition on line 1", finding["message"])

    def test_unexpected_indent_mirrors_interpreter(self):
        finding = self.tool.execute(mode="lint", source="x = 1\n    y = 2\n")["findings"][0]
        self.assertEqual((finding["code"], finding["line"], finding["col"]), ("E_UNEXPECTED_INDENT", 2, 4))

    def test_unindent_mismatch_mirrors_interpreter(self):
        source = "def f():\n    x = 1\n  y = 2\n"
        result = self.tool.execute(mode="lint", source=source)
        errors = [f for f in result["findings"] if f["severity"] == "error"]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["code"], "E_UNINDENT_MISMATCH")
        self.assertEqual(errors[0]["line"], 3)

    def test_tab_error_mirrors_interpreter(self):
        source = "def f():\n    x = 1\n\ty = 2\n"
        result = self.tool.execute(mode="lint", source=source)
        errors = [f for f in result["findings"] if f["severity"] == "error"]
        self.assertEqual([e["code"] for e in errors], ["E_TAB_INCONSISTENT"])
        self.assertEqual(errors[0]["line"], 3)

    def test_tab_only_line_in_space_file(self):
        # Cross-function mixing compiles: the tab-indented def b() body is
        # legal because levels reset between top-level statements.
        source = "def a():\n    x = 1\n\ndef b():\n\ty = 2\n"
        self.assertIsNone(compile_or_none(source))
        result = self.tool.execute(mode="lint", source=source)
        self.assertEqual(result["compile"], "ok")
        self.assertIn(("W_TAB_IN_SPACE_FILE", 5), [(f["code"], f["line"]) for f in result["findings"]])

    def test_non_multiple_indent_width_flagged_when_valid(self):
        source = "if a:\n    b = 1\n    if c:\n        d = 2\n    if e:\n          f = 3\n"
        self.assertIsNone(compile_or_none(source))
        codes = self.codes(source)
        self.assertIn(("W_INDENT_WIDTH", 6), codes)

    def test_pep8_step_note(self):
        source = "if a:\n  b = 1\n  c = 2\n"
        codes = self.codes(source)
        self.assertIn(("I_PEP8_STEP", 1), codes)

    def test_trailing_and_blank_whitespace(self):
        source = "x = 1   \ny = 2\n   \nz = 3\n"
        codes = self.codes(source)
        self.assertIn(("W_TRAILING_WHITESPACE", 1), codes)
        self.assertIn(("W_BLANK_WHITESPACE", 3), codes)

    def test_form_feed_at_line_start_is_legal(self):
        source = "x = 1\n\fy = 2\n"
        result = self.tool.execute(mode="lint", source=source)
        self.assertEqual(result["compile"], "ok")
        self.assertIn(("W_FORM_FEED", 2), [(f["code"], f["line"]) for f in result["findings"]])

    def test_form_feed_after_indent_is_caught_via_compile(self):
        source = "def f():\n    \fx = 1\n"
        codes = self.codes(source)
        self.assertIn("E_EXPECTED_INDENT", [c for c, _ in codes])

    def test_crlf_reported_and_analyzed(self):
        source = "def f():\r\n    x = 1\r\n"
        result = self.tool.execute(mode="lint", source=source)
        self.assertEqual(result["compile"], "ok")
        self.assertEqual(result["newline_style"], "crlf")
        self.assertIn("W_CRLF", [f["code"] for f in result["findings"]])

    def test_bom_reported_and_stripped(self):
        result = self.tool.execute(mode="lint", source="\ufeffx = 1\n")
        self.assertEqual(result["compile"], "ok")
        self.assertTrue(result["bom"])
        self.assertIn("W_BOM", [f["code"] for f in result["findings"]])

    def test_string_content_never_flagged(self):
        source = 's = """\n\ttab inside string\n   spaces\n"""\nx = 1\n'
        codes = self.codes(source)
        self.assertEqual(codes, [])

    def test_continuation_indent_is_free_style_only(self):
        source = "def f():\n    x = [1,\n\t\t2,\n        3]\n    return x\n"
        self.assertIsNone(compile_or_none(source))
        infos = [f for f in self.tool.execute(mode="lint", source=source)["findings"] if f["severity"] == "info"]
        self.assertIn("I_CONTINUATION_TAB", [f["code"] for f in infos])

    def test_visual_dedent_level_warning(self):
        # Interpreter columns: "\tif a:" -> 8, "           y" -> 11 (deeper,
        # unambiguous under every tab size, so it compiles). Visually with
        # tab_width=12 the tab is 12 columns, so y at 11 is SHALLOWER: the
        # visual dedent lands on no live visual level.
        source = "def f():\n\tif a:\n           y = 2\n\tz = 3\n"
        self.assertIsNone(compile_or_none(source))
        result = self.tool.execute(mode="lint", source=source, tab_width=12)
        self.assertIn("W_DEDENT_LEVEL", [f["code"] for f in result["findings"]])
        # Under the default width the same file has no such divergence.
        default = self.tool.execute(mode="lint", source=source)
        self.assertNotIn("W_DEDENT_LEVEL", [f["code"] for f in default["findings"]])

    def test_comment_indent_is_free(self):
        source = "def f():\n        # deep comment\n    x = 1\n"
        self.assertEqual(self.codes(source), [])

    def test_stats_fields(self):
        source = (
            "def outer():\n"
            "    a = 1\n"
            "    def inner():\n"
            "        if a:\n"
            "            return 2\n"
            "        return 3\n"
            "    return inner()\n"
        )
        stats = self.tool.execute(mode="stats", source=source)
        self.assertEqual(stats["total_lines"], 7)
        self.assertEqual(stats["indented_lines"], 6)
        self.assertEqual(stats["space_lines"], 6)
        self.assertEqual(stats["tab_lines"], 0)
        self.assertEqual(stats["mixed_lines"], 0)
        self.assertEqual(stats["inferred_step"], 4)
        self.assertEqual(stats["inferred_style"], "spaces")
        self.assertEqual(stats["max_depth"], 3)
        self.assertEqual(stats["depth_histogram"], {"0": 1, "1": 3, "2": 2, "3": 1})
        names = {f["name"]: f["max_nesting"] for f in stats["per_function"]}
        self.assertEqual(names["outer"], 3)
        self.assertEqual(names["inner"], 2)

    def test_stats_max_functions_cap(self):
        source = "".join(f"def f{i}():\n    return {i}\n" for i in range(30))
        capped = IndentLintTool(max_functions=5)
        stats = capped.execute(mode="stats", source=source)
        self.assertEqual(len(stats["per_function"]), 5)

    def test_stats_on_broken_source_still_returns(self):
        stats = self.tool.execute(mode="stats", source="def f():\nx = 1\n")
        self.assertEqual(stats["status"], "success")
        self.assertEqual(stats["per_function"], [])

    def test_convert_refuses_when_semantics_would_change(self):
        # Levels 4 and 6: converting the 4-space level to one tab (interpreter
        # column 8) inverts the nesting of the 6-space body line, so the
        # converted text no longer parses -> verified refusal.
        source = "if a:\n    if c:\n      d = 2\n"
        self.assertIsNone(compile_or_none(source))
        result = self.tool.execute(mode="convert", source=source, target="tabs", tab_width=4)
        self.assertTrue(result["refused"])
        self.assertEqual(result["converted"], source)
        self.assertTrue(any("does not parse" in note for note in result["notes"]))

    def test_convert_refuses_non_compiling_source(self):
        result = self.tool.execute(mode="convert", source="def f():\nx = 1\n", target="spaces")
        self.assertTrue(result["refused"])
        self.assertEqual(result["converted"], "def f():\nx = 1\n")

    def test_convert_leaves_string_content_alone(self):
        source = 'def f():\n    s = """\n\tkeep\n    """\n    return s\n'
        result = self.tool.execute(mode="convert", source=source, target="tabs", tab_width=4)
        self.assertFalse(result["refused"])
        self.assertIn("\tkeep", result["converted"])
        self.assertIn("multi-line strings", " ".join(result["notes"]))

    def test_convert_non_multiple_indents_left_and_noted(self):
        source = "if a:\n    b = 1\n"
        result = self.tool.execute(mode="convert", source=source, target="tabs", tab_width=3)
        self.assertFalse(result["refused"])
        self.assertEqual(result["converted"], source)
        self.assertTrue(any("not multiples" in note for note in result["notes"]))

    def test_explain_on_rejected_line(self):
        source = "def f():\n    x = 1\n  y = 2\n"
        result = self.tool.execute(mode="explain", source=source, line=3)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["levels"], [0, 4])
        self.assertIsNone(result["parent_construct"])
        self.assertIn("unindent does not match", result["why_the_line_fails"])

    def test_explain_parent_construct(self):
        source = "def f(a):\n    if a:\n        return 1\n    return 0\n"
        result = self.tool.execute(mode="explain", source=source, line=3)
        self.assertEqual(result["levels"], [0, 4, 8])
        self.assertEqual(result["parent_construct"]["kind"], "If")
        stack = [(item["kind"], item.get("name")) for item in result["construct_stack"]]
        self.assertEqual(stack[0], ("If", None))  # innermost construct first
        self.assertIn(("FunctionDef", "f"), stack)
        self.assertIsNone(result["why_the_line_fails"])

    def test_explain_continuation_and_other_line(self):
        source = "x = [1,\n\t2]\n"
        result = self.tool.execute(mode="explain", source=source, line=2)
        self.assertEqual(result["classification"], "tabs")
        result = self.tool.execute(mode="explain", source="def f():\nx = 1\n", line=1)
        self.assertIn("fails at line 2", result["why_the_line_fails"])

    def test_validation_errors(self):
        self.assertIn("mode must be", self.tool.execute(mode="lints", source="x=1\n")["error"])
        self.assertIn("source must be", self.tool.execute(mode="lint", source="")["error"])
        self.assertIn("tab_width must be", self.tool.execute(mode="lint", source="x=1\n", tab_width=17)["error"])
        self.assertIn("target must be", self.tool.execute(mode="convert", source="x=1\n", target="both")["error"])
        self.assertIn("line is required", self.tool.execute(mode="explain", source="x=1\n")["error"])
        self.assertIn("between 1 and", self.tool.execute(mode="explain", source="x=1\n", line=5)["error"])

    def test_input_bounds(self):
        huge = "x = 1\n" + "y = 2\n" * 10
        tiny = IndentLintTool(max_input_bytes=8)
        self.assertIn("max_input_bytes", tiny.execute(mode="lint", source=huge)["error"])
        tiny_lines = IndentLintTool(max_lines=3)
        self.assertIn("max_lines", tiny_lines.execute(mode="lint", source="a\n" * 10)["error"])
        tiny_line_bytes = IndentLintTool(max_line_bytes=10)
        self.assertIn("max_line_bytes", tiny_line_bytes.execute(mode="lint", source="x = '" + "z" * 40 + "'\n")["error"])

    def test_finding_cap_truncates_gracefully(self):
        capped = IndentLintTool(max_findings=5)
        source = "".join(f"line{i}   \n" for i in range(40))
        result = capped.execute(mode="lint", source=source)
        self.assertLessEqual(len(result["findings"]), 5)
        self.assertTrue(result["findings_truncated"])

    def test_deterministic_results(self):
        source = "def f():\n    x = 1\n   y = 2\n"
        first = self.tool.execute(mode="lint", source=source)
        for _ in range(3):
            self.assertEqual(self.tool.execute(mode="lint", source=source), first)


class IndentLintToolRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped indent_lint_tool.yaml."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """The shipped yaml resolves to a tool component exposing IndentLintTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "IndentLintTool")

    def test_manager(self):
        """IndentLintTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, IndentLintTool)
        self.assertEqual(tool.input_keys, ["mode", "source"])

    def test_package_export(self):
        """IndentLintTool is exported from the common_tool package."""
        from agentuniverse.agent.action.tool.common_tool import IndentLintTool as Exported
        from agentuniverse.agent.action.tool.common_tool import __all__ as exported_names

        self.assertIs(Exported, IndentLintTool)
        self.assertIn("IndentLintTool", exported_names)


class SelfReviewRegressionTest(unittest.TestCase):
    """Regressions for defects found by hostile self-review differential
    probes (compile/tokenize oracles over a wider corpus than the originals)."""

    def setUp(self):
        self.tool = IndentLintTool()

    def test_mixed_eol_transport_still_tokenizes(self):
        """Mixed LF/CRLF and CR-only transports must not degrade to the
        untokenized fallback: the same code gets identical verdicts and
        string content never produces style findings."""
        body = (
            'if True:\n'
            '    s = """start\n'
            '\t\tif True:\n'
            '\t\t\tpass\n'
            '\t\t\t\tdeeper\n'
            '"""\n'
            '    pass\n'
            'x = [\n'
            '\t1,\n'
            '\t\t2,\n'
            ']\n'
        )
        lf = self.tool.execute(mode="lint", source=body)
        mixed = body.replace("\n", "\r\n", 4)
        for label, variant in (("mixed", mixed), ("cr", body.replace("\n", "\r"))):
            result = self.tool.execute(mode="lint", source=variant)
            self.assertTrue(result["tokenized"], label)
            self.assertEqual(result["compile"], "ok", label)
            self.assertNotIn(
                "W_SPACE_IN_TAB_FILE", [f["code"] for f in result["findings"]], label
            )
            self.assertNotIn(
                "W_TAB_SPACE_MIX", [f["code"] for f in result["findings"]], label
            )
        lf_stats = self.tool.execute(mode="stats", source=body)
        for variant in (mixed, body.replace("\n", "\r")):
            stats = self.tool.execute(mode="stats", source=variant)
            self.assertEqual(stats["depth_histogram"], lf_stats["depth_histogram"])
            self.assertEqual(stats["continuation_lines"], lf_stats["continuation_lines"])
            self.assertEqual(stats["string_content_lines"], lf_stats["string_content_lines"])
        conv = self.tool.execute(mode="convert", source=mixed, target="spaces")
        self.assertFalse(conv["refused"])

    def test_blank_lines_never_rewritten_by_convert(self):
        """tab -> space -> tab is byte-stable on pure-tab files even when
        they contain tab-only blank lines."""
        source = "if True:\n\tx = 1\n\t\t\n\ty = 2\n"
        to_spaces = self.tool.execute(
            mode="convert", source=source, target="spaces", tab_width=8
        )
        self.assertFalse(to_spaces["refused"])
        back = self.tool.execute(
            mode="convert", source=to_spaces["converted"], target="tabs", tab_width=8
        )
        self.assertFalse(back["refused"])
        self.assertEqual(back["converted"], source)

    def test_convert_form_feed_resets_column_like_interpreter(self):
        """A form feed in the indent prefix resets the column to 0 for BOTH
        the analyzer and the converter: with tab_width=4 the tab after the
        form feed expands to 4 spaces (the next multiple of 4 measured from
        the reset column 0), not to a single space counted from the form
        feed as if it were one column wide."""
        source = "if True:\n  \x0c\tpass\n"
        result = self.tool.execute(mode="convert", source=source, target="spaces", tab_width=4)
        self.assertFalse(result["refused"])
        converted_line = result["converted"].split("\n")[1]
        self.assertEqual(converted_line, "  \x0c    pass")

    def test_convert_preserves_bom_on_output(self):
        """A refused conversion returns the input byte-identical (BOM
        included); an accepted one re-attaches the BOM."""
        broken = "\ufeffif True:\n  pass\n pass\n"
        refused = self.tool.execute(mode="convert", source=broken, target="spaces")
        self.assertTrue(refused["refused"])
        self.assertEqual(refused["converted"], broken)
        accepted = self.tool.execute(
            mode="convert", source="\ufeffif True:\n\tpass\n", target="spaces", tab_width=4
        )
        self.assertFalse(accepted["refused"])
        self.assertTrue(accepted["converted"].startswith("\ufeff"))

    def test_explain_bounded_leading_whitespace_echo(self):
        """The leading-whitespace echo is capped, not the raw prefix."""
        source = " " * 60000 + "x = 1\n"
        result = self.tool.execute(mode="explain", source=source, line=1)
        echo = result["leading_whitespace"]
        self.assertLess(len(echo), 200)
        self.assertIn("more whitespace chars", echo)


if __name__ == "__main__":
    unittest.main()
