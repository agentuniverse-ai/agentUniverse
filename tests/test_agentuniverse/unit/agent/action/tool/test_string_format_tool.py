#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_string_format_tool.py

"""Offline unit tests for StringFormatTool.

The tool is built purely on the standard library and never touches
the network, so this suite runs fully offline. Every claim is
checked against ground truth derived independently of the tool's
implementation — the real ``str.format`` / ``str.format_map`` / ``%``
machinery and ``string.Formatter``:

* the 500-seed lint oracle renders every seeded template with its
  own inert dummy batteries (an oracle-local permissive value class
  plus plain str/int/float, with an independent field-name walk via
  ``string.Formatter``) and asserts the tool's verdict equals
  "real format succeeds with some inert dummy set"; adjudication
  guarantees templates the real machinery renders never carry an
  error finding;
* the scanner decomposition is cross-validated against
  ``string.Formatter().parse`` on every valid seeded template;
* render results are asserted byte-equal to the real
  ``str.format_map`` on the keyword-only seeded subset, and missing
  keys are asserted against precisely reported key names and spans;
* the 300-seed printf oracle asserts the round-trip invariant —
  the original %-template rendered with sample values equals the
  translated .format template rendered with the same values —
  across %s %r %a %d %i %o %x %X %e %E %f %F %g %G %c %% with
  widths, precisions and - + <space> 0 # flags, plus the reverse
  to_percent direction;
* exact unit matrices cover the lint rule set, field extraction
  spans, f-string checking, and the full validation error surface.
"""

import random
import re
import unittest
from string import Formatter

from agentuniverse.agent.action.tool.common_tool import StringFormatTool
from agentuniverse.agent.action.tool.common_tool.string_format_tool import (
    StringFormatTool as DirectStringFormatTool,
)


def codes_of(result):
    """The ordered list of lint/finding codes."""
    return [f["code"] for f in result["findings"]]


def error_codes_of(result):
    return [f["code"] for f in result["findings"] if f["severity"] == "error"]


# --------------------------------------------------------------------- #
# Oracle machinery (independent of the tool's implementation)
# --------------------------------------------------------------------- #

class OracleValue:
    """Test-local inert dummy: real str/int/float format semantics,
    permissive attribute/index traversal."""

    def __init__(self, value):
        self._value = value

    def __getattr__(self, name):
        if name == "_value":
            raise AttributeError(name)
        return OracleValue(self._value)

    def __getitem__(self, key):
        return OracleValue(self._value)

    def __repr__(self):
        return repr(self._value)

    def __str__(self):
        return str(self._value)

    def __format__(self, spec):
        return format(self._value, spec)


def oracle_roles(template):
    """Independent slot-role walk via string.Formatter (stdlib).

    Top-level fields are value slots; fields found inside a format
    spec are spec-token slots (the tool's published dummy policy).
    Raises ValueError when the template is structurally broken.
    """
    pos_roles: dict[int, str] = {}
    kw_roles: dict[str, str] = {}
    auto = [0]
    manual = [-1]

    def record(name, role):
        if name == "":
            slot = auto[0]
            auto[0] += 1
            store, key = pos_roles, slot
        elif name.isdigit():
            manual[0] = max(manual[0], int(name))
            store, key = pos_roles, int(name)
        else:
            store = kw_roles
            key = name.split(".")[0].split("[")[0]
        if store.get(key) != "value":
            store[key] = role

    def walk(text, role):
        for _, fname, spec, _conv in Formatter().parse(text):
            if fname is None:
                continue
            record(fname, role)
            if spec and "{" in spec:
                walk(spec, "nested")

    walk(template, "value")
    return pos_roles, kw_roles, auto[0], manual[0]


def oracle_renders(template):
    """True iff the real str.format renders the template with some
    inert dummy combination (oracle-local policy): value slots get
    one of 'x'/7/2.5 uniformly, spec-token slots get '7'/'x'/7 (the
    bare int matters for nested conversions: repr(7) is the usable
    spec '7' while repr('7') is quoted and unusable)."""
    try:
        pos_roles, kw_roles, auto, manual = oracle_roles(template)
    except ValueError:
        return False
    count = max(auto, manual + 1)
    for plain in ("x", 7, 2.5):
        for nested in ("7", "x", 7):
            args = [
                OracleValue(nested if pos_roles.get(i) == "nested" else plain)
                for i in range(count)
            ]
            kw = {
                k: OracleValue(nested if r == "nested" else plain)
                for k, r in kw_roles.items()
            }
            for _attempt in (0, 1):
                try:
                    template.format(*args, **kw)
                    return True
                except IndexError:
                    args = args + [OracleValue(plain)] * 10
                except Exception:  # noqa: BLE001 - oracle catches all
                    break
    return False


# --------------------------------------------------------------------- #
# Deterministic seeded corpora
# --------------------------------------------------------------------- #

VALID_BLOCKS = [
    "{}", "{0}", "{1}", "{name}", "{user}", "{0.x}", "{d[0]}", "{d[k]}",
    "{!r}", "{!s}", "{!a}", "{:>10}", "{:.2f}", "{name!s:^8}", "{:#x}",
    "{:+d}", "{:%}", "{:,}", "{:n}", "{:c}", "{:5s}", "{:<8}", "{:>8.3f}",
    "{0[0][1]}", "{a.b.c}", "{:{}}", "{0:{1}}", "{:{w}}", "{!r:>{w}}",
    "{{", "}}", "text", " ", "{name!r}", "{0:d}", "{x:{y}d}",
]

