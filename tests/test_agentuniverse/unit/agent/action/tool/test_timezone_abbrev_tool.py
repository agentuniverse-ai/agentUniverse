#!/usr/bin/env python3

# @Time    : 2026/10/20
# @FileName: test_timezone_abbrev_tool.py

"""Tests for TimezoneAbbrevTool.

All results are deterministic: the reference table is a static module
constant and no mode reads the wall clock. Ground-truth offsets below
were cross-checked against publicly known timezone facts (IANA zone
offsets as of 2026).
"""

import os
import re
import unittest

from agentuniverse.agent.action.tool.common_tool import (
    timezone_abbrev_tool as module,
)
from agentuniverse.agent.action.tool.common_tool.timezone_abbrev_tool import (
    TimezoneAbbrevTool,
)

YAML_PATH = os.path.join(
    os.path.dirname(module.__file__), "timezone_abbrev_tool.yaml")

# Spot-check ground truths: (abbr, 1-based entry ordinal, name fragment,
# offset_minutes, sign, dst). Each offset is a well-known real value.
GROUND_TRUTHS = [
    ("UTC", 1, "Coordinated Universal Time", 0, "+00:00", False),
    ("GMT", 1, "Greenwich Mean Time", 0, "+00:00", False),
    ("Z", 1, "Zulu", 0, "+00:00", False),
    ("EST", 1, "Eastern Standard", -300, "-05:00", False),
    ("EDT", 1, "Eastern Daylight", -240, "-04:00", True),
    ("PST", 1, "Pacific Standard", -480, "-08:00", False),
    ("PDT", 1, "Pacific Daylight", -420, "-07:00", True),
    ("NST", 1, "Newfoundland Standard", -210, "-03:30", False),
    ("ChST", 1, "Chamorro Standard", 600, "+10:00", False),
    ("CET", 1, "Central European Time", 60, "+01:00", False),
    ("CEST", 1, "Central European Summer", 120, "+02:00", True),
    ("MSK", 1, "Moscow Standard", 180, "+03:00", False),
    ("IST", 1, "India Standard Time", 330, "+05:30", False),
    ("MMT", 1, "Myanmar Time", 390, "+06:30", False),
    ("ICT", 1, "Indochina Time", 420, "+07:00", False),
    ("JST", 1, "Japan Standard Time", 540, "+09:00", False),
    ("ACST", 1, "Australian Central Standard", 570, "+09:30", False),
    ("NZST", 1, "New Zealand Standard", 720, "+12:00", False),
    ("NZDT", 1, "New Zealand Daylight", 780, "+13:00", True),
    ("SST", 1, "Samoa Standard Time", -660, "-11:00", False),
]


def entry_for(result: dict, ordinal: int) -> dict:
    return result["entries"][ordinal - 1]


