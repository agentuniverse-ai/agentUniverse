#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_json_schema_tool.py

"""Offline unit tests for JsonSchemaTool.

The tool is built purely on the standard library and never touches
the network or the filesystem, so this suite runs fully offline.
Every assertion is deterministic: validate results are compared
against literal ground-truth payloads (each supported keyword with a
passing and a failing document, exact dot-paths, exact applied_rules
counts, the documented integer-vs-number policy, deep-equality
semantics, $ref nesting and the cycle guard, the formats matrix,
unsupported-keyword collection and strict schema-value errors),
infer_schema against a literal expected skeleton (including secret
masking) and a 200-document seeded round-trip
(validate(infer_schema(d), d).valid is True for every d), and
simplify_errors against a literal grouped summary.

Security invariant asserted wherever a fixture carries a secret-ish
property name (containing KEY/SECRET/PASSWORD/TOKEN): the raw secret
value must not appear anywhere in the serialized result.
"""

import json
import random
import unittest

from agentuniverse.agent.action.tool.common_tool import JsonSchemaTool
from agentuniverse.agent.action.tool.common_tool.json_schema_tool import (
    JsonSchemaTool as DirectJsonSchemaTool,
)

SECRET_MARKERS = ("KEY", "SECRET", "PASSWORD", "TOKEN")


def _secretish(name):
    upper = name.upper()
    return any(marker in upper for marker in SECRET_MARKERS)


class JsonSchemaToolTestCase(unittest.TestCase):
    """Shared helpers."""

    def setUp(self) -> None:
        self.tool = JsonSchemaTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)


# --------------------------------------------------------------------- #
# type keyword — ground truth per JSON type
# --------------------------------------------------------------------- #


class TypeKeywordTest(JsonSchemaToolTestCase):
    """type: every JSON type, lists of types, the integer/number edge."""

    def test_pass_each_type(self) -> None:
        for document, declared in (
            ('"hello"', "string"),
            (1.5, "number"),
            (1, "number"),
            (7, "integer"),
            (1.0, "integer"),  # documented: zero fractional part
            (True, "boolean"),
            (None, "null"),
            ([1, 2], "array"),
            ({"a": 1}, "object"),
        ):
            result = self.tool.execute(
                mode="validate",
                document=document,
                schema={"type": declared},
            )
            self.assertTrue(result["valid"], (document, declared))

    def test_fail_each_type_with_exact_actual(self) -> None:
        for document, declared, actual in (
            (5, "string", "integer"),
            ('"x"', "integer", "string"),
            (1.5, "integer", "number"),
            (True, "integer", "boolean"),
            (True, "number", "boolean"),
            (None, "string", "null"),
            ([], "object", "array"),
            ({}, "array", "object"),
        ):
            result = self.tool.execute(
                mode="validate",
                document=document,
                schema={"type": declared},
            )
            self.assertFalse(result["valid"], (document, declared))
            self.assertEqual(len(result["errors"]), 1)
            error = result["errors"][0]
            self.assertEqual(error["path"], "")
            self.assertEqual(error["schema_rule"], "type")
            self.assertEqual(error["actual"], actual)

    def test_integer_edge_documented_choice(self) -> None:
        # draft 2020-12: 1.0 IS an integer (zero fractional part),
        # 1.5 is not; integers also satisfy number.
        ok = self.tool.execute(
            mode="validate", document=1.0, schema={"type": "integer"}
        )
        self.assertTrue(ok["valid"])
        bad = self.tool.execute(
            mode="validate", document=1.5, schema={"type": "integer"}
        )
        self.assertFalse(bad["valid"])
        self.assertEqual(bad["errors"][0]["actual"], "number")

    def test_multiple_allowed_types(self) -> None:
        schema = {"type": ["string", "null"]}
        for document in ('"x"', None):
            self.assertTrue(
                self.tool.execute(
                    mode="validate", document=document, schema=schema
                )["valid"]
            )
        result = self.tool.execute(
            mode="validate", document=5, schema=schema
        )
        self.assertFalse(result["valid"])
        self.assertEqual(
            result["errors"][0]["message"],
            "expected type one of string, null, got integer",
        )

    def test_applied_rules_simple_count(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"name": "au", "extra": 1},
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )
        # root type + name type + required = 3 assertions, all passing
        self.assertTrue(result["valid"])
        self.assertEqual(result["applied_rules"], 3)

    def test_boolean_subschemas(self) -> None:
        ok = self.tool.execute(
            mode="validate", document={"a": 1}, schema={"properties": {"a": True}}
        )
        self.assertTrue(ok["valid"])
        self.assertEqual(ok["applied_rules"], 0)
        bad = self.tool.execute(
            mode="validate", document=["x"], schema={"items": False}
        )
        self.assertFalse(bad["valid"])
        self.assertEqual(bad["applied_rules"], 1)
        self.assertEqual(bad["errors"][0]["path"], "[0]")
        self.assertEqual(bad["errors"][0]["schema_rule"], "false")