INVALID_BLOCKS = [
    "{", "}", "{0} {}", "{} {0}", "{!q}", "{a[]}", "{0.}", "{0:{1:{2}}}",
    "{:!}", "{:+s}", "{!rs}", "{0:{1>{2}}}", "{:}", "{ }", "{0:{}}",
    "{:.{}}", "{0..x}",
]

KEYWORD_POOL = ["name", "user", "d", "a", "w", "x", "y", "k", "b", "count"]


def seeded_templates(count, seed):
    rng = random.Random(seed)
    templates = []
    for _ in range(count):
        blocks = []
        for _ in range(rng.randint(1, 4)):
            pool = VALID_BLOCKS if rng.random() < 0.62 else INVALID_BLOCKS
            blocks.append(rng.choice(pool))
            if rng.random() < 0.5:
                blocks.append(rng.choice(["lit ", "a", " ", " ", "-", "x y "]))
        templates.append("".join(blocks))
    return templates


LINT_CORPUS = seeded_templates(500, seed=252)

RENDER_BLOCKS = [
    "{name}", "{user}", "{name!r}", "{user!s:>8}", "{d[0]}",
    "{d[k]}", "{a.b}", "{name!r:>10}", "{w:.2f}", "{x:^6}",
    "{count:,}", "{v:%}", "{n}", "{name!a}", "{q:#x}", "{t:e}",
    "{y:g}", "{z:>12}", "lit ", "-", " ", "end",
]


def seeded_render_templates(count, seed):
    rng = random.Random(seed)
    templates = []
    for _ in range(count):
        blocks = []
        for _ in range(rng.randint(1, 3)):
            blocks.append(rng.choice(RENDER_BLOCKS))
        templates.append("".join(blocks))
    return templates


RENDER_CORPUS = seeded_render_templates(80, seed=2527)


# --------------------------------------------------------------------- #
# Lint: exact rule matrix
# --------------------------------------------------------------------- #

class StringFormatLintMatrixTest(unittest.TestCase):
    def setUp(self):
        self.tool = StringFormatTool()

    def test_error_matrix(self):
        cases = {
            "{": "unterminated_field",
            "x{": "unterminated_field",
            "}": "stray_close_brace",
            "a}b": "stray_close_brace",
            "{}}": "stray_close_brace",
            "{0} {}": "mixed_numbering",
            "{} {0}": "mixed_numbering",
            "{0} {1} {name} {}": "mixed_numbering",
            "{0:{}}": "mixed_numbering",
            "{!q}": "unknown_conversion",
            "{name!z}": "unknown_conversion",
            "{!rs}": "malformed_conversion",
            "{a[]}": "empty_attribute_or_index",
            "{0.}": "empty_attribute_or_index",
            "{0..x}": "empty_attribute_or_index",
            "{0:{1:{2}}}": "spec_recursion_exceeded",
            "{0:>{1:>{2}}}": "spec_recursion_exceeded",
            "{:!}": "value_independent_spec_error",
            "{:+s}": "value_independent_spec_error",
            "{0:{1>{2}}}": None,  # scanner span claim; verdict must be error
        }
        for template, code in cases.items():
            with self.subTest(template=template):
                result = self.tool.execute("lint", template=template)
                self.assertEqual(
                    result["verdict"], "error",
                    f"{template!r}: {result['findings']}",
                )
                self.assertTrue(
                    result["probe"]["checked"],
                    "every error verdict must come from the probe",
                )
                if code is not None:
                    self.assertIn(code, error_codes_of(result))
                # verdict error <=> the real machinery cannot render it
                self.assertFalse(oracle_renders(template))

    def test_ok_matrix(self):
        cases = {
            "{}": None,
            "{0}": None,
            "{name}": None,
            "{0.x}": None,
            "{d[0]}": None,
            "{d[k]}": None,
            "{!r}": None,
            "{!s}": None,
            "{!a}": None,
            "{:>10}": None,
            "{:.2f}": "type_dependent_spec",
            "{:#x}": "type_dependent_spec",
            "{:+d}": "type_dependent_spec",
            "{:c}": "type_dependent_spec",
            "{:n}": "locale_aware_n_specifier",
            "{:>{}}": "nested_replacement_in_spec",
            "{0:{1}}": "nested_replacement_in_spec",
            "{ x}": "field_name_whitespace",
            "{0}{0}": "duplicate_field_reference",
            "{name}{name!r}": "duplicate_field_reference",
            "{{}}": "no_placeholders",
            "": "no_placeholders",
            "plain": "no_placeholders",
            "{:.{}}": "nested_replacement_in_spec",
        }
        for template, code in cases.items():
            with self.subTest(template=template):
                result = self.tool.execute("lint", template=template)
                self.assertEqual(
                    result["verdict"], "ok",
                    f"{template!r}: {result['findings']}",
                )
                self.assertEqual(error_codes_of(result), [])
                if code is not None:
                    self.assertIn(code, codes_of(result))
                # verdict ok <=> the real machinery renders it
                self.assertTrue(oracle_renders(template))

    def test_probe_metadata_honesty(self):
        result = self.tool.execute("lint", template="{name}")
        self.assertEqual(result["probe"]["keyword_names"], ["name"])
        self.assertEqual(result["probe"]["positional_slots"], 0)
        result = self.tool.execute("lint", template="{} {0} {name}")
        self.assertEqual(result["probe"]["positional_slots"], 1)

    def test_verdict_survives_findings_cap(self):
        # 51 info findings push the lone error finding past the
        # max_findings cap; the verdict must still be error because
        # the real machinery raises (unknown conversion) for any
        # argument values.
        template = "{ x}" * 51 + "{!q}"
        result = self.tool.execute("lint", template=template)
        self.assertLessEqual(len(result["findings"]), 50)
        self.assertEqual(result["verdict"], "error",
                         f"{result['findings'][:3]}")
        self.assertFalse(oracle_renders(template))

    def test_nested_conversion_in_spec_renders(self):
        # repr(int) is a usable spec ('7') while every digit *string*
        # candidate produces a quoted, unusable one — the real
        # machinery renders these, so the verdict must be ok.
        for template in ("{x:{y!r}}", "{0:{1!r}}", "{x:{y!s}}"):
            with self.subTest(template=template):
                result = self.tool.execute("lint", template=template)
                self.assertEqual(
                    result["verdict"], "ok",
                    f"{template!r}: {result['findings']}")
                self.assertEqual(error_codes_of(result), [])
                self.assertTrue(oracle_renders(template))
        self.assertEqual("{x:{y!r}}".format(x=5, y=6), "     5")

    def test_unicode_digit_names_match_real_machinery(self):
        # '²' is str.isdigit() but not a decimal digit: the real
        # machinery treats it as a keyword ('int' would raise, and a
        # crash in the tool is not acceptable). '٠' (Arabic-Indic
        # zero) is a decimal digit and is a real positional index.
        self.assertEqual("{٠}".format(*range(10)), "0")
        self.assertEqual("{²}".format(**{"²": "kw"}), "kw")
        lint = self.tool.execute("lint", template="{²}")
        self.assertEqual(lint["verdict"], "ok")
        fields = self.tool.execute("fields", template="{²}")
        self.assertEqual(fields["scan_errors"], [])
        self.assertEqual(fields["fields"][0]["index_or_key"], "²")
        self.assertEqual(fields["keyword_names"], ["²"])
        indexed = self.tool.execute("fields", template="{٠}")
        self.assertEqual(indexed["max_manual_index"], 0)
        bracket = self.tool.execute("fields", template="{a[²]}")
        self.assertEqual(bracket["fields"][0]["index_parts"][0]["type"],
                         "str")
        rendered = self.tool.execute(
            "render", template="{²}", mapping={"²": "kw"})
        self.assertTrue(rendered["ok"])
        self.assertEqual(rendered["rendered"], "kw")
        # to_percent classifies the name the same way
        percent = self.tool.execute(
            "translate_percent", template="{²}", direction="to_percent")
        self.assertIn("%(²)s", percent["translation"])


