#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_strftime_lint_tool.py

"""Offline unit tests for StrftimeLintTool.

The tool is built purely on the standard library and never touches
the network, so this suite runs fully offline. Every knowledge-base
claim is checked against ground truth derived independently of the
tool's implementation — real ``datetime.strftime`` /
``datetime.strptime`` behavior on this platform:

* the 200-seed oracle runs every seeded format string through all
  four modes and re-derives the answers with the real datetime
  machinery: each directive the tool marks ``parsed_by_strptime``
  must genuinely parse when rendered at the fixed reference
  datetime, each directive marked unparseable must genuinely be
  rejected, every ``example_output`` must equal the real
  ``strftime`` rendering, and every ``roundtrip_check`` verdict
  must match an independent recomputation of
  ``strptime(strftime(REFERENCE, fmt), fmt)``;
* lint statics (no error findings ⇒ the format really renders on
  POSIX), the full lint rule matrix, ISO-trio context sensitivity,
  and a complete validation error matrix are asserted exactly.
"""

import random
import re
import sys
import unittest
from datetime import datetime, timezone

from agentuniverse.agent.action.tool.common_tool import StrftimeLintTool
from agentuniverse.agent.action.tool.common_tool.strftime_lint_tool import (
    DIRECTIVES,
    REFERENCE_DATETIME,
    StrftimeLintTool as DirectStrftimeLintTool,
)

FIX = REFERENCE_DATETIME
# The tool was built against CPython 3.11; the oracle below is valid
# wherever the runtime's datetime behaves the same way.
POSIX = sys.platform != "win32"


def findings(result):
    """The ordered list of finding (code, severity, line) triples."""
    return [(f["code"], f["severity"], f["line"]) for f in result["findings"]]


def codes_of(result):
    """The ordered list of finding codes."""
    return [f["code"] for f in result["findings"]]


# --------------------------------------------------------------------- #
# Deterministic 200-seed corpus
# --------------------------------------------------------------------- #
def seeded_format_strings():
    """Exactly 200 distinct, deterministically generated format strings."""
    seeds = []
    # 1. Every base directive alone (includes %%), plus the colon forms.
    for letter in sorted(DIRECTIVES):
        seeds.append("%" + letter)
    seeds.extend(["%:z", "%::z", "%:::z", "%::::z"])
    # 2. Flag / width / modifier forms.
    seeds.extend([
        "%-d", "%_m", "%0H", "%^a", "%#Z", "%3Y", "%Ec", "%Od",
        "%10S", "%-15e", "%05I", "%0e",
    ])
    # 3. Unknown directives and dangling forms.
    seeds.extend(["%q", "%i", "%o", "%Q", "%E", "%5", "% ", "%:", "%3%"])
    # 4. Structured real-world and pitfall formats.
    seeds.extend([
        "%Y-%m-%d", "%H:%M:%S", "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f%z", "%G-%V-%u", "%G-%V-%a", "%Y-%U-%w",
        "%Y-%W-%w", "%Y-%j", "%j", "%U", "%W", "%c", "%x", "%X", "%Z",
        "%z", "%s", "%f", "%A, %B %d %Y", "%p %I", "%d/%m/%y %I:%M %p",
        "abc%", "%%", "\u5e74-%Y", "", "Y-m-d", "%n", "%t",
        "%Y%n%m%t%d", "%Y年%m月%d日\n%H时",
    ])
    # 5. Random (seeded) combinations to fill up to exactly 200.
    rng = random.Random(252)
    pool = sorted({"%" + letter for letter in DIRECTIVES}
                  | {"%-d", "%_m", "%0H", "%^a", "%#Z", "%3Y", "%Ec",
                     "%:z", "%q", "%i"})
    joiners = ["-", ":", "/", "T", " ", "_", ", ", "", " | "]
    seeds = list(dict.fromkeys(seeds))  # drop curated duplicates
    seen = set(seeds)
    while len(seeds) < 200:
        count = rng.randint(2, 5)
        fmt = rng.choice(joiners).join(
            rng.choice(pool) for _ in range(count)
        )
        if fmt not in seen:
            seen.add(fmt)
            seeds.append(fmt)
    assert len(seeds) == 200
    return seeds


SEEDS = seeded_format_strings()