# --------------------------------------------------------------------- #
# object / array keyword ground truths
# --------------------------------------------------------------------- #


class ObjectArrayKeywordTest(JsonSchemaToolTestCase):
    """properties/required/additionalProperties and the item rules."""

    def test_required_missing_exact_path(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"name": "au"},
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}, "port": {}},
                "required": ["name", "port"],
            },
        )
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["path"], "")
        self.assertEqual(result["errors"][0]["schema_rule"], "required")
        self.assertEqual(result["errors"][0]["actual"], "port")

    def test_nested_dot_paths(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"user": {"tags": [{"id": "x"}]}},
            schema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"}
                                    },
                                },
                            }
                        },
                    }
                },
            },
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["path"], "user.tags[0].id")
        self.assertEqual(result["errors"][0]["schema_rule"], "type")

    def test_additional_properties(self) -> None:
        schema = {
            "type": "object",
            "properties": {"a": {"type": "integer"}},
            "additionalProperties": False,
        }
        ok = self.tool.execute(
            mode="validate", document={"a": 1}, schema=schema
        )
        self.assertTrue(ok["valid"])
        bad = self.tool.execute(
            mode="validate", document={"a": 1, "b": 2}, schema=schema
        )
        self.assertFalse(bad["valid"])
        self.assertEqual(bad["errors"][0]["path"], "b")
        self.assertEqual(
            bad["errors"][0]["schema_rule"], "additionalProperties"
        )
        # without properties every key is undeclared
        bare = self.tool.execute(
            mode="validate",
            document={"a": 1},
            schema={"additionalProperties": False},
        )
        self.assertFalse(bare["valid"])

    def test_item_counts(self) -> None:
        schema = {"type": "array", "minItems": 2, "maxItems": 3}
        self.assertTrue(
            self.tool.execute(
                mode="validate", document=[1, 2], schema=schema
            )["valid"]
        )
        short = self.tool.execute(
            mode="validate", document=[1], schema=schema
        )
        self.assertEqual(short["errors"][0]["schema_rule"], "minItems")
        self.assertEqual(short["errors"][0]["actual"], 1)
        long = self.tool.execute(
            mode="validate", document=[1, 2, 3, 4], schema=schema
        )
        self.assertEqual(long["errors"][0]["schema_rule"], "maxItems")
        self.assertEqual(long["errors"][0]["actual"], 4)

    def test_unique_items_deep_equality(self) -> None:
        schema = {"type": "array", "uniqueItems": True}
        for document, unique in (
            ([1, 2, 3], True),
            ([1, True, "1", None], True),  # true is never 1
            ([{"a": 1}, {"a": 2}], True),
            ([[1, 2], [1, 3]], True),
            ([1, 1.0], False),  # numbers compare numerically
            ([1, True, 1], False),
            ([{"a": 1}, {"a": 1}], False),  # deep, key order-free
            ([[1, 2], [1, 2]], False),
            ([{"a": 1, "b": 2}, {"b": 2, "a": 1}], False),
        ):
            result = self.tool.execute(
                mode="validate", document=document, schema=schema
            )
            self.assertEqual(result["valid"], unique, document)
            if not unique:
                self.assertEqual(
                    result["errors"][0]["schema_rule"], "uniqueItems"
                )


# --------------------------------------------------------------------- #
# scalar keyword ground truths
# --------------------------------------------------------------------- #


class ScalarKeywordTest(JsonSchemaToolTestCase):
    """numeric bounds, lengths, pattern, enum, const."""

    def test_numeric_bounds_edges(self) -> None:
        self.assertTrue(
            self.tool.execute(
                mode="validate",
                document=5,
                schema={"minimum": 5, "maximum": 5},
            )["valid"]
        )
        excl = self.tool.execute(
            mode="validate",
            document=5,
            schema={"exclusiveMinimum": 5, "exclusiveMaximum": 5},
        )
        self.assertFalse(excl["valid"])
        self.assertEqual(
            [e["schema_rule"] for e in excl["errors"]],
            ["exclusiveMinimum", "exclusiveMaximum"],
        )
        self.assertEqual(excl["applied_rules"], 2)
        # bounds never apply to non-numbers
        naive = self.tool.execute(
            mode="validate", document='"5"', schema={"minimum": 5}
        )
        self.assertTrue(naive["valid"])
        self.assertEqual(naive["applied_rules"], 0)

    def test_string_lengths(self) -> None:
        schema = {"type": "string", "minLength": 2, "maxLength": 3}
        for document, valid in (('"ab"', True), ('"abc"', True), ('"a"', False), ('"abcd"', False)):
            result = self.tool.execute(
                mode="validate", document=document, schema=schema
            )
            self.assertEqual(result["valid"], valid, document)
        result = self.tool.execute(
            mode="validate", document='"abcd"', schema=schema
        )
        self.assertEqual(result["errors"][0]["actual"], 4)

    def test_pattern_is_re_search(self) -> None:
        schema = {"type": "string", "pattern": "b"}  # unanchored
        self.assertTrue(
            self.tool.execute(
                mode="validate", document='"abc"', schema=schema
            )["valid"]
        )
        bad = self.tool.execute(
            mode="validate", document='"xyz"', schema=schema
        )
        self.assertFalse(bad["valid"])
        self.assertEqual(bad["errors"][0]["schema_rule"], "pattern")
        self.assertIn("re.search", bad["errors"][0]["message"])

    def test_enum_const_deep_equality(self) -> None:
        schema = {"enum": [{"a": 1}, 2, "x", None, True]}
        for document in ({"a": 1}, {"a": 1.0}, 2, 2.0, '"x"', None, True):
            self.assertTrue(
                self.tool.execute(
                    mode="validate", document=document, schema=schema
                )["valid"],
                document,
            )
        for document in ({"a": 2}, 3, 1, False):
            self.assertFalse(
                self.tool.execute(
                    mode="validate", document=document, schema=schema
                )["valid"],
                document,
            )
        const = self.tool.execute(
            mode="validate", document={"x": 1}, schema={"const": {"x": 1}}
        )
        self.assertTrue(const["valid"])
        bad_const = self.tool.execute(
            mode="validate", document={"x": 2}, schema={"const": {"x": 1}}
        )
        self.assertEqual(bad_const["errors"][0]["schema_rule"], "const")