# --------------------------------------------------------------------- #
# The 500-seed lint oracle
# --------------------------------------------------------------------- #

class StringFormatLintOracleTest(unittest.TestCase):
    def setUp(self):
        self.tool = StringFormatTool()

    def test_verdict_matches_real_format_on_500_seeds(self):
        mismatches = 0
        for template in LINT_CORPUS:
            expected = oracle_renders(template)
            result = self.tool.execute("lint", template=template)
            got = result["verdict"] == "ok"
            with self.subTest(template=template):
                self.assertEqual(
                    got, expected,
                    f"tool={result['verdict']} oracle={expected}: "
                    f"{result['findings']}",
                )
                if expected:
                    # adjudication: real-renders templates carry no error
                    self.assertEqual(
                        error_codes_of(result), [],
                        f"format renders, errors must be vetoed: {template!r}",
                    )
            if got != expected:
                mismatches += 1
        self.assertEqual(mismatches, 0)

    def test_deterministic(self):
        for template in LINT_CORPUS[:80]:
            first = self.tool.execute("lint", template=template)
            second = self.tool.execute("lint", template=template)
            self.assertEqual(first, second)


# --------------------------------------------------------------------- #
# Scanner cross-validation against string.Formatter
# --------------------------------------------------------------------- #

class StringFormatScannerAgreementTest(unittest.TestCase):
    def setUp(self):
        self.tool = StringFormatTool()

    def test_fields_agree_with_string_formatter(self):
        checked = 0
        for template in LINT_CORPUS:
            if not oracle_renders(template):
                continue  # Formatter().parse raises on broken templates
            result = self.tool.execute("fields", template=template)
            if result["scan_errors"]:
                continue
            expected = [
                (literal, name, spec, conv)
                for literal, name, spec, conv in Formatter().parse(template)
                if name is not None
            ]
            got = [
                (None, f["field_name"],
                 f["format_spec"] if f["has_spec"] else None,
                 f["conversion"])
                for f in result["fields"]
            ]
            self.assertEqual(
                len(expected), len(got), template)
            for (exp_lit, exp_name, exp_spec, exp_conv), \
                    (_, got_name, got_spec, got_conv) in zip(expected, got):
                self.assertEqual(got_name, exp_name, template)
                self.assertEqual(got_conv, exp_conv, template)
                # Formatter reports a missing spec as '' (trailing
                # tuples) or None; the tool reports None or ''
                if not exp_spec:
                    self.assertFalse(got_spec, template)
                else:
                    self.assertEqual(got_spec, exp_spec, template)
            checked += 1
        self.assertGreater(checked, 150)


