#!/usr/bin/env python3

"""Tests for the built-in CSVQueryTool."""

import os
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import csv_query_tool as csv_module
from agentuniverse.agent.action.tool.common_tool.csv_query_tool import CSVQueryTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)
from agentuniverse.base.config.component_configer.configers.tool_configer import (
    ToolConfiger,
)
from agentuniverse.base.config.configer import Configer

CSV_TEXT = (
    "name,city,age,salary\n"
    "Alice,Beijing,30,8000\n"
    "Bob,Shanghai,25,6500\n"
    "Carol,Beijing,35,12000\n"
    "Dave,Hangzhou,28,\n"
    "Eve,,41,9000\n"
)


class TestCSVQuerySelect(unittest.TestCase):
    """Parsing and SELECT projection."""

    def setUp(self) -> None:
        self.tool = CSVQueryTool()

    def test_select_all(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT)
        self.assertEqual(result["columns"], ["name", "city", "age", "salary"])
        self.assertEqual(result["row_count"], 5)
        self.assertEqual(result["rows"][0], ["Alice", "Beijing", "30", "8000"])

    def test_select_subset_string(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, select="name, age")
        self.assertEqual(result["columns"], ["name", "age"])
        self.assertEqual(result["rows"][1], ["Bob", "25"])

    def test_select_subset_list_and_reorder(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, select=["age", "name"])
        self.assertEqual(result["columns"], ["age", "name"])
        self.assertEqual(result["rows"][0], ["30", "Alice"])

    def test_select_case_insensitive_column(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, select="NAME")
        self.assertEqual(result["columns"], ["name"])
        self.assertEqual(result["row_count"], 5)

    def test_quoted_fields_with_commas(self) -> None:
        text = 'id,note\n1,"hello, world"\n2,"multi"\n'
        result = self.tool.execute(csv_text=text)
        self.assertEqual(result["rows"][0], ["1", "hello, world"])

    def test_bom_is_stripped(self) -> None:
        result = self.tool.execute(csv_text="\ufeffname,age\nAlice,30\n")
        self.assertEqual(result["columns"], ["name", "age"])

    def test_short_rows_are_padded(self) -> None:
        text = "a,b,c\n1,2\n"
        result = self.tool.execute(csv_text=text)
        self.assertEqual(result["rows"][0], ["1", "2", ""])


