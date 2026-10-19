#!/usr/bin/env python3

import json
import unittest
from pathlib import Path

import yaml

from agentuniverse.agent.action.tool.common_tool.version_range_tool import (
    VersionRangeTool,
    compare_versions,
    evaluate,
    parse_constraint,
    parse_version,
    select_latest,
    sort_versions,
)

ASCENDING = [
    "0.9.9",
    "1.0.0-0",
    "1.0.0-1",
    "1.0.0-1.2",
    "1.0.0-2",
    "1.0.0-10",
    "1.0.0-alpha",
    "1.0.0-alpha.1",
    "1.0.0-beta",
    "1.0.0-rc",
    "1.0.0",
]

PARSE_OK = [
    ("1.2.3", (1, 2, 3, None)),
    ("0.0.0", (0, 0, 0, None)),
    ("10.20.30", (10, 20, 30, None)),
    ("01.02.03", (1, 2, 3, None)),
    ("1.2.3-0", (1, 2, 3, (0,))),
    ("1.2.3-1.2.3", (1, 2, 3, (1, 2, 3))),
    ("1.2.3-rc.1", (1, 2, 3, ("rc", 1))),
    ("1.2.3-RC.1", (1, 2, 3, ("rc", 1))),
    ("1.2.3-ALPHA", (1, 2, 3, ("alpha",))),
    ("1.2.3-x8", (1, 2, 3, ("x8",))),
    ("1.2.3-a.b.7", (1, 2, 3, ("a", "b", 7))),
    ("1.2.3-rc.1.extra", (1, 2, 3, ("rc", 1, "extra"))),
]

PARSE_BAD = [
    None,
    12,
    "",
    "1",
    "1.2",
    "1.2.3.4",
    "v1.2.3",
    "1.2.3+build",
    "1.2.3-",
    "1.2.3-.",
    "1.2.3-rc..1",
    " 1.2.3",
    "1.2.3 ",
]

RELATION_PAIRS = [
    ("1.9.9", "1.10.0", -1),
    ("1.10.0", "1.9.9", 1),
    ("1.2.3", "1.2.3", 0),
    ("1.2.3", "1.2.3-rc.1", 1),
    ("1.2.3-rc.1", "1.2.3", -1),
    ("1.2.3-rc.1", "1.2.3-rc.1", 0),
    ("1.2.3-RC.1", "1.2.3-rc.1", 0),
    ("1.2.3-2", "1.2.3-10", -1),
    ("1.2.3-1", "1.2.3-beta", -1),
    ("1.2.3-rc.1", "1.2.3-rc.2", -1),
]

NO_PRERELEASE_PAIRS = [
    ("1.2.3-rc.1", "1.2.3-beta", 0),
    ("1.2.3-rc.1", "1.2.3", 0),
    ("1.2.3", "1.2.3-9", 0),
    ("1.2.3-rc.1", "1.2.4-rc.1", -1),
    ("1.2.4-rc.1", "1.2.3-rc.1", 1),
]

CHECK_TRUTH = [
    (">=1.2.0, <2.0.0, !=1.5.0", "1.5.0", False, ["!=1.5.0"]),
    (">=1.2.0, <2.0.0, !=1.5.0", "1.5.2", True, []),
    (">=1.2.0, <2.0.0, !=1.5.0", "0.9.0", False, [">=1.2.0"]),
    (">=1.2.0, <2.0.0, !=1.5.0", "2.0.0", False, ["<2.0.0"]),
    (">1.5.0", "1.5.0", False, [">1.5.0"]),
    (">=1.5.0", "1.5.0", True, []),
    ("<1.5.0", "1.5.0", False, ["<1.5.0"]),
    ("<=1.5.0", "1.5.0", True, []),
    ("==1.5.0", "1.5.0", True, []),
    ("!=1.5.0", "1.5.1", True, []),
    ("1.5.0", "1.5.0", True, []),
    ("1.5.1", "1.5.0", False, ["==1.5.1"]),
    ("", "1.2.3", True, []),
]

CONSTRAINT_BAD = [
    None,
    1,
    "1.2",
    "1.2.3,",
    ",1.2.3",
    "1.2.3,,1.3.0",
    ">>1.2.0",
    "> =1.2.0",
    "=>1.2.0",
    ">= 1.2 .0",
    "!=1.2.3-",
]

VERSIONS_ASC = ["1.10.0", "1.9.9", "1.2.3", "1.02.3", "0.9.0", "1.0.0-rc.1", "1.0.0"]