# --------------------------------------------------------------------- #
# fields mode: exact extraction
# --------------------------------------------------------------------- #

class StringFormatFieldsTest(unittest.TestCase):
    def setUp(self):
        self.tool = StringFormatTool()

    def test_exact_extraction(self):
        template = "pre {a.b[0]!r:>{w}} mid {0[1][k]!s} post {{esc}}"
        result = self.tool.execute("fields", template=template)
        self.assertEqual(result["template"], template)
        self.assertEqual(result["field_count"], 3)  # a.b[0], w, 0[1][k]
        self.assertEqual(result["top_level_field_count"], 2)
        self.assertEqual(result["escape_count"], 2)  # {{ and }}
        first, second = result["fields"]

        self.assertEqual(first["field_name"], "a.b[0]")
        self.assertEqual(first["index_or_key"], "a")
        self.assertEqual(first["attribute_chain"], ["b"])
        self.assertEqual(first["index_parts"],
                         [{"raw": "0", "type": "int", "value": 0}])
        self.assertEqual(first["conversion"], "r")
        self.assertEqual(first["format_spec"], ">{w}")
        self.assertTrue(first["has_spec"])
        self.assertEqual(first["position_span"], [4, 19])
        self.assertEqual(
            [(n["field_name"], n["position_span"]) for n in first["nested"]],
            [("w", [15, 18])],
        )

        self.assertEqual(second["field_name"], "0[1][k]")
        self.assertEqual(second["index_or_key"], 0)
        self.assertEqual(second["index_parts"], [
            {"raw": "1", "type": "int", "value": 1},
            {"raw": "k", "type": "str"},
        ])
        self.assertEqual(second["conversion"], "s")

    def test_numbering_summary(self):
        result = self.tool.execute("fields", template="{} {} {name} {:{w}}")
        self.assertEqual(result["auto_field_count"], 3)   # {}, {}, {w}
        self.assertIsNone(result["max_manual_index"])
        self.assertEqual(result["keyword_names"], ["name", "w"])
        result = self.tool.execute("fields", template="{0} {3}")
        self.assertEqual(result["max_manual_index"], 3)
        self.assertEqual(result["auto_field_count"], 0)


# --------------------------------------------------------------------- #
# render mode
# --------------------------------------------------------------------- #

class StringFormatRenderTest(unittest.TestCase):
    def setUp(self):
        self.tool = StringFormatTool()

    def test_byte_equality_with_format_map(self):
        rng = random.Random(2529)
        value_pool = ["x", "yy", 7, 2.5, True, None, [1, 2], {"k": 1}]
        checked = 0
        for template in RENDER_CORPUS + LINT_CORPUS:
            fields = self.tool.execute("fields", template=template)
            if fields["scan_errors"] or fields["auto_field_count"] or \
                    fields["max_manual_index"] is not None:
                continue
            names = fields["keyword_names"]
            if not names:
                continue
            expected = None
            mapping = None
            for _attempt in range(6):
                candidate = {n: rng.choice(value_pool) for n in names}
                try:
                    expected = template.format_map(candidate)
                    mapping = candidate
                    break
                except Exception:  # noqa: BLE001 - value-shape dependent
                    continue
            if expected is None:
                continue
            result = self.tool.execute(
                "render", template=template, mapping=mapping)
            self.assertTrue(result["ok"], template)
            self.assertEqual(result["rendered"], expected, template)
            checked += 1
        self.assertGreater(checked, 60)

    def test_missing_key_precision(self):
        template = "a {name} b {other.x} c"
        result = self.tool.execute(
            "render", template=template, mapping={"name": 1})
        self.assertFalse(result["ok"])
        self.assertIsNone(result["rendered"])
        self.assertEqual(result["missing_keys"], ["other"])
        finding = result["findings"][0]
        self.assertEqual(finding["code"], "missing_key")
        self.assertEqual(finding["key"], "other")
        # the span points exactly at the offending field
        self.assertEqual(
            template[finding["span"][0]:finding["span"][1]], "{other.x}")

    def test_nested_path_missing_key_from_format_map(self):
        # '{d[k]}' with d present but lacking 'k': the real format_map
        # raises KeyError('k'); the tool must structure it, not crash
        result = self.tool.execute(
            "render", template="{d[k]}", mapping={"d": {"z": 1}})
        self.assertFalse(result["ok"])
        self.assertEqual(result["missing_keys"], ["k"])

    def test_positional_fields_rejected_like_format_map(self):
        for template in ("{0}", "{}", "{0} {name}", "{:{w}}"):
            with self.subTest(template=template):
                result = self.tool.execute(
                    "render", template=template, mapping={"w": 5, "name": 1})
                self.assertFalse(result["ok"])
                self.assertIn(
                    "positional_field_unsupported", error_codes_of(result))

    def test_render_failure_reported_not_raised(self):
        result = self.tool.execute(
            "render", template="{a.b}", mapping={"a": 7})
        self.assertFalse(result["ok"])
        self.assertEqual(error_codes_of(result), ["render_failed"])


