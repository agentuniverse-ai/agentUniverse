#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_requirements_tool.py

"""Offline unit tests for RequirementsTool.

The tool inspects and diffs requirements.txt text purely on the
standard library and never touches the network, so this suite runs
fully offline. Every assertion is deterministic against
hand-computed ground truths: the ``parse`` vectors cover the PEP 508
matrix (names / extras / verbatim specifiers / environment markers,
``--hash`` options, editable, VCS, direct-URL, wheel and sdist
lines, pip file options, comments and blanks reported distinctly,
and the documented continuation-less handling — a trailing
backslash is an error, lines are never joined), the normalization
collisions (``Foo_Bar`` / ``foo-bar`` / ``foo.bar`` / ``FOO-BAR``
are one package), the ``lint`` vectors trigger every rule plus a
clean control file, the ``diff`` matrix covers added / removed /
changed with the specifier / marker / extras / other flags,
duplicate-name positional pairing and error passthrough, and the
error matrix walks every content-level parse failure. Parameter
level mistakes are ``ValueError`` (wrong types, over-cap inputs).

When the third-party ``packaging`` distribution is importable, a
differential suite additionally round-trips 300 seeded PEP 508
lines through ``packaging.requirements.Requirement``: every seed
packaging accepts must parse to the same normalized name, clause
set, extras set and (whitespace- and quote-normalized) marker, and
every seed packaging rejects must land in our error list — the
grammar is deliberately kept aligned with ``packaging`` 23.x on
everything structural (it is skipped when ``packaging`` is absent,
so the suite stays stdlib-only offline).
"""

import re
import unittest

from agentuniverse.agent.action.tool.common_tool import (
    RequirementsTool,
)
from agentuniverse.agent.action.tool.common_tool.requirements_tool \
    import RequirementsTool as DirectRequirementsTool


def run_parse(requirements):
    return RequirementsTool().execute(
        mode="parse", requirements=requirements
    )


def run_lint(requirements):
    return RequirementsTool().execute(
        mode="lint", requirements=requirements
    )


def run_diff(old, new):
    return RequirementsTool().execute(
        mode="diff", requirements_old=old, requirements_new=new
    )


# ------------------------------------------------------------------ #
# parse mode — the PEP 508 / requirements-file matrix
# ------------------------------------------------------------------ #

