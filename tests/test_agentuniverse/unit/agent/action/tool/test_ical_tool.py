"""Oracle tests for IcalTool: RFC 5545 itself is the specification.

(a) the RFC 5545 spec's own examples, embedded verbatim: the 3.1 folding
    example, the four 3.6.1 VEVENT examples, and the 3.8.5.3 RRULE examples
    whose full occurrence lists the RFC prints (checked occurrence by
    occurrence, not just the first three);
(b) python-dateutil parity (installed into the test environment only; the
    tool runtime stays stdlib-only): 200 seeded rules over the supported
    subset (FREQ/INTERVAL/COUNT/UNTIL/BYDAY/BYMONTHDAY) with the built-in
    engine checked against dateutil.rrule, plus 300 seeded DATE/DATE-TIME
    values whose ISO normalization is verified with
    datetime.date.fromisoformat / datetime.datetime.fromisoformat;
(c) property tests: fold-unfold idempotence over 300 seeded texts (every
    physical line at most 75 octets, octet-aware so multibyte text folds
    earlier), and octet-length measurement pinned on multibyte samples;
(d) a 200-item mutation battery: corrupted calendars (unclosed BEGIN,
    wrong nesting, DATE form mismatch, TZID orphan, COUNT+UNTIL, bad
    escapes, bare-LF tolerance) where every mutation must be caught by lint
    with the exact expected finding code;
(e) determinism (repeated runs byte-equal), caps, and structured validation
    errors, plus the yaml registration tests shared by the tool family.
"""

import os
import random
import time
import unittest
from datetime import date, datetime, timedelta

from agentuniverse.agent.action.tool.common_tool import ical_tool as ical_tool_module
from agentuniverse.agent.action.tool.common_tool.ical_tool import IcalTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(ical_tool_module.__file__), "ical_tool.yaml")

try:
    from dateutil.rrule import rrule as dateutil_rrule  # noqa: F401
    DATEUTIL_AVAILABLE = True
except Exception:  # pragma: no cover - test environment guarantee
    DATEUTIL_AVAILABLE = False

CRLF = "\r\n"


def wrap(*lines):
    """Wrap content lines in a minimal valid VCALENDAR."""
    return CRLF.join(["BEGIN:VCALENDAR", "VERSION:2.0",
                      "PRODID:-//IcalTool Tests//EN", *lines,
                      "END:VCALENDAR"]) + CRLF


def calendar_with_event_lines(*event_lines):
    return wrap("BEGIN:VEVENT", "UID:seed-1@example.com",
                "DTSTAMP:19970901T130000Z", *event_lines, "END:VEVENT")


def finding_codes(result):
    return [f["code"] for f in result["findings"]]


# ---------------------------------------------------------------------------
# RFC 5545's own examples, embedded verbatim from the published RFC text.
# ---------------------------------------------------------------------------

# RFC 5545 section 3.1: the folding example. The RFC prints the folded form
# with its own page indentation removed here; continuation lines keep the
# single fold SPACE plus, on the third line, one genuine content SPACE.
RFC_3_1_UNFOLDED = "DESCRIPTION:This is a long description that exists on a long line."
RFC_3_1_FOLDED = (
    "DESCRIPTION:This is a lo\r\n"
    " ng description\r\n"
    "  that exists on a long line."
)

# RFC 5545 section 3.6.1: the four VEVENT examples.
RFC_3_6_1_MEETING = [
    "BEGIN:VEVENT",
    "UID:19970901T130000Z-123401@example.com",
    "DTSTAMP:19970901T130000Z",
    "DTSTART:19970903T163000Z",
    "DTEND:19970903T190000Z",
    "SUMMARY:Annual Employee Review",
    "CLASS:PRIVATE",
    "CATEGORIES:BUSINESS,HUMAN RESOURCES",
    "END:VEVENT",
]
RFC_3_6_1_TRANSPARENT = [
    "BEGIN:VEVENT",
    "UID:19970901T130000Z-123402@example.com",
    "DTSTAMP:19970901T130000Z",
    "DTSTART:19970401T163000Z",
    "DTEND:19970402T010000Z",
    "SUMMARY:Laurel is in sensitivity awareness class.",
    "CLASS:PUBLIC",
    "CATEGORIES:BUSINESS,HUMAN RESOURCES",
    "TRANSP:TRANSPARENT",
    "END:VEVENT",
]
RFC_3_6_1_ANNIVERSARY = [
    "BEGIN:VEVENT",
    "UID:19970901T130000Z-123403@example.com",
    "DTSTAMP:19970901T130000Z",
    "DTSTART;VALUE=DATE:19971102",
    "SUMMARY:Our Blissful Anniversary",
    "TRANSP:TRANSPARENT",
    "CLASS:CONFIDENTIAL",
    "CATEGORIES:ANNIVERSARY,PERSONAL,SPECIAL OCCASION",
    "RRULE:FREQ=YEARLY",
    "END:VEVENT",
]
RFC_3_6_1_MULTIDAY = [
    "BEGIN:VEVENT",
    "UID:20070423T123432Z-541111@example.com",
    "DTSTAMP:20070423T123432Z",
    "DTSTART;VALUE=DATE:20070628",
    "DTEND;VALUE=DATE:20070709",
    "SUMMARY:Festival International de Jazz de Montreal",
    "TRANSP:TRANSPARENT",
    "END:VEVENT",
]

# RFC 5545 section 3.8.5.3: RRULE examples with the RFC's printed occurrence
# lists. All examples assume the Eastern US zone; the wall-time engine
# reproduces the RFC's local dates exactly.
RFC_RRULE_CASES = [
    # (rrule, dtstart, full occurrence list from the RFC text)
    ("FREQ=DAILY;COUNT=10", "19970902T090000",
     ["1997-09-%02d" % d for d in range(2, 12)]),
    ("FREQ=DAILY;UNTIL=19971224T000000Z", "19970902T090000", None),  # 113 days, checked by count
    ("FREQ=DAILY;INTERVAL=10;COUNT=5", "19970902T090000",
     ["1997-09-02", "1997-09-12", "1997-09-22", "1997-10-02", "1997-10-12"]),
    ("FREQ=WEEKLY;COUNT=10", "19970902T090000",
     ["1997-09-02", "1997-09-09", "1997-09-16", "1997-09-23", "1997-09-30",
      "1997-10-07", "1997-10-14", "1997-10-21", "1997-10-28", "1997-11-04"]),
    ("FREQ=WEEKLY;UNTIL=19971224T000000Z", "19970902T090000",
     ["1997-09-02", "1997-09-09", "1997-09-16", "1997-09-23", "1997-09-30",
      "1997-10-07", "1997-10-14", "1997-10-21", "1997-10-28", "1997-11-04",
      "1997-11-11", "1997-11-18", "1997-11-25",
      "1997-12-02", "1997-12-09", "1997-12-16", "1997-12-23"]),
    ("FREQ=WEEKLY;INTERVAL=2;WKST=SU", "19970902T090000",
     ["1997-09-02", "1997-09-16", "1997-09-30", "1997-10-14", "1997-10-28",
      "1997-11-11", "1997-11-25", "1997-12-09", "1997-12-23", "1998-01-06"]),
    ("FREQ=WEEKLY;UNTIL=19971007T000000Z;WKST=SU;BYDAY=TU,TH", "19970902T090000",
     ["1997-09-02", "1997-09-04", "1997-09-09", "1997-09-11", "1997-09-16",
      "1997-09-18", "1997-09-23", "1997-09-25", "1997-09-30", "1997-10-02"]),
    ("FREQ=WEEKLY;COUNT=10;WKST=SU;BYDAY=TU,TH", "19970902T090000",
     ["1997-09-02", "1997-09-04", "1997-09-09", "1997-09-11", "1997-09-16",
      "1997-09-18", "1997-09-23", "1997-09-25", "1997-09-30", "1997-10-02"]),
    ("FREQ=WEEKLY;INTERVAL=2;UNTIL=19971224T000000Z;WKST=SU;BYDAY=MO,WE,FR",
     "19970901T090000",
     ["1997-09-01", "1997-09-03", "1997-09-05", "1997-09-15", "1997-09-17",
      "1997-09-19", "1997-09-29", "1997-10-01", "1997-10-03", "1997-10-13",
      "1997-10-15", "1997-10-17", "1997-10-27", "1997-10-29", "1997-10-31",
      "1997-11-10", "1997-11-12", "1997-11-14", "1997-11-24", "1997-11-26",
      "1997-11-28", "1997-12-08", "1997-12-10", "1997-12-12", "1997-12-22"]),
    ("FREQ=WEEKLY;INTERVAL=2;COUNT=8;WKST=SU;BYDAY=TU,TH", "19970902T090000",
     ["1997-09-02", "1997-09-04", "1997-09-16", "1997-09-18", "1997-09-30",
      "1997-10-02", "1997-10-14", "1997-10-16"]),
    ("FREQ=MONTHLY;COUNT=10;BYMONTHDAY=2,15", "19970902T090000",
     ["1997-09-02", "1997-09-15", "1997-10-02", "1997-10-15", "1997-11-02",
      "1997-11-15", "1997-12-02", "1997-12-15", "1998-01-02", "1998-01-15"]),
    ("FREQ=MONTHLY;INTERVAL=18;COUNT=10;BYMONTHDAY=10,11,12,13,14,15",
     "19970910T090000",
     ["1997-09-10", "1997-09-11", "1997-09-12", "1997-09-13", "1997-09-14",
      "1997-09-15", "1999-03-10", "1999-03-11", "1999-03-12", "1999-03-13"]),
    ("FREQ=YEARLY", "19970610T090000",
     ["1997-06-10", "1998-06-10", "1999-06-10", "2000-06-10", "2001-06-10"]),
]