SORT_BAD = [
    None,
    "1.2.3",
    [1, 2],
    [None],
    [1.2],
    [["1.2.3"]],
]


def repo_root() -> Path:
    """Locate the repository root by walking up to the pyproject.toml."""
    probe = Path(__file__).resolve()
    for _step in range(10):
        if (probe / "pyproject.toml").is_file():
            return probe
        probe = probe.parent
    raise AssertionError("repository root not found")


class TestParseVersion(unittest.TestCase):
    def test_known_versions_parse(self):
        for text, expected in PARSE_OK:
            with self.subTest(text=text):
                self.assertEqual(parse_version(text), expected)

    def test_malformed_versions_raise(self):
        for text in PARSE_BAD:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_version(text)

    def test_parsed_versions_render_back(self):
        for text, _expected in PARSE_OK:
            with self.subTest(text=text):
                from agentuniverse.agent.action.tool.common_tool.version_range_tool import _render

                parsed = parse_version(text)
                self.assertEqual(parse_version(_render(parsed)), parsed)


class TestCompareVersions(unittest.TestCase):
    def test_ladder_is_totally_ordered(self):
        for i, low in enumerate(ASCENDING):
            for high in ASCENDING[i + 1:]:
                with self.subTest(low=low, high=high):
                    self.assertEqual(compare_versions(low, high), -1)
                    self.assertEqual(compare_versions(high, low), 1)

    def test_adjacent_relations(self):
        for left, right, expected in RELATION_PAIRS:
            with self.subTest(left=left, right=right):
                self.assertEqual(compare_versions(left, right), expected)

    def test_no_prerelease_mode_collapses_triples(self):
        for left, right, expected in NO_PRERELEASE_PAIRS:
            with self.subTest(left=left, right=right):
                self.assertEqual(compare_versions(left, right, include_prerelease=False), expected)

    def test_antisymmetry_over_the_pool(self):
        for one in ASCENDING:
            for two in ASCENDING:
                forward = compare_versions(one, two)
                backward = compare_versions(two, one)
                with self.subTest(one=one, two=two):
                    self.assertEqual(forward, -backward)

    def test_malformed_inputs_raise(self):
        with self.assertRaises(ValueError):
            compare_versions("1.2", "1.2.3")
        with self.assertRaises(ValueError):
            compare_versions("1.2.3", "1.2.3+")


class TestConstraintAndCheck(unittest.TestCase):
    def test_parse_known_constraints(self):
        parsed = parse_constraint(">=1.2.0, <2.0.0, !=1.5.0")
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0][0], ">=")
        self.assertEqual(parsed[0][1], (1, 2, 0, None))
        self.assertEqual(parsed[1][0], "<")
        self.assertEqual(parsed[2][0], "!=")
        self.assertEqual(parse_constraint(""), [])
        self.assertEqual(parse_constraint("1.2.3"), [("==", (1, 2, 3, None))])
        self.assertEqual(parse_constraint(">=1.0.0,>=1.3.0"), [
            (">=", (1, 0, 0, None)),
            (">=", (1, 3, 0, None)),
        ])

    def test_parse_bounds(self):
        twelve = ">=1.0.0," * 11 + ">=1.0.0"
        self.assertEqual(len(parse_constraint(twelve)), 12)
        thirteen = twelve + ",<2.0.0"
        with self.assertRaises(ValueError):
            parse_constraint(thirteen)
        with self.assertRaises(ValueError):
            parse_constraint("1" * 241)

    def test_parse_malformed(self):
        for text in CONSTRAINT_BAD:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_constraint(text)

    def test_evaluate_truth_table(self):
        for constraint, version, satisfied, mismatches in CHECK_TRUTH:
            with self.subTest(constraint=constraint, version=version):
                got_satisfied, got_mismatches = evaluate(parse_constraint(constraint), version)
                self.assertEqual(got_satisfied, satisfied)
                self.assertEqual(got_mismatches, mismatches)

    def test_evaluate_prerelease_modes(self):
        comparators = parse_constraint(">=1.2.3")
        self.assertEqual(evaluate(comparators, "1.2.3-rc.1"), (False, [">=1.2.3"]))
        self.assertEqual(
            evaluate(comparators, "1.2.3-rc.1", include_prerelease=False),
            (True, []),
        )