class LintModeTest(unittest.TestCase):
    """The static lint rule matrix."""

    def setUp(self):
        self.tool = StrftimeLintTool()

    def test_clean_c89_formats_have_no_findings(self):
        for fmt in ("%Y-%m-%d", "%H:%M:%S", "%A, %B %d %Y", "%y%m%d"):
            result = self.tool.execute("lint", fmt)
            self.assertEqual(result["findings"], [], fmt)
            self.assertEqual(result["finding_counts"]["total"], 0)

    def test_unknown_directive_is_error_listing_valid_set(self):
        for fmt in ("%q", "%Q", "%i", "%o"):
            result = self.tool.execute("lint", fmt)
            self.assertEqual(
                findings(result), [("unknown_directive", "error", 1)]
            )
            message = result["findings"][0]["message"]
            for known in ("%Y", "%f", "%:z", "%k", "%G"):
                self.assertIn(known, message)

    def test_percent_with_flags_or_width_is_invalid(self):
        result = self.tool.execute("lint", "%3%")
        self.assertEqual(findings(result), [("unknown_directive", "error", 1)])
        self.assertIn("cannot take flags", result["findings"][0]["message"])

    def test_locale_dependent_directives_flagged_info(self):
        result = self.tool.execute("lint", "%c %x %X")
        self.assertEqual(
            findings(result),
            [("locale_dependent", "info", 1)] * 3,
        )
        self.assertIn("'Thu Feb 29 13:45:06 2024'",
                      result["findings"][0]["message"])

    def test_lint_messages_are_locale_independent(self):
        """Lint must never echo the process locale (no strftime calls).

        The locale_dependent message hardcodes the C-locale rendering:
        under a different LC_TIME it must stay byte-identical instead of
        quoting the active locale while claiming it is the C locale.
        """
        import locale
        original = locale.setlocale(locale.LC_TIME)
        baseline = self.tool.execute("lint", "%c %x %X")
        candidates = [loc for loc in (
            "de_DE.UTF-8", "fr_FR.UTF-8", "zh_CN.UTF-8", "en_GB.UTF-8",
            "de_DE", "fr_FR",
        ) if loc != original]
        other = None
        for candidate in candidates:
            try:
                locale.setlocale(locale.LC_TIME, candidate)
                other = candidate
                break
            except locale.Error:
                continue
        if other is None:
            self.skipTest("no other locale available on this platform")
        try:
            self.assertEqual(self.tool.execute("lint", "%c %x %X"),
                             baseline)
            message = self.tool.execute("lint", "%c")["findings"][0]["message"]
            self.assertIn("'Thu Feb 29 13:45:06 2024'", message)
        finally:
            locale.setlocale(locale.LC_TIME, original)

    def test_dangling_percent_is_error(self):
        for fmt in ("abc%", "%", "%-", "%5", "%:"):
            result = self.tool.execute("lint", fmt)
            self.assertEqual(
                findings(result), [("dangling_percent", "error", 1)], fmt
            )

    def test_percent_literal_and_whitespace_are_clean(self):
        result = self.tool.execute("lint", "%% %n %t 100%%")
        self.assertEqual(result["findings"], [])

    def test_gnu_directives_flagged_info(self):
        for letter in "klsPv":
            result = self.tool.execute("lint", "%" + letter)
            self.assertEqual(
                findings(result), [("gnu_extension", "info", 1)], letter
            )
        # %s additionally mentions the local-timezone dependence.
        message = self.tool.execute("lint", "%s")["findings"][0]["message"]
        self.assertIn("local timezone", message)

    def test_colon_offset_forms(self):
        for fmt in ("%:z", "%::z", "%:::z"):
            result = self.tool.execute("lint", fmt)
            self.assertEqual(
                findings(result), [("gnu_extension", "info", 1)], fmt
            )
        # Four colons are not a glibc form.
        result = self.tool.execute("lint", "%::::z")
        self.assertEqual(
            findings(result), [("unknown_directive", "error", 1)]
        )

    def test_non_c89_directives_flagged_info(self):
        for letter in ("C", "D", "e", "F", "g", "G", "h", "r", "R", "T",
                       "u", "V"):
            result = self.tool.execute("lint", "%" + letter)
            self.assertEqual(
                findings(result), [("non_c89_directive", "info", 1)], letter
            )

    def test_flag_width_modifier_forms_flagged_info(self):
        for fmt in ("%-d", "%_m", "%0H", "%^a", "%#Z", "%3Y", "%Ec", "%Od",
                    "%10S", "%-15e"):
            result = self.tool.execute("lint", fmt)
            self.assertEqual(
                findings(result), [("gnu_extension", "info", 1)], fmt
            )
            message = result["findings"][0]["message"]
            self.assertIn("strptime", message)

    def test_tz_directive_caveats(self):
        result = self.tool.execute("lint", "%Z")
        self.assertEqual(
            findings(result), [("tz_directive_caveat", "info", 1)]
        )
        self.assertIn("time.tzname", result["findings"][0]["message"])
        self.assertIn("naive", result["findings"][0]["message"])
        result = self.tool.execute("lint", "%z")
        self.assertEqual(
            findings(result), [("tz_directive_caveat", "info", 1)]
        )
        self.assertIn("naive", result["findings"][0]["message"])

    def test_non_ascii_literal_info(self):
        result = self.tool.execute("lint", "\u5e74%Y\u6708")
        self.assertEqual(
            findings(result), [("non_ascii_literal", "info", 1)]
        )
        self.assertIn("U+5E74", result["findings"][0]["message"])

    def test_empty_and_directive_free_formats(self):
        result = self.tool.execute("lint", "")
        self.assertEqual(findings(result), [("empty_format", "warning", 1)])
        self.assertIn("1900", result["findings"][0]["message"])
        result = self.tool.execute("lint", "YYYY-MM-DD")
        self.assertEqual(findings(result), [("no_directives", "warning", 1)])

    def test_line_numbers_in_multiline_format(self):
        fmt = "line1 %q\nline2 %Y\nline3 %"
        result = self.tool.execute("lint", fmt)
        self.assertEqual(
            findings(result),
            [("unknown_directive", "error", 1),
             ("dangling_percent", "error", 3)],
        )

    def test_finding_counts_tally(self):
        result = self.tool.execute("lint", "%q %c\n\n")
        counts = result["finding_counts"]
        self.assertEqual(counts["error"], 1)
        self.assertEqual(counts["warning"], 0)
        self.assertEqual(counts["info"], 1)
        self.assertEqual(counts["total"], 2)

    def test_lint_is_platform_independent_pure_static(self):
        # The same input must give byte-identical findings twice.
        first = self.tool.execute("lint", "%e %k %-d %q")
        second = self.tool.execute("lint", "%e %k %-d %q")
        self.assertEqual(first, second)

    def test_result_carries_format(self):
        result = self.tool.execute("lint", "%Y")
        self.assertEqual(result["mode"], "lint")
        self.assertEqual(result["format"], "%Y")