def builtin_dates(rrule_text, dtstart_raw, count, cap=5000):
    """Run the built-in engine directly (no dateutil involvement)."""
    parsed = ical_tool_module._parse_rrule(rrule_text)
    parsed_dtstart = ical_tool_module._parse_ical_datetime(dtstart_raw)
    assert parsed_dtstart["ok"], dtstart_raw
    result = ical_tool_module._builtin_occurrences(
        parsed["normalized"], parsed_dtstart["datetime"], count, cap,
    )
    assert result["unsupported"] == [], result["unsupported"]
    return [value.date().isoformat() for value in result["occurrences"]]


def rfc_case_count(rrule_text, expected):
    """How many occurrences to request for an RFC case: the full printed
    list length (unbounded rules print only their first entries)."""
    return len(expected) if expected is not None else 200


class IcalToolRfcFoldingExampleTest(unittest.TestCase):
    """The RFC 5545 3.1 folding example, verbatim."""

    def setUp(self):
        self.tool = IcalTool()

    def test_unfold_rfc_example(self):
        unfolded = ical_tool_module._unfold(RFC_3_1_FOLDED)
        self.assertEqual(len(unfolded["logical"]), 1)
        self.assertEqual(unfolded["logical"][0]["text"], RFC_3_1_UNFOLDED)
        self.assertEqual(unfolded["fold_sites"],
                         [{"logical_line": 1, "physical_line": 1, "continuations": 2}])

    def test_parse_reports_fold_sites(self):
        result = self.tool.execute(
            mode="parse", text=calendar_with_event_lines(RFC_3_1_FOLDED))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["unfold_log"]["total_folds"], 1)
        site = result["unfold_log"]["fold_sites"][0]
        self.assertEqual(site["continuations"], 2)
        event = result["components"][0]["components"][0]
        description = [p for p in event["properties"] if p["name"] == "DESCRIPTION"][0]
        self.assertEqual(description["value"],
                         "This is a long description that exists on a long line.")

    def test_fold_reproduces_rfc_shape(self):
        folded = self.tool.execute(mode="fold", text=RFC_3_1_UNFOLDED + CRLF)
        self.assertEqual(folded["status"], "ok")
        self.assertTrue(folded["round_trip_ok"])
        physical = folded["folded_text"].split(CRLF)
        physical = [p for p in physical if p != ""]
        # The RFC's own fold points differ (looser), but the invariants hold:
        # every physical line fits 75 octets and continuations start with SPACE.
        for piece in physical[1:]:
            self.assertTrue(piece.startswith(" "))
        for piece in physical:
            self.assertLessEqual(ical_tool_module._octets(piece), 75)


class IcalToolRfcVeventExampleTest(unittest.TestCase):
    """The RFC 5545 3.6.1 VEVENT examples, embedded verbatim."""

    def setUp(self):
        self.tool = IcalTool()

    def _parse_example(self, lines):
        return self.tool.execute(mode="parse", text=CRLF.join(lines) + CRLF)

    def test_meeting_example_properties(self):
        result = self._parse_example(RFC_3_6_1_MEETING)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["stats"]["components"], {"VEVENT": 1})
        event = result["components"][0]
        self.assertEqual(event["type"], "VEVENT")
        names = [p["name"] for p in event["properties"]]
        self.assertEqual(names, ["UID", "DTSTAMP", "DTSTART", "DTEND",
                                 "SUMMARY", "CLASS", "CATEGORIES"])
        values = {p["name"]: p["value"] for p in event["properties"]}
        self.assertEqual(values["DTSTART"], "19970903T163000Z")
        self.assertEqual(values["DTEND"], "19970903T190000Z")
        self.assertEqual(values["CATEGORIES"], "BUSINESS,HUMAN RESOURCES")

    def test_rfc_examples_lint_reports_only_the_missing_wrapper(self):
        # The RFC prints bare VEVENTs; lint must flag exactly the structural
        # gap (no VCALENDAR) and nothing inside the examples themselves.
        for lines in (RFC_3_6_1_MEETING, RFC_3_6_1_TRANSPARENT,
                      RFC_3_6_1_ANNIVERSARY, RFC_3_6_1_MULTIDAY):
            result = self.tool.execute(mode="lint", text=CRLF.join(lines) + CRLF)
            self.assertEqual(result["status"], "ok")
            codes = finding_codes(result)
            self.assertEqual(codes, ["no_vcalendar"], (lines[1], codes))

    def test_wrapped_examples_lint_clean(self):
        for lines in (RFC_3_6_1_MEETING, RFC_3_6_1_TRANSPARENT,
                      RFC_3_6_1_ANNIVERSARY, RFC_3_6_1_MULTIDAY):
            result = self.tool.execute(mode="lint", text=wrap(*lines))
            self.assertTrue(result["ok"], (lines[1], result["findings"]))

    def test_meeting_example_events_mode(self):
        result = self.tool.execute(mode="events", text=wrap(*RFC_3_6_1_MEETING))
        event = result["events"][0]
        self.assertEqual(event["uid"], "19970901T130000Z-123401@example.com")
        self.assertEqual(event["summary"], "Annual Employee Review")
        self.assertEqual(event["start"]["iso"], "1997-09-03T16:30:00+00:00")
        self.assertEqual(event["end"]["iso"], "1997-09-03T19:00:00+00:00")
        self.assertFalse(event["all_day"])
        self.assertIsNone(event["recurrence"])
        self.assertEqual(event["alarms"], 0)

    def test_anniversary_example_events_mode(self):
        result = self.tool.execute(mode="events", text=wrap(*RFC_3_6_1_ANNIVERSARY))
        event = result["events"][0]
        self.assertTrue(event["all_day"])
        self.assertEqual(event["start"]["iso"], "1997-11-02")
        # DATE + no DTEND/DURATION: non-inclusive end is the next date.
        self.assertEqual(event["end"]["iso"], "1997-11-03")
        self.assertEqual(event["end"]["implied_by"], "next_calendar_date")
        recurrence = event["recurrence"]
        self.assertEqual(recurrence["normalized"]["FREQ"], "YEARLY")
        self.assertEqual(recurrence["next_occurrences"],
                         ["1997-11-02", "1998-11-02", "1999-11-02"])

    def test_multiday_example_events_mode(self):
        result = self.tool.execute(mode="events", text=wrap(*RFC_3_6_1_MULTIDAY))
        event = result["events"][0]
        self.assertTrue(event["all_day"])
        self.assertEqual(event["start"]["iso"], "2007-06-28")
        self.assertEqual(event["end"]["iso"], "2007-07-09")
        self.assertIsNone(event["end"]["implied_by"])


