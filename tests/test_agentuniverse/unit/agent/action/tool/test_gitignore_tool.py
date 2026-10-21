#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_gitignore_tool.py

r"""Unit tests for GitignoreTool.

The tool implements git ignore-rule semantics on the pure Python
standard library only (a faithful translation of git's
wildmatch.c / dir.c pipeline), so this suite runs fully offline —
EXCEPT the oracle test, which invokes the REAL git binary
(``git -c core.ignoreCase=false check-ignore -v --no-index``) as
the normative reference:

* Real-git oracle — exactly 400 seeded (ruleset, path) pairs (a
  hand-curated trap corpus plus a random.Random(20261021)
  generated corpus) are materialized in a throwaway repository
  under /tmp/git-oracle-*/ (files and directories created on disk
  so git's dtype resolution is deterministic), and the tool's
  match verdicts (matched / decisive rule line / negated /
  effective) must equal git's verbose output on every pair. The
  corpus deliberately includes the classic semantic traps:
  negation-after-dir-rule (``doc/`` + ``!doc/readme.md`` — the
  negation is dead because git never descends into ignored
  directories), ``**/x``, ``x/**``, ``a/**/b`` (zero directories),
  non-special ``**`` acting as ``*``, trailing-space rules,
  escaped trailing ``\ ``, ``[!a]`` / ``[^a]`` classes, POSIX
  ``[[:alpha:]]`` classes, unterminated and reversed-range
  classes, case sensitivity, CRLF, the UTF-8 BOM, and a missing
  final newline.
* Hand-embedded gitignore(5) ground truths — every documented
  behavior asserted directly (anchoring, dir-only rules, basename
  matching at any depth, ``*``/``?`` never crossing ``/``, the
  three special ``**`` positions, escaping, comments, trailing
  spaces).

The analyze vectors cover the honest last-match-wins reachability
analysis (dead negations via duplicate / covering / ignored-
directory proofs, contradictions, duplicates), trailing-space
traps, the missing-final-newline effect, any-depth patterns and
escaping errors. The lint vectors walk every finding code; the
explain vectors pin the segment structure and VERIFY the example
matches/misses by feeding each single example back through the
match mode. Parameter-level mistakes are ``ValueError``.
"""

import os
import random
import shutil
import subprocess
import tempfile
import unittest

from agentuniverse.agent.action.tool.common_tool import GitignoreTool
from agentuniverse.agent.action.tool.common_tool.gitignore_tool import (
    _parse_rules,
    _rule_matches,
    _trim_trailing_spaces,
    GitignoreTool as DirectGitignoreTool,
)

TOOL = GitignoreTool()


def match(rules, path, is_dir=None):
    if is_dir is None:
        return TOOL.execute(mode="match", rules=rules, path=path)
    return TOOL.execute(mode="match", rules=rules, path=path, is_dir=is_dir)


def analyze(rules):
    return TOOL.execute(mode="analyze", rules=rules)


def lint(rules):
    return TOOL.execute(mode="lint", rules=rules)


def explain(rule):
    return TOOL.execute(mode="explain", rule=rule)


def codes(result):
    return [f["code"] for f in result["findings"]]


def dead_indexes(result):
    return [d["index"] for d in result["dead_rules"]]


# ------------------------------------------------------------------ #
# match mode — hand-embedded gitignore(5) ground truths
# ------------------------------------------------------------------ #


