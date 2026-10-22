#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_freeze_diff_tool.py

"""Offline unit tests for FreezeDiffTool.

The tool compares installed-environment snapshots on the standard
library plus ``importlib.metadata`` (stdlib) and never touches the
network, so this suite runs fully offline. Assertions are
deterministic against hand-computed ground truths on the
text-parsing paths; the ``live`` source is environment-dependent by
definition, so its tests assert only structural invariants (source
tag, sorted order, PEP 503 normalized names, count consistency)
that hold in every interpreter. The ``installed`` vectors cover the
freeze matrix (pins, ``===`` pins, PEP 503 normalization collisions
counted as duplicates, editable and direct-reference lines, comments
and blanks reported distinctly, junk lines as errors), the
``compare`` vectors walk every operator class (``==`` with zero
padding, ``!=``, range pairs, ``~=``, wildcards, bare names,
``===``, pre-release policy) plus missing / undeclared / exempt
handling, marker and non-version exclusion and the summary counts,
the ``snapshot_diff`` vectors cover upgrade / downgrade / add /
remove with PEP 440 ordering (``1.0rc1 < 1.0 < 1.0.post1``, epoch
bumps, ``1.9 < 1.10``), ordering-equal renames and unparsable
pairs, and the error matrix walks every content-level failure.
Parameter-level mistakes are ``ValueError`` (wrong types, missing
required parameters, over-cap inputs, malformed exempt lists).

When the third-party ``packaging`` distribution is importable, a
differential suite additionally cross-checks the built-in minimal
evaluator against ``packaging.specifiers.SpecifierSet.contains`` on
500 seeded (specifier, version) pairs and the ordering key against
``packaging.version.Version`` on a seeded pair matrix — the
evaluator is deliberately aligned with packaging on everything the
two share. Two documented exclusions: range clauses carrying a
local segment (packaging rejects them at parse time — so does this
tool) and epoch-bearing candidates under wildcard / ``~=`` clauses
(packaging 23.x carries a known epoch-prefix bug there, fixed
upstream; this tool follows PEP 440 and packaging 24+). The
differential is skipped when ``packaging`` is absent so the suite
stays stdlib-only offline.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import FreezeDiffTool
from agentuniverse.agent.action.tool.common_tool.freeze_diff_tool import (
    FreezeDiffTool as DirectFreezeDiffTool,
)
from agentuniverse.agent.action.tool.common_tool.freeze_diff_tool import (
    _evaluate_minimal,
    _ordering_key,
    _parse_version,
)

try:  # pragma: no cover - exercised once, cheaply
    from packaging.specifiers import SpecifierSet
    from packaging.version import InvalidVersion, Version

    PACKAGING_AVAILABLE = True
except ImportError:  # pragma: no cover
    PACKAGING_AVAILABLE = False


def run_installed(freeze=None):
    return FreezeDiffTool().execute(mode="installed", freeze=freeze)


def run_compare(requirements, freeze=None, exempt=None):
    return FreezeDiffTool().execute(
        mode="compare",
        requirements=requirements,
        freeze=freeze,
        exempt=exempt,
    )


def run_snapshot(freeze_old, freeze_new):
    return FreezeDiffTool().execute(
        mode="snapshot_diff", freeze_old=freeze_old, freeze_new=freeze_new
    )


# ------------------------------------------------------------------ #
# installed mode — the freeze-text matrix
# ------------------------------------------------------------------ #

class InstalledTextGroundTruths(unittest.TestCase):
    """``installed`` with a freeze text: pins and everything else."""

    def test_full_matrix(self):
        """Pins, === pins, editables, URLs, comments, blanks, errors."""
        text = "\n".join(
            [
                "requests==2.31.0",
                "zope.interface===6.0.post1",
                "# Editable install with no version control (pip==23.0)",
                "-e /tmp/workspace/pkg",
                "agentuniverse @ file:///tmp/au.whl",
                "",
                "Flask-Cors==4.0.0",
                "not a pin",
            ]
        )
        result = run_installed(text)
        self.assertEqual(result["mode"], "installed")
        self.assertEqual(result["source"], "text")
        self.assertEqual(result["count"], 3)
        self.assertEqual(
            result["distributions"],
            [
                {
                    "name": "flask-cors",
                    "name_raw": "Flask-Cors",
                    "version": "4.0.0",
                },
                {"name": "requests", "name_raw": "requests", "version": "2.31.0"},
                {
                    "name": "zope-interface",
                    "name_raw": "zope.interface",
                    "version": "6.0.post1",
                },
            ],
        )
        self.assertEqual(result["comments"], 1)
        self.assertEqual(result["blanks"], 1)
        self.assertEqual(len(result["editables"]), 1)
        self.assertEqual(result["editables"][0]["line"], 4)
        self.assertEqual(len(result["direct_urls"]), 1)
        self.assertEqual(result["direct_urls"][0]["line"], 5)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["line"], 8)
        self.assertEqual(result["errors"][0]["raw"], "not a pin")

    def test_normalization_collision_is_duplicate(self):
        """Foo_Bar / foo-bar / foo.bar are one package: first wins."""
        text = "Foo_Bar==1.0\nfoo-bar==2.0\nfoo.bar==3.0"
        result = run_installed(text)
        self.assertEqual(result["count"], 1)
        self.assertEqual(
            result["distributions"][0],
            {"name": "foo-bar", "name_raw": "Foo_Bar", "version": "1.0"},
        )
        self.assertEqual(len(result["errors"]), 2)
        self.assertIn("duplicate pin", result["errors"][0]["reason"])

    def test_sorted_and_empty(self):
        """Output sorted by normalized name; empty text is empty env."""
        result = run_installed("bbb==1.0\naaa==2.0")
        self.assertEqual(
            [item["name"] for item in result["distributions"]], ["aaa", "bbb"]
        )
        empty = run_installed("")
        self.assertEqual(empty["count"], 0)
        self.assertEqual(empty["distributions"], [])

    def test_whitespace_pins(self):
        """``==`` accepts the spaced freeze spellings."""
        result = run_installed("requests == 2.31.0")
        self.assertEqual(
            result["distributions"][0]["version"], "2.31.0"
        )


class InstalledLiveStructural(unittest.TestCase):
    """``installed`` live — structural invariants only (the live
    environment is machine-dependent; these hold everywhere)."""

    def test_live_structure(self):
        result = run_installed()
        self.assertEqual(result["mode"], "installed")
        self.assertEqual(result["source"], "live")
        self.assertEqual(result["count"], len(result["distributions"]))
        names = [item["name"] for item in result["distributions"]]
        self.assertEqual(names, sorted(names))
        import re

        for item in result["distributions"]:
            self.assertTrue(item["name"])
            self.assertNotRegex(item["name"], r"[._]")
            self.assertIsInstance(item["requires_dist_count"], int)
            self.assertIn("version", item)
        self.assertIn("note", result)


# ------------------------------------------------------------------ #
# compare mode — declared vs installed
# ------------------------------------------------------------------ #

class CompareGroundTruths(unittest.TestCase):
    """``compare``: verdicts, missing, undeclared, exempt, summary."""

    FREEZE = (
        "requests==2.28.1\n"
        "flask==3.0.0\n"
        "numpy==1.26.0\n"
        "pip==24.0\n"
        "setuptools==68.0.0\n"
        "wheel==0.42.0\n"
        "wheel-insider==1.0\n"
        "leftover==9.9\n"
    )

    def test_operator_matrix(self):
        """Every operator class judged against the freeze text."""
        requirements = "\n".join(
            [
                "requests>=2.0,<3.0",       # satisfied both clauses
                "flask==3.0.0.0",           # == zero padding
                "numpy!=1.25.0",            # != satisfied
                "scipy~=1.10",              # not installed -> missing
                "leftover<9.9",             # installed but unsatisfied
                "wheel-insider==1.0",        # declared, not exempt here
            ]
        )
        result = run_compare(requirements, self.FREEZE)
        self.assertEqual(result["mode"], "compare")
        self.assertEqual(result["source"], "text")
        rows = {row["name"]: row for row in result["declared"]}
        self.assertTrue(rows["requests"]["satisfied"])
        self.assertEqual(
            [c["satisfied"] for c in rows["requests"]["clauses"]], [True, True]
        )
        self.assertTrue(rows["flask"]["satisfied"])
        self.assertTrue(rows["numpy"]["satisfied"])
        self.assertTrue(rows["wheel-insider"]["satisfied"])
        self.assertFalse(rows["leftover"]["satisfied"])
        self.assertIn("clause <9.9 not satisfied", rows["leftover"]["reason"])
        self.assertIsNone(rows["scipy"].get("installed_version"))
        self.assertEqual(rows["scipy"]["reason"], "not installed")
        self.assertEqual(result["missing_not_installed"], ["scipy"])
        # every installed distribution here is declared except the
        # exempt bootstrap trio, so nothing is undeclared drift.
        self.assertEqual(result["undeclared_installed"], [])
        self.assertEqual(
            {item["name"] for item in result["exempt_filtered"]},
            {"pip", "setuptools", "wheel"},
        )

    def test_bare_name_and_extras_and_normalization(self):
        """Bare names need only presence; extras match the base name;
        Flask_Login matches an installed flask-login pin."""
        requirements = "numpy\nFlask_Login[async]\n"
        result = run_compare(requirements, "numpy==1.26.0\nflask-login==0.6.2\n")
        rows = {row["name"]: row for row in result["declared"]}
        self.assertIsNone(rows["numpy"]["spec"])
        self.assertEqual(rows["numpy"]["clauses"], [])
        self.assertTrue(rows["numpy"]["satisfied"])
        self.assertTrue(rows["flask-login"]["satisfied"])
        self.assertEqual(rows["flask-login"]["name_raw"], "Flask_Login")
        self.assertEqual(rows["flask-login"]["extras"], ["async"])
        self.assertEqual(result["summary"]["satisfied"], 2)

    def test_prerelease_policy(self):
        """A pre-release install satisfies only a clause that itself
        mentions a pre-release (packaging-compatible)."""
        requirements = "pkg>=1.0\n"
        result = run_compare(requirements, "pkg==1.1rc1\n")
        row = result["declared"][0]
        self.assertFalse(row["satisfied"])
        self.assertIn("pre-release installed version excluded", row["reason"])
        result2 = run_compare("pkg>=1.0rc1\n", "pkg==1.1rc1\n")
        self.assertTrue(result2["declared"][0]["satisfied"])

    def test_exempt_list_variants(self):
        """Custom exempt list replaces the default; [] filters nothing."""
        requirements = "declared==1.0\n"
        freeze = "declared==1.0\npip==24.0\nsetuptools==68.0\nmystery==2.0\n"
        result = run_compare(requirements, freeze, exempt=["pip", "Mystery"])
        self.assertEqual(
            [item["name"] for item in result["undeclared_installed"]],
            ["setuptools"],
        )
        self.assertEqual(
            {item["name"] for item in result["exempt_filtered"]},
            {"pip", "mystery"},
        )
        none = run_compare(requirements, freeze, exempt=[])
        self.assertEqual(none["exempt_filtered"], [])
        self.assertEqual(len(none["undeclared_installed"]), 3)

    def test_marker_and_non_version_lines_excluded(self):
        """Markers are listed verbatim, never judged; editable / URL /
        path / direct-ref lines cannot be version-compared."""
        requirements = "\n".join(
            [
                "requests==2.28.1",
                "winpkg ; sys_platform == 'win32'",
                "-e ./local/pkg",
                "gitpkg @ git+https://x/y.git#egg=gitpkg",
                "./some/path",
                "https://example.com/thing.whl",
            ]
        )
        result = run_compare(requirements, self.FREEZE)
        self.assertEqual(len(result["declared"]), 1)
        self.assertEqual(result["marker_lines"][0]["marker"], "sys_platform == 'win32'")
        self.assertEqual(result["summary"]["marker_excluded"], 1)
        kinds = [item["kind"] for item in result["non_version_lines"]]
        self.assertEqual(
            kinds, ["editable", "direct_url", "path_or_url", "path_or_url"]
        )
        self.assertEqual(result["summary"]["non_version_lines"], 4)
        self.assertEqual(result["summary"]["declared"], 1)

    def test_options_comments_and_errors(self):
        """pip options and comments never declare; bad clauses error."""
        requirements = "\n".join(
            [
                "# core deps",
                "-r requirements-base.txt",
                "--no-index",
                "requests==2.28.1",
                "broken==",
                "alsobad~=1",
            ]
        )
        result = run_compare(requirements, self.FREEZE)
        self.assertEqual(result["comments"], ["core deps"])
        self.assertEqual(len(result["options"]), 2)
        self.assertEqual(len(result["declared"]), 1)
        self.assertEqual(len(result["errors"]), 2)
        reasons = {error["line"] for error in result["errors"]}
        self.assertEqual(reasons, {5, 6})

    def test_summary_counts(self):
        """The summary matches the rows exactly."""
        requirements = (
            "requests>=2.0,<3.0\nflask==3.0.0\nscipy\nleftover==9.9\n"
        )
        result = run_compare(requirements, self.FREEZE)
        self.assertEqual(
            result["summary"],
            {
                "total_installed": 8,
                "declared": 4,
                "satisfied": 3,
                "unsatisfied_installed": 0,
                "missing": 1,
                "marker_excluded": 0,
                "non_version_lines": 0,
                "undeclared_installed": 2,
                "exempt_filtered": 3,
            },
        )
        # numpy and wheel-insider are installed but never declared
        # ('wheel-insider' is not exempt — only 'wheel' is).

    def test_errors_environment_passthrough(self):
        """Freeze junk lines surface as errors_environment."""
        result = run_compare(
            "requests==2.28.1\n", "requests==2.28.1\nwhat is this\n"
        )
        self.assertEqual(len(result["errors_environment"]), 1)
        self.assertEqual(result["errors_environment"][0]["line"], 2)

    def test_duplicate_declarations_evaluated_independently(self):
        """Two lines for one package -> two rows, both judged."""
        requirements = "leftover>=9.0\nleftover<9.5\n"
        result = run_compare(requirements, self.FREEZE)
        self.assertEqual(len(result["declared"]), 2)
        verdicts = [row["satisfied"] for row in result["declared"]]
        self.assertEqual(verdicts, [True, False])

    def test_live_compare_structural(self):
        """Live compare: structural invariants only."""
        result = run_compare("requests\n")
        self.assertEqual(result["mode"], "compare")
        self.assertEqual(result["source"], "live")
        self.assertEqual(
            result["summary"]["total_installed"],
            len({item["name"] for item in result["declared"]})
            + result["summary"]["undeclared_installed"]
            + result["summary"]["exempt_filtered"]
            + len({row["name"] for row in result["declared"] if row["satisfied"]})
            - len(result["declared"]),
        )
        self.assertEqual(result["verifier"] in ("packaging", "minimal-evaluator"), True)


# ------------------------------------------------------------------ #
# the minimal evaluator — operator ground truths
# ------------------------------------------------------------------ #

class MinimalEvaluatorGroundTruths(unittest.TestCase):
    """The built-in ==/!=/>=/<=/~=/</>/=== evaluator."""

    def evaluate(self, spec, version):
        clauses = []
        for piece in spec.split(","):
            piece = piece.strip()
            op, _, rest = piece.partition(" ")
            if not rest:
                op = piece.rstrip("0123456789.*!+ abcdefghijklmnopqrstuvwxyz")
                rest = piece[len(op):]
            clauses.append((op, rest))
        return _evaluate_minimal(clauses, version)[0]

    def test_equality_zero_padding_and_local(self):
        self.assertTrue(self.evaluate("==1.0", "1.0.0"))
        self.assertTrue(self.evaluate("==1.0", "1.0+local"))
        self.assertFalse(self.evaluate("==1.0", "1.0.post1"))
        self.assertFalse(self.evaluate("==1.0", "1.0.dev1"))
        self.assertTrue(self.evaluate("==1.0+local", "1.0+LOCAL"))
        self.assertFalse(self.evaluate("==1.0+local", "1.0+other"))
        self.assertTrue(self.evaluate("!=1.0", "1.1"))

    def test_wildcards(self):
        self.assertTrue(self.evaluate("==1.2.*", "1.2.5"))
        self.assertTrue(self.evaluate("==1.2.*", "1.2"))
        self.assertTrue(self.evaluate("==1.2.0.*", "1.2"))
        self.assertFalse(self.evaluate("==1.2.*", "1.10"))
        self.assertFalse(self.evaluate("==1.2.*", "1"))
        self.assertFalse(self.evaluate("==1.2.*", "1!1.2"))
        self.assertTrue(self.evaluate("!=1.2.*", "1.3"))
        self.assertFalse(self.evaluate("!=1.2.*", "1.2.9"))

    def test_ranges(self):
        self.assertTrue(self.evaluate(">=1.0", "1.0+local"))
        self.assertTrue(self.evaluate(">=1.0", "1!0.5"))
        self.assertTrue(self.evaluate("<=1.0", "1.0+local"))
        self.assertFalse(self.evaluate("<=1.0", "1.0.1"))
        self.assertTrue(self.evaluate(">1.0", "1.0.post1") is False)
        self.assertTrue(self.evaluate(">1.0", "1.1.post1"))
        self.assertTrue(self.evaluate(">0.9", "1.0.post1"))
        # both same-base and foreign-base dev releases are excluded
        # by the pre-release gate (packaging contains() semantics)
        self.assertFalse(self.evaluate("<3.1", "3.1.dev0"))
        self.assertFalse(self.evaluate("<3.1", "3.0.dev0"))
        self.assertTrue(self.evaluate("<3.1", "3.0"))

    def test_compatible_release(self):
        self.assertTrue(self.evaluate("~=1.2.3", "1.2.9"))
        self.assertFalse(self.evaluate("~=1.2.3", "1.3"))
        self.assertFalse(self.evaluate("~=1.2.3", "1.2.2"))
        self.assertTrue(self.evaluate("~=1.2", "1.9"))
        self.assertFalse(self.evaluate("~=1.2", "2.0"))
        self.assertTrue(self.evaluate("~=2.2.post3", "2.3"))

    def test_arbitrary_equality(self):
        self.assertTrue(self.evaluate("===1.0", "v1.0"))
        self.assertFalse(self.evaluate("===1.0", "1.0.0"))
        self.assertTrue(self.evaluate("===1.0.0", "1.0.0"))
        self.assertFalse(self.evaluate("===v1.0", "1.0"))
        self.assertFalse(self.evaluate("===1.0", "1.0.post1"))

    def test_prerelease_policy(self):
        self.assertFalse(self.evaluate(">=1.0", "1.1rc1"))
        self.assertTrue(self.evaluate(">=1.0rc1", "1.1rc1"))
        self.assertFalse(self.evaluate("==1.2.*", "1.2rc1"))
        # the excluded-because-prerelease reason is reported
        ok, reason = _evaluate_minimal([(">=", "1.0")], "1.1rc1")
        self.assertFalse(ok)
        self.assertIn("pre-release", reason)
        # an unparseable installed version is False with a reason
        ok, reason = _evaluate_minimal([("==", "1.0")], "not-a-version")
        self.assertFalse(ok)
        self.assertIn("not parseable", reason)


# ------------------------------------------------------------------ #
# snapshot_diff mode — the before/after matrix
# ------------------------------------------------------------------ #

class SnapshotDiffGroundTruths(unittest.TestCase):
    """``snapshot_diff``: direction, add/remove, ordering."""

    def test_full_matrix(self):
        old = "\n".join(
            [
                "requests==2.28.0",
                "flask==3.0.0",
                "numpy==1.26.0",
                "gone==1.0",
                "pkg==1.0rc1",
                "epoch==0!1.0",
                "num==1.9",
            ]
        )
        new = "\n".join(
            [
                "requests==2.31.0",
                "flask==2.3.0",
                "numpy==1.26.0",
                "fresh==0.1",
                "pkg==1.0",
                "epoch==1!0.5",
                "num==1.10",
            ]
        )
        result = run_snapshot(old, new)
        self.assertEqual(result["mode"], "snapshot_diff")
        self.assertEqual(
            result["upgraded"],
            [
                {"name": "epoch", "from": "0!1.0", "to": "1!0.5"},
                {"name": "num", "from": "1.9", "to": "1.10"},
                {"name": "pkg", "from": "1.0rc1", "to": "1.0"},
                {"name": "requests", "from": "2.28.0", "to": "2.31.0"},
            ],
        )
        self.assertEqual(
            result["downgraded"],
            [{"name": "flask", "from": "3.0.0", "to": "2.3.0"}],
        )
        self.assertEqual(result["added"], [{"name": "fresh", "version": "0.1"}])
        self.assertEqual(result["removed"], [{"name": "gone", "version": "1.0"}])
        self.assertEqual(result["unchanged_count"], 1)
        self.assertIn(result["ordering"], ("packaging", "pep440-minimal"))

    def test_ordering_equal_rename_is_unchanged(self):
        """1.0 -> 1.0.0 is not a move under PEP 440."""
        result = run_snapshot("a==1.0\n", "a==1.0.0\n")
        self.assertEqual(result["unchanged_count"], 1)
        self.assertEqual(result["upgraded"], [])
        self.assertEqual(result["downgraded"], [])

    def test_unparsed_and_ignored_passthrough(self):
        """Junk versions land in unparsed; non-pin lines in ignored_*."""
        old = "-e /old/pkg\nweird==1.0$\noldurl @ https://x/y.whl\n"
        new = "weird==2.0$\n"
        result = run_snapshot(old, new)
        self.assertEqual(
            result["unparsed"], [{"name": "weird", "from": "1.0$", "to": "2.0$"}]
        )
        self.assertEqual(result["upgraded"], [])
        self.assertEqual(len(result["ignored_old"]), 2)
        self.assertEqual(result["ignored_new"], [])
        self.assertEqual(len(result["errors_old"]), 0)
        self.assertEqual(result["errors_new"], [])

    def test_pre_and_post_ordering(self):
        """1.0.dev1 < 1.0a1 < 1.0rc1 < 1.0 < 1.0.post1 < 1.0.1."""
        chain = ["1.0.dev1", "1.0a1", "1.0rc1", "1.0", "1.0.post1", "1.0.1"]
        for before, after in zip(chain, chain[1:]):
            result = run_snapshot(f"p=={before}\n", f"p=={after}\n")
            self.assertEqual(
                result["upgraded"],
                [{"name": "p", "from": before, "to": after}],
                f"{before} -> {after} should upgrade",
            )
            back = run_snapshot(f"p=={after}\n", f"p=={before}\n")
            self.assertEqual(
                back["downgraded"],
                [{"name": "p", "from": after, "to": before}],
            )


# ------------------------------------------------------------------ #
# content-level errors
# ------------------------------------------------------------------ #

class ErrorMatrix(unittest.TestCase):
    """Malformed content lands in errors, never raises."""

    def test_freeze_junk_and_duplicates(self):
        result = run_installed("???\n==1.0\na==1\na==2\n")
        self.assertEqual(len(result["errors"]), 3)
        self.assertEqual(result["count"], 1)

    def test_requirement_clause_errors(self):
        cases = [
            ("foo==", "carries no version"),
            ("foo bar", "does not start with an operator"),
            ("foo~=1", "at least two release"),
            ("foo>=1.2.*", "only valid with == or !="),
            ("foo>=1.0+local", "local version segment"),
            ("foo==not!a@version", "not a PEP 440"),
        ]
        for line, expected in cases:
            result = run_compare(f"{line}\n", "foo==1.0\n")
            self.assertEqual(len(result["errors"]), 1, line)
            self.assertIn(expected, result["errors"][0]["reason"], line)
            self.assertEqual(len(result["declared"]), 0, line)

    def test_marker_errors(self):
        for line in ["foo ;", "foo ; ", 'foo ; (x == "1', "foo ; x == 'open"]:
            result = run_compare(f"{line}\n", "foo==1.0\n")
            self.assertEqual(len(result["errors"]), 1, line)

    def test_empty_extras_item(self):
        result = run_compare("foo[,]>=1.0\n", "foo==1.0\n")
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("empty extras", result["errors"][0]["reason"])
        # a bracket holding only whitespace is an empty extras list
        ok = run_compare("foo[ ]>=1.0\n", "foo==1.0\n")
        self.assertEqual(len(ok["errors"]), 0)
        self.assertEqual(ok["declared"][0]["extras"], [])


# ------------------------------------------------------------------ #
# parameter-level validation
# ------------------------------------------------------------------ #

class ValidationErrors(unittest.TestCase):
    """Malformed parameters raise ValueError before any work."""

    def test_mode(self):
        for bad in (None, "", "parse", "diff", 5):
            with self.assertRaises(ValueError):
                FreezeDiffTool().execute(mode=bad)

    def test_compare_requires_requirements(self):
        with self.assertRaises(ValueError):
            FreezeDiffTool().execute(mode="compare")
        with self.assertRaises(ValueError):
            FreezeDiffTool().execute(mode="compare", requirements=None)

    def test_snapshot_requires_both(self):
        with self.assertRaises(ValueError):
            FreezeDiffTool().execute(mode="snapshot_diff", freeze_old="a==1\n")
        with self.assertRaises(ValueError):
            FreezeDiffTool().execute(mode="snapshot_diff", freeze_new="a==1\n")

    def test_wrong_types(self):
        with self.assertRaises(ValueError):
            run_installed(freeze=123)
        with self.assertRaises(ValueError):
            run_installed(freeze=True)
        with self.assertRaises(ValueError):
            run_compare(requirements=["requests"], freeze="a==1\n")
        with self.assertRaises(ValueError):
            run_compare("a==1\n", freeze=b"bytes")

    def test_caps(self):
        with self.assertRaises(ValueError):
            run_installed(freeze="a==1\n" * 10001)
        with self.assertRaises(ValueError):
            run_installed(freeze="a==" + "1" * 10001 + "\n")
        with self.assertRaises(ValueError):
            run_installed(freeze="x" * 4_000_001)

    def test_exempt_validation(self):
        for bad in ("pip", 42, True, [42], [""], ["a", None], [True]):
            with self.assertRaises(ValueError):
                run_compare("a==1\n", "a==1\n", exempt=bad)
        with self.assertRaises(ValueError):
            run_compare("a==1\n", "a==1\n", exempt=[f"p{i}" for i in range(1001)])


# ------------------------------------------------------------------ #
# packaging differential (500 seeded specifier/version pairs)
# ------------------------------------------------------------------ #

try:  # pragma: no cover
    if PACKAGING_AVAILABLE:
        _SPEC_POOL = [
            "==1.0", "==1.0.0", "==1.0.*", "==1.2.*", "==1.2.0.*",
            "==0.*", "==1.0.0.*", "==1!1.0", "==2.0.dev1",
            "!=1.0", "!=1.2.*", "!=1.0.0", "!=1.2.0.*", "!=1!1.0",
            ">=1.0", ">=1.0a1", ">=1.0.dev1", ">=2.0.5", ">=1!0.5",
            ">=1.0.post1",
            "<=1.0", "<=2.0.5", "<=1.0a1", "<=1!1.0",
            ">1.0", ">1.0.post1", ">0.9", ">1.0a1", ">1!0.5",
            "<3.1", "<2.0", "<3.1.dev5", "<1.5",
            "~=1.2", "~=1.2.3", "~=2.2.post3", "~=1.4.5a4", "~=0.9",
            "===1.0", "===1.0.0", "===2.0.post1", "===1!1.0", "===v1.0",
            "===1.0+local",
        ]
        _VER_POOL = [
            "1.0", "1.0.0", "1", "1.2", "1.2.0", "1.2.3", "1.2.5",
            "1.10", "2.0", "0.9", "1.0a1", "1.0b2", "1.0rc1", "1.0.dev1",
            "1.0.dev2", "1.0a1.dev1", "1.0.post1", "1.0.post2",
            "1.0+local", "1.0+local.2", "1!0.5", "1!1.0", "2.0.5",
            "1.5", "1.4.5a5", "1.4.5a4", "3.1.dev0", "0.5", "1.0.1",
            "1.0.post1+local", "v1.0", "1.0alpha1", "1.0-beta2",
            "1!1.0rc1", "1.2.0rc1",
        ]
except Exception:  # pragma: no cover
    pass


@unittest.skipUnless(
    PACKAGING_AVAILABLE, "the packaging distribution is not installed"
)
class PackagingDifferential(unittest.TestCase):
    """500 seeded pairs through packaging vs the minimal evaluator."""

    @staticmethod
    def _clauses_of(spec):
        from agentuniverse.agent.action.tool.common_tool import (
            freeze_diff_tool as fdt,
        )

        clauses = []
        for piece in spec.split(","):
            match = fdt._CLAUSE_OP_RE.match(piece.strip())
            clauses.append((match.group(1), match.group(2).strip()))
        return clauses

    def test_seeded_specifier_pairs_full_cross_product(self):
        """The whole spec x version cross product (plus seeded
        two-clause sets) is checked — a previous revision sliced
        ``pairs[:500]``, and since the == / != specs alone fill the
        first 500 slots, the > / < / ~= / === families and every
        multi-clause combination were never differentially tested.
        """
        import random

        rng = random.Random(20261021)
        pairs = []

        def wildcardish(spec):
            return any(
                piece.strip().endswith(".*")
                or piece.strip().startswith("~=")
                for piece in spec.split(",")
            )

        for spec in _SPEC_POOL:
            for version in _VER_POOL:
                # Excluded, documented: packaging 23.x epoch-prefix bug
                # under wildcard / ~= (fixed in packaging 24+; this
                # tool follows PEP 440 there).
                if wildcardish(spec) and "!" in version:
                    continue
                pairs.append((spec, version))
        # seeded two-clause sets (pre-release gate interactions)
        combos = set()
        while len(combos) < 500:
            spec = f"{rng.choice(_SPEC_POOL)},{rng.choice(_SPEC_POOL)}"
            version = rng.choice(_VER_POOL)
            if wildcardish(spec) and "!" in version:
                continue
            combos.add((spec, version))
        pairs.extend(sorted(combos))
        checked = 0
        for spec, version in pairs:
            ours, _ = _evaluate_minimal(self._clauses_of(spec), version)
            theirs = SpecifierSet(spec).contains(version)
            self.assertEqual(
                ours,
                theirs,
                f"specifier {spec!r} vs version {version!r}: minimal "
                f"says {ours}, packaging says {theirs}",
            )
            checked += 1
        self.assertGreaterEqual(checked, 2000)

    def test_ordering_key_agrees_with_packaging(self):
        import itertools

        pool = _VER_POOL
        for a, b in itertools.combinations(pool, 2):
            ours_lt = _parse_version(a).cmpkey() < _parse_version(b).cmpkey()
            ours_eq = _parse_version(a).cmpkey() == _parse_version(b).cmpkey()
            theirs_lt = Version(a) < Version(b)
            theirs_eq = Version(a) == Version(b)
            self.assertEqual(ours_lt, theirs_lt, f"{a} < {b}")
            self.assertEqual(ours_eq, theirs_eq, f"{a} == {b}")

    def test_compare_rows_agree_with_packaging(self):
        """End-to-end: compare-mode verdicts match SpecifierSet."""
        requirements = "\n".join(
            [
                "pkg1>=1.0,<3.0",
                "pkg2==2.0",
                "pkg3~=1.4",
                "pkg4!=1.2.*",
                "pkg5>0.9",
                "pkg6<=2.0.5",
                "pkg7===1.0",
            ]
        )
        freeze = "\n".join(
            [
                "pkg1==2.8",
                "pkg2==2.0.post1",
                "pkg3==1.4.9",
                "pkg4==1.2.7",
                "pkg5==1.0.post1",
                "pkg6==2.0.5",
                "pkg7==v1.0",
            ]
        )
        result = run_compare(requirements, freeze)
        for row in result["declared"]:
            spec = row["spec"]
            expected = SpecifierSet(spec).contains(row["installed_version"])
            self.assertEqual(
                row["satisfied"],
                expected,
                f"{spec} vs installed {row['installed_version']}",
            )


# ------------------------------------------------------------------ #
# self-review regressions (differential findings, #4026 review)
# ------------------------------------------------------------------ #

class SelfReviewRegressions(unittest.TestCase):
    """Defects found by differential testing against packaging
    (Version / SpecifierSet / Requirement) and fixed — one test
    per provable disagreement."""

    def test_ascii_only_version_grammar(self):
        """PEP 440 requires ASCII digits; ``\\d`` also matched
        Arabic-Indic / fullwidth digits that packaging rejects."""
        from agentuniverse.agent.action.tool.common_tool import (
            freeze_diff_tool as fdt,
        )

        for bad in ["\u0661.\u0662", "\uff11.\uff10", "1!\u0662",
                    "v\u0661.0", "1.0.post\u0661"]:
            self.assertIsNone(fdt._parse_version(bad), repr(bad))
        # the requirement side rejects such clauses outright
        result = run_compare("pkg==\uff11.\uff10\n", "pkg==1.0\n")
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("not a PEP 440", result["errors"][0]["reason"])
        # the snapshot side routes such pins to unparsed
        snap = run_snapshot("p==1.0\n", "p==\uff10\n")
        self.assertEqual(
            snap["unparsed"], [{"name": "p", "from": "1.0", "to": "\uff10"}]
        )

    def test_parenthesized_specifiers(self):
        """PEP 508 / packaging accept the clause list in one layer of
        parentheses — 'pkg (>=1.0)', 'pkg(>=1.0,<2.0)' and 'pkg()'
        were previously errors."""
        result = run_compare(
            "pkg (>=1.0,<2.0)\nother(>=1.0)\nempty()\n", "pkg==1.5\n"
        )
        rows = {row["name"]: row for row in result["declared"]}
        self.assertEqual(len(result["errors"]), 0)
        self.assertEqual(rows["pkg"]["spec"], ">=1.0,<2.0")
        self.assertTrue(rows["pkg"]["satisfied"])
        self.assertEqual(rows["empty"]["clauses"], [])
        for bad in ["pkg ((>=1.0))", "pkg (>=1.0) extra", "pkg (>=1.0"]:
            errors = run_compare(f"{bad}\n", "pkg==1.0\n")["errors"]
            self.assertEqual(len(errors), 1, bad)

    def test_comma_rule_matches_packaging(self):
        """Exactly one trailing comma is allowed; leading and doubled
        commas are errors, like packaging.requirements.Requirement."""
        for ok in ["pkg==1.0,", "pkg>=1.0,<2.0,", "pkg==1.0 ,"]:
            result = run_compare(f"{ok}\n", "pkg==1.5\n")
            self.assertEqual(len(result["errors"]), 0, ok)
        for bad in ["pkg,==1.0", "pkg==1.0,,", "pkg>=1.0,,<2.0"]:
            result = run_compare(f"{bad}\n", "pkg==1.5\n")
            self.assertEqual(len(result["errors"]), 1, bad)
            self.assertIn(
                "trailing comma", result["errors"][0]["reason"], bad
            )

    def test_freeze_wildcard_is_an_error(self):
        """``==X.*`` is requirements-file syntax pip freeze never
        emits; it previously parsed as a pin carrying the junk
        version 'X.*'."""
        result = run_installed("pkg==1.0.*\n")
        self.assertEqual(result["count"], 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("wildcard", result["errors"][0]["reason"])
        # surfaced as environment errors in compare mode too
        compared = run_compare("pkg==1.0\n", "pkg==1.0.*\n")
        self.assertEqual(len(compared["errors_environment"]), 1)
        # === keeps arbitrary operands (legacy pins) — stays a pin
        legacy = run_installed("pkg===1.0.*\n")
        self.assertEqual(legacy["count"], 1)

    def test_caps_are_real_overridable_fields(self):
        """The documented caps were dead attributes (assignment used
        to raise 'object has no field'); they are real fields now."""
        tool = FreezeDiffTool()
        self.assertIn("max_lines", type(tool).model_fields)
        self.assertIn("max_line_chars", type(tool).model_fields)
        self.assertIn("max_text_chars", type(tool).model_fields)
        tool.max_lines = 3  # attribute override works
        with self.assertRaises(ValueError):
            tool.execute(mode="installed", freeze="a==1\nb==2\nc==3\nd==4\n")
        self.assertEqual(
            tool.execute(mode="installed", freeze="a==1\nb==2\nc==3\n")[
                "count"
            ],
            3,
        )
        strict = FreezeDiffTool(max_line_chars=12)  # constructor override
        with self.assertRaises(ValueError):
            strict.execute(mode="installed", freeze="a==1.0.0.0.0.0\n")
        with self.assertRaises(Exception):
            FreezeDiffTool(max_lines=0)  # caps must be positive

    def test_error_messages_bounded(self):
        """Wrong-typed parameters used to be echoed whole in the
        ValueError message — a 50k-element list became megabytes."""
        with self.assertRaises(ValueError) as ctx:
            FreezeDiffTool().execute(mode="compare", requirements=[0] * 50000)
        self.assertLess(len(str(ctx.exception)), 300)
        with self.assertRaises(ValueError) as ctx:
            run_compare("a==1\n", "a==1\n", exempt=["ok", ("x" * 5000,)])
        self.assertLess(len(str(ctx.exception)), 300)

    def test_snapshot_identical_junk_is_unchanged(self):
        """Identical raw version strings count as unchanged without
        a parse (no ordering decision is involved)."""
        result = run_snapshot("p==1.0$\n", "p==1.0$\n")
        self.assertEqual(result["unchanged_count"], 1)
        self.assertEqual(result["unparsed"], [])

    @unittest.skipUnless(
        PACKAGING_AVAILABLE, "the packaging distribution is not installed"
    )
    def test_requirement_verdicts_vs_packaging_oracle(self):
        """Tool parse verdicts must agree with
        packaging.requirements.Requirement accept/reject on PEP 508
        shapes (path-shaped lines are the documented
        requirements-file extension and stay out of this corpus)."""
        accepted = [
            "pkg", "pkg==1.0", "pkg[a]", "pkg[ a , b ]==1.0",
            "pkg[a-b]==1.0", "pkg>=1.0,<2.0", "pkg~=1.2.3",
            "pkg!=1.2.*", "pkg===lol", "pkg@ file:///x",
            "pkg @ https://e/x.whl", "pkg==1.0+local", "pkg==1!1.0",
            "pkg (>=1.0)", "pkg(>=1.0,<2.0)", "pkg()", "pkg[]",
            "pkg==1.0, ",
            'pkg==1.0 ; python_version >= "3.8"',
        ]
        rejected = [
            "pkg==1.0 ==2.0", "pkg >=1.0<2.0", "pkg==", "pkg[a",
            "pkg[,]", "pkg[a][]", "pkg..==1.0", "pkg==1.0 --hash=sha256:x",
            "pkg 1.0", "==1.0", "pkg==\uff11.\uff10", "pkg,==1.0",
            "pkg==1.0,,", "pkg ((>=1.0))", "pkg (>=1.0) extra",
        ]
        from packaging.requirements import Requirement as PkgRequirement

        def tool_errors(line):
            return bool(run_compare(f"{line}\n", "pkg==1.0\n")["errors"])

        for line in accepted:
            PkgRequirement(line)  # must not raise
            self.assertFalse(tool_errors(line), line)
        for line in rejected:
            with self.assertRaises(Exception, msg=line):
                PkgRequirement(line)
            self.assertTrue(tool_errors(line), line)


# ------------------------------------------------------------------ #
# export sanity
# ------------------------------------------------------------------ #

class ExportSanity(unittest.TestCase):
    """The package export and the direct import are the same class."""

    def test_same_class(self):
        self.assertIs(FreezeDiffTool, DirectFreezeDiffTool)
        self.assertEqual(FreezeDiffTool().name, "freeze_diff_tool")

    def test_modes(self):
        self.assertEqual(
            FreezeDiffTool.MODES,
            ("installed", "compare", "snapshot_diff"),
        )


if __name__ == "__main__":
    unittest.main()
