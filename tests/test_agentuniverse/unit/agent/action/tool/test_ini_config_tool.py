#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_ini_config_tool.py

"""Offline unit tests for IniConfigTool.

The tool is built purely on the standard library (configparser) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: parse results are checked against literal
ground-truth dicts derived from configparser's documented semantics
(DEFAULT merging, lowercased keys, raw %-free-of-interpolation values,
multiline continuation joining), and set results are checked with
exact line-level text comparisons so that comment and key-order
preservation is proven, not assumed. Error paths are covered as an
explicit matrix (parse errors with line numbers, duplicate keys and
sections, missing sections/keys, values that cannot round-trip).
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import IniConfigTool
from agentuniverse.agent.action.tool.common_tool.ini_config_tool import (
    IniConfigTool as DirectIniConfigTool,
)

# --------------------------------------------------------------------- #
# Ground-truth sample (line numbers referenced by the tests):
#   1  "; top-level comment"
#   2  "[DEFAULT]"
#   3  "timeout = 30"
#   4  "log_level = INFO"
#   5  ""
#   6  "[server]"
#   7  "host = localhost"
#   8  "port = 8080"
#   9  "; comment inside server"
#  10  "tags = a"
#  11  "  b"                     <- continuation line, value "a\nb"
#  12  ""
#  13  "[client]"
#  14  "debug = true"
# --------------------------------------------------------------------- #
SAMPLE = (
    "; top-level comment\n"
    "[DEFAULT]\n"
    "timeout = 30\n"
    "log_level = INFO\n"
    "\n"
    "[server]\n"
    "host = localhost\n"
    "port = 8080\n"
    "; comment inside server\n"
    "tags = a\n"
    "  b\n"
    "\n"
    "[client]\n"
    "debug = true\n"
)

LITERAL_DEFAULT = {"timeout": "30", "log_level": "INFO"}
LITERAL_SERVER = {"host": "localhost", "port": "8080", "tags": "a\nb"}
LITERAL_CLIENT = {"debug": "true"}

MERGED_SERVER = {
    "timeout": "30",
    "log_level": "INFO",
    "host": "localhost",
    "port": "8080",
    "tags": "a\nb",
}
MERGED_CLIENT = {"timeout": "30", "log_level": "INFO", "debug": "true"}

UNICODE_TEXT = "[sección]\nclave.dotted = ünïcode ✓\n"


class IniConfigToolParseTest(unittest.TestCase):
    """parse mode: nested dict output, DEFAULT semantics, raw values."""

    def setUp(self) -> None:
        self.tool = IniConfigTool()

    def test_parse_nested_dict_with_defaults_merged(self) -> None:
        result = self.tool.execute(mode="parse", text=SAMPLE)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "include_defaults": True,
                "result": {
                    "DEFAULT": LITERAL_DEFAULT,
                    "server": MERGED_SERVER,
                    "client": MERGED_CLIENT,
                },
                "section_count": 3,
                "option_count": 6,
            },
        )

    def test_parse_include_defaults_false_keeps_literal_keys(self) -> None:
        result = self.tool.execute(
            mode="parse", text=SAMPLE, include_defaults=False
        )
        self.assertEqual(result["include_defaults"], False)
        self.assertEqual(
            result["result"],
            {
                "DEFAULT": dict(LITERAL_DEFAULT),
                "server": dict(LITERAL_SERVER),
                "client": dict(LITERAL_CLIENT),
            },
        )

    def test_parse_section_override_wins_over_default(self) -> None:
        text = "[DEFAULT]\nd = 1\n[a]\nx = 2\n[a2]\nd = 9\n"
        result = self.tool.execute(mode="parse", text=text)
        # configparser items() semantics: DEFAULT keys first (overridden
        # in place), then the section's own keys.
        self.assertEqual(result["result"]["a"], {"d": "1", "x": "2"})
        self.assertEqual(result["result"]["a2"], {"d": "9"})

    def test_parse_section_names_case_sensitive_keys_lowered(self) -> None:
        result = self.tool.execute(mode="parse", text="[Section One]\nKeyWord = v\n")
        self.assertEqual(result["result"], {"Section One": {"keyword": "v"}})

    def test_parse_raw_percent_values_no_interpolation(self) -> None:
        text = "[paths]\nroot = %(BASE)s/share\nfmt = 100%% done\n"
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(
            result["result"]["paths"],
            {"root": "%(BASE)s/share", "fmt": "100%% done"},
        )

    def test_parse_inline_comment_text_is_kept(self) -> None:
        # Inline comments are disabled by default in configparser, so
        # everything after the delimiter is the value.
        result = self.tool.execute(mode="parse", text="[a]\nk = v ; note\n")
        self.assertEqual(result["result"]["a"]["k"], "v ; note")

    def test_parse_multiline_continuation_joins_with_newline(self) -> None:
        result = self.tool.execute(
            mode="parse", text="[a]\nk = first\n  second\n    third\n"
        )
        self.assertEqual(result["result"]["a"]["k"], "first\nsecond\nthird")

    def test_parse_blank_line_inside_value_is_preserved(self) -> None:
        result = self.tool.execute(
            mode="parse", text="[a]\nk = first\n\n  second\n"
        )
        self.assertEqual(result["result"]["a"]["k"], "first\n\nsecond")

    def test_parse_comment_between_continuations_is_skipped(self) -> None:
        result = self.tool.execute(
            mode="parse", text="[a]\nk = first\n# interleaved\n  second\n"
        )
        self.assertEqual(result["result"]["a"]["k"], "first\nsecond")

    def test_parse_colon_delimiter_and_empty_values(self) -> None:
        result = self.tool.execute(
            mode="parse", text="[a]\nhost: example.org\nempty =\n"
        )
        self.assertEqual(
            result["result"]["a"], {"host": "example.org", "empty": ""}
        )

    def test_parse_unicode_sections_and_values(self) -> None:
        result = self.tool.execute(mode="parse", text=UNICODE_TEXT)
        self.assertEqual(
            result["result"], {"sección": {"clave.dotted": "ünïcode ✓"}}
        )

    def test_parse_comment_only_text_has_no_sections(self) -> None:
        result = self.tool.execute(mode="parse", text="\n; nothing here\n")
        self.assertEqual(result["result"], {})
        self.assertEqual(result["section_count"], 0)
        self.assertEqual(result["option_count"], 0)

    def test_parse_duplicate_key_is_a_parse_error(self) -> None:
        result = self.tool.execute(mode="parse", text="[a]\nk = 1\nk = 2\n")
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["error"]["type"], "parse_error")
        self.assertEqual(result["error"]["error_class"], "DuplicateOptionError")
        self.assertEqual(result["error"]["line"], 3)
        self.assertNotIn("result", result)

    def test_parse_duplicate_section_is_a_parse_error(self) -> None:
        result = self.tool.execute(mode="parse", text="[a]\nk = 1\n[a]\nj = 2\n")
        self.assertEqual(result["error"]["error_class"], "DuplicateSectionError")
        self.assertEqual(result["error"]["line"], 3)

    def test_parse_bad_line_reports_line_number(self) -> None:
        result = self.tool.execute(mode="parse", text="[a]\nk = 1\noops\n")
        self.assertEqual(result["error"]["type"], "parse_error")
        self.assertEqual(result["error"]["error_class"], "ParsingError")
        self.assertEqual(result["error"]["line"], 2 + 1)
        self.assertIsNone(result["error"]["column"])

    def test_parse_unparseable_text_missing_section_header(self) -> None:
        result = self.tool.execute(mode="parse", text="k = 1\n[a]\n")
        self.assertEqual(
            result["error"]["error_class"], "MissingSectionHeaderError"
        )
        self.assertEqual(result["error"]["line"], 1)


class IniConfigToolGetTest(unittest.TestCase):
    """get mode: value lookup with DEFAULT fallback and error listing."""

    def setUp(self) -> None:
        self.tool = IniConfigTool()

    def test_get_existing_key_from_section(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="server", key="port"
        )
        self.assertEqual(
            result,
            {
                "mode": "get",
                "section": "server",
                "key": "port",
                "result": "8080",
                "source": "section",
            },
        )

    def test_get_key_is_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="server", key="PORT"
        )
        self.assertEqual(result["result"], "8080")

    def test_get_value_inherited_from_default(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="client", key="timeout"
        )
        self.assertEqual(result["result"], "30")
        self.assertEqual(result["source"], "DEFAULT")

    def test_get_direct_default_section_lookup(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="DEFAULT", key="log_level"
        )
        self.assertEqual(result["result"], "INFO")
        self.assertEqual(result["source"], "section")

    def test_get_multiline_value(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="server", key="tags"
        )
        self.assertEqual(result["result"], "a\nb")

    def test_get_missing_key_lists_available_keys(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="server", key="worker"
        )
        self.assertEqual(result["error"]["type"], "key_not_found")
        message = result["error"]["message"]
        self.assertIn("'server'", message)
        self.assertIn("'worker'", message)
        for available in ("host", "log_level", "port", "tags", "timeout"):
            self.assertIn(available, message)

    def test_get_missing_section_lists_available_sections(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="db", key="port"
        )
        self.assertEqual(result["error"]["type"], "section_not_found")
        message = result["error"]["message"]
        self.assertIn("'db'", message)
        for available in ("DEFAULT", "server", "client"):
            self.assertIn(available, message)

    def test_get_fallback_returned_for_missing_key(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="server", key="worker",
            fallback="4",
        )
        self.assertEqual(result["result"], "4")
        self.assertEqual(result["source"], "fallback")

    def test_get_fallback_returned_for_missing_section(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="db", key="port", fallback=""
        )
        self.assertEqual(result["result"], "")
        self.assertEqual(result["source"], "fallback")

    def test_get_on_unparseable_text_is_a_parse_error(self) -> None:
        result = self.tool.execute(
            mode="get", text="[a]\nnope\n", section="a", key="k"
        )
        self.assertEqual(result["error"]["type"], "parse_error")


class IniConfigToolSetTest(unittest.TestCase):
    """set mode: string-level patching with comment/order preservation."""

    def setUp(self) -> None:
        self.tool = IniConfigTool()

    def test_set_replaces_only_the_target_line(self) -> None:
        result = self.tool.execute(
            mode="set", text=SAMPLE, section="server", key="port", value="9090"
        )
        self.assertEqual(result["action"], "replaced")
        self.assertEqual(result["line"], 8)
        expected = SAMPLE.replace("port = 8080", "port = 9090")
        self.assertEqual(result["result"], expected)
        original_lines = SAMPLE.splitlines()
        new_lines = result["result"].splitlines()
        self.assertEqual(len(new_lines), len(original_lines))
        diff = [
            (i, a, b)
            for i, (a, b) in enumerate(zip(original_lines, new_lines))
            if a != b
        ]
        self.assertEqual(diff, [(7, "port = 8080", "port = 9090")])

    def test_set_preserves_unrelated_comments_everywhere(self) -> None:
        result = self.tool.execute(
            mode="set", text=SAMPLE, section="client", key="debug", value="false"
        )
        # The top-level, in-section and blank-line structure survives:
        self.assertEqual(result["result"], SAMPLE.replace("debug = true", "debug = false"))
        for comment in ("; top-level comment", "; comment inside server"):
            self.assertIn(comment, result["result"])

    def test_set_appends_key_before_next_sections_comment(self) -> None:
        text = (
            "# header comment\n"
            "[server]\n"
            "host = localhost\n"
            "\n"
            "; client settings below\n"
            "[client]\n"
            "debug = true\n"
        )
        result = self.tool.execute(
            mode="set", text=text, section="server", key="port", value="8080"
        )
        self.assertEqual(result["action"], "added")
        self.assertEqual(result["line"], 4)
        self.assertEqual(
            result["result"],
            "# header comment\n"
            "[server]\n"
            "host = localhost\n"
            "port = 8080\n"
            "\n"
            "; client settings below\n"
            "[client]\n"
            "debug = true\n",
        )

    def test_set_appends_after_last_continuation_line(self) -> None:
        result = self.tool.execute(
            mode="set", text=SAMPLE, section="server", key="workers", value="4"
        )
        self.assertEqual(result["action"], "added")
        self.assertEqual(result["line"], 12)
        self.assertEqual(
            result["result"],
            SAMPLE.replace("  b\n\n[client]", "  b\nworkers = 4\n\n[client]"),
        )

    def test_set_creates_missing_section_at_end(self) -> None:
        result = self.tool.execute(
            mode="set", text=SAMPLE, section="extra", key="mode", value="fast"
        )
        self.assertEqual(result["action"], "created_section")
        self.assertEqual(result["line"], 16)
        self.assertEqual(result["result"], SAMPLE + "[extra]\nmode = fast\n")

    def test_set_section_names_are_case_sensitive(self) -> None:
        # configparser treats 'Server' and 'server' as distinct
        # sections; setting the wrong case creates a new section.
        result = self.tool.execute(
            mode="set", text="[server]\nport = 1\n", section="Server",
            key="port", value="2",
        )
        self.assertEqual(result["action"], "created_section")
        self.assertEqual(
            result["result"], "[server]\nport = 1\n[Server]\nport = 2\n"
        )

    def test_set_keeps_original_key_spelling_and_delimiter_style(self) -> None:
        cases = [
            ("[a]\nPort = 8080\n", "PORT", "[a]\nPort = 9090\n"),
            ("[a]\nport=8080\n", "port", "[a]\nport=9090\n"),
            ("[a]\nport: 8080\n", "port", "[a]\nport: 9090\n"),
        ]
        for text, key, expected in cases:
            with self.subTest(text=text):
                result = self.tool.execute(
                    mode="set", text=text, section="a", key=key, value="9090"
                )
                self.assertEqual(result["action"], "replaced")
                self.assertEqual(result["result"], expected)

    def test_set_multiline_value_becomes_continuation_lines(self) -> None:
        result = self.tool.execute(
            mode="set", text="[a]\nk = one\nj = 2\n", section="a",
            key="k", value="x\ny",
        )
        self.assertEqual(result["result"], "[a]\nk = x\n y\nj = 2\n")
        reparsed = self.tool.execute(
            mode="parse", text=result["result"], include_defaults=False
        )
        self.assertEqual(reparsed["result"]["a"]["k"], "x\ny")

    def test_set_drops_old_continuation_lines_when_patching(self) -> None:
        result = self.tool.execute(
            mode="set", text="[a]\nk = one\n  two\nj = 2\n", section="a",
            key="k", value="v",
        )
        self.assertEqual(result["result"], "[a]\nk = v\nj = 2\n")

    def test_set_adds_key_to_default_section(self) -> None:
        result = self.tool.execute(
            mode="set", text=SAMPLE, section="DEFAULT", key="retries", value="3"
        )
        self.assertEqual(result["action"], "added")
        self.assertEqual(result["line"], 5)
        self.assertEqual(
            result["result"],
            SAMPLE.replace("log_level = INFO\n", "log_level = INFO\nretries = 3\n"),
        )

    def test_set_without_trailing_newline_keeps_shape(self) -> None:
        result = self.tool.execute(
            mode="set", text="[a]\nk = 1", section="a", key="k", value="2"
        )
        self.assertEqual(result["result"], "[a]\nk = 2")

    def test_set_append_on_text_without_trailing_newline(self) -> None:
        result = self.tool.execute(
            mode="set", text="[a]\nk = 1", section="a", key="j", value="2"
        )
        self.assertEqual(result["result"], "[a]\nk = 1\nj = 2\n")

    def test_set_survives_blank_line_inside_multiline_value(self) -> None:
        # A blank line inside a value is part of the value; appending
        # after the whole value must not corrupt it.
        result = self.tool.execute(
            mode="set", text="[a]\nk = first\n\n  second\n", section="a",
            key="new", value="1",
        )
        self.assertEqual(
            result["result"], "[a]\nk = first\n\n  second\nnew = 1\n"
        )

    def test_set_keeps_deep_comment_after_multiline_value(self) -> None:
        # A full-line comment is never part of a value per configparser
        # (however deeply indented), so patching the value must leave it
        # in the file. Regression test: it used to be swallowed by the
        # contiguous continuation-range deletion.
        result = self.tool.execute(
            mode="set", text="[a]\nk = v1\n  v2\n    # deep comment\n",
            section="a", key="k", value="z",
        )
        self.assertEqual(
            result["result"], "[a]\nk = z\n    # deep comment\n"
        )

    def test_set_keeps_comment_between_key_and_continuation(self) -> None:
        # Comments do not close a multiline value either (configparser
        # skips them without ending the option), but they are still not
        # value members and must survive the patch.
        result = self.tool.execute(
            mode="set", text="[a]\nk = v1\n\n# interleaved\n  v2\n",
            section="a", key="k", value="z",
        )
        self.assertEqual(result["result"], "[a]\nk = z\n\n# interleaved\n")

    def test_set_keeps_comment_between_continuation_lines(self) -> None:
        result = self.tool.execute(
            mode="set",
            text="[a]\nk = v1\n  v2\n;c1\n  v3\nj = 2\n",
            section="a", key="k", value="z",
        )
        self.assertEqual(result["result"], "[a]\nk = z\n;c1\nj = 2\n")
        # and the new value must read back exactly
        parsed = self.tool.execute(mode="parse", text=result["result"])
        self.assertEqual(parsed["result"]["a"], {"k": "z", "j": "2"})

    def test_set_multiline_value_keeps_interleaved_blank_line(self) -> None:
        # Interior blank lines belong to the old value in parsed form but
        # are not deleted with it; the re-parsed structure stays correct
        # (configparser rstrips trailing value whitespace).
        result = self.tool.execute(
            mode="set", text="[a]\nk = v1\n  v2\n\n  v3\n", section="a",
            key="k", value="z",
        )
        self.assertEqual(result["result"], "[a]\nk = z\n\n")
        parsed = self.tool.execute(mode="parse", text=result["result"])
        self.assertEqual(parsed["result"]["a"]["k"], "z")

    def test_set_multiline_replacement_is_idempotent(self) -> None:
        text = "[a]\nk = v1\n  v2\n    # deep comment\n"
        first = self.tool.execute(
            mode="set", text=text, section="a", key="k", value="n1\nn2"
        )
        second = self.tool.execute(
            mode="set", text=first["result"], section="a", key="k",
            value="n1\nn2",
        )
        self.assertEqual(first["result"], second["result"])
        self.assertEqual(
            first["result"], "[a]\nk = n1\n n2\n    # deep comment\n"
        )

    def test_set_value_that_cannot_round_trip_is_rejected(self) -> None:
        # Continuation lines lose their indentation on read, so a value
        # whose second line is padded can never round-trip.
        result = self.tool.execute(
            mode="set", text="[a]\nk = old\n", section="a",
            key="k", value="line1\n  padded",
        )
        self.assertEqual(result["error"]["type"], "unrepresentable_value")
        self.assertNotIn("result", result)

    def test_set_value_whose_continuation_would_be_a_comment(self) -> None:
        result = self.tool.execute(
            mode="set", text="[a]\nk = old\n", section="a",
            key="k", value="line1\n# not a comment to configparser",
        )
        self.assertEqual(result["error"]["type"], "unrepresentable_value")

    def test_set_guards_against_exotic_newline_corruption(self) -> None:
        # U+0085 is a line separator for str.splitlines but NOT for
        # configparser; a naive insert would corrupt the value. The
        # post-edit verification must catch it and return an error
        # instead of broken text.
        text = "[a]\nk = " + "a" + chr(0x85) + "b\n"
        result = self.tool.execute(
            mode="set", text=text, section="a", key="new", value="1"
        )
        self.assertIn(
            result.get("error", {}).get("type"),
            ("unrepresentable_value", "patch_failed"),
        )
        self.assertNotIn("result", result)

    def test_set_on_unparseable_text_is_a_parse_error(self) -> None:
        result = self.tool.execute(
            mode="set", text="[a\nk = 1\n", section="a", key="k", value="2"
        )
        self.assertEqual(result["error"]["type"], "parse_error")
        self.assertNotIn("result", result)

    def test_set_on_duplicate_key_text_is_a_parse_error(self) -> None:
        result = self.tool.execute(
            mode="set", text="[a]\nk = 1\nk = 2\n", section="a",
            key="k", value="3",
        )
        self.assertEqual(result["error"]["error_class"], "DuplicateOptionError")


class IniConfigToolSectionsTest(unittest.TestCase):
    """sections mode: file-order listing with literal key counts."""

    def setUp(self) -> None:
        self.tool = IniConfigTool()

    def test_sections_listing_with_key_counts(self) -> None:
        result = self.tool.execute(mode="sections", text=SAMPLE)
        self.assertEqual(
            result,
            {
                "mode": "sections",
                "default_section": "DEFAULT",
                "count": 3,
                "result": [
                    {"name": "DEFAULT", "key_count": 2},
                    {"name": "server", "key_count": 3},
                    {"name": "client", "key_count": 1},
                ],
            },
        )

    def test_sections_counts_are_literal_not_merged(self) -> None:
        # [DEFAULT] keys are not counted in the other sections.
        result = self.tool.execute(
            mode="sections", text="[DEFAULT]\nd = 1\n[a]\nx = 2\ny = 3\n"
        )
        self.assertEqual(
            result["result"],
            [
                {"name": "DEFAULT", "key_count": 1},
                {"name": "a", "key_count": 2},
            ],
        )

    def test_sections_empty_section_has_zero_keys(self) -> None:
        result = self.tool.execute(mode="sections", text="[a]\n[b]\nk = 1\n")
        self.assertEqual(
            result["result"],
            [
                {"name": "a", "key_count": 0},
                {"name": "b", "key_count": 1},
            ],
        )

    def test_sections_comment_only_text(self) -> None:
        result = self.tool.execute(mode="sections", text="; nothing\n")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["result"], [])

    def test_sections_on_unparseable_text(self) -> None:
        result = self.tool.execute(mode="sections", text="[a]\nraw line\n")
        self.assertEqual(result["error"]["type"], "parse_error")


class IniConfigToolValidateTest(unittest.TestCase):
    """validate mode: strict parse attempt with error positions."""

    def setUp(self) -> None:
        self.tool = IniConfigTool()

    def test_validate_ok_reports_counts(self) -> None:
        result = self.tool.execute(mode="validate", text=SAMPLE)
        self.assertEqual(
            result,
            {
                "mode": "validate",
                "valid": True,
                "section_count": 3,
                "option_count": 6,
            },
        )

    def test_validate_error_matrix(self) -> None:
        cases = [
            ("[a]\nk = 1\noops\n", "ParsingError", 3),
            ("[a]\nkey\n", "ParsingError", 2),
            ("k = 1\n[a]\n", "MissingSectionHeaderError", 1),
            ("[a\nk = 1\n", "MissingSectionHeaderError", 1),
            ("[a]\nk = 1\nk = 2\n", "DuplicateOptionError", 3),
            ("[a]\nk=1\n[a]\nk=2\n", "DuplicateSectionError", 3),
        ]
        for text, error_class, line in cases:
            with self.subTest(text=text):
                result = self.tool.execute(mode="validate", text=text)
                self.assertEqual(result["mode"], "validate")
                self.assertIs(result["valid"], False)
                self.assertEqual(result["error"]["type"], "parse_error")
                self.assertEqual(result["error"]["error_class"], error_class)
                self.assertEqual(result["error"]["line"], line)
                self.assertIsNone(result["error"]["column"])
                self.assertTrue(result["error"]["message"])

    def test_validate_multi_digit_line_numbers(self) -> None:
        text = "[a]\n" + "".join(f"k{i} = {i}\n" for i in range(9)) + "oops\n"
        result = self.tool.execute(mode="validate", text=text)
        self.assertIs(result["valid"], False)
        self.assertEqual(result["error"]["line"], 11)

    def test_validate_accumulates_multiple_bad_lines_reports_first(self) -> None:
        result = self.tool.execute(mode="validate", text="[a]\nbad1 x\nbad2 x\n")
        self.assertIs(result["valid"], False)
        self.assertEqual(result["error"]["line"], 2)


class IniConfigToolValidationTest(unittest.TestCase):
    """Strict parameter validation raises ValueError before any work."""

    def setUp(self) -> None:
        self.tool = IniConfigTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="ini", text=SAMPLE)
        self.assert_invalid(mode=None, text=SAMPLE)
        self.assert_invalid(mode=123, text=SAMPLE)
        self.assert_invalid(mode="PARSE", text=SAMPLE)

    def test_invalid_text(self) -> None:
        for bad in (None, "", 123, True, b"[a]\n", ["[a]\n"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", text=bad)
                self.assert_invalid(mode="validate", text=bad)

    def test_text_length_limit(self) -> None:
        oversized = "[a]\nk = " + "v" * 100_000 + "\n"
        self.assert_invalid(mode="parse", text=oversized)
        ok = self.tool.execute(mode="validate", text="[a]\nk = " + "v" * 99_000)
        self.assertIs(ok["valid"], True)

    def test_invalid_section(self) -> None:
        for bad in (None, "", "a]b", "a[b", "a\nb", 123, True):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="get", text=SAMPLE, section=bad, key="port"
                )
                self.assert_invalid(
                    mode="set", text=SAMPLE, section=bad, key="k", value="v"
                )

    def test_invalid_key(self) -> None:
        for bad in (None, "", "a=b", "a:b", " padded", "padded ", "#hash",
                    ";semi", "a\nb", 123, True):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="get", text=SAMPLE, section="server", key=bad
                )
                self.assert_invalid(
                    mode="set", text=SAMPLE, section="server", key=bad, value="v"
                )

    def test_invalid_value(self) -> None:
        for bad in (None, 123, True, " padded", "padded ", "a\rb"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="set", text=SAMPLE, section="server", key="k", value=bad
                )

    def test_invalid_fallback_and_include_defaults(self) -> None:
        self.assert_invalid(
            mode="get", text=SAMPLE, section="server", key="k", fallback=5
        )
        self.assert_invalid(
            mode="get", text=SAMPLE, section="server", key="k", fallback=True
        )
        self.assert_invalid(mode="parse", text=SAMPLE, include_defaults="yes")
        self.assert_invalid(mode="parse", text=SAMPLE, include_defaults=1)

    def test_fallback_accepts_empty_string(self) -> None:
        result = self.tool.execute(
            mode="get", text=SAMPLE, section="server", key="absent", fallback=""
        )
        self.assertEqual(result["source"], "fallback")


class IniConfigToolPackagingTest(unittest.TestCase):
    """Packaging / registration."""

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectIniConfigTool, IniConfigTool)
        tool = IniConfigTool()
        self.assertEqual(tool.name, "ini_config_tool")
        for word in ("parse", "get", "set", "sections", "validate", "INI"):
            self.assertIn(word, tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("IniConfigTool", __all__)


if __name__ == "__main__":
    unittest.main()