# --------------------------------------------------------------------- #
# formats matrix
# --------------------------------------------------------------------- #


class FormatMatrixTest(JsonSchemaToolTestCase):
    """Every family format with passing and failing values."""

    MATRIX = {
        "email": (
            ("user@example.com", "a@b", "first.last@sub.example.co.uk"),
            ("user@@example.com", ".user@example.com",
             "user@-example.com", "user@ex_ample.com",
             "user.name@example..com", "us er@example.com", "user@"),
        ),
        "date": (
            ("2026-02-28", "2024-02-29", "2000-02-29", "1999-12-31"),
            ("2026-02-30", "1900-02-29", "2026-13-01", "2026-00-10",
             "2026-1-1", "26-02-28", "2026/02/28", "2026-02-28x"),
        ),
        "date-time": (
            ("2026-10-21T12:30:45Z", "2026-10-21T12:30:45.123+08:00",
             "0001-01-01T00:00:00Z", "2026-10-21T23:59:59-05:00"),
            ("2026-10-21T12:30:45", "2026-10-21 12:30:45Z",
             "2026-10-21T24:00:00Z", "2026-10-21T12:60:00Z",
             "2026-02-30T10:00:00Z", "2026-10-21T12:30:45+0800"),
        ),
        "uuid": (
            ("123e4567-e89b-12d3-a456-426614174000",
             "123E4567-E89B-12D3-A456-426614174000",
             "00000000-0000-0000-0000-000000000000"),
            ("123e4567e89b12d3a456426614174000",
             "123e4567-e89b-12d3-a456-42661417400g",
             "123e4567-e89b-12d3-a456-4266141740000"),
        ),
        "url": (
            ("https://example.com/x", "http://h",
             "postgres://db:5432/x", "ftp://files.example.com"),
            ("example.com", "http://", "h:8080", "//example.com", "a b"),
        ),
        "ipv4": (
            ("192.168.1.1", "0.0.0.0", "255.255.255.255", "10.0.0.1"),
            ("256.1.1.1", "192.168.01.1", "192.168.1", "1.2.3.4.5",
             "::1", "1.2.3."),
        ),
    }

    def test_matrix(self) -> None:
        for fmt, (good, bad) in self.MATRIX.items():
            schema = {"type": "string", "format": fmt}
            for value in good:
                result = self.tool.execute(
                    mode="validate", document=json.dumps(value), schema=schema
                )
                self.assertTrue(result["valid"], (fmt, value))
                self.assertEqual(result["applied_rules"], 2)
            for value in bad:
                result = self.tool.execute(
                    mode="validate", document=json.dumps(value), schema=schema
                )
                self.assertFalse(result["valid"], (fmt, value))
                self.assertEqual(
                    result["errors"][0]["schema_rule"], "format", (fmt, value)
                )
                self.assertIn(fmt, result["errors"][0]["message"])

    def test_format_only_applies_to_strings(self) -> None:
        result = self.tool.execute(
            mode="validate", document=5, schema={"format": "email"}
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["applied_rules"], 0)

    def test_unknown_format_noted_not_asserted(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document='"not a phone"',
            schema={"format": "phone"},
        )
        self.assertTrue(result["valid"])
        self.assertEqual(
            result["unsupported_keywords"],
            [
                {
                    "keyword": "format:phone",
                    "path": "#",
                    "note": (
                        "format 'phone' is not one of ['email', 'date', "
                        "'date-time', 'uuid', 'url', 'ipv4']; it was "
                        "skipped"
                    ),
                }
            ],
        )


# --------------------------------------------------------------------- #
# $defs / $ref
# --------------------------------------------------------------------- #