class MatchGroundTruthTest(unittest.TestCase):
    def test_trailing_spaces_ignored_unless_escaped(self):
        # git drops unescaped trailing spaces before matching.
        res = match("foo \n", "foo")
        self.assertTrue(res["matched"])
        self.assertEqual(res["rule_text"], "foo")
        res = match("foo \n", "foo ")
        self.assertFalse(res["matched"])
        # An escaped space matches a literal trailing-space name,
        # and the escape also survives in rule_text.
        res = match("bar\\ \n", "bar ")
        self.assertTrue(res["matched"])
        self.assertEqual(res["rule_text"], "bar\\ ")
        res = match("bar\\ \n", "bar")
        self.assertFalse(res["matched"])

    def test_negation_after_dir_rule_is_dead(self):
        # The classic trap: git never descends into an ignored
        # directory, so !doc/readme.md can never re-include.
        rules = "doc/\n!doc/readme.md\n"
        res = match(rules, "doc/readme.md")
        self.assertTrue(res["matched"])
        self.assertEqual(res["rule_line"], 1)
        self.assertFalse(res["negated"])
        self.assertTrue(res["effective"])
        self.assertEqual(res["matched_on"], "directory")
        self.assertEqual(res["matched_directory"], "doc")
        # ... but re-including the directory itself works.
        rules2 = "logs/**\n!logs/keep/\nlogs/keep/x\n"
        res2 = match(rules2, "logs/keep", is_dir=True)
        self.assertEqual(res2["rule_line"], 2)
        self.assertTrue(res2["negated"])
        self.assertFalse(res2["effective"])
        res3 = match(rules2, "logs/keep/x")
        self.assertEqual(res3["rule_line"], 3)
        self.assertTrue(res3["effective"])

    def test_last_matching_rule_wins(self):
        # gitignore(5): the last matching pattern decides.
        res = match("!important.log\n*.log\n", "important.log")
        self.assertEqual((res["rule_line"], res["effective"]), (2, True))
        res = match("*.log\n!keep.log\n", "keep.log")
        self.assertEqual((res["rule_line"], res["negated"], res["effective"]),
                         (2, True, False))

    def test_anchoring(self):
        # A leading '/' (or any interior '/') anchors to the
        # .gitignore's directory; slash-free rules match basenames
        # at any depth.
        self.assertFalse(match("/foo\n", "d/foo")["matched"])
        self.assertTrue(match("/foo\n", "foo")["matched"])
        self.assertFalse(match("foo/bar\n", "y/foo/bar", is_dir=True)["matched"])
        self.assertTrue(match("foo/bar\n", "foo/bar", is_dir=True)["matched"])
        # ancestor-dir walk still catches files below an anchored
        # dir rule
        self.assertTrue(match("foo/bar\n", "foo/bar/f")["matched"])
        self.assertTrue(match("*.log\n", "a/b/c.log")["matched"])

    def test_dir_only_rules(self):
        self.assertFalse(match("build/\n", "build")["matched"])
        self.assertTrue(match("build/\n", "build", is_dir=True)["matched"])
        self.assertTrue(match("build/\n", "build/")["matched"])  # slash asserts
        # a dir-only rule never matches a file at its own level;
        # below an excluded directory everything is ignored.
        self.assertTrue(match("doc/\n", "doc/file.txt")["matched"])
        self.assertEqual(match("doc/\n", "doc/file.txt")["matched_on"],
                         "directory")

    def test_wildcards_never_cross_slash(self):
        self.assertTrue(match("f?o\n", "foo")["matched"])
        self.assertFalse(match("f?o\n", "f/o")["matched"])
        self.assertTrue(match("a/*.log\n", "a/x.log")["matched"])
        self.assertFalse(match("a/*.log\n", "a/b/x.log")["matched"])

    def test_doublestar_positions(self):
        self.assertTrue(match("**/x\n", "x")["matched"])
        self.assertTrue(match("**/x\n", "a/b/x")["matched"])
        self.assertFalse(match("x/**\n", "x", is_dir=True)["matched"])
        self.assertTrue(match("x/**\n", "x/y/f")["matched"])
        # '/**/' matches zero or more directories.
        self.assertTrue(match("a/**/b\n", "a/b", is_dir=True)["matched"])
        self.assertTrue(match("a/**/b\n", "a/c/b", is_dir=True)["matched"])
        # Non-special '**' behaves as a single '*' (verified with
        # real git): matches within a segment, never crosses '/'.
        self.assertTrue(match("**foo\n", "xfoo")["matched"])
        self.assertFalse(match("mid/**foo\n", "mid/a/foo")["matched"])
        self.assertTrue(match("mid/**foo\n", "mid/axfoo")["matched"])
        self.assertTrue(match("a**b\n", "axxb")["matched"])

    def test_character_classes(self):
        self.assertTrue(match("[a-c]x\n", "bx")["matched"])
        self.assertFalse(match("[a-c]x\n", "dx")["matched"])
        self.assertFalse(match("[a-c]x\n", "Ax")["matched"])  # case-sensitive
        self.assertTrue(match("[!a]x\n", "bx")["matched"])
        self.assertFalse(match("[!a]x\n", "ax")["matched"])
        self.assertTrue(match("[^a]x\n", "bx")["matched"])  # ^ negates too
        self.assertTrue(match("[a/]x\n", "ax")["matched"])
        # classes never match '/' under WM_PATHNAME
        self.assertFalse(match("[a/]x\n", "a/x")["matched"])
        # POSIX classes work, ASCII-only
        self.assertTrue(match("[[:alpha:]]x\n", "zx")["matched"])
        self.assertFalse(match("[[:alpha:]]x\n", "9x")["matched"])
        # unterminated and reversed classes are dead patterns
        self.assertFalse(match("[abc\n", "abc")["matched"])
        self.assertFalse(match("[z-a]x\n", "mx")["matched"])

    def test_escapes_comments_and_negation(self):
        self.assertTrue(match("\\#hash\n", "#hash")["matched"])
        self.assertTrue(match("\\!bang\n", "!bang")["matched"])
        self.assertFalse(match("# comment\n", "comment")["matched"])
        # \!x is a literal (line 1); !\!x negates the literal (line 2)
        # — the later rule is the last match, so it wins.
        res = match("\\!x\n!\\!x\n", "!x")
        self.assertEqual(res["rule_line"], 2)
        self.assertTrue(res["negated"])
        self.assertFalse(res["effective"])

    def test_line_handling_crlf_bom_missing_newline(self):
        # CRLF endings are handled (the \r before \n is dropped).
        self.assertTrue(match("a.log\r\nb.log\n", "a.log")["matched"])
        self.assertTrue(match("a.log\r\nb.log\n", "b.log")["matched"])
        # A UTF-8 BOM is skipped.
        self.assertTrue(match("\ufeffw\n", "w")["matched"])
        # The final line without a newline is still honored.
        self.assertTrue(match("q1\nq2", "q2")["matched"])

    def test_case_sensitivity_documented(self):
        self.assertFalse(match("Foo\n", "foo")["matched"])
        self.assertFalse(match("foo\n", "Foo")["matched"])

    def test_empty_and_blank_lines(self):
        self.assertFalse(match("\n   \n# c\n", "x")["matched"])
        # spaces-only lines become empty rules that match nothing
        res = match("   \nx\n", "x")
        self.assertEqual(res["rule_count"], 2)
        self.assertEqual(res["rule_line"], 2)