class TimezoneAbbrevLookupTest(unittest.TestCase):
    """mode=lookup: case-insensitive resolution and ground-truth table."""

    def setUp(self):
        self.tool = TimezoneAbbrevTool()

    def test_ground_truth_offsets(self):
        # 20 spot-checks against publicly known timezone values.
        for abbr, ordinal, fragment, minutes, sign, dst in GROUND_TRUTHS:
            result = self.tool.execute(mode="lookup", abbr=abbr)
            self.assertEqual(result["status"], "success", msg=abbr)
            self.assertEqual(result["abbr"], abbr.upper(), msg=abbr)
            entry = entry_for(result, ordinal)
            self.assertIn(fragment, entry["name"], msg=abbr)
            self.assertEqual(entry["offset_minutes"], minutes, msg=abbr)
            self.assertEqual(entry["sign"], sign, msg=abbr)
            self.assertEqual(entry["dst"], dst, msg=abbr)
            self.assertIn("ambiguous", entry)

    def test_case_insensitive_and_whitespace(self):
        for variant in ("est", "Est", " eSt ", "EST"):
            result = self.tool.execute(mode="lookup", abbr=variant)
            self.assertEqual(result["status"], "success", msg=variant)
            self.assertEqual(result["abbr"], "EST")
            self.assertEqual(result["count"], 1)
            self.assertFalse(result["ambiguous"])

    def test_cst_returns_all_three_entries_with_flags(self):
        result = self.tool.execute(mode="lookup", abbr="cst")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 3)
        self.assertTrue(result["ambiguous"])
        offsets = {e["offset_minutes"] for e in result["entries"]}
        self.assertEqual(offsets, {-360, 480, -300})
        names = {e["name"] for e in result["entries"]}
        self.assertEqual(names, {
            "Central Standard Time (North America)",
            "China Standard Time",
            "Cuba Standard Time",
        })
        self.assertTrue(all(e["ambiguous"] for e in result["entries"]))

    def test_ist_returns_both_entries_with_flags(self):
        result = self.tool.execute(mode="lookup", abbr="IST")
        self.assertEqual(result["count"], 2)
        self.assertTrue(result["ambiguous"])
        pairs = {(e["name"], e["offset_minutes"]) for e in result["entries"]}
        self.assertEqual(pairs, {
            ("India Standard Time", 330),
            ("Israel Standard Time", 120),
        })

    def test_bst_returns_both_entries_with_flags(self):
        result = self.tool.execute(mode="lookup", abbr="BST")
        self.assertEqual(result["count"], 2)
        self.assertTrue(result["ambiguous"])
        pairs = {(e["name"], e["offset_minutes"], e["dst"])
                 for e in result["entries"]}
        self.assertEqual(pairs, {
            ("British Summer Time (UK)", 60, True),
            ("Bangladesh Standard Time", 360, False),
        })

    def test_ast_and_sst_ambiguity(self):
        ast = self.tool.execute(mode="lookup", abbr="AST")
        self.assertEqual(ast["count"], 2)
        self.assertEqual(
            {e["offset_minutes"] for e in ast["entries"]}, {-240, 180})
        sst = self.tool.execute(mode="lookup", abbr="SST")
        self.assertEqual(sst["count"], 2)
        self.assertEqual(
            {e["offset_minutes"] for e in sst["entries"]}, {-660, 660})

    def test_table_shape_and_size(self):
        table = module._ABBREVIATION_TABLE
        # ~55 unique abbreviations across ~60 rows.
        uniques = {row[0].upper() for row in table}
        self.assertGreaterEqual(len(uniques), 55)
        self.assertGreaterEqual(len(table), len(uniques))
        seen = set()
        for abbr, name, minutes, _dst in table:
            self.assertTrue(re.fullmatch(r"[A-Za-z]{1,5}", abbr), abbr)
            self.assertTrue(name)
            self.assertTrue(-720 <= minutes <= 840, minutes)
            self.assertEqual(minutes % 15, 0, minutes)
            key = (abbr.upper(), name)
            self.assertNotIn(key, seen)
            seen.add(key)


