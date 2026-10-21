#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_regex_lint_tool.py

"""Tests for RegexLintTool.

Oracle policy: every dynamic claim about CPython's ``re`` engine is
verified against the running interpreter (3.11 when these tests were
authored), never assumed:

* ``test_compile_verdict_oracle`` — 500 seeded patterns (a valid pool
  plus random mutations): the tool's compile verdict must byte-agree
  with the real ``re.compile`` outcome, including the exact
  ``re.error.pos`` when the engine reports one, and the
  OverflowError / RecursionError outcomes for absurd repeat counts
  and nesting depth.
* ``test_structure_group_map_oracle`` — the tool's group map must
  equal the real parser's (``re._parser`` / ``sre_parse``)
  ``state.groupdict`` inverted, and every group span must point at
  the actual parentheses.
* ``test_lookbehind_width_oracle`` — the structural fixed-width
  verdict must agree with the real compile outcome for a battery of
  lookbehind shapes (including backreference widths, which CPython
  resolves to the referenced group's width).
* ``test_evil_corpus_flagged`` — 20 published catastrophic-backtracking
  patterns, each hand-graded, each of which must be flagged with the
  right severity grade; precision controls must stay unflagged.
"""

import random
import re
import warnings

import pytest

try:
    import re._parser as _sre_parser
except ImportError:  # Python 3.10
    import sre_parse as _sre_parser  # type: ignore[no-redef]

from agentuniverse.agent.action.tool.common_tool.regex_lint_tool import (
    RegexLintTool,
)


@pytest.fixture()
def tool() -> RegexLintTool:
    return RegexLintTool()


# --------------------------------------------------------------------- #
# The published catastrophic-backtracking corpus (hand-graded).
# --------------------------------------------------------------------- #
EVIL_CORPUS = [
    (r"(a+)+$", "exponential"),
    (r"(a|aa)+$", "exponential"),
    (r"(.*a).*b", "polynomial"),
    (r"(a*)*b", "exponential"),
    (r"(a|a)*$", "exponential"),
    (r"(a|ab)*c", "exponential"),
    (r"(.*a){10}b", "exponential"),
    (r"([a-zA-Z]+)*$", "exponential"),
    (r"(a+)*", "exponential"),
    (r"a*a*a*b", "polynomial"),
    (r"([a-z]+)*x", "exponential"),
    (r"(a?)+$", "exponential"),
    (r"(a*)*$", "exponential"),
    (r"(a{1,3})+$", "exponential"),
    (r"(\w*)*$", "exponential"),
    (r"(\w+\s?)*$", "exponential"),  # the StackOverflow 2019 shape
    (r"(a*b*)*c", "exponential"),
    (r"(a|b|ab)*c", "exponential"),
    (r"(a+|b+)*$", "exponential"),
    (r".*.*b", "polynomial"),
]

# Patterns with pinned boundaries that must NOT be graded exponential
# (the b-anchor and disjoint-alphabet shapes disambiguate the runs).
PRECISION_CONTROLS = [
    r"(a+b)+$",
    r"([0-9]+[a-z]+)+",
    r"[0-9]*[a-z]*b",
    r"(foo|bar)+",
    r"a?b?c?",
    r"^\d{4}-\d{2}-\d{2}$",
    r"(ab+)+c",
    r"[\w.+-]+@[\w-]+\.[a-z]{2,}",
]