class ParseGroundTruths(unittest.TestCase):
    """``parse`` — entries, comments, blanks, options, errors."""

    def test_pep508_full_matrix(self):
        """Names, extras, verbatim specifiers and markers."""
        text = "\n".join(
            [
                "requests",
                "requests>=2.0",
                "requests >= 2.0, < 3.0 ; python_version < '3.10'",
                "zope.interface~=2.0,",
                "Flask-Login[security, socks] == 0.1",
                "requests[ security , socks ] >= 2.0  # inline note",
                "foo[]>=1.0",
                "1.0",
                "foo==1.2.*",
                "foo===whatever!!",
                "foo==1!2.0+local.1 ; extra == 'security'",
            ]
        )
        result = run_parse(text)
        self.assertEqual(result["errors"], [])
        entries = result["entries"]
        self.assertEqual(len(entries), 11)

        bare, simple, ranged, compat, extras, spaced, empty_extras, \
            digit, wildcard, arbitrary, epoch = entries

        self.assertEqual(bare["name"], "requests")
        self.assertIsNone(bare["specifier"])
        self.assertEqual(bare["kind"], "requirement")

        self.assertEqual(simple["specifier"], ">=2.0")

        # Specifier and marker kept VERBATIM (spaces and all).
        self.assertEqual(ranged["specifier"], ">= 2.0, < 3.0")
        self.assertEqual(ranged["markers"], "python_version < '3.10'")
        self.assertIsNone(ranged.get("extras"))

        self.assertEqual(compat["name"], "zope-interface")
        self.assertEqual(compat["specifier"], "~=2.0,")

        self.assertEqual(extras["name"], "flask-login")
        self.assertEqual(extras["extras"], ["security", "socks"])
        self.assertEqual(extras["specifier"], "== 0.1")

        self.assertEqual(spaced["extras"], ["security", "socks"])
        self.assertEqual(spaced["comment"], "inline note")

        # Empty extras bracket matches packaging: an empty list.
        self.assertEqual(empty_extras["extras"], [])

        # Digit-leading names are legal PEP 508 ('1.0' IS a name).
        self.assertEqual(digit["name"], "1-0")
        self.assertIsNone(digit["specifier"])

        self.assertEqual(wildcard["specifier"], "==1.2.*")
        self.assertEqual(arbitrary["specifier"], "===whatever!!")
        self.assertEqual(epoch["markers"], "extra == 'security'")

    def test_editable_vcs_url_and_path_lines(self):
        """Editables, VCS lines, direct URLs and local paths."""
        text = "\n".join(
            [
                "-e .",
                "-e ./lib/pkg",
                "--editable=/abs/path/pkg",
                "-e pkg @ git+https://github.com/x/pkg.git@v1#egg=pkg",
                "-e git+https://github.com/x/pkg.git#egg=pkg",
                "git+https://github.com/x/y.git#egg=y",
                "hg+ssh://hg@host/repo#egg=repo",
                "https://files.example/zipped/zipped-0.1.0-py3-none-any.whl",
                "https://files.example/src/src-1.0.tar.gz",
                "https://files.example/no-hint.tar.gz",
                "./local/pkg",
                "C:\\\\work\\\\pkg",
                "requests @ https://files.example/r/r-2.0.tar.gz",
            ]
        )
        result = run_parse(text)
        self.assertEqual(result["errors"], [])
        entries = result["entries"]
        self.assertEqual(len(entries), 13)
        here, rel, absolute, named_vcs, edit_vcs, git_vcs, hg_vcs, \
            wheel, sdist, unnamed_url, local_pkg, windows, direct = entries

        self.assertTrue(here["editable"])
        self.assertEqual(here["path"], ".")
        self.assertEqual(rel["path"], "./lib/pkg")
        self.assertEqual(absolute["path"], "/abs/path/pkg")

        self.assertEqual(named_vcs["name"], "pkg")
        self.assertEqual(named_vcs["vcs"], "git")
        self.assertTrue(named_vcs["editable"])
        self.assertIn("#egg=pkg", named_vcs["url"])

        self.assertEqual(edit_vcs["name"], "pkg")
        self.assertEqual(edit_vcs["vcs"], "git")

        self.assertEqual(git_vcs["name"], "y")
        self.assertEqual(git_vcs["vcs"], "git")
        self.assertEqual(git_vcs["kind"], "vcs")

        self.assertEqual(hg_vcs["vcs"], "hg")
        self.assertEqual(hg_vcs["name"], "repo")

        # Wheel name inference (PEP 427) and sdist best effort.
        self.assertEqual(wheel["name"], "zipped")
        self.assertEqual(sdist["name"], "src")
        self.assertIsNone(unnamed_url["name"])

        self.assertEqual(local_pkg["kind"], "path")
        self.assertEqual(local_pkg["path"], "./local/pkg")

        self.assertEqual(windows["kind"], "path")

        self.assertEqual(direct["name"], "requests")
        self.assertEqual(direct["url"], "https://files.example/r/r-2.0.tar.gz")

    def test_hash_options(self):
        """--hash extraction: single, repeated, comma-separated."""
        text = "\n".join(
            [
                "numpy==1.26.0 --hash=sha256:0123456789abcdef",
                "requests==2.31.0 --hash=sha256:0123456789abcdef "
                "--hash=sha512:fedcba9876543210",
                "urllib3==2.0.7 --hash=sha256:0123456789abcdef,sha256:ffff",
                "git+https://x/y.git#egg=y --hash=sha256:0123456789abcdef",
            ]
        )
        result = run_parse(text)
        self.assertEqual(result["errors"], [])
        entries = result["entries"]
        self.assertEqual(entries[0]["specifier"], "==1.26.0")
        self.assertEqual(entries[0]["hash"], ["sha256:0123456789abcdef"])
        self.assertEqual(
            entries[1]["hash"],
            ["sha256:0123456789abcdef", "sha512:fedcba9876543210"],
        )
        self.assertEqual(
            entries[2]["hash"],
            ["sha256:0123456789abcdef", "sha256:ffff"],
        )
        self.assertEqual(entries[3]["hash"], ["sha256:0123456789abcdef"])

    def test_comments_and_blanks_reported_distinctly(self):
        """Comment and blank lines never become entries or errors."""
        text = "\n".join(
            [
                "# top comment",
                "   # indented comment",
                "requests==2.0",
                "",
                "   ",
                "\t",
                "numpy==1.0  # trailing comment",
                "https://x/y.whl#egg=y",  # '#' glued: NOT a comment
            ]
        )
        result = run_parse(text)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["counts"]["comments"], 2)
        self.assertEqual(result["counts"]["blank_lines"], 3)
        self.assertEqual(result["counts"]["entries"], 3)
        self.assertEqual(
            [c["text"] for c in result["comments"]],
            ["top comment", "indented comment"],
        )
        self.assertEqual(
            [c["line"] for c in result["comments"]], [1, 2]
        )
        by_line = {e["line"]: e for e in result["entries"]}
        self.assertEqual(by_line[7]["comment"], "trailing comment")
        self.assertEqual(by_line[8]["name"], "y")

    def test_pip_options_captured_not_parsed_as_requirements(self):
        """-r / -i / flags land in options; unknown ones error."""
        text = "\n".join(
            [
                "-r other.txt",
                "--requirement=more.txt",
                "-i https://pypi.example/simple",
                "--extra-index-url https://mir.example/simple",
                "-f ./wheels",
                "--trusted-host mir.example",
                "--no-index",
                "--require-hashes",
                "--prefer-binary",
                "--pre",
                "--no-binary=:all:",
                "--only-binary=:all:",
                "-c constraints.txt",
            ]
        )
        result = run_parse(text)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["counts"]["entries"], 0)
        self.assertEqual(result["counts"]["options"], 13)
        self.assertEqual(result["options"][0]["value"], "other.txt")
        self.assertEqual(result["options"][1]["value"], "more.txt")
        self.assertEqual(
            result["options"][2]["value"], "https://pypi.example/simple"
        )
        self.assertIsNone(result["options"][7]["value"])

    def test_continuation_is_documented_as_unsupported(self):
        """Lines are never joined — a trailing backslash errors."""
        result = run_parse("foo >= 1.0 \\\nbar == 2.0")
        self.assertEqual(result["counts"]["entries"], 1)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["line"], 1)
        self.assertIn("continuation", result["errors"][0]["reason"])

    def test_normalization_collisions(self):
        """foo_bar / foo-bar / foo.bar / FOO-BAR are one package."""
        text = "\n".join(
            ["foo_bar==1", "foo-bar==2", "foo.bar==3", "FOO-BAR==4"]
        )
        result = run_parse(text)
        self.assertEqual(result["errors"], [])
        self.assertEqual(
            [e["name"] for e in result["entries"]],
            ["foo-bar", "foo-bar", "foo-bar", "foo-bar"],
        )
        self.assertEqual(
            [e["name_raw"] for e in result["entries"]],
            ["foo_bar", "foo-bar", "foo.bar", "FOO-BAR"],
        )

    def test_empty_and_trailing_whitespace_file(self):
        """An empty string is a valid empty file."""
        result = run_parse("")
        self.assertEqual(
            result["counts"],
            {
                "total_lines": 0,
                "entries": 0,
                "errors": 0,
                "comments": 0,
                "blank_lines": 0,
                "options": 0,
            },
        )
        self.assertEqual(result["entries"], [])
        result = run_parse("\n\n")
        self.assertEqual(result["counts"]["blank_lines"], 2)

    def test_packaging_grammar_alignment(self):
        """Operator/operand rules and === quirks match packaging 23.x."""
        text = "\n".join(
            [
                "foo~=1!2.0",
                "foo~=2.2.post3",
                "foo==1.0-1",
                "foo==1.0post",
                "foo==v1.0",
                "foo==1!2.0",
                "foo===whatever!!",
                "foo===",
                "foo=== ",
                "foo====1.0",
                "foo===..",
                "foo===-",
                "foo=== x",
                "foo===1.0,,",
                "foo===1.0,==2",
                "foo===1.0,==2.0 , >=3",
            ]
        )
        result = run_parse(text)
        self.assertEqual(
            result["errors"], [], str(result["errors"])
        )
        by_line = {e["line"]: e for e in result["entries"]}
        self.assertEqual(by_line[1]["specifier"], "~=1!2.0")
        self.assertEqual(by_line[2]["specifier"], "~=2.2.post3")
        self.assertEqual(by_line[3]["specifier"], "==1.0-1")
        self.assertEqual(by_line[5]["specifier"], "==v1.0")
        self.assertEqual(by_line[7]["specifier"], "===whatever!!")
        self.assertEqual(by_line[8]["specifier"], "===")
        self.assertEqual(by_line[9]["specifier"], "===")
        self.assertEqual(by_line[10]["specifier"], "====1.0")
        self.assertEqual(by_line[11]["specifier"], "===..")
        self.assertEqual(by_line[12]["specifier"], "===-")
        self.assertEqual(by_line[13]["specifier"], "=== x")
        self.assertEqual(by_line[14]["specifier"], "===1.0,,")

    def test_bom_stripped_from_first_line(self):
        """A UTF-8 BOM (Windows editors, pip's auto-decode) is dropped."""
        result = run_parse("\ufeffrequests==2.0\nnumpy>=1\n")
        self.assertEqual(result["errors"], [], str(result["errors"]))
        self.assertEqual(
            [e["name"] for e in result["entries"]], ["requests", "numpy"]
        )
        result = run_parse("\ufeff# comment only")
        self.assertEqual(result["counts"]["comments"], 1)

    def test_marker_and_extras_extensions(self):
        """Comma membership markers, hash placement, path extras."""
        text = "\n".join(
            [
                'foo>=1.0 ; python_version in "3.8, 3.9"',
                'foo==1.0 ; python_version >= "3" --hash=sha256:0123abcd',
                "foo @ https://files.example/r.tar.gz --hash=sha256:0123abcd",
                "./pkg ; python_version >= '3.9'",
                "./pkg[extra] ; os_name == 'nt'",
                "-e .[test]",
                '-e . ; python_version >= "3.8"',
                "-e pkg[dev]",
                "https://x/y.whl ; sys_platform == 'darwin'",
            ]
        )
        result = run_parse(text)
        self.assertEqual(result["errors"], [], str(result["errors"]))
        by_line = {e["line"]: e for e in result["entries"]}
        self.assertEqual(
            by_line[1]["markers"], 'python_version in "3.8, 3.9"'
        )
        self.assertEqual(by_line[2]["markers"], 'python_version >= "3"')
        self.assertEqual(by_line[2]["hash"], ["sha256:0123abcd"])
        self.assertEqual(by_line[3]["url"], "https://files.example/r.tar.gz")
        self.assertEqual(by_line[3]["hash"], ["sha256:0123abcd"])
        self.assertEqual(by_line[4]["path"], "./pkg")
        self.assertEqual(by_line[4]["markers"], "python_version >= '3.9'")
        self.assertEqual(by_line[5]["path"], "./pkg")
        self.assertEqual(by_line[5]["extras"], ["extra"])
        self.assertEqual(by_line[6]["path"], ".")
        self.assertEqual(by_line[6]["extras"], ["test"])
        self.assertTrue(by_line[6]["editable"])
        self.assertEqual(by_line[7]["path"], ".")
        self.assertEqual(by_line[7]["markers"], 'python_version >= "3.8"')
        self.assertEqual(by_line[8]["name"], "pkg")
        self.assertEqual(by_line[8]["extras"], ["dev"])
        self.assertIsNone(by_line[8]["path"])
        self.assertEqual(by_line[9]["url"], "https://x/y.whl")
        self.assertEqual(by_line[9]["markers"], "sys_platform == 'darwin'")