class TimezoneAbbrevConvertTest(unittest.TestCase):
    """mode=convert: offset arithmetic, midnight wrap, ambiguity policy."""

    def setUp(self):
        self.tool = TimezoneAbbrevTool()

    def test_est_to_jst_same_day(self):
        result = self.tool.execute(
            mode="convert", time="09:00", from_abbr="EST", to_abbr="JST")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result_time"], "23:00")
        self.assertEqual(result["day_shift"], 0)
        self.assertEqual(result["delta_minutes"], 840)
        self.assertEqual(result["delta"], "+14:00")
        self.assertEqual(result["from_sign"], "-05:00")
        self.assertEqual(result["to_sign"], "+09:00")
        self.assertFalse(result["ambiguous"])

    def test_midnight_wrap_forward(self):
        # PST 16:00 + 18h (PST -8 -> AEST +10) = 10:00 the next day.
        result = self.tool.execute(
            mode="convert", time="16:00", from_abbr="PST", to_abbr="AEST")
        self.assertEqual(result["result_time"], "10:00")
        self.assertEqual(result["day_shift"], 1)
        self.assertEqual(result["delta_minutes"], 1080)

    def test_midnight_wrap_backward(self):
        # JST 09:00 - 17h (JST +9 -> PST -8) = 16:00 the previous day.
        result = self.tool.execute(
            mode="convert", time="09:00", from_abbr="JST", to_abbr="PST")
        self.assertEqual(result["result_time"], "16:00")
        self.assertEqual(result["day_shift"], -1)
        self.assertEqual(result["delta_minutes"], -1020)
        self.assertEqual(result["delta"], "-17:00")

    def test_exact_midnight_boundary(self):
        # UTC 13:00 -> NZST (+12) lands exactly on 01:00 next day.
        result = self.tool.execute(
            mode="convert", time="13:00", from_abbr="UTC", to_abbr="NZST")
        self.assertEqual(result["result_time"], "01:00")
        self.assertEqual(result["day_shift"], 1)
        # UTC 00:00 -> GMT stays at exactly midnight.
        result = self.tool.execute(
            mode="convert", time="00:00", from_abbr="UTC", to_abbr="GMT")
        self.assertEqual(result["result_time"], "00:00")
        self.assertEqual(result["day_shift"], 0)

    def test_dst_pair_est_to_edt_delta_plus_one_hour(self):
        # Documented behaviour: EST (-05:00) and EDT (-04:00) are the
        # winter/summer labels of the same North American zone family.
        # The label difference is exactly +1 hour; the tool reports the
        # arithmetic delta of the two abbreviations, not any country's
        # DST calendar.
        result = self.tool.execute(
            mode="convert", time="09:00", from_abbr="EST", to_abbr="EDT")
        self.assertEqual(result["result_time"], "10:00")
        self.assertEqual(result["day_shift"], 0)
        self.assertEqual(result["delta_minutes"], 60)
        self.assertEqual(result["delta"], "+01:00")
        self.assertFalse(result["ambiguous"])

    def test_half_hour_offset_arithmetic(self):
        # IST India +05:30 -> NST -03:30, delta -540 (-9h exactly).
        result = self.tool.execute(
            mode="convert", time="08:00", from_abbr="IST", to_abbr="NST",
        )
        # Ambiguous IST resolves to India (+05:30): 08:00 - 9h = 23:00.
        self.assertEqual(result["from_sign"], "+05:30")
        self.assertEqual(result["to_sign"], "-03:30")
        self.assertEqual(result["delta_minutes"], -540)
        self.assertEqual(result["result_time"], "23:00")
        self.assertEqual(result["day_shift"], -1)
        self.assertTrue(result["ambiguous"])

    def test_ambiguous_from_abbr_uses_first_entry_with_warning(self):
        result = self.tool.execute(
            mode="convert", time="09:00", from_abbr="CST", to_abbr="UTC")
        # CST resolves to the first table entry: US Central (-06:00).
        self.assertEqual(result["from_offset_minutes"], -360)
        self.assertEqual(result["from_sign"], "-06:00")
        self.assertEqual(result["result_time"], "15:00")
        self.assertEqual(result["day_shift"], 0)
        self.assertTrue(result["ambiguous"])
        self.assertIn("ambiguous", result["warning"])
        self.assertIn("China Standard Time", result["warning"])
        self.assertIn("Cuba Standard Time", result["warning"])

    def test_ambiguous_to_abbr_uses_first_entry_with_warning(self):
        result = self.tool.execute(
            mode="convert", time="09:00", from_abbr="UTC", to_abbr="BST")
        # BST resolves to the first table entry: British Summer (+01:00).
        self.assertEqual(result["to_offset_minutes"], 60)
        self.assertEqual(result["result_time"], "10:00")
        self.assertTrue(result["ambiguous"])
        self.assertIn("Bangladesh Standard Time", result["warning"])

    def test_same_abbr_zero_delta(self):
        result = self.tool.execute(
            mode="convert", time="09:05", from_abbr="KST", to_abbr="JST")
        self.assertEqual(result["result_time"], "09:05")
        self.assertEqual(result["day_shift"], 0)
        self.assertEqual(result["delta_minutes"], 0)
        self.assertEqual(result["delta"], "+00:00")