# A diverse pool of valid patterns; mutations of these feed the
# 500-pattern compile oracle.
VALID_POOL = [
    r"abc", r"a", r"", r"a|b|c", r"^a", r"a$", r"^$", r".", r"a.c",
    r"a*", r"a+", r"a?", r"a*?", r"a+?", r"a??", r"a{2}", r"a{2,}",
    r"a{2,5}", r"a{0,3}", r"a{2,5}?", r"[abc]", r"[^abc]", r"[a-z]",
    r"[a-zA-Z0-9_]", r"[]a]", r"[a-z0-9\-]", r"\d", r"\w+", r"\s*",
    r"\D+", r"\W", r"\S", r"\bword\b", r"\B", r"\Astart", r"end\Z",
    r"(a)", r"(a)(b)(c)", r"(?:ab)+", r"(a|b)+c", r"(?P<name>a+)",
    r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})", r"(a)\1", r"(a)(b)\2\1",
    r"(?P<x>a)(?P=x)", r"(?=a)", r"(?!a)", r"a(?=b)", r"(?<=a)b",
    r"(?<!a)b", r"(?<=ab)c", r"(?<=a|b)c", r"(?#comment)a", r"((a))",
    r"(a(b(c)))", r"a|", r"|a", r"(?:)", r"a\.", r"\.", r"\.", r"\*",
    r"\(\)", r"\[abc\]", r"\{2\}", r"a\|b", r"\\", r"\n", r"\t",
    r"\x41", r"\x7f", r"caf\xc3\xa9", r"中", r"\u4e2d", r"foo.bar",
    r"https?://[\w.-]+(/[\w./-]*)?", r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", r"(a)?b(?(1)c|d)",
    r"a?# not verbose", r"a++", r"a*+", r"(?>a|b)c", r"(?i:abc)",
    r"(?i)abc", r"(?s).", r"(?m)^a", r"(?x)a b", r"(?im-sx:a)",
    r"[\w.+-]+", r"[^\d]", r"(a+)(b+)?", r"((?:a|b)c)+", r"x{0}y",
    r"a{,3}", r"(a)|(b)", r"(a(b)?)+", r"\$\d+\.\d{2}",
    r"^\s*$", r"\w+@\w+\.\w+", r"[\x00-\x1f]", r"(?<=\d{4})-",
    r"\N{SNOWMAN}", r"a{10}", r"((a)|(b))+", r"(?<=(a))b",
]

# Lookbehind battery: (pattern, does CPython reject it as not
# fixed-width?) — verified live in the test, not trusted blindly.
LOOKBEHIND_BATTERY = [
    (r"(?<=a)b", False),
    (r"(?<=ab)b", False),
    (r"(?<=a|b)b", False),
    (r"(?<=ab|cd)b", False),
    (r"(?<=a|bb)b", True),
    (r"(?<=a+)b", True),
    (r"(?<=a*)b", True),
    (r"(?<=a?)b", True),
    (r"(?<=a{2})b", False),
    (r"(?<=a{2,3})b", True),
    (r"(?<=x{0,3})b", True),
    (r"(?<=a?b)b", True),
    (r"(?<=ab?)b", True),
    (r"(?<!a*b)b", True),
    (r"(?<=(a))b", False),
    (r"(?<=((a)))b", False),
    (r"(?<=(a)|b)b", False),
    (r"(?<=\d)b", False),
    (r"(?<=^)b", False),
    (r"(?<=\b)b", False),
    (r"(a)(?<=\1)b", False),
    (r"(a)(?<=\1?)b", True),
    (r"(?<=\d{4})-", False),
]


# --------------------------------------------------------------------- #
# Compile-verdict oracle — 500 seeded patterns
# --------------------------------------------------------------------- #