class ExplainModeTest(unittest.TestCase):
    """Directive explanation and the context-aware parseability flag."""

    def setUp(self):
        self.tool = StrftimeLintTool()

    def test_entries_in_order_of_appearance(self):
        result = self.tool.execute("explain", "%Y\u5e74%m\u6708%d\u65e5")
        self.assertEqual(
            [entry["directive"] for entry in result["directives"]],
            ["%Y", "%m", "%d"],
        )
        for entry in result["directives"]:
            self.assertEqual(
                sorted(entry),
                ["directive", "example_output", "gnu_only", "meaning",
                 "parsed_by_strptime", "windows_note"],
            )
        self.assertEqual(
            [entry["example_output"] for entry in result["directives"]],
            ["2024", "02", "29"],
        )

    def test_reference_datetime_is_fixed_leap_thursday(self):
        result = self.tool.execute("explain", "%Y")
        self.assertEqual(result["reference_datetime"],
                         "2024-02-29T13:45:06.123456+00:00")
        entry = result["directives"][0]
        self.assertEqual(entry["example_output"], "2024")

    def test_iso_trio_context_sensitivity(self):
        together = self.tool.execute("explain", "%G-%V-%u")
        self.assertEqual(
            [entry["parsed_by_strptime"]
             for entry in together["directives"]],
            [True, True, True],
        )
        for fmt in ("%G", "%V", "%G-%V"):
            result = self.tool.execute("explain", fmt)
            for entry in result["directives"]:
                self.assertFalse(entry["parsed_by_strptime"], fmt)

    def test_gnu_only_flag(self):
        result = self.tool.execute("explain", "%Y %k %s %:z %-d %f %P")
        flags = {entry["directive"]: entry["gnu_only"]
                 for entry in result["directives"]}
        self.assertEqual(flags, {
            "%Y": False, "%k": True, "%s": True, "%:z": True,
            "%-d": True, "%f": False, "%P": True,
        })

    def test_windows_notes(self):
        result = self.tool.execute("explain", "%Y %f %k %Z")
        notes = {entry["directive"]: entry["windows_note"]
                 for entry in result["directives"]}
        self.assertIsNone(notes["%Y"])
        self.assertIn("CPython", notes["%f"])
        self.assertIn("Windows", notes["%k"])
        self.assertIn("Windows", notes["%Z"])

    def test_unknown_and_dangling_entries(self):
        result = self.tool.execute("explain", "%q %G")
        first = result["directives"][0]
        self.assertIsNone(first["meaning"])
        self.assertIsNone(first["example_output"])
        self.assertFalse(first["parsed_by_strptime"])
        result = self.tool.execute("explain", "x%")
        entry = result["directives"][0]
        self.assertEqual(entry["directive"], "%")
        self.assertFalse(entry["parsed_by_strptime"])

    def test_determinism_note_for_epoch_seconds(self):
        result = self.tool.execute("explain", "%s")
        self.assertIn("determinism_notes", result)
        self.assertTrue(any("local timezone" in note
                            for note in result["determinism_notes"]))
        result = self.tool.execute("explain", "%Y")
        self.assertNotIn("determinism_notes", result)