# ------------------------------------------------------------------ #
# parse mode — content error matrix
# ------------------------------------------------------------------ #

class ErrorMatrix(unittest.TestCase):
    """Every content-level failure lands in errors with a line no."""

    def assert_error(self, line, fragment):
        result = run_parse(line)
        self.assertEqual(
            result["counts"]["entries"], 0,
            f"{line!r} unexpectedly parsed",
        )
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["line"], 1)
        self.assertIn(fragment, result["errors"][0]["reason"])

    def test_error_matrix(self):
        self.assert_error(">=1.0", "package name")
        self.assert_error("foo >= 1.0 < 2.0", "not a valid PEP 440 version")
        self.assert_error("foo>=2.0<3.0", "not a valid PEP 440 version")
        self.assert_error("foo~=1", "compatible-release")
        self.assert_error("foo~=2!1", "compatible-release")
        self.assert_error("foo==", "malformed specifier clause")
        self.assert_error("foo bar", "malformed specifier clause")
        self.assert_error("foo==1..0", "not a valid PEP 440 version")
        self.assert_error("foo==a", "not a valid PEP 440 version")
        self.assert_error("foo!=x!y", "not a valid PEP 440 version")
        self.assert_error("foo==..1.0", "not a valid PEP 440 version")
        self.assert_error("foo==1.0_1", "not a valid PEP 440 version")
        self.assert_error("foo==1.*.*", "not a valid prefix match")
        self.assert_error("foo==1.0a1.*", "not a valid prefix match")
        self.assert_error("foo>1.2.*", "wildcard")
        self.assert_error("foo<=1.2.*", "wildcard")
        self.assert_error("foo~=1.2.*", "wildcard")
        self.assert_error("foo>1.0+local.1", "local version label")
        self.assert_error("foo~=1.0+local.1", "local version label")
        self.assert_error("foo[a>=1.0", "extras bracket")
        self.assert_error("foo[a,]", "invalid extra name")
        self.assert_error("foo[a b]", "invalid extra name")
        self.assert_error("foo[a!]", "invalid extra name")
        self.assert_error("foo;", "must not be empty")
        self.assert_error("foo ; python_version", "no comparison")
        self.assert_error("foo ; python_version <", "ends with a comparison")
        self.assert_error("foo ; x == '1' and", "operand must follow")
        self.assert_error('foo ; x == "unterminated', "unterminated")
        self.assert_error("foo ; ((x == '1')", "unclosed")
        self.assert_error("foo ; )x == '1')", "never opened")
        self.assert_error("foo===1.0, ==2", "glued there")
        self.assert_error("foo===1.0,== 2", "glued there")
        self.assert_error("trailing-@git+https://x/y.git", "neither a path nor")
        self.assert_error("foo @ 1.0 2.0", "malformed")
        self.assert_error("foo==1.0 --random", "unexpected option")
        self.assert_error("foo --hash", "carries no value")
        self.assert_error("foo==1.0 --hash=notahash", "malformed hash")
        self.assert_error("https://a/b.whl https://c/d.whl", "single token")
        self.assert_error("-x", "unknown requirements-file option")
        self.assert_error("-i", "requires a value")
        self.assert_error("foo >= 1.0 \\", "continuation")
        self.assert_error("!!foo==1.0", "package name")

    def test_errors_never_fail_the_run(self):
        """Good lines still parse alongside bad ones."""
        result = run_parse("good==1.0\nbad line here!\nalsogood>=2")
        self.assertEqual(result["counts"]["entries"], 2)
        self.assertEqual(result["errors"][0]["line"], 2)
        self.assertEqual(result["errors"][0]["raw"], "bad line here!")