# ------------------------------------------------------------------ #
# match mode — result envelope
# ------------------------------------------------------------------ #


class MatchEnvelopeTest(unittest.TestCase):
    def test_no_match_envelope(self):
        res = match("a\nb\n", "c")
        self.assertFalse(res["matched"])
        self.assertIsNone(res["rule_index"])
        self.assertIsNone(res["rule_line"])
        self.assertIsNone(res["rule_text"])
        self.assertFalse(res["negated"])
        self.assertFalse(res["effective"])
        self.assertIsNone(res["matched_on"])
        self.assertEqual(res["matching_rules"], [])
        self.assertIn("not ignored", res["explanation"])

    def test_matching_rules_list_and_overridden(self):
        rules = "*.log\n!keep.log\n*.log\n"
        res = match(rules, "keep.log")
        self.assertEqual([m["index"] for m in res["matching_rules"]], [0, 1, 2])
        self.assertIn("overridden earlier rules", res["explanation"])
        self.assertIn("line 1", res["explanation"])

    def test_directory_walk_explanation_names_dead_negations(self):
        rules = "doc/\n!doc/readme.md\n"
        res = match(rules, "doc/readme.md")
        self.assertIn("never descends", res["explanation"])
        self.assertIn("line 2", res["explanation"])

    def test_is_dir_flag_and_trailing_slash(self):
        rules = "build/\n"
        self.assertTrue(match(rules, "build", is_dir=True)["matched"])
        self.assertTrue(match(rules, "build/")["matched"])
        self.assertFalse(match(rules, "build", is_dir=False)["matched"])


# ------------------------------------------------------------------ #
# analyze mode
# ------------------------------------------------------------------ #