class ProbeModeTest(unittest.TestCase):
    """The live-platform rendering oracle."""

    def setUp(self):
        self.tool = StrftimeLintTool()

    def test_default_reference_datetime(self):
        result = self.tool.execute("probe", "%Y-%m-%d %H:%M:%S.%f %z %Z")
        self.assertEqual(result["datetime_source"], "default_reference")
        self.assertEqual(result["datetime"], FIX.isoformat())
        self.assertEqual(result["platform"], sys.platform)
        self.assertTrue(result["render"]["ok"])
        # On every CPython platform the C89 subset renders identically.
        outputs = {entry["directive"]: entry["output"]
                   for entry in result["directives"]}
        self.assertEqual(
            outputs, {"%Y": "2024", "%m": "02", "%d": "29", "%H": "13",
                      "%M": "45", "%S": "06", "%f": "123456",
                      "%z": FIX.strftime("%z"), "%Z": FIX.strftime("%Z")}
        )

    def test_caller_supplied_datetime_aware_and_naive(self):
        result = self.tool.execute(
            "probe", "%Y %H", dt="2026-01-05T09:30:00+08:00"
        )
        self.assertEqual(result["datetime_source"], "provided")
        self.assertEqual(result["datetime"], "2026-01-05T09:30:00+08:00")
        outputs = {entry["directive"]: entry["output"]
                   for entry in result["directives"]}
        self.assertEqual(outputs, {"%Y": "2026", "%H": "09"})
        naive = self.tool.execute("probe", "%z", dt="2026-01-05T09:30:00")
        self.assertEqual(naive["directives"][0]["output"],
                         datetime(2026, 1, 5).strftime("%z"))

    def test_trailing_z_suffix_accepted(self):
        result = self.tool.execute("probe", "%Y", dt="2024-02-29T13:45:06Z")
        self.assertEqual(result["directives"][0]["output"], "2024")

    def test_dangling_reported_as_error_entry(self):
        result = self.tool.execute("probe", "abc%")
        entry = result["directives"][0]
        self.assertIsNone(entry["output"])
        self.assertIn("dangling", entry["error"])
        # Whether the whole render raises is platform-dependent (glibc
        # raises ValueError; BSD/macOS renders a literal '%') — check
        # it against the runtime's real behavior.
        try:
            expected = FIX.strftime("abc%")
            self.assertTrue(result["render"]["ok"])
            self.assertEqual(result["render"]["output"], expected)
        except ValueError:
            self.assertFalse(result["render"]["ok"])

    def test_whole_render_matches_real_strftime(self):
        # BSD/macOS renders unknown '%q' literally; glibc raises. The
        # tool must agree with whatever the runtime really does.
        for fmt in ("%Y-%q", "abc%", "%Y-%m-%d"):
            result = self.tool.execute("probe", fmt)
            try:
                expected = FIX.strftime(fmt)
                self.assertTrue(result["render"]["ok"], fmt)
                self.assertEqual(result["render"]["output"], expected, fmt)
            except ValueError:
                self.assertFalse(result["render"]["ok"], fmt)
                self.assertIn("error", result["render"])