class TimezoneAbbrevNowOffsetTest(unittest.TestCase):
    """mode=now_offset: abbreviation -> fixed table offset."""

    def setUp(self):
        self.tool = TimezoneAbbrevTool()

    def test_unambiguous_offsets(self):
        for abbr, minutes, sign in (
            ("UTC", 0, "+00:00"),
            ("PST", -480, "-08:00"),
            ("JST", 540, "+09:00"),
            ("ist", 330, "+05:30"),  # India is the first IST entry
        ):
            result = self.tool.execute(mode="now_offset", abbr=abbr)
            self.assertEqual(result["status"], "success", msg=abbr)
            self.assertEqual(result["offset_minutes"], minutes, msg=abbr)
            self.assertEqual(result["sign"], sign, msg=abbr)

    def test_ambiguous_abbr_first_entry_and_warning(self):
        result = self.tool.execute(mode="now_offset", abbr="CST")
        self.assertEqual(result["offset_minutes"], -360)
        self.assertEqual(result["sign"], "-06:00")
        self.assertTrue(result["ambiguous"])
        self.assertIn("warning", result)
        self.assertIn("China Standard Time (+08:00)", result["warning"])

    def test_dst_flag_reported(self):
        self.assertTrue(
            self.tool.execute(mode="now_offset", abbr="EDT")["dst"])
        self.assertFalse(
            self.tool.execute(mode="now_offset", abbr="EST")["dst"])


class TimezoneAbbrevSearchByOffsetTest(unittest.TestCase):
    """mode=search_by_offset: both input formats."""

    def setUp(self):
        self.tool = TimezoneAbbrevTool()

    def test_string_and_integer_forms_agree(self):
        by_string = self.tool.execute(mode="search_by_offset", offset="+08:00")
        by_int = self.tool.execute(mode="search_by_offset", offset=480)
        self.assertEqual(by_string["status"], "success")
        self.assertEqual(by_int["status"], "success")
        self.assertEqual(by_string["offset_minutes"], 480)
        self.assertEqual(by_int["offset_minutes"], 480)
        self.assertEqual(by_string["sign"], "+08:00")
        self.assertEqual(by_int["sign"], "+08:00")
        self.assertEqual(by_string["entries"], by_int["entries"])
        pairs = {(e["abbr"], e["name"]) for e in by_string["entries"]}
        self.assertEqual(pairs, {
            ("CST", "China Standard Time"),
            ("AWST", "Australian Western Standard Time"),
        })

    def test_half_hour_offset_string_form(self):
        result = self.tool.execute(mode="search_by_offset", offset="-03:30")
        self.assertEqual([e["abbr"] for e in result["entries"]], ["NST"])
        result = self.tool.execute(mode="search_by_offset", offset=330)
        self.assertEqual(
            [e["name"] for e in result["entries"]], ["India Standard Time"])

    def test_zero_offset_lists_multiple_codes(self):
        result = self.tool.execute(mode="search_by_offset", offset="+00:00")
        codes = {e["abbr"] for e in result["entries"]}
        self.assertEqual(codes, {"UTC", "GMT", "Z", "WET"})

    def test_no_match_returns_empty_success(self):
        result = self.tool.execute(mode="search_by_offset", offset="-11:30")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["entries"], [])