class TestSortVersions(unittest.TestCase):
    def test_sorts_numerically_not_lexically(self):
        ordered, duplicates = sort_versions(["1.10.0", "1.9.9", "1.2.3"])
        self.assertEqual(ordered, ["1.2.3", "1.9.9", "1.10.0"])
        self.assertEqual(duplicates, 0)

    def test_sorts_the_mixed_pool_ascending(self):
        ordered, duplicates = sort_versions(VERSIONS_ASC)
        self.assertEqual(ordered, [
            "0.9.0",
            "1.0.0-rc.1",
            "1.0.0",
            "1.2.3",
            "1.02.3",
            "1.9.9",
            "1.10.0",
        ])
        self.assertEqual(duplicates, 0)

    def test_duplicates_are_counted_and_dropped(self):
        ordered, duplicates = sort_versions(["1.2.3", "1.2.3", "1.9.9", "1.2.3"])
        self.assertEqual(ordered, ["1.2.3", "1.9.9"])
        self.assertEqual(duplicates, 2)

    def test_equal_spellings_keep_input_order(self):
        ordered, duplicates = sort_versions(["1.2.3", "1.02.3"])
        self.assertEqual(ordered, ["1.2.3", "1.02.3"])
        self.assertEqual(duplicates, 0)

    def test_prerelease_mode_switches_order(self):
        listed = ["1.0.0", "1.0.0-rc.1"]
        self.assertEqual(sort_versions(listed, include_prerelease=True)[0], ["1.0.0-rc.1", "1.0.0"])
        self.assertEqual(sort_versions(listed, include_prerelease=False)[0], ["1.0.0", "1.0.0-rc.1"])

    def test_sort_is_idempotent(self):
        once, duplicates = sort_versions(VERSIONS_ASC * 3)
        self.assertEqual(duplicates, 14)
        twice, _ = sort_versions(once)
        self.assertEqual(once, twice)

    def test_sort_bounds_and_malformed(self):
        with self.assertRaises(ValueError):
            sort_versions(["1.2.3"] * 201)
        for listed in SORT_BAD:
            with self.subTest(listed=listed):
                with self.assertRaises(ValueError):
                    sort_versions(listed)

    def test_empty_and_missing_lists_sort_to_nothing(self):
        self.assertEqual(sort_versions([]), ([], 0))


class TestSelectLatest(unittest.TestCase):
    def test_selects_the_greatest_satisfying_version(self):
        selected, count = select_latest(["1.2.3", "1.10.0", "1.9.9"], parse_constraint(">=1.0.0"))
        self.assertEqual(selected, "1.10.0")
        self.assertEqual(count, 3)

    def test_counts_only_satisfying_distinct_versions(self):
        selected, count = select_latest(
            ["1.2.3", "1.2.3", "0.9.0"], parse_constraint(">=1.0.0"))
        self.assertEqual(selected, "1.2.3")
        self.assertEqual(count, 1)

    def test_returns_none_when_nothing_satisfies(self):
        selected, count = select_latest(["0.9.0"], parse_constraint(">=1.0.0"))
        self.assertIsNone(selected)
        self.assertEqual(count, 0)

    def test_empty_constraint_satisfies_everything(self):
        selected, count = select_latest(["1.2.3", "1.10.0"], [])
        self.assertEqual(selected, "1.10.0")
        self.assertEqual(count, 2)

    def test_released_outranks_its_prerelease(self):
        selected, count = select_latest(["1.0.0-rc.1", "1.0.0"], [])
        self.assertEqual(selected, "1.0.0")
        self.assertEqual(count, 2)

    def test_no_prerelease_mode_picks_the_prelaunch(self):
        selected, count = select_latest(
            ["1.0.0-rc.1"], [], include_prerelease=False)
        self.assertEqual(selected, "1.0.0-rc.1")
        self.assertEqual(count, 1)

    def test_latest_honors_the_limit(self):
        with self.assertRaises(ValueError):
            select_latest(["1.2.3"] * 201, [])