class RoundtripCheckTest(unittest.TestCase):
    """The real strptime(strftime(...)) verdict and its pitfalls."""

    def setUp(self):
        self.tool = StrftimeLintTool()

    def test_full_rfc3339_format_round_trips_losslessly(self):
        fmt = "%Y-%m-%dT%H:%M:%S.%f%z"
        result = self.tool.execute("roundtrip_check", fmt)
        self.assertTrue(result["possible"])
        self.assertEqual(result["recovered_iso"], FIX.isoformat())
        self.assertEqual(result["loss_fields"], [])
        self.assertEqual(result["rendered"],
                         "2024-02-29T13:45:06.123456+0000")

    def test_second_only_format_loses_everything_else(self):
        result = self.tool.execute("roundtrip_check", "%S")
        self.assertTrue(result["possible"])
        self.assertEqual(result["recovered_iso"], "1900-01-01T00:00:06")
        self.assertEqual(
            result["loss_fields"],
            ["year", "month", "day", "hour", "minute", "microsecond",
             "utcoffset"],
        )

    def test_zone_name_parses_but_loses_the_offset(self):
        result = self.tool.execute("roundtrip_check", "%Z")
        self.assertTrue(result["possible"])
        # strptime %Z yields a naive datetime: the offset is gone.
        self.assertEqual(result["recovered_iso"], "1900-01-01T00:00:00")
        self.assertIn("utcoffset", result["loss_fields"])
        self.assertTrue(any("naive" in pitfall and "%Z" in pitfall
                            for pitfall in result["pitfalls"]))

    def test_day_of_year_without_year_defaults_to_1900(self):
        result = self.tool.execute("roundtrip_check", "%j")
        self.assertTrue(result["possible"])
        # 1900 is not a leap year: day 60 is March 1st, not February 29th.
        self.assertEqual(result["recovered_iso"], "1900-03-01T00:00:00")
        self.assertTrue(any("1900" in pitfall
                            for pitfall in result["pitfalls"]))
        # With a year the date is recovered correctly.
        result = self.tool.execute("roundtrip_check", "%Y-%j")
        self.assertTrue(result["possible"])
        self.assertTrue(result["recovered_iso"].startswith("2024-02-29"))

    def test_week_numbers_ignored_without_year_and_weekday(self):
        result = self.tool.execute("roundtrip_check", "%U")
        self.assertTrue(any("%U" in pitfall
                            for pitfall in result["pitfalls"]))
        # The documented trio recovers the date (week-of-year + weekday).
        result = self.tool.execute("roundtrip_check", "%Y-%U-%w")
        self.assertTrue(result["possible"])
        self.assertTrue(result["recovered_iso"].startswith("2024-02-29"))

    def test_iso_pairing_failure_reported(self):
        result = self.tool.execute("roundtrip_check", "%G-%V")
        self.assertFalse(result["possible"])
        self.assertTrue(any("%G/%V" in pitfall
                            for pitfall in result["pitfalls"]))

    def test_flag_forms_render_but_never_reparse(self):
        result = self.tool.execute("roundtrip_check", "%-d")
        self.assertFalse(result["possible"])
        self.assertEqual(result["rendered"], "29")
        self.assertTrue(any("flag/width" in pitfall
                            for pitfall in result["pitfalls"]))

    def test_c99_shorthand_directives_never_reparse(self):
        for fmt in ("%F", "%T", "%D", "%e"):
            result = self.tool.execute("roundtrip_check", fmt)
            self.assertFalse(result["possible"], fmt)

    def test_empty_format_round_trips_to_defaults(self):
        result = self.tool.execute("roundtrip_check", "")
        self.assertTrue(result["possible"])
        self.assertEqual(result["recovered_iso"], "1900-01-01T00:00:00")
        self.assertEqual(len(result["loss_fields"]), 8)

    def test_c_locale_representation_loses_microseconds(self):
        result = self.tool.execute("roundtrip_check", "%c")
        self.assertTrue(result["possible"])
        self.assertIn("microsecond", result["loss_fields"])

    def test_unparseable_directive_reported(self):
        # %q is unknown: on BSD/macOS it renders literally (no render
        # error), on glibc strftime raises — either way strptime
        # rejects it, so no round-trip is possible.
        result = self.tool.execute("roundtrip_check", "%Y-%q")
        self.assertFalse(result["possible"])
        self.assertIsNone(result["recovered_iso"])
        try:
            rendered = FIX.strftime("%Y-%q")
        except ValueError:
            rendered = None
        self.assertEqual(result["rendered"], rendered)
        self.assertTrue(any("strptime" in pitfall
                            for pitfall in result["pitfalls"]))

    def test_duplicate_directives_break_strptime_regex(self):
        # CPython's _strptime compiles the format to one named group
        # per directive: a repeated directive raises re.error.
        result = self.tool.execute("roundtrip_check", "%Y-%V-%V")
        self.assertFalse(result["possible"])
        self.assertTrue(any("more than once" in pitfall
                            for pitfall in result["pitfalls"]))
        # A repeated %% literal is fine.
        result = self.tool.execute("roundtrip_check", "%Y %% %%")
        self.assertTrue(result["possible"])

    def test_epoch_seconds_and_whitespace_pitfalls(self):
        result = self.tool.execute("roundtrip_check", "%s")
        self.assertFalse(result["possible"])
        self.assertTrue(any("%s" in pitfall
                            for pitfall in result["pitfalls"]))
        result = self.tool.execute("roundtrip_check", "%Y%n")
        self.assertFalse(result["possible"])
        self.assertTrue(any("%n/%t" in pitfall
                            for pitfall in result["pitfalls"]))

    def test_pitfalls_capped(self):
        result = self.tool.execute("roundtrip_check", "%Z %j %U %s %-d %n %W")
        self.assertLessEqual(len(result["pitfalls"]), 6)