# ------------------------------------------------------------------ #
# lint mode — every rule triggered, plus a clean control
# ------------------------------------------------------------------ #

class LintRules(unittest.TestCase):
    """``lint`` — one rule at a time plus the clean control."""

    @staticmethod
    def codes(text):
        return [
            (f["code"], f["line"]) for f in run_lint(text)["findings"]
        ]

    def test_non_pinned_no_specifier(self):
        findings = run_lint("requests\nnumpy>=1.0")["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["code"], "non_pinned_no_specifier")
        self.assertEqual(findings[0]["severity"], "info")
        self.assertEqual(findings[0]["line"], 1)

    def test_mixed_pin_styles(self):
        findings = run_lint("a==1.0\nb==2.0\nc>=1.0")["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["code"], "mixed_pin_styles")
        self.assertEqual(findings[0]["severity"], "warning")
        self.assertIn("2 entries pin exactly", findings[0]["detail"])
        # A single-style file (all ranges) stays silent.
        self.assertEqual(run_lint("a>=1\nb<2")["findings"], [])

    def test_version_pinned_too_tightly(self):
        findings = run_lint("lib==1.2.3")["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["code"], "version_pinned_too_tightly")
        self.assertEqual(findings[0]["severity"], "info")
        # Minor-level pins (==1.2) do not trigger the heuristic.
        self.assertEqual(run_lint("lib==1.2")["findings"], [])

    def test_editable_without_path(self):
        findings = run_lint("-e barename")["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["code"], "editable_without_path")
        self.assertEqual(findings[0]["severity"], "error")
        self.assertEqual(run_lint("-e ./pkg")["findings"], [])

    def test_duplicate_names_after_normalization(self):
        findings = run_lint("foo_bar==1\nfoo-bar==2")["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["code"], "duplicate_names")
        self.assertEqual(findings[0]["severity"], "warning")
        self.assertEqual(findings[0]["lines"], [1, 2])
        self.assertEqual(findings[0]["name"], "foo-bar")

    def test_url_without_hash(self):
        findings = run_lint("https://x/y-1.0.whl")["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["code"], "url_without_hash")
        self.assertEqual(findings[0]["severity"], "info")
        clean = (
            "https://x/y-1.0.whl "
            "--hash=sha256:0123456789abcdef"
        )
        self.assertEqual(run_lint(clean)["findings"], [])

    def test_very_old_line_format(self):
        findings = run_lint("setuptools==0.6c9")["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["code"], "very_old_line_format")
        self.assertEqual(findings[0]["severity"], "info")
        findings = run_lint("distribute==0.7")["findings"]
        self.assertEqual(
            [f["code"] for f in findings], ["very_old_line_format"]
        )
        self.assertEqual(run_lint("setuptools==69.0")["findings"], [])

    def test_case_inconsistent_names(self):
        findings = run_lint("Foo==1\nfoo==2")["findings"]
        codes = sorted(f["code"] for f in findings)
        self.assertEqual(
            codes, ["case_inconsistent_names", "duplicate_names"]
        )
        case = next(
            f for f in findings if f["code"] == "case_inconsistent_names"
        )
        self.assertEqual(case["severity"], "info")

    def test_mixed_relative_absolute_editable(self):
        findings = run_lint("-e ./a\n-e /abs/b")["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(
            findings[0]["code"], "mixed_relative_absolute_editable"
        )
        self.assertEqual(findings[0]["severity"], "warning")
        self.assertEqual(run_lint("-e ./a\n-e ../b")["findings"], [])

    def test_clean_control_file(self):
        clean = "\n".join(
            [
                "# a deliberately clean file",
                "requests[security] ~= 2.31 --hash=sha256:0123456789abcdef",
                "numpy >= 1.26, < 2.0 ; python_version >= '3.9'",
                "-e ./lib/local-helper",
                "",
            ]
        )
        result = run_lint(clean)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["findings"], [])
        self.assertEqual(
            result["finding_counts"],
            {"total": 0, "info": 0, "warning": 0, "error": 0},
        )

    def test_finding_severity_counts_and_order(self):
        text = "\n".join(
            [
                "a==1.2.3",
                "b",
                "-e lost",
                "https://x/y.whl",
            ]
        )
        result = run_lint(text)
        lines = [f.get("line") for f in result["findings"]]
        # Per-line findings sorted by line, file-level (none here) last.
        self.assertEqual(lines, sorted(lines))
        self.assertEqual(
            result["finding_counts"],
            {"total": 4, "info": 3, "warning": 0, "error": 1},
        )


# ------------------------------------------------------------------ #
# diff mode — the freeze-drift matrix
# ------------------------------------------------------------------ #

class DiffMatrix(unittest.TestCase):
    """``diff`` — added / removed / changed with change flags."""

    OLD = "\n".join(
        [
            "requests==2.31.0",
            "numpy==1.26.0 ; python_version >= '3.9'",
            "Foo==1.0",
            "Foo==1.1",
            "./local-helper",
            "urllib3==2.0.7",
            "pydantic[all]==1.10.0",
        ]
    )
    NEW = "\n".join(
        [
            "requests==2.32.3",
            "numpy==1.26.0 ; python_version >= '3.9'",
            "foo>=1.0",
            "Foo==1.2",
            "./local-helper",
            "pydantic[email]==2.6.0",
            "httpx==0.27.0",
        ]
    )

    def test_full_matrix(self):
        result = run_diff(self.OLD, self.NEW)
        # Duplicates pair first-with-first, so 'foo' changes TWICE
        # (Foo==1.0 -> foo>=1.0 and Foo==1.1 -> Foo==1.2); requests
        # and pydantic change once; numpy and ./local-helper hold.
        self.assertEqual(
            result["counts"],
            {
                "total_old": 7,
                "total_new": 7,
                "added": 1,
                "removed": 1,
                "changed": 4,
                "unchanged": 2,
            },
        )
        self.assertEqual(
            [(a["name"], a["raw"]) for a in result["added"]],
            [("httpx", "httpx==0.27.0")],
        )
        self.assertEqual(
            [(r["name"], r["raw"]) for r in result["removed"]],
            [("urllib3", "urllib3==2.0.7")],
        )
        by_name = {}
        for change in result["changed"]:
            by_name.setdefault(change["name"], []).append(change)
        self.assertEqual(sorted(by_name), ["foo", "pydantic", "requests"])

        requests = by_name["requests"][0]
        self.assertTrue(requests["specifier_changed"])
        self.assertFalse(requests["marker_changed"])
        self.assertFalse(requests["extras_changed"])
        self.assertEqual(requests["from"]["specifier"], "==2.31.0")
        self.assertEqual(requests["to"]["specifier"], "==2.32.3")

        pydantic = by_name["pydantic"][0]
        self.assertTrue(pydantic["specifier_changed"])
        self.assertTrue(pydantic["extras_changed"])
        self.assertEqual(pydantic["from"]["extras"], ["all"])
        self.assertEqual(pydantic["to"]["extras"], ["email"])

        # Duplicates pair first-with-first: Foo==1.0 -> foo>=1.0
        # (changed), the Foo==1.1 tail pairs with Foo==1.2 (changed).
        foo_rows = by_name["foo"]
        self.assertEqual(len(foo_rows), 2)
        pairs = {(r["from"]["raw"], r["to"]["raw"]) for r in foo_rows}
        self.assertEqual(
            pairs,
            {("Foo==1.0", "foo>=1.0"), ("Foo==1.1", "Foo==1.2")},
        )

    def test_marker_change_flag(self):
        result = run_diff(
            "numpy==1.26.0", "numpy==1.26.0 ; python_version >= '3.9'"
        )
        self.assertEqual(result["counts"]["changed"], 1)
        row = result["changed"][0]
        self.assertTrue(row["marker_changed"])
        self.assertFalse(row["specifier_changed"])

    def test_other_changed_covers_url_and_hash(self):
        result = run_diff(
            "git+https://x/y.git#egg=y",
            "git+https://x/y.git#egg=y --hash=sha256:0123456789abcdef",
        )
        row = result["changed"][0]
        self.assertTrue(row["other_changed"])
        self.assertFalse(row["specifier_changed"])

    def test_nameless_entries_keyed_by_raw(self):
        result = run_diff("./a\n./b", "./a")
        self.assertEqual(result["counts"]["removed"], 1)
        self.assertEqual(result["counts"]["unchanged"], 1)

    def test_empty_files(self):
        result = run_diff("", "")
        self.assertEqual(
            result["counts"],
            {
                "total_old": 0,
                "total_new": 0,
                "added": 0,
                "removed": 0,
                "changed": 0,
                "unchanged": 0,
            },
        )

    def test_parse_errors_pass_through(self):
        result = run_diff("good==1\nbad line!!\n", "good==2\nworse !!\n")
        self.assertEqual(len(result["errors_old"]), 1)
        self.assertEqual(len(result["errors_new"]), 1)
        self.assertEqual(result["errors_old"][0]["line"], 2)
        self.assertEqual(result["counts"]["changed"], 1)


# ------------------------------------------------------------------ #
# parameter validation (ValueError before any computation)
# ------------------------------------------------------------------ #

class ValidationErrors(unittest.TestCase):
    """Malformed parameters raise instead of returning payloads."""

    def test_bad_mode(self):
        with self.assertRaises(ValueError):
            RequirementsTool().execute(mode="explode", requirements="a==1")
        with self.assertRaises(ValueError):
            RequirementsTool().execute()

    def test_bad_requirements_type(self):
        for bad in (None, 123, True, ["a==1"], b"a==1"):
            with self.assertRaises(ValueError):
                RequirementsTool().execute(mode="parse", requirements=bad)

    def test_diff_requires_both_texts(self):
        with self.assertRaises(ValueError):
            RequirementsTool().execute(
                mode="diff", requirements_old="a==1", requirements_new=None
            )
        with self.assertRaises(ValueError):
            RequirementsTool().execute(
                mode="diff", requirements_old=None, requirements_new="a==1"
            )

    def test_line_count_cap(self):
        text = "\n".join(["a==1"] * 10_001)
        with self.assertRaises(ValueError):
            RequirementsTool().execute(mode="parse", requirements=text)

    def test_single_line_length_cap(self):
        with self.assertRaises(ValueError):
            RequirementsTool().execute(
                mode="parse", requirements="a==" + "1" * 10_001
            )

    def test_total_character_cap(self):
        # 410 lines x 9,900 chars: each line under the line cap and
        # the line count under the file cap, but > 4,000,000 chars.
        text = "\n".join(["a" * 9_900] * 410)
        with self.assertRaises(ValueError):
            RequirementsTool().execute(mode="parse", requirements=text)


# ------------------------------------------------------------------ #
# packaging differential (300 seeded PEP 508 lines)
# ------------------------------------------------------------------ #

try:  # pragma: no cover - exercised once, cheaply
    from packaging.requirements import InvalidRequirement, Requirement
    from packaging.utils import canonicalize_name

    PACKAGING_AVAILABLE = True
except ImportError:  # pragma: no cover
    PACKAGING_AVAILABLE = False

# (line, valid) pairs. The valid lines span the structural PEP 508
# surface; the invalid ones are lines packaging rejects — our parser
# must agree on every seed. Requirements-file-only syntax (comments,
# --hash, editable / path / option lines) is NOT seeded here: it is
# requirements-file layer syntax packaging does not model.
_VALID_SEED_POOL = [
    "requests",
    "requests>=2.0",
    "requests >= 2.0",
    "requests>=2.0,<3.0",
    "requests >= 2.0, < 3.0",
    "requests>=2.0,",
    "requests==2.31.0",
    "requests!=2.30.0",
    "requests<=3.0",
    "requests<3.0",
    "requests>1.0",
    "requests~=2.31",
    "requests===whatever!!",
    "requests==1.2.*",
    "requests!=1.2.*",
    "requests[social]",
    "requests[security,socks]",
    "requests[ security , socks ]",
    "requests[]",
    "requests[security]>=2.0",
    "requests[security,socks] >= 2.0, < 3.0",
    "zope.interface>=3.5",
    "Flask-Login==0.1",
    "a-b_c.d>=1.0",
    "A",
    "A.B-C_D",
    "1.0",
    "42",
    "foo==1.0a1",
    "foo==1.0b2.post3",
    "foo==1.0.dev3",
    "foo==1.0rc1",
    "foo==1!2.0",
    "foo==1.0+local.1",
    "foo==2013.4",
    'foo>=2.0 ; python_version < "3.10"',
    "foo>=2.0;python_version<'3.10'",
    'foo ; os_name == "nt" and python_version >= "3.8"',
    'foo ; (python_version >= "3.8" or python_version < "3.4") and os_name != "posix"',
    'foo ; sys_platform == "darwin"',
    'foo ; "linux" in sys_platform',
    "foo ; extra == 'security'",
    'foo ; implementation_name ~= "cpy"',
    "foo @ https://example.com/x.tar.gz",
    "foo@git+https://example.com/x/y.git#egg=z",
    "foo[socks] @ git+https://x/y.git#egg=z",
    'foo @ https://example.com/x.tar.gz ; python_version >= "3.7"',
    "foo@1.0",
    "foo~=1!2.0",
    "foo~=2!2.0.1",
    "foo~=2.2.post3",
    "foo==1.0-1",
    "foo==1.0post",
    "foo==1.0_r1",
    "foo==v1.0",
    "foo==V1.0",
    "foo==1!2.0",
    "foo===whatever!!",
    "foo===",
    "foo=== ",
    "foo====1.0",
    "foo===..",
    "foo===-",
    "foo=== x",
    "foo===1.0,,",
    "foo===1.0,==2",
    "foo===1.0,==2.0 , >=3",
    'foo>=1.0 ; python_version in "3.8, 3.9"',
    'foo ; python_version in "3.8" and sys_platform not in "win32, cygwin"',
    "foo[a-b]",
    "foo[a_b]",
    "foo[1a]",
    "pytest>=7.0 ; python_full_version >= '3.8.1'",
    "urllib3==2.0.7 ; sys_platform == 'win32' and python_version < '3.10'",
]

_INVALID_SEED_POOL = [
    ">=1.0",
    "foo >= 2.0 < 3.0",
    "foo>=2.0<3.0",
    "foo~=1",
    "foo~=2!1",
    "foo==1..0",
    "foo==a",
    "foo!=x!y",
    "foo==..1.0",
    "foo==1.0_1",
    "foo==1.*.*",
    "foo==1.0a1.*",
    "foo>1.2.*",
    "foo<=1.2.*",
    "foo~=1.2.*",
    "foo>1.0+local.1",
    "foo~=1.0+local.1",
    "foo;",
    "foo ; ",
    "foo ; python_version",
    "foo ; python_version <",
    "foo ; x == '1' and",
    'foo ; x == "unterminated',
    "foo ; ((x == '1')",
    "foo ; )x == '1')",
    "foo==",
    "foo >==1.0",
    "foo bar",
    "foo!!",
    "!!foo==1.0",
    "foo[a>=1.0",
    "foo[a,]",
    "foo[a b]",
    "foo[a!]",
    "foo @ 1.0 2.0",
    "foo==1.0 --random",
    "foo @ ",
    "foo===1.0, ==2",
    "foo===1.0,== 2",
    "trailing-@git+https://x/y.git",
]

# Exactly 300 seeds, deterministically tiled from the pools.
_SEED_POOL = [(line, True) for line in _VALID_SEED_POOL] + [
    (line, False) for line in _INVALID_SEED_POOL
]
SEEDS = [_SEED_POOL[index % len(_SEED_POOL)] for index in range(300)]


def _normalize_marker_text(text):
    """Whitespace / quote / operator-spacing-normalized marker text."""
    collapsed = re.sub(r"\s+", " ", text.strip()).lower()
    collapsed = collapsed.replace("'", '"')
    collapsed = re.sub(
        r"\s*(===|==|!=|<=|>=|<|>|~=)\s*",
        lambda match: " " + match.group(1) + " ",
        collapsed,
    )
    return re.sub(r"\s+", " ", collapsed).strip()


def _our_clauses(entry):
    """Our verbatim specifier as a sorted op+version clause list."""
    if not entry.get("specifier"):
        return []
    clauses = []
    text = entry["specifier"].strip().rstrip(",")
    for clause in text.split(","):
        match = re.match(
            r"^\s*(===|==|!=|<=|>=|~=|<|>)\s*([^\s,;#]*)\s*$", clause
        )
        clauses.append(match.group(1) + match.group(2))
    return sorted(clauses)


@unittest.skipUnless(
    PACKAGING_AVAILABLE, "the packaging distribution is not installed"
)
class PackagingDifferential(unittest.TestCase):
    """300 seeded lines through packaging.Requirement vs our parser.

    Every valid seed: same normalized name, same clause set, same
    extras set, same normalized marker. Every invalid seed: our
    error list carries the line.
    """

    def test_three_hundred_seeded_lines(self):
        self.assertEqual(len(SEEDS), 300)
        text = "\n".join(line for line, _ in SEEDS)
        parsed = run_parse(text)
        entries_by_line = {e["line"]: e for e in parsed["entries"]}
        errors_by_line = {e["line"]: e for e in parsed["errors"]}

        mismatches = []
        for number, (line, valid) in enumerate(SEEDS, start=1):
            try:
                requirement = Requirement(line)
                packaging_valid = True
            except InvalidRequirement:
                packaging_valid = False

            if valid != packaging_valid:
                mismatches.append(
                    f"line {number} {line!r}: seed says valid={valid}, "
                    f"packaging says {packaging_valid}"
                )
                continue
            if not packaging_valid:
                if number not in errors_by_line:
                    mismatches.append(
                        f"line {number} {line!r}: packaging rejects and "
                        f"so must we (no error reported)"
                    )
                continue
            entry = entries_by_line.get(number)
            if entry is None:
                mismatches.append(
                    f"line {number} {line!r}: packaging accepts but we "
                    f"produced no entry"
                )
                continue
            if canonicalize_name(requirement.name) != entry["name"]:
                mismatches.append(
                    f"line {number} {line!r}: name "
                    f"{canonicalize_name(requirement.name)!r} != "
                    f"{entry['name']!r}"
                )
            theirs = sorted(str(s) for s in requirement.specifier)
            ours = _our_clauses(entry)
            if theirs != ours:
                mismatches.append(
                    f"line {number} {line!r}: clauses {theirs!r} != "
                    f"{ours!r}"
                )
            if {e.lower() for e in requirement.extras} != {
                e.lower() for e in (entry.get("extras") or [])
            }:
                mismatches.append(
                    f"line {number} {line!r}: extras "
                    f"{sorted(requirement.extras)!r} != "
                    f"{entry.get('extras')!r}"
                )
            if (requirement.marker is None) != (entry.get("markers") is None):
                mismatches.append(
                    f"line {number} {line!r}: marker presence disagrees"
                )
            elif requirement.marker is not None:
                theirs = _normalize_marker_text(str(requirement.marker))
                ours = _normalize_marker_text(entry["markers"])
                if theirs != ours:
                    mismatches.append(
                        f"line {number} {line!r}: marker {theirs!r} != "
                        f"{ours!r}"
                    )
        self.assertEqual(
            mismatches, [], f"{len(mismatches)} differential mismatches"
        )


# ------------------------------------------------------------------ #
# package-level export sanity
# ------------------------------------------------------------------ #

class ExportSanity(unittest.TestCase):
    """The tool is importable from the package and self-describing."""

    def test_package_exports(self):
        self.assertIs(DirectRequirementsTool, RequirementsTool)

    def test_metadata(self):
        tool = RequirementsTool()
        self.assertEqual(tool.name, "requirements_tool")
        self.assertIn("requirements.txt", tool.description.lower())
        self.assertEqual(tool.MODES, ("parse", "lint", "diff"))


if __name__ == "__main__":
    unittest.main()