# --------------------------------------------------------------------- #
# translate_percent: the 300-seed equivalence oracle
# --------------------------------------------------------------------- #

PERCENT_CONVERSIONS = list("sradi") + list("oxXeEfFgGc")

PERCENT_SAMPLE_VALUES = {
    "s": ["ab", "", 42],
    "r": ["ab", 42],
    "a": ["ab"],
    "d": [0, 7, -42, 1234567],
    "i": [0, 7, -42, 1234567],
    "o": [0, 8, 255, 4096],
    "x": [0, 255, 4096],
    "X": [0, 255, 4096],
    "e": [0.0, 3.14159, -2.5, 1e10, 1e-8],
    "E": [0.0, 3.14159, -2.5, 1e10, 1e-8],
    "f": [0.0, 3.14159, -2.5, 1e10, 1e-8],
    "F": [0.0, 3.14159, -2.5, 1e10, 1e-8],
    "g": [0.0, 3.14159, -2.5, 1e10, 1e-8],
    "G": [0.0, 3.14159, -2.5, 1e10, 1e-8],
    "c": [65, 97, 42],
}


def seeded_percent_cases(count, seed):
    """(template, values_tuple_or_dict) pairs, all fully translatable."""
    rng = random.Random(seed)
    cases = []
    for _ in range(count):
        field_count = rng.randint(1, 4)
        named = rng.random() < 0.3
        chunks = []
        values = [] if not named else {}
        for index in range(field_count):
            conv = rng.choice(PERCENT_CONVERSIONS)
            flags = "".join(
                rng.sample(["-", "+", " ", "0", "#"],
                           rng.randint(0, 2)))
            width = rng.choice(["", "", str(rng.randint(1, 15))])
            prec = ""
            if conv in "eEfFgG" and rng.random() < 0.4:
                prec = "." + str(rng.randint(0, 6))
            length = rng.choice(["", "", "h", "l", "L"])
            value = rng.choice(PERCENT_SAMPLE_VALUES[conv])
            if named:
                key = rng.choice(KEYWORD_POOL) + str(index)
                chunks.append(f"%({key}){flags}{width}{prec}{length}{conv}")
                values[key] = value
            else:
                chunks.append(f"%{flags}{width}{prec}{length}{conv}")
                values.append(value)
            if rng.random() < 0.6:
                chunks.append(rng.choice([" ", "-", " | ", "text ", "s "]))
        template = "".join(chunks)
        if rng.random() < 0.3:
            template += " %% done"
        cases.append((template, tuple(values) if not named else values))
    return cases


PERCENT_CASES = seeded_percent_cases(300, seed=2523)