class Oracle200SeedsTest(unittest.TestCase):
    """Every verdict re-derived against real datetime behavior."""

    def setUp(self):
        self.tool = StrftimeLintTool()

    def test_exactly_200_distinct_seeds(self):
        self.assertEqual(len(SEEDS), 200)
        self.assertEqual(len(set(SEEDS)), 200)

    def test_parsed_by_strptime_verdicts_match_real_strptime(self):
        """The tool's parseability claims vs the real datetime engine.

        A directive marked parseable must genuinely parse when
        rendered at the fixed reference datetime; one marked
        unparseable must genuinely be rejected. The ISO %G/%V pair is
        context-sensitive and is covered by the trio formats.
        """
        for fmt in SEEDS:
            result = self.tool.execute("explain", fmt)
            for entry in result["directives"]:
                token = entry["directive"]
                if token in ("%",) or entry["meaning"] is None:
                    self.assertFalse(entry["parsed_by_strptime"], fmt)
                    continue
                try:
                    rendered = FIX.strftime(token)
                except ValueError:
                    self.assertIsNone(entry["example_output"], fmt)
                    continue
                self.assertIsNotNone(entry["example_output"], fmt)
                if token in ("%G", "%V"):
                    continue  # context-dependent; see trio test below
                try:
                    datetime.strptime(rendered, token)
                    parses = True
                except ValueError:
                    parses = False
                self.assertEqual(
                    entry["parsed_by_strptime"], parses,
                    f"{token!r} in {fmt!r}: claimed "
                    f"{entry['parsed_by_strptime']}, real {parses} "
                    f"(rendered {rendered!r})",
                )

    def test_iso_trio_formats_really_parse(self):
        for fmt in ("%G-%V-%u", "%G-%V-%a", "%Y-%G-%V-%w"):
            rendered = FIX.strftime(fmt)
            parsed = datetime.strptime(rendered, fmt)
            self.assertEqual(parsed.date(), FIX.date())

    def test_example_outputs_match_real_strftime(self):
        """Deterministic examples must equal the real rendering."""
        for fmt in SEEDS:
            result = self.tool.execute("explain", fmt)
            for entry in result["directives"]:
                token = entry["directive"]
                if entry["meaning"] is None:
                    continue
                try:
                    rendered = FIX.strftime(token)
                except ValueError:
                    rendered = None
                self.assertEqual(entry["example_output"], rendered, fmt)

    def test_roundtrip_verdicts_match_independent_recomputation(self):
        """possible / rendered / recovered_iso re-derived from scratch."""
        for fmt in SEEDS:
            result = self.tool.execute("roundtrip_check", fmt)
            try:
                rendered = FIX.strftime(fmt)
            except ValueError:
                rendered = None
            self.assertEqual(result["rendered"], rendered, fmt)
            if rendered is None:
                self.assertFalse(result["possible"], fmt)
                continue
            try:
                recovered = datetime.strptime(rendered, fmt)
            except (ValueError, re.error):
                self.assertFalse(result["possible"], fmt)
                self.assertIsNone(result["recovered_iso"], fmt)
                continue
            self.assertTrue(result["possible"], fmt)
            self.assertEqual(result["recovered_iso"],
                             recovered.isoformat(), fmt)
            expected_loss = []
            pairs = (
                ("year", recovered.year, FIX.year),
                ("month", recovered.month, FIX.month),
                ("day", recovered.day, FIX.day),
                ("hour", recovered.hour, FIX.hour),
                ("minute", recovered.minute, FIX.minute),
                ("second", recovered.second, FIX.second),
                ("microsecond", recovered.microsecond, FIX.microsecond),
            )
            for name, got, want in pairs:
                if got != want:
                    expected_loss.append(name)
            if recovered.utcoffset() != FIX.utcoffset():
                expected_loss.append("utcoffset")
            self.assertEqual(result["loss_fields"], expected_loss, fmt)

    @unittest.skipUnless(POSIX, "render guarantee holds on POSIX libcs")
    def test_error_free_lint_really_renders(self):
        """No lint errors ⇒ strftime succeeds on POSIX platforms."""
        for fmt in SEEDS:
            result = self.tool.execute("lint", fmt)
            if not any(f["severity"] == "error" for f in result["findings"]):
                try:
                    FIX.strftime(fmt)
                except ValueError as exc:
                    self.fail(f"{fmt!r} passed lint but failed to "
                              f"render: {exc}")

    def test_lint_findings_are_deterministic(self):
        for fmt in SEEDS[:50]:
            self.assertEqual(self.tool.execute("lint", fmt),
                             self.tool.execute("lint", fmt), fmt)