class AnalyzeTest(unittest.TestCase):
    def test_dead_rule_via_duplicate(self):
        res = analyze("a.log\nb/\na.log\n")
        self.assertIn(0, dead_indexes(res))
        dead = res["dead_rules"][0]
        self.assertEqual(dead["blocked_by"]["index"], 2)

    def test_dead_negation_via_covering_later_rule(self):
        # *.log after !keep.log provably covers every path the
        # negation matches -> the negation can never be last.
        res = analyze("*.log\n!keep.log\n*.log\n")
        self.assertIn(1, dead_indexes(res))
        dead = [d for d in res["dead_rules"] if d["index"] == 1][0]
        self.assertEqual(dead["blocked_by"]["index"], 2)
        # plain later rule killed by suffix-cover: !x then *
        res2 = analyze("z\n!z\n*\n")
        self.assertIn(1, dead_indexes(res2))

    def test_dead_negation_inside_ignored_directory(self):
        res = analyze("doc/\n!doc/readme.md\n")
        self.assertEqual(dead_indexes(res), [1])
        dead = res["dead_rules"][0]
        self.assertEqual(dead["blocked_by"]["index"], 0)
        self.assertIn("ignored directory 'doc'", dead["reason"])
        # re-including the directory first keeps deeper rules alive
        res2 = analyze("logs/**\n!logs/keep/\nlogs/keep/x\n")
        self.assertEqual(dead_indexes(res2), [])

    def test_negation_matching_only_the_dir_itself_is_alive(self):
        res = analyze("logs/**\n!logs/keep/\n")
        self.assertEqual(dead_indexes(res), [])

    def test_contradictions(self):
        res = analyze("*.log\n!*.log\n")
        self.assertEqual(len(res["contradictions"]), 1)
        pair = res["contradictions"][0]
        self.assertEqual(pair["negated"]["index"], 1)
        self.assertEqual(pair["plain"]["index"], 0)
        self.assertIn("last-match-wins", pair["winner"])

    def test_duplicates(self):
        res = analyze("x\ny\nx\nx\n")
        self.assertEqual(len(res["duplicates"]), 1)
        self.assertEqual(res["duplicates"][0]["indexes"], [0, 2, 3])
        self.assertEqual(res["rule_count"], 4)

    def test_trailing_space_traps(self):
        res = analyze("foo \nbar\n")
        self.assertEqual(len(res["trailing_space_traps"]), 1)
        trap = res["trailing_space_traps"][0]
        self.assertEqual(trap["line"], 1)
        self.assertEqual(trap["effective_rule"], "foo")

    def test_missing_final_newline(self):
        res = analyze("a\nb")
        self.assertTrue(res["missing_final_newline"]["present"])
        self.assertIn("virtual newline", res["missing_final_newline"]["effect"])
        self.assertFalse(analyze("a\nb\n")["missing_final_newline"]["present"])

    def test_any_depth_patterns_info_only(self):
        res = analyze("node_modules\n/build\n*.log\n")
        indexes = [p["index"] for p in res["any_depth_patterns"]]
        self.assertIn(0, indexes)   # slash-free literal: any depth
        self.assertNotIn(1, indexes)  # anchored by leading /
        self.assertNotIn(2, indexes)  # wildcard breadth is intended

    def test_escaping_errors(self):
        res = analyze("foo\\\nbar\\ \nbuild\\temp\n")
        problems = {(e["line"], e["rule"]) for e in res["escaping_errors"]}
        self.assertIn((1, "foo\\"), problems)   # dangling backslash
        self.assertIn((2, "bar\\ "), problems)  # escaped trailing space
        self.assertIn((3, "build\\temp"), problems)  # ordinary-char escape

    def test_empty_rules_text(self):
        res = analyze("")
        self.assertEqual(res["rule_count"], 0)
        self.assertEqual(res["dead_rules"], [])


# ------------------------------------------------------------------ #
# lint mode
# ------------------------------------------------------------------ #


class LintTest(unittest.TestCase):
    def test_clean_rules_have_no_findings(self):
        res = lint("*.log\n/build/\n!build/keep.txt\n**/tmp\n")
        self.assertEqual(res["findings"], [])
        self.assertEqual(res["summary"], {"total": 0, "error": 0,
                                          "warning": 0, "info": 0})

    def test_invalid_glob_unterminated_class(self):
        res = lint("[abc\nx[def\n")
        self.assertEqual(codes(res).count("invalid_glob"), 2)
        self.assertEqual(res["summary"]["error"], 2)

    def test_invalid_glob_malformed_posix_class(self):
        res = lint("[[:alpha:]]x\n[[:foo:]]x\n")
        self.assertEqual(codes(res), ["invalid_glob"])

    def test_never_matches_cases(self):
        res = lint("a\\\n")
        self.assertEqual(codes(res), ["never_matches"])
        res = lint("a//b\n")
        self.assertEqual(codes(res), ["never_matches"])
        res = lint("!\n")
        self.assertEqual(codes(res), ["never_matches"])

    def test_reversed_range(self):
        res = lint("[z-a]x\n")
        self.assertEqual(codes(res), ["reversed_range"])
        self.assertEqual(res["summary"]["warning"], 1)

    def test_redundant_doublestar(self):
        res = lint("a**b\n**foo\nfoo**\n**/x\nx/**\na/**/b\n")
        self.assertEqual(codes(res).count("redundant_doublestar"), 3)
        # the three special positions produce no redundant finding
        specials = lint("**/x\nx/**\na/**/b\n")
        self.assertNotIn("redundant_doublestar", codes(specials))

    def test_doublestar_midsegment_note(self):
        res = lint("a/**/b\n")
        self.assertEqual(codes(res), ["doublestar_midsegment"])
        self.assertEqual(res["findings"][0]["severity"], "info")

    def test_windows_separator(self):
        res = lint("build\\temp\n")
        self.assertEqual(codes(res), ["windows_separator"])

    def test_duplicate_rule_and_negation(self):
        res = lint("x\nx\n!y\n!y\n")
        self.assertEqual(codes(res).count("duplicate_rule"), 1)
        self.assertEqual(codes(res).count("duplicate_negation"), 1)

    def test_line_numbers_and_ordering(self):
        res = lint("[abc\na//b\n[z-a]x\n")
        lines = [(f["line"], f["code"]) for f in res["findings"]]
        self.assertEqual(lines, [(1, "invalid_glob"),
                                 (2, "never_matches"),
                                 (3, "reversed_range")])
        self.assertEqual(res["summary"]["total"], 3)

    def test_severity_counts(self):
        res = lint("[abc\na**b\na/**/b\n")
        self.assertEqual(res["summary"],
                         {"total": 3, "error": 1, "warning": 1, "info": 1})


