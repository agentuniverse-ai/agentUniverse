#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_log_lint_tool.py

"""Offline unit tests for LogLintTool.

The tool is built purely on the standard library and never touches
the network, so this suite runs fully offline. Every assertion is
deterministic and checked against ground truths derived
independently of the tool's implementation: hand-counted format
votes and drift counts over realistic multi-format logs, hand-done
timestamp arithmetic (including tz-aware to UTC normalization and
tz-less wall-clock spans), hand-evaluated level sequences (with the
stack-trace exemption), hand-drawn hour buckets, and a full
validation error matrix.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import LogLintTool
from agentuniverse.agent.action.tool.common_tool.log_lint_tool import (
    LogLintTool as DirectLogLintTool,
)


def codes(result):
    """The ordered list of finding (code, severity, line) triples."""
    return [
        (f["code"], f["severity"], f["line"]) for f in result["findings"]
    ]


# --------------------------------------------------------------------- #
# Audit fixtures
# --------------------------------------------------------------------- #
CLEAN_LEVELED = "\n".join(
    [
        "2026-10-19T10:00:00Z INFO app.worker boot complete",
        "2026-10-19T10:00:30Z INFO app.worker ready",
        "2026-10-19T10:01:00Z WARN app.worker slow query",
        "2026-10-19T10:01:30Z INFO app.worker recovered",
        "2026-10-19T10:02:00Z INFO app.worker idle",
    ]
)

# A realistic composite log: one blank line, one syslog-format drift
# line inside a dominant leveled file, a two-line stack trace after an
# ERROR (exempting the following INFO from the sequence rule), a
# 7-line duplicate burst, one 71.5h gap and one out-of-order line.
COMPOSITE_LINES = [
    "2026-10-19T10:00:00 INFO app.worker boot complete",       # 1
    "",                                                         # 2 blank
    "2026-10-19T10:30:00 WARN app.worker queue depth 120",     # 3
    "Oct 19 10:31:00 worker01 app[2312]: drift line",          # 4 drift
    "2026-10-19T11:00:00 ERROR app.db connection refused",     # 5
    "Traceback (most recent call last):",                      # 6 stack
    "Exception: connection refused",                           # 7 stack
    "2026-10-19T12:00:00 INFO app.worker reconnected",         # 8
    "2026-10-19T12:30:00 INFO app.worker heartbeat ok",        # 9 burst
    "2026-10-19T12:30:00 INFO app.worker heartbeat ok",        # 10
    "2026-10-19T12:30:00 INFO app.worker heartbeat ok",        # 11
    "2026-10-19T12:30:00 INFO app.worker heartbeat ok",        # 12
    "2026-10-19T12:30:00 INFO app.worker heartbeat ok",        # 13
    "2026-10-19T12:30:00 INFO app.worker heartbeat ok",        # 14
    "2026-10-19T12:30:00 INFO app.worker heartbeat ok",        # 15
    "2026-10-22T12:00:00 INFO app.worker daily summary",       # 16 gap
    "2026-10-18T00:00:00 INFO app.worker late flush",          # 17 back
]
COMPOSITE = "\n".join(COMPOSITE_LINES)

MULTI_FORMAT_LINES = [
    '127.0.0.1 - frank [19/Oct/2026:10:30:00 +0000] "GET /a'
    ' HTTP/1.1" 200 512 "https://ref.example/x" "Mozilla/5.0"',  # 1
    '127.0.0.1 - - [19/Oct/2026:10:31:00 +0000] "POST /b'
    ' HTTP/1.1" 401 64 "-" "curl/8.4.0"',                        # 2
    '10.0.0.9 - alice [19/Oct/2026:10:32:00 +0000] "GET /c'
    ' HTTP/1.1" 404 - "-" "Mozilla/5.0"',                        # 3
    "Oct 19 10:33:00 worker01 sshd[99]: Accepted publickey",     # 4 drift
    "auth token=abcdef1234567890abcdef1234567890 trailing",      # 5 drift
]


class ValidationMatrixTest(unittest.TestCase):
    """Strict parameter validation raises before any computation."""

    def setUp(self):
        self.tool = LogLintTool()

    def test_unknown_mode(self):
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="bogus", text="a\n")
        self.assertIn("mode must be one of", str(ctx.exception))

    def test_bad_text_values(self):
        for bad in (None, 123, True, "", "   \n\t\n"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="audit", text=bad)

    def test_input_character_cap(self):
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="audit", text="x" * 10_000_001)
        self.assertIn("10,000,000-character limit", str(ctx.exception))

    def test_line_count_cap(self):
        text = "\n".join(["2026-10-19T10:00:00Z INFO a.b x"] * 100_001)
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="audit", text=text)
        self.assertIn("100,000-line limit", str(ctx.exception))

    def test_single_line_cap(self):
        line = "2026-10-19T10:00:00Z INFO a.b " + "x" * 1_000_000
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="audit", text=line)
        self.assertIn("1,000,000-character limit", str(ctx.exception))

    def test_threshold_hours_matrix(self):
        for bad in ("24", True, 0, -1, 87600.5):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="audit", text="a\n", threshold_hours=bad
                    )
        # Accepted: int, float and the 87600 upper bound itself.
        for good in (24, 0.5, 87600):
            with self.subTest(good=good):
                self.tool.execute(
                    mode="timeline", text=CLEAN_LEVELED, threshold_hours=good
                )

    def test_threshold_hours_rejected_in_level_summary(self):
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="level_summary", text=CLEAN_LEVELED, threshold_hours=24
            )
        self.assertIn("only accepted in audit, timeline mode", str(ctx.exception))

    def test_per_hour_matrix(self):
        with self.assertRaises(ValueError):
            self.tool.execute(mode="level_summary", text=CLEAN_LEVELED, per_hour="yes")
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="audit", text=CLEAN_LEVELED, per_hour=True)
        self.assertIn("per_hour is only accepted in level_summary mode", str(ctx.exception))
        with self.assertRaises(ValueError):
            self.tool.execute(mode="timeline", text=CLEAN_LEVELED, per_hour=False)

    def test_direct_module_class_matches_package_export(self):
        self.assertIs(LogLintTool, DirectLogLintTool)


class AuditModeTest(unittest.TestCase):
    """mode='audit' ground truths over hand-built logs."""

    def setUp(self):
        self.tool = LogLintTool()

    def test_clean_log_has_no_findings(self):
        result = self.tool.execute(mode="audit", text=CLEAN_LEVELED)
        self.assertEqual(result["findings"], [])
        self.assertEqual(
            result["finding_counts"], {"error": 0, "warning": 0, "info": 0, "total": 0}
        )
        self.assertEqual(result["format"], "leveled")
        self.assertEqual(result["timestamp_coverage"], 1.0)
        self.assertEqual(result["total_lines"], 5)
        self.assertEqual(result["blank_lines"], 0)
        self.assertEqual(result["stacktrace_context"], {"count": 0, "first_lines": []})
        self.assertEqual(result["line_endings"], {"crlf": 0, "lf": 4, "cr": 0})
        self.assertEqual(result["threshold_hours"], 24.0)

    def test_composite_log_fires_every_expected_rule_once(self):
        result = self.tool.execute(mode="audit", text=COMPOSITE)
        self.assertEqual(result["format"], "leveled")
        self.assertEqual(result["total_lines"], 16)  # 17 lines, 1 blank
        self.assertEqual(result["blank_lines"], 1)
        # 13 of 16 non-blank lines carry timestamps (81.25% >= 80%).
        self.assertEqual(result["timestamp_coverage"], 0.8125)
        self.assertEqual(result["stacktrace_context"], {"count": 2, "first_lines": [6, 7]})
        self.assertEqual(
            codes(result),
            [
                ("empty_lines", "info", 2),
                ("format_drift", "warning", 4),
                ("duplicate_line_burst", "warning", 9),
                ("timestamp_gaps", "info", 16),
                ("timestamp_regression", "error", 17),
            ],
        )
        self.assertEqual(
            result["finding_counts"], {"error": 1, "warning": 2, "info": 2, "total": 5}
        )

    def test_composite_messages_carry_ground_truth_arithmetic(self):
        result = self.tool.execute(mode="audit", text=COMPOSITE)
        by_code = {f["code"]: f for f in result["findings"]}
        drift = by_code["format_drift"]
        self.assertIn("1/16 lines (6.2%) deviate from the dominant 'leveled' format", drift["message"])
        self.assertIn("line 4: Oct 19 10:31:00 worker01 app[2312]: drift line", drift["message"])
        burst = by_code["duplicate_line_burst"]
        self.assertIn("identical line repeated 7 times consecutively (lines 9-15)", burst["message"])
        gap = by_code["timestamp_gaps"]
        self.assertIn("jumps 71.50h (> 24h threshold)", gap["message"])
        self.assertIn("2026-10-19T12:30:00 (line 15)", gap["message"])
        self.assertIn("2026-10-22T12:00:00 (line 16)", gap["message"])
        regression = by_code["timestamp_regression"]
        self.assertIn("timestamp goes backwards by 388800s", regression["message"])
        self.assertIn("2026-10-22T12:00:00 (line 16)", regression["message"])
        self.assertIn("2026-10-18T00:00:00 (line 17)", regression["message"])
        empty = by_code["empty_lines"]
        self.assertIn("1 blank line(s) present (first at line 2)", empty["message"])

    def test_multi_format_log_votes_and_drift(self):
        result = self.tool.execute(mode="audit", text="\n".join(MULTI_FORMAT_LINES))
        # Votes: 3 combined, 1 syslog, 1 unparseable -> combined wins.
        self.assertEqual(result["format"], "combined")
        self.assertEqual(result["total_lines"], 5)
        by_code = {f["code"]: f for f in result["findings"]}
        self.assertIn("format_drift", by_code)
        drift = by_code["format_drift"]
        self.assertEqual(drift["line"], 4)
        self.assertIn("2/5 lines (40.0%) deviate from the dominant 'combined' format", drift["message"])
        # Only 3/5 lines (60%) carry timestamps -> coverage rule fires.
        self.assertIn("missing_timestamp_mode", by_code)
        self.assertEqual(result["timestamp_coverage"], 0.6)

    def test_drift_preview_masks_secrets_and_caps_length(self):
        text = "\n".join(
            [
                MULTI_FORMAT_LINES[0],
                MULTI_FORMAT_LINES[1],
                MULTI_FORMAT_LINES[2],
                MULTI_FORMAT_LINES[3],
                "password=hunter2secret api_token=sk-live-987654321 detail="
                + "z" * 120,
            ]
        )
        result = self.tool.execute(mode="audit", text=text)
        drift = next(f for f in result["findings"] if f["code"] == "format_drift")
        self.assertIn("password=***", drift["message"])
        self.assertIn("api_token=***", drift["message"])
        self.assertNotIn("hunter2secret", drift["message"])
        self.assertNotIn("sk-live-", drift["message"])
        # The 60-char preview cap: the excerpt is truncated with "..."
        # and never carries anywhere near the full 120-char tail.
        self.assertIn("...", drift["message"])
        self.assertLess(drift["message"].count("z"), 60)

    def test_unrecognized_format_returns_structured_error(self):
        result = self.tool.execute(mode="audit", text="hello world\nfoo bar\n")
        self.assertIn("error", result)
        self.assertEqual(result["error"]["type"], "unrecognized_format")
        self.assertNotIn("findings", result)

    def test_level_sequence_anomaly_and_exemptions(self):
        hit = "\n".join(
            [
                "2026-10-19T10:00:00Z ERROR app.db connection refused",
                "2026-10-19T10:00:01Z INFO app.worker all fine now",
            ]
        )
        result = self.tool.execute(mode="audit", text=hit)
        self.assertIn(("level_sequence_anomaly", "info", 2), codes(result))
        message = next(
            f["message"] for f in result["findings"]
            if f["code"] == "level_sequence_anomaly"
        )
        self.assertIn("ERROR at line 1", message)
        self.assertIn("INFO at line 2", message)

        # A WARN between clears the suspicion.
        with_warn = hit.replace(
            "2026-10-19T10:00:01Z INFO",
            "2026-10-19T10:00:01Z WARN",
        ) + "\n2026-10-19T10:00:02Z INFO app.worker fine"
        result = self.tool.execute(mode="audit", text=with_warn)
        self.assertNotIn("level_sequence_anomaly", [c for c, _, _ in codes(result)])

        # A stack trace between also clears the suspicion.
        with_stack = "\n".join(
            [
                "2026-10-19T10:00:00Z ERROR app.db connection refused",
                "Traceback (most recent call last):",
                "Caused by: pool exhausted",
                "2026-10-19T10:00:01Z INFO app.worker reconnected",
                "2026-10-19T10:00:02Z INFO app.worker stable",
            ]
        )
        result = self.tool.execute(mode="audit", text=with_stack)
        self.assertNotIn("level_sequence_anomaly", [c for c, _, _ in codes(result)])
        self.assertEqual(result["stacktrace_context"], {"count": 2, "first_lines": [2, 3]})

        # FATAL counts as the ERROR family too.
        fatal = hit.replace("ERROR app.db", "FATAL app.db")
        result = self.tool.execute(mode="audit", text=fatal)
        self.assertIn(("level_sequence_anomaly", "info", 2), codes(result))

    def test_missing_timestamp_mode_skips_gap_and_regression(self):
        # Bracket lines carry levels but no timestamps: 2/5 = 40%
        # coverage, and the 30-day jump between the two timestamped
        # lines must NOT be reported once the rules are skipped.
        text = "\n".join(
            [
                "[INFO] start",
                "[INFO] run",
                "[INFO] done",
                "2026-10-19T10:00:00 INFO app.a first",
                "2026-11-18T10:30:00 INFO app.a second",
            ]
        )
        result = self.tool.execute(mode="audit", text=text)
        self.assertEqual(result["format"], "leveled")
        self.assertEqual(result["timestamp_coverage"], 0.4)
        present = [c for c, _, _ in codes(result)]
        self.assertIn("missing_timestamp_mode", present)
        self.assertNotIn("timestamp_gaps", present)
        self.assertNotIn("timestamp_regression", present)
        note = next(
            f for f in result["findings"] if f["code"] == "missing_timestamp_mode"
        )
        self.assertIn("2/5 lines (40.0%)", note["message"])
        self.assertIn("timestamp_gaps and timestamp_regression rules skipped", note["message"])

    def test_coverage_at_exactly_80_percent_still_runs_gap_rules(self):
        # 4 of 5 lines carry timestamps (exactly the floor): the gap
        # between line 4 and line 5 is 48h and must be reported.
        text = "\n".join(
            [
                "2026-10-19T10:00:00 INFO app.a one",
                "2026-10-19T10:30:00 INFO app.a two",
                "2026-10-19T11:00:00 INFO app.a three",
                "[INFO] no timestamp here",
                "2026-10-21T11:00:00 INFO app.a four",
            ]
        )
        result = self.tool.execute(mode="audit", text=text)
        self.assertEqual(result["timestamp_coverage"], 0.8)
        present = [c for c, _, _ in codes(result)]
        self.assertNotIn("missing_timestamp_mode", present)
        self.assertIn("timestamp_gaps", present)

    def test_mixed_line_endings(self):
        text = (
            "2026-10-19T10:00:00Z INFO a.b one\r\n"
            "2026-10-19T10:01:00Z INFO a.b two\n"
        )
        result = self.tool.execute(mode="audit", text=text)
        self.assertEqual(result["line_endings"], {"crlf": 1, "lf": 1, "cr": 0})
        self.assertIn(("mixed_line_endings", "warning", 1), codes(result))
        # Uniform CRLF is not mixed.
        result = self.tool.execute(
            mode="audit",
            text="2026-10-19T10:00:00Z INFO a.b one\r\n"
            "2026-10-19T10:01:00Z INFO a.b two\r\n",
        )
        self.assertEqual(result["line_endings"], {"crlf": 2, "lf": 0, "cr": 0})
        self.assertNotIn("mixed_line_endings", [c for c, _, _ in codes(result)])

    def test_encoding_replacement_chars(self):
        text = (
            "2026-10-19T10:00:00Z INFO a.b got \ufffd bytes\n"
            "2026-10-19T10:00:01Z INFO a.b fine\n"
        )
        result = self.tool.execute(mode="audit", text=text)
        self.assertIn(("encoding_replacement_chars", "info", 1), codes(result))
        message = next(
            f["message"] for f in result["findings"]
            if f["code"] == "encoding_replacement_chars"
        )
        self.assertIn("1 U+FFFD replacement character(s) on 1 line(s)", message)

    def test_very_long_line_isolated_warning(self):
        line = "2026-10-19T10:00:00Z INFO a.b " + "x" * 11_000
        result = self.tool.execute(mode="audit", text=line)
        self.assertEqual(
            codes(result), [("very_long_line", "warning", 1)]
        )
        self.assertIn(f"line is {len(line):,} characters long", result["findings"][0]["message"])

    def test_very_long_line_stack_trace_run_collapses(self):
        def long_line(i):
            # Unique tails keep the duplicate-burst rule out of the way.
            return "2026-10-19T10:00:00Z INFO a.b frame " + str(i) + " " + "x" * 10_500

        # Six consecutive over-long lines -> one info finding.
        result = self.tool.execute(
            mode="audit", text="\n".join(long_line(i) for i in range(6))
        )
        self.assertEqual(codes(result), [("very_long_line", "info", 1)])
        self.assertIn(
            "6 consecutive lines over 10,000 characters starting here",
            result["findings"][0]["message"],
        )
        # Five consecutive over-long lines stay individual warnings.
        result = self.tool.execute(
            mode="audit", text="\n".join(long_line(i) for i in range(5))
        )
        self.assertEqual(
            codes(result), [("very_long_line", "warning", i) for i in range(1, 6)]
        )

    def test_duplicate_line_burst_threshold(self):
        dup = "2026-10-19T12:30:00 INFO app.worker heartbeat ok"
        # Exactly five repeats: at the threshold, not over it.
        result = self.tool.execute(mode="audit", text="\n".join([dup] * 5))
        self.assertNotIn("duplicate_line_burst", [c for c, _, _ in codes(result)])
        # Six repeats: one finding for the whole burst.
        result = self.tool.execute(mode="audit", text="\n".join([dup] * 6))
        self.assertEqual(codes(result), [("duplicate_line_burst", "warning", 1)])
        self.assertIn("repeated 6 times consecutively (lines 1-6)", result["findings"][0]["message"])

    def test_custom_threshold_hours_changes_gap_sensitivity(self):
        text = (
            "2026-10-19T10:00:00 INFO a.b one\n"
            "2026-10-19T20:00:00 INFO a.b two\n"
        )  # exactly 10h apart
        result = self.tool.execute(mode="audit", text=text, threshold_hours=24)
        self.assertNotIn("timestamp_gaps", [c for c, _, _ in codes(result)])
        result = self.tool.execute(mode="audit", text=text, threshold_hours=9.5)
        self.assertIn(("timestamp_gaps", "info", 2), codes(result))
        self.assertIn("jumps 10.00h (> 9.5h threshold)", result["findings"][0]["message"])


class TimelineModeTest(unittest.TestCase):
    """mode='timeline' arithmetic, gaps, runs and clean skips."""

    def setUp(self):
        self.tool = LogLintTool()

    def test_naive_wall_clock_arithmetic(self):
        text = "\n".join(
            [
                "2026-10-19T10:00:00 INFO a.b m1",
                "2026-10-19T10:30:00 INFO a.b m2",
                "2026-10-19T11:00:00 INFO a.b m3",
                "2026-10-19T10:15:00 INFO a.b m4",
                "2026-10-19T10:45:00 INFO a.b m5",
                "2026-10-20T09:00:00 INFO a.b m6",
            ]
        )
        result = self.tool.execute(mode="timeline", text=text, threshold_hours=20)
        self.assertFalse(result["skipped"])
        self.assertEqual(result["parsed_timestamps"], 6)
        self.assertEqual(result["timestamp_coverage"], 1.0)
        self.assertEqual(result["min"], "2026-10-19T10:00:00")
        self.assertEqual(result["max"], "2026-10-20T09:00:00")
        self.assertEqual(result["span_seconds"], 82800.0)  # 23h
        self.assertEqual(result["regression_count"], 1)
        self.assertEqual(result["gaps"]["count"], 1)
        self.assertEqual(
            result["gaps"]["top"],
            [
                {
                    "from_line": 5,
                    "to_line": 6,
                    "from_ts": "2026-10-19T10:45:00",
                    "to_ts": "2026-10-20T09:00:00",
                    "gap_hours": 22.25,
                }
            ],
        )
        self.assertEqual(
            result["monotonic_runs"],
            [
                {"start_line": 1, "end_line": 3, "length": 3},
                {"start_line": 4, "end_line": 6, "length": 3},
            ],
        )
        self.assertFalse(result["monotonic_runs_truncated"])

    def test_aware_timestamps_normalize_to_utc(self):
        text = "\n".join(
            [
                "2026-10-19T10:00:00+08:00 INFO a.b a",  # = 02:00Z
                "2026-10-19T02:00:00Z INFO a.b b",       # equal wall clock
                "2026-10-19T11:30:00+08:00 INFO a.b c",  # = 03:30Z
            ]
        )
        result = self.tool.execute(mode="timeline", text=text)
        self.assertEqual(result["min"], "2026-10-19T02:00:00")
        self.assertEqual(result["max"], "2026-10-19T03:30:00")
        self.assertEqual(result["span_seconds"], 5400.0)
        self.assertEqual(result["regression_count"], 0)
        self.assertEqual(
            result["monotonic_runs"],
            [{"start_line": 1, "end_line": 3, "length": 3}],
        )

    def test_apache_offsets_normalize_to_utc(self):
        text = "\n".join(
            [
                '127.0.0.1 - - [19/Oct/2026:10:30:00 +0200] "GET / HTTP/1.1"'
                ' 200 100 "-" "curl/8.0"',
                '127.0.0.1 - - [19/Oct/2026:09:00:00 +0000] "GET / HTTP/1.1"'
                ' 200 100 "-" "curl/8.0"',
            ]
        )
        result = self.tool.execute(mode="timeline", text=text)
        self.assertEqual(result["format"], "combined")
        self.assertEqual(result["min"], "2026-10-19T08:30:00")
        self.assertEqual(result["max"], "2026-10-19T09:00:00")
        self.assertEqual(result["span_seconds"], 1800.0)

    def test_single_timestamp(self):
        result = self.tool.execute(
            mode="timeline", text="2026-10-19T10:00:00 INFO a.b only"
        )
        self.assertFalse(result["skipped"])
        self.assertEqual(result["span_seconds"], 0.0)
        self.assertEqual(result["gaps"]["count"], 0)
        self.assertEqual(
            result["monotonic_runs"],
            [{"start_line": 1, "end_line": 1, "length": 1}],
        )

    def test_skips_cleanly_without_timestamps(self):
        result = self.tool.execute(
            mode="timeline", text="level=INFO service=api\nlevel=ERROR service=api"
        )
        self.assertTrue(result["skipped"])
        self.assertEqual(result["format"], "keyvalue")
        self.assertIn("no line carries a parseable timestamp", result["reason"])
        result = self.tool.execute(mode="timeline", text="unstructured noise\nmore noise")
        self.assertTrue(result["skipped"])
        self.assertIsNone(result["format"])
        self.assertIn("no line matching any known format", result["reason"])

    def test_gap_ordering_largest_first(self):
        text = "\n".join(
            [
                "2026-10-19T10:00:00 INFO a.b a",
                "2026-10-20T10:00:00 INFO a.b b",   # +24h
                "2026-10-23T10:00:00 INFO a.b c",   # +72h
                "2026-10-23T22:00:00 INFO a.b d",   # +12h
            ]
        )
        result = self.tool.execute(mode="timeline", text=text, threshold_hours=23)
        self.assertEqual(result["gaps"]["count"], 2)
        self.assertEqual(
            [g["gap_hours"] for g in result["gaps"]["top"]], [72.0, 24.0]
        )
        # 2026-10-19T10:00 to 2026-10-23T22:00 = 4 days 12h = 108h.
        self.assertEqual(result["span_seconds"], 388800.0)


class LevelSummaryModeTest(unittest.TestCase):
    """mode='level_summary' histogram and hour buckets."""

    def setUp(self):
        self.tool = LogLintTool()

    def test_histogram_with_alias_folding(self):
        text = "\n".join(
            [
                "2026-10-19T10:00:00Z TRACE a.b t",
                "2026-10-19T10:00:01Z DEBUG a.b d",
                "2026-10-19T10:00:02Z INFO a.b i1",
                "2026-10-19T10:00:03Z INFO a.b i2",
                "2026-10-19T10:00:04Z WARNING a.b w",
                "2026-10-19T10:00:05Z ERROR a.b e",
                "2026-10-19T10:00:06Z CRITICAL a.b c",
            ]
        )
        result = self.tool.execute(mode="level_summary", text=text)
        self.assertFalse(result["skipped"])
        self.assertEqual(result["leveled_lines"], 7)
        self.assertEqual(
            result["level_histogram"],
            {"TRACE": 1, "DEBUG": 1, "INFO": 2, "WARN": 1, "ERROR": 1, "FATAL": 1},
        )
        self.assertNotIn("per_hour", result)

    def test_per_hour_buckets_use_utc_hour_keys(self):
        text = "\n".join(
            [
                "2026-10-19T10:00:00Z INFO a.b x",
                "2026-10-19T10:20:00Z ERROR a.b y",
                "2026-10-19T11:45:00Z INFO a.b z",
                "2026-10-19T18:30:00+08:00 WARN a.b w",  # = 10:30Z
            ]
        )
        result = self.tool.execute(mode="level_summary", text=text, per_hour=True)
        self.assertEqual(
            result["per_hour"],
            {
                "2026-10-19T10": {"ERROR": 1, "INFO": 1, "WARN": 1},
                "2026-10-19T11": {"INFO": 1},
            },
        )

    def test_keyvalue_levels_and_unknown_bucket(self):
        text = "\n".join(
            [
                "level=INFO service=api",
                "level=WEIRD service=api",
                "level=ERROR service=api",
            ]
        )
        result = self.tool.execute(mode="level_summary", text=text)
        self.assertEqual(result["format"], "keyvalue")
        self.assertFalse(result["skipped"])
        self.assertEqual(result["leveled_lines"], 2)
        self.assertEqual(
            result["level_histogram"],
            {"TRACE": 0, "DEBUG": 0, "INFO": 1, "WARN": 0, "ERROR": 1, "FATAL": 0, "UNKNOWN": 1},
        )
        self.assertEqual(result["unknown_levels"], {"WEIRD": 1})

    def test_skips_cleanly_without_levels(self):
        text = "\n".join(MULTI_FORMAT_LINES[:3])  # combined only: no levels
        result = self.tool.execute(mode="level_summary", text=text)
        self.assertTrue(result["skipped"])
        self.assertEqual(result["format"], "combined")
        self.assertIn("no line carries a recognized level", result["reason"])
        text = "Oct 19 10:30:00 host app[1]: syslog has no level"
        result = self.tool.execute(mode="level_summary", text=text)
        self.assertTrue(result["skipped"])
        self.assertEqual(result["format"], "syslog")


if __name__ == "__main__":
    unittest.main()
