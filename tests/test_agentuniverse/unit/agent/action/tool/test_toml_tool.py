#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_toml_tool.py

"""Offline unit tests for TomlTool.

The tool is built purely on the standard library ``tomllib`` module and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: parse results are checked against literal
expected documents (datetime / date / time values verified against the
ISO 8601 strings ``isoformat()`` produces for the fixture below),
``validate`` against literal key / table inventories and error
positions, ``get`` against literal values and type names, and ``paths``
against an exact ordered listing. The 500-path cap is exercised with a
generated 600-key document whose ordering is fixed by construction.
"""

import json
import unittest

from agentuniverse.agent.action.tool.common_tool import TomlTool
from agentuniverse.agent.action.tool.common_tool.toml_tool import (
    TomlTool as DirectTomlTool,
)

# --------------------------------------------------------------------- #
# Fixture: every TOML value shape the tool documents.
# --------------------------------------------------------------------- #
TOML_DOC = '''\
title = "TOML Example"
port = 8000
enabled = true
ratio = 0.5

[server]
host = "127.0.0.1"
port = 8080

[server.auth]
user = "admin"

[database]
ports = [8001, 8002]

[[items]]
name = "first"
tags = ["a", "b"]

[[items]]
name = "second"

[owner]
dob = 1979-05-27T07:32:00Z
birthday = 1979-05-27
shift_start = 09:00:00
"quoted.key" = "v"
multi = """
line1
line2"""
'''

# Literal ground truth (ISO strings verified against tomllib + isoformat).
PARSE_DOC = {
    "title": "TOML Example",
    "port": 8000,
    "enabled": True,
    "ratio": 0.5,
    "server": {"host": "127.0.0.1", "port": 8080, "auth": {"user": "admin"}},
    "database": {"ports": [8001, 8002]},
    "items": [
        {"name": "first", "tags": ["a", "b"]},
        {"name": "second"},
    ],
    "owner": {
        # Offset "Z" datetime -> isoformat() renders "+00:00".
        "dob": "1979-05-27T07:32:00+00:00",
        "birthday": "1979-05-27",
        "shift_start": "09:00:00",
        "quoted.key": "v",
        "multi": "line1\nline2",
    },
}

# Every table (dict node) in document order, pre-order — arrays of
# tables appear as name[i] entries; inline tables would appear too.
TABLES_DOC = [
    "server",
    "server.auth",
    "database",
    "items[0]",
    "items[1]",
    "owner",
]

# Every leaf path with its TOML type, in document order; non-bare keys
# are rendered double-quoted.
PATHS_DOC = [
    ("title", "string"),
    ("port", "integer"),
    ("enabled", "boolean"),
    ("ratio", "float"),
    ("server.host", "string"),
    ("server.port", "integer"),
    ("server.auth.user", "string"),
    ("database.ports[0]", "integer"),
    ("database.ports[1]", "integer"),
    ("items[0].name", "string"),
    ("items[0].tags[0]", "string"),
    ("items[0].tags[1]", "string"),
    ("items[1].name", "string"),
    ("owner.dob", "datetime"),
    ("owner.birthday", "date"),
    ("owner.shift_start", "time"),
    ('owner."quoted.key"', "string"),
    ("owner.multi", "string"),
]

# Documents exercising documented conversions and edge shapes.
NONFINITE_DOC = "a = inf\nb = -inf\nc = nan\n"
EMPTY_CONTAINERS_DOC = "[outer]\n\n[outer.empty]\n[nothing]\n"
ESCAPED_KEY_DOC = '[a]\n"x\\ty" = 1\n"h\\u00e9llo" = 2\n'


class TomlToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TomlTool."""

    def setUp(self) -> None:
        self.tool = TomlTool()

    # ------------------------------------------------------------------ #
    # Registration / metadata
    # ------------------------------------------------------------------ #

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(TomlTool, DirectTomlTool)

    def test_tool_metadata(self) -> None:
        self.assertEqual(self.tool.name, "toml_tool")
        self.assertEqual(
            DirectTomlTool.MODES, ("parse", "validate", "get", "paths")
        )
        self.assertEqual(DirectTomlTool().max_paths, 500)

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def test_parse_full_document_literal(self) -> None:
        result = self.tool.execute(mode="parse", text=TOML_DOC)
        self.assertEqual(
            result, {"mode": "parse", "data": PARSE_DOC}
        )

    def test_parse_output_is_strict_json_safe(self) -> None:
        result = self.tool.execute(mode="parse", text=TOML_DOC)
        # allow_nan=False fails on Infinity/NaN — the whole point of the
        # datetime / non-finite stringification rules.
        json.dumps(result, allow_nan=False)

    def test_parse_datetimes_iso_stringified(self) -> None:
        result = self.tool.execute(mode="parse", text=TOML_DOC)
        owner = result["data"]["owner"]
        self.assertEqual(owner["dob"], "1979-05-27T07:32:00+00:00")
        self.assertEqual(owner["birthday"], "1979-05-27")
        self.assertEqual(owner["shift_start"], "09:00:00")

    def test_parse_nonfinite_floats_stringified(self) -> None:
        result = self.tool.execute(mode="parse", text=NONFINITE_DOC)
        self.assertEqual(
            result["data"], {"a": "inf", "b": "-inf", "c": "nan"}
        )
        json.dumps(result, allow_nan=False)

    def test_parse_inline_and_multiline_strings(self) -> None:
        result = self.tool.execute(mode="parse", text=TOML_DOC)
        self.assertEqual(result["data"]["owner"]["multi"], "line1\nline2")

    def test_parse_invalid_toml_returns_error_with_position(self) -> None:
        result = self.tool.execute(mode="parse", text="a = = 1")
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["error"]["type"], "invalid_toml")
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["col"], 5)
        self.assertIn("Invalid value", result["error"]["message"])

    def test_parse_invalid_toml_end_of_document(self) -> None:
        result = self.tool.execute(mode="parse", text="a =")
        self.assertEqual(result["error"]["type"], "invalid_toml")
        self.assertIsNone(result["error"]["line"])
        self.assertIsNone(result["error"]["col"])
        self.assertIn("end of document", result["error"]["message"])

    def test_parse_error_on_later_line(self) -> None:
        result = self.tool.execute(mode="parse", text="a = 1\nb = 2\nc = = 3")
        self.assertEqual(result["error"]["line"], 3)
        self.assertEqual(result["error"]["col"], 5)

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def test_validate_ok_inventory(self) -> None:
        result = self.tool.execute(mode="validate", text=TOML_DOC)
        self.assertEqual(
            result,
            {
                "mode": "validate",
                "valid": True,
                "root_key_count": 8,
                "tables": TABLES_DOC,
            },
        )

    def test_validate_empty_document_is_valid(self) -> None:
        result = self.tool.execute(mode="validate", text="")
        self.assertEqual(
            result,
            {"mode": "validate", "valid": True, "root_key_count": 0, "tables": []},
        )

    def test_validate_scalars_only_has_no_tables(self) -> None:
        result = self.tool.execute(mode="validate", text="a = 1\nb = 2\n")
        self.assertEqual(result["tables"], [])
        self.assertEqual(result["root_key_count"], 2)

    def test_validate_inline_table_listed(self) -> None:
        result = self.tool.execute(mode="validate", text="point = {x = 1, y = 2}\n")
        self.assertEqual(result["tables"], ["point"])

    def test_validate_error_with_line_and_col(self) -> None:
        result = self.tool.execute(mode="validate", text="[a\nb = 1")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["type"], "invalid_toml")
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["col"], 3)

    def test_validate_error_end_of_document_position_is_none(self) -> None:
        result = self.tool.execute(mode="validate", text="a =")
        self.assertEqual(result["valid"], False)
        self.assertIsNone(result["error"]["line"])
        self.assertIsNone(result["error"]["col"])

    def test_validate_duplicate_key(self) -> None:
        result = self.tool.execute(mode="validate", text="a = 1\na = 2\n")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["type"], "invalid_toml")

    # ------------------------------------------------------------------ #
    # get mode — resolution
    # ------------------------------------------------------------------ #

    def test_get_nested_key(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="server.auth.user")
        self.assertEqual(
            result, {"mode": "get", "path": "server.auth.user", "value": "admin", "type": "string"}
        )

    def test_get_array_index(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="database.ports[1]")
        self.assertEqual(result["value"], 8002)
        self.assertEqual(result["type"], "integer")

    def test_get_array_of_tables_index(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="items[0].tags[1]")
        self.assertEqual(result["value"], "b")
        self.assertEqual(result["type"], "string")

    def test_get_datetime_value_is_iso_string_with_toml_type(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="owner.dob")
        self.assertEqual(result["value"], "1979-05-27T07:32:00+00:00")
        self.assertEqual(result["type"], "datetime")

    def test_get_root_scalar(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="enabled")
        self.assertEqual(result["value"], True)
        self.assertEqual(result["type"], "boolean")

    def test_get_table_returns_json_safe_subtree(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="items")
        self.assertEqual(
            result["value"],
            [
                {"name": "first", "tags": ["a", "b"]},
                {"name": "second"},
            ],
        )
        self.assertEqual(result["type"], "array")
        json.dumps(result, allow_nan=False)

    def test_get_double_quoted_key_with_dot(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path='owner."quoted.key"')
        self.assertEqual(result["value"], "v")

    def test_get_single_quoted_literal_key(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="owner.'quoted.key'")
        self.assertEqual(result["value"], "v")

    def test_get_quoted_key_with_escapes(self) -> None:
        result = self.tool.execute(mode="get", text=ESCAPED_KEY_DOC, path='a."x\\ty"')
        self.assertEqual(result["value"], 1)
        # The document key uses a TOML basic-string \u escape (héllo);
        # the path side addresses it with the literal character.
        result = self.tool.execute(mode="get", text=ESCAPED_KEY_DOC, path='a."héllo"')
        self.assertEqual(result["value"], 2)

    def test_get_bare_key_with_dash_and_digits(self) -> None:
        result = self.tool.execute(mode="get", text="my-key_2 = 7\n", path="my-key_2")
        self.assertEqual(result["value"], 7)

    def test_get_nonfinite_float(self) -> None:
        result = self.tool.execute(mode="get", text=NONFINITE_DOC, path="a")
        self.assertEqual(result["value"], "inf")
        self.assertEqual(result["type"], "float")

    def test_get_unicode_quoted_key(self) -> None:
        result = self.tool.execute(mode="get", text='[a]\n"héllo" = 3\n', path='a."héllo"')
        self.assertEqual(result["value"], 3)

    # ------------------------------------------------------------------ #
    # get mode — content-level errors (structured payloads)
    # ------------------------------------------------------------------ #

    def test_get_missing_key(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="server.missing")
        self.assertEqual(result["mode"], "get")
        self.assertEqual(result["error"]["type"], "path_not_found")
        self.assertIn("missing", result["error"]["message"])

    def test_get_index_out_of_range(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="items[5].name")
        self.assertEqual(result["error"]["type"], "path_not_found")
        self.assertIn("out of range", result["error"]["message"])

    def test_get_index_on_table(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="server[0]")
        self.assertEqual(result["error"]["type"], "path_type_mismatch")
        self.assertIn("not an array", result["error"]["message"])

    def test_get_key_on_array(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="database.ports.x")
        self.assertEqual(result["error"]["type"], "path_type_mismatch")
        self.assertIn("not a table", result["error"]["message"])

    def test_get_descend_into_scalar(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="title.sub")
        self.assertEqual(result["error"]["type"], "path_type_mismatch")
        self.assertIn("string", result["error"]["message"])

    def test_get_missing_key_in_second_table_row(self) -> None:
        result = self.tool.execute(mode="get", text=TOML_DOC, path="items[1].tags")
        self.assertEqual(result["error"]["type"], "path_not_found")

    def test_get_invalid_toml_returns_error_payload(self) -> None:
        result = self.tool.execute(mode="get", text="a = = 1", path="a")
        self.assertEqual(result["error"]["type"], "invalid_toml")
        self.assertEqual(result["error"]["line"], 1)

    # ------------------------------------------------------------------ #
    # paths mode
    # ------------------------------------------------------------------ #

    def test_paths_full_listing_with_types(self) -> None:
        result = self.tool.execute(mode="paths", text=TOML_DOC)
        self.assertEqual(result["mode"], "paths")
        self.assertFalse(result["truncated"])
        self.assertEqual(result["count"], len(PATHS_DOC))
        self.assertEqual(result["total"], len(PATHS_DOC))
        self.assertEqual(result["limit"], 500)
        self.assertEqual(
            result["paths"], [{"path": p, "type": t} for p, t in PATHS_DOC]
        )

    def test_paths_quoted_and_unicode_keys_rendered_quoted(self) -> None:
        result = self.tool.execute(mode="paths", text='[a]\n"b.c" = 1\n"héllo" = 2\nx = 3\n')
        self.assertEqual(
            result["paths"],
            [
                {"path": 'a."b.c"', "type": "integer"},
                {"path": 'a."héllo"', "type": "integer"},
                {"path": "a.x", "type": "integer"},
            ],
        )

    def test_paths_empty_table_and_array_are_leaves(self) -> None:
        result = self.tool.execute(mode="paths", text=EMPTY_CONTAINERS_DOC)
        self.assertEqual(
            result["paths"],
            [
                {"path": "outer.empty", "type": "table"},
                {"path": "nothing", "type": "table"},
            ],
        )

    def test_paths_cap_500(self) -> None:
        text = "".join(f"k{i:03d} = {i}\n" for i in range(600))
        result = self.tool.execute(mode="paths", text=text)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["count"], 500)
        self.assertEqual(result["total"], 600)
        self.assertEqual(result["limit"], 500)
        self.assertEqual(result["paths"][0], {"path": "k000", "type": "integer"})
        self.assertEqual(result["paths"][499], {"path": "k499", "type": "integer"})

    def test_paths_invalid_toml_returns_error_payload(self) -> None:
        result = self.tool.execute(mode="paths", text="a = = 1")
        self.assertEqual(result["error"]["type"], "invalid_toml")

    def test_paths_datetime_leaf_types(self) -> None:
        result = self.tool.execute(
            mode="paths", text="d = 1979-05-27\nt = 07:32:00\ndt = 1979-05-27T07:32:00Z\n"
        )
        self.assertEqual(
            result["paths"],
            [
                {"path": "d", "type": "date"},
                {"path": "t", "type": "time"},
                {"path": "dt", "type": "datetime"},
            ],
        )

    # ------------------------------------------------------------------ #
    # Parameter validation (ValueError) — the error matrix
    # ------------------------------------------------------------------ #

    def test_invalid_mode_rejected(self) -> None:
        for mode in ("dump", "", None, 123, "PARSE"):
            with self.assertRaisesRegex(ValueError, "mode must be one of"):
                self.tool.execute(mode=mode, text="a = 1")

    def test_text_type_rejected(self) -> None:
        for text in (None, 123, True, ["a"], b"a = 1"):
            with self.assertRaisesRegex(ValueError, "text must be a string"):
                self.tool.execute(mode="parse", text=text)

    def test_text_empty_rejected_except_validate(self) -> None:
        for mode in ("parse", "get", "paths"):
            with self.assertRaisesRegex(ValueError, "non-empty"):
                self.tool.execute(mode=mode, text="")
        # validate accepts the empty document (valid TOML, zero keys).
        result = self.tool.execute(mode="validate", text="")
        self.assertTrue(result["valid"])

    def test_text_over_1mib_rejected(self) -> None:
        text = "a = 1  # " + "z" * 1_048_576
        self.assertGreater(len(text), 1_048_576)
        for mode in ("parse", "validate", "get", "paths"):
            with self.assertRaisesRegex(ValueError, "1,048,576-character limit"):
                self.tool.execute(mode=mode, text=text, path="a")

    def test_path_type_rejected(self) -> None:
        for path in (None, 123, True, ["a"]):
            with self.assertRaisesRegex(ValueError, "path must be a non-empty"):
                self.tool.execute(mode="get", text="a = 1", path=path)

    def test_path_empty_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-empty dotted path"):
            self.tool.execute(mode="get", text="a = 1", path="")

    def test_path_over_2000_chars_rejected(self) -> None:
        path = "a" * 2001
        with self.assertRaisesRegex(ValueError, "2,000-character limit"):
            self.tool.execute(mode="get", text="a = 1", path=path)

    def test_path_syntax_error_matrix(self) -> None:
        # (path, expected message fragment) — positions are 0-based.
        cases = [
            (".a", "expected a bare key"),
            ("a.", "dangling '.'"),
            ("a..b", "expected a bare key"),
            ("a b", "unexpected character ' '"),
            ("a[", "non-negative integer array index"),
            ("a[x]", "non-negative integer array index"),
            ("a[01]", "leading zeros"),
            ("a[10", "expected ']'"),
            ('a."b', 'unterminated "-quoted key'),
            ("a.'b", "unterminated '-quoted key"),
            ("a.''", "empty quoted key"),
            ('a."b\\q"', "unsupported escape"),
            ('a."b\\', "dangling escape"),
            ("[0].a", "expected a bare key"),
            ("a[b]", "non-negative integer array index"),
        ]
        for path, fragment in cases:
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, "at position"):
                    self.tool.execute(mode="get", text="a = 1", path=path)
                try:
                    self.tool.execute(mode="get", text="a = 1", path=path)
                except ValueError as exc:
                    self.assertIn(fragment, str(exc))

    def test_path_syntax_error_reports_position(self) -> None:
        with self.assertRaisesRegex(
            ValueError, r"invalid path 'a b' at position 1"
        ):
            self.tool.execute(mode="get", text="a = 1", path="a b")

    def test_path_is_ignored_by_other_modes(self) -> None:
        # Mirrors the sibling tools: parameters unused by a mode are
        # ignored rather than rejected.
        result = self.tool.execute(mode="parse", text="a = 1", path="ignored")
        self.assertNotIn("error", result)


if __name__ == "__main__":
    unittest.main()