class TestToolExecute(unittest.TestCase):
    def setUp(self):
        self.tool = VersionRangeTool()

    def test_check_reports_comparators_and_mismatches(self):
        result = self.tool.execute(action="check", constraint=">=1.2.0, <2.0.0", version="1.5.2")
        self.assertEqual(result["action"], "check")
        self.assertTrue(result["satisfied"])
        self.assertEqual(result["comparators"], [">=1.2.0", "<2.0.0"])
        self.assertEqual(result["mismatches"], [])
        self.assertTrue(isinstance(self.tool.default_include_prerelease, bool))

    def test_compare_returns_relation(self):
        self.assertEqual(self.tool.execute(action="compare", version="1.9.9", other="1.10.0")["relation"], -1)
        self.assertEqual(self.tool.execute(action="compare", version="2.0.0", other="1.9.9")["relation"], 1)
        self.assertEqual(self.tool.execute(action="compare", version="1.2.3", other="1.2.3")["relation"], 0)

    def test_sort_shape(self):
        result = self.tool.execute(action="sort", versions=["1.10.0", "1.9.9", "1.2.3", "1.9.9"])
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["unique"], 3)
        self.assertEqual(result["duplicates"], 1)
        self.assertEqual(result["sorted"], ["1.2.3", "1.9.9", "1.10.0"])

    def test_sort_treats_missing_list_as_empty(self):
        result = self.tool.execute(action="sort")
        self.assertEqual((result["count"], result["unique"], result["duplicates"]), (0, 0, 0))

    def test_latest_shape(self):
        result = self.tool.execute(action="latest", constraint=">=1.0.0", versions=["1.2.3", "1.10.0", "1.9.9"])
        self.assertEqual(result["selected"], "1.10.0")
        self.assertEqual(result["satisfied_count"], 3)
        self.assertEqual(result["pool"], 3)
        self.assertEqual(result["comparators"], [">=1.0.0"])

    def test_latest_none_is_json_null(self):
        result = self.tool.execute(action="latest", constraint=">=2.0.0", versions=["1.2.3"])
        self.assertIsNone(result["selected"])
        self.assertIn("null", json.dumps(result))
        payload = json.loads(json.dumps(result))
        self.assertIsNone(payload["selected"])

    def test_check_empty_constraint_satisfies(self):
        result = self.tool.execute(action="check", constraint="", version="1.2.3")
        self.assertTrue(result["satisfied"])
        self.assertEqual(result["comparators"], [])

    def test_unknown_action_raises(self):
        with self.assertRaises(ValueError):
            self.tool.execute(action="derive")

    def test_malformed_inputs_raise(self):
        with self.assertRaises(ValueError):
            self.tool.execute(action="check", constraint=">=1.0.0", version="1.2")
        with self.assertRaises(ValueError):
            self.tool.execute(action="check", constraint="1.2.3,", version="1.2.3")
        with self.assertRaises(ValueError):
            self.tool.execute(action="compare", version="1.2.3")
        with self.assertRaises(ValueError):
            self.tool.execute(action="sort", versions=["1.2.3"] * 201)
        with self.assertRaises(ValueError):
            self.tool.execute(action="latest", constraint="1" * 241, versions=["1.2.3"])

    def test_prerelease_flag_matrix(self):
        base = {"action": "check", "constraint": ">=1.2.3", "version": "1.2.3-rc.1"}
        self.assertFalse(self.tool.execute(**base)["satisfied"])
        self.assertTrue(self.tool.execute(include_prerelease=False, **base)["satisfied"])
        strict = VersionRangeTool(default_include_prerelease=False)
        self.assertTrue(strict.execute(**base)["satisfied"])
        self.assertFalse(strict.execute(include_prerelease=True, **base)["satisfied"])


class TestConfigShape(unittest.TestCase):
    def test_component_yaml_matches_the_module(self):
        root = repo_root()
        module_path = root / "agentuniverse" / "agent" / "action" / "tool" / "common_tool" / "version_range_tool.py"
        yaml_path = root / "examples" / "sample_standard_app" / "intelligence" / "agentic" / "tool" / "buildin" / "version_range_tool.yaml"
        self.assertTrue(module_path.is_file())
        self.assertTrue(yaml_path.is_file())
        with open(yaml_path, "r", encoding="utf-8") as stream:
            loaded = yaml.safe_load(stream)
        self.assertEqual(loaded["name"], "version_range_tool")
        self.assertEqual(loaded["tool_type"], "func")
        self.assertEqual(loaded["input_keys"], ["action"])
        self.assertEqual(loaded["metadata"]["type"], "TOOL")
        self.assertEqual(loaded["metadata"]["module"], "agentuniverse.agent.action.tool.common_tool.version_range_tool")
        self.assertEqual(VersionRangeTool.__module__, loaded["metadata"]["module"])
        self.assertIn("network", loaded["description"])
        self.assertIn("ValueError", loaded["description"])


if __name__ == "__main__":
    unittest.main()