# ------------------------------------------------------------------ #
# explain mode
# ------------------------------------------------------------------ #


class ExplainTest(unittest.TestCase):
    def test_simple_negated_rule(self):
        res = explain("!keep.log")
        self.assertTrue(res["negated"])
        self.assertFalse(res["anchored"])
        self.assertFalse(res["dir_only"])
        kinds = [(s["kind"], s["text"]) for s in res["segments"]]
        self.assertEqual(kinds, [("negation", "!"), ("literal", "keep.log")])
        res_wild = explain("!keep*.log")
        self.assertIn(("wildcard", "*"),
                      [(s["kind"], s["text"]) for s in res_wild["segments"]])

    def test_anchoring_and_dir_only(self):
        res = explain("/build/")
        self.assertTrue(res["anchored"])
        self.assertTrue(res["dir_only"])
        res2 = explain("build")
        self.assertFalse(res2["anchored"])
        self.assertFalse(res2["dir_only"])
        res3 = explain("a/b")
        self.assertTrue(res3["anchored"])

    def test_doublestar_segment_kinds(self):
        res = explain("**/x/**")
        kinds = [s["kind"] for s in res["segments"]]
        self.assertEqual(kinds.count("doublestar"), 2)
        # non-special ** is a plain wildcard
        res2 = explain("a**b")
        kinds2 = [s["kind"] for s in res2["segments"]]
        self.assertNotIn("doublestar", kinds2)

    def test_class_segment(self):
        res = explain("[a-c]?x")
        class_seg = [s for s in res["segments"] if s["kind"] == "class"][0]
        self.assertIn("a", class_seg["matches"])
        self.assertIn("c", class_seg["matches"])

    def test_examples_are_verifiable(self):
        # Anchored exact literals have a single-element match set;
        # every other rule shape yields three distinct examples.
        expected_counts = {"/build/": 1, "doc/readme.md": 1}
        for rule in ["**/x", "x/**", "a/**/b", "/build/", "!keep.log",
                     "[a-c]*.log", "doc/readme.md", "f?o", "[!a]y",
                     "**foo", "[[:alpha:]]x"]:
            res = explain(rule)
            want = expected_counts.get(rule, 3)
            self.assertEqual(len(res["example_matches"]), want, rule)
            self.assertEqual(len(res["example_misses"]), 2, rule)
            rule_obj = _parse_rules(rule + "\n")[0]
            for m in res["example_matches"]:
                is_dir = m.endswith("/")
                body = m[:-1] if is_dir else m
                self.assertTrue(_rule_matches(rule_obj, body, is_dir),
                                f"{rule}: example {m!r} must match")
            for m in res["example_misses"]:
                is_dir = m.endswith("/")
                body = m[:-1] if is_dir else m
                self.assertFalse(_rule_matches(rule_obj, body, is_dir),
                                 f"{rule}: miss {m!r} must not match")

    def test_notes(self):
        self.assertIn("ANY depth", explain("foo")["notes"][0])
        self.assertIn("anchors", explain("/foo")["notes"][0])
        self.assertIn("directories", explain("foo/")["notes"][-1])


# ------------------------------------------------------------------ #
# Parameter validation
# ------------------------------------------------------------------ #