class TestCSVQueryWhere(unittest.TestCase):
    """WHERE filtering operators."""

    def setUp(self) -> None:
        self.tool = CSVQueryTool()

    def test_where_eq_quoted(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="city = 'Beijing'")
        self.assertEqual(result["row_count"], 2)
        self.assertEqual([row[0] for row in result["rows"]], ["Alice", "Carol"])

    def test_where_eq_unquoted(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="city = Beijing")
        self.assertEqual(result["row_count"], 2)

    def test_where_not_eq(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="city != Beijing")
        self.assertEqual([row[0] for row in result["rows"]], ["Bob", "Dave", "Eve"])

    def test_where_angle_bracket_alias(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="city <> Beijing")
        self.assertEqual(result["row_count"], 3)

    def test_where_numeric_comparisons(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="age >= 30")
        self.assertEqual([row[0] for row in result["rows"]], ["Alice", "Carol", "Eve"])
        result = self.tool.execute(csv_text=CSV_TEXT, where="age < 30")
        self.assertEqual([row[0] for row in result["rows"]], ["Bob", "Dave"])
        result = self.tool.execute(csv_text=CSV_TEXT, where="age > 35")
        self.assertEqual([row[0] for row in result["rows"]], ["Eve"])
        result = self.tool.execute(csv_text=CSV_TEXT, where="age <= 25")
        self.assertEqual([row[0] for row in result["rows"]], ["Bob"])

    def test_where_numeric_not_lexicographic(self) -> None:
        text = "n\n9\n10\n100\n"
        result = self.tool.execute(csv_text=text, where="n > 9")
        self.assertEqual([row[0] for row in result["rows"]], ["10", "100"])

    def test_where_string_comparison(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="name > 'Carol'")
        self.assertEqual([row[0] for row in result["rows"]], ["Dave", "Eve"])

    def test_where_like_wildcards(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="name LIKE 'A%'")
        self.assertEqual([row[0] for row in result["rows"]], ["Alice"])
        result = self.tool.execute(csv_text=CSV_TEXT, where="name LIKE '%e'")
        self.assertEqual([row[0] for row in result["rows"]], ["Alice", "Dave", "Eve"])
        result = self.tool.execute(csv_text=CSV_TEXT, where="name LIKE '%a%'")
        # LIKE is case-insensitive, so 'Alice' matches '%a%' through 'A'.
        self.assertEqual([row[0] for row in result["rows"]], ["Alice", "Carol", "Dave"])
        result = self.tool.execute(csv_text=CSV_TEXT, where="name LIKE '_ob'")
        self.assertEqual([row[0] for row in result["rows"]], ["Bob"])

    def test_where_like_is_case_insensitive(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="name LIKE 'alice'")
        self.assertEqual([row[0] for row in result["rows"]], ["Alice"])

    def test_where_not_like(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="name NOT LIKE 'A%'")
        self.assertEqual(result["row_count"], 4)

    def test_where_in(self) -> None:
        result = self.tool.execute(
            csv_text=CSV_TEXT, where="city IN ('Beijing', 'Hangzhou')"
        )
        self.assertEqual([row[0] for row in result["rows"]], ["Alice", "Carol", "Dave"])

    def test_where_not_in(self) -> None:
        result = self.tool.execute(
            csv_text=CSV_TEXT, where="city NOT IN ('Beijing', 'Hangzhou')"
        )
        self.assertEqual([row[0] for row in result["rows"]], ["Bob", "Eve"])

    def test_where_multiple_conditions_and(self) -> None:
        result = self.tool.execute(
            csv_text=CSV_TEXT, where="city = Beijing AND age > 32"
        )
        self.assertEqual([row[0] for row in result["rows"]], ["Carol"])

    def test_where_list_is_anded(self) -> None:
        result = self.tool.execute(
            csv_text=CSV_TEXT, where=["city = Beijing", "age < 32"]
        )
        self.assertEqual([row[0] for row in result["rows"]], ["Alice"])


class TestCSVQueryOrderByLimit(unittest.TestCase):
    """ORDER BY and LIMIT clauses."""

    def setUp(self) -> None:
        self.tool = CSVQueryTool()

    def test_order_by_default_asc(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, order_by="age")
        self.assertEqual([row[0] for row in result["rows"]], ["Bob", "Dave", "Alice", "Carol", "Eve"])

    def test_order_by_desc(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, order_by="age DESC")
        self.assertEqual(result["rows"][0][0], "Eve")
        self.assertEqual(result["rows"][-1][0], "Bob")

    def test_order_by_numeric_not_lexicographic(self) -> None:
        text = "n\n10\n9\n100\n"
        result = self.tool.execute(csv_text=text, order_by="n")
        self.assertEqual([row[0] for row in result["rows"]], ["9", "10", "100"])

    def test_order_by_multiple_keys(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, order_by="city ASC, age DESC")
        # Ascending city order places the empty city first, then Beijing
        # (Carol 35 before Alice 30), Hangzhou and Shanghai.
        self.assertEqual(
            [row[0] for row in result["rows"]],
            ["Eve", "Carol", "Alice", "Dave", "Bob"],
        )

    def test_limit(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, order_by="age ASC", limit=2)
        self.assertEqual(result["row_count"], 2)
        self.assertEqual([row[0] for row in result["rows"]], ["Bob", "Dave"])

    def test_limit_zero(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, limit=0)
        self.assertEqual(result["row_count"], 0)
        self.assertEqual(result["rows"], [])

    def test_limit_larger_than_result(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, limit=100)
        self.assertEqual(result["row_count"], 5)


