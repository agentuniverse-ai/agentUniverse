#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_sql_format_tool.py

"""Offline unit tests for SqlFormatTool.

The tool is built purely on the standard library and never touches a
database, the network or the filesystem, so this suite runs fully
offline. Assertions are exact ground truths: every option and preset
is checked against hand-derived expected output, the keyword-case
matrix proves strings / quoted identifiers / comments stay untouched,
comment and string contents are byte-preserved, formatting is
deterministic and idempotent over a 100+-statement corpus times nine
option combinations (format(format(x)) == format(x)), the check mode
is verified against exact first-difference records and diff line
lists, CTE / subquery nesting is checked against exact indents, and
the error matrix covers every strict-validation branch of the
single-statement contract and the option table.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import SqlFormatTool
from agentuniverse.agent.action.tool.common_tool.sql_format_tool import (
    SAMPLE_STATEMENT,
    SqlFormatTool as DirectSqlFormatTool,
)

SAMPLE = (
    "select u.id, u.name, count(o.id) as orders -- pick columns\n"
    "from users u join orders o on u.id = o.user_id "
    "where u.status = 'active' and o.total > 100 "
    "group by u.id, u.name having count(o.id) > 5 "
    "order by orders desc limit 10;"
)

DEFAULT_SAMPLE = """SELECT u.id, u.name, count(o.id) AS orders -- pick columns
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active' AND o.total > 100
GROUP BY u.id, u.name
HAVING count(o.id) > 5
ORDER BY orders DESC
LIMIT 10;"""

COMPACT_SAMPLE = (
    "SELECT u.id, u.name, count(o.id) AS orders -- pick columns\n"
    "FROM users u JOIN orders o ON u.id = o.user_id "
    "WHERE u.status = 'active' AND o.total > 100 "
    "GROUP BY u.id, u.name HAVING count(o.id) > 5 "
    "ORDER BY orders DESC LIMIT 10;"
)

PYTHONIC_SAMPLE = """select u.id
    , u.name
    , count(o.id) as orders -- pick columns
from users u
join orders o on u.id = o.user_id
where u.status = 'active'
    and o.total > 100
group by u.id
    , u.name