class TimezoneAbbrevValidationTest(unittest.TestCase):
    """Error matrix, suggestions, exports and packaging."""

    def setUp(self):
        self.tool = TimezoneAbbrevTool()

    def test_unknown_abbr_error_lists_similar(self):
        result = self.tool.execute(mode="lookup", abbr="ESTT")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("Unknown timezone abbreviation 'ESTT'", result["error"])
        self.assertIn("Closest matches:", result["error"])
        self.assertIn("EST", result["error"].split("Closest matches:")[1])

    def test_unknown_abbr_in_convert(self):
        result = self.tool.execute(
            mode="convert", time="09:00", from_abbr="XYZ", to_abbr="UTC")
        self.assertEqual(result["status"], "error")
        self.assertIn("Unknown timezone abbreviation 'XYZ'", result["error"])

    def test_bad_abbr_charset_and_length(self):
        for bad in ("E5T", "EST!", "TOOLONG", "E T", "-", 123):
            result = self.tool.execute(mode="lookup", abbr=bad)
            self.assertEqual(result["status"], "error", msg=repr(bad))
            self.assertEqual(result["error_type"], "validation_error")

    def test_missing_abbr(self):
        for empty in ("", "   ", None):
            result = self.tool.execute(mode="lookup", abbr=empty)
            self.assertEqual(result["status"], "error")
            self.assertIn("required", result["error"])

    def test_bad_time_formats(self):
        for bad in ("9:00", "09:0", "0900", "24:00", "09:60", "09:00:00",
                    "09-00", "09:0O", 900):
            result = self.tool.execute(
                mode="convert", time=bad, from_abbr="EST", to_abbr="UTC")
            self.assertEqual(result["status"], "error", msg=repr(bad))
            if isinstance(bad, str):
                self.assertIn("Invalid time", result["error"])
            else:
                self.assertIn("time must be a string", result["error"])

    def test_missing_time(self):
        for empty in ("", "   ", None):
            result = self.tool.execute(
                mode="convert", time=empty, from_abbr="EST", to_abbr="UTC")
            self.assertEqual(result["status"], "error", msg=repr(empty))
            self.assertIn("required", result["error"])

    def test_convert_missing_from_or_to_abbr(self):
        result = self.tool.execute(
            mode="convert", time="09:00", from_abbr="", to_abbr="UTC")
        self.assertEqual(result["status"], "error")
        self.assertIn("from_abbr", result["error"])
        result = self.tool.execute(
            mode="convert", time="09:00", from_abbr="EST", to_abbr="")
        self.assertEqual(result["status"], "error")
        self.assertIn("to_abbr", result["error"])

    def test_bad_offset_formats(self):
        for bad in ("+8:00", "08:00", "+25:00", "+08:60", "08", "abc",
                    "+08", True, 1.5, None):
            result = self.tool.execute(mode="search_by_offset", offset=bad)
            self.assertEqual(result["status"], "error", msg=repr(bad))
            self.assertEqual(result["error_type"], "validation_error")

    def test_offset_minutes_out_of_range(self):
        result = self.tool.execute(mode="search_by_offset", offset=2000)
        self.assertEqual(result["status"], "error")
        self.assertIn("must not exceed", result["error"])

    def test_unknown_and_non_string_mode(self):
        result = self.tool.execute(mode="nope", abbr="EST")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("Unsupported mode", result["error"])
        self.assertEqual(result["mode"], "nope")
        result = self.tool.execute(mode=42)
        self.assertEqual(result["status"], "error")
        self.assertIn("mode must be a string", result["error"])

    def test_mode_case_and_whitespace_normalised(self):
        result = self.tool.execute(mode=" LOOKUP ", abbr="est")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "lookup")

    def test_package_export(self):
        from agentuniverse.agent.action.tool.common_tool import (
            TimezoneAbbrevTool as exported)
        self.assertIs(exported, TimezoneAbbrevTool)

    def test_yaml_exists_and_declares_component(self):
        self.assertTrue(os.path.isfile(YAML_PATH))
        with open(YAML_PATH, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("class: TimezoneAbbrevTool", content)
        self.assertIn(
            "module: agentuniverse.agent.action.tool.common_tool."
            "timezone_abbrev_tool", content)

    def test_tool_name_and_description(self):
        self.assertEqual(self.tool.name, "timezone_abbrev_tool")
        self.assertTrue(self.tool.description)


if __name__ == "__main__":
    unittest.main()
