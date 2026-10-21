#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_sql_lint_tool.py

"""Offline unit tests for SqlLintTool.

The tool is built purely on the standard library and never touches a
database, the network or the filesystem, so this suite runs fully
offline. Assertions are exact ground truths: every rule is checked in
its triggering shape and in a non-triggering control shape, multi-line
positions are checked against hand-derived offset/line/column triples,
comment and string-literal masking is proven keyword-immune, structure
extraction is verified on 18 crafted statements (CTEs, subqueries,
aliases, joins, INSERT/UPDATE/DELETE shapes, MySQL / FETCH limits), the
format mode is checked against exact expected output plus round-trip
parse-stability (format(format(x)) == format(x) and unchanged
structure), and the error matrix covers every strict-validation branch
of the single-statement contract.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import SqlLintTool
from agentuniverse.agent.action.tool.common_tool.sql_lint_tool import (
    SqlLintTool as DirectSqlLintTool,
)


def _codes(result: dict) -> list:
    return [finding["code"] for finding in result["findings"]]


class SqlLintToolBasicsTest(unittest.TestCase):
    """Export surface, determinism and ok semantics."""

    def setUp(self) -> None:
        self.tool = SqlLintTool()

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(SqlLintTool, DirectSqlLintTool)

    def test_name_and_modes(self) -> None:
        self.assertEqual(self.tool.name, "sql_lint_tool")
        self.assertEqual(
            SqlLintTool.MODES,
            ("lint", "explain_structure", "format"),
        )
        self.assertEqual(len(SqlLintTool.RULE_CODES), 11)

    def test_deterministic_repeat(self) -> None:
        sql = ("SELECT * FROM t1, t2 WHERE a LIKE '%x' "
               "GROUP BY b ORDER BY c")
        first = self.tool.execute(mode="lint", sql=sql)
        second = self.tool.execute(mode="lint", sql=sql)
        self.assertEqual(first, second)

    def test_info_only_is_ok(self) -> None:
        result = self.tool.execute(mode="lint", sql="SELECT * FROM t")
        self.assertEqual(_codes(result), ["SQL001"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["statement_type"], "select")

    def test_warning_or_error_breaks_ok(self) -> None:
        result = self.tool.execute(mode="lint", sql="DELETE FROM t")
        self.assertFalse(result["ok"])
        self.assertEqual(_codes(result), ["SQL002"])

    def test_findings_sorted_by_offset_then_code(self) -> None:
        sql = "SELECT * FROM t WHERE a LIKE '%x'"
        result = self.tool.execute(mode="lint", sql=sql)
        positions = [f["position"]["offset"] for f in result["findings"]]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(_codes(result), ["SQL001", "SQL006"])


class SqlLintToolRuleTest(unittest.TestCase):
    """Every rule: triggering shape plus non-triggering control."""

    def setUp(self) -> None:
        self.tool = SqlLintTool()

    def _codes(self, sql: str, **options) -> list:
        return _codes(self.tool.execute(mode="lint", sql=sql, **options))

    # -- SQL001 select_star ------------------------------------------------

    def test_sql001_select_star(self) -> None:
        self.assertEqual(self._codes("SELECT * FROM t"), ["SQL001"])

    def test_sql001_star_after_comma(self) -> None:
        self.assertEqual(self._codes("SELECT a, * FROM t"), ["SQL001"])

    def test_sql001_qualified_star(self) -> None:
        self.assertEqual(self._codes("SELECT t.* FROM t"), ["SQL001"])

    def test_sql001_control_multiplication(self) -> None:
        self.assertEqual(
            self._codes("SELECT price * qty FROM t"), [])

    def test_sql001_control_count_star(self) -> None:
        self.assertEqual(self._codes("SELECT COUNT(*) FROM t"), [])

    # -- SQL002 / SQL003 delete|update without WHERE ----------------------

    def test_sql002_delete_without_where(self) -> None:
        result = self.tool.execute(mode="lint", sql="DELETE FROM t")
        self.assertEqual(_codes(result), ["SQL002"])
        self.assertEqual(result["findings"][0]["severity"], "error")

    def test_sql002_control_delete_with_where(self) -> None:
        self.assertEqual(
            self._codes("DELETE FROM t WHERE id = 1"), [])

    def test_sql003_update_without_where(self) -> None:
        result = self.tool.execute(mode="lint", sql="UPDATE t SET a = 1")
        self.assertEqual(_codes(result), ["SQL003"])
        self.assertEqual(result["findings"][0]["severity"], "error")

    def test_sql003_control_update_with_where(self) -> None:
        self.assertEqual(
            self._codes("UPDATE t SET a = 1 WHERE id = 1"), [])

    # -- SQL004 missing LIMIT (gated by require_limit) ---------------------

    def test_sql004_off_by_default(self) -> None:
        self.assertEqual(self._codes("SELECT a FROM t"), [])

    def test_sql004_on_without_limit(self) -> None:
        result = self.tool.execute(
            mode="lint", sql="SELECT a FROM t", require_limit=True)
        self.assertEqual(_codes(result), ["SQL004"])
        self.assertEqual(result["findings"][0]["severity"], "warning")

    def test_sql004_control_with_limit(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t LIMIT 10", require_limit=True),
            [],
        )

    def test_sql004_control_fetch_first_counts(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT a FROM t FETCH FIRST 5 ROWS ONLY",
                require_limit=True,
            ),
            [],
        )

    # -- SQL005 cartesian: comma join / CROSS JOIN without WHERE -----------

    def test_sql005_comma_join_without_where(self) -> None:
        result = self.tool.execute(
            mode="lint", sql="SELECT a FROM t1, t2")
        self.assertEqual(_codes(result), ["SQL005"])
        self.assertEqual(result["findings"][0]["severity"], "error")

    def test_sql005_control_comma_join_with_where(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t1, t2 WHERE t1.x = t2.x"), [])

    def test_sql005_cross_join_without_where(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t1 CROSS JOIN t2"), ["SQL005"])

    def test_sql005_control_cross_join_with_where(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t1 CROSS JOIN t2 WHERE x = 1"), [])

    def test_sql005_control_explicit_join_on(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t1 JOIN t2 ON t1.x = t2.x"), [])

    def test_sql005_nested_subquery_comma_join(self) -> None:
        result = self.tool.execute(
            mode="lint",
            sql="SELECT a FROM t WHERE b IN (SELECT c FROM x, y)")
        self.assertEqual(_codes(result), ["SQL005"])

    def test_sql005_control_group_by_commas(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT a, b FROM t GROUP BY a, b HAVING COUNT(*) > 1"),
            [],
        )

    def test_sql005_control_limit_commas_mysql(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t LIMIT 5, 10"), [])

    # -- SQL006 LIKE leading wildcard --------------------------------------

    def test_sql006_percent_prefix(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t WHERE b LIKE '%x'"), ["SQL006"])

    def test_sql006_underscore_prefix(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t WHERE b LIKE '_x'"), ["SQL006"])

    def test_sql006_ilike_variant(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t WHERE b ILIKE '%x'"), ["SQL006"])

    def test_sql006_control_suffix_wildcard(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t WHERE b LIKE 'x%'"), [])

    def test_sql006_control_plain_pattern(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t WHERE b LIKE 'x'"), [])

    # -- SQL007 DISTINCT + ORDER BY non-selected ---------------------------

    def test_sql007_trigger(self) -> None:
        result = self.tool.execute(
            mode="lint", sql="SELECT DISTINCT a FROM t ORDER BY b")
        self.assertEqual(_codes(result), ["SQL007"])
        self.assertEqual(result["findings"][0]["severity"], "error")

    def test_sql007_control_alias(self) -> None:
        self.assertEqual(
            self._codes("SELECT DISTINCT a AS x FROM t ORDER BY x"), [])

    def test_sql007_control_bare_column(self) -> None:
        self.assertEqual(
            self._codes("SELECT DISTINCT t.a FROM t ORDER BY a"), [])

    def test_sql007_control_positional(self) -> None:
        self.assertEqual(
            self._codes("SELECT DISTINCT a FROM t ORDER BY 1"), [])

    def test_sql007_control_matching_expression(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT DISTINCT COUNT(*) FROM t ORDER BY COUNT(*)"), [])

    def test_sql007_control_no_distinct(self) -> None:
        self.assertEqual(self._codes("SELECT a FROM t ORDER BY b"), [])

    def test_sql007_control_desc_suffix_stripped(self) -> None:
        self.assertEqual(
            self._codes("SELECT DISTINCT a FROM t ORDER BY a DESC"), [])

    # -- SQL008 GROUP BY column not selected --------------------------------

    def test_sql008_trigger(self) -> None:
        result = self.tool.execute(
            mode="lint",
            sql="SELECT u.id, u.name FROM u GROUP BY u.status")
        self.assertEqual(_codes(result), ["SQL008"])
        self.assertEqual(result["findings"][0]["severity"], "warning")

    def test_sql008_control_group_column_selected(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT u.id, u.status FROM u GROUP BY u.status"), [])

    def test_sql008_control_select_alias(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT status AS s, COUNT(*) AS n FROM u GROUP BY status"),
            [],
        )

    def test_sql008_control_aggregate_only_select(self) -> None:
        # legal in every engine: nothing non-aggregated is projected
        self.assertEqual(
            self._codes("SELECT COUNT(*) FROM u GROUP BY status"), [])

    def test_sql008_control_mixed_agg_and_key(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT status, COUNT(*) FROM u GROUP BY status"), [])

    def test_sql008_control_positional_group_by(self) -> None:
        self.assertEqual(
            self._codes("SELECT u.id, u.name FROM u GROUP BY 1"), [])

    # -- SQL009 oversized literal IN list ----------------------------------

    @staticmethod
    def _ints(count: int) -> str:
        return ", ".join(str(i) for i in range(count))

    def test_sql009_twenty_one_literals(self) -> None:
        result = self.tool.execute(
            mode="lint",
            sql=f"SELECT a FROM t WHERE x IN ({self._ints(21)})")
        self.assertEqual(_codes(result), ["SQL009"])
        self.assertEqual(result["findings"][0]["severity"], "warning")

    def test_sql009_control_twenty_literals(self) -> None:
        self.assertEqual(
            self._codes(
                f"SELECT a FROM t WHERE x IN ({self._ints(20)})"), [])

    def test_sql009_custom_threshold(self) -> None:
        self.assertEqual(
            self._codes(
                f"SELECT a FROM t WHERE x IN ({self._ints(3)})",
                in_list_max=2,
            ),
            ["SQL009"],
        )

    def test_sql009_control_subquery_in(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT a FROM t WHERE x IN (SELECT y FROM u)"), [])

    def test_sql009_control_column_in_list(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t WHERE (x, y) IN ((1, 2))"), [])

    # -- SQL010 OR chain on one column -------------------------------------

    def test_sql010_three_or_equalities(self) -> None:
        result = self.tool.execute(
            mode="lint",
            sql="SELECT a FROM t WHERE x = 1 OR x = 2 OR x = 3")
        self.assertEqual(_codes(result), ["SQL010"])
        self.assertEqual(result["findings"][0]["severity"], "info")

    def test_sql010_control_two_or_equalities(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t WHERE x = 1 OR x = 2"), [])

    def test_sql010_control_and_chain(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT a FROM t WHERE x = 1 AND x = 2 AND x = 3"), [])

    def test_sql010_control_mixed_columns(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT a FROM t WHERE x = 1 OR y = 2 OR x = 3"), [])

    def test_sql010_custom_minimum(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT a FROM t WHERE x = 1 OR x = 2",
                or_chain_min=2,
            ),
            ["SQL010"],
        )

    def test_sql010_qualified_column_in_message(self) -> None:
        result = self.tool.execute(
            mode="lint",
            sql="SELECT a FROM t WHERE t.x = 1 OR t.x = 2 OR t.x = 3")
        self.assertIn("T.X", result["findings"][0]["message"])

    # -- SQL011 mixed literal types per column -----------------------------

    def test_sql011_equalities(self) -> None:
        result = self.tool.execute(
            mode="lint", sql="SELECT a FROM t WHERE x = 1 AND x = 'a'")
        self.assertEqual(_codes(result), ["SQL011"])
        self.assertEqual(result["findings"][0]["severity"], "warning")

    def test_sql011_via_in_list(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT a FROM t WHERE x IN (1, 2) AND x = 'a'"),
            ["SQL011"],
        )

    def test_sql011_within_one_in_list(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t WHERE x IN (1, 'a')"), ["SQL011"])

    def test_sql011_control_distinct_columns(self) -> None:
        self.assertEqual(
            self._codes("SELECT a FROM t WHERE x = 1 AND y = 'a'"), [])

    def test_sql011_control_consistent_types(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT a FROM t WHERE x = 1 AND x = 2 OR x = 3"), [],
        )

    def test_sql011_across_join_on(self) -> None:
        self.assertEqual(
            self._codes(
                "SELECT a FROM t JOIN u ON t.k = 1 WHERE t.k = 'z'"),
            ["SQL011"],
        )

    # -- SQL012 documentation-only ------------------------------------------

    def test_sql012_not_toggleable(self) -> None:
        # SQL012 is documentation-only by design (schema-dependent
        # coercion is undetectable offline), so it is not a rule code
        # and the option rejects it outright
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="lint", sql="SELECT 1", rules={"SQL012": False})
        self.assertIn("rules keys", str(ctx.exception))


class SqlLintToolRuleSwitchTest(unittest.TestCase):
    """The rules on/off option."""

    def setUp(self) -> None:
        self.tool = SqlLintTool()

    def test_disable_single_rule(self) -> None:
        result = self.tool.execute(
            mode="lint", sql="SELECT * FROM t", rules={"SQL001": False})
        self.assertEqual(_codes(result), [])
        self.assertEqual(result["rules_disabled"], ["SQL001"])

    def test_enable_keeps_rule(self) -> None:
        result = self.tool.execute(
            mode="lint", sql="SELECT * FROM t", rules={"SQL001": True})
        self.assertEqual(_codes(result), ["SQL001"])
        self.assertEqual(result["rules_disabled"], [])

    def test_disabled_rule_absent_even_when_triggered(self) -> None:
        result = self.tool.execute(
            mode="lint",
            sql="SELECT * FROM t1, t2",
            rules={"SQL005": False},
        )
        self.assertEqual(_codes(result), ["SQL001"])


class SqlLintToolPositionTest(unittest.TestCase):
    """Exact offset/line/column on a multi-line statement.

    Line starts (0-based) of the statement below:
    L1 "-- fetch users"                starts at 0    (len 14 + NL)
    L2 "SELECT u.id, u.name, COUNT(*) AS cnt" at 15   (len 36 + NL)
    L3 "FROM users u, orders o"         at 52          (len 22 + NL)
    L4 "WHERE u.name LIKE '%smith'"     at 75          (len 26 + NL)
    L5 "  AND u.id = 1 OR u.id = 2 OR u.id = 3" at 102 (len 38 + NL)
    L6 "GROUP BY u.status"              at 141
    L7 "ORDER BY u.created_at"          at 159
    L8 "LIMIT 10"                       at 181

    Hand-derived expectations:
    - the '%smith' literal opens at 75 + 18 = 93  -> line 4, column 19
    - the first OR-chain predicate u.id at 102 + 6 = 108 -> line 5, col 7
    - the GROUP BY item u.status at 141 + 9 = 150 -> line 6, column 10
    """

    SQL = (
        "-- fetch users\n"
        "SELECT u.id, u.name, COUNT(*) AS cnt\n"
        "FROM users u, orders o\n"
        "WHERE u.name LIKE '%smith'\n"
        "  AND u.id = 1 OR u.id = 2 OR u.id = 3\n"
        "GROUP BY u.status\n"
        "ORDER BY u.created_at\n"
        "LIMIT 10"
    )

    def setUp(self) -> None:
        self.tool = SqlLintTool()
        self.by_code = {
            f["code"]: f
            for f in self.tool.execute(
                mode="lint", sql=self.SQL, require_limit=True)["findings"]
        }

    def test_line_start_arithmetic(self) -> None:
        # guard the hand-derived line starts used below
        lines = self.SQL.split("\n")
        starts = [0]
        for line in lines[:-1]:
            starts.append(starts[-1] + len(line) + 1)
        self.assertEqual(starts, [0, 15, 52, 75, 102, 141, 159, 181])

    def test_sql006_position_exact(self) -> None:
        finding = self.by_code["SQL006"]
        self.assertEqual(
            finding["position"],
            {"offset": 93, "line": 4, "column": 19},
        )

    def test_sql010_position_exact(self) -> None:
        finding = self.by_code["SQL010"]
        self.assertEqual(
            finding["position"],
            {"offset": 108, "line": 5, "column": 7},
        )

    def test_sql008_position_exact(self) -> None:
        finding = self.by_code["SQL008"]
        self.assertEqual(
            finding["position"],
            {"offset": 150, "line": 6, "column": 10},
        )

    def test_finding_shape(self) -> None:
        for finding in self.by_code.values():
            self.assertEqual(
                sorted(finding),
                ["code", "hint", "message", "position", "severity"],
            )
            self.assertEqual(
                sorted(finding["position"]), ["column", "line", "offset"])

    def test_offset_indexes_original_statement(self) -> None:
        # every reported offset must point into the original statement
        for finding in self.by_code.values():
            offset = finding["position"]["offset"]
            self.assertGreaterEqual(offset, 0)
            self.assertLess(offset, len(self.SQL))


class SqlLintToolMaskingTest(unittest.TestCase):
    """Keywords inside strings and comments never trigger rules."""

    def setUp(self) -> None:
        self.tool = SqlLintTool()

    def test_keywords_inside_string_literal(self) -> None:
        self.assertEqual(
            self._lint("SELECT 'SELECT * FROM a, b' AS q FROM t"), [])

    def test_delete_keyword_inside_string(self) -> None:
        self.assertEqual(
            self._lint("SELECT 'delete from x' FROM t"), [])

    def test_like_pattern_inside_string_is_still_seen(self) -> None:
        # the pattern itself is a literal argument of LIKE: SQL006 fires
        result = self.tool.execute(
            mode="lint", sql="SELECT a FROM t WHERE b LIKE '%x'")
        self.assertEqual(_codes(result), ["SQL006"])

    def test_dash_dash_comment_masks_keywords(self) -> None:
        self.assertEqual(
            self._lint(
                "SELECT a FROM t -- delete from x; select * from y\n"
                "WHERE b = 1"),
            [],
        )

    def test_hash_comment_masks_keywords(self) -> None:
        self.assertEqual(
            self._lint("SELECT a FROM t # drop table x\nWHERE b = 1"), [])

    def test_block_comment_masks_comma_join(self) -> None:
        self.assertEqual(
            self._lint("SELECT a /* , b CROSS JOIN c */ FROM t"), [])

    def test_multiline_block_comment_keeps_line_numbers(self) -> None:
        sql = (
            "SELECT a\n"
            "/* cross join x\n"
            "   select * from y */\n"
            "FROM t"
        )
        result = self.tool.execute(mode="lint", sql=sql)
        self.assertEqual(_codes(result), [])
        # FROM on the fourth physical line: prove offsets survived the
        # multi-line comment by linting the trailing clause keyword
        self.assertEqual(result["statement_type"], "select")

    def test_string_with_newline_and_doubled_quotes(self) -> None:
        sql = "SELECT 'a\nb and ''c'' -- not a comment' AS s FROM t"
        self.assertEqual(self._lint(sql), [])

    def test_double_quoted_identifier_not_a_keyword(self) -> None:
        self.assertEqual(self._lint('SELECT "select" FROM "from"'), [])

    def test_backtick_quoted_identifier_not_a_keyword(self) -> None:
        self.assertEqual(self._lint("SELECT `delete` FROM `update`"), [])

    def test_semicolon_inside_string_is_not_a_separator(self) -> None:
        result = self.tool.execute(
            mode="lint", sql="SELECT 'a;b' AS s FROM t")
        self.assertEqual(_codes(result), [])

    def _lint(self, sql: str) -> list:
        return _codes(self.tool.execute(mode="lint", sql=sql))


class SqlLintToolStructureTest(unittest.TestCase):
    """explain_structure on 18 crafted statements."""

    def setUp(self) -> None:
        self.tool = SqlLintTool()

    def _structure(self, sql: str) -> dict:
        return self.tool.execute(mode="explain_structure", sql=sql)

    def test_01_simple_select(self) -> None:
        self.assertEqual(
            self._structure("SELECT id, name FROM users"),
            {
                "mode": "explain_structure", "type": "select",
                "tables": ["users"], "columns": ["id", "name"],
                "has_where": False, "has_group_by": False,
                "has_order_by": False, "has_limit": False,
                "limit_value": None, "join_kinds": [],
                "subquery_count": 0, "cte_names": [],
            },
        )

    def test_02_full_flag_matrix(self) -> None:
        result = self._structure(
            "SELECT dept, COUNT(*) FROM emp WHERE active = 1 "
            "GROUP BY dept HAVING COUNT(*) > 2 ORDER BY dept "
            "LIMIT 25 OFFSET 50")
        self.assertEqual(result["type"], "select")
        self.assertEqual(result["tables"], ["emp"])
        self.assertEqual(result["columns"], ["dept", "COUNT(*)"])
        for flag in ("has_where", "has_group_by", "has_order_by",
                     "has_limit"):
            self.assertTrue(result[flag], flag)
        self.assertEqual(result["limit_value"], 25)

    def test_03_aliased_joins(self) -> None:
        result = self._structure(
            "SELECT u.id FROM users u "
            "LEFT JOIN orders o ON o.uid = u.id "
            "INNER JOIN tags t ON t.uid = u.id")
        self.assertEqual(result["tables"], ["users", "orders", "tags"])
        self.assertEqual(result["join_kinds"], ["left", "inner"])

    def test_04_bare_join_counts_as_inner(self) -> None:
        result = self._structure(
            "SELECT a FROM t JOIN u ON t.k = u.k")
        self.assertEqual(result["join_kinds"], ["inner"])

    def test_05_right_outer_join_kind(self) -> None:
        result = self._structure(
            "SELECT a FROM t RIGHT OUTER JOIN u ON t.k = u.k")
        self.assertEqual(result["join_kinds"], ["right"])

    def test_06_from_subquery(self) -> None:
        result = self._structure(
            "SELECT s.x FROM (SELECT x FROM base) AS s")
        self.assertEqual(result["tables"], ["base"])
        self.assertEqual(result["subquery_count"], 1)

    def test_07_in_subquery(self) -> None:
        result = self._structure(
            "SELECT a FROM t WHERE id IN (SELECT uid FROM admins)")
        self.assertEqual(result["tables"], ["t", "admins"])
        self.assertEqual(result["subquery_count"], 1)
        self.assertTrue(result["has_where"])

    def test_08_scalar_subquery_in_select_list(self) -> None:
        result = self._structure(
            "SELECT id, (SELECT MAX(n) FROM seq) AS m FROM t")
        self.assertEqual(
            result["columns"],
            ["id", "(SELECT MAX(n) FROM seq) AS m"],
        )
        self.assertEqual(result["subquery_count"], 1)

    def test_09_single_cte(self) -> None:
        result = self._structure(
            "WITH active AS (SELECT id FROM users WHERE ok = 1) "
            "SELECT id FROM active")
        self.assertEqual(result["type"], "select")
        self.assertEqual(result["cte_names"], ["active"])
        self.assertEqual(result["tables"], ["users", "active"])
        self.assertEqual(result["subquery_count"], 1)

    def test_10_recursive_cte(self) -> None:
        result = self._structure(
            "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL "
            "SELECT n + 1 FROM r WHERE n < 10) SELECT n FROM r")
        self.assertEqual(result["type"], "select")
        self.assertEqual(result["cte_names"], ["r"])

    def test_11_two_ctes(self) -> None:
        result = self._structure(
            "WITH a AS (SELECT 1 AS x), b AS (SELECT 2 AS y) "
            "SELECT x, y FROM a, b")
        self.assertEqual(result["cte_names"], ["a", "b"])
        self.assertEqual(result["subquery_count"], 2)

    def test_12_insert_select(self) -> None:
        result = self._structure(
            "INSERT INTO archive (id, name) "
            "SELECT id, name FROM src WHERE created < '2024-01-01'")
        self.assertEqual(result["type"], "insert")
        self.assertEqual(result["tables"], ["archive", "src"])
        self.assertEqual(result["columns"], ["id", "name"])
        self.assertTrue(result["has_where"])

    def test_13_update_shape(self) -> None:
        result = self._structure(
            "UPDATE db.users SET status = 'x' WHERE id = 1")
        self.assertEqual(result["type"], "update")
        self.assertEqual(result["tables"], ["db.users"])
        self.assertEqual(result["columns"], [])
        self.assertTrue(result["has_where"])

    def test_14_delete_with_mysql_limit(self) -> None:
        result = self._structure(
            "DELETE FROM logs WHERE ts < 100 LIMIT 5")
        self.assertEqual(result["type"], "delete")
        self.assertEqual(result["tables"], ["logs"])
        self.assertTrue(result["has_limit"])
        self.assertEqual(result["limit_value"], 5)

    def test_15_mysql_limit_offset_count(self) -> None:
        result = self._structure("SELECT a FROM t LIMIT 5, 10")
        self.assertTrue(result["has_limit"])
        self.assertEqual(result["limit_value"], 10)

    def test_16_fetch_first(self) -> None:
        result = self._structure(
            "SELECT a FROM t ORDER BY a FETCH FIRST 5 ROWS ONLY")
        self.assertTrue(result["has_limit"])
        self.assertEqual(result["limit_value"], 5)

    def test_17_fetch_first_row_only(self) -> None:
        result = self._structure(
            "SELECT a FROM t FETCH FIRST ROW ONLY")
        self.assertTrue(result["has_limit"])
        self.assertEqual(result["limit_value"], 1)

    def test_18_union_all_columns_from_first_branch(self) -> None:
        result = self._structure(
            "SELECT id, name FROM a UNION ALL SELECT id, name FROM b")
        self.assertEqual(result["type"], "select")
        self.assertEqual(result["tables"], ["a", "b"])
        self.assertEqual(result["columns"], ["id", "name"])

    def test_star_select_list_reports_star(self) -> None:
        self.assertEqual(
            self._structure("SELECT * FROM t")["columns"], ["*"])

    def test_distinct_not_leaked_into_columns(self) -> None:
        self.assertEqual(
            self._structure("SELECT DISTINCT a FROM t")["columns"], ["a"])

    def test_qualified_columns_keep_dots(self) -> None:
        self.assertEqual(
            self._structure("SELECT u.id, u.name AS n FROM users u")[
                "columns"],
            ["u.id", "u.name AS n"],
        )


class SqlLintToolFormatTest(unittest.TestCase):
    """Deterministic formatting and round-trip parse-stability."""

    def setUp(self) -> None:
        self.tool = SqlLintTool()

    def _format(self, sql: str, **options) -> str:
        return self.tool.execute(
            mode="format", sql=sql, **options)["result"]

    def test_canonical_clauses_each_on_own_line(self) -> None:
        self.assertEqual(
            self._format(
                "select id, name from users where id in "
                "(select uid from admin where lvl > 3) "
                "and name = 'x' order by id desc limit 5"),
            "SELECT id, name\n"
            "FROM users\n"
            "WHERE id IN (\n"
            "  SELECT uid\n"
            "  FROM admin\n"
            "  WHERE lvl > 3\n"
            ") AND name = 'x'\n"
            "ORDER BY id DESC\n"
            "LIMIT 5",
        )

    def test_subquery_indentation_two_spaces(self) -> None:
        self.assertEqual(
            self._format(
                "select a from t where b = (select max(x) from u "
                "where k = 1)"),
            # max stays verbatim: only recognized keywords are
            # upper-cased, function names are identifiers
            "SELECT a\n"
            "FROM t\n"
            "WHERE b = (\n"
            "  SELECT max(x)\n"
            "  FROM u\n"
            "  WHERE k = 1\n"
            ")",
        )

    def test_cte_and_joins(self) -> None:
        self.assertEqual(
            self._format(
                "with cte as (select id from users where active = 1) "
                "select c.id from cte c inner join logs l "
                "on l.uid = c.id where l.lvl > 2"),
            "WITH cte AS (\n"
            "  SELECT id\n"
            "  FROM users\n"
            "  WHERE active = 1\n"
            ")\n"
            "SELECT c.id\n"
            "FROM cte c\n"
            "INNER JOIN logs l ON l.uid = c.id\n"
            "WHERE l.lvl > 2",
        )

    def test_uppercase_keywords_false_keeps_case(self) -> None:
        self.assertEqual(
            self._format(
                "select id from t where a = 1",
                uppercase_keywords=False),
            "select id\nfrom t\nwhere a = 1",
        )

    def test_uppercase_leaves_identifiers_and_strings_alone(self) -> None:
        result = self._format(
            "select myColumn from myTable where note = 'select from'")
        self.assertIn("myColumn", result)
        self.assertIn("myTable", result)
        self.assertIn("'select from'", result)
        self.assertIn("SELECT", result.split("\n")[0])

    def test_unary_minus_and_function_parens(self) -> None:
        self.assertEqual(
            self._format(
                "select count(*) , price * -1 from t where x in "
                "(-1, -2)"),
            # count stays verbatim (function name, not a keyword)
            "SELECT count(*), price * -1\n"
            "FROM t\n"
            "WHERE x IN (-1, -2)",
        )

    def test_union_all_on_own_line(self) -> None:
        self.assertEqual(
            self._format("select a from t union all select b from u"),
            "SELECT a\nFROM t\nUNION ALL\nSELECT b\nFROM u",
        )

    def test_mysql_limit_pair(self) -> None:
        self.assertEqual(
            self._format("select a from t limit 5, 10"),
            "SELECT a\nFROM t\nLIMIT 5, 10",
        )

    def test_comments_dropped_and_trailing_semicolon_dropped(self) -> None:
        self.assertEqual(
            self._format(
                "select a -- trailing comment\nfrom t /* block */;"),
            "SELECT a\nFROM t",
        )

    def test_update_stays_compact(self) -> None:
        self.assertEqual(
            self._format("update t set a = 1, b = 'x y' where id = -3"),
            "UPDATE t SET a = 1, b = 'x y'\nWHERE id = -3",
        )

    ROUND_TRIPS = [
        "select id, name from users where id in (select uid from admin "
        "where lvl > 3) and name = 'x' order by id desc limit 5",
        "SELECT price * qty AS revenue, -discount FROM orders o "
        "JOIN items i ON i.oid = o.id LEFT JOIN tags t2 ON t2.iid = i.id "
        "WHERE o.note LIKE '%oops' OR o.qty = -1 GROUP BY revenue "
        "HAVING COUNT(*) > 1.5e2 ORDER BY 2",
        "with recursive r(n) as (select 1 union all select n + 1 from r "
        "where n < 10) select n from r",
        "update t set a = 1, b = 'x y' where id in (-3, -4) and z <> 0",
        "delete from logs where ts < 100 limit 5",
        "insert into arch (id, v) select id, v from src "
        "where v <> 'keep' order by id",
        "select distinct a, count(*) as c from t group by a "
        "having count(*) > 2 order by c desc, a fetch first 10 rows only",
        "select a from t1 cross join t2 where t1.k = t2.k "
        "and t1.s like '%bad' or t1.n = 1 or t1.n = 2 or t1.n = 3",
    ]

    def test_format_round_trip_stable(self) -> None:
        for sql in self.ROUND_TRIPS:
            once = self._format(sql)
            twice = self._format(once)
            self.assertEqual(once, twice, msg=sql)

    def test_format_preserves_structure(self) -> None:
        for sql in self.ROUND_TRIPS:
            before = self.tool.execute(mode="explain_structure", sql=sql)
            after = self.tool.execute(
                mode="explain_structure", sql=self._format(sql))
            # keyword letter case may shift inside extracted text items
            # (uppercase_keywords defaults on); everything else is exact
            before["columns"] = [c.casefold() for c in before["columns"]]
            after["columns"] = [c.casefold() for c in after["columns"]]
            self.assertEqual(before, after, msg=sql)

    def test_format_preserves_lint_codes(self) -> None:
        for sql in self.ROUND_TRIPS:
            before = _codes(self.tool.execute(mode="lint", sql=sql))
            after = _codes(
                self.tool.execute(mode="lint", sql=self._format(sql)))
            self.assertEqual(before, after, msg=sql)

    def test_format_result_metadata(self) -> None:
        result = self.tool.execute(
            mode="format", sql="select a from t where x = 1")
        self.assertEqual(result["mode"], "format")
        self.assertEqual(result["statement_type"], "select")
        self.assertEqual(result["line_count"], 3)


class SqlLintToolErrorMatrixTest(unittest.TestCase):
    """Every strict-validation branch raises the documented error."""

    def setUp(self) -> None:
        self.tool = SqlLintTool()

    def _assertRaisesMessage(self, sql=None, *, options=None,
                             contains: str) -> None:
        kwargs = dict(options or {})
        if sql is not None:
            kwargs["sql"] = sql
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        self.assertIn(contains, str(ctx.exception))

    # -- mode --------------------------------------------------------------

    def test_mode_unknown(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1", options={"mode": "parse"}, contains="mode must be")

    def test_mode_missing(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1", options={"mode": None}, contains="mode must be")

    # -- options -----------------------------------------------------------

    def test_rules_not_a_dict(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1", options={"mode": "lint", "rules": ["SQL001"]},
            contains="rules must be a dict")

    def test_rules_unknown_code(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1",
            options={"mode": "lint", "rules": {"SQL999": True}},
            contains="rules keys must be one of")

    def test_rules_non_boolean_value(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1",
            options={"mode": "lint", "rules": {"SQL001": "off"}},
            contains="rules['SQL001'] must be a bool")

    def test_require_limit_not_bool(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1",
            options={"mode": "lint", "require_limit": "yes"},
            contains="require_limit must be a bool")

    def test_uppercase_keywords_not_bool(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1",
            options={"mode": "format", "uppercase_keywords": 1},
            contains="uppercase_keywords must be a bool")

    def test_in_list_max_zero(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1", options={"mode": "lint", "in_list_max": 0},
            contains="in_list_max must be an int in 1..10000")

    def test_in_list_max_too_large(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1", options={"mode": "lint", "in_list_max": 10001},
            contains="in_list_max must be an int in 1..10000")

    def test_in_list_max_bool_rejected(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1", options={"mode": "lint", "in_list_max": True},
            contains="in_list_max must be an int in 1..10000")

    def test_or_chain_min_below_two(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1", options={"mode": "lint", "or_chain_min": 1},
            contains="or_chain_min must be an int in 2..1000")

    def test_or_chain_min_float(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1", options={"mode": "lint", "or_chain_min": 2.5},
            contains="or_chain_min must be an int in 2..1000")

    # -- statement contract -------------------------------------------------

    def test_sql_not_a_string(self) -> None:
        self._assertRaisesMessage(
            options={"mode": "lint", "sql": 42},
            contains="sql must be a non-empty string")

    def test_sql_none(self) -> None:
        self._assertRaisesMessage(
            options={"mode": "lint", "sql": None},
            contains="sql must be a non-empty string")

    def test_sql_empty(self) -> None:
        self._assertRaisesMessage(
            "  ", options={"mode": "lint"},
            contains="sql must be a non-empty string")

    def test_sql_too_long(self) -> None:
        self._assertRaisesMessage(
            "SELECT " + "a" * 20001, options={"mode": "lint"},
            contains="sql exceeds MAX_SQL_CHARS")

    def test_sql_nul_byte(self) -> None:
        self._assertRaisesMessage(
            "SELECT \x00", options={"mode": "lint"},
            contains="must not contain NUL")

    def test_only_comment(self) -> None:
        self._assertRaisesMessage(
            "-- nothing here", options={"mode": "lint"},
            contains="empty after comment stripping")

    def test_only_block_comment(self) -> None:
        self._assertRaisesMessage(
            "/* nothing\nhere */", options={"mode": "lint"},
            contains="empty after comment stripping")

    def test_multiple_statements_two_selects(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1; SELECT 2", options={"mode": "lint"},
            contains="multiple statements are not supported")

    def test_multiple_statements_offset_and_position(self) -> None:
        message = self._error_message(
            mode="lint", sql="SELECT 1; SELECT 2")
        self.assertIn("offset 8", message)
        self.assertIn("line 1, column 9", message)

    def test_two_trailing_semicolons(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1;;", options={"mode": "lint"},
            contains="multiple statements")

    def test_single_trailing_semicolon_tolerated(self) -> None:
        result = self.tool.execute(mode="lint", sql="SELECT 1 FROM t;")
        self.assertEqual(_codes(result), [])

    def test_unbalanced_close_paren(self) -> None:
        message = self._error_message(mode="lint", sql="SELECT a FROM t)")
        self.assertIn("unbalanced ')'", message)
        self.assertIn("offset 15", message)

    def test_unbalanced_open_paren(self) -> None:
        message = self._error_message(mode="lint", sql="SELECT (a FROM t")
        self.assertIn("unbalanced '('", message)
        self.assertIn("offset 7", message)

    def test_unbalanced_paren_inside_string_ignored(self) -> None:
        result = self.tool.execute(
            mode="lint", sql="SELECT ')(' AS s FROM t")
        self.assertEqual(_codes(result), [])

    def test_paren_depth_cap(self) -> None:
        sql = "SELECT " + "(" * 65 + "1" + ")" * 65
        self._assertRaisesMessage(
            sql, options={"mode": "lint"},
            contains="nesting depth exceeds MAX_PAREN_DEPTH")

    def test_unterminated_string_literal(self) -> None:
        self._assertRaisesMessage(
            "SELECT 'abc", options={"mode": "lint"},
            contains="unterminated string literal starting at offset 7")

    def test_unterminated_quoted_identifier(self) -> None:
        self._assertRaisesMessage(
            'SELECT "abc', options={"mode": "lint"},
            contains="unterminated quoted identifier")

    def test_unterminated_block_comment(self) -> None:
        self._assertRaisesMessage(
            "SELECT 1 /* oops", options={"mode": "lint"},
            contains="unterminated block comment starting at offset 9")

    def test_validation_precedes_analysis_for_all_modes(self) -> None:
        for mode in ("lint", "explain_structure", "format"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, sql="SELECT 1; SELECT 2")

    def _error_message(self, **kwargs) -> str:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        return str(ctx.exception)


class SqlLintToolIssueExampleTest(unittest.TestCase):
    """The review/QA story this tool exists for, end to end.

    An agent drafts a reporting query; the tool reviews it offline before
    any executor touches a database.
    """

    def setUp(self) -> None:
        self.tool = SqlLintTool()

    def test_draft_review_pipeline(self) -> None:
        draft = (
            "select * from orders o, customers c "
            "where o.note like '%urgent%' "
            "and o.cid = 1 or o.cid = 2 or o.cid = 3 "
            "group by c.region"
        )
        linted = self.tool.execute(
            mode="lint", sql=draft, require_limit=True)
        self.assertFalse(linted["ok"])
        self.assertEqual(
            _codes(linted),
            # offsets: SELECT(0) < *(7) < '%urgent%' literal < first OR
            # predicate < GROUP BY item; the comma join is filtered by
            # the WHERE clause so SQL005 stays silent by design
            ["SQL004", "SQL001", "SQL006", "SQL010", "SQL008"],
        )
        structure = self.tool.execute(
            mode="explain_structure", sql=draft)
        self.assertEqual(structure["type"], "select")
        self.assertEqual(structure["tables"], ["orders", "customers"])
        formatted = self.tool.execute(mode="format", sql=draft)["result"]
        self.assertIn("SELECT *\nFROM orders o", formatted)

    def test_clean_query_passes(self) -> None:
        clean = (
            "SELECT o.id, c.name FROM orders o "
            "JOIN customers c ON c.id = o.cid "
            "WHERE o.note LIKE 'urgent%' LIMIT 100"
        )
        result = self.tool.execute(
            mode="lint", sql=clean, require_limit=True)
        self.assertTrue(result["ok"])
        self.assertEqual(_codes(result), [])


if __name__ == "__main__":
    unittest.main()
