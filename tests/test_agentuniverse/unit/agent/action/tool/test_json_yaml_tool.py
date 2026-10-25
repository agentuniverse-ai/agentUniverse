#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_json_yaml_tool.py

"""Offline unit tests for JsonYamlTool.

The tool wraps the standard library ``json`` module and the framework's
PyYAML dependency, and never touches the network, so this suite runs
fully offline. Every assertion is deterministic: conversions are
checked against literal ground-truth strings (nested structures, CJK
text with ``allow_unicode``, scalar roots, exact JSON indentation),
round trips are checked for value stability, and every failure path —
invalid JSON with position, YAML syntax errors with 1-based line and
column marks, multi-document streams, JSON-unrepresentable structures,
strict parameter validation — is exercised as an error matrix.
"""

import json
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import JsonYamlTool
from agentuniverse.agent.action.tool.common_tool.json_yaml_tool import (
    JsonYamlTool as DirectJsonYamlTool,
)

# --------------------------------------------------------------------- #
# Ground-truth payloads (literal expected values, independent of PyYAML)
# --------------------------------------------------------------------- #
NESTED_JSON = (
    '{"server": {"host": "localhost", "port": 8080}, '
    '"tags": ["a", "b"], "retries": null}'
)
NESTED_YAML = (
    "server:\n"
    "  host: localhost\n"
    "  port: 8080\n"
    "tags:\n"
    "- a\n"
    "- b\n"
    "retries: null\n"
)
NESTED_OBJ = {
    "server": {"host": "localhost", "port": 8080},
    "tags": ["a", "b"],
    "retries": None,
}
SIMPLE_YAML = "name: agentUniverse\nstars: 128\nactive: true\n"
SIMPLE_JSON = '{\n  "name": "agentUniverse",\n  "stars": 128,\n  "active": true\n}'
SIMPLE_OBJ = {"name": "agentUniverse", "stars": 128, "active": True}

CJK_JSON = '{"应用": "智能体宇宙", "emoji": "🌍"}'
CJK_YAML = "应用: 智能体宇宙\nemoji: 🌍\n"

ANCHOR_YAML = (
    "defaults: &d\n"
    "  timeout: 30\n"
    "  retries: 3\n"
    "service_a:\n"
    "  <<: *d\n"
    "  retries: 5\n"
    "aliased: *d\n"
)
MERGED_OBJ = {
    "defaults": {"timeout": 30, "retries": 3},
    "service_a": {"timeout": 30, "retries": 5},
    "aliased": {"timeout": 30, "retries": 3},
}