class RefTest(JsonSchemaToolTestCase):
    """nested $defs/$ref, missing targets, non-local refs, cycles."""

    def _tree_schema(self):
        node = {
            "type": "object",
            "properties": {
                "value": {"type": "integer"},
                "children": {"type": "array", "items": {"$ref": "#/$defs/node"}},
            },
            "required": ["value"],
        }
        return {"$ref": "#/$defs/node", "$defs": {"node": node}}

    def test_recursive_tree_schema(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={
                "value": 1,
                "children": [
                    {"value": 2, "children": []},
                    {"value": 3, "children": [{"value": "x"}]},
                ],
            },
            schema=self._tree_schema(),
        )
        self.assertFalse(result["valid"])
        self.assertEqual(
            result["errors"][0]["path"], "children[1].children[0].value"
        )
        self.assertEqual(result["errors"][0]["schema_rule"], "type")
        self.assertNotIn("cycle_stops", result)  # distinct instances

    def test_ref_chain_nested_defs(self) -> None:
        schema = {
            "type": "object",
            "properties": {"home": {"$ref": "#/$defs/address"}},
            "$defs": {
                "address": {
                    "type": "object",
                    "properties": {
                        "city": {"$ref": "#/$defs/city"},
                        "zip": {"type": "string"},
                    },
                    "required": ["city"],
                },
                "city": {"type": "string", "minLength": 2},
            },
        }
        ok = self.tool.execute(
            mode="validate",
            document={"home": {"city": "beijing", "zip": "100000"}},
            schema=schema,
        )
        self.assertTrue(ok["valid"])
        bad = self.tool.execute(
            mode="validate", document={"home": {"city": "b"}}, schema=schema
        )
        self.assertFalse(bad["valid"])
        self.assertEqual(bad["errors"][0]["path"], "home.city")
        self.assertEqual(bad["errors"][0]["schema_rule"], "minLength")

    def test_ref_siblings_apply(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document=5,
            schema={
                "$ref": "#/$defs/pair",
                "enum": [1, 3],
                "$defs": {"pair": {"type": "integer"}},
            },
        )
        # both the ref target's type and the sibling enum assert
        self.assertFalse(result["valid"])
        self.assertEqual(
            [e["schema_rule"] for e in result["errors"]], ["enum"]
        )

    def test_missing_defs_target_raises(self) -> None:
        self.assert_invalid(
            mode="validate",
            document={},
            schema={"$ref": "#/$defs/ghost"},
        )

    def test_non_local_ref_skipped(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document=5,
            schema={
                "$ref": "https://example.com/schema.json",
                "type": "integer",
            },
        )
        self.assertTrue(result["valid"])  # type still applied
        self.assertEqual(
            result["unsupported_keywords"][0]["keyword"], "$ref(non-local)"
        )

    def test_deep_pointer_ref_skipped(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={},
            schema={
                "properties": {"a": {"$ref": "#/properties/a"}},
            },
        )
        self.assertTrue(result["valid"])
        self.assertEqual(
            result["unsupported_keywords"][0]["keyword"], "$ref(non-local)"
        )
        self.assertEqual(result["unsupported_keywords"][0]["path"],
                         "#/properties/a")

    def test_cycle_guard_terminates(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"anything": 1},
            schema={
                "$ref": "#/$defs/loop",
                "$defs": {"loop": {"$ref": "#/$defs/loop"}},
            },
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["cycle_stops"], [{"ref": "loop", "path": ""}])
        self.assertEqual(result["applied_rules"], 0)


# --------------------------------------------------------------------- #
# unsupported keywords vs invalid values
# --------------------------------------------------------------------- #