class TestCSVQueryAggregate(unittest.TestCase):
    """Aggregation expressions."""

    def setUp(self) -> None:
        self.tool = CSVQueryTool()

    def test_count_star(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, select="COUNT(*)")
        self.assertEqual(result["columns"], ["COUNT(*)"])
        self.assertEqual(result["rows"], [[5]])

    def test_count_column_skips_empty(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, select="COUNT(salary)")
        self.assertEqual(result["rows"], [[4]])

    def test_sum_avg_min_max(self) -> None:
        result = self.tool.execute(
            csv_text=CSV_TEXT, select="SUM(salary), AVG(salary), MIN(salary), MAX(salary)"
        )
        self.assertEqual(
            result["columns"],
            ["SUM(salary)", "AVG(salary)", "MIN(salary)", "MAX(salary)"],
        )
        sum_, avg_, min_, max_ = result["rows"][0]
        self.assertEqual(sum_, 35500)
        self.assertEqual(avg_, 8875)
        self.assertEqual(min_, 6500)
        self.assertEqual(max_, 12000)

    def test_aggregate_respects_where(self) -> None:
        result = self.tool.execute(
            csv_text=CSV_TEXT, select="COUNT(*)", where="city = Beijing"
        )
        self.assertEqual(result["rows"], [[2]])

    def test_aggregate_on_empty_input_rows(self) -> None:
        text = "name,salary\nAlice,\n"
        result = self.tool.execute(csv_text=text, select="SUM(salary), COUNT(salary)")
        self.assertEqual(result["rows"], [[None, 0]])


class TestCSVQueryPipeline(unittest.TestCase):
    """Combined clauses and the run() entry point."""

    def setUp(self) -> None:
        self.tool = CSVQueryTool()

    def test_where_select_order_limit_pipeline(self) -> None:
        result = self.tool.execute(
            csv_text=CSV_TEXT,
            select="name, salary",
            where="age > 24 AND salary > 0",
            order_by="salary DESC",
            limit=3,
        )
        self.assertEqual(result["columns"], ["name", "salary"])
        self.assertEqual(
            result["rows"],
            [["Carol", "12000"], ["Eve", "9000"], ["Alice", "8000"]],
        )


class TestCSVQueryValidation(unittest.TestCase):
    """Structured error reporting and configuration budgets."""

    def setUp(self) -> None:
        self.tool = CSVQueryTool()

    def test_empty_csv_text(self) -> None:
        result = self.tool.execute(csv_text="   ")
        self.assertIn("error", result)
        self.assertIn("empty", result["error"])

    def test_non_string_csv_text(self) -> None:
        result = self.tool.execute(csv_text=12345)
        self.assertIn("must be a string", result["error"])

    def test_duplicate_columns(self) -> None:
        result = self.tool.execute(csv_text="a,a\n1,2\n")
        self.assertIn("duplicate column", result["error"])

    def test_row_longer_than_header(self) -> None:
        result = self.tool.execute(csv_text="a,b\n1,2,3\n")
        self.assertIn("fields but the header has", result["error"])

    def test_unknown_select_column(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, select="nickname")
        self.assertIn("unknown column 'nickname'", result["error"])

    def test_unknown_where_column(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="nickname = 'x'")
        self.assertIn("unknown column 'nickname'", result["error"])

    def test_malformed_where_condition(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="just-a-column")
        self.assertIn("cannot parse where condition", result["error"])

    def test_missing_where_value(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="age >")
        self.assertIn("missing value", result["error"])

    def test_in_without_value_list(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, where="city IN Beijing")
        self.assertIn("expects a value list", result["error"])

    def test_invalid_order_direction(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, order_by="age SIDEWAYS")
        self.assertIn("invalid order_by direction", result["error"])

    def test_negative_limit(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, limit=-1)
        self.assertIn("limit must be a non-negative integer", result["error"])

    def test_mixed_aggregate_and_plain_column(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, select="name, COUNT(*)")
        self.assertIn("cannot be mixed", result["error"])

    def test_star_aggregate_only_for_count(self) -> None:
        result = self.tool.execute(csv_text=CSV_TEXT, select="SUM(*)")
        self.assertIn("only supported by COUNT(*)", result["error"])

    def test_max_rows_budget(self) -> None:
        tool = CSVQueryTool(max_rows=2)
        result = tool.execute(csv_text="a\n1\n2\n3\n")
        self.assertIn("exceeds max_rows", result["error"])

    def test_max_input_chars_budget(self) -> None:
        tool = CSVQueryTool(max_input_chars=10)
        result = tool.execute(csv_text="a,b,c,d,e,f\n1,2,3,4,5,6\n")
        self.assertIn("exceeds max_input_chars", result["error"])