class JsonYamlToolTest(unittest.TestCase):
    """Offline deterministic test cases for the JSON/YAML converter."""

    def setUp(self) -> None:
        self.tool = JsonYamlTool()

    # ------------------------------------------------------------------ #
    # to_yaml mode — JSON text to YAML
    # ------------------------------------------------------------------ #

    def test_to_yaml_nested_ground_truth(self) -> None:
        result = self.tool.execute(mode="to_yaml", text=NESTED_JSON)
        self.assertEqual(
            result, {"mode": "to_yaml", "sort_keys": False, "result": NESTED_YAML}
        )

    def test_to_yaml_cjk_stays_readable(self) -> None:
        result = self.tool.execute(mode="to_yaml", text=CJK_JSON)
        self.assertEqual(result["result"], CJK_YAML)
        self.assertNotIn("\\x", result["result"])
        self.assertNotIn("\\u", result["result"])

    def test_to_yaml_preserves_key_order_by_default(self) -> None:
        result = self.tool.execute(mode="to_yaml", text='{"b": 1, "a": 2}')
        self.assertEqual(result["result"], "b: 1\na: 2\n")
        self.assertEqual(result["sort_keys"], False)

    def test_to_yaml_sort_keys_option(self) -> None:
        result = self.tool.execute(
            mode="to_yaml", text='{"b": 1, "a": 2, "c": 3}', sort_keys=True
        )
        self.assertEqual(result["result"], "a: 2\nb: 1\nc: 3\n")
        self.assertEqual(result["sort_keys"], True)

    def test_to_yaml_block_style_never_flow(self) -> None:
        result = self.tool.execute(mode="to_yaml", text='{"items": [1, 2, 3]}')
        self.assertEqual(result["result"], "items:\n- 1\n- 2\n- 3\n")
        self.assertNotIn("{", result["result"])

    def test_to_yaml_scalar_and_empty_roots(self) -> None:
        cases = [
            ('"hello"', "hello\n...\n"),
            ("42", "42\n...\n"),
            ("3.5", "3.5\n...\n"),
            ("true", "true\n...\n"),
            ("false", "false\n...\n"),
            ("null", "null\n...\n"),
            ("{}", "{}\n"),
            ("[]", "[]\n"),
            ('[NaN, Infinity, -Infinity]', "- .nan\n- .inf\n- -.inf\n"),
        ]
        for json_text, expected in cases:
            with self.subTest(json_text=json_text):
                result = self.tool.execute(mode="to_yaml", text=json_text)
                self.assertEqual(result["result"], expected)

    def test_to_yaml_escapes_special_strings(self) -> None:
        # A string that looks like a number/date must be quoted on dump.
        result = self.tool.execute(mode="to_yaml", text='["2024-01-15", "123"]')
        self.assertEqual(result["result"], "- '2024-01-15'\n- '123'\n")

    # ------------------------------------------------------------------ #
    # to_json mode — YAML text to JSON
    # ------------------------------------------------------------------ #

    def test_to_json_ground_truth(self) -> None:
        result = self.tool.execute(mode="to_json", text=SIMPLE_YAML)
        self.assertEqual(
            result,
            {"mode": "to_json", "indent": 2, "sort_keys": False, "result": SIMPLE_JSON},
        )

    def test_to_json_nested_value_stability(self) -> None:
        result = self.tool.execute(
            mode="to_json", text=yaml.safe_dump(NESTED_OBJ, default_flow_style=False)
        )
        self.assertEqual(json.loads(result["result"]), NESTED_OBJ)

    def test_to_json_indent_option(self) -> None:
        for indent in (0, 1, 4, 10):
            with self.subTest(indent=indent):
                result = self.tool.execute(
                    mode="to_json", text="a: 1", indent=indent
                )
                self.assertEqual(result["indent"], indent)
                expected = json.dumps({"a": 1}, indent=indent, ensure_ascii=False)
                self.assertEqual(result["result"], expected)

    def test_to_json_sort_keys_option(self) -> None:
        result = self.tool.execute(
            mode="to_json", text="b: 1\na: 2", sort_keys=True
        )
        self.assertEqual(result["sort_keys"], True)
        self.assertEqual(json.loads(result["result"]), {"a": 2, "b": 1})
        self.assertLess(
            result["result"].index('"a"'), result["result"].index('"b"')
        )

    def test_to_json_cjk_not_ascii_escaped(self) -> None:
        result = self.tool.execute(mode="to_json", text=CJK_YAML)
        self.assertIn("智能体宇宙", result["result"])
        self.assertIn("🌍", result["result"])
        self.assertNotIn("\\u", result["result"])

    def test_to_json_scalar_and_null_roots(self) -> None:
        cases = [
            ("42", "42"),
            ("'quoted'", '"quoted"'),
            ("true", "true"),
            ("null", "null"),
            ("~", "null"),
            ("# comment only\n", "null"),
        ]
        for yaml_text, expected in cases:
            with self.subTest(yaml_text=yaml_text):
                result = self.tool.execute(mode="to_json", text=yaml_text)
                self.assertEqual(result["result"], expected)

    def test_to_json_integer_keys_become_strings(self) -> None:
        result = self.tool.execute(mode="to_json", text="1: x")
        self.assertEqual(result["result"], '{\n  "1": "x"\n}')

    # ------------------------------------------------------------------ #
    # Anchors, aliases and merge keys (resolved by safe_load)
    # ------------------------------------------------------------------ #

    def test_to_json_resolves_merge_keys_and_aliases(self) -> None:
        result = self.tool.execute(mode="to_json", text=ANCHOR_YAML)
        self.assertEqual(json.loads(result["result"]), MERGED_OBJ)
        # Anchors are expanded — the output contains no YAML anchors.
        self.assertNotIn("&", result["result"])
        self.assertNotIn("*", result["result"])

    def test_to_json_alias_expands_to_copies(self) -> None:
        result = self.tool.execute(
            mode="to_json", text="a: &list\n  - 1\n  - 2\nb: *list\n"
        )
        self.assertEqual(json.loads(result["result"]), {"a": [1, 2], "b": [1, 2]})

    # ------------------------------------------------------------------ #
    # Date / timestamp scalars (explicit default hook)
    # ------------------------------------------------------------------ #

    def test_to_json_date_scalar_becomes_iso_string(self) -> None:
        result = self.tool.execute(mode="to_json", text="release: 2024-01-15")
        # safe_load resolves the bare scalar to datetime.date; JSON has no
        # date literal, so it is serialized explicitly as an ISO 8601 string.
        self.assertEqual(json.loads(result["result"]), {"release": "2024-01-15"})

    def test_to_json_datetime_scalar_becomes_iso_string(self) -> None:
        result = self.tool.execute(
            mode="to_json", text="when: 2024-01-15T10:30:00Z"
        )
        self.assertTrue(
            json.loads(result["result"])["when"].startswith("2024-01-15T10:30:00")
        )

    def test_date_round_trip_documented_caveat(self) -> None:
        # yaml -> json -> yaml is NOT stable for bare date scalars: the
        # date becomes a quoted ISO string on the way back.
        as_json = self.tool.execute(mode="to_json", text="release: 2024-01-15")
        back = self.tool.execute(mode="to_yaml", text=as_json["result"])
        self.assertEqual(back["result"], "release: '2024-01-15'\n")

    # ------------------------------------------------------------------ #
    # Round-trip guarantees
    # ------------------------------------------------------------------ #

    def test_json_to_yaml_to_json_value_stability(self) -> None:
        for json_text in (
            NESTED_JSON,
            CJK_JSON,
            '[1, 2.5, true, false, null, "text"]',
            '{"deep": {"deeper": {"deepest": [ {"x": 1} ] }}}',
            '{"empty_obj": {}, "empty_list": []}',
            '{"special": "a: b\\n\\t- c # not a comment"}',
        ):
            with self.subTest(json_text=json_text):
                as_yaml = self.tool.execute(mode="to_yaml", text=json_text)
                self.assertNotIn("error", as_yaml)
                as_json = self.tool.execute(mode="to_json", text=as_yaml["result"])
                self.assertNotIn("error", as_json)
                self.assertEqual(json.loads(as_json["result"]), json.loads(json_text))

    def test_yaml_to_json_to_yaml_value_stability(self) -> None:
        for yaml_text in (
            SIMPLE_YAML,
            "list:\n- 1\n- two\n- three: 3\n",
            "nested:\n  a:\n    b:\n      c: deep\n",
            "- alpha\n- beta\n",
            "flag: true\nratio: 0.25\nnothing: null\n",
        ):
            with self.subTest(yaml_text=yaml_text):
                as_json = self.tool.execute(mode="to_json", text=yaml_text)
                self.assertNotIn("error", as_json)
                as_yaml = self.tool.execute(mode="to_yaml", text=as_json["result"])
                self.assertNotIn("error", as_yaml)
                self.assertEqual(
                    yaml.safe_load(as_yaml["result"]), yaml.safe_load(yaml_text)
                )

    # ------------------------------------------------------------------ #
    # validate_yaml mode
    # ------------------------------------------------------------------ #

    def test_validate_yaml_mapping_reports_type_and_key_count(self) -> None:
        result = self.tool.execute(
            mode="validate_yaml", text="name: x\nport: 8080\ndebug: true\n"
        )
        self.assertEqual(
            result,
            {
                "mode": "validate_yaml",
                "valid": True,
                "root_type": "mapping",
                "key_count": 3,
            },
        )

    def test_validate_yaml_sequence_reports_item_count(self) -> None:
        result = self.tool.execute(mode="validate_yaml", text="- a\n- b\n- c\n")
        self.assertEqual(result["valid"], True)
        self.assertEqual(result["root_type"], "sequence")
        self.assertEqual(result["key_count"], 0)
        self.assertEqual(result["item_count"], 3)

    def test_validate_yaml_scalar_root_types(self) -> None:
        cases = [
            ("42", "integer"),
            ("3.14", "float"),
            ("'text'", "string"),
            ("true", "boolean"),
            ("null", "null"),
            ("2024-01-15", "date"),
            ("2024-01-15T10:30:00Z", "datetime"),
        ]
        for yaml_text, root_type in cases:
            with self.subTest(yaml_text=yaml_text):
                result = self.tool.execute(mode="validate_yaml", text=yaml_text)
                self.assertEqual(result["valid"], True)
                self.assertEqual(result["root_type"], root_type)
                self.assertEqual(result["key_count"], 0)

    def test_validate_yaml_empty_mapping(self) -> None:
        result = self.tool.execute(mode="validate_yaml", text="{}")
        self.assertEqual(
            result,
            {"mode": "validate_yaml", "valid": True, "root_type": "mapping", "key_count": 0},
        )

    def test_validate_yaml_invalid_reports_mark(self) -> None:
        result = self.tool.execute(mode="validate_yaml", text="a: [1, 2")
        self.assertEqual(result["mode"], "validate_yaml")
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["type"], "yaml_error")
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["column"], 9)

    def test_validate_yaml_multi_document(self) -> None:
        result = self.tool.execute(
            mode="validate_yaml", text="a: 1\n---\nb: 2\n---\nc: 3\n"
        )
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["type"], "multi_document_yaml")
        self.assertIn("3 documents", result["error"]["message"])
        self.assertIn("---", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Error matrix — invalid JSON (to_yaml)
    # ------------------------------------------------------------------ #

    def test_to_yaml_invalid_json_single_quotes_reports_position(self) -> None:
        result = self.tool.execute(mode="to_yaml", text="{'a': 1}")
        self.assertEqual(result["mode"], "to_yaml")
        error = result["error"]
        self.assertEqual(error["type"], "invalid_json")
        self.assertEqual(error["line"], 1)
        self.assertEqual(error["column"], 2)
        self.assertEqual(error["position"], 1)
        self.assertIn("double quotes", error["message"])

    def test_to_yaml_trailing_garbage_reports_position(self) -> None:
        result = self.tool.execute(mode="to_yaml", text='{"a": 1} trailing')
        self.assertEqual(result["error"]["type"], "invalid_json")
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["column"], 10)
        self.assertEqual(result["error"]["position"], 9)
        self.assertIn("Extra data", result["error"]["message"])

    def test_to_yaml_unclosed_container(self) -> None:
        for bad in ('{"a": 1', '[1, 2', '{"a" 1}'):
            with self.subTest(bad=bad):
                result = self.tool.execute(mode="to_yaml", text=bad)
                self.assertEqual(result["error"]["type"], "invalid_json")
                self.assertIn("line", result["error"])

    def test_to_yaml_invalid_json_error_is_structured_not_raised(self) -> None:
        result = self.tool.execute(mode="to_yaml", text="not json at all")
        self.assertNotIn("result", result)
        self.assertIsInstance(result["error"]["message"], str)

    # ------------------------------------------------------------------ #
    # Error matrix — invalid YAML (to_json / validate_yaml)
    # ------------------------------------------------------------------ #

    def test_to_json_tab_character_reports_line_and_column(self) -> None:
        result = self.tool.execute(mode="to_json", text="a:\n\tb: 1")
        error = result["error"]
        self.assertEqual(error["type"], "yaml_error")
        self.assertEqual(error["line"], 2)
        self.assertEqual(error["column"], 1)
        self.assertIn("\\t", error["message"])

    def test_to_json_unclosed_flow_sequence(self) -> None:
        result = self.tool.execute(mode="to_json", text="a: [1, 2")
        self.assertEqual(result["error"]["type"], "yaml_error")
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["column"], 9)

    def test_to_json_unclosed_quote(self) -> None:
        result = self.tool.execute(mode="to_json", text="a: 'unclosed")
        self.assertEqual(result["error"]["type"], "yaml_error")
        self.assertEqual(result["error"]["line"], 1)
        self.assertEqual(result["error"]["column"], 13)

    def test_to_json_bad_indentation(self) -> None:
        result = self.tool.execute(
            mode="to_json", text="a: 1\n  b: 2\nc: 3\n"
        )
        self.assertEqual(result["error"]["type"], "yaml_error")
        self.assertIn("line", result["error"])
        self.assertIn("column", result["error"])

    def test_to_json_duplicate_key_is_yaml_semantics_not_error(self) -> None:
        # safe_load keeps the last value, like json.loads — documented
        # last-wins behavior rather than an error.
        result = self.tool.execute(mode="to_json", text="a: 1\na: 2\n")
        self.assertEqual(json.loads(result["result"]), {"a": 2})

    def test_to_json_unhashable_key_is_yaml_error(self) -> None:
        result = self.tool.execute(mode="to_json", text="? [one, two]\n: value\n")
        self.assertEqual(result["error"]["type"], "yaml_error")
        self.assertIn("unhashable key", result["error"]["message"])

    def test_to_json_multi_document_rejected_clearly(self) -> None:
        for text in ("a: 1\n---\nb: 2\n", "a: 1\n---\n"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="to_json", text=text)
                error = result["error"]
                self.assertEqual(error["type"], "multi_document_yaml")
                self.assertIn("documents", error["message"])
                self.assertIn("---", error["message"])
                self.assertIn("separately", error["message"])

    def test_to_json_date_key_is_unsupported_type(self) -> None:
        # json.dumps cannot serialize a datetime.date mapping key and the
        # default hook does not apply to keys — structured error, not a crash.
        result = self.tool.execute(mode="to_json", text="2024-01-15: x\n")
        self.assertEqual(result["error"]["type"], "unsupported_type")
        self.assertIn("JSON cannot represent", result["error"]["message"])

    def test_to_json_self_referencing_alias_is_unsupported_type(self) -> None:
        result = self.tool.execute(mode="to_json", text="&a\n- *a\n")
        self.assertEqual(result["error"]["type"], "unsupported_type")
        self.assertIn("self-referencing", result["error"]["message"])

    def test_to_json_mixed_key_types_with_sort_keys_unsupported(self) -> None:
        result = self.tool.execute(
            mode="to_json", text="1: a\nb: c\n", sort_keys=True
        )
        self.assertEqual(result["error"]["type"], "unsupported_type")

    # ------------------------------------------------------------------ #
    # Strict input validation (raises ValueError before any work)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="convert", text="a: 1")
        self.assert_invalid(mode=None, text="a: 1")
        self.assert_invalid(mode=123, text="a: 1")
        self.assert_invalid(mode="TO_JSON", text="a: 1")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"{}", ["a"], {"a": 1}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="to_json", text=bad)
                self.assert_invalid(mode="to_yaml", text=bad)
                self.assert_invalid(mode="validate_yaml", text=bad)

    def test_empty_and_whitespace_only_text(self) -> None:
        self.assert_invalid(mode="to_json", text="")
        self.assert_invalid(mode="to_yaml", text="")
        self.assert_invalid(mode="validate_yaml", text="")
        self.assert_invalid(mode="to_json", text="   \n  \t ")
        self.assert_invalid(mode="validate_yaml", text="\n\n")

    def test_text_size_limit(self) -> None:
        oversized = '"' + "a" * 1_048_575 + '"'  # 1,048,577 chars — over the cap
        self.assert_invalid(mode="to_yaml", text=oversized)
        self.assert_invalid(mode="to_json", text="a" * 1_048_577)
        self.assert_invalid(mode="validate_yaml", text="a" * 1_048_577)
        # Exactly at the 1 MiB cap is accepted.
        ok = self.tool.execute(mode="to_json", text="a" * 1_048_576)
        self.assertNotIn("error", ok)

    def test_invalid_sort_keys(self) -> None:
        for bad in ("true", 1, 0, [True]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="to_yaml", text="{}", sort_keys=bad)
                self.assert_invalid(mode="to_json", text="a: 1", sort_keys=bad)
        # None and real booleans are accepted.
        for good in (None, True, False):
            self.assertNotIn(
                "error", self.tool.execute(mode="to_yaml", text="{}", sort_keys=good)
            )

    def test_invalid_indent(self) -> None:
        for bad in (True, "2", 2.5, -1, 11, 100):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="to_json", text="a: 1", indent=bad)
        # None and integers in range are accepted.
        for good in (None, 0, 2, 10):
            self.assertNotIn(
                "error", self.tool.execute(mode="to_json", text="a: 1", indent=good)
            )

    def test_unused_options_are_type_checked_but_ignored(self) -> None:
        # indent is meaningless for to_yaml but must still be well-typed;
        # a valid value is simply ignored and absent from the result.
        result = self.tool.execute(mode="to_yaml", text='{"a": 1}', indent=4)
        self.assertEqual(result["result"], "a: 1\n")
        self.assertNotIn("indent", result)
        self.assert_invalid(mode="to_yaml", text='{"a": 1}', indent="4")
        # sort_keys is meaningless for validate_yaml but type-checked.
        ok = self.tool.execute(mode="validate_yaml", text="a: 1", sort_keys=True)
        self.assertEqual(ok["valid"], True)
        self.assert_invalid(mode="validate_yaml", text="a: 1", sort_keys="yes")

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectJsonYamlTool, JsonYamlTool)
        self.assertEqual(self.tool.name, "json_yaml_tool")
        self.assertIn("YAML", self.tool.description)
        self.assertIn("safe_load", self.tool.description)
        self.assertEqual(JsonYamlTool.MODES, ("to_yaml", "to_json", "validate_yaml"))
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("JsonYamlTool", __all__)

    def test_yaml_config_sidecar_exists_and_matches(self) -> None:
        import os

        import agentuniverse.agent.action.tool.common_tool as pkg

        path = os.path.join(os.path.dirname(pkg.__file__), "json_yaml_tool.yaml")
        self.assertTrue(os.path.exists(path), f"missing sidecar: {path}")
        with open(path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "json_yaml_tool")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.json_yaml_tool",
        )
        self.assertEqual(config["metadata"]["class"], "JsonYamlTool")
        self.assertEqual(config["input_keys"], ["mode"])


if __name__ == "__main__":
    unittest.main()
