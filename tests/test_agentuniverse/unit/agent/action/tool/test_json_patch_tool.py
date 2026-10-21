#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_json_patch_tool.py

"""Offline unit tests for JsonPatchTool.

The tool implements RFC 6902 (JSON Patch) and RFC 6901 (JSON
Pointer) purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: ``apply`` is checked against the ground-truth
vectors of RFC 6902 Appendix A (including the famous ``~0``/``~1``
adds and the failing ``test`` operation) plus the RFC 6901 §5
pointer-evaluation document, every operation is exercised against
object and array targets, and the pointer / validation / error
matrices cover both the parameter-level ``ValueError`` inputs and
the content-level structured ``error`` payloads. The ``diff`` mode
is verified through the round-trip property ``apply(diff(a, b),
a) == b`` over 200 seeded document pairs, plus determinism and the
documented large-array fallback. Isolation is asserted explicitly:
no input document and no patch entry is ever mutated.
"""

import copy
import json
import random
import unittest

from agentuniverse.agent.action.tool.common_tool import JsonPatchTool
from agentuniverse.agent.action.tool.common_tool.json_patch_tool import (
    JsonPatchTool as DirectJsonPatchTool,
)


def run_apply(document, patch, atomic=None):
    kwargs = {"mode": "apply", "document": document, "patch": patch}
    if atomic is not None:
        kwargs["atomic"] = atomic
    return JsonPatchTool().execute(**kwargs)


def run_diff(a, b):
    return JsonPatchTool().execute(mode="diff", document=a, document_b=b)


def run_validate(patch):
    return JsonPatchTool().execute(mode="validate_patch", patch=patch)


# --------------------------------------------------------------------- #
# RFC 6901 §5: the pointer-evaluation document and its vectors
# --------------------------------------------------------------------- #

RFC6901_DOC = {
    "foo": ["bar", "baz"],
    "": 0,
    "a/b": 1,
    "c%d": 2,
    "e^f": 3,
    "g|h": 4,
    "i\\j": 5,
    "k\"l": 6,
    " ": 7,
    "m~n": 8,
}

RFC6901_VECTORS = [
    ("", RFC6901_DOC),
    ("/foo", ["bar", "baz"]),
    ("/foo/0", "bar"),
    ("/", 0),
    ("/a~1b", 1),
    ("/c%d", 2),
    ("/e^f", 3),
    ("/g|h", 4),
    ("/i\\j", 5),
    ("/k\"l", 6),
    ("/ ", 7),
    ("/m~0n", 8),
]