having count(o.id) > 5
order by orders desc
limit 10;"""


def _fmt(tool, sql, **kwargs):
    return tool.execute(mode="format", sql=sql, **kwargs)["result"]


class SqlFormatToolBasicsTest(unittest.TestCase):
    """Export surface, determinism and result shape."""

    def setUp(self) -> None:
        self.tool = SqlFormatTool()

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(SqlFormatTool, DirectSqlFormatTool)

    def test_name_modes_and_presets(self) -> None:
        self.assertEqual(self.tool.name, "sql_format_tool")
        self.assertEqual(
            SqlFormatTool.MODES, ("format", "check", "styles"))
        self.assertEqual(
            SqlFormatTool.PRESET_NAMES, ("default", "compact", "pythonic"))
        self.assertEqual(
            SqlFormatTool.KEYWORD_CASES, ("upper", "lower", "preserve"))
        self.assertEqual(
            SqlFormatTool.IDENTIFIER_CASES, ("preserve", "lower"))
        self.assertEqual(SqlFormatTool.INDENTS, (2, 4))
        self.assertEqual(
            SqlFormatTool.COMMA_STYLES, ("trailing", "leading"))
        self.assertEqual(
            SqlFormatTool.SELECT_WRAPS, ("none", "at_width"))

    def test_deterministic_repeat(self) -> None:
        first = self.tool.execute(mode="format", sql=SAMPLE)
        second = self.tool.execute(mode="format", sql=SAMPLE)
        self.assertEqual(first, second)

    def test_format_result_shape(self) -> None:
        result = self.tool.execute(mode="format", sql=SAMPLE)
        self.assertEqual(result["mode"], "format")
        self.assertEqual(result["statement_type"], "select")
        self.assertEqual(
            result["line_count"], result["result"].count("\n") + 1)
        self.assertEqual(result["style"], "default")
        self.assertEqual(
            result["options"],
            {
                "keyword_case": "upper", "identifier_case": "preserve",
                "indent": 2, "comma_style": "trailing",
                "newline_before_major": True, "select_wrap": "none",
                "wrap_column": 100, "and_newline_group": False,
            },
        )

    def test_style_partial_override(self) -> None:
        result = self.tool.execute(
            mode="format", sql="select a from t", style="pythonic",
            comma_style="trailing",
        )
        self.assertEqual(result["style"], "pythonic")
        self.assertEqual(result["options"]["keyword_case"], "lower")
        self.assertEqual(result["options"]["indent"], 4)
        self.assertEqual(result["options"]["comma_style"], "trailing")
        self.assertEqual(result["options"]["and_newline_group"], True)

    def test_statement_type_resolution(self) -> None:
        cases = {
            "select 1": "select",
            "with c as (select 1) select * from c": "select",
            "with c as (select 1) insert into t select * from c":
                "insert",
            "update t set a = 1": "update",
            "delete from t": "delete",
            "create table t (a int)": "create",
        }
        for sql, expected in cases.items():
            self.assertEqual(
                self.tool.execute(mode="format", sql=sql)
                ["statement_type"],
                expected,
                msg=sql,
            )


class FormatPresetGroundTruthTest(unittest.TestCase):
    """Exact expected output for every built-in preset."""

    def setUp(self) -> None:
        self.tool = SqlFormatTool()

    def test_default_preset(self) -> None:
        self.assertEqual(
            _fmt(self.tool, SAMPLE), DEFAULT_SAMPLE)

    def test_default_preset_via_explicit_style(self) -> None:
        self.assertEqual(
            _fmt(self.tool, SAMPLE, style="default"), DEFAULT_SAMPLE)

    def test_compact_preset(self) -> None:
        self.assertEqual(
            _fmt(self.tool, SAMPLE, style="compact"), COMPACT_SAMPLE)

    def test_pythonic_preset(self) -> None:
        self.assertEqual(
            _fmt(self.tool, SAMPLE, style="pythonic"), PYTHONIC_SAMPLE)

    def test_preset_outputs_are_idempotent(self) -> None:
        for style, expected in (
            ("default", DEFAULT_SAMPLE),
            ("compact", COMPACT_SAMPLE),
            ("pythonic", PYTHONIC_SAMPLE),
        ):
            again = _fmt(self.tool, expected, style=style)
            self.assertEqual(again, expected, msg=style)


class FormatOptionGroundTruthTest(unittest.TestCase):
    """Exact expected output per option, all hand-derived."""

    def setUp(self) -> None:
        self.tool = SqlFormatTool()

    def test_keyword_case_upper(self) -> None:
        sql = ("Select Name, Surname From TheTable "
               "Where Msg = 'Select ALL From X' "
               "-- WHERE and SELECT are words\n"
               "And Flag Is Not Null")
        self.assertEqual(
            _fmt(self.tool, sql, keyword_case="upper"),
            "SELECT Name, Surname\n"
            "FROM TheTable\n"
            "WHERE Msg = 'Select ALL From X'"
            " -- WHERE and SELECT are words\n"
            "AND Flag IS NOT NULL",
        )

    def test_keyword_case_lower(self) -> None:
        sql = ("Select Name, Surname From TheTable "
               "Where Msg = 'Select ALL From X' "
               "-- WHERE and SELECT are words\n"
               "And Flag Is Not Null")
        self.assertEqual(
            _fmt(self.tool, sql, keyword_case="lower"),
            "select Name, Surname\n"
            "from TheTable\n"
            "where Msg = 'Select ALL From X'"
            " -- WHERE and SELECT are words\n"
            "and Flag is not null",  # Flag is an identifier: preserved
        )

    def test_keyword_case_preserve(self) -> None:
        sql = "Select a From t Where x Is Not Null"
        self.assertEqual(
            _fmt(self.tool, sql, keyword_case="preserve"),
            "Select a\nFrom t\nWhere x Is Not Null",
        )

    def test_identifier_case_lower_and_preserve(self) -> None:
        sql = ("SELECT Name, COUNT(Surname) AS N "
               "FROM MyTable MT WHERE MT.Q = 1")
        self.assertEqual(
            _fmt(self.tool, sql, identifier_case="lower"),
            "SELECT name, count(surname) AS n\n"
            "FROM mytable mt\n"
            "WHERE mt.q = 1",
        )
        self.assertEqual(
            _fmt(self.tool, sql, identifier_case="preserve"),
            "SELECT Name, COUNT(Surname) AS N\n"
            "FROM MyTable MT\n"
            "WHERE MT.Q = 1",
        )

    def test_quoted_identifiers_and_strings_verbatim(self) -> None:
        sql = 'select "Select Me", `from`, \'WHERE\' from "The Table"'
        self.assertEqual(
            _fmt(self.tool, sql, keyword_case="upper",
                 identifier_case="lower"),
            'SELECT "Select Me", `from`, \'WHERE\'\nFROM "The Table"',
        )
        self.assertEqual(
            _fmt(self.tool, sql, keyword_case="lower"),
            'select "Select Me", `from`, \'WHERE\'\nfrom "The Table"',
        )

    def test_doubled_quote_escape_preserved(self) -> None:
        self.assertEqual(
            _fmt(self.tool, "select 'it''s fine' from t"),
            "SELECT 'it''s fine'\nFROM t",
        )

    def test_indent_four_nested_subqueries(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from (select b from (select c from deep) x) y",
                 indent=4),
            "SELECT a\n"
            "FROM (\n"
            "    SELECT b\n"
            "    FROM (\n"
            "        SELECT c\n"
            "        FROM deep\n"
            "    ) x\n"
            ") y",
        )

    def test_indent_two_nested_subqueries(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from (select b from (select c from deep) x) y"),
            "SELECT a\n"
            "FROM (\n"
            "  SELECT b\n"
            "  FROM (\n"
            "    SELECT c\n"
            "    FROM deep\n"
            "  ) x\n"
            ") y",
        )

    def test_comma_style_leading(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select t.* , s.* from t, s where t.id = s.id",
                 comma_style="leading"),
            "SELECT t.*\n"
            "  , s.*\n"
            "FROM t\n"
            "  , s\n"
            "WHERE t.id = s.id",
        )

    def test_comma_style_trailing_default(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select t.*, s.* from t, s where t.id = s.id"),
            "SELECT t.*, s.*\nFROM t, s\nWHERE t.id = s.id",
        )

    def test_commas_inside_parens_always_inline(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select f(a, b, c), g(1, 2) from t where x in (1, 2, 3)",
                 comma_style="leading"),
            "SELECT f(a, b, c)\n"
            "  , g(1, 2)\n"
            "FROM t\n"
            "WHERE x IN (1, 2, 3)",
        )

    def test_newline_before_major_false_single_line(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from t where x = 1 group by a order by a",
                 newline_before_major=False),
            "SELECT a FROM t WHERE x = 1 GROUP BY a ORDER BY a",
        )

    def test_newline_before_major_false_keeps_subqueries_inline(
            self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from (select b from u) d where a > 1",
                 newline_before_major=False),
            "SELECT a FROM (SELECT b FROM u) d WHERE a > 1",
        )

    def test_leading_commas_force_breaks_even_when_compact(self) -> None:
        self.assertEqual(
            _fmt(self.tool, "select a, b, c from t",
                 newline_before_major=False, comma_style="leading"),
            "SELECT a\n  , b\n  , c\nFROM t",  # majors leave comma lines
        )

    def test_select_wrap_at_width(self) -> None:
        cols = ", ".join(f"col_{i} AS alias_number_{i}" for i in range(8))
        wide = f"select {cols} from big_table"
        expected = (
            "SELECT col_0 AS alias_number_0,\n"
            + "".join(
                f"  col_{i} AS alias_number_{i},\n" for i in range(1, 7))
            + "  col_7 AS alias_number_7\n"
            + "FROM big_table"
        )
        self.assertEqual(
            _fmt(self.tool, wide, select_wrap="at_width", wrap_column=80),
            expected,
        )

    def test_select_wrap_boundary_between_columns(self) -> None:
        # logical single-line width: SELECT + 5 columns = 97 chars, so
        # it wraps at 80 but not at 120
        cols = ", ".join(f"column_number_{i}" for i in range(5))
        wide = f"select {cols} from t"
        logical = len(f"SELECT {cols}")
        self.assertTrue(80 < logical <= 120, msg=f"len={logical}")
        self.assertEqual(
            _fmt(self.tool, wide, select_wrap="at_width",
                 wrap_column=80),
            "SELECT column_number_0,\n"
            "  column_number_1,\n"
            "  column_number_2,\n"
            "  column_number_3,\n"
            "  column_number_4\n"
            "FROM t",
        )
        self.assertEqual(
            _fmt(self.tool, wide, select_wrap="at_width",
                 wrap_column=120),
            f"SELECT {cols}\nFROM t",
        )

    def test_select_wrap_none_never_wraps(self) -> None:
        cols = ", ".join(f"column_number_{i}" for i in range(20))
        wide = f"select {cols} from t"
        self.assertEqual(
            _fmt(self.tool, wide), f"SELECT {cols}\nFROM t")

    def test_and_newline_group(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from t where (a = 1 and b = 2) "
                 "or (c = 3 and d = 4)",
                 and_newline_group=True),
            "SELECT a\n"
            "FROM t\n"
            "WHERE (a = 1 AND b = 2)\n"
            "  OR (c = 3 AND d = 4)",
        )

    def test_and_newline_group_between_and_never_breaks(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from t where b in (1, 2) and c between 1 and 10",
                 and_newline_group=True),
            "SELECT a\n"
            "FROM t\n"
            "WHERE b IN (1, 2)\n"
            "  AND c BETWEEN 1 AND 10",
        )

    def test_and_newline_group_mixed_connectors(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from t where x between 1 and 2 and y = 3 "
                 "and z between 4 and 5 or w = 9",
                 and_newline_group=True),
            "SELECT a\n"
            "FROM t\n"
            "WHERE x BETWEEN 1 AND 2\n"
            "  AND y = 3\n"
            "  AND z BETWEEN 4 AND 5\n"
            "  OR w = 9",
        )

    def test_and_newline_off_stays_inline(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from t where a = 1 and b = 2 or c = 3"),
            "SELECT a\nFROM t\nWHERE a = 1 AND b = 2 OR c = 3",
        )

    def test_trailing_semicolon_preserved(self) -> None:
        self.assertEqual(
            _fmt(self.tool, "select a from t;"), "SELECT a\nFROM t;")
        self.assertEqual(
            _fmt(self.tool, "select a from t"), "SELECT a\nFROM t")

    def test_spacing_rules(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select count(*) , t.a , -1 , .5 , x||y , j->'k' , "
                 "a<=b , c>=d , e<>f from t where g!=-1"),
            "SELECT count(*), t.a, -1, .5, x || y, j -> 'k', a <= b, "
            "c >= d, e <> f\nFROM t\nWHERE g != -1",
        )


class CommentPreservationTest(unittest.TestCase):
    """String and comment contents are byte-preserved, never
    reformatted; line comments end their line by definition."""

    def setUp(self) -> None:
        self.tool = SqlFormatTool()

    def test_block_comment_inline_bytes_exact(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select /**/ a /* keep   this   spacing */ from t"),
            "SELECT /**/ a /* keep   this   spacing */\nFROM t",
        )

    def test_line_comments_end_their_line(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a -- c1\nfrom t -- c2\nwhere x = 1 -- c3"),
            "SELECT a -- c1\nFROM t -- c2\nWHERE x = 1 -- c3",
        )

    def test_hash_line_comment(self) -> None:
        self.assertEqual(
            _fmt(self.tool, "# lead\nselect a from t # tail\nwhere x = 1"),
            "# lead\nSELECT a\nFROM t # tail\nWHERE x = 1",
        )

    def test_leading_block_comment(self) -> None:
        self.assertEqual(
            _fmt(self.tool, "/* header */ select a from t"),
            "/* header */\nSELECT a\nFROM t",
        )

    def test_multiline_block_comment_bytes_exact(self) -> None:
        self.assertEqual(
            _fmt(self.tool, "select a /* one\ntwo\nthree */ from t"),
            "SELECT a /* one\ntwo\nthree */\nFROM t",
        )

    def test_keyword_case_never_touches_comments_or_strings(self) -> None:
        sql = "select a -- SELECT from WHERE\nfrom t where m = 'ORDER BY not touched'"
        out = _fmt(self.tool, sql, keyword_case="lower")
        self.assertIn("-- SELECT from WHERE", out)
        self.assertIn("'ORDER BY not touched'", out)
        self.assertTrue(out.startswith("select a"))

    def test_comments_survive_every_preset(self) -> None:
        for style in ("default", "compact", "pythonic"):
            out = _fmt(self.tool, SAMPLE, style=style)
            self.assertIn("-- pick columns", out, msg=style)

    def test_string_containing_comment_markers(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from t where m = '-- not a comment' "
                 "and n = '/* also not */'"),
            "SELECT a\n"
            "FROM t\n"
            "WHERE m = '-- not a comment' AND n = '/* also not */'",
        )


class NestingGroundTruthTest(unittest.TestCase):
    """CTE / subquery indent nesting, exact."""

    def setUp(self) -> None:
        self.tool = SqlFormatTool()

    def test_cte_chain_and_nested_subquery(self) -> None:
        sql = ("with c as (select x, y from t1 where y > "
               "(select avg(y) from t1)), d as (select z from t2) "
               "select c.x, d.z from c join d on c.x = d.z order by 1")
        self.assertEqual(
            _fmt(self.tool, sql),
            "WITH c AS (\n"
            "  SELECT x, y\n"
            "  FROM t1\n"
            "  WHERE y > (\n"
            "    SELECT avg(y)\n"
            "    FROM t1\n"
            "  )\n"
            "), d AS (\n"
            "  SELECT z\n"
            "  FROM t2\n"
            ")\n"
            "SELECT c.x, d.z\n"
            "FROM c\n"
            "JOIN d ON c.x = d.z\n"
            "ORDER BY 1",
        )

    def test_in_subquery_block(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select * from (select 1 as x) d where x in "
                 "(select y from u)"),
            "SELECT *\n"
            "FROM (\n"
            "  SELECT 1 AS x\n"
            ") d\n"
            "WHERE x IN (\n"
            "  SELECT y\n"
            "  FROM u\n"
            ")",
        )

    def test_recursive_cte_pythonic(self) -> None:
        sql = ("with recursive r(n) as (select 1 union all select n + 1 "
               "from r where n < 10) select sum(n) from r")
        self.assertEqual(
            _fmt(self.tool, sql, style="pythonic"),
            "with recursive r(n) as (\n"
            "    select 1\n"
            "    union all\n"
            "    select n + 1\n"
            "    from r\n"
            "    where n < 10\n"
            ")\n"
            "select sum(n)\n"
            "from r",
        )

    def test_union_breaks(self) -> None:
        self.assertEqual(
            _fmt(self.tool,
                 "select a from t union all select b from u"),
            "SELECT a\nFROM t\nUNION ALL\nSELECT b\nFROM u",
        )


class CheckModeTest(unittest.TestCase):
    """The CI mode: clean detection, first difference, diff summary."""

    def setUp(self) -> None:
        self.tool = SqlFormatTool()

    def test_clean_on_exact_formatted_text(self) -> None:
        formatted = _fmt(self.tool, "select a from t where x = 1")
        result = self.tool.execute(mode="check", sql=formatted)
        self.assertTrue(result["clean"])
        self.assertIsNone(result["first_difference"])
        self.assertEqual(result["diff_lines"], [])
        self.assertFalse(result["diff_truncated"])
        self.assertEqual(result["statement_type"], "select")

    def test_clean_tolerates_trailing_newlines(self) -> None:
        formatted = _fmt(self.tool, "select a from t")
        result = self.tool.execute(mode="check", sql=formatted + "\n\n")
        self.assertTrue(result["clean"])

    def test_dirty_first_difference_exact(self) -> None:
        result = self.tool.execute(
            mode="check", sql="select a from t where  x=1")
        self.assertFalse(result["clean"])
        self.assertEqual(
            result["first_difference"],
            {"line": 1, "col": 1, "expected": "SELECT a",
             "actual": "select a from t where  x=1"},
        )

    def test_dirty_first_difference_on_later_line(self) -> None:
        formatted = _fmt(self.tool, "select a from t where x = 1")
        dirty = formatted.replace("FROM t", "FROM   t")
        result = self.tool.execute(mode="check", sql=dirty)
        self.assertFalse(result["clean"])
        self.assertEqual(
            result["first_difference"],
            {"line": 2, "col": 6, "expected": "FROM t",
             "actual": "FROM   t"},
        )

    def test_dirty_shorter_actual_side(self) -> None:
        # one compact line vs a four-line leading-comma expectation:
        # the actual line list is shorter than the expected one
        result = self.tool.execute(
            mode="check", sql="SELECT a, b FROM t ORDER BY a",
            comma_style="leading", and_newline_group=True)
        self.assertFalse(result["clean"])
        self.assertEqual(
            result["first_difference"],
            {"line": 1, "col": 9, "expected": "SELECT a",
             "actual": "SELECT a, b FROM t ORDER BY a"},
        )

    def test_diff_lines_exact(self) -> None:
        result = self.tool.execute(
            mode="check", sql="select a from t where  x=1")
        self.assertEqual(
            result["diff_lines"],
            ["@@ -1,3 +1 @@",
             "-SELECT a",
             "-FROM t",
             "-WHERE x = 1",
             "+select a from t where  x=1"],
        )
        self.assertFalse(result["diff_truncated"])

    def test_diff_truncation_cap(self) -> None:
        # 60+ differing lines exceed the 40-line cap
        dirty = "\n".join(
            f"select col_{i} from t" for i in range(60))
        result = self.tool.execute(mode="check", sql=dirty)
        self.assertFalse(result["clean"])
        self.assertTrue(result["diff_truncated"])
        self.assertGreater(result["diff_lines"], [])
        self.assertLessEqual(len(result["diff_lines"]), 40)

    def test_check_with_style(self) -> None:
        formatted = _fmt(self.tool, "select a from t", style="pythonic")
        self.assertTrue(
            self.tool.execute(mode="check", sql=formatted,
                              style="pythonic")["clean"])
        # the same text is NOT clean under the default preset
        self.assertFalse(
            self.tool.execute(mode="check", sql=formatted)["clean"])


class StylesModeTest(unittest.TestCase):
    """The styles catalog lists presets with rendered samples."""

    def setUp(self) -> None:
        self.tool = SqlFormatTool()

    def test_catalog_shape(self) -> None:
        result = self.tool.execute(mode="styles")
        self.assertEqual(result["mode"], "styles")
        self.assertEqual([s["name"] for s in result["styles"]],
                         ["default", "compact", "pythonic"])
        for entry in result["styles"]:
            self.assertEqual(
                sorted(entry["options"]),
                ["and_newline_group", "comma_style", "identifier_case",
                 "indent", "keyword_case", "newline_before_major",
                 "select_wrap", "wrap_column"],
            )
            self.assertTrue(entry["sample"])

    def test_each_sample_matches_format_of_sample_statement(self) -> None:
        for entry in self.tool.execute(mode="styles")["styles"]:
            formatted = self.tool.execute(
                mode="format", sql=SAMPLE_STATEMENT,
                **entry["options"])["result"]
            self.assertEqual(entry["sample"], formatted,
                             msg=entry["name"])

    def test_pythonic_sample_uses_leading_commas(self) -> None:
        catalog = {
            s["name"]: s for s in
            self.tool.execute(mode="styles")["styles"]
        }
        self.assertIn("\n    , ", catalog["pythonic"]["sample"])
        self.assertEqual(
            catalog["default"]["options"]["keyword_case"], "upper")
        self.assertEqual(
            catalog["compact"]["options"]["newline_before_major"],
            False)


class IdempotenceCorpusTest(unittest.TestCase):
    """format(format(x)) == format(x) plus call determinism over a
    100+-statement corpus times nine option combinations."""

    def setUp(self) -> None:
        self.tool = SqlFormatTool()

    @staticmethod
    def _corpus():
        stmts = []
        bases = [
            "select * from t",
            "select a, b, c from t where x = 1 and y <> 2 or z is null",
            "select distinct a from t order by a desc limit 5",
            "select count(*), sum(x), avg(y) from t group by z "
            "having count(*) > 3",
            "select t1.a, t2.b from t1 left outer join t2 "
            "on t1.id = t2.id cross join t3",
            "select a from t where b in (1, 2, 3) and c between 1 and 10 "
            "and d not like '%x%'",
            "select a from t where msg = "
            "'select * from where -- not a comment'",
            "select 'it''s quoted', `back tick`, \"Double Quoted\" from t",
            "select case when a = 1 then 'one' when a = 2 then 'two' "
            "else 'other' end as label from t",
            "select a from t where x = -5 and y = .5 and z = 1e-3",
            "update t set a = 1, b = 2 where c = 3",
            "delete from t where d < 100",
            "insert into t (a, b, c) values (1, 'x', null), (2, 'y', 3.14)",
            "select a from t union all select b from u except select c "
            "from v intersect select d from w",
            "with recursive r(n) as (select 1 union all select n + 1 "
            "from r where n < 10) select sum(n) from r",
            "select a from (select b from (select c from deep) x) y",
            "select a from t where exists (select 1 from u "
            "where u.id = t.id)",
            "select a from t where id in (select id from u where k = 2)",
            "select a || '-' || b as glued, c -> 'x' as js from t "
            "where a <= 5 and b >= 5 and c != 'q'",
            "select nulls_first, x from t order by a nulls first, b asc, "
            "c desc offset 10 fetch first 5 rows only",
            "select a from t group by a, b, c order by a, b",
            "create table x (a int, b text)",
            "select /**/ a /* keep   this   spacing */ from t",
            "select a from t -- trailing note",
            "select a -- c1\nfrom t -- c2\nwhere x = 1 -- c3",
            "# leading hash\nselect a from t",
            "/* multi\nline\nblock */ select a from t",
            "select filter_col from t where x > 1",
            "select row_number() over (partition by a order by b) as rn "
            "from t",
            "select a from t where (a = 1 and b = 2) or (c = 3 and d = 4)",
            "select -1, +2, 3.14159, .5, 1e10, 0.0001 from t",
            'select a as "Weird Alias", b as plain_alias '
            'from "My Table" x',
            "select max(a) from t where b > 0 group by d",
            "select sum(x) over () from t",
            "select t.* , s.* from t, s where t.id = s.id",
            "select /* one */ a, /* two */ b /* three */ from t",
            "select a from t where x between -1 and 1",
            "with a as (select 1), b as (select 2), c as (select 3) "
            "select * from a, b, c",
            "select greatest(a, b, c), least(a, b) from t",
            "select a from t where (x between 1 and 2) and y = 3",
            "select a from t where x between 1 and 2 and y = 3 "
            "and z between 4 and 5 or w = 9",
        ]
        for base in bases:
            stmts.append(base)
            stmts.append(base.rstrip(";") + ";")
        for i in range(12):
            stmts.append(
                f"select f{i}(a), col_{i} as out_{i} from tbl_{i} t{i} "
                f"join dim d on d.k = t{i}.k where t{i}.v >= {i * 7} "
                f"and t{i}.w in ("
                f"{', '.join(str(j) for j in range(i + 3))}) "
                f"group by 1 having count(*) > {i} "
                f"order by 2 desc limit {i + 1}"
            )
            stmts.append(
                f"with cte_{i} as (select x_{i}, y_{i} from src_{i} "
                f"where z_{i} like '%pat{i}%') "
                f"select a.x_{i} from cte_{i} a "
                f"where a.y_{i} > (select avg(y_{i}) from cte_{i})"
            )
        return stmts

    COMBOS = (
        {"style": "default"},
        {"style": "compact"},
        {"style": "pythonic"},
        {"keyword_case": "preserve", "identifier_case": "lower",
         "indent": 4},
        {"comma_style": "leading", "and_newline_group": True,
         "newline_before_major": False},
        {"select_wrap": "at_width", "wrap_column": 80,
         "keyword_case": "lower"},
        {"select_wrap": "at_width", "wrap_column": 120, "indent": 4,
         "comma_style": "leading"},
        {"style": "pythonic", "select_wrap": "none"},
        {"style": "compact", "newline_before_major": True,
         "and_newline_group": True},
    )

    def test_idempotence_and_determinism_over_corpus(self) -> None:
        corpus = self._corpus()
        self.assertGreaterEqual(len(corpus), 100)
        checked = 0
        for combo in self.COMBOS:
            for sql in corpus:
                once = _fmt(self.tool, sql, **combo)
                twice = _fmt(self.tool, once, **combo)
                again = _fmt(self.tool, sql, **combo)
                self.assertEqual(
                    twice, once,
                    msg=f"not idempotent: {combo} on {sql!r}")
                self.assertEqual(
                    again, once,
                    msg=f"not deterministic: {combo} on {sql!r}")
                checked += 1
        self.assertEqual(checked, len(corpus) * len(self.COMBOS))


class ErrorMatrixTest(unittest.TestCase):
    """Every strict-validation branch raises ValueError."""

    def setUp(self) -> None:
        self.tool = SqlFormatTool()

    def assertErr(self, snippet, **kwargs):
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        self.assertIn(
            "sql_format_tool:", str(ctx.exception),
            msg=f"{snippet}: {ctx.exception}",
        )
        return str(ctx.exception)

    def test_bad_mode(self) -> None:
        msg = self.assertErr("mode", mode="pretty", sql="select 1")
        self.assertIn("mode must be one of", msg)
        self.assertErr("mode none", mode=None, sql="select 1")

    def test_missing_sql(self) -> None:
        msg = self.assertErr("missing sql", mode="format")
        self.assertIn("sql must be a non-empty string", msg)
        self.assertErr("empty sql", mode="format", sql="   ")
        self.assertErr("non-str sql", mode="check", sql=5)
        self.assertErr("no sql check", mode="check")

    def test_styles_rejects_sql(self) -> None:
        msg = self.assertErr("styles sql", mode="styles", sql="select 1")
        self.assertIn("styles mode takes no sql", msg)

    def test_unknown_style(self) -> None:
        msg = self.assertErr("style", mode="format", sql="select 1",
                             style="gnu")
        self.assertIn("style must be one of", msg)

    def test_option_value_matrix(self) -> None:
        base = {"mode": "format", "sql": "select 1"}
        cases = [
            ("keyword_case", "Capital"),
            ("identifier_case", "upper"),
            ("indent", 3),
            ("indent", True),
            ("indent", "2"),
            ("comma_style", "both"),
            ("newline_before_major", "yes"),
            ("select_wrap", "width"),
            ("wrap_column", 79),
            ("wrap_column", 121),
            ("wrap_column", True),
            ("wrap_column", "80"),
            ("and_newline_group", 1),
        ]
        for key, value in cases:
            msg = self.assertErr(f"{key}={value!r}", **base,
                                 **{key: value})
            self.assertIn(key, msg)

    def test_multiple_statements(self) -> None:
        msg = self.assertErr("two stmts", mode="format",
                             sql="select 1; select 2")
        self.assertIn("multiple statements", msg)
        self.assertErr("mid semicolon", mode="format",
                       sql="select 1 ; select 2")
        self.assertErr("leading semicolon", mode="format",
                       sql="; select 1")

    def test_unbalanced_parens(self) -> None:
        msg = self.assertErr("unclosed", mode="format",
                             sql="select a from (select 1")
        self.assertIn("unbalanced '('", msg)
        msg = self.assertErr("extra close", mode="format",
                             sql="select 1)")
        self.assertIn("unbalanced ')'", msg)

    def test_unterminated_literals_and_comments(self) -> None:
        msg = self.assertErr("string", mode="format", sql="select 'x")
        self.assertIn("unterminated string literal", msg)
        msg = self.assertErr("qid", mode="format", sql='select "x')
        self.assertIn("unterminated quoted identifier", msg)
        msg = self.assertErr("block", mode="format", sql="select /* x")
        self.assertIn("unterminated block comment", msg)

    def test_nul_and_size_cap(self) -> None:
        msg = self.assertErr("nul", mode="format", sql="select 1\x00")
        self.assertIn("NUL", msg)
        msg = self.assertErr(
            "size", mode="format",
            sql="select " + "a" * SqlFormatTool.MAX_SQL_CHARS)
        self.assertIn("MAX_SQL_CHARS", msg)

    def test_empty_after_comments(self) -> None:
        msg = self.assertErr("comments only", mode="format",
                             sql="-- nothing here\n/* at all */")
        self.assertIn("empty after comment stripping", msg)

    def test_paren_depth_cap(self) -> None:
        depth = SqlFormatTool.MAX_PAREN_DEPTH + 1
        msg = self.assertErr(
            "depth", mode="format",
            sql="select " + "(" * depth + "1" + ")" * depth)
        self.assertIn("MAX_PAREN_DEPTH", msg)

    def test_check_validates_like_format(self) -> None:
        self.assertErr("check bad sql", mode="check",
                       sql="select 1; select 2")


if __name__ == "__main__":
    unittest.main()
