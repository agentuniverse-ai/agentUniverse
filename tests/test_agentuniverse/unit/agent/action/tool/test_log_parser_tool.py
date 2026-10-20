#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_log_parser_tool.py

"""Offline unit tests for LogParserTool.

The tool is built purely on the standard library ``re`` module and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: parsing is checked against hand-parsed
ground-truth records derived line by line from realistic samples of
each format, detection against hand-counted per-line votes (including
mixed samples and majority-unparseable samples), and filtering against
hand-evaluated predicates including the DEBUG < INFO < WARN < ERROR <
FATAL severity ordering.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import LogParserTool
from agentuniverse.agent.action.tool.common_tool.log_parser_tool import (
    LogParserTool as DirectLogParserTool,
)

# --------------------------------------------------------------------- #
# Hand-parsed fixtures (expected values derived independently of the
# tool's regexes — literal expected records)
# --------------------------------------------------------------------- #
COMBINED_TEXT = "\n".join(
    [
        '127.0.0.1 - frank [10/Oct/2026:13:55:36 -0700] "GET /apache_pb.gif'
        ' HTTP/1.0" 200 2326 "http://www.example.com/start.html"'
        ' "Mozilla/5.0 (X11; Linux x86_64)"',
        '192.168.1.10 - - [19/Oct/2026:10:30:00 +0200] "POST /api/login'
        ' HTTP/2.0" 401 512 "-" "curl/8.4.0"',
        '10.0.0.9 - alice [19/Oct/2026:11:00:01 +0000] "GET /missing'
        ' HTTP/1.1" 404 - "-" "Mozilla/5.0"',
    ]
)

COMBINED_RECORD_1 = {
    "line_no": 1,
    "ip": "127.0.0.1",
    "ident": None,
    "user": "frank",
    "time": "10/Oct/2026:13:55:36 -0700",
    "method": "GET",
    "path": "/apache_pb.gif",
    "protocol": "HTTP/1.0",
    "status": 200,
    "bytes": 2326,
    "referrer": "http://www.example.com/start.html",
    "agent": "Mozilla/5.0 (X11; Linux x86_64)",
}
COMBINED_RECORD_2 = {
    "line_no": 2,
    "ip": "192.168.1.10",
    "ident": None,
    "user": None,
    "time": "19/Oct/2026:10:30:00 +0200",
    "method": "POST",
    "path": "/api/login",
    "protocol": "HTTP/2.0",
    "status": 401,
    "bytes": 512,
    "referrer": "-",
    "agent": "curl/8.4.0",
}
COMBINED_RECORD_3 = {
    "line_no": 3,
    "ip": "10.0.0.9",
    "ident": None,
    "user": "alice",
    "time": "19/Oct/2026:11:00:01 +0000",
    "method": "GET",
    "path": "/missing",
    "protocol": "HTTP/1.1",
    "status": 404,
    "bytes": None,
    "referrer": "-",
    "agent": "Mozilla/5.0",
}

COMMON_TEXT = "\n".join(
    [
        '127.0.0.1 - frank [10/Oct/2026:13:55:36 -0700] "GET /apache_pb.gif'
        ' HTTP/1.0" 200 2326',
        '10.0.0.5 - alice [19/Oct/2026:10:30:00 +0200] "HEAD /healthz'
        ' HTTP/1.1" 200 -',
    ]
)

SYSLOG_TEXT = "\n".join(
    [
        "Oct 19 10:30:00 web01 sshd[1234]: Accepted publickey for root from 10.0.0.9",
        "Oct  9 09:01:02 db02 systemd: Started Daily Cleanup.",
        "Oct 19 11:00:00 web01 CRON[9001]: (root) CMD (/usr/bin/backup)",
    ]
)

LEVELED_TEXT = "\n".join(
    [
        "2026-10-19T10:30:00Z TRACE auth.trace entering handle()",
        "2026-10-19T10:30:01Z DEBUG auth.service cache lookup missed",
        "2026-10-19T10:30:02Z INFO auth.service User logged in successfully",
        "2026-10-19 10:31:05.123+02:00 ERROR db.pool Connection refused after 3 retries",
        "2026-10-19T10:32:00Z [WARN] cache miss ratio high",
        "2026-10-19T10:33:11Z FATAL watchdog",
        "[DEBUG] bare bracket line without timestamp",
    ]
)

KEYVALUE_TEXT = "\n".join(
    [
        "level=INFO user=alice duration_ms=42",
        'event=request path="/api/v1/users" status=200',
    ]
)

GARBAGE_TEXT = "\n".join(
    ["the quick brown fox", "!!! random noise ???", "not a log line at all"]
)


class LogParserToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib LogParserTool."""

    def setUp(self) -> None:
        self.tool = LogParserTool()

    # ------------------------------------------------------------------ #
    # import surface
    # ------------------------------------------------------------------ #

    def test_package_and_direct_import_are_the_same_class(self) -> None:
        self.assertIs(LogParserTool, DirectLogParserTool)
        self.assertEqual(self.tool.name, "log_parser_tool")
        self.assertTrue(self.tool.description)

    # ------------------------------------------------------------------ #
    # detect mode: per-line votes, majority wins, mixed reporting
    # ------------------------------------------------------------------ #

    def test_detect_uniform_combined_sample(self) -> None:
        result = self.tool.execute(mode="detect", text=COMBINED_TEXT)
        self.assertEqual(
            result,
            {
                "mode": "detect",
                "total_lines": 3,
                "blank_lines": 0,
                "sampled_lines": 3,
                "format_guess": "combined",
                "confidence": 1.0,
                "majority": True,
                "votes": {
                    "combined": 3,
                    "common": 0,
                    "syslog": 0,
                    "leveled": 0,
                    "keyvalue": 0,
                    "unparseable": 0,
                },
                "mixed_lines": 0,
            },
        )

    def test_detect_common_sample(self) -> None:
        result = self.tool.execute(mode="detect", text=COMMON_TEXT)
        self.assertEqual(result["format_guess"], "common")
        self.assertEqual(result["votes"]["common"], 2)
        self.assertEqual(result["votes"]["combined"], 0)
        self.assertEqual(result["confidence"], 1.0)

    def test_detect_syslog_sample(self) -> None:
        result = self.tool.execute(mode="detect", text=SYSLOG_TEXT)
        self.assertEqual(result["format_guess"], "syslog")
        self.assertEqual(result["votes"]["syslog"], 3)

    def test_detect_leveled_sample(self) -> None:
        result = self.tool.execute(mode="detect", text=LEVELED_TEXT)
        self.assertEqual(result["format_guess"], "leveled")
        self.assertEqual(result["votes"]["leveled"], 7)

    def test_detect_keyvalue_sample(self) -> None:
        result = self.tool.execute(mode="detect", text=KEYVALUE_TEXT)
        self.assertEqual(result["format_guess"], "keyvalue")
        self.assertEqual(result["votes"]["keyvalue"], 2)

    def test_detect_mixed_sample_counts_and_reports_mixed_lines(self) -> None:
        text = COMBINED_TEXT + "\n" + SYSLOG_TEXT  # 3 combined + 3 syslog
        result = self.tool.execute(mode="detect", text=text)
        self.assertEqual(result["format_guess"], "combined")
        self.assertEqual(result["votes"]["combined"], 3)
        self.assertEqual(result["votes"]["syslog"], 3)
        # Ties break by fixed detection priority (combined first).
        self.assertEqual(result["confidence"], 0.5)
        self.assertFalse(result["majority"])
        self.assertEqual(result["mixed_lines"], 3)
        self.assertEqual(result["sampled_lines"], 6)

    def test_detect_majority_unparseable_still_reports_best_format(self) -> None:
        text = SYSLOG_TEXT + "\n" + GARBAGE_TEXT  # 3 syslog + 3 garbage
        result = self.tool.execute(mode="detect", text=text)
        self.assertEqual(result["format_guess"], "syslog")
        self.assertEqual(result["votes"]["syslog"], 3)
        self.assertEqual(result["votes"]["unparseable"], 3)
        self.assertEqual(result["confidence"], 0.5)
        self.assertFalse(result["majority"])
        self.assertEqual(result["mixed_lines"], 3)

    def test_detect_all_unparseable_has_no_guess(self) -> None:
        result = self.tool.execute(mode="detect", text=GARBAGE_TEXT)
        self.assertIsNone(result["format_guess"])
        self.assertEqual(result["confidence"], 0.0)
        self.assertFalse(result["majority"])
        self.assertEqual(result["votes"]["unparseable"], 3)
        self.assertEqual(result["mixed_lines"], 3)

    def test_detect_sample_size_caps_evenly_and_deterministically(self) -> None:
        # 4 combined lines then 1 garbage line; sampling 3 of 5 picks
        # indices [0, 2, 4] -> combined, combined, garbage.
        lines = [
            '127.0.0.1 - - [10/Oct/2026:13:5%d:00 -0700] "GET /a HTTP/1.1"'
            ' 200 1 "r" "a"' % i
            for i in range(4)
        ]
        text = "\n".join(lines + ["totally unknown line"])
        result = self.tool.execute(mode="detect", text=text, sample_size=3)
        self.assertEqual(result["sampled_lines"], 3)
        self.assertEqual(result["votes"]["combined"], 2)
        self.assertEqual(result["votes"]["unparseable"], 1)
        self.assertEqual(result["format_guess"], "combined")
        # round(2 / 3, 4) == 0.6667
        self.assertEqual(result["confidence"], 0.6667)
        again = self.tool.execute(mode="detect", text=text, sample_size=3)
        self.assertEqual(result, again)

    def test_detect_sample_size_one_takes_first_line(self) -> None:
        result = self.tool.execute(
            mode="detect", text=SYSLOG_TEXT, sample_size=1
        )
        self.assertEqual(result["sampled_lines"], 1)
        self.assertEqual(result["format_guess"], "syslog")
        self.assertEqual(result["confidence"], 1.0)

    def test_detect_counts_blank_lines_and_totals(self) -> None:
        text = COMBINED_TEXT + "\n\n   \n" + COMBINED_TEXT.split("\n")[0]
        result = self.tool.execute(mode="detect", text=text)
        self.assertEqual(result["total_lines"], 4)
        self.assertEqual(result["blank_lines"], 2)
        self.assertEqual(result["sampled_lines"], 4)
        self.assertEqual(result["votes"]["combined"], 4)

    # ------------------------------------------------------------------ #
    # parse mode: structured records per format
    # ------------------------------------------------------------------ #

    def test_parse_combined_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", text=COMBINED_TEXT)
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["format"], "combined")
        self.assertTrue(result["detected"])
        self.assertEqual(result["parsed_count"], 3)
        self.assertEqual(result["failed_count"], 0)
        self.assertEqual(
            result["records"],
            [COMBINED_RECORD_1, COMBINED_RECORD_2, COMBINED_RECORD_3],
        )

    def test_parse_combined_apache_escaped_quotes_and_backslashes(self) -> None:
        # Apache escapes a literal quote inside the logged referrer /
        # agent as \" and a backslash as \\; such lines must parse and
        # the records must carry the unescaped values. The field bodies
        # below are written as raw strings so the escapes read exactly
        # as they appear in the log file.
        referrer_body = r'-\"Mozilla/5.0 (search; \"q=\" )\"'
        agent_body = r'agent with \"escaped quotes\" and \\backslash\"'
        text = (
            '1.2.3.4 - - [19/Oct/2026:10:30:00 +0000] '
            '"GET /search?q=\\"1\\" HTTP/1.1" 200 10 '
            f'"{referrer_body}" "{agent_body}"\n'
        )
        result = self.tool.execute(mode="parse", text=text, format="combined")
        self.assertEqual(result["failed_count"], 0)
        record = result["records"][0]
        self.assertEqual(record["referrer"], '-"Mozilla/5.0 (search; "q=" )"')
        self.assertEqual(
            record["agent"], 'agent with "escaped quotes" and \\backslash"'
        )
        # Detection recognizes the escaped-quote line as combined too.
        detect = self.tool.execute(mode="detect", text=text)
        self.assertEqual(detect["format_guess"], "combined")
        self.assertEqual(detect["votes"]["combined"], 1)

    def test_parse_common_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", text=COMMON_TEXT)
        self.assertEqual(result["parsed_count"], 2)
        self.assertEqual(
            result["records"],
            [
                {
                    "line_no": 1,
                    "ip": "127.0.0.1",
                    "ident": None,
                    "user": "frank",
                    "time": "10/Oct/2026:13:55:36 -0700",
                    "method": "GET",
                    "path": "/apache_pb.gif",
                    "protocol": "HTTP/1.0",
                    "status": 200,
                    "bytes": 2326,
                },
                {
                    "line_no": 2,
                    "ip": "10.0.0.5",
                    "ident": None,
                    "user": "alice",
                    "time": "19/Oct/2026:10:30:00 +0200",
                    "method": "HEAD",
                    "path": "/healthz",
                    "protocol": "HTTP/1.1",
                    "status": 200,
                    "bytes": None,
                },
            ],
        )

    def test_parse_syslog_ground_truth_with_and_without_pid(self) -> None:
        result = self.tool.execute(mode="parse", text=SYSLOG_TEXT)
        self.assertEqual(result["parsed_count"], 3)
        self.assertEqual(
            result["records"],
            [
                {
                    "line_no": 1,
                    "timestamp": "Oct 19 10:30:00",
                    "host": "web01",
                    "proc": "sshd",
                    "pid": 1234,
                    "message": "Accepted publickey for root from 10.0.0.9",
                },
                {
                    "line_no": 2,
                    "timestamp": "Oct  9 09:01:02",
                    "host": "db02",
                    "proc": "systemd",
                    "pid": None,
                    "message": "Started Daily Cleanup.",
                },
                {
                    "line_no": 3,
                    "timestamp": "Oct 19 11:00:00",
                    "host": "web01",
                    "proc": "CRON",
                    "pid": 9001,
                    "message": "(root) CMD (/usr/bin/backup)",
                },
            ],
        )

    def test_parse_leveled_ground_truth_variants(self) -> None:
        result = self.tool.execute(mode="parse", text=LEVELED_TEXT)
        self.assertEqual(result["parsed_count"], 7)
        self.assertEqual(
            result["records"],
            [
                {
                    "line_no": 1,
                    "timestamp": "2026-10-19T10:30:00Z",
                    "level": "TRACE",
                    "logger": "auth.trace",
                    "message": "entering handle()",
                },
                {
                    "line_no": 2,
                    "timestamp": "2026-10-19T10:30:01Z",
                    "level": "DEBUG",
                    "logger": "auth.service",
                    "message": "cache lookup missed",
                },
                {
                    "line_no": 3,
                    "timestamp": "2026-10-19T10:30:02Z",
                    "level": "INFO",
                    "logger": "auth.service",
                    "message": "User logged in successfully",
                },
                {
                    "line_no": 4,
                    "timestamp": "2026-10-19 10:31:05.123+02:00",
                    "level": "ERROR",
                    "logger": "db.pool",
                    "message": "Connection refused after 3 retries",
                },
                {
                    "line_no": 5,
                    "timestamp": "2026-10-19T10:32:00Z",
                    "level": "WARN",
                    "logger": "cache",
                    "message": "miss ratio high",
                },
                {
                    "line_no": 6,
                    "timestamp": "2026-10-19T10:33:11Z",
                    "level": "FATAL",
                    "logger": "watchdog",
                    "message": "",
                },
                {
                    "line_no": 7,
                    "timestamp": None,
                    "level": "DEBUG",
                    "logger": None,
                    "message": "bare bracket line without timestamp",
                },
            ],
        )

    def test_parse_leveled_normalizes_level_case(self) -> None:
        text = "2026-10-19T10:33:11Z info lower.case tokens are fine"
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(
            result["records"],
            [
                {
                    "line_no": 1,
                    "timestamp": "2026-10-19T10:33:11Z",
                    "level": "INFO",
                    "logger": "lower.case",
                    "message": "tokens are fine",
                }
            ],
        )

    def test_parse_keyvalue_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", text=KEYVALUE_TEXT)
        self.assertEqual(result["parsed_count"], 2)
        self.assertEqual(
            result["records"],
            [
                {
                    "line_no": 1,
                    "level": "INFO",
                    "user": "alice",
                    "duration_ms": "42",
                },
                {
                    "line_no": 2,
                    "event": "request",
                    "path": "/api/v1/users",
                    "status": "200",
                },
            ],
        )

    def test_parse_keyvalue_single_quotes_equals_and_dangling_quotes(self) -> None:
        text = "note='single quoted value' a=b=c d=\"unclosed"
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(
            result["records"],
            [
                {
                    "line_no": 1,
                    "note": "single quoted value",
                    "a": "b=c",
                    "d": '"unclosed',
                }
            ],
        )

    def test_parse_keyvalue_duplicate_key_keeps_last(self) -> None:
        result = self.tool.execute(mode="parse", text="a=1 a=2 b=3")
        self.assertEqual(
            result["records"], [{"line_no": 1, "a": "2", "b": "3"}]
        )

    def test_parse_unparseable_lines_reported_as_raw_error(self) -> None:
        text = COMBINED_TEXT.split("\n")[0] + "\nnot an access log line"
        result = self.tool.execute(mode="parse", text=text, format="combined")
        self.assertEqual(result["detected"], False)
        self.assertEqual(result["parsed_count"], 1)
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(
            result["records"][1],
            {
                "line_no": 2,
                "raw": "not an access log line",
                "error": "line does not match the combined format",
            },
        )

    def test_parse_explicit_format_applies_to_every_line(self) -> None:
        result = self.tool.execute(mode="parse", text=SYSLOG_TEXT, format="keyvalue")
        self.assertEqual(result["format"], "keyvalue")
        self.assertEqual(result["parsed_count"], 0)
        self.assertEqual(result["failed_count"], 3)

    def test_parse_auto_detect_majority_wins_and_minority_fails(self) -> None:
        # 2 combined lines beat 1 common line; the common line then
        # fails to parse as combined (it lacks the referrer/agent tail).
        text = (
            "\n".join(COMBINED_TEXT.split("\n")[:2])
            + "\n"
            + COMMON_TEXT.split("\n")[0]
        )
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(result["format"], "combined")
        self.assertTrue(result["detected"])
        self.assertEqual(result["parsed_count"], 2)
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(result["records"][2]["line_no"], 3)
        self.assertIn("error", result["records"][2])

    def test_parse_blank_lines_skipped_with_original_line_numbers(self) -> None:
        first = COMBINED_TEXT.split("\n")[0]
        second = COMBINED_TEXT.split("\n")[1]
        text = first + "\n\n   \n" + second + "\n"
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(result["blank_lines"], 2)
        self.assertEqual(result["line_count"], 2)
        self.assertEqual(
            [record["line_no"] for record in result["records"]], [1, 4]
        )

    def test_parse_auto_detect_with_zero_parsable_lines_returns_error(self) -> None:
        result = self.tool.execute(mode="parse", text=GARBAGE_TEXT)
        self.assertEqual(result["error"]["type"], "unrecognized_format")
        self.assertIn("no line matching any known format", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # filter mode: predicates over parsed records
    # ------------------------------------------------------------------ #

    def test_filter_level_threshold_ordering(self) -> None:
        # DEBUG < INFO < WARN < ERROR < FATAL (TRACE below DEBUG).
        result = self.tool.execute(
            mode="filter", text=LEVELED_TEXT, level_min="INFO"
        )
        self.assertEqual(result["parsed_count"], 7)
        self.assertEqual(result["matched_count"], 4)
        self.assertEqual(
            [record["level"] for record in result["records"]],
            ["INFO", "ERROR", "WARN", "FATAL"],
        )
        self.assertEqual(result["matched_lines"], LEVELED_TEXT.split("\n")[2:6])

    def test_filter_level_threshold_excludes_debug_and_trace(self) -> None:
        result = self.tool.execute(
            mode="filter", text=LEVELED_TEXT, level_min="DEBUG"
        )
        self.assertEqual(
            [record["line_no"] for record in result["records"]], [2, 3, 4, 5, 6, 7]
        )

    def test_filter_level_threshold_is_inclusive(self) -> None:
        result = self.tool.execute(
            mode="filter", text=LEVELED_TEXT, level_min="ERROR"
        )
        self.assertEqual(
            [record["level"] for record in result["records"]], ["ERROR", "FATAL"]
        )

    def test_filter_level_warning_alias_matches_warn(self) -> None:
        text = "2026-10-19T10:00:00Z WARNING app disk usage high"
        for threshold in ("WARN", "WARNING"):
            result = self.tool.execute(
                mode="filter", text=text, level_min=threshold
            )
            self.assertEqual(result["matched_count"], 1)
            self.assertEqual(result["records"][0]["level"], "WARNING")

    def test_filter_level_critical_alias_matches_fatal(self) -> None:
        text = "2026-10-19T10:00:00Z CRITICAL app disk full"
        result = self.tool.execute(mode="filter", text=text, level_min="FATAL")
        self.assertEqual(result["matched_count"], 1)
        self.assertEqual(result["records"][0]["level"], "CRITICAL")

    def test_filter_level_min_is_case_insensitive_and_trimmed(self) -> None:
        result = self.tool.execute(
            mode="filter", text=LEVELED_TEXT, level_min=" error "
        )
        self.assertEqual(result["predicates"]["level_min"], "ERROR")
        self.assertEqual(
            [record["level"] for record in result["records"]], ["ERROR", "FATAL"]
        )

    def test_filter_status_threshold(self) -> None:
        result = self.tool.execute(
            mode="filter", text=COMBINED_TEXT, status_min=401
        )
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(
            [record["status"] for record in result["records"]], [401, 404]
        )
        self.assertEqual(
            result["matched_lines"],
            [COMBINED_TEXT.split("\n")[1], COMBINED_TEXT.split("\n")[2]],
        )

    def test_filter_status_threshold_inclusive_boundary(self) -> None:
        result = self.tool.execute(
            mode="filter", text=COMBINED_TEXT, status_min=404
        )
        self.assertEqual(result["matched_count"], 1)
        self.assertEqual(
            [record["status"] for record in result["records"]], [404]
        )

    def test_filter_method_exact_match(self) -> None:
        result = self.tool.execute(mode="filter", text=COMBINED_TEXT, method="POST")
        self.assertEqual(result["matched_count"], 1)
        self.assertEqual(result["records"][0]["method"], "POST")
        self.assertEqual(result["records"][0]["line_no"], 2)

    def test_filter_ip_exact_match(self) -> None:
        result = self.tool.execute(mode="filter", text=COMBINED_TEXT, ip="10.0.0.9")
        self.assertEqual(result["matched_count"], 1)
        self.assertEqual(result["records"][0]["ip"], "10.0.0.9")

    def test_filter_predicates_combine_with_and(self) -> None:
        text = (
            COMBINED_TEXT
            + "\n"
            + '203.0.113.5 - - [19/Oct/2026:12:00:00 +0000] "POST /big'
            ' HTTP/1.1" 503 100 "r" "a"'
        )
        result = self.tool.execute(
            mode="filter", text=text, status_min=400, method="POST"
        )
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(
            [record["status"] for record in result["records"]], [401, 503]
        )
        self.assertTrue(
            all(record["method"] == "POST" for record in result["records"])
        )

    def test_filter_predicate_excludes_records_without_the_field(self) -> None:
        # Combined records carry no level, so level_min matches nothing.
        result = self.tool.execute(
            mode="filter", text=COMBINED_TEXT, level_min="INFO"
        )
        self.assertEqual(result["parsed_count"], 3)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["matched_lines"], [])

    def test_filter_skips_unparseable_lines(self) -> None:
        text = LEVELED_TEXT + "\nnot a leveled line at all"
        result = self.tool.execute(
            mode="filter", text=text, format="leveled", level_min="ERROR"
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(result["matched_count"], 2)
        self.assertNotIn("not a leveled line at all", result["matched_lines"])

    def test_filter_reports_detected_format(self) -> None:
        result = self.tool.execute(
            mode="filter", text=COMBINED_TEXT, status_min=200
        )
        self.assertEqual(result["format"], "combined")
        self.assertTrue(result["detected"])
        self.assertEqual(result["predicates"]["status_min"], 200)

    def test_filter_unrecognizable_text_returns_error_payload(self) -> None:
        result = self.tool.execute(
            mode="filter", text=GARBAGE_TEXT, level_min="ERROR"
        )
        self.assertEqual(result["mode"], "filter")
        self.assertEqual(result["error"]["type"], "unrecognized_format")

    # ------------------------------------------------------------------ #
    # error matrix: strict validation raises before any computation
    # ------------------------------------------------------------------ #

    def assert_invalid(self, message: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        self.assertTrue(
            str(ctx.exception).startswith("log_parser_tool: "),
            msg=f"unexpected message: {ctx.exception}",
        )
        self.assertIn(message, str(ctx.exception))

    def test_error_unknown_mode(self) -> None:
        self.assert_invalid(
            "mode must be one of", mode="explode", text=SYSLOG_TEXT
        )

    def test_error_text_wrong_types(self) -> None:
        for bad in (None, 123, 4.5, True, b"Oct 19 10:30:00 h p[1]: m"):
            self.assert_invalid(
                "text must be a non-empty string", mode="detect", text=bad
            )

    def test_error_text_empty_or_blank_only(self) -> None:
        self.assert_invalid(
            "text must be a non-empty string", mode="detect", text=""
        )
        self.assert_invalid(
            "no non-blank lines", mode="detect", text="\n  \n\t\n"
        )

    def test_error_text_overall_character_cap(self) -> None:
        self.assert_invalid(
            "exceeds the 1,000,000-character limit",
            mode="detect",
            text="x" * 1_000_001,
        )

    def test_error_single_line_too_long(self) -> None:
        line = "Oct 19 10:30:00 web01 sshd[1]: " + "m" * 10_000
        self.assert_invalid(
            "line 1 exceeds the 10,000-character limit",
            mode="parse",
            text=line,
        )

    def test_error_too_many_lines(self) -> None:
        text = "\n".join(["level=INFO n=%d" % i for i in range(10_001)])
        self.assert_invalid(
            "exceeds the 10,000-line limit", mode="parse", text=text
        )

    def test_error_unknown_or_mistyped_format(self) -> None:
        self.assert_invalid(
            "format must be one of",
            mode="parse",
            text=COMBINED_TEXT,
            format="apache",
        )
        self.assert_invalid(
            "format must be one of",
            mode="parse",
            text=COMBINED_TEXT,
            format=7,
        )

    def test_error_sample_size_bounds_and_type(self) -> None:
        for bad in (0, -1, 10_001, "200", 2.5, True):
            self.assert_invalid(
                "sample_size must be an integer between 1 and 10000",
                mode="detect",
                text=COMBINED_TEXT,
                sample_size=bad,
            )

    def test_error_level_min_unknown_or_mistyped(self) -> None:
        for bad in ("VERBOSE", "notice", "", 5, True):
            self.assert_invalid(
                "level_min must be one of",
                mode="filter",
                text=LEVELED_TEXT,
                level_min=bad,
            )

    def test_error_status_min_range_and_type(self) -> None:
        for bad in (99, 600, "500", 404.5, True):
            self.assert_invalid(
                "status_min must be an integer HTTP status code",
                mode="filter",
                text=COMBINED_TEXT,
                status_min=bad,
            )

    def test_error_method_and_ip_must_be_non_empty_strings(self) -> None:
        for bad in ("", 5, True):
            self.assert_invalid(
                "method must be a non-empty string",
                mode="filter",
                text=COMBINED_TEXT,
                method=bad,
            )
            self.assert_invalid(
                "ip must be a non-empty string",
                mode="filter",
                text=COMBINED_TEXT,
                ip=bad,
            )

    def test_error_filter_requires_at_least_one_predicate(self) -> None:
        self.assert_invalid(
            "requires at least one predicate",
            mode="filter",
            text=COMBINED_TEXT,
        )

    def test_error_predicates_rejected_outside_filter_mode(self) -> None:
        self.assert_invalid(
            "only accepted in filter mode",
            mode="parse",
            text=COMBINED_TEXT,
            method="GET",
        )
        self.assert_invalid(
            "only accepted in filter mode",
            mode="detect",
            text=COMBINED_TEXT,
            status_min=200,
        )

    def test_detect_ignores_explicit_format(self) -> None:
        # detect always votes; a format hint must not change the result.
        without = self.tool.execute(mode="detect", text=COMBINED_TEXT)
        with_hint = self.tool.execute(
            mode="detect", text=COMBINED_TEXT, format="syslog"
        )
        self.assertEqual(without, with_hint)


if __name__ == "__main__":
    unittest.main()