class StringFormatTranslatePercentOracleTest(unittest.TestCase):
    def setUp(self):
        self.tool = StringFormatTool()

    def test_round_trip_equivalence_on_300_seeds(self):
        for template, values in PERCENT_CASES:
            with self.subTest(template=template):
                result = self.tool.execute(
                    "translate_percent", template=template)
                self.assertEqual(
                    error_codes_of(result), [],
                    f"{template!r}: {result['findings']}")
                self.assertTrue(result["translatable"])
                translation = result["translation"]
                if isinstance(values, dict):
                    expected = template % values
                    got = translation.format(**values)
                else:
                    expected = template % values
                    got = translation.format(*values)
                self.assertEqual(
                    got, expected,
                    f"{template!r} -> {translation!r}: "
                    f"{got!r} != {expected!r}",
                )

    def test_reverse_direction_equivalence(self):
        checked = 0
        for template, values in PERCENT_CASES[:120]:
            forward = self.tool.execute(
                "translate_percent", template=template)
            back = self.tool.execute(
                "translate_percent", template=forward["translation"],
                direction="to_percent",
            )
            if not back["translatable"]:
                continue  # honest rejection is allowed; never miscompile
            if isinstance(values, dict):
                expected = template % values
                got = back["translation"] % values
            else:
                expected = template % values
                got = back["translation"] % values
            self.assertEqual(
                got, expected,
                f"{template!r} -> {forward['translation']!r} -> "
                f"{back['translation']!r}",
            )
            checked += 1
        self.assertGreater(checked, 50)

    def test_full_conversion_coverage(self):
        """Every listed conversion appears in the corpus."""
        used = set()
        for template, _ in PERCENT_CASES:
            for match in re.finditer(
                    r"%(?:\([^)]*\))?[-+ 0#]*[hlL]*(?:\d+)?(?:\.\d+)?"
                    r"([a-zA-Z])", template):
                used.add(match.group(1))
        for conv in PERCENT_CONVERSIONS:
            self.assertIn(conv, used)
        self.assertTrue(any("%%" in t for t, _ in PERCENT_CASES))

    def test_flag_edge_equivalence(self):
        cases = [
            ("%-08.2f", (3.14159,)), ("%08.2f", (3.14159,)),
            ("%-8d", (42,)), ("%+ d", (42,)), ("%+ d", (-42,)),
            ("%#d", (5,)), ("%#o", (8,)), ("%#.0f", (3.0,)),
            ("%05c", (65,)), ("% x", (255,)), ("%-5s", ("ab",)),
            ("%5s", ("ab",)), ("%a", ("é",)), ("%F", (1.5,)),
            ("%#g", (1.0,)), ("%+.2e", (12345.6789,)),
            ("% .1g", (0.049,)), ("%-10.3E", (1234.5,)),
            ("%015.6g", (2.5e-7,)), ("%#+x", (255,)),
            ("%(n)s=%(v)05.1f", {"n": "n", "v": 3.5}),
            ("100%%", ()), ("%hd", (5,)), ("%ld", (5,)),
            ("%-10r", ("ab",)), ("%10r", ("ab",)),
        ]
        for template, values in cases:
            with self.subTest(template=template):
                result = self.tool.execute(
                    "translate_percent", template=template)
                self.assertTrue(
                    result["translatable"],
                    f"{template!r}: {result['findings']}")
                if isinstance(values, dict):
                    expected = template % values
                    got = result["translation"].format(**values)
                else:
                    expected = template % values
                    got = result["translation"].format(*values)
                self.assertEqual(got, expected)

    def test_untranslatable_reported_honestly(self):
        cases = {
            "%*d": "not_translatable",
            "%-*s": "not_translatable",
            "%.*f": "not_translatable",
            "%.3s": "not_translatable",
            "%10.2r": "not_translatable",
            "%.1c": "not_translatable",
            "%.5d": "not_translatable",
            "%.3o": "not_translatable",
            "%.2x": "not_translatable",
            "%q": "unsupported_format_character",
            "%5": "incomplete_format",
            "%": "incomplete_format",
            "%d %": "incomplete_format",
            "%(a)s %s": "mixed_named_positional",
        }
        for template, code in cases.items():
            with self.subTest(template=template):
                result = self.tool.execute(
                    "translate_percent", template=template)
                self.assertFalse(result["translatable"])
                self.assertIn(code, error_codes_of(result))

    def test_percent_c_caveat_info(self):
        result = self.tool.execute("translate_percent", template="%c")
        self.assertTrue(result["translatable"])
        self.assertEqual(result["translation"], "{0:c}")
        self.assertIn("percent_c_int_only", codes_of(result))
        self.assertEqual("A", "%c" % 65, "{0:c}".format(65))

    def test_to_percent_untranslatable(self):
        cases = [
            "{:5}", "{:^6}", "{:,}", "{:_d}", "{:*^7}", "{:n}",
            "{:{w}}", "{0:{1}}", "{a.b}", "{a[0]}", "{x!q:5}",
            "{:>10.2f},{x}",  # mixed positional + keyword
        ]
        for template in cases:
            with self.subTest(template=template):
                result = self.tool.execute(
                    "translate_percent", template=template,
                    direction="to_percent")
                self.assertFalse(result["translatable"])
                self.assertTrue(error_codes_of(result))

    def test_to_percent_translatable(self):
        cases = [
            ("{}", "%s", ("ab",)),
            ("{0}", "%s", ("ab",)),
            ("{name}", "%(name)s", ({"name": "v"},)),
            ("{!r}", "%r", ("ab",)),
            ("{!a}", "%a", ("ab",)),
            ("{a!r:>10}", "%(a)10r", ({"a": "ab"},)),
            ("{x:>8.2f}", "%(x)8.2f", ({"x": 3.14159},)),
            ("{0:<8d}", "%-8d", (42,)),
            ("{0:05d}", "%05d", (42,)),
            ("{0:+d}", "%+d", (42,)),
            ("{0:#x}", "%#x", (255,)),
            ("{0:#o}", "%#o", (8,)),
            ("{0:.2e}", "%.2e", (1234.5,)),
            ("{0:12.4g}", "%12.4g", (2.5e-7,)),
            ("100%", "100%%", ()),
            ("{{literal}}", "{literal}", ()),
        ]
        for template, expected_percent, values in cases:
            with self.subTest(template=template):
                result = self.tool.execute(
                    "translate_percent", template=template,
                    direction="to_percent")
                self.assertTrue(
                    result["translatable"],
                    f"{template!r}: {result['findings']}")
                self.assertEqual(result["translation"], expected_percent)
                if values:
                    if isinstance(values[0], dict):
                        expected = template.format(**values[0])
                        got = result["translation"] % values[0]
                    else:
                        expected = template.format(*values)
                        got = result["translation"] % values
                    self.assertEqual(got, expected)


# --------------------------------------------------------------------- #
# check_fstring
# --------------------------------------------------------------------- #