class UnsupportedKeywordTest(JsonSchemaToolTestCase):
    """Out-of-subset keywords are collected; bad values raise."""

    def test_unsupported_collected_never_crash(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"name": "au", "zone": "x"},
            schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "anyOf": [{"minLength": 2}],
                        "allOf": [{"pattern": "^[a-z]+$"}],
                        "oneOf": [{"enum": ["au"]}],
                        "not": {"enum": ["bad"]},
                        "multipleOf": 1,
                    },
                    "zone": {
                        "type": "string",
                        "patternProperties": {"^z": {"minLength": 1}},
                        "dependencies": {"zone": ["name"]},
                    },
                },
                "minProperties": 1,
                "maxProperties": 5,
                "$comment": "collected at the root? no - it is an annotation",
            },
        )
        # every supported rule passes; unsupported ones are noted
        self.assertTrue(result["valid"])
        collected = {
            (e["keyword"], e["path"]) for e in result["unsupported_keywords"]
        }
        self.assertEqual(
            collected,
            {
                ("anyOf", "#/properties/name"),
                ("allOf", "#/properties/name"),
                ("oneOf", "#/properties/name"),
                ("not", "#/properties/name"),
                ("multipleOf", "#/properties/name"),
                ("patternProperties", "#/properties/zone"),
                ("dependencies", "#/properties/zone"),
                ("minProperties", "#"),
                ("maxProperties", "#"),
            },
        )
        for entry in result["unsupported_keywords"]:
            self.assertIn("skipped", entry["note"])

    def test_unsupported_does_not_mask_supported_failures(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"age": "old"},
            schema={
                "type": "object",
                "properties": {
                    "age": {"type": "integer", "anyOf": [{"minimum": 0}]}
                },
            },
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["schema_rule"], "type")
        self.assertEqual(
            result["unsupported_keywords"][0]["keyword"], "anyOf"
        )

    def test_items_array_form_and_schema_additional(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"a": 1, "b": "x"},
            schema={
                "items": [{"type": "integer"}],  # root-level: wrong type
                "additionalProperties": {"type": "integer"},
            },
        )
        collected = {
            (e["keyword"], e["path"]) for e in result["unsupported_keywords"]
        }
        self.assertEqual(
            collected,
            {
                ("items(array form)", "#"),
                ("additionalProperties(schema)", "#"),
            },
        )

    def test_invalid_keyword_values_raise(self) -> None:
        for keyword_value in (
            {"type": "strng"},
            {"type": []},
            {"type": ["string", "string"]},
            {"type": 5},
            {"minLength": -1},
            {"minLength": 1.5},
            {"maxLength": True},
            {"minItems": "2"},
            {"minimum": "5"},
            {"maximum": None},
            {"exclusiveMinimum": float("nan")},
            {"pattern": "("},
            {"pattern": 7},
            {"required": "name"},
            {"required": []},
            {"required": ["a", 1]},
            {"required": ["a", "a"]},
            {"properties": ["a"]},
            {"additionalProperties": "no"},
            {"uniqueItems": "yes"},
            {"enum": []},
            {"enum": "x"},
            {"enum": [1, {1, 2}]},
            {"items": 5},
            {"format": 7},
            {"$defs": []},
            {"$defs": {"x": 5}},
            {"$ref": 5},
            {"properties": {"a": 5}},
        ):
            self.assert_invalid(
                mode="validate", document={}, schema=keyword_value
            ), keyword_value

    def test_error_messages_name_the_schema_location(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="validate",
                document={},
                schema={
                    "type": "object",
                    "properties": {"port": {"type": "integer", "minimum": "1"}},
                },
            )
        self.assertIn("#/properties/port", str(ctx.exception))

    def test_schema_must_be_object(self) -> None:
        for bad in ([], "not json ok", 5, True, None):
            self.assert_invalid(mode="validate", document={}, schema=bad)

    def test_schema_as_json_text(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"name": "au"},
            schema='{"properties": {"name": {"type": "string"}},'
            ' "required": ["name"]}',
        )
        self.assertTrue(result["valid"])
        self.assert_invalid(
            mode="validate", document={}, schema='[1, 2]'
        )

    def test_annotations_ignored_gracefully(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"name": "au"},
            schema={
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": 123,
                "description": None,
                "examples": [["anything", {"x": 1}]],
                "deprecated": "yes",
                "readOnly": 1,
                "type": "object",
                "properties": {
                    "name": {
                        "title": "Name",
                        "description": "the name",
                        "type": "string",
                    }
                },
                "required": ["name"],
            },
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["unsupported_keywords"], [])
        self.assertEqual(result["defaults_declared"], [])

    def test_default_is_report_only(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={},
            schema={
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "default": 8080},
                    "api_key": {"type": "string", "default": "sk-live-123"},
                },
                "required": ["port"],
            },
        )
        # the default was NOT applied: port is still missing
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["schema_rule"], "required")
        self.assertEqual(
            result["defaults_declared"],
            [
                {
                    "schema_path": "#/properties/api_key",
                    "default": "***",  # masked (secret-ish name)
                },
                {"schema_path": "#/properties/port", "default": 8080},
            ],
        )


# --------------------------------------------------------------------- #
# secret masking
# --------------------------------------------------------------------- #


class MaskingTest(JsonSchemaToolTestCase):
    """Values under secret-ish names never appear in payloads."""

    def test_error_actual_masked(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"api_key": "sk-live-abcdef123456", "port": 70000},
            schema={
                "type": "object",
                "properties": {
                    "api_key": {"type": "string", "minLength": 50},
                    "port": {"type": "integer", "maximum": 65535},
                },
            },
        )
        dumped = json.dumps(result)
        self.assertNotIn("sk-live-abcdef123456", dumped)
        key_error = result["errors"][0]
        self.assertEqual(key_error["path"], "api_key")
        self.assertEqual(key_error["schema_rule"], "minLength")
        self.assertEqual(key_error["actual"], 20)  # the length, not the value
        self.assertEqual(result["errors"][1]["actual"], 70000)

    def test_masking_propagates_into_arrays(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={"passwords": ["hunter2-secret", "abc"]},
            schema={
                "type": "object",
                "properties": {
                    "passwords": {
                        "type": "array",
                        "items": {"type": "string", "pattern": "^[a-z]{10,}$"},
                    }
                },
            },
        )
        dumped = json.dumps(result)
        self.assertNotIn("hunter2-secret", dumped)
        self.assertNotIn("abc", dumped)
        self.assertEqual(result["errors"][0]["path"], "passwords[0]")
        self.assertEqual(result["errors"][0]["actual"], "***")
        self.assertEqual(result["errors"][1]["actual"], "***")

    def test_long_actual_truncated(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document='"' + "x" * 500 + '"',
            schema={"type": "string", "pattern": "y"},
        )
        actual = result["errors"][0]["actual"]
        self.assertEqual(actual, "x" * 120 + "...")