class ValidationTest(unittest.TestCase):
    """The strict, before-any-computation validation matrix."""

    def setUp(self):
        self.tool = StrftimeLintTool()

    def test_unknown_mode_rejected(self):
        for mode in ("", "lints", "LINT", None, 1):
            with self.assertRaises(ValueError):
                self.tool.execute(mode, "%Y")

    def test_fmt_type_and_length_checks(self):
        for bad in (None, True, 42, ["%Y"], {"fmt": "%Y"}):
            with self.assertRaises(ValueError):
                self.tool.execute("lint", bad)
        with self.assertRaises(ValueError):
            self.tool.execute("lint", "x" * 4_001)
        # Exactly at the cap is accepted.
        result = self.tool.execute("lint", "x" * 4_000)
        self.assertEqual(codes_of(result), ["no_directives"])

    def test_dt_only_accepted_in_probe_mode(self):
        for mode in ("lint", "explain", "roundtrip_check"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode, "%Y", dt="2024-02-29T13:45:06+00:00")

    def test_dt_value_checks(self):
        for bad in (True, 42, "", "not-a-date", "2024-13-45",
                    "2024-02-29T99:00:00Z", "z" * 65):
            with self.assertRaises(ValueError):
                self.tool.execute("probe", "%Y", dt=bad)

    def test_error_messages_are_prefixed(self):
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute("nope", "%Y")
        self.assertIn("strftime_lint_tool:", str(ctx.exception))
        self.assertIn("mode must be one of", str(ctx.exception))

    def test_package_and_direct_imports_are_the_same_class(self):
        self.assertIs(StrftimeLintTool, DirectStrftimeLintTool)


if __name__ == "__main__":
    unittest.main()