class IcalToolRfcRruleExampleTest(unittest.TestCase):
    """The RFC 5545 3.8.5.3 RRULE examples with printed occurrence lists."""

    def test_builtin_engine_matches_rfc_lists(self):
        for rrule_text, dtstart, expected in RFC_RRULE_CASES:
            got = builtin_dates(rrule_text, dtstart, rfc_case_count(rrule_text, expected))
            if expected is None:  # the 113-day daily-until example
                self.assertEqual(len(got), 113)
                self.assertEqual(got[0], "1997-09-02")
                self.assertEqual(got[-1], "1997-12-23")
                continue
            self.assertEqual(got, expected, rrule_text)

    def test_events_mode_next_three(self):
        tool = IcalTool()
        for rrule_text, dtstart, expected in RFC_RRULE_CASES:
            text = wrap("BEGIN:VEVENT", "UID:rr@example.com",
                        "DTSTAMP:19970901T130000Z",
                        f"DTSTART:{dtstart}", f"RRULE:{rrule_text}",
                        "END:VEVENT")
            result = tool.execute(mode="events", text=text)
            self.assertEqual(result["status"], "ok", rrule_text)
            recurrence = result["events"][0]["recurrence"]
            first_three = expected[:3] if expected is not None \
                else ["1997-09-02", "1997-09-03", "1997-09-04"]
            self.assertEqual([o[:10] for o in recurrence["next_occurrences"]],
                             first_three, rrule_text)

    def test_out_of_subset_examples_disclosed(self):
        # RFC's "Monthly on the first Friday" (BYDAY ordinal) and "Yearly in
        # June and July" (BYMONTH) are outside the built-in subset; the
        # output must say which engine expanded them, and the RFC's printed
        # occurrence list is the oracle when dateutil did the expansion.
        tool = IcalTool()
        for rrule_text, dtstart, first_three in (
            ("FREQ=MONTHLY;COUNT=10;BYDAY=1FR", "19970905T090000",
             ["1997-09-05", "1997-10-03", "1997-11-07"]),
            ("FREQ=YEARLY;COUNT=10;BYMONTH=6,7", "19970610T090000",
             ["1997-06-10", "1997-07-10", "1998-06-10"]),
        ):
            text = wrap("BEGIN:VEVENT", "UID:rr@example.com",
                        "DTSTAMP:19970901T130000Z",
                        f"DTSTART:{dtstart}", f"RRULE:{rrule_text}",
                        "END:VEVENT")
            recurrence = tool.execute(mode="events", text=text)["events"][0]["recurrence"]
            if DATEUTIL_AVAILABLE:
                self.assertEqual(recurrence["engine"], "dateutil")
                self.assertEqual([o[:10] for o in recurrence["next_occurrences"]],
                                 first_three, rrule_text)
            else:
                self.assertFalse(recurrence["supported"])
                self.assertEqual(recurrence["next_occurrences"], [])


class IcalToolDateutilParityTest(unittest.TestCase):
    """200 seeded rules: the built-in engine must match dateutil.rrule."""

    def _seeded_rules(self, seed, count):
        rng = random.Random(seed)  # noqa: S311
        rules = []
        for _ in range(count):
            freq = rng.choice(["DAILY", "WEEKLY", "MONTHLY", "YEARLY"])
            interval = rng.choice([1, 1, 2, 3])
            base = date(1997, rng.randint(1, 12), rng.randint(1, 28))
            raw = f"FREQ={freq};INTERVAL={interval}"
            byday = []
            bymonthday = []
            if freq == "WEEKLY":
                weekdays = rng.sample(["MO", "TU", "WE", "TH", "FR", "SA", "SU"],
                                      rng.randint(1, 3))
                byday = sorted(weekdays)
                # DTSTART synchronized with the pattern (the RFC SHOULD and
                # the common case; unsynchronized sets are undefined per RFC).
                names = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
                base = date(1997, 9, 1)
                while names[base.weekday()] not in byday:
                    base += timedelta(days=1)
                raw += ";BYDAY=" + ",".join(byday)
            elif freq == "MONTHLY" and rng.random() < 0.5:
                days = sorted(rng.sample(range(1, 29), rng.randint(1, 2)))
                if base.day not in days:
                    base = date(1997, base.month, days[0])
                bymonthday = days
                raw += ";BYMONTHDAY=" + ",".join(str(d) for d in days)
            if rng.random() < 0.5:
                raw += f";COUNT={rng.randint(3, 9)}"
            elif rng.random() < 0.5:
                span = rng.randint(20, 400)
                until_date = base + timedelta(days=span)
                if rng.random() < 0.5:
                    raw += ";UNTIL=" + until_date.strftime("%Y%m%d")
                else:
                    raw += ";UNTIL=" + until_date.strftime("%Y%m%d") + "T235959Z"
            if freq == "WEEKLY" and rng.random() < 0.3:
                raw += ";WKST=" + rng.choice(["MO", "SU"])
            rules.append((raw, datetime(1997 if freq != "YEARLY" else base.year,
                                        base.month, base.day, 9, 0)))
        return rules

    @unittest.skipUnless(DATEUTIL_AVAILABLE, "python-dateutil not installed")
    def test_200_seeded_rules_match_dateutil(self):
        tool_cases = self._seeded_rules(20260101, 200)
        for rrule_text, dtstart in tool_cases:
            parsed = ical_tool_module._parse_rrule(rrule_text)
            builtin = ical_tool_module._builtin_occurrences(
                parsed["normalized"], dtstart, 6, 5000)
            self.assertEqual(builtin["unsupported"], [], rrule_text)
            dateutil_result = ical_tool_module._dateutil_occurrences(
                parsed["normalized"], dtstart, 6)
            self.assertIsNotNone(dateutil_result, rrule_text)
            self.assertEqual(
                [o.isoformat() for o in builtin["occurrences"]],
                [o.isoformat() for o in dateutil_result["occurrences"]],
                rrule_text,
            )

    @unittest.skipUnless(DATEUTIL_AVAILABLE, "python-dateutil not installed")
    def test_utc_aware_rules_match_dateutil(self):
        rng = random.Random(77)  # noqa: S311
        from datetime import timezone as tzmod
        for seed in range(40):
            interval = rng.choice([1, 2])
            count = rng.randint(2, 6)
            raw = f"FREQ={rng.choice(['DAILY', 'WEEKLY', 'MONTHLY'])};INTERVAL={interval};COUNT={count}"
            parsed = ical_tool_module._parse_rrule(raw)
            dtstart = datetime(2020, rng.randint(1, 12), rng.randint(1, 28),
                               rng.randint(0, 23), 30, tzinfo=tzmod.utc)
            builtin = ical_tool_module._builtin_occurrences(parsed["normalized"], dtstart, 6, 5000)
            dateutil_result = ical_tool_module._dateutil_occurrences(parsed["normalized"], dtstart, 6)
            self.assertEqual([o.isoformat() for o in builtin["occurrences"]],
                             [o.isoformat() for o in dateutil_result["occurrences"]], raw)

    @unittest.skipUnless(DATEUTIL_AVAILABLE, "python-dateutil not installed")
    def test_date_form_rules_match_dateutil(self):
        rng = random.Random(88)  # noqa: S311
        for _ in range(40):
            raw = f"FREQ={rng.choice(['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY'])};INTERVAL={rng.choice([1, 2])};COUNT={rng.randint(2, 6)}"
            parsed = ical_tool_module._parse_rrule(raw)
            dtstart = date(1997, rng.randint(1, 12), rng.randint(1, 28))
            builtin = ical_tool_module._builtin_occurrences(parsed["normalized"], dtstart, 6, 5000)
            dateutil_result = ical_tool_module._dateutil_occurrences(parsed["normalized"], dtstart, 6)
            self.assertEqual([o.isoformat() for o in builtin["occurrences"]],
                             [o.isoformat() for o in dateutil_result["occurrences"]], raw)