# --------------------------------------------------------------------- #
# document loading
# --------------------------------------------------------------------- #


class DocumentLoadingTest(JsonSchemaToolTestCase):
    """JSON text parsing, structured errors, native values."""

    def test_json_text_document(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document='{"name": "au"}',
            schema={"properties": {"name": {"type": "string"}}},
        )
        self.assertTrue(result["valid"])

    def test_invalid_json_is_structured_error(self) -> None:
        for mode in ("validate", "infer_schema"):
            payload = self.tool.execute(
                mode=mode, document='{"name": ', schema={"type": "object"}
            )
            self.assertEqual(payload["mode"], mode)
            self.assertEqual(payload["error"]["type"], "invalid_json")

    def test_null_document_is_valid_json(self) -> None:
        result = self.tool.execute(
            mode="validate", document=None, schema={"type": "null"}
        )
        self.assertTrue(result["valid"])

    def test_native_document_must_be_json_shaped(self) -> None:
        self.assert_invalid(
            mode="validate", document={1: "a"}, schema={"type": "object"}
        )
        self.assert_invalid(
            mode="validate",
            document=float("nan"),
            schema={"type": "number"},
        )
        self.assert_invalid(
            mode="infer_schema", document={1, 2}
        )
        # tuples are arrays
        result = self.tool.execute(
            mode="validate", document=(1, 2), schema={"type": "array"}
        )
        self.assertTrue(result["valid"])

    def test_too_deep_document_structured_error(self) -> None:
        document = current = {}
        for _ in range(70):
            current["child"] = {}
            current = current["child"]
        payload = self.tool.execute(
            mode="validate", document=document, schema={"type": "object"}
        )
        self.assertEqual(payload["error"]["type"], "document_too_deep")


# --------------------------------------------------------------------- #
# the full error matrix (exact order, paths and counts)
# --------------------------------------------------------------------- #


class ErrorMatrixTest(JsonSchemaToolTestCase):
    """One document violating many keywords at once — literal ground truth."""

    SCHEMA = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 2, "pattern": "^[a-z]+$"},
            "age": {"type": "integer", "minimum": 0, "exclusiveMaximum": 150},
            "email": {"type": "string", "format": "email"},
            "role": {"enum": ["admin", "user"]},
            "tags": {
                "type": "array",
                "minItems": 1,
                "uniqueItems": True,
                "items": {"type": "string", "maxLength": 4},
            },
        },
        "required": ["name", "email"],
        "additionalProperties": False,
    }

    DOCUMENT = {
        "name": "X",  # minLength + pattern
        "age": 150,  # exclusiveMaximum
        "email": "not-an-email",  # format
        "role": "guest",  # enum
        "tags": ["ok", "toolong", "ok"],  # uniqueItems + items[1] maxLength
        "extra": 1,  # additionalProperties
    }

    def test_exact_error_list_and_count(self) -> None:
        result = self.tool.execute(
            mode="validate", document=self.DOCUMENT, schema=self.SCHEMA
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["applied_rules"], 21)
        self.assertEqual(
            [(e["path"], e["schema_rule"]) for e in result["errors"]],
            [
                ("name", "minLength"),
                ("name", "pattern"),
                ("age", "exclusiveMaximum"),
                ("email", "format"),
                ("role", "enum"),
                ("tags", "uniqueItems"),
                ("tags[1]", "maxLength"),
                ("extra", "additionalProperties"),
            ],
        )
        self.assertEqual(result["errors"][0]["actual"], 1)  # length, not value
        self.assertEqual(result["errors"][2]["actual"], 150)
        self.assertEqual(result["errors"][3]["actual"], "not-an-email")

    def test_all_passing_counts(self) -> None:
        result = self.tool.execute(
            mode="validate",
            document={
                "name": "au",
                "age": 10,
                "email": "a@example.com",
                "role": "user",
                "tags": ["ok", "sure"],
            },
            schema=self.SCHEMA,
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["applied_rules"], 19)

    def test_error_cap_truncation(self) -> None:
        document = [{"id": "not-an-int"}] * 300
        result = self.tool.execute(
            mode="validate",
            document=document,
            schema={"items": {"properties": {"id": {"type": "integer"}}}},
        )
        self.assertEqual(len(result["errors"]), self.tool.max_errors)
        self.assertTrue(result["truncated"])

    def test_deterministic(self) -> None:
        first = self.tool.execute(
            mode="validate", document=self.DOCUMENT, schema=self.SCHEMA
        )
        second = DirectJsonSchemaTool().execute(
            mode="validate", document=self.DOCUMENT, schema=self.SCHEMA
        )
        self.assertEqual(first, second)


