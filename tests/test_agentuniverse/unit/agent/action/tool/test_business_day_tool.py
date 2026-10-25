#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_business_day_tool.py

"""Offline unit tests for BusinessDayTool.

The tool is built purely on the standard library (``datetime.date``)
and never touches the network, so this suite runs fully offline. Every
assertion is deterministic and checked against hand-computed ground
truths derived from fixed calendar facts:

* 2026-10-14/15/16 are Wed/Thu/Fri; 2026-10-17/18 are Sat/Sun;
  2026-10-19/20 are Mon/Tue; 2026-10-23 is Fri and 2026-10-30 is Fri;
  2026-11-01 is Sun and 2026-11-02 is Mon (month boundary).
* 2027-12-31 is Fri and 2028-01-03 is Mon (year boundary).
* 2028 is a leap year: 2028-02-25/26/28/29 and 2028-03-01 are
  Fri/Sat/Mon/Tue/Wed.
* 9999-12-31 is Fri and 0001-01-01 is Mon (datetime.date range ends).
* 2026 has 365 days starting on a Thursday, so it holds exactly 261
  Monday-Friday business days (52 full weeks + the extra Thursday).
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import BusinessDayTool
from agentuniverse.agent.action.tool.common_tool.business_day_tool import (
    BusinessDayTool as DirectBusinessDayTool,
)

# Weekend-skipping walk over the 2026-10-16 (Fri) .. 2026-10-20 (Tue) span.
OCT16_FRI = "2026-10-16"
OCT17_SAT = "2026-10-17"
OCT18_SUN = "2026-10-18"
OCT19_MON = "2026-10-19"
OCT20_TUE = "2026-10-20"
OCT21_WED = "2026-10-21"
OCT22_THU = "2026-10-22"
OCT23_FRI = "2026-10-23"
OCT25_SUN = "2026-10-25"
OCT30_FRI = "2026-10-30"
NOV01_SUN = "2026-11-01"
NOV02_MON = "2026-11-02"


class BusinessDayToolAddTest(unittest.TestCase):
    """add mode — date + N business days."""

    def setUp(self) -> None:
        self.tool = BusinessDayTool()

    def test_add_one_day_forward_across_weekend(self) -> None:
        result = self.tool.execute(mode="add", date_str=OCT16_FRI, days=1)
        self.assertEqual(
            result,
            {
                "mode": "add",
                "date": OCT16_FRI,
                "days": 1,
                "weekend": "sat_sun",
                "holidays_skipped": 0,
                "result": OCT19_MON,
            },
        )

    def test_add_three_days_from_midweek(self) -> None:
        result = self.tool.execute(mode="add", date_str="2026-10-14", days=3)
        # Wed +1 -> Thu, +2 -> Fri, +3 -> Mon (weekend skipped).
        self.assertEqual(result["result"], OCT19_MON)

    def test_add_negative_walks_backwards_across_weekend(self) -> None:
        result = self.tool.execute(mode="add", date_str=OCT19_MON, days=-1)
        self.assertEqual(result["result"], OCT16_FRI)
        self.assertEqual(result["days"], -1)

    def test_add_from_sunday_lands_monday(self) -> None:
        result = self.tool.execute(mode="add", date_str=OCT18_SUN, days=1)
        self.assertEqual(result["result"], OCT19_MON)

    def test_add_zero_returns_input_unchanged(self) -> None:
        # Documented: a zero offset never rolls, even on a weekend day.
        result = self.tool.execute(mode="add", date_str=OCT17_SAT, days=0)
        self.assertEqual(result["result"], OCT17_SAT)
        self.assertEqual(result["holidays_skipped"], 0)
        weekday = self.tool.execute(mode="add", date_str=OCT19_MON, days=0)
        self.assertEqual(weekday["result"], OCT19_MON)

    def test_add_crosses_month_boundary(self) -> None:
        result = self.tool.execute(mode="add", date_str=OCT30_FRI, days=1)
        self.assertEqual(result["result"], NOV02_MON)

    def test_add_crosses_year_boundary(self) -> None:
        result = self.tool.execute(mode="add", date_str="2027-12-31", days=1)
        self.assertEqual(result["result"], "2028-01-03")

    def test_add_backwards_crosses_month_boundary(self) -> None:
        result = self.tool.execute(mode="add", date_str=NOV02_MON, days=-1)
        self.assertEqual(result["result"], OCT30_FRI)

    def test_add_ten_business_days(self) -> None:
        result = self.tool.execute(mode="add", date_str=OCT16_FRI, days=10)
        # Oct 19-23 (5) + Oct 26-30 (5).
        self.assertEqual(result["result"], OCT30_FRI)

    def test_add_skips_single_holiday(self) -> None:
        result = self.tool.execute(
            mode="add", date_str=OCT16_FRI, days=1, holidays=[OCT19_MON]
        )
        self.assertEqual(result["result"], OCT20_TUE)
        self.assertEqual(result["holidays_skipped"], 1)

    def test_add_skips_consecutive_holidays_from_dict(self) -> None:
        result = self.tool.execute(
            mode="add",
            date_str=OCT16_FRI,
            days=2,
            holidays={OCT19_MON: "Bridge Day", OCT20_TUE: "Market Close"},
        )
        self.assertEqual(result["result"], OCT22_THU)
        self.assertEqual(result["holidays_skipped"], 2)

    def test_add_fri_sat_weekend_variant(self) -> None:
        # Thu +1 with a Fri/Sat weekend skips to Sunday.
        result = self.tool.execute(
            mode="add", date_str="2026-10-15", days=1, weekend="fri_sat"
        )
        self.assertEqual(result["result"], OCT18_SUN)
        self.assertEqual(result["weekend"], "fri_sat")

    def test_add_sun_only_weekend_variant(self) -> None:
        # Saturday is a business day; only Sunday is skipped.
        result = self.tool.execute(
            mode="add", date_str=OCT17_SAT, days=1, weekend="sun_only"
        )
        self.assertEqual(result["result"], OCT19_MON)

    def test_add_over_leap_february(self) -> None:
        one = self.tool.execute(mode="add", date_str="2028-02-25", days=1)
        self.assertEqual(one["result"], "2028-02-28")  # Fri -> Mon
        two = self.tool.execute(mode="add", date_str="2028-02-28", days=2)
        # Tue Feb 29 (leap day, business) then Wed Mar 1.
        self.assertEqual(two["result"], "2028-03-01")

    def test_add_max_positive_boundary(self) -> None:
        # 3650 = 730 five-day weeks = 5110 calendar days; Fri stays Fri.
        result = self.tool.execute(mode="add", date_str=OCT16_FRI, days=3650)
        self.assertEqual(result["result"], "2040-10-12")

    def test_add_max_negative_boundary(self) -> None:
        result = self.tool.execute(mode="add", date_str=OCT19_MON, days=-3650)
        self.assertEqual(result["result"], "2012-10-22")

    def test_add_days_as_integer_string(self) -> None:
        forward = self.tool.execute(mode="add", date_str="2026-10-14", days="3")
        self.assertEqual(forward["result"], OCT19_MON)
        backward = self.tool.execute(mode="add", date_str=OCT19_MON, days="-1")
        self.assertEqual(backward["result"], OCT16_FRI)
        zero = self.tool.execute(mode="add", date_str=OCT19_MON, days="0")
        self.assertEqual(zero["result"], OCT19_MON)

    def test_add_weekend_preset_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="add", date_str=OCT16_FRI, days=1, weekend="SAT_SUN"
        )
        self.assertEqual(result["weekend"], "sat_sun")
        self.assertEqual(result["result"], OCT19_MON)

    def test_add_holiday_on_weekend_is_walked_over(self) -> None:
        # The Sat holiday is skipped as a weekend day; +1 from Fri is Mon.
        result = self.tool.execute(
            mode="add", date_str=OCT16_FRI, days=1, holidays=[OCT17_SAT]
        )
        self.assertEqual(result["result"], OCT19_MON)


class BusinessDayToolCountTest(unittest.TestCase):
    """count mode — business days between two dates."""

    def setUp(self) -> None:
        self.tool = BusinessDayTool()

    def test_count_full_week_inclusive(self) -> None:
        result = self.tool.execute(
            mode="count", start_date=OCT19_MON, end_date=OCT23_FRI
        )
        self.assertEqual(
            result,
            {
                "mode": "count",
                "start_date": OCT19_MON,
                "end_date": OCT23_FRI,
                "weekend": "sat_sun",
                "include_ends": True,
                "calendar_days": 5,
                "weekend_days": 0,
                "holidays_in_range": 0,
                "result": 5,
            },
        )

    def test_count_full_week_exclusive(self) -> None:
        # Strictly between Mon..Fri leaves Tue/Wed/Thu.
        result = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT23_FRI,
            include_ends=False,
        )
        self.assertEqual(result["result"], 3)
        self.assertEqual(result["calendar_days"], 3)

    def test_count_with_holiday(self) -> None:
        result = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT23_FRI,
            holidays=[OCT20_TUE],
        )
        self.assertEqual(result["result"], 4)
        self.assertEqual(result["holidays_in_range"], 1)

    def test_count_holidays_as_name_dict(self) -> None:
        result = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT23_FRI,
            holidays={OCT20_TUE: "Year End"},
        )
        self.assertEqual(result["result"], 4)

    def test_count_weekend_only_span(self) -> None:
        for include_ends in (True, False):
            result = self.tool.execute(
                mode="count",
                start_date=OCT17_SAT,
                end_date=OCT18_SUN,
                include_ends=include_ends,
            )
            self.assertEqual(result["result"], 0)

    def test_count_single_business_day(self) -> None:
        inclusive = self.tool.execute(
            mode="count", start_date=OCT19_MON, end_date=OCT19_MON
        )
        self.assertEqual(inclusive["result"], 1)
        exclusive = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT19_MON,
            include_ends=False,
        )
        self.assertEqual(exclusive["result"], 0)

    def test_count_single_weekend_day(self) -> None:
        result = self.tool.execute(
            mode="count", start_date=OCT17_SAT, end_date=OCT17_SAT
        )
        self.assertEqual(result["result"], 0)
        self.assertEqual(result["weekend_days"], 1)

    def test_count_monday_to_sunday(self) -> None:
        result = self.tool.execute(
            mode="count", start_date=OCT19_MON, end_date=OCT25_SUN
        )
        self.assertEqual(result["calendar_days"], 7)
        self.assertEqual(result["weekend_days"], 2)
        self.assertEqual(result["result"], 5)

    def test_count_fri_sat_weekend_variant(self) -> None:
        # Mon..Sun with a Fri/Sat weekend: business days are
        # Mon, Tue, Wed, Thu, Sun (Friday and Saturday are off).
        result = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT25_SUN,
            weekend="fri_sat",
        )
        self.assertEqual(result["result"], 5)
        self.assertEqual(result["weekend_days"], 2)

    def test_count_sun_only_weekend_variant(self) -> None:
        # Mon..Sun with a Sunday-only weekend skips just Oct 25.
        result = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT25_SUN,
            weekend="sun_only",
        )
        self.assertEqual(result["result"], 6)

    def test_count_leap_february_span(self) -> None:
        result = self.tool.execute(
            mode="count", start_date="2028-02-28", end_date="2028-03-01"
        )
        self.assertEqual(result["result"], 3)  # Mon, leap Tue, Wed
        with_leap_holiday = self.tool.execute(
            mode="count",
            start_date="2028-02-28",
            end_date="2028-03-01",
            holidays=["2028-02-29"],
        )
        self.assertEqual(with_leap_holiday["result"], 2)

    def test_count_full_year_2026(self) -> None:
        # 365 days from a Thursday: 52 weeks * 5 + the extra Thursday.
        result = self.tool.execute(
            mode="count", start_date="2026-01-01", end_date="2026-12-31"
        )
        self.assertEqual(result["calendar_days"], 365)
        self.assertEqual(result["weekend_days"], 104)
        self.assertEqual(result["result"], 261)

    def test_count_holiday_on_weekend_not_double_subtracted(self) -> None:
        # Oct 21 (Wed) counts; Oct 25 (Sun) is out of range;
        # Oct 17 (Sat) is already a weekend day.
        result = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT23_FRI,
            holidays=[OCT21_WED, OCT25_SUN, OCT17_SAT],
        )
        self.assertEqual(result["holidays_in_range"], 1)
        self.assertEqual(result["result"], 4)

    def test_count_exclusive_adjacent_days(self) -> None:
        result = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT20_TUE,
            include_ends=False,
        )
        self.assertEqual(result["result"], 0)
        self.assertEqual(result["calendar_days"], 0)

    def test_count_exclusive_three_day_span(self) -> None:
        # Strictly between Mon and Wed leaves only Tue.
        result = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT21_WED,
            include_ends=False,
        )
        self.assertEqual(result["result"], 1)


class BusinessDayToolIsBusinessTest(unittest.TestCase):
    """is_business mode — verdict with reason for one date."""

    def setUp(self) -> None:
        self.tool = BusinessDayTool()

    def test_is_business_on_business_day(self) -> None:
        result = self.tool.execute(mode="is_business", date_str=OCT19_MON)
        self.assertEqual(
            result,
            {
                "mode": "is_business",
                "date": OCT19_MON,
                "weekend": "sat_sun",
                "weekday": "Monday",
                "is_business": True,
                "reason": "business",
                "holiday_name": None,
                "result": True,
            },
        )

    def test_is_business_saturday_weekend(self) -> None:
        result = self.tool.execute(mode="is_business", date_str=OCT17_SAT)
        self.assertFalse(result["is_business"])
        self.assertEqual(result["reason"], "weekend")
        self.assertEqual(result["weekday"], "Saturday")

    def test_is_business_sunday_weekend(self) -> None:
        result = self.tool.execute(mode="is_business", date_str=OCT18_SUN)
        self.assertEqual(result["reason"], "weekend")
        self.assertEqual(result["weekday"], "Sunday")

    def test_is_business_fri_sat_variant(self) -> None:
        friday = self.tool.execute(
            mode="is_business", date_str=OCT16_FRI, weekend="fri_sat"
        )
        self.assertEqual(friday["reason"], "weekend")
        sunday = self.tool.execute(
            mode="is_business", date_str=OCT18_SUN, weekend="fri_sat"
        )
        self.assertEqual(sunday["reason"], "business")

    def test_is_business_sun_only_variant(self) -> None:
        saturday = self.tool.execute(
            mode="is_business", date_str=OCT17_SAT, weekend="sun_only"
        )
        self.assertEqual(saturday["reason"], "business")
        sunday = self.tool.execute(
            mode="is_business", date_str=OCT18_SUN, weekend="sun_only"
        )
        self.assertEqual(sunday["reason"], "weekend")

    def test_is_business_holiday_name_echoed(self) -> None:
        result = self.tool.execute(
            mode="is_business",
            date_str=OCT19_MON,
            holidays={OCT19_MON: "Deepavali"},
        )
        self.assertFalse(result["is_business"])
        self.assertEqual(result["reason"], "holiday")
        self.assertEqual(result["holiday_name"], "Deepavali")

    def test_is_business_holiday_list_has_no_name(self) -> None:
        result = self.tool.execute(
            mode="is_business", date_str=OCT19_MON, holidays=[OCT19_MON]
        )
        self.assertEqual(result["reason"], "holiday")
        self.assertIsNone(result["holiday_name"])

    def test_is_business_weekend_precedence_over_holiday(self) -> None:
        # A holiday falling on a weekend day is reported as a weekend.
        result = self.tool.execute(
            mode="is_business",
            date_str=OCT17_SAT,
            holidays={OCT17_SAT: "Observed Saturday"},
        )
        self.assertEqual(result["reason"], "weekend")
        self.assertIsNone(result["holiday_name"])

    def test_is_business_leap_day(self) -> None:
        result = self.tool.execute(mode="is_business", date_str="2028-02-29")
        self.assertEqual(result["weekday"], "Tuesday")
        self.assertTrue(result["is_business"])


class BusinessDayToolNextTest(unittest.TestCase):
    """next mode — next business day strictly after (or same day)."""

    def setUp(self) -> None:
        self.tool = BusinessDayTool()

    def test_next_from_friday_skips_weekend(self) -> None:
        result = self.tool.execute(mode="next", date_str=OCT16_FRI)
        self.assertEqual(
            result,
            {
                "mode": "next",
                "date": OCT16_FRI,
                "weekend": "sat_sun",
                "same_day": False,
                "calendar_days_advanced": 3,
                "result": OCT19_MON,
            },
        )

    def test_next_from_monday_is_strictly_after_by_default(self) -> None:
        result = self.tool.execute(mode="next", date_str=OCT19_MON)
        self.assertEqual(result["result"], OCT20_TUE)
        self.assertEqual(result["calendar_days_advanced"], 1)

    def test_next_same_day_on_business_day(self) -> None:
        result = self.tool.execute(
            mode="next", date_str=OCT19_MON, same_day=True
        )
        self.assertEqual(result["result"], OCT19_MON)
        self.assertEqual(result["calendar_days_advanced"], 0)
        self.assertTrue(result["same_day"])

    def test_next_same_day_on_weekend_rolls_forward(self) -> None:
        result = self.tool.execute(
            mode="next", date_str=OCT17_SAT, same_day=True
        )
        self.assertEqual(result["result"], OCT19_MON)

    def test_next_crosses_month_boundary(self) -> None:
        result = self.tool.execute(mode="next", date_str=OCT30_FRI)
        self.assertEqual(result["result"], NOV02_MON)
        self.assertEqual(result["calendar_days_advanced"], 3)

    def test_next_skips_holiday(self) -> None:
        result = self.tool.execute(
            mode="next", date_str=OCT16_FRI, holidays={OCT19_MON: "Holiday"}
        )
        self.assertEqual(result["result"], OCT20_TUE)

    def test_next_fri_sat_variant_from_thursday(self) -> None:
        result = self.tool.execute(
            mode="next", date_str="2026-10-15", weekend="fri_sat"
        )
        self.assertEqual(result["result"], OCT18_SUN)

    def test_next_from_sunday(self) -> None:
        result = self.tool.execute(mode="next", date_str=NOV01_SUN)
        self.assertEqual(result["result"], NOV02_MON)


class BusinessDayToolValidationTest(unittest.TestCase):
    """Strict input validation — the error matrix."""

    def setUp(self) -> None:
        self.tool = BusinessDayTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    # -- mode and required arguments ---------------------------------- #

    def test_unknown_mode_rejected(self) -> None:
        self.assert_invalid(mode="subtract", date_str=OCT19_MON)
        self.assert_invalid(mode=None)
        self.assert_invalid(mode=7)

    def test_add_requires_date_and_days(self) -> None:
        self.assert_invalid(mode="add", days=1)
        self.assert_invalid(mode="add", date_str=OCT19_MON)
        self.assert_invalid(mode="add", date_str=OCT19_MON, days=None)

    def test_is_business_requires_date(self) -> None:
        self.assert_invalid(mode="is_business")

    def test_next_requires_date(self) -> None:
        self.assert_invalid(mode="next")

    def test_count_requires_start_and_end(self) -> None:
        self.assert_invalid(mode="count", end_date=OCT23_FRI)
        self.assert_invalid(mode="count", start_date=OCT19_MON)

    def test_count_start_after_end_rejected(self) -> None:
        self.assert_invalid(mode="count", start_date=OCT23_FRI, end_date=OCT19_MON)

    # -- date format --------------------------------------------------- #

    def test_malformed_dates_rejected(self) -> None:
        for bad in (
            "2026-13-01",      # month 13
            "2026-00-10",      # month 0
            "2026-02-30",      # non-calendar day
            "2026-02-29",      # Feb 29 of a non-leap year
            "2026-2-3",        # missing zero padding
            "20261019",        # compact form (fromisoformat accepts it)
            "2026-W43-1",      # ISO week form
            "2026/10/19",      # wrong separator
            "2026-10-19 ",     # trailing whitespace
            " 2026-10-19",     # leading whitespace
            "",                # empty
            "2026-10-19T00:00:00",  # datetime, not a date
            42,                # not a string
            None,
            True,
            ["2026-10-19"],
        ):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="is_business", date_str=bad)

    def test_leap_day_accepted_in_leap_year(self) -> None:
        result = self.tool.execute(mode="is_business", date_str="2028-02-29")
        self.assertTrue(result["is_business"])

    def test_count_malformed_dates_rejected(self) -> None:
        self.assert_invalid(mode="count", start_date="2026-1-1", end_date=OCT23_FRI)
        self.assert_invalid(mode="count", start_date=OCT19_MON, end_date="2026-02-30")

    # -- days bounds and types ----------------------------------------- #

    def test_days_out_of_bounds_rejected(self) -> None:
        for bad in (3651, -3651, "3651", "-3651", 100_000):
            self.assert_invalid(mode="add", date_str=OCT19_MON, days=bad)

    def test_days_bounds_accepted(self) -> None:
        upper = self.tool.execute(mode="add", date_str=OCT19_MON, days=3650)
        self.assertEqual(upper["result"], "2040-10-15")
        lower = self.tool.execute(mode="add", date_str=OCT19_MON, days=-3650)
        self.assertEqual(lower["result"], "2012-10-22")

    def test_days_wrong_types_rejected(self) -> None:
        for bad in ("abc", "5.0", " 5", "+5", 5.5, True, False, [3], {"days": 3}):
            self.assert_invalid(mode="add", date_str=OCT19_MON, days=bad)

    # -- weekend preset ------------------------------------------------- #

    def test_unknown_weekend_rejected(self) -> None:
        for bad in ("mon_tue", "weekend", "", "sat", 7, True, ["sat_sun"]):
            self.assert_invalid(mode="is_business", date_str=OCT19_MON, weekend=bad)

    def test_weekend_case_and_space_insensitive(self) -> None:
        for label in ("sat_sun", "SAT_SUN", "Fri_Sat", "SUN_ONLY", " sat_sun "):
            result = self.tool.execute(
                mode="is_business", date_str=OCT19_MON, weekend=label
            )
            self.assertIn(result["weekend"], ("sat_sun", "fri_sat", "sun_only"))

    # -- holidays shape -------------------------------------------------- #

    def test_holidays_wrong_shapes_rejected(self) -> None:
        for bad in (
            42,
            "2026-01-01",            # bare date string, not a list
            {"2026-01-01"},          # set
            [42],
            ["2026-1-1"],
            ["2026-02-30"],
            [["2026-01-01"]],
            ["2026-01-01", None],
            {"2026-01-01": 5},
            {"2026-01-01": ""},
            {"2026-01-01": None},
            {"2026-01-01": True},
            {"2026-02-30": "Bad Day"},
            {7: "Week"},
        ):
            self.assert_invalid(mode="count",
                                start_date=OCT19_MON, end_date=OCT23_FRI,
                                holidays=bad)

    def test_holidays_entry_cap_enforced(self) -> None:
        many = [f"2040-01-{day:02d}" for day in range(1, 32)]
        oversized = many * 33  # 1023 entries -> over the 1000-entry cap
        self.assert_invalid(mode="is_business", date_str=OCT19_MON,
                            holidays=oversized)
        at_cap = many * 32 + many[:8]  # exactly 1000 entries
        result = self.tool.execute(mode="is_business", date_str=OCT19_MON,
                                   holidays=at_cap)
        self.assertTrue(result["is_business"])

    def test_empty_holiday_collections_accepted(self) -> None:
        for empty in ([], (), {}):
            result = self.tool.execute(
                mode="count",
                start_date=OCT19_MON,
                end_date=OCT23_FRI,
                holidays=empty,
            )
            self.assertEqual(result["result"], 5)

    def test_duplicate_holidays_in_list_accepted(self) -> None:
        result = self.tool.execute(
            mode="count",
            start_date=OCT19_MON,
            end_date=OCT23_FRI,
            holidays=[OCT20_TUE, OCT20_TUE],
        )
        self.assertEqual(result["holidays_in_range"], 1)
        self.assertEqual(result["result"], 4)

    # -- boolean flags ---------------------------------------------------- #

    def test_include_ends_and_same_day_must_be_boolean(self) -> None:
        for bad in ("true", 1, 0, [True], "yes"):
            self.assert_invalid(
                mode="count", start_date=OCT19_MON, end_date=OCT23_FRI,
                include_ends=bad,
            )
            self.assert_invalid(mode="next", date_str=OCT19_MON, same_day=bad)

    # -- datetime.date range guards --------------------------------------- #

    def test_add_overflow_beyond_date_max(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="add", date_str="9999-12-31", days=1)

    def test_add_underflow_below_date_min(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="add", date_str="0001-01-01", days=-1)

    def test_add_zero_at_range_boundary_accepted(self) -> None:
        result = self.tool.execute(mode="add", date_str="9999-12-31", days=0)
        self.assertEqual(result["result"], "9999-12-31")

    def test_next_overflow_at_date_max(self) -> None:
        # 9999-12-31 is a Friday — a business day — but next is strict.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="next", date_str="9999-12-31")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="next", date_str="9999-12-31", same_day=False)

    def test_next_same_day_at_date_max_accepted(self) -> None:
        result = self.tool.execute(
            mode="next", date_str="9999-12-31", same_day=True
        )
        self.assertEqual(result["result"], "9999-12-31")


class BusinessDayToolRegistrationTest(unittest.TestCase):
    """Package registration and class metadata."""

    def test_exported_from_common_tool_package(self) -> None:
        self.assertIs(BusinessDayTool, DirectBusinessDayTool)

    def test_tool_metadata(self) -> None:
        tool = BusinessDayTool()
        self.assertEqual(tool.name, "business_day_tool")
        self.assertIn("Business day tool", tool.description)
        self.assertEqual(tool.MODES, ("add", "count", "is_business", "next"))
        self.assertEqual(
            tool.WEEKENDS,
            {"sat_sun": frozenset({5, 6}),
             "fri_sat": frozenset({4, 5}),
             "sun_only": frozenset({6})},
        )
        self.assertEqual(tool.max_days, 3650)
        self.assertEqual(tool.max_holidays, 1000)


if __name__ == "__main__":
    unittest.main()