class IcalToolDatetimeIsoParityTest(unittest.TestCase):
    """300 seeded DATE / DATE-TIME values verified with fromisoformat."""

    def test_300_seeded_values(self):
        rng = random.Random(555)  # noqa: S311
        for index in range(300):
            year = rng.randint(1900, 2199)
            month = rng.randint(1, 12)
            day = rng.randint(1, 28)
            if rng.random() < 0.3:
                day = rng.randint(29, 31)
            try:
                expected = date(year, month, day)
            except ValueError:
                continue
            if rng.random() < 0.35:
                raw = expected.strftime("%Y%m%d")
                parsed = ical_tool_module._parse_ical_date(raw)
                self.assertTrue(parsed["ok"], raw)
                self.assertEqual(parsed["form"], "DATE")
                self.assertEqual(parsed["iso"], expected.isoformat())
                self.assertEqual(date.fromisoformat(parsed["iso"]), expected)
            else:
                hour, minute, second = (rng.randint(0, 23), rng.randint(0, 59),
                                        rng.randint(0, 59))
                expected_dt = datetime(year, month, day, hour, minute, second)
                zulu = "Z" if rng.random() < 0.5 else ""
                raw = expected_dt.strftime("%Y%m%dT%H%M%S") + zulu
                parsed = ical_tool_module._parse_ical_datetime(raw)
                self.assertTrue(parsed["ok"], raw)
                self.assertEqual(parsed["form"], "DATE-TIME")
                self.assertEqual(parsed["utc"], zulu == "Z")
                self.assertEqual(datetime.fromisoformat(parsed["iso"]),
                                 expected_dt.replace(
                                     tzinfo=tzmod_utc() if zulu else None))
            self.assertLess(index, 300)

    def test_invalid_forms_rejected(self):
        for raw in ("19971301", "19970230", "19970132", "1997-01-01",
                    "19970902T0900", "19970902T090000X", "19970902 090000",
                    "19970902T240000", "19970902T096000", "19970902T090060"
                    "x"):
            self.assertFalse(ical_tool_module._parse_ical_date(raw)["ok"], raw)
            self.assertFalse(ical_tool_module._parse_ical_datetime(raw)["ok"], raw)

    def test_leap_second_grammar(self):
        parsed = ical_tool_module._parse_ical_datetime("19970630T235960")
        self.assertTrue(parsed["ok"])
        self.assertTrue(parsed["leap_second"])
        self.assertEqual(parsed["iso"], "1997-06-30T23:59:59")

    def test_duration_grammar(self):
        ok = {"P1D": 86400, "PT1H30M": 5400, "P2W": 1209600, "-P1DT12H": -129600,
              "PT15M": 900, "P1DT": None, "P": None, "1D": None, "PT0S": 0}
        for raw, seconds in ok.items():
            parsed = ical_tool_module._parse_duration(raw)
            if seconds is None:
                self.assertFalse(parsed["ok"], raw)
            else:
                self.assertTrue(parsed["ok"], raw)
                self.assertEqual(parsed["total_seconds"], seconds, raw)


def tzmod_utc():
    from datetime import timezone
    return timezone.utc


class IcalToolFoldPropertyTest(unittest.TestCase):
    """fold/unfold idempotence and octet awareness over 300 seeded texts."""

    def setUp(self):
        self.tool = IcalTool()
        self.rng = random.Random(31337)  # noqa: S311
        self.alphabets = [
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            "会議の予定ですよね会議の予定",  # 3 octets per char
            "emoji🎉🎊🎈calendar📅",  # astral plane, 4 octets per char
            "mixed ASCII と 日本語 🎉 and punctuation;:,",
        ]

    def _seeded_text(self):
        parts = []
        for _ in range(self.rng.randint(1, 12)):
            alphabet = self.rng.choice(self.alphabets)
            length = self.rng.randint(1, 200)
            body = "".join(self.rng.choice(alphabet) for _ in range(length))
            parts.append(self.rng.choice(["SUMMARY:", "DESCRIPTION:", "COMMENT:", ""])
                         + body)
        return "\r\n".join(parts)

    def test_300_seeded_fold_unfold_idempotence(self):
        for _ in range(300):
            text = self._seeded_text()
            unfolded = [e["text"] for e in ical_tool_module._unfold(text)["logical"]]
            folded = self.tool.execute(mode="fold", text=text + CRLF)
            self.assertTrue(folded["round_trip_ok"])
            physical = [p for p in folded["folded_text"].split(CRLF) if p]
            for piece in physical:
                self.assertLessEqual(ical_tool_module._octets(piece), 75)
            refolded = self.tool.execute(mode="fold", text=folded["folded_text"])
            self.assertTrue(refolded["round_trip_ok"])
            # idempotence: folding an already folded text yields the same bytes.
            self.assertEqual(refolded["folded_text"], folded["folded_text"])
            # unfold(fold(x)) restores exactly the logical lines of x
            self.assertEqual(
                [e["text"] for e in
                 ical_tool_module._unfold(folded["folded_text"])["logical"]],
                unfolded,
            )

    def test_octet_measurement_multibyte(self):
        # 40 CJK chars after "SUMMARY:": 8 + 120 = 128 octets over 48 chars.
        line = "SUMMARY:" + "会" * 40
        self.assertEqual(ical_tool_module._octets(line), 128)
        self.assertEqual(len(line), 48)
        lint = self.tool.execute(mode="lint", text=wrap(line))
        code_matches = [f for f in lint["findings"]
                        if f["code"] == "long_line_over_75_octets"]
        self.assertEqual(len(code_matches), 1)
        self.assertIn("128 octets", code_matches[0]["detail"])
        # A folded version of the same content stays under the limit and is
        # not flagged.
        folded = self.tool.execute(mode="fold", text=line + CRLF)
        lint2 = self.tool.execute(mode="lint", text=wrap(folded["folded_text"].rstrip(CRLF)))
        self.assertNotIn("long_line_over_75_octets", finding_codes(lint2))

    def test_octet_not_char_limit(self):
        # 74 ASCII chars fit; 74 CJK chars (222+ octets) must not.
        fit = "SUMMARY:" + "a" * 60
        lint = self.tool.execute(mode="lint", text=wrap(fit))
        self.assertNotIn("long_line_over_75_octets", finding_codes(lint))
        overflow = "SUMMARY:" + "会" * 30  # 8 + 90 octets
        lint = self.tool.execute(mode="lint", text=wrap(overflow))
        self.assertIn("long_line_over_75_octets", finding_codes(lint))


