#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_env_file_tool.py

"""Offline unit tests for EnvFileTool.

The tool is built purely on the standard library (re) and operates only
on in-memory text, so this suite runs fully offline. Every assertion is
deterministic: parse results are compared against hand-computed ground
truths that cover each dotenv quoting rule (double-quote escapes,
single-quote literals, unquoted inline comments, escaped hashes),
export prefixes, duplicate keys (last-wins plus the duplicates list),
line-level ``set`` patches are compared as *exact* expected texts,
``serialize`` output against the canonical form including every quoting
decision, and ``validate`` against known reference sets.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import EnvFileTool
from agentuniverse.agent.action.tool.common_tool.env_file_tool import (
    EnvFileTool as DirectEnvFileTool,
)

BASIC_TEXT = (
    "# Service configuration\n"
    "DEBUG=true\n"
    "\n"
    "export API_HOST = localhost\n"
    "API_PORT=8080\n"
    "EMPTY=\n"
)

QUOTING_TEXT = "\n".join(
    [
        'DOUBLE="line1\\nline2"',
        'TABS="a\\tb"',
        'SLASH="a\\\\b"',
        'QUOTE="say \\"hi\\""',
        "SINGLE='a\\nb \\\\ kept'",
        "UNQ=value # trailing comment",
        "HASHKEEP=a#b",
        "ESCHASH=a\\#b",
        "HASHSTART=# only a comment",
        "TRAILQ=\"v\" # after closing quote",
        "ONLYWS=   # comment after whitespace",
        'UNKNOWN="a\\qb"',
        'CR="a\\rb"',
        'EDQ=""',
        "ESQ=''",
        "SHIELD=a \\# b # real comment",
        "LEADWS=  spaced  ",
        "HASHDIRECT=#data",
    ]
)

DUPLICATE_TEXT = (
    "MODE=first\n"
    "# comment\n"
    "MODE=second\n"
    "OTHER=x\n"
    "MODE=third\n"
)

MALFORMED_TEXT = "\n".join(
    [
        "NOT_AN_ASSIGNMENT",
        "=value",
        "1KEY=v",
        "KEY KEy=v",
        "export KEY",
        "--",
    ]
) + "\n"

VALIDATE_TEXT = "\n".join(
    [
        "BASE_URL=https://api",
        "API=${BASE_URL}/v1",
        "TOKEN=$MISSING_TOKEN",
        "BOTH=${MISSING_A} and $MISSING_A",
        "LIT=$$not and $5 and $ none",
        "SELF=$SELF",
    ]
) + "\n"


class EnvFileToolParseTest(unittest.TestCase):
    """Offline deterministic test cases for parse mode."""

    def setUp(self) -> None:
        self.tool = EnvFileTool()

    def test_parse_basic_structure_and_metadata(self) -> None:
        result = self.tool.execute(mode="parse", text=BASIC_TEXT)
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["count"], 4)
        self.assertEqual(list(result["variables"]), ["DEBUG", "API_HOST", "API_PORT", "EMPTY"])
        self.assertEqual(result["blank_lines"], 1)
        self.assertEqual(result["comment_lines"], 1)
        self.assertEqual(result["malformed_lines"], [])
        self.assertEqual(result["duplicates"], [])

        debug = result["variables"]["DEBUG"]
        self.assertEqual(
            debug,
            {"value": "true", "raw": "true", "line": 2, "exported": False, "lines": [2]},
        )
        host = result["variables"]["API_HOST"]
        self.assertEqual(host["value"], "localhost")
        self.assertEqual(host["raw"], "localhost")
        self.assertEqual(host["line"], 4)
        self.assertTrue(host["exported"])
        self.assertEqual(result["variables"]["EMPTY"]["value"], "")
        self.assertIn("4 variable(s)", result["result"])

    def test_parse_quoting_rules_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", text=QUOTING_TEXT)
        expected = {
            # Double quotes unescape \n \t \\ \" (and \r); unknown
            # escapes stay literal; raw keeps the source form.
            "DOUBLE": ("line1\nline2", '"line1\\nline2"'),
            "TABS": ("a\tb", '"a\\tb"'),
            "SLASH": ("a\\b", '"a\\\\b"'),
            "QUOTE": ('say "hi"', '"say \\"hi\\""'),
            # Single quotes are fully literal (deliberate divergence
            # from python-dotenv, which unescapes \\ and \' inside
            # single quotes): the tool contract says single = literal.
            "SINGLE": ("a\\nb \\\\ kept", "'a\\nb \\\\ kept'"),
            "UNQ": ("value", "value # trailing comment"),
            "HASHKEEP": ("a#b", "a#b"),
            # \# shields the comment and stays in the value as written
            # (python-dotenv behavior).
            "ESCHASH": ("a\\#b", "a\\#b"),
            # A '#' glued directly after '=' (no whitespace) is data.
            "HASHSTART": ("# only a comment", "# only a comment"),
            "TRAILQ": ("v", '"v" # after closing quote'),
            "ONLYWS": ("", "# comment after whitespace"),
            "UNKNOWN": ("a\\qb", '"a\\qb"'),
            "CR": ("a\rb", '"a\\rb"'),
            "EDQ": ("", '""'),
            "ESQ": ("", "''"),
            "SHIELD": ("a \\# b", "a \\# b # real comment"),
            "LEADWS": ("spaced", "spaced"),
            "HASHDIRECT": ("#data", "#data"),
        }
        for key, (value, raw) in expected.items():
            self.assertEqual(result["variables"][key]["value"], value, key)
            self.assertEqual(result["variables"][key]["raw"], raw, key)
        self.assertEqual(list(result["variables"]), list(expected))

    def test_parse_matches_python_dotenv_reference(self) -> None:
        """Cross-checked by hand against python-dotenv's dotenv_values.

        python-dotenv is NOT a dependency of the tool; these vectors
        were produced with it once and are asserted offline here. The
        single-quote case is the documented exception (fully literal).
        """
        text = "\n".join(
            [
                "A=a \\#b",
                "B=a\\#b",
                "C=\\#b",
                "D=#c",
                "E= #c",
                "F=value   ",
                "G=a#b",
                "H=a  #  c  ",
                "I=a \\# b # c",
                "J=$x",
                "K=a\\nb",
            ]
        ) + "\n"
        result = self.tool.execute(mode="parse", text=text)
        expected = {
            "A": "a \\#b",
            "B": "a\\#b",
            "C": "\\#b",
            "D": "#c",
            "E": "",
            "F": "value",
            "G": "a#b",
            "H": "a",
            "I": "a \\# b",
            "J": "$x",
            "K": "a\\nb",
        }
        self.assertEqual(
            {k: v["value"] for k, v in result["variables"].items()}, expected
        )

    def test_parse_spaces_around_equals_are_valid(self) -> None:
        result = self.tool.execute(mode="parse", text="  KEY  =  spaced  \n")
        entry = result["variables"]["KEY"]
        self.assertEqual(entry["value"], "spaced")
        self.assertEqual(entry["raw"], "spaced")
        self.assertEqual(entry["line"], 1)

    def test_parse_first_equals_splits_key_from_value(self) -> None:
        result = self.tool.execute(mode="parse", text="URL=https://x/?a=b\n")
        self.assertEqual(result["variables"]["URL"]["value"], "https://x/?a=b")

    def test_parse_duplicates_last_wins(self) -> None:
        result = self.tool.execute(mode="parse", text=DUPLICATE_TEXT)
        self.assertEqual(list(result["variables"]), ["MODE", "OTHER"])
        mode = result["variables"]["MODE"]
        self.assertEqual(mode["value"], "third")
        self.assertEqual(mode["line"], 5)
        self.assertEqual(mode["lines"], [1, 3, 5])
        self.assertEqual(
            result["duplicates"], [{"key": "MODE", "lines": [1, 3, 5]}]
        )
        self.assertEqual(result["variables"]["OTHER"]["value"], "x")
        self.assertIn("1 duplicated key(s)", result["result"])

    def test_parse_malformed_lines_are_listed_not_raised(self) -> None:
        result = self.tool.execute(mode="parse", text=MALFORMED_TEXT)
        self.assertEqual(result["count"], 0)
        self.assertEqual(
            result["malformed_lines"],
            [
                {"line": 1, "content": "NOT_AN_ASSIGNMENT"},
                {"line": 2, "content": "=value"},
                {"line": 3, "content": "1KEY=v"},
                {"line": 4, "content": "KEY KEy=v"},
                {"line": 5, "content": "export KEY"},
                {"line": 6, "content": "--"},
            ],
        )
        self.assertIn("6 malformed line(s)", result["result"])

    def test_parse_unterminated_double_quote(self) -> None:
        result = self.tool.execute(mode="parse", text="OK=1\nBAD=\"unclosed\n")
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["error"]["type"], "unterminated_quote")
        self.assertIn("line 2", result["error"]["message"])

    def test_parse_unterminated_single_quote(self) -> None:
        result = self.tool.execute(mode="parse", text="BAD='unclosed\n")
        self.assertEqual(result["error"]["type"], "unterminated_quote")
        self.assertIn("line 1", result["error"]["message"])

    def test_parse_key_named_export_without_value_is_valid(self) -> None:
        # "export" itself is a legal key when directly followed by '='.
        result = self.tool.execute(mode="parse", text="export=v\nexport KEY=v\n")
        self.assertEqual(result["variables"]["export"]["value"], "v")
        self.assertFalse(result["variables"]["export"]["exported"])
        self.assertTrue(result["variables"]["KEY"]["exported"])


class EnvFileToolGetTest(unittest.TestCase):
    """Offline deterministic test cases for get mode."""

    def setUp(self) -> None:
        self.tool = EnvFileTool()

    def test_get_found(self) -> None:
        result = self.tool.execute(mode="get", text=BASIC_TEXT, key="API_HOST")
        self.assertEqual(
            result,
            {
                "mode": "get",
                "key": "API_HOST",
                "value": "localhost",
                "raw": "localhost",
                "line": 4,
                "exported": True,
                "lines": [4],
                "result": "localhost",
            },
        )

    def test_get_missing_key_error(self) -> None:
        result = self.tool.execute(mode="get", text=BASIC_TEXT, key="NOPE")
        self.assertEqual(result["mode"], "get")
        self.assertEqual(result["key"], "NOPE")
        self.assertEqual(result["error"]["type"], "key_not_found")
        self.assertIn("API_HOST", result["error"]["message"])

    def test_get_is_case_sensitive(self) -> None:
        result = self.tool.execute(mode="get", text=BASIC_TEXT, key="debug")
        self.assertEqual(result["error"]["type"], "key_not_found")

    def test_get_duplicate_key_returns_last(self) -> None:
        result = self.tool.execute(mode="get", text=DUPLICATE_TEXT, key="MODE")
        self.assertEqual(result["value"], "third")
        self.assertEqual(result["line"], 5)


class EnvFileToolSetTest(unittest.TestCase):
    """Offline deterministic test cases for set mode (exact patched text)."""

    def setUp(self) -> None:
        self.tool = EnvFileTool()

    def test_set_updates_in_place_preserving_everything(self) -> None:
        text = "# header\nHOST=localhost\n\nPORT=8080\n# trailing note\n"
        result = self.tool.execute(mode="set", text=text, key="HOST", value="example.com")
        self.assertEqual(
            result["result"],
            "# header\nHOST=example.com\n\nPORT=8080\n# trailing note\n",
        )
        self.assertEqual(result["updated_line"], 2)
        self.assertEqual(result["removed_duplicate_lines"], [])
        self.assertFalse(result["appended"])

    def test_set_updates_first_and_removes_later_duplicates(self) -> None:
        text = "MODE=a\nOTHER=1\nMODE=b\nMODE=c\nLAST=z\n"
        result = self.tool.execute(mode="set", text=text, key="MODE", value="final")
        self.assertEqual(result["result"], "MODE=final\nOTHER=1\nLAST=z\n")
        self.assertEqual(result["updated_line"], 1)
        self.assertEqual(result["removed_duplicate_lines"], [3, 4])

    def test_set_appends_before_trailing_comments(self) -> None:
        text = "A=1\nB=2\n\n# trailing\n\n# more\n"
        result = self.tool.execute(mode="set", text=text, key="NEW", value="n")
        self.assertEqual(result["result"], "A=1\nB=2\nNEW=n\n\n# trailing\n\n# more\n")
        self.assertTrue(result["appended"])
        self.assertEqual(result["updated_line"], 3)

    def test_set_appends_at_end_without_trailing_comments(self) -> None:
        result = self.tool.execute(mode="set", text="A=1\n", key="B", value="2")
        self.assertEqual(result["result"], "A=1\nB=2\n")

    def test_set_preserves_missing_trailing_newline_style(self) -> None:
        result = self.tool.execute(mode="set", text="A=1", key="B", value="2")
        self.assertEqual(result["result"], "A=1\nB=2")

    def test_set_appends_to_comment_only_file_at_end(self) -> None:
        result = self.tool.execute(mode="set", text="# just a header\n", key="K", value="v")
        self.assertEqual(result["result"], "# just a header\nK=v\n")

    def test_set_on_empty_text_creates_single_assignment(self) -> None:
        result = self.tool.execute(mode="set", text="", key="K", value="v")
        self.assertEqual(result["result"], "K=v\n")
        self.assertTrue(result["appended"])

    def test_set_quotes_values_needing_it(self) -> None:
        result = self.tool.execute(mode="set", text="A=1\n", key="A", value="hello world")
        self.assertEqual(result["result"], 'A="hello world"\n')

    def test_set_normalizes_previous_quoting(self) -> None:
        result = self.tool.execute(mode="set", text='A="old"\n', key="A", value="new")
        self.assertEqual(result["result"], "A=new\n")

    def test_set_replaces_the_whole_assignment_line(self) -> None:
        # An inline comment on the replaced line is overwritten with it;
        # comments on other lines are untouched.
        result = self.tool.execute(mode="set", text="A=old # note\nB=1 # keep\n", key="A", value="new")
        self.assertEqual(result["result"], "A=new\nB=1 # keep\n")

    def test_set_escapes_newline_in_value(self) -> None:
        result = self.tool.execute(mode="set", text="A=old\n", key="A", value="x\ny")
        self.assertEqual(result["result"], 'A="x\\ny"\n')

    def test_set_empty_value(self) -> None:
        result = self.tool.execute(mode="set", text="A=old\n", key="A", value="")
        self.assertEqual(result["result"], "A=\n")

    def test_set_preserves_existing_export_prefix(self) -> None:
        result = self.tool.execute(mode="set", text="export A=1\nB=2\n", key="A", value="9")
        self.assertEqual(result["result"], "export A=9\nB=2\n")
        self.assertTrue(result["export"])

    def test_set_export_true_adds_prefix(self) -> None:
        result = self.tool.execute(
            mode="set", text="A=1\nB=2\n", key="B", value="9", export=True
        )
        self.assertEqual(result["result"], "A=1\nexport B=9\n")

    def test_set_export_false_removes_prefix(self) -> None:
        result = self.tool.execute(
            mode="set", text="export A=1\n", key="A", value="9", export=False
        )
        self.assertEqual(result["result"], "A=9\n")

    def test_set_round_trip_with_parse(self) -> None:
        patched = self.tool.execute(
            mode="set", text=BASIC_TEXT, key="API_PORT", value="9090"
        )["result"]
        reparsed = self.tool.execute(mode="parse", text=patched)
        self.assertEqual(reparsed["variables"]["API_PORT"]["value"], "9090")
        self.assertEqual(reparsed["comment_lines"], 1)
        self.assertEqual(reparsed["blank_lines"], 1)
        self.assertTrue(reparsed["variables"]["API_HOST"]["exported"])


class EnvFileToolSerializeTest(unittest.TestCase):
    """Offline deterministic test cases for serialize mode."""

    def setUp(self) -> None:
        self.tool = EnvFileTool()
        self.data = {
            "PLAIN": "simple",
            "SPACED": "hello world",
            "HASH": "a#b",
            "QUOTE": 'say "hi"',
            "APOS": "it's",
            "BACK": "a\\b",
            "NL": "l1\nl2",
            "TAB": "a\tb",
            "EMPTY": "",
        }

    def test_serialize_canonical_quoting_ground_truth(self) -> None:
        result = self.tool.execute(mode="serialize", data=self.data)
        expected = (
            "PLAIN=simple\n"
            'SPACED="hello world"\n'
            'HASH="a#b"\n'
            'QUOTE="say \\"hi\\""\n'
            "APOS=\"it's\"\n"
            'BACK="a\\\\b"\n'
            'NL="l1\\nl2"\n'
            'TAB="a\\tb"\n'
            "EMPTY=\n"
        )
        self.assertEqual(result["result"], expected)
        self.assertEqual(result["count"], 9)
        self.assertEqual(result["exported_keys"], [])

    def test_serialize_export_all(self) -> None:
        result = self.tool.execute(mode="serialize", data={"A": "1"}, export=True)
        self.assertEqual(result["result"], "export A=1\n")
        self.assertEqual(result["exported_keys"], ["A"])

    def test_serialize_export_subset(self) -> None:
        data = {"A": "1", "B": "2", "C": "3"}
        result = self.tool.execute(mode="serialize", data=data, export=["A", "C"])
        self.assertEqual(result["result"], "export A=1\nB=2\nexport C=3\n")
        self.assertEqual(result["exported_keys"], ["A", "C"])

    def test_serialize_empty_dict(self) -> None:
        result = self.tool.execute(mode="serialize", data={})
        self.assertEqual(result["result"], "")
        self.assertEqual(result["count"], 0)

    def test_serialize_preserves_dict_order(self) -> None:
        result = self.tool.execute(mode="serialize", data={"Z": "1", "A": "2", "M": "3"})
        self.assertEqual(result["result"], "Z=1\nA=2\nM=3\n")

    def test_serialize_parse_round_trip(self) -> None:
        serialized = self.tool.execute(mode="serialize", data=self.data)["result"]
        reparsed = self.tool.execute(mode="parse", text=serialized)
        self.assertEqual(
            {k: v["value"] for k, v in reparsed["variables"].items()}, self.data
        )
        self.assertEqual(list(reparsed["variables"]), list(self.data))

    def test_serialize_parse_round_trip_tricky(self) -> None:
        data = {
            "WS": " lead and trail ",
            "SHARP": "# lead",
            "DOLLAR": "$HOME and ${PATH}",
            "ESCAPES": "\\\n\t\r\"'",
            "UNICODE": "héllo 世界",
        }
        serialized = self.tool.execute(mode="serialize", data=data)["result"]
        reparsed = self.tool.execute(mode="parse", text=serialized)
        self.assertEqual(
            {k: v["value"] for k, v in reparsed["variables"].items()}, data
        )


class EnvFileToolValidateTest(unittest.TestCase):
    """Offline deterministic test cases for validate mode."""

    def setUp(self) -> None:
        self.tool = EnvFileTool()

    def test_validate_undefined_references_ground_truth(self) -> None:
        result = self.tool.execute(mode="validate", text=VALIDATE_TEXT)
        self.assertEqual(
            result["warnings"],
            [
                {"variable": "MISSING_TOKEN", "lines": [3]},
                {"variable": "MISSING_A", "lines": [4]},
            ],
        )
        self.assertEqual(result["defined_count"], 6)
        self.assertIn("2 undefined variable(s)", result["result"])

    def test_validate_ok(self) -> None:
        text = "A=1\nB=${A}\nC=$B\n"
        result = self.tool.execute(mode="validate", text=text)
        self.assertEqual(result["warnings"], [])
        self.assertTrue(result["result"].startswith("ok —"))

    def test_validate_non_references_are_ignored(self) -> None:
        # $$, $5 and "$ " are not variable references.
        result = self.tool.execute(mode="validate", text=VALIDATE_TEXT)
        literal = self.tool.execute(
            mode="validate", text="LIT=$$not and $5 and $ none\n"
        )
        self.assertEqual(literal["warnings"], [])

    def test_validate_reports_malformed_lines_too(self) -> None:
        result = self.tool.execute(mode="validate", text="NOEQ\nA=$B\n")
        self.assertEqual(result["warnings"], [{"variable": "B", "lines": [2]}])
        self.assertEqual(result["malformed_lines"], [{"line": 1, "content": "NOEQ"}])
        self.assertIn("1 malformed line(s)", result["result"])

    def test_validate_self_reference_is_defined(self) -> None:
        result = self.tool.execute(mode="validate", text="PATH=/bin:$PATH\n")
        self.assertEqual(result["warnings"], [])

    def test_validate_scans_overridden_duplicates(self) -> None:
        # Even an overridden duplicate line still references $GONE.
        result = self.tool.execute(mode="validate", text="X=1\nX=$GONE\n")
        self.assertEqual(result["warnings"], [{"variable": "GONE", "lines": [2]}])

    def test_validate_unterminated_quote(self) -> None:
        result = self.tool.execute(mode="validate", text='A="x\n')
        self.assertEqual(result["error"]["type"], "unterminated_quote")


class EnvFileToolErrorMatrixTest(unittest.TestCase):
    """Parameter validation errors (ValueError before any computation)."""

    def setUp(self) -> None:
        self.tool = EnvFileTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode(self) -> None:
        self.assert_invalid(mode="dump", text="A=1\n")

    def test_text_type_and_emptiness(self) -> None:
        self.assert_invalid(mode="parse", text=None)
        self.assert_invalid(mode="parse", text=123)
        self.assert_invalid(mode="parse", text="")
        self.assert_invalid(mode="validate", text="")
        self.assert_invalid(mode="get", text="", key="A")
        self.assert_invalid(mode="parse", text=True)

    def test_text_size_limit(self) -> None:
        self.assert_invalid(mode="parse", text="A=" + "x" * 100_001 + "\n")

    def test_key_charset(self) -> None:
        self.assert_invalid(mode="get", text="A=1\n", key="1BAD")
        self.assert_invalid(mode="get", text="A=1\n", key="HAS SPACE")
        self.assert_invalid(mode="get", text="A=1\n", key="KE-Y")
        self.assert_invalid(mode="get", text="A=1\n", key="")
        self.assert_invalid(mode="get", text="A=1\n", key=42)
        self.assert_invalid(mode="set", text="A=1\n", key="a.b", value="1")

    def test_set_value_and_export_types(self) -> None:
        self.assert_invalid(mode="set", text="A=1\n", key="A", value=None)
        self.assert_invalid(mode="set", text="A=1\n", key="A", value=5)
        self.assert_invalid(mode="set", text="A=1\n", key="A", value="x" * 100_001)
        # set mode accepts only None or a boolean, not a list.
        self.assert_invalid(mode="set", text="A=1\n", key="A", value="x", export=["A"])

    def test_serialize_data_types(self) -> None:
        self.assert_invalid(mode="serialize", data=None)
        self.assert_invalid(mode="serialize", data="A=1")
        self.assert_invalid(mode="serialize", data=["A"])
        self.assert_invalid(mode="serialize", data={"A": 1})
        self.assert_invalid(mode="serialize", data={"A": True})
        self.assert_invalid(mode="serialize", data={"1BAD": "x"})
        self.assert_invalid(mode="serialize", data={"HAS SPACE": "x"})

    def test_serialize_export_list_membership(self) -> None:
        self.assert_invalid(mode="serialize", data={"A": "1"}, export=["NOPE"])
        self.assert_invalid(mode="serialize", data={"A": "1"}, export=7)
        self.assert_invalid(mode="serialize", data={"A": "1"}, export="A")

    def test_serialize_variable_count_limit(self) -> None:
        data = {f"K{i}": "v" for i in range(1_001)}
        self.assert_invalid(mode="serialize", data=data)

    def test_package_and_direct_imports_are_the_same_class(self) -> None:
        self.assertIs(EnvFileTool, DirectEnvFileTool)


if __name__ == "__main__":
    unittest.main()