class StringFormatFStringTest(unittest.TestCase):
    def setUp(self):
        self.tool = StringFormatTool()

    def test_literal_extraction(self):
        template = 'f"hi {name!r:>10} and {x+1:>{w}}"'
        result = self.tool.execute("check_fstring", template=template)
        self.assertTrue(result["ok"])
        self.assertEqual(result["kind"], "literal")
        self.assertEqual(result["literal_parts"], ["hi ", " and "])
        by_expr = {e["expression"]: e for e in result["expressions"]}
        self.assertEqual(by_expr["name"]["conversion"], "r")
        self.assertEqual(by_expr["name"]["format_spec"], ">10")
        self.assertEqual(by_expr["name"]["position_span"], [5, 17])
        self.assertEqual(template[5:17], "{name!r:>10}")
        self.assertEqual(by_expr["x + 1"]["format_spec"], ">{w}")
        self.assertEqual(by_expr["x + 1"]["nested_spec_fields"], ["w"])
        self.assertEqual(by_expr["w"]["position_span"], [28, 31])
        self.assertEqual(template[28:31], "{w}")

    def test_inner_source(self):
        result = self.tool.execute("check_fstring", template="a {v} b {w.x:>3}")
        self.assertTrue(result["ok"])
        self.assertEqual(result["kind"], "inner_source")
        self.assertEqual(
            [(e["expression"], e["format_spec"]) for e in result["expressions"]],
            [("v", None), ("w.x", ">3")],
        )

    def test_triple_quoted_multiline(self):
        template = "f'''multi {a}\nline {b!s}'''"
        result = self.tool.execute("check_fstring", template=template)
        self.assertTrue(result["ok"])
        spans = {e["expression"]: e["position_span"]
                 for e in result["expressions"]}
        self.assertEqual(spans["a"], [10, 13])
        self.assertEqual(spans["b"], [19, 24])
        self.assertEqual(result["literal_parts"], ["multi ", "\nline "])

    def test_syntax_findings(self):
        cases = [
            "broken {name",
            'f"unterminated {x',
            'f"{x!q}"',
            'f"{x"',
        ]
        for template in cases:
            with self.subTest(template=template):
                result = self.tool.execute("check_fstring", template=template)
                self.assertFalse(result["ok"])
                self.assertEqual(
                    error_codes_of(result), ["fstring_syntax_error"])
                self.assertTrue(result["findings"][0]["message"])

    def test_compile_level_syntax_errors(self):
        # ast.parse accepts these; the real compiler rejects them
        # ('yield'/'await' outside a function only surfaces at
        # compile() time), so the tool must compile, not just parse.
        cases = ['f"{yield}"', 'f"{await z}"', 'f"{x} {yield}"',
                 'f"{(yield)}"']
        for template in cases:
            with self.subTest(template=template):
                with self.assertRaises(SyntaxError):
                    compile(template, "<case>", "eval")
                result = self.tool.execute("check_fstring", template=template)
                self.assertFalse(result["ok"])
                self.assertIn("fstring_syntax_error", error_codes_of(result))

    def test_deep_expression_no_crash(self):
        # a ~2000-deep expression AST must not raise RecursionError
        template = "{" + "1+" * 1000 + "1}"
        result = self.tool.execute("check_fstring", template=template)
        self.assertTrue(result["ok"])
        self.assertIn("analysis_depth_exceeded", codes_of(result))
        self.assertTrue(len(result["expressions"]) >= 1)

    def test_empty_spec_ok(self):
        result = self.tool.execute("check_fstring", template="f'{x:}'")
        self.assertTrue(result["ok"])
        self.assertEqual(result["expressions"][0]["format_spec"], "")

    def test_nested_fstring_in_expression(self):
        template = 'f"outer {f\'in {y}\'} end"'
        result = self.tool.execute("check_fstring", template=template)
        self.assertTrue(result["ok"])
        exprs = [(e["expression"], e["depth"]) for e in result["expressions"]]
        self.assertIn(("y", 2), exprs)
        self.assertIn("nested_fstring_in_expression", codes_of(result))

    def test_not_an_fstring(self):
        result = self.tool.execute("check_fstring", template='f"x"+y')
        self.assertFalse(result["ok"])
        self.assertIn("not_an_fstring", error_codes_of(result))

    def test_quoted_inner_source_is_literal_ok(self):
        # a bare quoted source wraps into an f-string with quote
        # literals — legal, no expressions
        result = self.tool.execute("check_fstring", template='"plain"')
        self.assertTrue(result["ok"])
        self.assertEqual(result["expressions"], [])


# --------------------------------------------------------------------- #
# Validation matrix
# --------------------------------------------------------------------- #

class StringFormatValidationTest(unittest.TestCase):
    def setUp(self):
        self.tool = StringFormatTool()

    def assert_invalid(self, **kwargs):
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_mode(self):
        self.assert_invalid(mode="nope", template="{}")
        self.assert_invalid(mode=None, template="{}")

    def test_template(self):
        self.assert_invalid(mode="lint")
        self.assert_invalid(mode="lint", template=123)
        self.assert_invalid(mode="lint", template="{" * 4001)
        self.assert_invalid(mode="fields", template=["{}"])

    def test_field_cap(self):
        self.assert_invalid(mode="lint", template="{}" * 201)
        result = self.tool.execute(mode="lint", template="{}" * 200)
        self.assertEqual(result["verdict"], "ok")

    def test_mapping(self):
        self.assert_invalid(mode="render", template="{a}")
        self.assert_invalid(mode="render", template="{a}", mapping=["x"])
        self.assert_invalid(mode="render", template="{a}", mapping={1: "x"})
        self.assert_invalid(
            mode="render", template="{a}", mapping={str(i): i for i in range(201)})
        self.assert_invalid(
            mode="lint", template="{}", mapping={"a": 1})

    def test_direction(self):
        self.assert_invalid(
            mode="translate_percent", template="%s", direction="sideways")
        self.assert_invalid(
            mode="lint", template="{}", direction="to_format")

    def test_render_cap(self):
        self.assert_invalid(
            mode="render", template="{a}{a}{a}",
            mapping={"a": "x" * 40000},
        )