class ValidationTest(unittest.TestCase):
    def test_bad_mode(self):
        with self.assertRaises(ValueError):
            TOOL.execute(mode="nope", rules="x\n")

    def test_rules_must_be_string(self):
        for bad in (None, 42, ["a"], b"a\n"):
            with self.assertRaises(ValueError):
                TOOL.execute(mode="analyze", rules=bad)

    def test_rules_caps(self):
        with self.assertRaises(ValueError):
            TOOL.execute(mode="analyze", rules="x" * 65_537 + "\n")
        with self.assertRaises(ValueError):
            TOOL.execute(mode="analyze", rules="a\n" * 4_097)
        # exactly at the caps is accepted
        TOOL.execute(mode="analyze", rules="a\n" * 4_096)
        with self.assertRaises(ValueError):
            TOOL.execute(mode="analyze", rules="a\x00b\n")

    def test_path_validation(self):
        good = "a\n"
        for bad in (None, "", "/abs/path", "a//b", "a/./b", "a/../b",
                    "a\\b", "a\x00b"):
            with self.assertRaises(ValueError):
                TOOL.execute(mode="match", rules=good, path=bad)
        with self.assertRaises(ValueError):
            TOOL.execute(mode="match", rules=good, path="a" * 4_097)
        with self.assertRaises(ValueError):
            TOOL.execute(mode="match", rules=good, path="/".join(["a"] * 65))

    def test_is_dir_type(self):
        with self.assertRaises(ValueError):
            TOOL.execute(mode="match", rules="a\n", path="a", is_dir="yes")

    def test_rule_validation(self):
        for bad in (None, "", "# comment", "a\nb", "a\n", "x" * 1_025):
            with self.assertRaises(ValueError):
                TOOL.execute(mode="explain", rule=bad)

    def test_mode_specific_required_args(self):
        with self.assertRaises(ValueError):
            TOOL.execute(mode="match", rules="a\n")  # no path
        with self.assertRaises(ValueError):
            TOOL.execute(mode="match", path="a")     # no rules
        with self.assertRaises(ValueError):
            TOOL.execute(mode="analyze")             # no rules
        with self.assertRaises(ValueError):
            TOOL.execute(mode="explain")             # no rule


# ------------------------------------------------------------------ #
# Determinism
# ------------------------------------------------------------------ #


class DeterminismTest(unittest.TestCase):
    def test_identical_calls_identical_results(self):
        rules = "*.log\n!keep.log\nlogs/**\n!logs/keep/\n[abc\nx  \n"
        for mode_call in (
            lambda: TOOL.execute(mode="analyze", rules=rules),
            lambda: TOOL.execute(mode="lint", rules=rules),
            lambda: TOOL.execute(mode="match", rules=rules, path="logs/keep/x"),
        ):
            self.assertEqual(mode_call(), mode_call())

    def test_trim_trailing_spaces_pure(self):
        self.assertEqual(_trim_trailing_spaces("foo  "), "foo")
        self.assertEqual(_trim_trailing_spaces("foo\\ "), "foo\\ ")
        self.assertEqual(_trim_trailing_spaces("foo\\ "), "foo\\ ")
        self.assertEqual(_trim_trailing_spaces(" a b "), " a b")
        self.assertEqual(_trim_trailing_spaces("x\\"), "x\\")


# ------------------------------------------------------------------ #
# Real-git oracle — 400 seeded (ruleset, path) pairs
# ------------------------------------------------------------------ #

GIT_BIN = shutil.which("git")