class TestCSVQueryRegistration(unittest.TestCase):
    """Load the shipped YAML through the real component pipeline."""

    YAML_PATH = os.path.join(os.path.dirname(csv_module.__file__), "csv_query_tool.yaml")

    def setUp(self) -> None:
        self.configer = Configer(path=os.path.abspath(self.YAML_PATH)).load()
        try:
            self.previous_app_configer = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous_app_configer = None

    def tearDown(self) -> None:
        ApplicationConfigManager().app_configer = self.previous_app_configer

    def test_yaml_resolves_to_tool_component(self) -> None:
        component = ComponentConfiger().load_by_configer(self.configer)
        self.assertEqual(
            component.get_component_config_type(),
            ComponentEnum.TOOL.value,
        )
        self.assertEqual(
            component.metadata_module,
            "agentuniverse.agent.action.tool.common_tool.csv_query_tool",
        )
        self.assertEqual(component.metadata_class, "CSVQueryTool")

    def test_tool_manager_resolves_configured_tool(self) -> None:
        tool_configer = ToolConfiger().load_by_configer(self.configer)
        app_configer = AppConfiger()
        app_configer.tool_configer_map = {tool_configer.name: tool_configer}
        ApplicationConfigManager().app_configer = app_configer

        tool = ToolManager().get_instance_obj(tool_configer.name)

        self.assertIsInstance(tool, CSVQueryTool)
        self.assertEqual(tool.name, "csv_query_tool")
        self.assertEqual(tool.input_keys, ["csv_text"])
        self.assertEqual(tool.max_input_chars, 1_000_000)
        self.assertEqual(tool.max_rows, 100_000)
        self.assertEqual(
            tool.args_model_schema["properties"]["limit"]["minimum"], 0
        )

    def test_configured_tool_executes_queries(self) -> None:
        tool_configer = ToolConfiger().load_by_configer(self.configer)
        app_configer = AppConfiger()
        app_configer.tool_configer_map = {tool_configer.name: tool_configer}
        ApplicationConfigManager().app_configer = app_configer

        tool = ToolManager().get_instance_obj(tool_configer.name)
        result = tool.execute(csv_text="a,b\n1,2\n3,4\n", where="a > 1")
        self.assertEqual(result["rows"], [["3", "4"]])


class TestCSVQueryYaml(unittest.TestCase):
    """The packaged component configuration."""

    YAML_PATH = os.path.join(os.path.dirname(csv_module.__file__), "csv_query_tool.yaml")

    def test_yaml_declares_component_metadata(self) -> None:
        with open(self.YAML_PATH, encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "csv_query_tool")
        self.assertEqual(config["metadata"]["type"], "TOOL")
        self.assertEqual(config["metadata"]["module"], "agentuniverse.agent.action.tool.common_tool.csv_query_tool")
        self.assertEqual(config["metadata"]["class"], "CSVQueryTool")
        self.assertEqual(config["input_keys"], ["csv_text"])

    def test_yaml_limits_match_defaults(self) -> None:
        with open(self.YAML_PATH, encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        tool = CSVQueryTool()
        self.assertEqual(config["max_input_chars"], tool.max_input_chars)
        self.assertEqual(config["max_rows"], tool.max_rows)


if __name__ == "__main__":
    unittest.main()