# --------------------------------------------------------------------- #
# Package-level ergonomics
# --------------------------------------------------------------------- #

class StringFormatToolSurfaceTest(unittest.TestCase):
    def test_exported_from_package(self):
        self.assertIs(StringFormatTool, DirectStringFormatTool)

    def test_name_and_description(self):
        tool = StringFormatTool()
        self.assertEqual(tool.name, "string_format_tool")
        self.assertTrue(tool.description.startswith("String format tool"))

    def test_config_fields_are_real_pydantic_fields(self):
        # the documented Attributes must be real fields: constructor
        # kwargs are honored and instance assignment works (as a
        # ClassVar the knobs were dead config).
        capped = StringFormatTool(max_template_chars=8)
        self.assertEqual(capped.max_template_chars, 8)
        with self.assertRaises(ValueError):
            capped.execute("lint", template="x" * 9)
        tool = StringFormatTool()
        tool.max_findings = 2
        result = tool.execute("lint", template="{ x}" * 6)
        self.assertEqual(len(result["findings"]), 2)
        tool.max_template_chars = 4
        with self.assertRaises(ValueError):
            tool.execute("lint", template="xxxxx")


if __name__ == "__main__":
    unittest.main()


# --------------------------------------------------------------------- #

class StringFormatBracketStateTest(unittest.TestCase):
    """The field-name scanner must mirror the real machinery's bracket
    rule: ``[`` opens an index part that only the first ``]`` closes
    (no nesting), and ':', '!' and '}' inside the index part are
    ordinary key characters."""

    def test_names_agree_with_formatter_bracket_state(self):
        cases = {
            "{a[b[c]]}": "a[b[c]]",   # first ']' closes; second is literal
            "{a[[]}": "a[[]",
            "{a[b]c]d}": "a[b]c]d",
            "{a[}b]}": "a[}b]",
            "{a[b:c]}": "a[b:c]",
            "{a[b][c]}": "a[b][c]",
        }
        for template, expected in cases.items():
            with self.subTest(template=template):
                fmt_name = Formatter().parse(template).__next__()[1]
                self.assertEqual(fmt_name, expected)
                result = StringFormatTool().execute(
                    "fields", template=template)
                self.assertEqual(
                    [f["field_name"] for f in result["fields"]],
                    [expected])
                self.assertEqual(result["scan_errors"], [])

    def test_unbalanced_bracket_still_lints_like_the_real_format(self):
        # one '[' whose ']' arrives much later: the real machinery
        # takes everything between as the index key and renders, so
        # the veto contract demands verdict ok with zero errors.
        template = "!{x[!r:{w}{p}}{{{x.0!r:>{}{}}{b[0]!s:>{}{}}"
        fmt_name = Formatter().parse(template).__next__()[1]
        self.assertEqual(
            fmt_name, "x[!r:{w}{p}}{{{x.0!r:>{}{}}{b[0]")
        verdict = StringFormatTool().execute("lint", template=template)
        self.assertEqual(verdict["verdict"], "ok")
        self.assertEqual(error_codes_of(verdict), [])

    def test_render_missing_key_reports_the_real_first_segment(self):
        # the index key contains '.', but the machinery looks up the
        # first segment 'a' — not 'a[b.c' — before indexing.
        template = "{a[b.c]}"
        result = StringFormatTool().execute(
            "render", template=template, mapping={})
        self.assertEqual(result["missing_keys"], ["a"])


class StringFormatFStringSpanTest(unittest.TestCase):
    """f-string expression spans must honor Python expression nesting:
    brace displays (dict/set literals), slices, lambdas, walrus and
    string literals containing braces do not terminate the field."""

    def test_spans_cover_brace_displays_exactly(self):
        cases = [
            'f"{ {1, 2} }"',
            "f\"{ {'a':1}['a'] }\"",
            "f\"{ {k: v for k, v in []} }\"",
            "f'{d[\"}\"]}'",
            "f'{a[1:2]}'",
            "f'{x if y else z}'",
            "f'{a != b}'",
            'f"{(lambda: 5)()}"',
            "f'{(n := 5)}'",
        ]
        for template in cases:
            with self.subTest(template=template):
                result = StringFormatTool().execute(
                    "check_fstring", template=template)
                self.assertTrue(result["ok"], result["findings"])
                top = [e for e in result["expressions"]
                       if e["depth"] == 1]
                self.assertEqual(len(top), 1)
                s0, s1 = top[0]["position_span"]
                raw = template[s0:s1]
                self.assertTrue(
                    raw.startswith("{") and raw.endswith("}"),
                    raw)
                # the span covers the expression verbatim (ast.unparse
                # normalizes quote style, so compare modulo quotes and
                # spaces)
                inner = raw[1:-1].replace("'", '"').replace(" ", "")
                expr = (top[0]["expression"].replace("'", '"')
                        .replace(" ", ""))
                self.assertIn(expr, inner)

    def test_nested_spec_field_span(self):
        result = StringFormatTool().execute(
            "check_fstring", template="f'{x!s:{a}}'")
        spans = [(e["expression"], tuple(e["position_span"]))
                 for e in result["expressions"]]
        self.assertEqual(spans, [("x", (2, 11)), ("a", (7, 10))])