# Curated trap corpus: (rules_text, [(query_path, is_dir), ...]).
# Files/dirs are created on disk with the declared dtype; the
# query is passed to git verbatim (a trailing '/' is appended for
# dir assertions on paths that do not exist).
_CURATED = [
    ("doc/\n!doc/readme.md\n", [
        ("doc/readme.md", False), ("doc/other.txt", False),
        ("doc", True), ("other.md", False),
    ]),
    ("*.log\n!keep.log\n", [
        ("keep.log", False), ("x.log", False), ("a/b/y.log", False),
        ("keep", False),
    ]),
    ("!important.log\n*.log\n", [
        ("important.log", False), ("debug.log", False),
    ]),
    ("**/x\n", [
        ("x", False), ("a/x", False), ("a/b/x", False), ("ax", False),
    ]),
    ("x/**\n", [
        ("x", True), ("x/f", False), ("x/y/g", False), ("other", False),
    ]),
    ("a/**/b\n", [
        ("a/b", True), ("a/c/b", True), ("a/bb", False), ("a/bb/cc", False),
    ]),
    ("/foo\n", [("foo", False), ("d/foo", False), ("foo/bar", False)]),
    ("foo/bar\n", [
        ("foo/bar", True), ("y/foo/bar", True), ("foo/bar/f", False),
        ("y/foo/bar/f", False),
    ]),
    ("Foo\n", [("Foo", False), ("foo", False), ("a/Foo", False)]),
    ("foo \nbar\\ \n", [
        ("foo", False), ("foo ", False), ("bar", False), ("bar ", False),
    ]),
    ("build/\n", [
        ("build", False),              # file: dir-only rule must not match
        ("build/x", False),            # walk treats 'build' as a directory
    ]),
    ("[a-c]x\n[!d]y\n", [
        ("ax", False), ("cx", False), ("dx", False), ("ay", False),
        ("dy", False),
    ]),
    ("[abc\n", [("[abc", False), ("abc", False), ("a", False)]),
    ("[z-a]x\n", [("ax", False), ("mx", False)]),
    ("# c\n\\#hash\n\\!bang\n", [
        ("#hash", False), ("!bang", False), ("c", False),
    ]),
    ("a.log\r\nb.log\n", [("a.log", False), ("b.log", False)]),
    ("\ufeffw\n", [("w", False), ("v", False)]),
    ("q1\nq2", [("q1", False), ("q2", False)]),
    ("**foo\n", [("foo", False), ("xfoo", False), ("a/xfoo", False)]),
    ("logs/**\n!logs/keep/\nlogs/keep/x\n", [
        ("logs/z", False), ("logs/keep", True), ("logs/keep/x", False),
        ("logs", True),
    ]),
    ("f?o\na/*.log\n", [
        ("foo", False), ("f/o", False), ("a/x.log", False),
        ("a/b/x.log", False),
    ]),
    ("[a/]x\n", [("ax", False), ("a/x", False)]),
    ("[[:alpha:]]x\n", [("zx", False), ("9x", False)]),
    ("src/**\n!src/**/*.keep\n", [
        ("src/a.txt", False), ("src/d/b.keep", False), ("src", True),
    ]),
    ("sub/build/\n", [
        ("sub/build", True), ("sub/build/x", False), ("sub/y", False),
    ]),
]

_NAMES = ["foo", "bar", "baz", "qux", "log", "tmp", "src", "doc",
          "build", "x", "y", "z", "data", "keep"]
_CHARS = "abcxyz"

def _random_rulesets(rng, count):
    """Deterministic random rulesets from a pattern-template pool."""
    templates = [
        "{n}", "{n}/", "/{n}", "*.{n}", "{n}/*.tmp", "**/{n}", "{n}/**",
        "a/**/{n}", "!{n}", "!*.{n}", "{n}?x", "[{c1}{c2}]x", "[!{c1}]y",
        "{n1}/{n2}/", "**", "?{n}", "{n}[0-9]", "!{n1}/{n2}",
        "**/{n1}/{n2}", "{n1}/**/{n2}",
    ]
    rulesets = []
    for _ in range(count):
        n_rules = rng.randint(3, 8)
        lines = []
        for _ in range(n_rules):
            t = rng.choice(templates)
            lines.append(t.format(
                n=rng.choice(_NAMES), n1=rng.choice(_NAMES),
                n2=rng.choice(_NAMES), c1=rng.choice(_CHARS),
                c2=rng.choice(_CHARS),
            ))
        rules_text = "\n".join(lines) + "\n"
        paths = []
        for _ in range(9):
            depth = rng.randint(1, 4)
            comps = [rng.choice(_NAMES) for _ in range(depth)]
            last = rng.random() < 0.5
            if last:
                comps[-1] = comps[-1] + rng.choice(["", ".log", ".tmp", "x"])
            paths.append(("/".join(comps), rng.random() < 0.25))
        rulesets.append((rules_text, paths))
    return rulesets


def _materialize(rulesets, root):
    """Create one repo per ruleset; return [(repo, rules_text,
    query, is_dir), ...] pairs.

    Files/dirs are created on disk so git's dtype resolution is
    deterministic. When creation is impossible (a path is also a
    parent file of another path) the path stays missing on disk
    and git resolves DT_UNKNOWN — which behaves like a file for
    dir-only rules — so the pair's is_dir is lowered to False.
    """
    pairs = []
    for idx, (rules_text, paths) in enumerate(rulesets):
        repo = os.path.join(root, f"repo{idx:03d}")
        os.makedirs(repo)
        subprocess.run(["git", "init", "-q", repo], check=True,
                       capture_output=True)
        with open(os.path.join(repo, ".gitignore"), "wb") as fh:
            fh.write(rules_text.encode("utf-8"))
        dtypes = {}
        for path, is_dir in paths:
            dtypes.setdefault(path, False)
            dtypes[path] = dtypes[path] or is_dir
        created = {}
        for path, is_dir in sorted(dtypes.items()):
            full = os.path.join(repo, path)
            try:
                os.makedirs(os.path.dirname(full), exist_ok=True)
                if is_dir:
                    os.makedirs(full, exist_ok=True)
                else:
                    if not os.path.exists(full):
                        open(full, "wb").close()
                created[path] = is_dir
            except OSError:
                created[path] = False  # missing on disk: DT_UNKNOWN
        for path, is_dir in paths:
            pairs.append((repo, rules_text, path, created[path]))
    return pairs


