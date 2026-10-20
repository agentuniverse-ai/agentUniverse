#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_changelog_parser_tool.py

"""Offline unit tests for ChangelogParserTool.

The tool is built purely on the standard library (re, datetime,
functools) and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: the main fixture is a
Keep-a-Changelog style document exercising all six canonical sections
plus a free-form one, an Unreleased section, ISO dates, yanked
markers, link-reference definitions and nested bullets, and the
expected parse result is written out in full as a literal ground
truth. Ordering rules are pinned by dedicated documents whose dates
and version numbers deliberately disagree with the document order,
and SemVer precedence is pinned through the public ``between`` mode
using the precedence chain from the SemVer 2.0.0 specification.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import ChangelogParserTool
from agentuniverse.agent.action.tool.common_tool.changelog_parser_tool import (
    ChangelogParserTool as DirectChangelogParserTool,
)

# --------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------- #

# A Keep-a-Changelog style document: preamble with inline links, an
# Unreleased section, five releases (one yanked in both the heading
# and the link title), all six canonical sections plus a free-form
# "Internal" section, nested bullets, a non-release "##" appendix and
# link-reference definitions with mixed key casing.
KEEP_A_CHANGELOG_MD = """\
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Icon set for the export dialog

## [1.1.0] - 2018-03-21

### Added