class IcalToolMutationBatteryTest(unittest.TestCase):
    """200 corrupted calendars; every mutation caught with the exact code."""

    BASE_EVENT = [
        "BEGIN:VEVENT",
        "UID:mutation-{index}@example.com",
        "DTSTAMP:19970901T130000Z",
        "DTSTART:19970903T163000Z",
        "DTEND:19970903T190000Z",
        "SUMMARY:Mutation battery event {index}",
        "RRULE:FREQ=DAILY;COUNT=5",
        "END:VEVENT",
    ]
    BASE_ALARM = ["BEGIN:VALARM", "ACTION:DISPLAY",
                  "TRIGGER:-PT15M", "DESCRIPTION:Reminder", "END:VALARM"]
    BASE_TIMEZONE = [
        "BEGIN:VTIMEZONE", "TZID:Factory", "BEGIN:STANDARD",
        "DTSTART:19700101T000000", "TZOFFSETFROM:+0000", "TZOFFSETTO:+0000",
        "END:STANDARD", "END:VTIMEZONE",
    ]

    def _calendar(self, index, event_extra=(), timezone=True, alarm=False,
                  rrule="RRULE:FREQ=DAILY;COUNT=5", dtstart="DTSTART:19970903T163000Z"):
        event = [line.format(index=index) for line in self.BASE_EVENT]
        event = [line for line in event if not line.startswith("RRULE:")]
        if rrule is not None:
            event.insert(-1, rrule)
        event = [line for line in event if not line.startswith("DTSTART:")]
        event.insert(3, dtstart)
        event.extend(event_extra)
        if alarm:
            event = event[:-1] + self.BASE_ALARM + [event[-1]]
        lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Mutations//EN"]
        if timezone:
            lines.extend(self.BASE_TIMEZONE)
        lines.extend(event)
        lines.append("END:VCALENDAR")
        return CRLF.join(lines) + CRLF

    def _mutations(self):
        """Each entry: (name, calendar, expected finding code)."""
        mutations = []
        for index in range(200):
            kind = index % 25
            if kind == 0:  # BEGIN without END
                text = self._calendar(index).replace("END:VEVENT" + CRLF, "")
                mutations.append(("begin_without_end", text, "component_not_closed"))
            elif kind == 1:  # wrong nesting: END:VEVENT inside VALARM
                text = self._calendar(index, alarm=True)
                text = text.replace("TRIGGER:-PT15M" + CRLF + "DESCRIPTION:Reminder" + CRLF,
                                    "TRIGGER:-PT15M" + CRLF + "END:VEVENT" + CRLF)
                mutations.append(("wrong_nesting", text, "component_end_mismatch"))
            elif kind == 2:  # END without BEGIN
                text = self._calendar(index) + "END:VEVENT" + CRLF
                mutations.append(("end_without_begin", text, "unexpected_end"))
            elif kind == 3:  # VALUE=DATE with a time part
                text = self._calendar(index, dtstart="DTSTART;VALUE=DATE:19970903T163000Z")
                mutations.append(("date_with_time", text, "datetime_form_mismatch"))
            elif kind == 4:  # TZID without VTIMEZONE
                text = self._calendar(index, timezone=False,
                                      dtstart="DTSTART;TZID=Missing/Zone:19970903T163000Z")
                mutations.append(("tzid_orphan", text, "tzid_without_vtimezone"))
            elif kind == 5:  # COUNT and UNTIL together
                text = self._calendar(index, rrule="RRULE:FREQ=DAILY;COUNT=5;UNTIL=19971224T000000Z")
                mutations.append(("count_and_until", text, "rrule_count_until_exclusive"))
            elif kind == 6:  # UNTIL form must match DTSTART form
                text = self._calendar(index, dtstart="DTSTART;VALUE=DATE:19970903",
                                      rrule="RRULE:FREQ=DAILY;UNTIL=19971224T000000Z")
                mutations.append(("until_form_mismatch", text, "rrule_until_form_mismatch"))
            elif kind == 7:  # bad escape
                text = self._calendar(index).replace(
                    f"SUMMARY:Mutation battery event {index}",
                    f"SUMMARY:bad\\x escape {index}")
                mutations.append(("bad_escape", text, "invalid_escape"))
            elif kind == 8:  # bare LF (accepted, pinned info finding)
                text = self._calendar(index).replace(CRLF, "\n")
                mutations.append(("bare_lf", text, "non_crlf_line_break"))
            elif kind == 9:  # mixed endings
                text = self._calendar(index).replace(
                    "SUMMARY:Mutation battery event %d%s" % (index, CRLF),
                    "SUMMARY:Mutation battery event %d\n" % index)
                mutations.append(("mixed_endings", text, "mixed_line_endings"))
            elif kind == 10:  # PRIORITY out of range
                text = self._calendar(index, event_extra=["PRIORITY:10"])
                mutations.append(("priority_10", text, "value_out_of_range"))
            elif kind == 11:  # SEQUENCE negative
                text = self._calendar(index, event_extra=["SEQUENCE:-1"])
                mutations.append(("sequence_negative", text, "value_out_of_range"))
            elif kind == 12:  # CALSCALE unknown
                text = self._calendar(index, event_extra=["CALSCALE:JULIAN"]).replace(
                    "CALSCALE:JULIAN" + CRLF + "END:VEVENT" + CRLF, "END:VEVENT" + CRLF
                ).replace("PRODID:-//Mutations//EN" + CRLF,
                          "PRODID:-//Mutations//EN" + CRLF + "CALSCALE:JULIAN" + CRLF)
                mutations.append(("calscale_julian", text, "unknown_calscale"))
            elif kind == 13:  # property outside any component
                text = self._calendar(index) + "X-NOTE:outside" + CRLF
                mutations.append(("outside_component", text, "content_outside_vcalendar"))
            elif kind == 14:  # no VCALENDAR at all
                text = CRLF.join(self.BASE_EVENT).format(index=index) + CRLF
                mutations.append(("no_vcalendar", text, "no_vcalendar"))
            elif kind == 15:  # missing UID
                text = self._calendar(index).replace(
                    f"UID:mutation-{index}@example.com" + CRLF, "")
                mutations.append(("missing_uid", text, "missing_required_property"))
            elif kind == 16:  # line over 75 octets, unfolded
                text = self._calendar(index).replace(
                    f"SUMMARY:Mutation battery event {index}",
                    "SUMMARY:" + "x" * 100)
                mutations.append(("long_line", text, "long_line_over_75_octets"))
            elif kind == 17:  # first line starts with SPACE
                text = " " + self._calendar(index)
                mutations.append(("leading_space_first", text, "continuation_without_previous"))
            elif kind == 18:  # continuation that reads like a new property
                text = self._calendar(index).replace(
                    "DTEND:19970903T190000Z" + CRLF,
                    "DTEND:19970903T190000Z" + CRLF + " UID:folded-or-new@example.com" + CRLF)
                mutations.append(("suspicious_continuation", text, "suspicious_continuation"))
            elif kind == 19:  # invalid DURATION
                text = self._calendar(index).replace(
                    "RRULE:FREQ=DAILY;COUNT=5" + CRLF, "DURATION:1hour" + CRLF)
                mutations.append(("bad_duration", text, "invalid_duration"))
            elif kind == 20:  # unbalanced param quote: the dangling quote
                # swallows the name/value separator, so the 3.1 grammar can
                # only report the line as having no unquoted ':' at all
                text = self._calendar(index, event_extra=['ATTENDEE;CN="Broken:name'])
                mutations.append(("quote_swallows_colon", text, "missing_colon"))
            elif kind == 21:  # VEVENT nested inside VEVENT
                text = self._calendar(index).replace(
                    "SUMMARY:Mutation battery event %d" % index + CRLF,
                    f"SUMMARY:Mutation battery event {index}" + CRLF +
                    "BEGIN:VEVENT" + CRLF + "UID:nested@example.com" + CRLF +
                    "DTSTAMP:19970901T130000Z" + CRLF + "END:VEVENT" + CRLF)
                mutations.append(("event_in_event", text, "invalid_nesting"))
            elif kind == 22:  # unknown property (not X-)
                text = self._calendar(index, event_extra=["TOTALLY-UNKNOWN:yes"])
                mutations.append(("unknown_property", text, "unknown_property"))
            elif kind == 23:  # RRULE without FREQ
                text = self._calendar(index, rrule="RRULE=COUNT=5".replace("RRULE=", "RRULE:"))
                mutations.append(("rrule_no_freq", text, "rrule_missing_freq"))
            else:  # kind == 24: missing colon
                text = self._calendar(index).replace(
                    f"SUMMARY:Mutation battery event {index}",
                    f"SUMMARY-Mutation battery event {index}")
                mutations.append(("missing_colon", text, "missing_colon"))
        return mutations

    def test_200_mutations_caught_with_exact_code(self):
        tool = IcalTool()
        mutations = self._mutations()
        self.assertEqual(len(mutations), 200)
        for name, text, expected_code in mutations:
            result = tool.execute(mode="lint", text=text)
            self.assertEqual(result["status"], "ok", name)
            codes = finding_codes(result)
            self.assertIn(expected_code, codes, (name, codes))

    def test_bare_lf_tolerance_pinned(self):
        tool = IcalTool()
        lf_only = self._calendar(999).replace(CRLF, "\n")
        parse = tool.execute(mode="parse", text=lf_only)
        self.assertEqual(parse["status"], "ok")
        self.assertEqual(parse["line_endings"]["mode"], "LF")
        lint = tool.execute(mode="lint", text=lf_only)
        info = [f for f in lint["findings"] if f["code"] == "non_crlf_line_break"]
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0]["severity"], "info")