def _git_verdicts(repo, queries):
    """Run git check-ignore -v --no-index once; return
    {path: (line, negated)} for the matched paths."""
    args = [GIT_BIN, "-C", repo, "-c", "core.ignoreCase=false",
            "check-ignore", "-v", "--no-index", "--"] + queries
    proc = subprocess.run(args, capture_output=True, text=True)
    verdicts = {}
    for line in proc.stdout.splitlines():
        if "\t" not in line:
            continue
        head, path = line.split("\t", 1)
        parts = head.split(":", 2)
        if len(parts) != 3:
            continue
        lineno = int(parts[1])
        pattern = parts[2]
        verdicts[path] = (lineno, pattern.startswith("!"))
    return verdicts


@unittest.skipIf(GIT_BIN is None, "git binary not available")
class RealGitOracleTest(unittest.TestCase):
    """400 seeded (ruleset, path) pairs against the real git binary."""

    TOTAL = 400

    @classmethod
    def setUpClass(cls):
        rng = random.Random(20261021)
        random_count = 37
        rulesets = list(_CURATED) + _random_rulesets(rng, random_count)
        try:
            cls.root = tempfile.mkdtemp(prefix="git-oracle-", dir="/tmp")
        except OSError:
            cls.root = tempfile.mkdtemp(prefix="git-oracle-")
        pairs = _materialize(rulesets, cls.root)
        # Deterministically land on exactly TOTAL pairs.
        if len(pairs) >= cls.TOTAL:
            pairs = pairs[: cls.TOTAL]
        else:
            need = cls.TOTAL - len(pairs)
            extra_repo = os.path.join(cls.root, "extra")
            os.makedirs(extra_repo)
            subprocess.run(["git", "init", "-q", extra_repo], check=True,
                           capture_output=True)
            extra_rules = "**/keep\n!*.log\nz/**\n"
            with open(os.path.join(extra_repo, ".gitignore"), "wb") as fh:
                fh.write(extra_rules.encode("utf-8"))
            extra_paths = []
            for i in range(need):
                p = f"p{i % 13}/f{i}.log" if i % 2 else f"z/p{i}"
                is_dir = i % 5 == 0
                full = os.path.join(extra_repo, p)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                if is_dir:
                    os.makedirs(full, exist_ok=True)
                else:
                    if not os.path.exists(full):
                        open(full, "wb").close()
                extra_paths.append((extra_repo, extra_rules, p, is_dir))
            pairs.extend(extra_paths)
        assert len(pairs) == cls.TOTAL, len(pairs)
        cls.pairs = pairs

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_parity_with_real_git(self):
        # Batch the git queries per repository for speed.
        by_repo = {}
        for repo, rules_text, path, is_dir in self.pairs:
            by_repo.setdefault(repo, []).append((rules_text, path, is_dir))
        checked = 0
        failures = []
        for repo, entries in sorted(by_repo.items()):
            queries = [e[1] for e in entries]
            verdicts = _git_verdicts(repo, queries)
            for rules_text, path, is_dir in entries:
                git_line, git_negated = verdicts.get(path, (None, False))
                git_matched = path in verdicts
                git_effective = git_matched and not git_negated
                res = TOOL.execute(
                    mode="match", rules=rules_text, path=path, is_dir=is_dir
                )
                got = (res["matched"], res["rule_line"], res["negated"],
                       res["effective"])
                want = (git_matched, git_line, git_negated, git_effective)
                checked += 1
                if got != want:
                    failures.append(
                        f"rules={rules_text!r} path={path!r} is_dir={is_dir}: "
                        f"tool={got} git={want}"
                    )
        self.assertEqual(checked, self.TOTAL)
        self.assertEqual(failures, [], "\n".join(failures[:12]))

    def test_corpus_covers_the_classic_traps(self):
        rules_texts = [rt for rt, _ in _CURATED]
        self.assertIn("doc/\n!doc/readme.md\n", rules_texts)
        self.assertIn("**/x\n", rules_texts)
        self.assertIn("x/**\n", rules_texts)
        self.assertIn("a/**/b\n", rules_texts)
        self.assertIn("foo \nbar\\ \n", rules_texts)
        self.assertIn("*.log\n!keep.log\n", rules_texts)


if __name__ == "__main__":
    unittest.main()