class TestRfc6902AppendixA(unittest.TestCase):
    """The RFC 6902 Appendix A examples, verbatim."""

    def test_a1_adding_an_object_member(self):
        result = run_apply(
            {"foo": "bar"},
            [{"op": "add", "path": "/baz", "value": "qux"}],
        )
        self.assertEqual(
            result["document"], {"baz": "qux", "foo": "bar"}
        )
        self.assertEqual(result["applied_count"], 1)
        self.assertEqual(result["failed_count"], 0)

    def test_a2_adding_an_array_element(self):
        result = run_apply(
            {"foo": ["bar", "baz"]},
            [{"op": "add", "path": "/foo/1", "value": "qux"}],
        )
        self.assertEqual(
            result["document"], {"foo": ["bar", "qux", "baz"]}
        )

    def test_a3_removing_an_object_member(self):
        result = run_apply(
            {"baz": "qux", "foo": "bar"},
            [{"op": "remove", "path": "/baz"}],
        )
        self.assertEqual(result["document"], {"foo": "bar"})

    def test_a4_removing_an_array_element(self):
        result = run_apply(
            {"foo": ["bar", "qux", "baz"]},
            [{"op": "remove", "path": "/foo/1"}],
        )
        self.assertEqual(result["document"], {"foo": ["bar", "baz"]})

    def test_a5_replacing_a_value(self):
        result = run_apply(
            {"baz": "qux", "foo": ["bar", "quux"]},
            [
                {"op": "replace", "path": "/baz", "value": "boo"},
                {"op": "replace", "path": "/foo/1", "value": "baz"},
            ],
        )
        self.assertEqual(
            result["document"], {"baz": "boo", "foo": ["bar", "baz"]}
        )
        self.assertEqual(result["applied_count"], 2)

    def test_a6_moving_a_value_between_objects(self):
        result = run_apply(
            {
                "foo": {"bar": "baz", "waldo": "fred"},
                "qux": {"corge": "grault"},
            },
            [
                {
                    "op": "move",
                    "from": "/foo/waldo",
                    "path": "/qux/thud",
                }
            ],
        )
        self.assertEqual(
            result["document"],
            {
                "foo": {"bar": "baz"},
                "qux": {"corge": "grault", "thud": "fred"},
            },
        )

    def test_a7_moving_an_array_element(self):
        result = run_apply(
            {"foo": ["all", "grass", "cows", "eat"]},
            [{"op": "move", "from": "/foo/1", "path": "/foo/3"}],
        )
        self.assertEqual(
            result["document"], {"foo": ["all", "cows", "eat", "grass"]}
        )

    def test_a8_testing_a_value_success(self):
        result = run_apply(
            {"baz": "qux", "foo": ["a", 2, "c"]},
            [
                {"op": "test", "path": "/baz", "value": "qux"},
                {"op": "test", "path": "/foo/1", "value": 2},
            ],
        )
        self.assertEqual(
            result["document"], {"baz": "qux", "foo": ["a", 2, "c"]}
        )
        self.assertEqual(result["applied_count"], 2)

    def test_a9_testing_a_value_error(self):
        result = run_apply(
            {"bar": "qux"},
            [{"op": "test", "path": "/bar", "value": "bar"}],
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(result["failed"][0]["index"], 0)
        self.assertEqual(result["failed"][0]["op"], "test")
        self.assertEqual(result["document"], {"bar": "qux"})

    def test_a10_adding_a_nested_member_object(self):
        result = run_apply(
            {"foo": "bar"},
            [
                {
                    "op": "add",
                    "path": "/child",
                    "value": {"grandchild": {}},
                }
            ],
        )
        self.assertEqual(
            result["document"],
            {"foo": "bar", "child": {"grandchild": {}}},
        )


class TestRfc6901PointerMatrix(unittest.TestCase):
    """RFC 6901 §5 pointer evaluation over the spec document."""

    def test_spec_vectors_via_test_op(self):
        for pointer, expected in RFC6901_VECTORS:
            with self.subTest(pointer=pointer):
                result = run_apply(
                    copy.deepcopy(RFC6901_DOC),
                    [{"op": "test", "path": pointer, "value": expected}],
                )
                self.assertEqual(result["applied_count"], 1, result)

    def test_spec_vectors_via_add_escaping(self):
        # The famous ~0/~1 add vectors: adding escaped keys.
        result = run_apply(
            {},
            [
                {"op": "add", "path": "/a~1b", "value": 1},
                {"op": "add", "path": "/m~0n", "value": 8},
                {"op": "add", "path": "/", "value": 0},
                {"op": "add", "path": "/k\"l", "value": 6},
            ],
        )
        self.assertEqual(
            result["document"],
            {"a/b": 1, "m~n": 8, "": 0, "k\"l": 6},
        )

    def test_escape_decoding_order(self):
        # RFC 6901 §3: "~01" decodes to "~1" (~0 first would corrupt).
        result = run_apply(
            {"~1": "hit"},
            [{"op": "test", "path": "/~01", "value": "hit"}],
        )
        self.assertEqual(result["applied_count"], 1)
        result = run_apply(
            {"a/b": "slash"},
            [{"op": "test", "path": "/a~1b", "value": "slash"}],
        )
        self.assertEqual(result["applied_count"], 1)

    def test_invalid_pointer_syntax(self):
        for pointer, fragment in [
            ("#/foo/bar", "must not start with '#'"),
            ("foo/bar", "must be empty or start with '/'"),
            ("/a~2b", "invalid escape"),
            ("/a~", "invalid escape"),
            ("~", "must be empty or start with '/'"),
        ]:
            with self.subTest(pointer=pointer):
                result = run_apply(
                    {"a": 1},
                    [{"op": "remove", "path": pointer}],
                )
                self.assertEqual(result["failed_count"], 1)
                self.assertIn(fragment, result["failed"][0]["reason"])

    def test_non_string_pointer(self):
        result = run_apply(
            {"a": 1}, [{"op": "remove", "path": 42}]
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertIn("'path' must be a JSON Pointer string",
                      result["failed"][0]["reason"])

    def test_leading_zero_array_index_rejected(self):
        result = run_apply(
            {"a": [1, 2, 3]}, [{"op": "remove", "path": "/a/01"}]
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertIn("leading zeros", result["failed"][0]["reason"])
        # ... but "01" is a legitimate *object* member name.
        result = run_apply(
            {"01": "yes"}, [{"op": "test", "path": "/01", "value": "yes"}]
        )
        self.assertEqual(result["applied_count"], 1)

    def test_non_digit_array_index_rejected(self):
        for index in ("-5", "1.5", "1e0", "+1", " 1", "١"):
            with self.subTest(index=index):
                result = run_apply(
                    {"a": [1, 2, 3]},
                    [{"op": "remove", "path": f"/a/{index}"}],
                )
                self.assertEqual(result["failed_count"], 1)
                self.assertIn("not valid", result["failed"][0]["reason"])


class TestAddOperation(unittest.TestCase):
    """add — object and array targets, the '-' marker, bounds."""

    def test_object_member_create_and_overwrite(self):
        result = run_apply(
            {"a": 1},
            [
                {"op": "add", "path": "/b", "value": 2},
                {"op": "add", "path": "/a", "value": 9},
            ],
        )
        self.assertEqual(result["document"], {"a": 9, "b": 2})
        self.assertIn("set the object member 'b'",
                      result["applied"][0]["summary"])
        self.assertIn("set the object member 'a'",
                      result["applied"][1]["summary"])

    def test_array_insert_head_middle_end(self):
        # Sequential evaluation: each insert sees the previous one.
        result = run_apply(
            {"a": [2, 3]},
            [
                {"op": "add", "path": "/a/0", "value": 1},
                {"op": "add", "path": "/a/2", "value": 4},
                {"op": "add", "path": "/a/4", "value": 5},
            ],
        )
        self.assertEqual(result["document"], {"a": [1, 2, 4, 3, 5]})
        # index == length is the append position at each step.
        result = run_apply(
            {"a": [2, 3]},
            [
                {"op": "add", "path": "/a/0", "value": 1},
                {"op": "add", "path": "/a/3", "value": 4},
                {"op": "add", "path": "/a/4", "value": 5},
            ],
        )
        self.assertEqual(result["document"], {"a": [1, 2, 3, 4, 5]})

    def test_append_marker(self):
        result = run_apply(
            {"a": [1, 2]},
            [{"op": "add", "path": "/a/-", "value": 3}],
        )
        self.assertEqual(result["document"], {"a": [1, 2, 3]})
        self.assertIn("appended", result["applied"][0]["summary"])

    def test_append_marker_only_as_final_token(self):
        result = run_apply(
            {"a": [1, 2]},
            [{"op": "add", "path": "/a/-/b", "value": 3}],
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertIn("'-' (the append marker)",
                      result["failed"][0]["reason"])

    def test_append_marker_invalid_for_remove(self):
        result = run_apply(
            {"a": [1, 2]}, [{"op": "remove", "path": "/a/-"}]
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertIn("'-' (the append marker)",
                      result["failed"][0]["reason"])

    def test_index_out_of_range(self):
        result = run_apply(
            {"a": [1, 2]}, [{"op": "add", "path": "/a/3", "value": 9}]
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertIn("out of range", result["failed"][0]["reason"])

    def test_navigating_through_missing_or_scalar(self):
        for path, fragment in [
            ("/x/y", "does not exist"),
            ("/a/0/b", "cannot descend into"),
            ("/a/b", "cannot add a member to a number"),
        ]:
            with self.subTest(path=path):
                result = run_apply(
                    {"a": 5}, [{"op": "add", "path": path, "value": 1}]
                )
                self.assertEqual(result["failed_count"], 1)
                self.assertIn(fragment, result["failed"][0]["reason"])

    def test_whole_document_add(self):
        result = run_apply(
            {"old": True},
            [{"op": "add", "path": "", "value": [1, 2]}],
        )
        self.assertEqual(result["document"], [1, 2])
        self.assertEqual(
            result["applied"][0]["summary"],
            "replaced the whole document",
        )


class TestRemoveOperation(unittest.TestCase):
    """remove — the target must exist."""

    def test_object_and_array(self):
        result = run_apply(
            {"a": 1, "list": [1, 2, 3]},
            [
                {"op": "remove", "path": "/a"},
                {"op": "remove", "path": "/list/1"},
            ],
        )
        self.assertEqual(result["document"], {"list": [1, 3]})
        self.assertIn("removed a number at '/a'",
                      result["applied"][0]["summary"])

    def test_missing_targets(self):
        for path in ("/zzz", "/list/9"):
            with self.subTest(path=path):
                result = run_apply(
                    {"a": 1, "list": [1]},
                    [{"op": "remove", "path": path}],
                )
                self.assertEqual(result["failed_count"], 1)

    def test_remove_whole_document_rejected(self):
        result = run_apply({"a": 1}, [{"op": "remove", "path": ""}])
        self.assertEqual(result["failed_count"], 1)
        self.assertIn("no JSON meaning", result["failed"][0]["reason"])


class TestReplaceOperation(unittest.TestCase):
    """replace — the target must exist (assignment, not insert)."""

    def test_object_and_array(self):
        result = run_apply(
            {"a": 1, "list": [1, 2, 3]},
            [
                {"op": "replace", "path": "/a", "value": None},
                {"op": "replace", "path": "/list/1", "value": 99},
            ],
        )
        self.assertEqual(
            result["document"], {"a": None, "list": [1, 99, 3]}
        )

    def test_missing_target_rejected(self):
        for path in ("/zzz", "/list/3"):
            with self.subTest(path=path):
                result = run_apply(
                    {"list": [1]},
                    [{"op": "replace", "path": path, "value": 0}],
                )
                self.assertEqual(result["failed_count"], 1)

    def test_whole_document_replace(self):
        result = run_apply(
            [1, 2], [{"op": "replace", "path": "", "value": {"a": 1}}]
        )
        self.assertEqual(result["document"], {"a": 1})


class TestMoveOperation(unittest.TestCase):
    """move — remove from, then add at, with the cycle check."""

    def test_move_between_siblings_and_whole_doc(self):
        result = run_apply(
            {"a": {"x": 1}, "b": {}},
            [{"op": "move", "from": "/a", "path": "/b/y"}],
        )
        self.assertEqual(result["document"], {"b": {"y": {"x": 1}}})
        result = run_apply(
            {"a": 1}, [{"op": "move", "from": "/a", "path": ""}]
        )
        self.assertEqual(result["document"], 1)

    def test_move_to_same_location_is_a_no_op(self):
        result = run_apply(
            {"a": [1, 2, 3]},
            [{"op": "move", "from": "/a", "path": "/a"}],
        )
        self.assertEqual(result["document"], {"a": [1, 2, 3]})
        self.assertIn("no-op", result["applied"][0]["summary"])

    def test_move_into_own_descendant_rejected(self):
        result = run_apply(
            {"foo": {"bar": "baz"}},
            [{"op": "move", "from": "/foo", "path": "/foo/bar"}],
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertIn("own descendant", result["failed"][0]["reason"])
        # Deeper descendant, same verdict.
        result = run_apply(
            {"a": {"b": {"c": {"d": 1}}}},
            [{"op": "move", "from": "/a/b", "path": "/a/b/c/d"}],
        )
        self.assertEqual(result["failed_count"], 1)

    def test_move_from_missing_rejected(self):
        result = run_apply(
            {"a": 1}, [{"op": "move", "from": "/zzz", "path": "/b"}]
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertIn("does not exist", result["failed"][0]["reason"])

    def test_array_indices_evaluated_after_removal(self):
        # Spec §4.4: move == remove followed by add — so the target
        # index is evaluated on the post-removal array.
        result = run_apply(
            {"a": [1, 2, 3, 4]},
            [{"op": "move", "from": "/a/0", "path": "/a/2"}],
        )
        self.assertEqual(result["document"], {"a": [2, 3, 1, 4]})


class TestCopyOperation(unittest.TestCase):
    """copy — a deep copy; the source is never aliased."""

    def test_copy_object_and_array_element(self):
        result = run_apply(
            {"a": {"x": 1}, "list": [10, 20]},
            [
                {"op": "copy", "from": "/a", "path": "/b"},
                {"op": "copy", "from": "/list/1", "path": "/list/0"},
            ],
        )
        self.assertEqual(
            result["document"],
            {"a": {"x": 1}, "b": {"x": 1}, "list": [20, 10, 20]},
        )

    def test_copy_is_deep(self):
        result = run_apply(
            {"src": {"inner": [1, 2]}},
            [
                {"op": "copy", "from": "/src", "path": "/dst"},
                {"op": "replace", "path": "/dst/inner/0", "value": 99},
            ],
        )
        self.assertEqual(
            result["document"],
            {"src": {"inner": [1, 2]}, "dst": {"inner": [99, 2]}},
        )

    def test_copy_from_missing_rejected(self):
        result = run_apply(
            {"a": 1}, [{"op": "copy", "from": "/zzz", "path": "/b"}]
        )
        self.assertEqual(result["failed_count"], 1)

    def test_copy_whole_document(self):
        result = run_apply(
            {"a": 1}, [{"op": "copy", "from": "", "path": "/b"}]
        )
        self.assertEqual(
            result["document"], {"a": 1, "b": {"a": 1}}
        )


class TestTestOperation(unittest.TestCase):
    """test — equality per JSON semantics (RFC 6902 §4.6)."""

    def test_equality_semantics(self):
        doc = {
            "int": 1,
            "float": 1.0,
            "str": "1",
            "true": True,
            "null": None,
            "arr": [1, 2],
            "obj_a": {"a": 1, "b": 2},
            "obj_b": {"b": 2, "a": 1},
        }
        cases = [
            ("/int", 1, True),
            ("/int", 1.0, True),      # numbers compare numerically
            ("/float", 1, True),
            ("/int", True, False),    # true != 1
            ("/true", 1, False),
            ("/true", True, True),
            ("/str", "1", True),
            ("/str", 1, False),       # "1" != 1
            ("/null", None, True),
            ("/null", "null", False),
            ("/arr", [1, 2], True),
            ("/arr", [2, 1], False),  # array order is significant
            ("/obj_a", {"b": 2, "a": 1}, True),  # order irrelevant
            ("/obj_a", {"a": 1}, False),
        ]
        for path, value, should_pass in cases:
            with self.subTest(path=path, value=value):
                result = run_apply(
                    copy.deepcopy(doc),
                    [{"op": "test", "path": path, "value": value}],
                )
                self.assertEqual(
                    result["applied_count"] if should_pass
                    else result["failed_count"],
                    1,
                )

    def test_whole_document_test(self):
        doc = {"a": [1, {"b": None}]}
        result = run_apply(
            copy.deepcopy(doc),
            [{"op": "test", "path": "", "value": {"a": [1, {"b": None}]}}],
        )
        self.assertEqual(result["applied_count"], 1)

    def test_failing_test_in_lenient_mode_continues(self):
        result = run_apply(
            {"a": 1},
            [
                {"op": "test", "path": "/a", "value": 2},
                {"op": "add", "path": "/b", "value": 3},
            ],
        )
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(result["applied_count"], 1)
        self.assertEqual(result["document"], {"a": 1, "b": 3})


class TestAtomicVersusLenient(unittest.TestCase):
    """Lenient applies what is valid; atomic leaves the original."""

    PATCH = [
        {"op": "add", "path": "/c", "value": 3},
        {"op": "remove", "path": "/zzz"},
        {"op": "replace", "path": "/a", "value": 9},
    ]

    def test_lenient_default(self):
        result = run_apply({"a": 1, "b": 2}, self.PATCH)
        self.assertFalse(result["atomic"])
        self.assertEqual(
            result["document"], {"a": 9, "b": 2, "c": 3}
        )
        self.assertEqual(result["applied_count"], 2)
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(result["failed"][0]["index"], 1)
        self.assertEqual(result["failed"][0]["op"], "remove")
        self.assertEqual(result["failed"][0]["path"], "/zzz")
        self.assertIn("lenient mode", result["note"])

    def test_atomic_leaves_document_untouched(self):
        original = {"a": 1, "b": 2}
        snapshot = copy.deepcopy(original)
        result = run_apply(original, self.PATCH, atomic=True)
        self.assertTrue(result["atomic"])
        self.assertEqual(result["document"], snapshot)
        self.assertEqual(result["applied"], [])
        self.assertEqual(result["applied_count"], 0)
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(result["failed"][0]["index"], 1)
        self.assertIn("atomic mode", result["failed"][0]["note"])
        self.assertEqual(original, snapshot)

    def test_atomic_success_path_applies_everything(self):
        result = run_apply(
            {"a": 1},
            [{"op": "add", "path": "/b", "value": 2}],
            atomic=True,
        )
        self.assertEqual(result["document"], {"a": 1, "b": 2})
        self.assertEqual(result["applied_count"], 1)
        self.assertEqual(result["failed_count"], 0)

    def test_empty_patch(self):
        result = run_apply({"a": 1}, [])
        self.assertEqual(result["document"], {"a": 1})
        self.assertEqual(result["applied_count"], 0)
        self.assertEqual(result["failed_count"], 0)


class TestDiffMode(unittest.TestCase):
    """diff — vectors, determinism, and the round-trip property."""

    def test_equal_documents(self):
        result = run_diff({"a": [1, {"b": 2}]}, {"a": [1, {"b": 2}]})
        self.assertTrue(result["equal"])
        self.assertEqual(result["patch"], [])
        self.assertEqual(result["op_count"], 0)
        self.assertIn("not guaranteed minimal", result["note"])

    def test_object_member_add_remove_replace(self):
        # Emission order: removes first, then the sorted-key walk of
        # b (adds and recursions interleaved) — deterministic.
        result = run_diff(
            {"keep": 1, "gone": 2, "changed": 3},
            {"keep": 1, "new": 4, "changed": 5},
        )
        self.assertEqual(
            result["patch"],
            [
                {"op": "remove", "path": "/gone"},
                {"op": "replace", "path": "/changed", "value": 5},
                {"op": "add", "path": "/new", "value": 4},
            ],
        )

    def test_array_vector(self):
        result = run_diff([1, 2, 3], [3, 2])
        round_trip = run_apply([1, 2, 3], result["patch"])
        self.assertEqual(round_trip["document"], [3, 2])
        self.assertEqual(round_trip["failed_count"], 0)

    def test_type_change_falls_back_to_replace(self):
        result = run_diff({"a": [1]}, {"a": "text"})
        self.assertEqual(
            result["patch"],
            [{"op": "replace", "path": "/a", "value": "text"}],
        )
        result = run_diff(5, {"a": 1})
        self.assertEqual(
            result["patch"], [{"op": "replace", "path": "", "value": {"a": 1}}]
        )

    def test_deterministic_output(self):
        a = {"z": [1, 2], "a": {"k": [3]}}
        b = {"z": [2, 1], "a": {"k": []}}
        first = run_diff(a, b)
        second = run_diff(a, b)
        self.assertEqual(
            json.dumps(first["patch"]), json.dumps(second["patch"])
        )

    def test_large_array_fallback(self):
        a = list(range(600))
        b = list(range(300, 900))
        result = run_diff(a, b)
        self.assertEqual(result["op_count"], 1)
        self.assertEqual(
            result["patch"][0],
            {"op": "replace", "path": "", "value": b},
        )

    def test_round_trip_over_seeded_pairs(self):
        for seed in range(200):
            with self.subTest(seed=seed):
                rng = random.Random(seed)
                a = _seeded_document(rng, 0)
                b = _seeded_document(rng, 1)
                # Documents go in as JSON text (exercising the decode
                # path); a top-level "" string is a valid document.
                diff = run_diff(json.dumps(a), json.dumps(b))
                applied = run_apply(json.dumps(a), diff["patch"])
                self.assertEqual(
                    applied["failed_count"], 0,
                    f"seed={seed} patch={diff['patch']}",
                )
                self.assertTrue(
                    _deep_equal(applied["document"], b),
                    f"seed={seed} got={applied['document']!r} "
                    f"want={b!r}",
                )

    def test_diff_uses_deep_values_not_aliases(self):
        # diff result values must be snapshots: mutating the source
        # afterwards cannot change the patch.
        a = {"x": 1}
        b = {"x": {"deep": [1, 2]}}
        result = run_diff(a, b)
        b["x"]["deep"].append(3)
        self.assertEqual(
            result["patch"],
            [{"op": "replace", "path": "/x", "value": {"deep": [1, 2]}}],
        )


class TestValidatePatchMode(unittest.TestCase):
    """validate_patch — structure and pointer syntax, no document."""

    def test_valid_patch_one_of_each_op(self):
        result = run_validate(
            [
                {"op": "add", "path": "/a", "value": 1},
                {"op": "remove", "path": "/b"},
                {"op": "replace", "path": "/c", "value": None},
                {"op": "move", "from": "/d", "path": "/e"},
                {"op": "copy", "from": "/f", "path": "/g"},
                {"op": "test", "path": "/h", "value": [1, {"i": True}]},
            ]
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["op_count"], 6)
        self.assertEqual(len(result["ops"]), 6)

    def test_extra_members_are_ignored(self):
        # RFC 6902 §4: undefined members MUST be ignored.
        result = run_validate(
            [{"op": "remove", "path": "/a", "comment": "why not"}]
        )
        self.assertTrue(result["valid"])

    def test_error_matrix(self):
        cases = [
            ([{"path": "/a"}], 0, "op"),
            ([{"op": "merge", "path": "/a"}], 0, "op"),
            ([{"op": 5, "path": "/a"}], 0, "op"),
            ([{"op": "remove"}], 0, "path"),
            ([{"op": "remove", "path": 7}], 0, "path"),
            ([{"op": "remove", "path": "#/a"}], 0, "path"),
            ([{"op": "add", "path": "/a"}], 0, "value"),
            ([{"op": "replace", "path": "/a"}], 0, "value"),
            ([{"op": "test", "path": "/a"}], 0, "value"),
            ([{"op": "move", "path": "/a"}], 0, "from"),
            ([{"op": "copy", "path": "/a"}], 0, "from"),
            ([{"op": "move", "path": "/a", "from": "no-slash"}], 0, "from"),
            (["not-an-object"], 0, "op"),
        ]
        for patch, index, field in cases:
            with self.subTest(patch=patch):
                result = run_validate(patch)
                self.assertFalse(result["valid"])
                self.assertEqual(len(result["errors"]), 1)
                self.assertEqual(result["errors"][0]["index"], index)
                self.assertEqual(result["errors"][0]["field"], field)

    def test_all_errors_collected(self):
        result = run_validate(
            [
                {"op": "add", "path": "/ok", "value": 1},
                {"op": "nope", "path": "/a"},
                {"op": "remove", "path": "bad"},
                {"op": "copy", "path": "/c", "from": "/x", "extra": 1},
            ]
        )
        self.assertFalse(result["valid"])
        self.assertEqual(
            [e["index"] for e in result["errors"]], [1, 2]
        )

    def test_empty_patch_is_valid(self):
        result = run_validate([])
        self.assertTrue(result["valid"])
        self.assertEqual(result["op_count"], 0)


class TestInputHandlingAndErrors(unittest.TestCase):
    """Parameter validation and content-level error payloads."""

    def test_bad_mode(self):
        with self.assertRaises(ValueError):
            JsonPatchTool().execute(mode="merge", patch=[])

    def test_missing_required_parameters(self):
        tool = JsonPatchTool()
        with self.assertRaises(ValueError):
            tool.execute(mode="apply")
        with self.assertRaises(ValueError):
            tool.execute(mode="apply", patch=[])
        with self.assertRaises(ValueError):
            tool.execute(mode="apply", patch=[], document=None)
        with self.assertRaises(ValueError):
            tool.execute(mode="diff", document={"a": 1})
        with self.assertRaises(ValueError):
            tool.execute(mode="validate_patch")

    def test_bad_parameter_types(self):
        tool = JsonPatchTool()
        with self.assertRaises(ValueError):
            tool.execute(mode="apply", document={"a": 1}, patch=5)
        with self.assertRaises(ValueError):
            tool.execute(mode="apply", document=b"nope", patch=[])
        with self.assertRaises(ValueError):
            tool.execute(
                mode="apply",
                document={"a": 1},
                patch=[],
                atomic="yes",
            )
        with self.assertRaises(ValueError):
            tool.execute(mode="apply", document="", patch=[])

    def test_document_text_decoding(self):
        result = run_apply('{"a": [1, 2]}', '[{"op": "add", "path": "/a/-", "value": 3}]')
        self.assertEqual(result["document"], {"a": [1, 2, 3]})
        # Parsed scalars / None are legitimate JSON documents too.
        result = run_apply("5", '[{"op": "test", "path": "", "value": 5}]')
        self.assertEqual(result["applied_count"], 1)

    def test_structured_error_payloads(self):
        # Invalid document text.
        result = run_apply("{not json}", [{"op": "remove", "path": "/a"}])
        self.assertIn("error", result)
        self.assertIn("not valid JSON", result["error"]["reason"])
        # Invalid patch text.
        result = run_apply({"a": 1}, "[not json")
        self.assertIn("not valid JSON", result["error"]["reason"])
        # Patch text decoding to a non-list.
        result = run_apply({"a": 1}, '{"op": "remove", "path": "/a"}')
        self.assertIn(
            "must decode to a list", result["error"]["reason"]
        )
        # The diff mode reports through the same payload shape.
        result = run_diff("{bad", {"a": 1})
        self.assertIn("error", result)
        result = run_diff({"a": 1}, "[bad")
        self.assertIn("error", result)
        result = run_validate("42")
        self.assertIn("must decode to a list",
                      result["error"]["reason"])

    def test_oversized_patch_rejected(self):
        with self.assertRaises(ValueError):
            run_validate([{"op": "remove", "path": "/a"}] * 1001)


class TestIsolation(unittest.TestCase):
    """The input document and patch are never mutated."""

    def test_document_never_mutated(self):
        original = {"a": {"b": [1, 2]}, "keep": True}
        snapshot = copy.deepcopy(original)
        run_apply(
            original,
            [
                {"op": "add", "path": "/a/b/-", "value": 3},
                {"op": "remove", "path": "/keep"},
                {"op": "move", "from": "/a", "path": "/c"},
            ],
        )
        self.assertEqual(original, snapshot)

    def test_patch_values_never_aliased(self):
        patch = [
            {"op": "add", "path": "/c", "value": {"x": 1}},
            {"op": "replace", "path": "/c/x", "value": 2},
        ]
        snapshot = copy.deepcopy(patch)
        result = run_apply({"a": 1}, patch)
        self.assertEqual(result["document"], {"a": 1, "c": {"x": 2}})
        self.assertEqual(patch, snapshot)

    def test_copy_does_not_alias_source(self):
        original = {"src": {"inner": [1]}}
        snapshot = copy.deepcopy(original)
        run_apply(
            original,
            [
                {"op": "copy", "from": "/src", "path": "dst"},
                {"op": "add", "path": "/dst/inner/-", "value": 2},
            ],
        )
        self.assertEqual(original, snapshot)


class TestToolWiring(unittest.TestCase):
    """Package wiring: export, names, deterministic metadata."""

    def test_exported_from_package(self):
        self.assertIs(DirectJsonPatchTool, JsonPatchTool)

    def test_identity_and_mode_whitelist(self):
        tool = JsonPatchTool()
        self.assertEqual(tool.name, "json_patch_tool")
        self.assertEqual(
            tool.MODES, ("apply", "diff", "validate_patch")
        )
        self.assertIn("RFC 6902", tool.description)


# --------------------------------------------------------------------- #
# Seeded document generator for the diff round-trip property
# --------------------------------------------------------------------- #

_KEY_POOL = [
    "a", "b", "c", "x", "y", "key", "with/slash", "with~tilde",
    "with space", "", "01", "m~n", "UPPER", "zażółć",
]


def _seeded_document(rng, variant):
    """Build a small random JSON document (deterministic per seed)."""
    return _seeded_value(rng, 0, variant)


def _seeded_value(rng, depth, variant):
    roll = rng.random()
    if depth >= 3 or roll < 0.35:
        pick = rng.randrange(7)
        if pick == 0:
            return rng.randrange(-1000, 1000)
        if pick == 1:
            return round(rng.uniform(-100, 100), 3)
        if pick == 2:
            return rng.choice([True, False])
        if pick == 3:
            return None
        if pick == 4:
            return ""
        return "".join(
            rng.choice("ab~/ c01\"\\ż") for _ in range(rng.randrange(0, 8))
        )
    if roll < 0.7:
        obj = {}
        for _ in range(rng.randrange(0, 5)):
            key = rng.choice(_KEY_POOL) + ("" if variant == 0 else "")
            obj[key] = _seeded_value(rng, depth + 1, variant)
        return obj
    array = []
    for _ in range(rng.randrange(0, 6)):
        array.append(_seeded_value(rng, depth + 1, variant))
    return array


def _deep_equal(a, b):
    """Test-side JSON equality (deliberately independent of the tool)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return set(a) == set(b) and all(
            _deep_equal(a[k], b[k]) for k in a
        )
    if isinstance(a, list):
        return len(a) == len(b) and all(
            _deep_equal(x, y) for x, y in zip(a, b)
        )
    return a == b


if __name__ == "__main__":
    unittest.main()