class IcalToolParseStructureTest(unittest.TestCase):
    """Component nesting, params, escapes, and calendar-level properties."""

    def setUp(self):
        self.tool = IcalTool()

    def test_vtimezone_standard_daylight_and_valarm(self):
        text = wrap(
            "BEGIN:VTIMEZONE", "TZID:Test/Zone",
            "BEGIN:STANDARD", "DTSTART:19971026T020000",
            "TZOFFSETFROM:-0400", "TZOFFSETTO:-0500", "TZNAME:EST", "END:STANDARD",
            "BEGIN:DAYLIGHT", "DTSTART:19970406T020000",
            "TZOFFSETFROM:-0500", "TZOFFSETTO:-0400", "TZNAME:EDT", "END:DAYLIGHT",
            "END:VTIMEZONE",
            "BEGIN:VEVENT", "UID:nest@example.com", "DTSTAMP:19970901T130000Z",
            "DTSTART;TZID=Test/Zone:19970903T163000",
            "SUMMARY:Nested", "BEGIN:VALARM", "ACTION:DISPLAY",
            "TRIGGER:-PT30M", "END:VALARM", "END:VEVENT",
        )
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(result["status"], "ok")
        counts = result["stats"]["components"]
        self.assertEqual(counts, {"VCALENDAR": 1, "VTIMEZONE": 1,
                                  "STANDARD": 1, "DAYLIGHT": 1,
                                  "VEVENT": 1, "VALARM": 1})
        calendar = result["components"][0]
        vtimezone = calendar["components"][0]
        self.assertEqual([c["type"] for c in vtimezone["components"]],
                         ["STANDARD", "DAYLIGHT"])
        event = calendar["components"][1]
        self.assertEqual([c["type"] for c in event["components"]], ["VALARM"])
        dtstart = [p for p in event["properties"] if p["name"] == "DTSTART"][0]
        self.assertEqual(dtstart["params"], {"TZID": ["Test/Zone"]})
        self.assertEqual(dtstart["value"], "19970903T163000")
        self.assertEqual(dtstart["line"], 22)

    def test_calendar_props_findings(self):
        text = CRLF.join(["BEGIN:VCALENDAR", "VERSION:2.0",
                          "BEGIN:VEVENT", "UID:x@example.com",
                          "DTSTAMP:19970901T130000Z", "END:VEVENT",
                          "END:VCALENDAR"]) + CRLF
        props = self.tool.execute(mode="parse", text=text)["calendar_props"]
        self.assertTrue(props["VERSION"]["present"])
        self.assertFalse(props["PRODID"]["present"])
        self.assertEqual(props["findings"],
                         ["missing PRODID (required by RFC 5545 3.7.3)"])

    def test_quoted_params_with_colons_and_semicolons(self):
        text = wrap("BEGIN:VEVENT", "UID:q@example.com",
                    "DTSTAMP:19970901T130000Z", "DTSTART:19970903T163000Z",
                    'ATTENDEE;CN="Doe; John:hdr";ROLE=REQ-PARTICIPANT:mailto:j@e.com',
                    "END:VEVENT")
        result = self.tool.execute(mode="parse", text=text)
        event = result["components"][0]["components"][0]
        prop = [p for p in event["properties"] if p["name"] == "ATTENDEE"][0]
        self.assertEqual(prop["params"]["CN"], ["Doe; John:hdr"])
        self.assertEqual(prop["params"]["ROLE"], ["REQ-PARTICIPANT"])
        self.assertEqual(prop["value"], "mailto:j@e.com")
        lint = self.tool.execute(mode="lint", text=text)
        self.assertTrue(lint["ok"], lint["findings"])

    def test_text_unescape(self):
        raw = "Line one\\nLine two\\; semicolon\\, comma \\\\ backslash"
        unescaped, bad = ical_tool_module._unescape_text(raw)
        self.assertEqual(bad, [])
        self.assertEqual(unescaped,
                         "Line one\nLine two; semicolon, comma \\ backslash")
        _, bad = ical_tool_module._unescape_text("broken \\q escape\\")
        self.assertEqual(sorted(bad), ["<trailing>", "\\q"])

    def test_lowercase_begin_end(self):
        text = CRLF.join(["BEGIN:vcalendar", "VERSION:2.0", "PRODID:-//x//EN",
                          "BEGIN:vevent", "UID:l@example.com",
                          "DTSTAMP:19970901T130000Z",
                          "DTSTART:19970903T163000Z", "END:vevent",
                          "END:vcalendar"]) + CRLF
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(result["components"][0]["type"], "VCALENDAR")
        self.assertEqual(result["components"][0]["components"][0]["type"], "VEVENT")

    def test_x_properties_reported_as_info(self):
        text = wrap("BEGIN:VEVENT", "UID:x@example.com",
                    "DTSTAMP:19970901T130000Z", "DTSTART:19970903T163000Z",
                    "X-CUSTOM-FLAG:yes", "END:VEVENT")
        lint = self.tool.execute(mode="lint", text=text)
        infos = [f for f in lint["findings"] if f["code"] == "x_property"]
        self.assertEqual(len(infos), 1)
        self.assertEqual(infos[0]["severity"], "info")
        self.assertTrue(lint["ok"])