def _real_outcome(pattern: str):
    """What the real engine does: None when it compiles, else the
    (exception class name, message, position) triple."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            re.compile(pattern)
        return None
    except re.error as exc:
        return ("re.error", str(exc), getattr(exc, "pos", None))
    except OverflowError:
        return ("OverflowError", None, None)
    except RecursionError:
        return ("RecursionError", None, None)


def _mutate(rng: random.Random, base: str) -> str:
    ops = ("delete", "insert", "duplicate", "swap", "truncate", "replace")
    pattern = base
    for _ in range(rng.randint(1, 3)):
        if not pattern:
            pattern = rng.choice("ab(|){[.*+?")
            continue
        op = rng.choice(ops)
        idx = rng.randrange(len(pattern))
        if op == "delete":
            pattern = pattern[:idx] + pattern[idx + 1:]
        elif op == "insert":
            pattern = pattern[:idx] + rng.choice(
                "()[]{}*+?|^$.\\abzZ0123456789,") + pattern[idx:]
        elif op == "duplicate":
            pattern = pattern[:idx] + pattern[idx] + pattern[idx:]
        elif op == "swap" and idx + 1 < len(pattern):
            pattern = (pattern[:idx] + pattern[idx + 1] + pattern[idx]
                       + pattern[idx + 2:])
        elif op == "truncate":
            pattern = pattern[:idx]
        elif op == "replace":
            pattern = (pattern[:idx] + rng.choice(
                "()[]{}*+?|^$.\\abzZ0123456789,") + pattern[idx + 1:])
    return pattern[:4000]


def test_pool_is_valid():
    """The oracle pool itself must compile on this interpreter."""
    for pattern in VALID_POOL:
        assert _real_outcome(pattern) is None, pattern


def test_compile_verdict_oracle(tool):
    rng = random.Random(20261021)
    checked = 0
    position_agreements = 0
    while checked < 500:
        base = rng.choice(VALID_POOL)
        mutated = _mutate(rng, base)
        real = _real_outcome(mutated)
        result = tool.execute(mode="lint", pattern=mutated)
        if real is None:
            assert result["compiles"] is True, mutated
            assert result["compile_error"] is None, mutated
            assert not any(f["severity"] == "error"
                           for f in result["findings"]), mutated
        else:
            exc_type, message, position = real
            assert result["compiles"] is False, (mutated, real)
            error = result["compile_error"]
            assert error["type"] == exc_type, (mutated, real, error)
            assert error["message"] == message, (mutated, message,
                                                 error["message"])
            assert error["position"] == position, (mutated, position,
                                                   error["position"])
            assert result["findings"][0]["severity"] == "error", mutated
            if isinstance(position, int):
                span = result["findings"][0]["span"]
                assert span == [position, position + 1], (mutated, span)
                position_agreements += 1
        checked += 1
    # The mutation mix must actually exercise positioned errors.
    assert position_agreements >= 50, position_agreements


# --------------------------------------------------------------------- #
# Structure oracle — group map vs the real parser
# --------------------------------------------------------------------- #

def test_structure_group_map_oracle(tool):
    for pattern in VALID_POOL:
        outcome = _real_outcome(pattern)
        if outcome is not None:
            continue  # the parser raises; group map is best-effort
        result = tool.execute(mode="structure", pattern=pattern)
        parsed = _sre_parser.parse(pattern)
        expected = {str(number): name
                    for name, number in parsed.state.groupdict.items()}
        for number in range(1, parsed.state.groups):
            expected.setdefault(str(number), None)
        assert result["group_map"] == expected, (
            pattern, result["group_map"], expected)
        assert len(result["group_map"]) == parsed.state.groups - 1, pattern
        assert result["compiles"] is True, pattern
        for number, span in result["group_spans"].items():
            start, end = span
            assert pattern[start] == "(", (pattern, number, span)
            assert pattern[end - 1] == ")", (pattern, number, span)


def test_structure_nodes_and_quantifiers(tool):
    result = tool.execute(mode="structure", pattern=r"(?P<y>\d{4})-(\d{2})")
    kinds = [n["type"] for n in result["nodes"]]
    assert kinds[0] == "root"
    assert "group" in kinds and "shorthand" in kinds
    quant_nodes = [n for n in result["nodes"] if "quantifier" in n]
    first_quant = quant_nodes[0]["quantifier"]
    assert {k: first_quant[k] for k in ("min", "max", "kind")} == \
        {"min": 4, "max": 4, "kind": "greedy"}
    star = tool.execute(mode="structure", pattern=r"a*")
    a_node = star["nodes"][1]
    assert a_node["quantifier"]["max"] is None  # unbounded serialized as null
    assert a_node["quantifier"]["min"] == 0


def test_structure_verbose_flag_scanning(tool):
    with pytest.raises(ValueError):
        # structure mode rejects the flags option outright.
        tool.execute(mode="structure", pattern="a b", flags="X")
    linted = tool.execute(mode="lint", pattern="a  b # note", flags="X")
    assert linted["compiles"] is True
    estimated = tool.execute(mode="estimate", pattern="a  b # c",
                             flags="VERBOSE", text_length=4)
    assert estimated["backtracking_risk_class"] == "linear"


# --------------------------------------------------------------------- #
# Lookbehind width oracle
# --------------------------------------------------------------------- #

def test_lookbehind_width_oracle(tool):
    for pattern, expected_reject in LOOKBEHIND_BATTERY:
        outcome = _real_outcome(pattern)
        actually_rejected = outcome is not None and \
            "fixed-width" in (outcome[1] or "")
        # The battery's expectation is verified live first.
        assert actually_rejected == expected_reject, (
            pattern, outcome, "battery expectation is stale")
        located = tool._locate_variable_lookbehind(pattern)
        assert (located is not None) == expected_reject, (
            pattern, located, expected_reject)
        if expected_reject:
            result = tool.execute(mode="lint", pattern=pattern)
            codes = [f["code"] for f in result["findings"]]
            assert "lookbehind_variable_width" in codes, pattern
            assert result["findings"][0]["span"] == located, pattern


# --------------------------------------------------------------------- #
# Evil corpus and precision
# --------------------------------------------------------------------- #

def test_evil_corpus_flagged(tool):
    for pattern, grade in EVIL_CORPUS:
        result = tool.execute(mode="lint", pattern=pattern)
        assert result["compiles"] is True, pattern  # evil but valid
        redos = [f for f in result["findings"]
                 if f["code"].startswith("redos_")]
        assert redos, f"unflagged evil pattern: {pattern}"
        codes = {f["code"] for f in redos}
        if grade == "exponential":
            assert "redos_exponential" in codes, pattern
            severities = {f["severity"] for f in redos}
            assert "warning" in severities, pattern
        else:
            assert "redos_polynomial" in codes, pattern
        estimate = tool.execute(mode="estimate", pattern=pattern,
                                text_length=64)
        assert estimate["backtracking_risk_class"] == grade, (
            pattern, estimate["backtracking_risk_class"], grade)
        assert estimate["heuristic"] is True


def test_precision_controls_not_exponential(tool):
    for pattern in PRECISION_CONTROLS:
        result = tool.execute(mode="lint", pattern=pattern)
        codes = [f["code"] for f in result["findings"]]
        assert "redos_exponential" not in codes, pattern
        estimate = tool.execute(mode="estimate", pattern=pattern,
                                text_length=64)
        assert estimate["backtracking_risk_class"] in (
            "linear", "polynomial", "unknown"), pattern


# --------------------------------------------------------------------- #
# Specific finding codes
# --------------------------------------------------------------------- #

@pytest.mark.parametrize("pattern,code", [
    (r"a(b", "unterminated_group"),
    (r"[]", "unterminated_character_class"),
    (r"a[b", "unterminated_character_class"),
    (r"(?P<x>a)(?P<x>b)", "duplicate_group_name"),
    (r"(a)\2", "undefined_group_reference"),
    (r"\2(a)", "undefined_group_reference"),
    (r"(?P=x)", "unknown_group_name_ref"),
    (r"(?<=a+)b", "lookbehind_variable_width"),
    (r"a{2,1}", "bad_repeat_range"),
    (r"a**", "double_quantifier"),
    (r"*", "nothing_to_repeat"),
    (r"a(?i)b", "misplaced_global_flag"),
    (r"a{4294967296}", "repeat_count_overflow"),
    (r"(?", "unexpected_end"),
    (r"(?z)", "unknown_extension"),
    (r"(?<name>a)", "unknown_extension"),
    (r"(?P<1x>a)", "bad_group_name"),
    (r"\q", "bad_escape"),
    (r"\x{110000}", "parse_error"),
    (r"(a+)+$", "redos_exponential"),
    (r"a*a*b", "redos_polynomial"),
    (r"a.*b", "redos_untrusted_input"),
    (r"[[:alpha:]]", "nested_set_possible"),
    (r"[[a][b]]", "nested_set_possible"),
    (r"{name}", "brace_literal"),
    (r"a{1,1000000}", "huge_repeat_bound"),
    (r"\w+", "unicode_class_wide"),
    (r"\s+", "unicode_class_wide"),
    (r"\b", "unicode_class_wide"),
    (r"a.*b", "dot_not_dotall"),
    (r"(?i)abc", "inline_flag_scope"),
    (r"a++", "py311_only_syntax"),
    (r"(?>a)", "py311_only_syntax"),
    (r"(?i:a)", "py311_only_syntax"),
    (r"", "empty_pattern"),
])
def test_finding_codes(tool, pattern, code):
    result = tool.execute(mode="lint", pattern=pattern)
    codes = [f["code"] for f in result["findings"]]
    assert code in codes, (pattern, code, codes)


def test_unicode_facts_verified_live(tool):
    """The unicode-pitfall findings state CPython facts; verify them
    against the live engine exactly as documented."""
    assert re.match(r"\w", "\u2460") is not None  # \w matches ① U+2460
    assert re.match(r"\w", "\u4e2d") is not None  # ... and CJK
    assert re.match(r"\s", "\u00a0") is not None  # \s matches NBSP
    assert re.match(r".", "\n") is None           # dot lacks newline
    assert re.match(r"\w", "\u2460", re.ASCII) is None

    wide = tool.execute(mode="lint", pattern=r"\w+")
    assert any(f["code"] == "unicode_class_wide" for f in wide["findings"])
    narrow = tool.execute(mode="lint", pattern=r"\w+", flags=["ASCII"])
    assert not any(f["code"] == "unicode_class_wide"
                   for f in narrow["findings"])


def test_dotall_flag_removes_reminder(tool):
    without = tool.execute(mode="lint", pattern=r"a.*b")
    with_flag = tool.execute(mode="lint", pattern=r"a.*b", flags=["DOTALL"])
    assert any(f["code"] == "dot_not_dotall"
               for f in without["findings"])
    assert not any(f["code"] == "dot_not_dotall"
                   for f in with_flag["findings"])


def test_overflow_boundary_matches_cpython(tool):
    """MAXREPEAT itself compiles; one past it raises OverflowError."""
    maxrep = getattr(_sre_parser, "MAXREPEAT", 4294967295)
    at_limit = tool.execute(mode="lint", pattern=f"a{{{maxrep}}}")
    assert at_limit["compiles"] is True
    beyond = tool.execute(mode="lint", pattern=f"a{{{maxrep + 1}}}")
    assert beyond["compiles"] is False
    assert beyond["compile_error"]["type"] == "OverflowError"
    assert _real_outcome(f"a{{{maxrep + 1}}}") is not None


def test_pattern_too_deep_mirrors_recursion_error(tool):
    deep = "(" * 600 + "a" + ")" * 600
    assert _real_outcome(deep) is not None  # engine really raises
    result = tool.execute(mode="lint", pattern=deep)
    assert result["compiles"] is False
    assert result["compile_error"]["type"] == "RecursionError"
    codes = [f["code"] for f in result["findings"]]
    assert "pattern_too_deep" in codes
    # 250-deep nesting compiles fine on CPython and must survive all
    # modes without blowing the interpreter stack.
    moderate = "(" * 250 + "a" + ")" * 250
    assert _real_outcome(moderate) is None
    assert tool.execute(mode="lint", pattern=moderate)["compiles"] is True
    structure = tool.execute(mode="structure", pattern=moderate)
    assert structure["compiles"] is True
    assert len(structure["group_map"]) == 250
    assert tool.execute(mode="explain", pattern=moderate)["groups"]
    estimate = tool.execute(mode="estimate", pattern=moderate,
                            text_length=10)
    assert estimate["backtracking_risk_class"] == "linear"


# --------------------------------------------------------------------- #
# explain / estimate
# --------------------------------------------------------------------- #

def test_explain_alternatives_and_annotations(tool):
    explained = tool.execute(mode="explain", pattern=r"(a|b)|c")
    assert len(explained["alternatives"]) == 2
    assert explained["alternatives"][0].startswith("alternative 1:")
    assert explained["alternatives"][1].startswith("alternative 2:")

    backref = tool.execute(mode="explain", pattern=r"(a)\1")
    kinds = [a["kind"] for a in backref["annotations"]]
    assert "backreference" in kinds
    assert backref["groups"][0]["number"] == 1

    look = tool.execute(mode="explain", pattern=r"a(?=b)(?<=c)")
    kinds = [a["kind"] for a in look["annotations"]]
    assert kinds.count("lookaround") == 2

    empty = tool.execute(mode="explain", pattern="")
    assert empty["alternatives"] == ["alternative 1: match the empty string"]


def test_estimate_values_and_unknown(tool):
    linear = tool.execute(mode="estimate", pattern="abc", text_length=5)
    assert linear["basic_ops"] == 3
    assert linear["backtracking_risk_class"] == "linear"
    star = tool.execute(mode="estimate", pattern=r"a*", text_length=10)
    assert star["basic_ops"] == 10
    # A quantified backreference makes static bounds impossible.
    unknown = tool.execute(mode="estimate", pattern=r"(ab)\1+",
                           text_length=10)
    assert unknown["backtracking_risk_class"] == "unknown"
    assert any("backreference" in r for r in unknown["reasons"])
    # So does a conditional.
    conditional = tool.execute(mode="estimate",
                               pattern=r"(a)?b(?(1)c|d)", text_length=10)
    assert conditional["backtracking_risk_class"] == "unknown"
    # Nested quantifiers still outrank the unknown grade.
    evil = tool.execute(mode="estimate", pattern=r"(a+)+$",
                        text_length=100)
    assert evil["backtracking_risk_class"] == "exponential"
    poly = tool.execute(mode="estimate", pattern=r"(.*a).*b",
                        text_length=100)
    assert poly["backtracking_risk_class"] == "polynomial"
    zero = tool.execute(mode="estimate", pattern=r"a*", text_length=0)
    assert zero["basic_ops"] == 1


# --------------------------------------------------------------------- #
# Validation, caps, determinism
# --------------------------------------------------------------------- #

def test_validation_errors(tool):
    with pytest.raises(ValueError):
        tool.execute(mode="bogus", pattern="a")
    with pytest.raises(ValueError):
        tool.execute(mode="lint", pattern=5)
    with pytest.raises(ValueError):
        tool.execute(mode="lint", pattern=None)
    with pytest.raises(ValueError):
        tool.execute(mode="lint", pattern="a", flags="BOGUS")
    with pytest.raises(ValueError):
        tool.execute(mode="lint", pattern="a", flags=["A", "U"])
    with pytest.raises(ValueError):
        tool.execute(mode="lint", pattern="a", flags=7)
    with pytest.raises(ValueError):
        tool.execute(mode="structure", pattern="a", flags="I")
    with pytest.raises(ValueError):
        tool.execute(mode="explain", pattern="a", text_length=3)
    with pytest.raises(ValueError):
        tool.execute(mode="lint", pattern="a", text_length=3)
    with pytest.raises(ValueError):
        tool.execute(mode="estimate", pattern="a", text_length=-1)
    with pytest.raises(ValueError):
        tool.execute(mode="estimate", pattern="a", text_length=10**9 + 1)
    with pytest.raises(ValueError):
        tool.execute(mode="estimate", pattern="a", text_length=True)
    with pytest.raises(ValueError):
        tool.execute(mode="lint", pattern="a" * 4001)


def test_flags_accepted_and_deduplicated(tool):
    result = tool.execute(mode="lint", pattern="a b # c",
                          flags=["VERBOSE", "x", "IGNORECASE", "i"])
    assert result["compiles"] is True
    assert result["flags"] == ["VERBOSE", "IGNORECASE"]


def test_determinism(tool):
    pattern = r"(a+)+b|(\d*)*|(?<=x)\w+"
    for mode, kwargs in (("lint", {"flags": ["MULTILINE"]}),
                         ("structure", {}), ("explain", {}),
                         ("estimate", {"text_length": 50})):
        first = tool.execute(mode=mode, pattern=pattern, **kwargs)
        second = tool.execute(mode=mode, pattern=pattern, **kwargs)
        assert first == second, mode


def test_lint_summary_and_order(tool):
    result = tool.execute(mode="lint", pattern=r"(a+)+$")
    summary = result["summary"]
    assert summary["error"] == 0
    assert summary["warning"] >= 1
    spans = [f["span"][0] for f in result["findings"]]
    assert spans == sorted(spans)
    assert result["truncated"] is False