# --------------------------------------------------------------------- #
# infer_schema
# --------------------------------------------------------------------- #


class InferSchemaTest(JsonSchemaToolTestCase):
    """Literal skeleton ground truth, masking, and the round-trip."""

    DOCUMENT = {
        "id": 7,
        "name": "au",
        "api_key": "sk-1234567890123456",
        "created": "2026-10-21",
        "owner": "a@example.com",
        "site": "https://example.com",
        "host": "10.0.0.1",
        "token_id": "e3d6a91c-8f21-4c01-9a1a-2f2f2f2f2f2f",
        "ratio": 1.5,
        "active": True,
        "note": None,
        "tags": ["x", "y"],
        "points": [1, 2, 3],
        "mixed": [1, "a"],
        "empty": [],
        "blank": {},
    }

    EXPECTED = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "examples": [7]},
            "name": {"type": "string", "examples": ["au"]},
            "api_key": {"type": "string", "examples": ["***"]},
            "created": {
                "type": "string",
                "format": "date",
                "examples": ["2026-10-21"],
            },
            "owner": {
                "type": "string",
                "format": "email",
                "examples": ["a@example.com"],
            },
            "site": {
                "type": "string",
                "format": "url",
                "examples": ["https://example.com"],
            },
            "host": {
                "type": "string",
                "format": "ipv4",
                "examples": ["10.0.0.1"],
            },
            "token_id": {
                "type": "string",
                "format": "uuid",
                "examples": ["***"],  # secret-ish name (TOKEN)
            },
            "ratio": {"type": "number", "examples": [1.5]},
            "active": {"type": "boolean", "examples": [True]},
            "note": {"type": "null", "examples": [None]},
            "tags": {"type": "array", "items": {"type": "string"}},
            "points": {"type": "array", "items": {"type": "integer"}},
            "mixed": {
                "type": "array",
                "items": {"type": ["integer", "string"]},
            },
            "empty": {"type": "array"},
            "blank": {"type": "object"},
        },
        "required": sorted(DOCUMENT),
    }

    def test_literal_skeleton(self) -> None:
        result = self.tool.execute(
            mode="infer_schema", document=self.DOCUMENT
        )
        self.assertEqual(result["document_type"], "object")
        self.assertEqual(result["schema"], self.EXPECTED)

    def test_no_secret_leak_in_inferred_schema(self) -> None:
        result = self.tool.execute(
            mode="infer_schema", document=self.DOCUMENT
        )
        dumped = json.dumps(result)
        self.assertNotIn("sk-1234567890123456", dumped)
        self.assertNotIn("e3d6a91c", dumped)

    def test_uniform_objects_merge(self) -> None:
        result = self.tool.execute(
            mode="infer_schema",
            document={
                "users": [
                    {"id": 1, "name": "a"},
                    {"id": 2, "name": "b", "admin": True},
                    {"id": 3, "admin": False},
                ]
            },
        )
        items = result["schema"]["properties"]["users"]["items"]
        self.assertEqual(items["type"], "object")
        self.assertEqual(
            items["properties"],
            {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "admin": {"type": "boolean"},
            },
        )
        self.assertEqual(items["required"], ["id"])  # intersection only

    def test_scalar_document(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="infer_schema", document='"hi"')["schema"],
            {"type": "string", "examples": ["hi"]},
        )
        self.assertEqual(
            self.tool.execute(mode="infer_schema", document=None)["schema"],
            {"type": "null", "examples": [None]},
        )

    def test_round_trip_200_seeded_documents(self) -> None:
        for index, document in enumerate(_seeded_documents(200)):
            # a native top-level string must travel as its JSON text
            carrier = json.dumps(document) if isinstance(document, str) else document
            inferred = self.tool.execute(
                mode="infer_schema", document=carrier
            )
            result = self.tool.execute(
                mode="validate",
                document=carrier,
                schema=inferred["schema"],
            )
            self.assertTrue(result["valid"], (index, document, result))
            dumped = json.dumps(inferred)
            self.assertNotIn("SECRETVALUE", dumped, index)

    def test_infer_then_validate_is_deterministic(self) -> None:
        for document in _seeded_documents(20):
            carrier = json.dumps(document) if isinstance(document, str) else document
            first = self.tool.execute(mode="infer_schema", document=carrier)
            second = self.tool.execute(mode="infer_schema", document=carrier)
            self.assertEqual(first, second)