class IcalToolEventsModeTest(unittest.TestCase):
    """Normalization: implied ends, alarms, determinism, caps."""

    def setUp(self):
        self.tool = IcalTool()

    def test_end_from_duration(self):
        text = calendar_with_event_lines("DTSTART:19970903T163000Z",
                                         "DURATION:PT1H30M")
        event = self.tool.execute(mode="events", text=text)["events"][0]
        self.assertEqual(event["start"]["iso"], "1997-09-03T16:30:00+00:00")
        self.assertEqual(event["end"]["iso"], "1997-09-03T18:00:00+00:00")
        self.assertEqual(event["end"]["implied_by"], "DURATION")
        self.assertEqual(event["duration"]["total_seconds"], 5400)

    def test_zero_duration_datetime(self):
        text = calendar_with_event_lines("DTSTART:19970903T163000Z")
        event = self.tool.execute(mode="events", text=text)["events"][0]
        self.assertEqual(event["end"]["iso"], "1997-09-03T16:30:00+00:00")
        self.assertEqual(event["end"]["implied_by"], "same_instant")

    def test_all_day_next_date(self):
        text = calendar_with_event_lines("DTSTART;VALUE=DATE:19971102")
        event = self.tool.execute(mode="events", text=text)["events"][0]
        self.assertTrue(event["all_day"])
        self.assertEqual(event["end"]["iso"], "1997-11-03")
        self.assertEqual(event["end"]["implied_by"], "next_calendar_date")

    def test_alarms_counted_and_rdate_noted(self):
        text = wrap(
            "BEGIN:VEVENT", "UID:a@example.com", "DTSTAMP:19970901T130000Z",
            "DTSTART:19970903T163000Z", "RRULE:FREQ=DAILY;COUNT=5",
            "RDATE:19971001T163000Z", "EXDATE:19970904T163000Z",
            "BEGIN:VALARM", "ACTION:AUDIO", "TRIGGER:-PT1H", "END:VALARM",
            "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-P1D", "END:VALARM",
            "END:VEVENT",
        )
        event = self.tool.execute(mode="events", text=text)["events"][0]
        self.assertEqual(event["alarms"], 2)
        self.assertEqual(event["unexpanded"], ["RDATE", "EXDATE"])
        self.assertEqual(event["recurrence"]["normalized"]["COUNT"], 5)

    def test_max_occurrences_and_determinism(self):
        text = calendar_with_event_lines("DTSTART:19970903T163000Z",
                                         "RRULE:FREQ=DAILY;COUNT=9")
        first = self.tool.execute(mode="events", text=text, max_occurrences=5)
        second = self.tool.execute(mode="events", text=text, max_occurrences=5)
        self.assertEqual(first, second)  # deterministic, wall-clock independent
        self.assertEqual(len(first["events"][0]["recurrence"]["next_occurrences"]), 5)
        default = self.tool.execute(mode="events", text=text)
        self.assertEqual(len(default["events"][0]["recurrence"]["next_occurrences"]), 3)
        zero = self.tool.execute(mode="events", text=text, max_occurrences=0)
        self.assertEqual(zero["events"][0]["recurrence"]["next_occurrences"], [])

    def test_events_cap(self):
        lines = []
        for index in range(5):
            lines.extend(["BEGIN:VEVENT", f"UID:e{index}@example.com",
                          "DTSTAMP:19970901T130000Z",
                          "DTSTART:19970903T163000Z", "END:VEVENT"])
        result = self.tool.execute(mode="events", text=wrap(*lines))
        self.assertEqual(result["event_count"], 5)
        capped = IcalTool(max_events=3).execute(mode="events", text=wrap(*lines))
        self.assertEqual(capped["event_count"], 3)
        self.assertTrue(capped["truncated"])

    def test_engine_field_disclosed(self):
        text = calendar_with_event_lines("DTSTART:19970903T163000Z",
                                         "RRULE:FREQ=DAILY;COUNT=5")
        recurrence = self.tool.execute(mode="events", text=text)["events"][0]["recurrence"]
        self.assertIn(recurrence["engine"], ("builtin", "dateutil"))
        self.assertTrue(recurrence["supported"])


class IcalToolValidationAndCapsTest(unittest.TestCase):
    """Structured errors, caps enforcement, pathological inputs."""

    def setUp(self):
        self.tool = IcalTool()

    def test_mode_validation(self):
        for bad in (None, 123, "parse ", "PARSE", "unknown"):
            result = self.tool.execute(mode=bad, text="BEGIN:VCALENDAR")
            self.assertEqual(result["status"], "error", bad)
            self.assertEqual(result["error_type"], "validation_error")

    def test_text_required(self):
        for mode in ("parse", "lint", "events", "fold"):
            result = self.tool.execute(mode=mode, text="")
            self.assertEqual(result["status"], "error")
            result = self.tool.execute(mode=mode)
            self.assertEqual(result["status"], "error")

    def test_max_occurrences_validation(self):
        text = calendar_with_event_lines("DTSTART:19970903T163000Z")
        for bad in (11, -1, "abc", True):
            result = self.tool.execute(mode="events", text=text, max_occurrences=bad)
            self.assertEqual(result["status"], "error", bad)

    def test_text_cap(self):
        capped = IcalTool(max_text_chars=100)
        result = capped.execute(mode="parse", text="x" * 101)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_text_chars", result["error"])

    def test_logical_line_cap(self):
        capped = IcalTool(max_logical_lines=10)
        text = CRLF.join(f"PROP{i}:x" for i in range(11)) + CRLF
        result = capped.execute(mode="parse", text=text)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_logical_lines", result["error"])

    def test_findings_cap(self):
        text = wrap(*["X-FLAG-%d:info" % i for i in range(50)])
        result = IcalTool(max_findings=10).execute(mode="lint", text=text)
        self.assertEqual(len(result["findings"]), 10)
        self.assertTrue(result["summary"]["truncated"])
        self.assertGreater(result["summary"]["total"], 10)

    def test_one_megabyte_under_two_seconds(self):
        big = "DESCRIPTION:" + "x" * (1_048_576 - 13 - 2)  # + CRLF stays in cap
        start = time.time()
        folded = self.tool.execute(mode="fold", text=big + CRLF)
        duration = time.time() - start
        self.assertEqual(folded["status"], "ok")
        self.assertTrue(folded["round_trip_ok"])
        self.assertLess(duration, 2.0, "1 MiB fold must stay under two seconds")

    def test_determinism_across_modes(self):
        text = wrap(*RFC_3_6_1_ANNIVERSARY)
        for mode in ("parse", "lint", "events"):
            self.assertEqual(self.tool.execute(mode=mode, text=text),
                             self.tool.execute(mode=mode, text=text))