- Arabic translation (#96)
- `vh` and `vw` units to the size parser (#101)

### Changed

- Switched to a new documentation engine (#99)

### Deprecated

- The `--verbose` flag; use `--log-level=info` instead

### Removed

- The `--silent` flag (#110)

### Fixed

- Russian pluralization for day and month names (#95)

### Security

- Bumped `libssl` to 1.1.1k to address CVE-2021-3450

### Internal

- Migrated the CI pipeline to a new runner image

## [1.0.1] - 2018-02-12 [YANKED]

### Fixed

- Crash when the input file is empty (#88)

## [1.0.0] - 2017-06-20

### Added

- Initial stable release
  - Parsing of `Keep a Changelog` documents
    - Version headings
    - Link reference definitions
  - The `Release` helper API

### Changed

- Renamed `parse_changelog` to `parse`

## [0.9.0] - 2017-05-15

### Added

- First public beta

## Appendix

Nothing in this appendix section belongs to a release.

[unreleased]: https://example.com/compare/v1.1.0...HEAD
[1.1.0]: https://example.com/compare/v1.0.1...v1.1.0
[1.0.1]: https://example.com/compare/v1.0.0...v1.0.1 (YANKED)
[1.0.0]: https://example.com/compare/v0.9.0...v1.0.0
"""

# Full literal ground truth for KEEP_A_CHANGELOG_MD.
EXPECTED_MAIN_RELEASES = [
    {
        "version": "Unreleased",
        "date": None,
        "yanked": False,
        "latest": True,
        "url": "https://example.com/compare/v1.1.0...HEAD",
        "sections": {
            "Added": [
                {"text": "Icon set for the export dialog", "indent": 0},
            ],
        },
    },
    {
        "version": "1.1.0",
        "date": "2018-03-21",
        "yanked": False,
        "latest": False,
        "url": "https://example.com/compare/v1.0.1...v1.1.0",
        "sections": {
            "Added": [
                {"text": "Arabic translation (#96)", "indent": 0},
                {"text": "`vh` and `vw` units to the size parser (#101)", "indent": 0},
            ],
            "Changed": [
                {"text": "Switched to a new documentation engine (#99)", "indent": 0},
            ],
            "Deprecated": [
                {"text": "The `--verbose` flag; use `--log-level=info` instead", "indent": 0},
            ],
            "Removed": [
                {"text": "The `--silent` flag (#110)", "indent": 0},
            ],
            "Fixed": [
                {"text": "Russian pluralization for day and month names (#95)", "indent": 0},
            ],
            "Security": [
                {"text": "Bumped `libssl` to 1.1.1k to address CVE-2021-3450", "indent": 0},
            ],
            "Internal": [
                {"text": "Migrated the CI pipeline to a new runner image", "indent": 0},
            ],
        },
    },
    {
        "version": "1.0.1",
        "date": "2018-02-12",
        "yanked": True,
        "latest": False,
        "url": "https://example.com/compare/v1.0.0...v1.0.1",
        "sections": {
            "Fixed": [
                {"text": "Crash when the input file is empty (#88)", "indent": 0},
            ],
        },
    },
    {
        "version": "1.0.0",
        "date": "2017-06-20",
        "yanked": False,
        "latest": False,
        "url": "https://example.com/compare/v0.9.0...v1.0.0",
        "sections": {
            "Added": [
                {"text": "Initial stable release", "indent": 0},
                {"text": "Parsing of `Keep a Changelog` documents", "indent": 1},
                {"text": "Version headings", "indent": 2},
                {"text": "Link reference definitions", "indent": 2},
                {"text": "The `Release` helper API", "indent": 1},
            ],
            "Changed": [
                {"text": "Renamed `parse_changelog` to `parse`", "indent": 0},
            ],
        },
    },
    {
        "version": "0.9.0",
        "date": "2017-05-15",
        "yanked": False,
        "latest": False,
        "url": None,
        "sections": {
            "Added": [
                {"text": "First public beta", "indent": 0},
            ],
        },
    },
]

# Document order disagrees with both the date order and the semver
# order, pinning the "document order is authoritative" rule for the
# latest flag / latest mode.
OUT_OF_ORDER_MD = """\
# Changelog

## [1.1.0] - 2024-01-01
### Added
- Oldest date listed first

## [1.3.0] - 2024-03-03
### Added
- Highest version listed in the middle

## [1.2.0] - 2024-05-05
### Added
- Newest date listed last
"""

# The SemVer 2.0.0 precedence chain (alpha < alpha.1 < alpha.beta <
# beta < beta.2 < beta.11 < rc.1 < release), listed in a shuffled
# document order so range filtering must rely on semver comparison.
SEMVER_CHAIN_MD = """\
# Changelog

## [1.0.0]
### Added
- Final release

## [1.0.0-rc.1]
### Added
- Release candidate

## [1.0.0-beta.11]
### Fixed
- Eleventh beta fix

## [1.0.0-beta.2]
### Fixed
- Second beta fix

## [1.0.0-beta]
### Added
- Beta program

## [1.0.0-alpha.beta]
### Added
- Alpha with a prerelease of its own

## [1.0.0-alpha.1]
### Fixed
- First alpha hotfix

## [1.0.0-alpha]
### Added
- First alpha
"""

CHAIN_DOC_ORDER = [
    "1.0.0",
    "1.0.0-rc.1",
    "1.0.0-beta.11",
    "1.0.0-beta.2",
    "1.0.0-beta",
    "1.0.0-alpha.beta",
    "1.0.0-alpha.1",
    "1.0.0-alpha",
]


class ChangelogParserToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib ChangelogParserTool."""

    def setUp(self) -> None:
        self.tool = ChangelogParserTool()

    # ------------------------------------------------------------------ #
    # parse mode — full-document ground truth
    # ------------------------------------------------------------------ #

    def test_parse_full_keep_a_changelog_document(self) -> None:
        result = self.tool.execute(mode="parse", text=KEEP_A_CHANGELOG_MD)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "release_count": 5,
                "releases": EXPECTED_MAIN_RELEASES,
            },
        )

    def test_parse_latest_flag_on_first_listed_release(self) -> None:
        releases = self.tool.execute(mode="parse", text=KEEP_A_CHANGELOG_MD)["releases"]
        flags = [release["latest"] for release in releases]
        self.assertEqual(flags, [True, False, False, False, False])

    def test_parse_section_names_preserved_in_document_order(self) -> None:
        releases = self.tool.execute(mode="parse", text=KEEP_A_CHANGELOG_MD)["releases"]
        self.assertEqual(
            list(releases[1]["sections"]),
            [
                "Added",
                "Changed",
                "Deprecated",
                "Removed",
                "Fixed",
                "Security",
                "Internal",
            ],
        )

    def test_parse_nested_bullets_flattened_with_indent(self) -> None:
        releases = self.tool.execute(mode="parse", text=KEEP_A_CHANGELOG_MD)["releases"]
        added = releases[3]["sections"]["Added"]
        self.assertEqual(
            added,
            [
                {"text": "Initial stable release", "indent": 0},
                {"text": "Parsing of `Keep a Changelog` documents", "indent": 1},
                {"text": "Version headings", "indent": 2},
                {"text": "Link reference definitions", "indent": 2},
                {"text": "The `Release` helper API", "indent": 1},
            ],
        )

    def test_parse_unreleased_normalized_and_linked(self) -> None:
        first = self.tool.execute(mode="parse", text=KEEP_A_CHANGELOG_MD)["releases"][0]
        self.assertEqual(first["version"], "Unreleased")
        self.assertIsNone(first["date"])
        self.assertEqual(
            first["url"], "https://example.com/compare/v1.1.0...HEAD"
        )

    def test_parse_yanked_from_heading_and_link_title(self) -> None:
        releases = self.tool.execute(mode="parse", text=KEEP_A_CHANGELOG_MD)["releases"]
        yanked = {release["version"]: release["yanked"] for release in releases}
        self.assertEqual(
            yanked,
            {"Unreleased": False, "1.1.0": False, "1.0.1": True, "1.0.0": False, "0.9.0": False},
        )

    def test_parse_release_without_link_definition_has_no_url(self) -> None:
        releases = self.tool.execute(mode="parse", text=KEEP_A_CHANGELOG_MD)["releases"]
        self.assertIsNone(releases[4]["url"])

    def test_parse_preamble_and_non_release_headings_ignored(self) -> None:
        # The preamble prose, the "## Appendix" heading and the text
        # after it produce no entries anywhere in the result.
        result = self.tool.execute(mode="parse", text=KEEP_A_CHANGELOG_MD)
        self.assertNotIn("Appendix", str(result))
        self.assertNotIn("documented in this file", str(result))
        self.assertNotIn("belongs to a release", str(result))
        self.assertEqual(result["release_count"], 5)

    # ------------------------------------------------------------------ #
    # parse mode — heading grammar
    # ------------------------------------------------------------------ #

    def test_heading_styles_bracket_bare_and_v_prefix_equivalent(self) -> None:
        for heading in ("## [1.2.3] - 2024-01-15", "## 1.2.3 - 2024-01-15", "## v1.2.3 - 2024-01-15"):
            with self.subTest(heading=heading):
                text = f"{heading}\n\n### Added\n\n- Entry\n"
                release = self.tool.execute(mode="parse", text=text)["releases"][0]
                self.assertEqual(release["version"], "1.2.3")
                self.assertEqual(release["date"], "2024-01-15")

    def test_heading_v_prefix_stripped_in_brackets_too(self) -> None:
        release = self.tool.execute(
            mode="parse", text="## [v1.2.3] - 2024-01-15\n"
        )["releases"][0]
        self.assertEqual(release["version"], "1.2.3")

    def test_heading_prerelease_and_build_versions(self) -> None:
        release = self.tool.execute(
            mode="parse", text="## [1.2.3-rc.1+build.5] - 2024-01-05\n"
        )["releases"][0]
        self.assertEqual(release["version"], "1.2.3-rc.1+build.5")
        self.assertEqual(release["date"], "2024-01-05")

    def test_heading_unreleased_case_insensitive(self) -> None:
        for heading in ("## [Unreleased]", "## [unreleased]", "## [UNRELEASED]"):
            with self.subTest(heading=heading):
                release = self.tool.execute(mode="parse", text=f"{heading}\n")["releases"][0]
                self.assertEqual(release["version"], "Unreleased")

    def test_heading_date_optional(self) -> None:
        release = self.tool.execute(mode="parse", text="## [1.2.3]\n")["releases"][0]
        self.assertIsNone(release["date"])

    def test_non_semver_heading_is_not_a_release(self) -> None:
        text = "# Changelog\n\n## [1.2]\n\n### Added\n\n- Lost\n\n## [1.2.3]\n\n### Added\n\n- Kept\n"
        releases = self.tool.execute(mode="parse", text=text)["releases"]
        self.assertEqual([release["version"] for release in releases], ["1.2.3"])

    def test_non_release_h2_terminates_current_release(self) -> None:
        text = (
            "## [1.0.0] - 2024-01-01\n\n### Added\n\n- Belongs\n\n"
            "## Notes\n\n- Stray\n\n### Fixed\n\n- Also stray\n"
        )
        releases = self.tool.execute(mode="parse", text=text)["releases"]
        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0]["sections"], {"Added": [{"text": "Belongs", "indent": 0}]})

    # ------------------------------------------------------------------ #
    # parse mode — sections and entries
    # ------------------------------------------------------------------ #

    def test_section_without_entries_kept_as_empty_list(self) -> None:
        text = "## [1.0.0] - 2024-01-01\n\n### Added\n\n### Fixed\n\n- Fix\n"
        sections = self.tool.execute(mode="parse", text=text)["releases"][0]["sections"]
        self.assertEqual(sections, {"Added": [], "Fixed": [{"text": "Fix", "indent": 0}]})

    def test_repeated_section_headings_merge(self) -> None:
        text = (
            "## [1.0.0]\n\n### Added\n\n- First\n\n"
            "### Fixed\n\n- Fix\n\n### Added\n\n- Second\n"
        )
        sections = self.tool.execute(mode="parse", text=text)["releases"][0]["sections"]
        self.assertEqual(
            sections,
            {
                "Added": [
                    {"text": "First", "indent": 0},
                    {"text": "Second", "indent": 0},
                ],
                "Fixed": [{"text": "Fix", "indent": 0}],
            },
        )

    def test_section_name_case_preserved(self) -> None:
        text = "## [1.0.0]\n\n### added\n\n- Entry\n"
        sections = self.tool.execute(mode="parse", text=text)["releases"][0]["sections"]
        self.assertEqual(list(sections), ["added"])

    def test_bullets_before_first_section_ignored(self) -> None:
        text = "## [1.0.0] - 2024-01-01\n\n- Stray bullet\n\n### Added\n\n- Real\n"
        sections = self.tool.execute(mode="parse", text=text)["releases"][0]["sections"]
        self.assertEqual(sections, {"Added": [{"text": "Real", "indent": 0}]})

    def test_prose_inside_section_ignored(self) -> None:
        text = "## [1.0.0]\n\n### Added\n\nSome prose line.\n- Entry\n\nMore prose.\n"
        sections = self.tool.execute(mode="parse", text=text)["releases"][0]["sections"]
        self.assertEqual(sections, {"Added": [{"text": "Entry", "indent": 0}]})

    def test_bullet_markers_dash_star_plus(self) -> None:
        text = "## [1.0.0]\n\n### Added\n\n- Dash\n* Star\n+ Plus\n"
        sections = self.tool.execute(mode="parse", text=text)["releases"][0]["sections"]
        self.assertEqual(
            sections["Added"],
            [
                {"text": "Dash", "indent": 0},
                {"text": "Star", "indent": 0},
                {"text": "Plus", "indent": 0},
            ],
        )

    def test_indent_level_is_leading_whitespace_over_two(self) -> None:
        text = (
            "## [1.0.0]\n\n### Added\n\n"
            "- Level zero\n"
            "  - Level one\n"
            "    - Level two\n"
            "   - Three spaces is still level one\n"
            "        - Eight spaces is level four\n"
        )
        entries = self.tool.execute(mode="parse", text=text)["releases"][0]["sections"]["Added"]
        self.assertEqual(
            [entry["indent"] for entry in entries], [0, 1, 2, 1, 4]
        )
        self.assertEqual(
            [entry["text"] for entry in entries],
            [
                "Level zero",
                "Level one",
                "Level two",
                "Three spaces is still level one",
                "Eight spaces is level four",
            ],
        )

    def test_horizontal_rules_are_not_entries(self) -> None:
        text = "## [1.0.0]\n\n### Added\n\n---\n\n- Entry\n\n***\n"
        sections = self.tool.execute(mode="parse", text=text)["releases"][0]["sections"]
        self.assertEqual(sections, {"Added": [{"text": "Entry", "indent": 0}]})

    def test_spaced_horizontal_rules_are_not_entries(self) -> None:
        # CommonMark thematic breaks may separate the markers with
        # spaces ("* * *", "- - -", "  ___  "); they must not be
        # mistaken for bullet entries with marker-shaped text.
        text = (
            "## [1.0.0]\n\n### Added\n\n- Entry\n\n* * *\n\n"
            "## [0.9.0]\n\n### Added\n\n- Older\n\n- - -\n\n### Fixed\n\n- Fix\n\n___\n"
        )
        releases = self.tool.execute(mode="parse", text=text)["releases"]
        self.assertEqual(
            releases[0]["sections"], {"Added": [{"text": "Entry", "indent": 0}]}
        )
        self.assertEqual(
            releases[1]["sections"],
            {
                "Added": [{"text": "Older", "indent": 0}],
                "Fixed": [{"text": "Fix", "indent": 0}],
            },
        )

    def test_hyphen_bullet_with_marker_shaped_text_stays_a_bullet(self) -> None:
        # "- -" / "- - x" carry fewer than three markers and remain
        # ordinary bullets whose text happens to contain dashes.
        text = "## [1.0.0]\n\n### Added\n\n- -\n- - x\n"
        entries = self.tool.execute(mode="parse", text=text)["releases"][0]["sections"]["Added"]
        self.assertEqual(
            entries,
            [{"text": "-", "indent": 0}, {"text": "- x", "indent": 0}],
        )

    def test_crlf_line_endings(self) -> None:
        text = "## [1.0.0] - 2024-01-15\r\n\r\n### Added\r\n\r\n- Entry one\r\n  - Nested\r\n"
        release = self.tool.execute(mode="parse", text=text)["releases"][0]
        self.assertEqual(release["date"], "2024-01-15")
        self.assertEqual(
            release["sections"]["Added"],
            [{"text": "Entry one", "indent": 0}, {"text": "Nested", "indent": 1}],
        )

    # ------------------------------------------------------------------ #
    # yanked / link-reference definitions
    # ------------------------------------------------------------------ #

    def test_yanked_marker_in_heading_case_insensitive(self) -> None:
        for rest in ("[YANKED]", "[yanked]"):
            with self.subTest(rest=rest):
                text = f"## [1.0.0] - 2024-01-01 {rest}\n"
                release = self.tool.execute(mode="parse", text=text)["releases"][0]
                self.assertTrue(release["yanked"])

    def test_yanked_via_link_title_only(self) -> None:
        text = "## [1.0.0] - 2024-01-01\n\n### Fixed\n\n- x\n\n[1.0.0]: https://example.com/v1.0.0 (YANKED)\n"
        release = self.tool.execute(mode="parse", text=text)["releases"][0]
        self.assertTrue(release["yanked"])
        self.assertEqual(release["url"], "https://example.com/v1.0.0")

    def test_link_definition_without_title(self) -> None:
        text = "## [1.0.0]\n\n[1.0.0]: https://example.com/compare/v0.9.0...v1.0.0\n"
        release = self.tool.execute(mode="parse", text=text)["releases"][0]
        self.assertEqual(release["url"], "https://example.com/compare/v0.9.0...v1.0.0")
        self.assertFalse(release["yanked"])

    def test_unmatched_link_definition_ignored(self) -> None:
        text = "## [1.0.0]\n\n[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/\n\n[mystery]: https://example.com\n"
        release = self.tool.execute(mode="parse", text=text)["releases"][0]
        self.assertIsNone(release["url"])
        self.assertEqual(release["version"], "1.0.0")

    def test_duplicate_link_definition_first_wins(self) -> None:
        text = "## [1.0.0]\n\n[1.0.0]: https://first.example.com\n[1.0.0]: https://second.example.com\n"
        release = self.tool.execute(mode="parse", text=text)["releases"][0]
        self.assertEqual(release["url"], "https://first.example.com")

    # ------------------------------------------------------------------ #
    # latest mode
    # ------------------------------------------------------------------ #

    def test_latest_returns_first_semver_release(self) -> None:
        result = self.tool.execute(mode="latest", text=KEEP_A_CHANGELOG_MD)
        self.assertEqual(result, {"mode": "latest", "release": EXPECTED_MAIN_RELEASES[1]})

    def test_latest_document_order_beats_date_and_semver_order(self) -> None:
        # Dates are ascending (newest listed last) and the highest
        # version is listed in the middle: the first listed release
        # (1.1.0) must still win per the document-order rule.
        releases = self.tool.execute(mode="parse", text=OUT_OF_ORDER_MD)["releases"]
        self.assertEqual([r["version"] for r in releases], ["1.1.0", "1.3.0", "1.2.0"])
        self.assertEqual([r["date"] for r in releases], ["2024-01-01", "2024-03-03", "2024-05-05"])
        self.assertTrue(releases[0]["latest"])
        result = self.tool.execute(mode="latest", text=OUT_OF_ORDER_MD)
        self.assertEqual(result["release"]["version"], "1.1.0")

    def test_latest_on_semver_chain_returns_first_listed(self) -> None:
        result = self.tool.execute(mode="latest", text=SEMVER_CHAIN_MD)
        self.assertEqual(result["release"]["version"], "1.0.0")

    def test_latest_without_semver_releases(self) -> None:
        text = "## [Unreleased]\n\n### Added\n\n- Something\n"
        result = self.tool.execute(mode="latest", text=text)
        self.assertEqual(result["mode"], "latest")
        self.assertEqual(result["error"]["type"], "no_semver_releases")
        self.assertIn("Unreleased", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # between mode
    # ------------------------------------------------------------------ #

    def test_between_on_main_fixture_boundaries(self) -> None:
        cases = [
            ("0.9.0", "1.1.0", ["1.1.0", "1.0.1", "1.0.0"]),
            ("1.0.0", "1.0.1", ["1.0.1"]),
            ("1.0.1", "1.1.0", ["1.1.0"]),
            ("0.1.0", "0.5.0", []),
            ("0.1.0", "9.9.9", ["1.1.0", "1.0.1", "1.0.0", "0.9.0"]),
        ]
        for from_version, to_version, expected in cases:
            with self.subTest(from_version=from_version, to_version=to_version):
                result = self.tool.execute(
                    mode="between",
                    text=KEEP_A_CHANGELOG_MD,
                    from_version=from_version,
                    to_version=to_version,
                )
                self.assertEqual(result["mode"], "between")
                self.assertEqual(result["from_version"], from_version)
                self.assertEqual(result["to_version"], to_version)
                self.assertEqual(result["release_count"], len(expected))
                self.assertEqual(
                    [release["version"] for release in result["releases"]], expected
                )
                self.assertNotIn("Unreleased", str(expected))

    def test_between_excludes_unreleased(self) -> None:
        result = self.tool.execute(
            mode="between",
            text=KEEP_A_CHANGELOG_MD,
            from_version="0.1.0",
            to_version="9.9.9",
        )
        versions = [release["version"] for release in result["releases"]]
        self.assertNotIn("Unreleased", versions)
        self.assertEqual(versions, ["1.1.0", "1.0.1", "1.0.0", "0.9.0"])

    def test_between_preserves_document_order(self) -> None:
        result = self.tool.execute(
            mode="between",
            text=SEMVER_CHAIN_MD,
            from_version="1.0.0-alpha",
            to_version="1.0.0-rc.1",
        )
        self.assertEqual(
            [release["version"] for release in result["releases"]],
            [
                "1.0.0-rc.1",
                "1.0.0-beta.11",
                "1.0.0-beta.2",
                "1.0.0-beta",
                "1.0.0-alpha.beta",
                "1.0.0-alpha.1",
            ],
        )

    def test_between_semver_precedence_numeric_prerelease_identifiers(self) -> None:
        # beta.11 must compare greater than beta.2 (numeric, not
        # lexicographic), so it lands inside (beta.2, rc.1].
        result = self.tool.execute(
            mode="between",
            text=SEMVER_CHAIN_MD,
            from_version="1.0.0-beta.2",
            to_version="1.0.0-rc.1",
        )
        self.assertEqual(
            [release["version"] for release in result["releases"]],
            ["1.0.0-rc.1", "1.0.0-beta.11"],
        )

    def test_between_semver_precedence_prerelease_below_release(self) -> None:
        result = self.tool.execute(
            mode="between",
            text=SEMVER_CHAIN_MD,
            from_version="1.0.0-rc.1",
            to_version="1.0.0",
        )
        self.assertEqual(
            [release["version"] for release in result["releases"]], ["1.0.0"]
        )

    def test_between_accepts_v_prefix_and_normalizes(self) -> None:
        result = self.tool.execute(
            mode="between",
            text=KEEP_A_CHANGELOG_MD,
            from_version="v0.9.0",
            to_version="v1.0.1",
        )
        self.assertEqual(result["from_version"], "0.9.0")
        self.assertEqual(result["to_version"], "1.0.1")
        self.assertEqual(
            [release["version"] for release in result["releases"]], ["1.0.1", "1.0.0"]
        )

    def test_between_empty_range_is_not_an_error(self) -> None:
        result = self.tool.execute(
            mode="between",
            text=SEMVER_CHAIN_MD,
            from_version="1.0.0",
            to_version="2.0.0",
        )
        self.assertEqual(result["release_count"], 0)
        self.assertEqual(result["releases"], [])

    # ------------------------------------------------------------------ #
    # Content-level error payloads
    # ------------------------------------------------------------------ #

    def test_no_release_headings(self) -> None:
        text = "# Notes\n\nJust some markdown text.\n\n## Section\n\n- bullet\n"
        for mode, kwargs in (
            ("parse", {}),
            ("latest", {}),
            ("between", {"from_version": "1.0.0", "to_version": "2.0.0"}),
        ):
            with self.subTest(mode=mode):
                result = self.tool.execute(mode=mode, text=text, **kwargs)
                self.assertEqual(result["mode"], mode)
                self.assertEqual(result["error"]["type"], "no_releases")
                self.assertIn("## [1.2.3]", result["error"]["message"])

    def test_invalid_calendar_date(self) -> None:
        for bad_date in ("2024-02-30", "2023-02-29"):
            with self.subTest(bad_date=bad_date):
                result = self.tool.execute(
                    mode="parse", text=f"## [1.0.0] - {bad_date}\n"
                )
                self.assertEqual(result["mode"], "parse")
                self.assertEqual(result["error"]["type"], "invalid_date")
                self.assertIn(bad_date, result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="summarize", text="## [1.0.0]\n")
        self.assert_invalid(mode=None, text="## [1.0.0]\n")
        self.assert_invalid(mode=123, text="## [1.0.0]\n")

    def test_invalid_text(self) -> None:
        for bad in (None, "", 123, True, b"## [1.0.0]", ["## [1.0.0]"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", text=bad)
                self.assert_invalid(mode="latest", text=bad)

    def test_text_length_limit(self) -> None:
        tail = "\n\n## [1.0.0] - 2020-01-01\n\n### Added\n\n- entry\n"
        oversized = "x" * (100_001 - len(tail))
        self.assert_invalid(mode="parse", text=oversized + tail)
        ok = "x" * (100_000 - len(tail)) + tail
        self.assertEqual(len(ok), 100_000)
        result = self.tool.execute(mode="parse", text=ok)
        self.assertEqual(result["release_count"], 1)

    def test_between_requires_both_versions(self) -> None:
        self.assert_invalid(mode="between", text="## [1.0.0]\n", to_version="2.0.0")
        self.assert_invalid(mode="between", text="## [1.0.0]\n", from_version="1.0.0")
        self.assert_invalid(mode="between", text="## [1.0.0]\n")
        self.assert_invalid(mode="between", text="## [1.0.0]\n", from_version="", to_version="2.0.0")

    def test_between_rejects_non_string_versions(self) -> None:
        for bad in (123, True, ["1.0.0"]):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="between", text="## [1.0.0]\n", from_version=bad, to_version="2.0.0"
                )
                self.assert_invalid(
                    mode="between", text="## [1.0.0]\n", from_version="1.0.0", to_version=bad
                )

    def test_between_rejects_invalid_semver(self) -> None:
        for bad in ("1.2", "1.2.3.4", "abc", "01.02.03", "1.2.3_1", "v"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="between", text="## [1.0.0]\n", from_version=bad, to_version="2.0.0"
                )
                self.assert_invalid(
                    mode="between", text="## [1.0.0]\n", from_version="1.0.0", to_version=bad
                )

    def test_between_rejects_empty_or_reversed_range(self) -> None:
        self.assert_invalid(
            mode="between", text="## [1.0.0]\n", from_version="1.0.0", to_version="1.0.0"
        )
        self.assert_invalid(
            mode="between", text="## [1.0.0]\n", from_version="2.0.0", to_version="1.0.0"
        )
        self.assert_invalid(
            mode="between", text="## [1.0.0]\n", from_version="1.0.0", to_version="1.0.0-rc.1"
        )

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectChangelogParserTool, ChangelogParserTool)
        self.assertEqual(self.tool.name, "changelog_parser_tool")
        self.assertIn("Keep-a-Changelog", self.tool.description)
        for mode in ("parse", "latest", "between"):
            self.assertIn(mode, self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("ChangelogParserTool", __all__)


if __name__ == "__main__":
    unittest.main()