def _seeded_documents(count):
    """Deterministic pseudo-random JSON documents for the round-trip."""
    keys = [
        "id", "name", "api_key", "user_password", "auth_token", "created",
        "owner_email", "website", "host", "tags", "scores", "active",
        "ratio", "meta", "note", "deep",
    ]

    def scalar(rng):
        pick = rng.randrange(12)
        if pick == 0:
            return rng.randint(-1000, 1000)
        if pick == 1:
            return round(rng.uniform(-50.0, 50.0), 3)
        if pick == 2:
            return rng.random() < 0.5
        if pick == 3:
            return None
        if pick == 4:
            return "user%d@example.com" % rng.randint(1, 99)
        if pick == 5:
            return "2024-%02d-%02d" % (rng.randint(1, 12), rng.randint(1, 28))
        if pick == 6:
            return "2024-06-0%dT0%d:00:00Z" % (
                rng.randint(1, 9), rng.randint(1, 9)
            )
        if pick == 7:
            return "https://example.com/page/%d" % rng.randint(1, 99)
        if pick == 8:
            return "123e4567-e89b-12d3-a456-42661417400%d" % rng.randint(0, 9)
        if pick == 9:
            return "10.0.%d.%d" % (rng.randint(0, 255), rng.randint(0, 255))
        if pick == 10:
            return "text-%d" % rng.randint(0, 99)
        return ""  # empty strings are valid JSON strings

    def make(rng, depth):
        if depth <= 0:
            return scalar(rng)
        roll = rng.random()
        if roll < 0.5:
            names = rng.sample(keys, rng.randint(0, 6))
            document = {}
            for name in names:
                if _secretish(name):
                    # exclusive alphabet: any leak is unambiguous
                    document[name] = "SECRETVALUE-%04d" % rng.randint(0, 9999)
                else:
                    document[name] = make(rng, depth - 1)
            return document
        if roll < 0.8:
            return [make(rng, depth - 1) for _ in range(rng.randint(0, 4))]
        return scalar(rng)

    return [
        make(random.Random(0xC0FFEE + index), 3) for index in range(count)
    ]


# --------------------------------------------------------------------- #
# simplify_errors
# --------------------------------------------------------------------- #


class SimplifyErrorsTest(JsonSchemaToolTestCase):
    """Grouped-by-path summary with literal ground truth."""

    ERRORS = [
        {"path": "user.email", "schema_rule": "format",
         "message": "not a valid email (family profile)", "actual": "x"},
        {"path": "user.email", "schema_rule": "required",
         "message": "required property 'email' is missing", "actual": "email"},
        {"path": "user.email", "schema_rule": "format",
         "message": "not a valid email (family profile)", "actual": "y"},
        {"path": "", "schema_rule": "type",
         "message": "expected type object, got array", "actual": "array"},
        {"path": "tags", "schema_rule": "uniqueItems",
         "message": "array items are not unique", "actual": 1},
        "not a dict",
        {"path": 5, "schema_rule": "type", "message": "x"},
    ]

    def test_literal_summary(self) -> None:
        result = self.tool.execute(mode="simplify_errors", errors=self.ERRORS)
        self.assertEqual(
            result,
            {
                "mode": "simplify_errors",
                "result": "5 error(s) across 3 path(s)",
                "total_errors": 7,
                "groups": [
                    {
                        "path": "user.email",
                        "count": 3,
                        "rules": ["format", "required"],
                        "messages": [
                            "not a valid email (family profile)",
                            "required property 'email' is missing",
                        ],
                    },
                    {
                        "path": "",
                        "count": 1,
                        "rules": ["type"],
                        "messages": [
                            "expected type object, got array"
                        ],
                    },
                    {
                        "path": "tags",
                        "count": 1,
                        "rules": ["uniqueItems"],
                        "messages": ["array items are not unique"],
                    },
                ],
                "rule_totals": {
                    "format": 2, "required": 1, "type": 1, "uniqueItems": 1
                },
                "unparseable": ["not a dict", self.ERRORS[6]],
            },
        )

    def test_round_trip_with_validate(self) -> None:
        report = self.tool.execute(
            mode="validate",
            document=ErrorMatrixTest.DOCUMENT,
            schema=ErrorMatrixTest.SCHEMA,
        )
        summary = self.tool.execute(
            mode="simplify_errors", errors=report["errors"]
        )
        self.assertEqual(summary["total_errors"], 8)
        top = summary["groups"][0]
        self.assertEqual(top["path"], "name")
        self.assertEqual(top["count"], 2)

    def test_errors_parameter_strict(self) -> None:
        self.assert_invalid(mode="simplify_errors", errors="nope")
        self.assert_invalid(mode="simplify_errors", errors=None)
        self.assert_invalid(mode="simplify_errors", errors={"a": 1})


# --------------------------------------------------------------------- #
# mode / parameter handling
# --------------------------------------------------------------------- #


class ModeHandlingTest(JsonSchemaToolTestCase):
    """Unknown modes and the package export."""

    def test_unknown_mode(self) -> None:
        self.assert_invalid(mode="repair", document={})

    def test_package_export_matches(self) -> None:
        self.assertIs(JsonSchemaTool, DirectJsonSchemaTool)


if __name__ == "__main__":
    unittest.main()