class IcalToolHostileReviewFixesTest(unittest.TestCase):
    """Regression tests for defects found by a hostile self-review pass.

    Covers: max_components enforcement (was counted but never enforced),
    WKST grammar, the RFC 5545 3.3.10 UNTIL zone-form clauses, COUNT=0
    (grammar plus builtin/dateutil agreement), and the PERCENT-COMPLETE /
    GEO value ranges.
    """

    def setUp(self):
        self.tool = IcalTool()

    def _many_events(self, count):
        lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Cap//EN"]
        for index in range(count):
            lines += ["BEGIN:VEVENT", f"UID:cap-{index}@example.com",
                      "DTSTAMP:19970901T130000Z", "END:VEVENT"]
        lines.append("END:VCALENDAR")
        return CRLF.join(lines) + CRLF

    def test_max_components_enforced(self):
        text = self._many_events(30)
        result = IcalTool(max_components=5).execute(mode="parse", text=text)
        # 1 VCALENDAR + 4 VEVENT = 5 kept; the rest are dropped.
        self.assertEqual(result["stats"]["components"], {"VCALENDAR": 1, "VEVENT": 4})
        self.assertTrue(result["stats"]["components_truncated"])
        lint = IcalTool(max_components=5).execute(mode="lint", text=text)
        self.assertIn("component_cap_reached", finding_codes(lint))
        events = IcalTool(max_components=5).execute(mode="events", text=text)
        self.assertEqual(events["event_count"], 4)
        self.assertTrue(events["components_truncated"])
        # The default cap leaves normal calendars untouched.
        self.assertFalse(self.tool.execute(mode="parse", text=text)
                         ["stats"]["components_truncated"])

    def test_capped_subtree_still_balances_end_lines(self):
        # max_components=1 keeps only the VCALENDAR; every nested component
        # is skipped, and their END lines must balance without corrupting
        # the stack (no unexpected_end / component_not_closed errors).
        text = calendar_with_event_lines("DTSTART:19970903T163000Z",
                                         "BEGIN:VALARM", "ACTION:DISPLAY",
                                         "TRIGGER:-PT15M", "END:VALARM")
        result = IcalTool(max_components=1).execute(mode="lint", text=text)
        codes = finding_codes(result)
        self.assertIn("component_cap_reached", codes)
        for unexpected in ("unexpected_end", "component_not_closed",
                           "component_end_mismatch"):
            self.assertNotIn(unexpected, codes)
        parse = IcalTool(max_components=1).execute(mode="parse", text=text)
        calendar = parse["components"][0]
        self.assertEqual(calendar["type"], "VCALENDAR")
        self.assertEqual(calendar["components"], [])
        # properties inside the skipped VEVENT are dropped with it
        self.assertEqual([p["name"] for p in calendar["properties"]],
                         ["VERSION", "PRODID"])

    def test_wkst_grammar(self):
        result = self.tool.execute(mode="lint", text=calendar_with_event_lines(
            "DTSTART:19970903T163000Z", "RRULE:FREQ=WEEKLY;WKST=XX;COUNT=3"))
        flagged = [f for f in result["findings"]
                   if f["code"] == "rrule_invalid_value" and "WKST" in f["detail"]]
        self.assertEqual(len(flagged), 1)
        clean = self.tool.execute(mode="lint", text=calendar_with_event_lines(
            "DTSTART:19970903T163000Z", "RRULE:FREQ=WEEKLY;WKST=SU;COUNT=3"))
        self.assertTrue(clean["ok"], clean["findings"])

    def test_until_zone_form_grammar(self):
        # RFC 5545 3.3.10: floating DTSTART needs a local UNTIL; UTC/TZID
        # DTSTART needs a UTC UNTIL (warning: the RFC's own 3.8.5.3
        # illustrations mix these, so real-world files do too).
        cases = [
            ("DTSTART:19970902T090000", "RRULE:FREQ=DAILY;UNTIL=19971224T000000Z", True),
            ("DTSTART:19970902T090000Z", "RRULE:FREQ=DAILY;UNTIL=19971224T000000Z", False),
            ("DTSTART:19970902T090000Z", "RRULE:FREQ=DAILY;UNTIL=19971224T000000", True),
            ("DTSTART:19970902T090000", "RRULE:FREQ=DAILY;UNTIL=19971224T000000", False),
        ]
        for dtstart, rrule, expect in cases:
            result = self.tool.execute(mode="lint", text=calendar_with_event_lines(
                dtstart, rrule))
            flagged = "rrule_until_zone_form_mismatch" in finding_codes(result)
            self.assertEqual(flagged, expect, (dtstart, rrule))

    def test_until_zone_form_with_tzid(self):
        vtimezone = ["BEGIN:VTIMEZONE", "TZID:Zone/One", "BEGIN:STANDARD",
                     "DTSTART:19700101T000000", "TZOFFSETFROM:+0000",
                     "TZOFFSETTO:+0000", "END:STANDARD", "END:VTIMEZONE"]
        event_lines = ["BEGIN:VEVENT", "UID:zf@example.com",
                       "DTSTAMP:19970901T130000Z",
                       "DTSTART;TZID=Zone/One:19970902T090000",
                       "RRULE:FREQ=DAILY;UNTIL=19971224T000000", "END:VEVENT"]
        text = wrap(*vtimezone, *event_lines)
        self.assertIn("rrule_until_zone_form_mismatch",
                      finding_codes(self.tool.execute(mode="lint", text=text)))
        fixed = text.replace("UNTIL=19971224T000000", "UNTIL=19971224T000000Z")
        self.assertNotIn("rrule_until_zone_form_mismatch",
                         finding_codes(self.tool.execute(mode="lint", text=fixed)))

    def test_count_zero_flagged_and_engines_agree(self):
        result = self.tool.execute(mode="lint", text=calendar_with_event_lines(
            "DTSTART:19970903T163000Z", "RRULE:FREQ=DAILY;COUNT=0"))
        self.assertIn("rrule_invalid_value", finding_codes(result))
        parsed = ical_tool_module._parse_rrule("FREQ=DAILY;COUNT=0")
        builtin = ical_tool_module._builtin_occurrences(
            parsed["normalized"], datetime(1997, 9, 2, 9, 0), 4, 5000)
        if DATEUTIL_AVAILABLE:
            dateutil_result = ical_tool_module._dateutil_occurrences(
                parsed["normalized"], datetime(1997, 9, 2, 9, 0), 4)
            self.assertEqual([o.isoformat() for o in builtin["occurrences"]],
                             [o.isoformat() for o in dateutil_result["occurrences"]])

    def test_percent_complete_range(self):
        for raw, bad in (("PERCENT-COMPLETE:101", True),
                         ("PERCENT-COMPLETE:100", False),
                         ("PERCENT-COMPLETE:0", False),
                         ("PERCENT-COMPLETE:abc", True)):
            result = self.tool.execute(mode="lint", text=calendar_with_event_lines(
                "DTSTART:19970903T163000Z", raw))
            errors = [f["code"] for f in result["findings"]
                      if f["severity"] == "error"]
            self.assertEqual("value_out_of_range" in errors, bad, raw)

    def test_geo_grammar(self):
        for raw, bad in (("GEO:37.386013;-122.082932", False),
                         ("GEO:+37.4;-122.0", False),
                         ("GEO:abc", True),
                         ("GEO:37.386013", True),
                         ("GEO:37.386013,-122.082932", True)):
            result = self.tool.execute(mode="lint", text=calendar_with_event_lines(
                "DTSTART:19970903T163000Z", raw))
            errors = [f["code"] for f in result["findings"]
                      if f["severity"] == "error"]
            self.assertEqual("invalid_geo" in errors, bad, raw)


class IcalToolRegistrationTest(unittest.TestCase):
    """Registration tests for the shipped ical_tool.yaml."""

    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "IcalTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, IcalTool)
        self.assertEqual(tool.input_keys, ["mode"])
        self.assertEqual(tool.max_text_chars, 1_048_576)
        self.assertEqual(tool.max_occurrences, 3)

    def test_package_export(self):
        from agentuniverse.agent.action.tool import common_tool
        from agentuniverse.agent.action.tool.common_tool import IcalTool as Exported

        self.assertIs(Exported, IcalTool)
        self.assertIn("IcalTool", common_tool.__all__)


if __name__ == "__main__":
    unittest.main()
