#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: sql_lint_tool.py

"""Offline heuristic SQL statement linter built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency review/QA layer for
agents that *generate* SQL. The tool never connects to a database and
never executes anything — it only examines SQL text, which no existing
common tool does: SqlLangchainTool executes queries against a
configured database and CSVQueryTool queries CSV text in memory, so
generated SQL currently reaches those executors unreviewed. SqlLintTool
sits in front of them: lint single statements, extract their shape, and
pretty-print them deterministically.

The implementation is deliberately heuristic and honest about it: no
grammar, no sqlglot / ANTLR dependency, no schema access. Input is
preprocessed once (comments stripped, string-literal contents masked
with same-length spaces so every reported offset maps 1:1 onto the
original statement), then a light token stream drives all rules. Every
rule below states exactly what triggers it; anything needing a live
schema is explicitly out of scope (see SQL012).

Single-statement contract
-------------------------
Exactly one SQL statement per call. Comments (``--`` line, ``#`` MySQL
line, ``/* ... */`` block) are ignored; one *trailing* semicolon is
tolerated; any other semicolon, an empty statement, unbalanced or
over-deeply-nested parentheses, unterminated literals or comments, and
statements over the size cap all raise ``ValueError`` before analysis.

Supported modes
---------------
* ``lint`` — run the rule table over ``sql`` and return ``ok`` plus a
  ``findings`` list. Each finding is ``{code, severity, message,
  position: {offset, line, column}, hint}`` with 1-based line/column
  and ``offset`` a character index into the original statement.
  ``ok`` is True only when no finding of severity error or warning was
  raised (info-only stays ok). Findings are sorted by offset then code
  and the run is fully deterministic.
* ``explain_structure`` — return ``{type, tables, columns, has_where,
  has_group_by, has_order_by, has_limit, limit_value, join_kinds,
  subquery_count, cte_names}``. ``type`` is the resolved statement
  type (a ``WITH`` prefix resolves to its operative SELECT / INSERT /
  UPDATE / DELETE); ``tables`` are the dotted names identified after
  FROM / JOIN (plus INSERT INTO and MERGE INTO targets and the UPDATE
  target, at any nesting depth, de-duplicated in order of appearance;
  parenthesized subquery items are not tables); ``columns`` are the
  top-level select-list items comma-split at depth 0 (normalized text,
  aliases included); ``limit_value`` is the literal LIMIT / FETCH
  FIRST row count or null (MySQL ``LIMIT o, c`` yields ``c``);
  ``join_kinds`` lists the join styles seen anywhere in order of first
  appearance (bare JOIN counts as inner); ``subquery_count`` counts
  parenthesized SELECT/WITH bodies; ``cte_names`` lists the
  ``WITH name AS (...)`` names.
* ``format`` — deterministic pretty-print: a newline before every
  top-level major clause (SELECT / FROM / WHERE / GROUP BY / HAVING /
  ORDER BY / LIMIT / OFFSET / FETCH / UNION [ALL|DISTINCT] / EXCEPT /
  INTERSECT and each JOIN family keyword run), two-space indentation
  per subquery level with the closing parenthesis returned to its
  opener's indent, single spaces elsewhere (no space before ``,`` /
  ``)`` / ``.`` / a function-call ``(`` or after ``(`` / ``.``; a unary
  minus attaches to its number; keyword-adjacent parens keep their
  space: ``IN (1, 2)``, ``COUNT(*)``). Comments are dropped — they are
  not part of the token stream; use lint positions to locate them.
  With ``uppercase_keywords`` (default True) recognized keywords are
  upper-cased and everything else stays verbatim. Formatting is
  round-trip parse-stable: ``format(format(x)) == format(x)`` and the
  token sequence is preserved, so lint findings and structure flags
  are identical before and after formatting (extracted text items such
  as select-list entries differ at most in keyword letter case).

Rule table (mode ``lint``)
--------------------------
=======================  ======  =======================================  =========================================================
Code                     Sev.    Trigger (heuristic, exact)               Hint
=======================  ======  =======================================  =========================================================
SQL001 select_star       info    ``*`` directly after SELECT, after a      enumerate the needed columns; ``SELECT *``
                                 list comma, or after a qualifier dot     breaks when the schema changes and drags
                                 (``t.*``); multiplication always has     unused columns through the pipeline
                                 an operand before it and never fires
SQL002 delete_no_where   error   statement type DELETE and no top-level   add a WHERE predicate (or an explicit
                                 WHERE                                    key-list guard) before running
SQL003 update_no_where   error   statement type UPDATE and no top-level   add a WHERE predicate (or an explicit
                                 WHERE                                    key-list guard) before running
SQL004 missing_limit     warn.   top-level SELECT without LIMIT / FETCH   add a LIMIT to bound the result size
                                 FIRST, only when the require_limit       (gated: fires only with require_limit=True)
                                 option is True
SQL005 cartesian         error   a CROSS JOIN, or a comma in a FROM       the comma join / CROSS JOIN builds the full
                                 list (any depth), whose enclosing        cross product before any filter — use an
                                 block has no WHERE at that depth         explicit JOIN ... ON
SQL006 like_prefix       warn.   LIKE / ILIKE with a literal pattern      a leading wildcard defeats the index range
                                 starting with ``%`` or ``_``             scan; consider a trigram / full-text index
SQL007 distinct_order    error   SELECT DISTINCT whose top-level ORDER    strict engines (PostgreSQL, MySQL
                                 BY names an item absent from the         ONLY_FULL_GROUP_BY) reject ordering by an
                                 select list (item text, alias and bare   unselected expression under DISTINCT
                                 column name all match; an integer
                                 item counts as positional)
SQL008 groupby_shape     warn.   GROUP BY present, the select list has     mixing grouping keys you never show with
                                 non-aggregated items, and a simple       non-aggregated select items is misleading
                                 GROUP BY column that is neither a        — align the two lists (heuristic, not a
                                 selected bare column nor a select        syntax error)
                                 alias
SQL009 in_list_size      warn.   a literal-only IN (...) list longer       a huge literal IN list is N+1-prone when
                                 than the in_list_max option (def. 20)    built in a loop — load the values into a
                                                                           temp table / VALUES join instead
SQL010 or_chain          info    or_chain_min (default 3) or more         an equality OR-chain on one column is a
                                 literal equality predicates on the       UNION ALL / IN-list shape and can defeat
                                 same column, connected only by OR        single-index plans
SQL011 mixed_lit_types   warn.   the same column is compared to both a     implicit coercion smell — verify the
                                 numeric and a string literal in one       column type and keep literal types
                                 statement (via =, <>, !=, <, >, <=,      consistent
                                 >= or IN)
SQL012 coerce_by_schema   —      *deliberately not implemented:* whether   needs the column type from a live schema;
                                 a string literal is compared to a        offline linting cannot know it. SQL011 is
                                 numeric column                           the honest offline proxy.
=======================  ======  =======================================  =========================================================

Options
-------
``require_limit`` (bool, default False) turns SQL004 on; ``in_list_max``
(int, default 20, 1..10000) bounds SQL009; ``or_chain_min`` (int,
default 3, 2..1000) bounds SQL010; ``rules`` maps any implemented rule
code to False to disable that single rule for the call (SQL012 is
documentation-only and not toggleable); ``uppercase_keywords`` (bool,
default True) drives the format mode. All options are validated before
any analysis.
"""

import re
from bisect import bisect_right
from typing import Any, ClassVar, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Static vocabulary
# ---------------------------------------------------------------------------

_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_$]*")
_NUM = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")

# Keywords recognized (case-insensitively) by the formatter.
KEYWORDS = frozenset({
    "SELECT", "FROM", "WHERE", "GROUP", "BY", "HAVING", "ORDER", "LIMIT",
    "OFFSET", "FETCH", "FIRST", "NEXT", "ROW", "ROWS", "ONLY", "UNION",
    "ALL", "EXCEPT", "INTERSECT", "JOIN", "INNER", "LEFT", "RIGHT",
    "FULL", "OUTER", "CROSS", "ON", "USING", "AS", "AND", "OR", "NOT",
    "IN", "IS", "NULL", "LIKE", "ILIKE", "BETWEEN", "EXISTS", "DISTINCT",
    "WITH", "RECURSIVE", "INSERT", "INTO", "VALUES", "UPDATE", "SET",
    "DELETE", "MERGE", "REPLACE", "TRUNCATE", "CREATE", "TABLE", "ALTER",
    "DROP", "ASC", "DESC", "CASE", "WHEN", "THEN", "ELSE", "END", "TRUE",
    "FALSE", "UNKNOWN", "NULLS", "PLAIN", "WINDOW", "FILTER",
})

# Aggregate function names (SQL008 classification).
AGG_FUNCS = frozenset({
    "COUNT", "SUM", "AVG", "MIN", "MAX", "TOTAL", "GROUP_CONCAT",
    "STRING_AGG", "ARRAY_AGG", "JSON_AGG", "JSONB_AGG", "BOOL_AND",
    "BOOL_OR", "EVERY", "ANY_VALUE", "STDDEV", "STDDEV_POP", "STDDEV_SAMP",
    "VARIANCE", "VAR_POP", "VAR_SAMP", "BIT_AND", "BIT_OR", "BIT_XOR",
})

# Statement-type keywords (first significant word of the statement).
_TYPE_WORDS = {
    "SELECT": "select", "INSERT": "insert", "UPDATE": "update",
    "DELETE": "delete", "MERGE": "merge", "REPLACE": "replace",
    "CREATE": "create", "ALTER": "alter", "DROP": "drop",
    "TRUNCATE": "truncate", "GRANT": "grant", "REVOKE": "revoke",
    "EXPLAIN": "explain", "SET": "set", "SHOW": "show", "USE": "use",
    "DESC": "desc", "DESCRIBE": "describe", "PRAGMA": "pragma",
    "VACUUM": "vacuum", "ANALYZE": "analyze", "ANALYSE": "analyze",
    "LOCK": "lock", "UNLOCK": "unlock", "CALL": "call",
    "EXECUTE": "execute", "EXEC": "exec", "BEGIN": "begin",
    "COMMIT": "commit", "ROLLBACK": "rollback", "START": "start",
    "SAVEPOINT": "savepoint", "PREPARE": "prepare",
    "DEALLOCATE": "deallocate", "DECLARE": "declare", "FETCH": "fetch",
    "CLOSE": "close", "OPEN": "open", "VALUES": "values",
    "TABLE": "table", "WITH": "with",
}
# Operative types resolvable behind a WITH prefix.
_OPERATIVE_WORDS = {
    "SELECT": "select", "INSERT": "insert", "UPDATE": "update",
    "DELETE": "delete", "MERGE": "merge", "REPLACE": "replace",
    "VALUES": "values", "TABLE": "table",
}

# One-word clause starters shared by region building and formatting.
_SIMPLE_STARTERS = frozenset({
    "SELECT", "FROM", "WHERE", "HAVING", "LIMIT", "OFFSET", "FETCH",
    "UNION", "EXCEPT", "INTERSECT", "JOIN",
})
# Region-only starters (formatting keeps these inline after their lead).
_REGION_ONLY_STARTERS = ("ON", "SET", "INTO", "WITH")
# Starters that end a query block for the WHERE hunt of SQL005.
_BLOCK_ENDERS = frozenset({
    "HAVING", "GROUP BY", "ORDER BY", "LIMIT", "OFFSET", "FETCH",
    "UNION", "EXCEPT", "INTERSECT",
})

_RULE_CODES = (
    "SQL001", "SQL002", "SQL003", "SQL004", "SQL005", "SQL006",
    "SQL007", "SQL008", "SQL009", "SQL010", "SQL011",
)

_TWO_CHAR_PUNCT = ("<=", ">=", "<>", "!=", "||", "->")

_COMPARISON_OPS = ("=", "<>", "!=", "<", ">", "<=", ">=")


def _err(message: str) -> ValueError:
    return ValueError(f"sql_lint_tool: {message}")


# ---------------------------------------------------------------------------
# Scanning: comments stripped, literal contents masked, offsets preserved
# ---------------------------------------------------------------------------

def _scan(sql: str) -> tuple[str, dict]:
    """Return ``(code, literals)`` for ``sql``.

    ``code`` has the same length as ``sql``: comment bodies and literal
    contents are replaced by spaces (newlines preserved), so a character
    offset in ``code`` maps 1:1 onto ``sql``. ``literals`` maps the
    offset of each opening quote to
    ``{end, raw, contents, quote}`` where ``raw`` spans both quotes and
    ``contents`` has doubled quotes unescaped.

    Raises:
        ValueError: On unterminated literals or block comments.
    """
    buf = list(sql)
    literals: dict = {}
    i, n = 0, len(sql)

    def _masked_span(start: int, end: int) -> None:
        for k in range(start, end):
            if buf[k] != "\n":
                buf[k] = " "

    def _scan_quoted(quote: str) -> dict:
        nonlocal i
        j = i + 1
        parts = []
        while True:
            if j >= n:
                kind = "string literal" if quote == "'" \
                    else "quoted identifier"
                raise _err(
                    f"unterminated {kind} starting at offset {i}"
                )
            if sql[j] == quote:
                if j + 1 < n and sql[j + 1] == quote:  # doubled escape
                    parts.append(quote)
                    j += 2
                    continue
                break
            parts.append(sql[j])
            j += 1
        end = j + 1
        _masked_span(i + 1, j)
        info = {
            "end": end, "raw": sql[i:end], "contents": "".join(parts),
            "quote": quote,
        }
        i = end
        return info

    while i < n:
        ch = sql[i]
        if ch == "'" or ch in ('"', "`"):
            # capture the offset before the call: _scan_quoted advances i
            offset = i
            literals[offset] = _scan_quoted(ch)
        elif ch == "-" and i + 1 < n and sql[i + 1] == "-":
            j = i
            while j < n and sql[j] != "\n":
                buf[j] = " "
                j += 1
            i = j  # keep the newline itself
        elif ch == "#":
            j = i
            while j < n and sql[j] != "\n":
                buf[j] = " "
                j += 1
            i = j
        elif ch == "/" and i + 1 < n and sql[i + 1] == "*":
            j = i + 2
            while True:
                if j + 1 >= n:
                    raise _err(
                        f"unterminated block comment starting at "
                        f"offset {i}"
                    )
                if sql[j] == "*" and sql[j + 1] == "/":
                    break
                j += 1
            _masked_span(i, j + 2)  # markers too; newlines inside kept
            i = j + 2
        else:
            i += 1
    return "".join(buf), literals


# ---------------------------------------------------------------------------
# Tokenization
# ---------------------------------------------------------------------------

def _tokenize(code: str, literals: dict) -> list:
    """Tokenize the masked ``code`` into ``{kind, text, offset, depth}``.

    Kinds: ``word``, ``num``, ``str`` (single-quoted, raw text from the
    literal registry), ``qid`` (double-quoted / backtick), ``punct``.
    Parentheses of a pair carry the same depth; enclosed tokens are one
    deeper.
    """
    tokens: list = []
    depth = 0
    i, n = 0, len(code)
    while i < n:
        ch = code[i]
        if ch.isspace():
            i += 1
            continue
        if ch in ("'", '"', "`"):
            lit = literals[i]
            tokens.append({
                "kind": "str" if ch == "'" else "qid",
                "text": lit["raw"],
                "offset": i,
                "depth": depth,
            })
            i = lit["end"]
            continue
        m = _WORD.match(code, i) or _NUM.match(code, i)
        if m:
            tokens.append({
                "kind": "word" if ch.isalpha() or ch == "_" else "num",
                "text": m.group(0),
                "offset": i,
                "depth": depth,
            })
            i = m.end()
            continue
        two = code[i:i + 2]
        if two in _TWO_CHAR_PUNCT:
            tokens.append({
                "kind": "punct", "text": two, "offset": i, "depth": depth,
            })
            i += 2
            continue
        if ch == "(":
            tokens.append({
                "kind": "punct", "text": "(", "offset": i, "depth": depth,
            })
            depth += 1
        elif ch == ")":
            depth -= 1
            tokens.append({
                "kind": "punct", "text": ")", "offset": i, "depth": depth,
            })
        else:
            tokens.append({
                "kind": "punct", "text": ch, "offset": i, "depth": depth,
            })
        i += 1
    return tokens


# ---------------------------------------------------------------------------
# Starter detection (clause keywords / join families)
# ---------------------------------------------------------------------------

def _starter_at(tokens: list, i: int, *, for_format: bool = False):
    """Return ``(name, raw, length)`` if a clause starter begins at ``i``.

    ``name`` is the canonical clause name (``GROUP BY``, ``JOIN`` …) and
    ``raw`` the matched keyword text (``CROSS JOIN``, ``LEFT JOIN`` …).
    Region building additionally treats ON / SET / INTO / WITH as
    starters; formatting keeps ON inline after its JOIN and treats WITH
    as plain text (its subquery bodies still indent).
    """
    token = tokens[i]
    if token["kind"] != "word":
        return None
    w = token["text"].upper()
    orig = token["text"]
    depth = token["depth"]

    def _word_at(j: int) -> str:
        if 0 <= j < len(tokens) and tokens[j]["kind"] == "word" \
                and tokens[j]["depth"] == depth:
            return tokens[j]["text"].upper()
        return ""

    if w in ("GROUP", "ORDER"):
        if _word_at(i + 1) == "BY":
            return (f"{w} BY", f"{orig} {tokens[i + 1]['text']}", 2)
        return None
    if w in _SIMPLE_STARTERS:
        if w == "UNION" and _word_at(i + 1) in ("ALL", "DISTINCT"):
            return ("UNION", f"{orig} {tokens[i + 1]['text']}", 2)
        return (w, orig, 1)
    if w in ("INNER", "LEFT", "RIGHT", "FULL", "CROSS", "OUTER"):
        j = i + 1
        words = [orig]
        while _word_at(j) == "OUTER":
            words.append(tokens[j]["text"])
            j += 1
        if _word_at(j) == "JOIN":
            words.append(tokens[j]["text"])
            return ("JOIN", " ".join(words), j + 1 - i)
        return None
    if not for_format and w in _REGION_ONLY_STARTERS:
        return (w, orig, 1)
    return None


def _regions(tokens: list) -> list:
    """Clause regions at every depth, in order of appearance."""
    regions: list = []
    i = 0
    while i < len(tokens):
        started = _starter_at(tokens, i)
        if started is None:
            i += 1
            continue
        name, raw, length = started
        depth = tokens[i]["depth"]
        j = i + length
        while j < len(tokens):
            if tokens[j]["depth"] < depth:
                break
            if tokens[j]["depth"] == depth and \
                    _starter_at(tokens, j) is not None:
                break
            j += 1
        regions.append({
            "name": name, "raw": raw, "depth": depth,
            "start": i, "kw_len": length, "end": j,
            "offset": tokens[i]["offset"],
        })
        i += length
    return regions


# ---------------------------------------------------------------------------
# Small helpers over token spans
# ---------------------------------------------------------------------------

def _norm_text(span: list) -> str:
    parts: list = []
    for t in span:
        text = t["text"]
        if parts:
            prev = parts[-1]
            glue = (
                text in (".", ")")
                or prev in (".", "(")
                or (text == "(" and prev not in KEYWORDS)  # COUNT(*)
            )
            if not glue:
                parts.append(" ")
        parts.append(text)
    return "".join(parts)


def _upper_text(span: list) -> str:
    parts: list = []
    for t in span:
        text = t["text"].upper() if t["kind"] == "word" else t["text"]
        if parts and parts[-1] != "." and text != ".":
            parts.append(" ")
        parts.append(text)
    return "".join(parts)


def _split_top_commas(span: list, depth: int) -> list:
    """Split a token span on commas sitting exactly at ``depth``."""
    items: list = []
    current: list = []
    for t in span:
        if t["kind"] == "punct" and t["text"] == "," and t["depth"] == depth:
            items.append(current)
            current = []
        else:
            current.append(t)
    items.append(current)
    return [item for item in items if item]


def _is_simple_col(span: list) -> bool:
    """True for ``col`` / ``t.col`` / ``db.t.col`` shapes."""
    expect_word = True
    for t in span:
        if expect_word:
            if t["kind"] != "word":
                return False
            expect_word = False
        else:
            if t["kind"] != "punct" or t["text"] != ".":
                return False
            expect_word = True
    return not expect_word


def _col_name(span: list) -> str:
    if span and span[-1]["kind"] == "word":
        return span[-1]["text"].upper()
    return ""


def _dotted_chain(span: list) -> str:
    """Leading ``a.b.c`` chain of a span, verbatim."""
    chain: list = []
    i = 0
    while i < len(span):
        t = span[i]
        if t["kind"] == "word":
            chain.append(t["text"])
            if i + 1 < len(span) and span[i + 1]["kind"] == "punct" \
                    and span[i + 1]["text"] == ".":
                chain.append(".")
                i += 2
                continue
            break
        break
    return "".join(chain)


def _alias_of(span: list) -> str:
    """Trailing ``AS alias`` of a select item (implicit aliases not
    guessed — SQL008/SQL007 document that)."""
    words = [(t["text"], i) for i, t in enumerate(span)
             if t["kind"] == "word"]
    for pos, (text, _) in enumerate(words):
        if text.upper() == "AS" and pos + 1 < len(words):
            return words[pos + 1][0]
    return ""


def _strip_alias(span: list) -> list:
    """Drop a trailing ``AS alias`` (or a lone trailing alias word after
    a function call) from a select item's tokens."""
    if len(span) >= 2 and span[-2]["kind"] == "word" and \
            span[-2]["text"].upper() == "AS":
        return span[:-2]
    return span


def _is_agg_item(span: list) -> bool:
    """True when the whole item is one aggregate call (+ ``AS`` alias)."""
    if not span or span[0]["kind"] != "word" or \
            span[0]["text"].upper() not in AGG_FUNCS:
        return False
    i = 1
    if i >= len(span) or span[i]["text"] != "(":
        return False
    open_depth = span[i]["depth"]
    closed = False
    while i < len(span):
        t = span[i]
        if t["kind"] == "punct" and t["text"] == ")" \
                and t["depth"] == open_depth:
            closed = True
            i += 1
            break
        i += 1
    if not closed:
        return False
    rest = span[i:]
    if not rest:
        return True
    if len(rest) == 1 and rest[0]["kind"] == "word":
        return True  # COUNT(*) total — implicit alias shape
    if len(rest) == 2 and rest[0]["kind"] == "word" and \
            rest[0]["text"].upper() == "AS":
        return True
    return False


def _literal_kind(token: dict) -> str:
    """'number' | 'string' | 'null' | 'bool' | '' for non-literals."""
    if token["kind"] == "num":
        return "number"
    if token["kind"] == "str":
        return "string"
    if token["kind"] == "word":
        w = token["text"].upper()
        if w == "NULL":
            return "null"
        if w in ("TRUE", "FALSE"):
            return "bool"
    return ""


def _is_subquery_paren(tokens: list, i: int) -> bool:
    """True when token ``i`` is '(' opening a SELECT/WITH subquery."""
    t = tokens[i]
    if t["kind"] != "punct" or t["text"] != "(":
        return False
    if i + 1 >= len(tokens):
        return False
    nxt = tokens[i + 1]
    return nxt["kind"] == "word" and nxt["text"].upper() in ("SELECT",
                                                              "WITH")


# ---------------------------------------------------------------------------
# Statement level: type resolution and structure
# ---------------------------------------------------------------------------

def _statement_type(tokens: list) -> tuple:
    """Return ``(type, operative_token_index)`` for the token stream."""
    i = 0
    while i < len(tokens) and tokens[i]["kind"] == "punct" \
            and tokens[i]["text"] == "(":
        i += 1
    if i >= len(tokens) or tokens[i]["kind"] != "word":
        return "other", min(i, len(tokens) - 1)
    first = tokens[i]["text"].upper()
    if first != "WITH":
        return _TYPE_WORDS.get(first, "other"), i
    # WITH prefix: walk the depth-0 CTE definitions, then the first
    # operative word at that depth.
    d = tokens[i]["depth"]
    j = i + 1
    if j < len(tokens) and tokens[j]["kind"] == "word" and \
            tokens[j]["text"].upper() == "RECURSIVE":
        j += 1
    while j < len(tokens):
        t = tokens[j]
        if t["depth"] != d:
            j += 1
            continue
        if t["kind"] == "word" and t["text"].upper() in _OPERATIVE_WORDS:
            return _OPERATIVE_WORDS[t["text"].upper()], j
        if (t["kind"] == "word" and j + 2 < len(tokens)
                and tokens[j + 1]["kind"] == "word"
                and tokens[j + 1]["text"].upper() == "AS"
                and tokens[j + 2]["kind"] == "punct"
                and tokens[j + 2]["text"] == "("):
            open_depth = tokens[j + 2]["depth"]
            k = j + 3
            while k < len(tokens):
                if tokens[k]["kind"] == "punct" and tokens[k]["text"] == ")"\
                        and tokens[k]["depth"] == open_depth:
                    break
                k += 1
            j = k + 1
            if j < len(tokens) and tokens[j]["kind"] == "punct" \
                    and tokens[j]["text"] == ",":
                j += 1
            continue
        j += 1
    return "with", i


def _tables(tokens: list, regions: list, stmt_type: str) -> list:
    """Dotted table names from FROM/JOIN/INTO regions (+ UPDATE target)."""
    tables: list = []
    seen: set = set()
    for region in regions:
        if region["name"] not in ("FROM", "JOIN", "INTO"):
            continue
        body = tokens[region["start"] + region["kw_len"]:region["end"]]
        for item in _split_top_commas(body, region["depth"]):
            name = _dotted_chain(item)
            if name and name not in seen:
                seen.add(name)
                tables.append(name)
    if stmt_type == "update":
        i = 0
        while i < len(tokens) and tokens[i]["kind"] == "punct" \
                and tokens[i]["text"] == "(":
            i += 1
        if i + 1 < len(tokens) and tokens[i]["kind"] == "word" and \
                tokens[i]["text"].upper() == "UPDATE" and \
                tokens[i + 1]["kind"] == "word":
            name = _dotted_chain(tokens[i + 1:])
            if name and name not in seen:
                seen.add(name)
                tables.append(name)
    return tables


def _select_items(tokens: list, select_region: dict) -> list:
    """Comma-split items of a SELECT region, past DISTINCT/ALL."""
    start = select_region["start"] + 1
    end = select_region["end"]
    first = tokens[start] if start < end else None
    if first is not None and first["kind"] == "word" and \
            first["text"].upper() in ("DISTINCT", "ALL"):
        start += 1
    return _split_top_commas(tokens[start:end], select_region["depth"])


def _structure(tokens: list, regions: list, stmt_type: str) -> dict:
    depth0 = [r for r in regions if r["depth"] == 0]

    columns: list = []
    selects = [r for r in depth0 if r["name"] == "SELECT"]
    if selects:
        columns = [_norm_text(item) for item in
                   _select_items(tokens, selects[0])]

    subquery_count = sum(1 for i in range(len(tokens))
                         if _is_subquery_paren(tokens, i))

    cte_names: list = []
    for r in depth0:
        if r["name"] != "WITH":
            continue
        body = tokens[r["start"] + 1:r["end"]]
        d = r["depth"]
        k = 0
        if body and body[k]["kind"] == "word" and \
                body[k]["text"].upper() == "RECURSIVE":
            k += 1
        while k < len(body):
            t = body[k]
            if t["kind"] != "word" or t["depth"] != d:
                k += 1
                continue
            nxt = k + 1
            # optional column list: name ( a, b ) AS ( ... )
            if nxt < len(body) and body[nxt]["kind"] == "punct" and \
                    body[nxt]["text"] == "(":
                open_depth = body[nxt]["depth"]
                while nxt < len(body) and not (
                    body[nxt]["kind"] == "punct" and
                    body[nxt]["text"] == ")" and
                    body[nxt]["depth"] == open_depth
                ):
                    nxt += 1
                nxt += 1
            if (nxt + 1 < len(body)
                    and body[nxt]["kind"] == "word"
                    and body[nxt]["text"].upper() == "AS"
                    and body[nxt + 1]["kind"] == "punct"
                    and body[nxt + 1]["text"] == "("):
                if t["text"] not in cte_names:
                    cte_names.append(t["text"])
                open_depth = body[nxt + 1]["depth"]
                nxt += 2
                while nxt < len(body) and not (
                    body[nxt]["kind"] == "punct" and
                    body[nxt]["text"] == ")" and
                    body[nxt]["depth"] == open_depth
                ):
                    nxt += 1
                k = nxt + 1
                if k < len(body) and body[k]["text"] == ",":
                    k += 1
            else:
                k += 1

    join_kinds: list = []
    for r in regions:
        if r["name"] != "JOIN":
            continue
        kind = r["raw"].split()[0].lower()
        if kind == "join":
            kind = "inner"
        if kind not in join_kinds:
            join_kinds.append(kind)

    limit_regions = [r for r in depth0 if r["name"] == "LIMIT"]
    fetch_regions = [r for r in depth0 if r["name"] == "FETCH"]
    has_limit = bool(limit_regions or fetch_regions)
    limit_value = None
    if has_limit:
        if limit_regions:
            body = tokens[limit_regions[-1]["start"] +
                          limit_regions[-1]["kw_len"]:
                        limit_regions[-1]["end"]]
            nums = [t for t in body if t["kind"] == "num"]
            commas = [t for t in body if t["text"] == ","]
            if len(nums) == 2 and commas:  # MySQL LIMIT offset, count
                limit_value = int(float(nums[1]["text"]))
            elif len(nums) == 1:
                limit_value = int(float(nums[0]["text"]))
        else:
            body = tokens[fetch_regions[-1]["start"] +
                          fetch_regions[-1]["kw_len"]:
                        fetch_regions[-1]["end"]]
            nums = [t for t in body if t["kind"] == "num"]
            limit_value = int(float(nums[0]["text"])) if nums else 1

    return {
        "type": stmt_type,
        "tables": _tables(tokens, regions, stmt_type),
        "columns": columns,
        "has_where": any(r["name"] == "WHERE" for r in depth0),
        "has_group_by": any(r["name"] == "GROUP BY" for r in depth0),
        "has_order_by": any(r["name"] == "ORDER BY" for r in depth0),
        "has_limit": has_limit,
        "limit_value": limit_value,
        "join_kinds": join_kinds,
        "subquery_count": subquery_count,
        "cte_names": cte_names,
    }


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

def _block_has_where(tokens: list, start: int, depth: int) -> bool:
    """Whether the query block continuing at ``start`` has a WHERE."""
    j = start
    while j < len(tokens):
        t = tokens[j]
        if t["depth"] < depth:
            return False
        if t["depth"] == depth:
            if t["kind"] == "word" and t["text"].upper() == "WHERE":
                return True
            starter = _starter_at(tokens, j)
            if starter is not None and starter[0] in _BLOCK_ENDERS:
                return False
        j += 1
    return False


def _rule_select_star(tokens: list) -> list:
    out = []
    for i, t in enumerate(tokens):
        if t["kind"] != "punct" or t["text"] != "*":
            continue
        prev = tokens[i - 1] if i else None
        if prev and prev["kind"] == "word" and \
                prev["text"].upper() == "SELECT":
            pass  # SELECT *
        elif prev and prev["text"] in (",", "."):
            pass   # a, * or t.*
        else:
            continue
        out.append((t["offset"], {
            "code": "SQL001", "severity": "info",
            "message": "SELECT * star (after SELECT, a comma or a "
                       "qualifier dot)",
            "hint": "enumerate the needed columns; SELECT * breaks when "
                    "the schema changes and drags unused columns "
                    "through the pipeline",
        }))
    return out


def _rule_no_where(tokens: list, regions: list, stmt_type: str,
                   type_index: int) -> list:
    depth0 = [r for r in regions if r["depth"] == 0]
    if any(r["name"] == "WHERE" for r in depth0):
        return []
    out = []
    for want, code, word in (
        ("delete", "SQL002", "DELETE"),
        ("update", "SQL003", "UPDATE"),
    ):
        if stmt_type == want:
            out.append((tokens[type_index]["offset"], {
                "code": code, "severity": "error",
                "message": f"{word} statement without a WHERE clause",
                "hint": "add a WHERE predicate (or an explicit key-list "
                        "guard) before running",
            }))
    return out


def _rule_missing_limit(tokens: list, regions: list, stmt_type: str,
                        type_index: int, require_limit: bool) -> list:
    if not require_limit or stmt_type != "select":
        return []
    depth0 = [r for r in regions if r["depth"] == 0]
    if any(r["name"] in ("LIMIT", "FETCH") for r in depth0):
        return []
    selects = [r for r in depth0 if r["name"] == "SELECT"]
    offset = selects[0]["offset"] if selects \
        else tokens[type_index]["offset"]
    return [(offset, {
        "code": "SQL004", "severity": "warning",
        "message": "top-level SELECT without LIMIT / FETCH FIRST "
                   "(require_limit option is on)",
        "hint": "add a LIMIT to bound the result size",
    })]


def _rule_cartesian(tokens: list, regions: list) -> list:
    out = []
    for region in regions:
        if region["name"] == "JOIN" and \
                region["raw"].upper() == "CROSS JOIN":
            if not _block_has_where(tokens, region["end"], region["depth"]):
                out.append((region["offset"], {
                    "code": "SQL005", "severity": "error",
                    "message": "CROSS JOIN in a query block without WHERE",
                    "hint": "the cross join builds the full cartesian "
                            "product before any filter — use an explicit "
                            "JOIN ... ON",
                }))
        elif region["name"] == "FROM":
            body = tokens[region["start"] + region["kw_len"]:region["end"]]
            commas = [t for t in body if t["text"] == "," and
                      t["depth"] == region["depth"]]
            if commas and not _block_has_where(tokens, region["end"],
                                               region["depth"]):
                out.append((commas[0]["offset"], {
                    "code": "SQL005", "severity": "error",
                    "message": "comma-separated FROM list (implicit "
                               "cross join) in a query block without "
                               "WHERE",
                    "hint": "comma joins build the full cross product "
                            "before any filter — use an explicit "
                            "JOIN ... ON",
                }))
    return out


def _rule_like_prefix(tokens: list) -> list:
    out = []
    for i, t in enumerate(tokens):
        if t["kind"] != "word" or t["text"].upper() not in ("LIKE",
                                                            "ILIKE"):
            continue
        if i + 1 < len(tokens) and tokens[i + 1]["kind"] == "str":
            contents = tokens[i + 1]["text"][1:-1].replace("''", "'")
            if contents[:1] in ("%", "_"):
                out.append((tokens[i + 1]["offset"], {
                    "code": "SQL006", "severity": "warning",
                    "message": f"LIKE pattern starts with a wildcard "
                               f"({contents[:8]!r})",
                    "hint": "a leading wildcard defeats the index range "
                            "scan; consider a trigram or full-text "
                            "index",
                }))
    return out


def _select_is_distinct(tokens: list, select_region: dict) -> bool:
    first = tokens[select_region["start"] + 1] \
        if select_region["start"] + 1 < select_region["end"] else None
    return first is not None and first["kind"] == "word" and \
        first["text"].upper() == "DISTINCT"


def _rule_distinct_order(tokens: list, regions: list) -> list:
    out = []
    depth0 = [r for r in regions if r["depth"] == 0]
    last_select = None
    for region in depth0:
        if region["name"] == "SELECT":
            last_select = region
            continue
        if region["name"] != "ORDER BY" or last_select is None:
            continue
        if not _select_is_distinct(tokens, last_select):
            continue
        matchable: set = set()
        for item in _select_items(tokens, last_select):
            matchable.add(_upper_text(item))
            alias = _alias_of(item)
            if alias:
                matchable.add(alias.upper())
            bare = _strip_alias(item)
            if _is_simple_col(bare):
                matchable.add(_col_name(bare))
        body = tokens[region["start"] + region["kw_len"]:region["end"]]
        for item in _split_top_commas(body, region["depth"]):
            trimmed = list(item)
            while trimmed and trimmed[-1]["kind"] == "word" and \
                    trimmed[-1]["text"].upper() in (
                        "ASC", "DESC", "NULLS", "FIRST", "LAST"):
                trimmed.pop()
            if not trimmed:
                continue
            if len(trimmed) == 1 and trimmed[0]["kind"] == "num":
                continue  # positional ORDER BY
            if _upper_text(trimmed) in matchable or \
                    (_is_simple_col(trimmed) and
                     _col_name(trimmed) in matchable):
                continue
            out.append((region["offset"], {
                "code": "SQL007", "severity": "error",
                "message": "SELECT DISTINCT with ORDER BY on "
                           f"{_norm_text(item)!r} which is not in the "
                           "select list",
                "hint": "strict engines reject ordering by an "
                        "expression that is not selected under "
                        "DISTINCT — add it to the select list or drop "
                        "the ordering",
            }))
            break
    return out


def _rule_groupby_shape(tokens: list, regions: list) -> list:
    out = []
    depth0 = [r for r in regions if r["depth"] == 0]
    last_select = None
    for region in depth0:
        if region["name"] == "SELECT":
            last_select = region
            continue
        if region["name"] != "GROUP BY" or last_select is None:
            continue
        nonagg_names: set = set()
        has_nonagg = False
        for item in _select_items(tokens, last_select):
            if _is_agg_item(item):
                continue
            has_nonagg = True
            alias = _alias_of(item)
            if alias:
                nonagg_names.add(alias.upper())
            bare = _strip_alias(item)
            if _is_simple_col(bare):
                nonagg_names.add(_col_name(bare))
        if not has_nonagg:
            continue
        body = tokens[region["start"] + region["kw_len"]:region["end"]]
        for item in _split_top_commas(body, region["depth"]):
            if not _is_simple_col(item):
                continue  # expressions / positional items: out of scope
            if _col_name(item) in nonagg_names:
                continue
            out.append((item[0]["offset"], {
                "code": "SQL008", "severity": "warning",
                "message": f"GROUP BY column {_norm_text(item)!r} is "
                           "not in the select list while the select "
                           "list has non-aggregated items",
                "hint": "grouping on keys you never show next to "
                        "non-aggregated items is misleading — align "
                        "the GROUP BY and select lists (heuristic, "
                        "not a syntax error)",
            }))
    return out


def _rule_in_list_size(tokens: list, in_list_max: int) -> list:
    out = []
    for i, t in enumerate(tokens):
        if t["kind"] != "word" or t["text"].upper() != "IN":
            continue
        if i + 1 >= len(tokens) or tokens[i + 1]["text"] != "(":
            continue
        open_tok = tokens[i + 1]
        j = i + 2
        count = 0
        all_literal = True
        while j < len(tokens) and not (
            tokens[j]["kind"] == "punct" and tokens[j]["text"] == ")"
            and tokens[j]["depth"] == open_tok["depth"]
        ):
            t2 = tokens[j]
            if t2["text"] == "," and t2["depth"] == open_tok["depth"] + 1:
                j += 1
                continue
            if t2["depth"] == open_tok["depth"] + 1 and \
                    _literal_kind(t2) in ("number", "string", "null"):
                count += 1
                j += 1
                continue
            all_literal = False
            break
        if all_literal and count > in_list_max:
            out.append((t["offset"], {
                "code": "SQL009", "severity": "warning",
                "message": f"literal-only IN list with {count} items "
                           f"(threshold {in_list_max})",
                "hint": "a huge literal IN list is N+1-prone when built "
                        "in a loop — load the values into a temp table "
                        "or a VALUES join instead",
            }))
    return out


def _iter_predicates(tokens: list, regions: list):
    """Yield ``(col_norm, literal_kind, offset)`` literal comparisons.

    Walks WHERE / ON / HAVING / SET clause regions at any depth; a
    predicate is ``col (=, <>, !=, <, >, <=, >=) literal`` or
    ``col IN (literal, ...)`` with col a simple (optionally dotted)
    column at the clause's own depth.
    """
    for region in regions:
        if region["name"] not in ("WHERE", "ON", "HAVING", "SET"):
            continue
        d = region["depth"]
        body = tokens[region["start"] + region["kw_len"]:region["end"]]
        i = 0
        while i < len(body):
            t = body[i]
            if t["depth"] != d or t["kind"] != "word":
                i += 1
                continue
            j = i
            while j + 2 < len(body) and body[j + 1]["text"] == "." and \
                    body[j + 2]["kind"] == "word":
                j += 2
            col_tokens = body[i:j + 1]
            if not _is_simple_col(col_tokens):
                i += 1
                continue
            col_norm = _upper_text(col_tokens)
            k = j + 1
            if k < len(body) and body[k]["depth"] == d:
                nxt = body[k + 1] if k + 1 < len(body) else None
                if body[k]["kind"] == "punct" and \
                        body[k]["text"] in _COMPARISON_OPS and nxt \
                        and nxt["depth"] == d and _literal_kind(nxt):
                    yield col_norm, _literal_kind(nxt), body[i]["offset"]
                    i = k + 2
                    continue
                if body[k]["kind"] == "word" and \
                        body[k]["text"].upper() == "IN" and nxt and \
                        nxt["text"] == "(":
                    open_depth = nxt["depth"]
                    m = k + 2
                    while m < len(body) and not (
                        body[m]["text"] == ")" and
                        body[m]["depth"] == open_depth
                    ):
                        if body[m]["depth"] == open_depth + 1 and \
                                _literal_kind(body[m]):
                            yield (col_norm, _literal_kind(body[m]),
                                   body[i]["offset"])
                        m += 1
                    i = m + 1
                    continue
            i = j + 1


def _match_or_pred(body: list, i: int):
    """Match ``col = lit (OR col = lit)*`` at ``i`` → [(col, off, nxt)]."""
    run: list = []
    pos = i
    while True:
        j = pos
        if j >= len(body) or body[j]["kind"] != "word":
            return run or None
        while j + 2 < len(body) and body[j + 1]["text"] == "." and \
                body[j + 2]["kind"] == "word":
            j += 2
        col_tokens = body[pos:j + 1]
        if not _is_simple_col(col_tokens):
            return run or None
        k = j + 1
        if k + 1 >= len(body) or body[k]["text"] != "=" or \
                body[k]["depth"] != body[pos]["depth"] or \
                not _literal_kind(body[k + 1]):
            return run or None
        nxt = k + 2
        run.append((_upper_text(col_tokens), body[pos]["offset"], nxt))
        if nxt < len(body) and body[nxt]["kind"] == "word" and \
                body[nxt]["text"].upper() == "OR":
            pos = nxt + 1
            continue
        return run


def _rule_or_chain(tokens: list, regions: list, or_chain_min: int) -> list:
    out = []
    for region in regions:
        if region["name"] not in ("WHERE", "ON", "HAVING"):
            continue
        d = region["depth"]
        body = [t for t in
                tokens[region["start"] + region["kw_len"]:region["end"]]
                if t["depth"] == d]
        i = 0
        while i < len(body):
            run = _match_or_pred(body, i)
            if run is None:
                i += 1
                continue
            cols = {c for c, _, _ in run}
            if len(run) >= or_chain_min and len(cols) == 1:
                out.append((run[0][1], {
                    "code": "SQL010", "severity": "info",
                    "message": f"{len(run)} literal equality predicates "
                               f"on {sorted(cols)[0]} connected only "
                               f"by OR",
                    "hint": "an equality OR-chain on one column is a "
                            "UNION ALL / IN-list shape and can defeat "
                            "single-index plans",
                }))
            i = run[-1][2]
    return out


def _rule_mixed_lit_types(tokens: list, regions: list) -> list:
    seen: dict = {}
    for col_norm, kind, offset in _iter_predicates(tokens, regions):
        if kind not in ("number", "string"):
            continue
        seen.setdefault(col_norm, {}).setdefault(kind, offset)
    out = []
    for col_norm in sorted(seen):
        kinds = seen[col_norm]
        if "number" in kinds and "string" in kinds:
            out.append((max(kinds.values()), {
                "code": "SQL011", "severity": "warning",
                "message": f"column {col_norm} is compared to both "
                           "numeric and string literals",
                "hint": "implicit coercion smell — verify the column "
                        "type and keep literal types consistent",
            }))
    return out


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _format(tokens: list, uppercase: bool) -> str:
    """Deterministic pretty-print of the token stream (see docstring)."""
    lines: list = []
    current: list = []
    subquery_depths: list = []

    def indent() -> str:
        return "  " * len(subquery_depths)

    def newline() -> None:
        text = "".join(current)
        if text.strip():
            lines.append(text)
        current.clear()

    def emit(text: str) -> None:
        if current:
            current.append(" ")
        current.append(text)

    i = 0
    n = len(tokens)
    prev_token: Optional[dict] = None
    no_space_next = False
    while i < n:
        t = tokens[i]
        starter = _starter_at(tokens, i, for_format=True)
        body_depth = subquery_depths[-1] + 1 if subquery_depths else 0
        if starter is not None and t["depth"] == body_depth:
            newline()
            current.append(indent())
            current.append(starter[1] if not uppercase
                           else starter[1].upper())
            i += starter[2]
            no_space_next = False
            prev_token = None
            continue
        if _is_subquery_paren(tokens, i):
            if current and current[-1] and not current[-1].endswith(" "):
                current.append(" ")
            current.append("(")
            newline()
            subquery_depths.append(t["depth"])
            i += 1
            no_space_next = False
            prev_token = t
            continue
        if t["text"] == ")" and subquery_depths and \
                t["depth"] == subquery_depths[-1]:
            newline()
            subquery_depths.pop()
            current.append(indent())
            current.append(")")
            i += 1
            no_space_next = False
            prev_token = t
            continue

        text = t["text"]
        if uppercase and t["kind"] == "word" and \
                t["text"].upper() in KEYWORDS:
            text = text.upper()
        if t["kind"] == "num" and text.startswith("."):
            text = "0" + text  # .5 -> 0.5 keeps re-parsing stable

        piece = text
        space = True
        minus_glue = False
        if piece in (",", ")", ".", ";"):
            space = False
        elif piece == "(":
            space = not (prev_token is not None and (
                prev_token["kind"] in ("num", "str", "qid")
                or (prev_token["kind"] == "punct" and
                    prev_token["text"] in (")",))
                or (prev_token["kind"] == "word" and
                    prev_token["text"].upper() not in KEYWORDS)
            ))
        elif piece == "-" and i + 1 < n and tokens[i + 1]["kind"] == "num":
            # unary minus: always glued to its number ("= -3", "* -1",
            # "(-1)"); a space before the sign survives except directly
            # after an opening parenthesis
            minus_glue = True
            space = not no_space_next and (prev_token is None or
                                           prev_token["text"] != "(")
        if no_space_next:
            space = False

        if current and space:
            current.append(" ")
        current.append(piece)
        no_space_next = piece in ("(", ".") or minus_glue
        prev_token = t
        i += 1
    newline()
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class SqlLintTool(Tool):
    """Offline heuristic linter / structure extractor / formatter for
    single SQL statements, built purely on the stdlib.

    The tool never connects to a database, never executes SQL and needs
    no schema — it reviews SQL *text*: lint it against the documented
    rule table, explain its structure, or pretty-print it. See the
    module docstring for the full rule table, mode reference and the
    honest-heuristics notes.

    Class attributes:
        MAX_SQL_CHARS (int): Upper bound on the statement length.
        MAX_PAREN_DEPTH (int): Upper bound on parenthesis nesting.
        DEFAULT_IN_LIST_MAX (int): Default SQL009 threshold.
        DEFAULT_OR_CHAIN_MIN (int): Default SQL010 threshold.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "sql_lint_tool"
    description: str = (
        "Offline heuristic SQL statement linting tool — pure Python "
        "stdlib, no database, no execution, no schema access. Lints a "
        "single SQL statement against a documented ~12-rule table "
        "(mode='lint': SELECT *, DELETE/UPDATE without WHERE, missing "
        "LIMIT when require_limit is on, cross/comma joins without "
        "WHERE, LIKE leading wildcards, DISTINCT+ORDER BY on "
        "non-selected columns, GROUP BY / select-list shape, oversized "
        "literal IN lists, OR chains vs UNION, mixed literal types; "
        "schema-dependent coercion is documented as out of scope), "
        "extracts statement structure (mode='explain_structure': type, "
        "tables, columns, where/group/order/limit flags, join kinds, "
        "subquery count, CTE names) and pretty-prints deterministically "
        "(mode='format': newline before major clauses, 2-space subquery "
        "indent, optional keyword upper-casing, round-trip stable). "
        "String-literal contents and comments are masked before any "
        "keyword scanning, and findings carry exact offsets and 1-based "
        "line/column positions."
    )

    MODES: ClassVar[tuple] = ("lint", "explain_structure", "format")
    RULE_CODES: ClassVar[tuple] = _RULE_CODES
    MAX_SQL_CHARS: ClassVar[int] = 20_000
    MAX_PAREN_DEPTH: ClassVar[int] = 64
    DEFAULT_IN_LIST_MAX: ClassVar[int] = 20
    DEFAULT_OR_CHAIN_MIN: ClassVar[int] = 3

    def execute(
        self,
        mode: Any = None,
        sql: Any = None,
        require_limit: Any = None,
        rules: Any = None,
        in_list_max: Any = None,
        or_chain_min: Any = None,
        uppercase_keywords: Any = None,
    ) -> dict:
        """Lint, explain or format a single SQL statement.

        Args:
            mode (str): One of ``lint``, ``explain_structure`` or
                ``format``.
            sql (str): The single SQL statement. Comments are ignored
                (``--``, ``#``, ``/* ... */``), one trailing semicolon
                is tolerated, anything beyond that violates the
                single-statement contract.
            require_limit (bool): Turn rule SQL004 on. Default False.
            rules (dict): Map a rule code (SQL001..SQL011) to False to
                disable that rule for this call.
            in_list_max (int): SQL009 literal IN list threshold.
                Default 20, range 1..10000.
            or_chain_min (int): SQL010 minimum OR-chain length.
                Default 3, range 2..1000.
            uppercase_keywords (bool): Uppercase keywords in the format
                mode. Default True.

        Returns:
            dict: ``lint`` → ``{mode, ok, statement_type, finding_count,
            findings, rules_disabled}`` with each finding ``{code,
            severity, message, position: {offset, line, column}, hint}``;
            ``explain_structure`` → ``{mode, type, tables, columns,
            has_where, has_group_by, has_order_by, has_limit,
            limit_value, join_kinds, subquery_count, cte_names}``;
            ``format`` → ``{mode, result, statement_type, line_count}``
            with a round-trip parse-stable pretty-print.

        Raises:
            ValueError: If any argument is malformed or the statement
                violates the single-statement contract (multiple
                statements, unbalanced / over-nested parens, unterminated
                literals or comments, size cap).
        """
        if mode not in self.MODES:
            raise _err(f"mode must be one of {self.MODES}, got {mode!r}")

        if rules is None:
            rules = {}
        if not isinstance(rules, dict):
            raise _err(f"rules must be a dict, got {type(rules).__name__}")
        disabled: set = set()
        for key, value in rules.items():
            if key not in _RULE_CODES:
                raise _err(
                    f"rules keys must be one of {list(_RULE_CODES)}, "
                    f"got {key!r}"
                )
            if not isinstance(value, bool):
                raise _err(
                    f"rules[{key!r}] must be a bool, got "
                    f"{type(value).__name__}"
                )
            if not value:
                disabled.add(key)

        if require_limit is None:
            require_limit = False
        if not isinstance(require_limit, bool):
            raise _err("require_limit must be a bool, got "
                       f"{type(require_limit).__name__}")
        if uppercase_keywords is None:
            uppercase_keywords = True
        if not isinstance(uppercase_keywords, bool):
            raise _err("uppercase_keywords must be a bool, got "
                       f"{type(uppercase_keywords).__name__}")
        if in_list_max is None:
            in_list_max = self.DEFAULT_IN_LIST_MAX
        if not isinstance(in_list_max, int) or isinstance(in_list_max, \
                                                          bool) or \
                not 1 <= in_list_max <= 10_000:
            raise _err(f"in_list_max must be an int in 1..10000, got "
                       f"{in_list_max!r}")
        if or_chain_min is None:
            or_chain_min = self.DEFAULT_OR_CHAIN_MIN
        if not isinstance(or_chain_min, int) or isinstance(or_chain_min, \
                                                           bool) or \
                not 2 <= or_chain_min <= 1_000:
            raise _err(f"or_chain_min must be an int in 2..1000, got "
                       f"{or_chain_min!r}")

        if not isinstance(sql, str) or not sql.strip():
            raise _err("sql must be a non-empty string")
        if len(sql) > self.MAX_SQL_CHARS:
            raise _err(f"sql exceeds MAX_SQL_CHARS "
                       f"({len(sql)} > {self.MAX_SQL_CHARS})")
        if "\x00" in sql:
            raise _err("sql must not contain NUL characters")

        code, literals = _scan(sql)

        # Parenthesis balance over the masked text (literal contents are
        # already spaces, so parens inside strings never count).
        depth = 0
        open_offsets: list = []
        for idx, ch in enumerate(code):
            if ch == "(":
                depth += 1
                if depth > self.MAX_PAREN_DEPTH:
                    raise _err(f"nesting depth exceeds MAX_PAREN_DEPTH "
                               f"({self.MAX_PAREN_DEPTH}) at offset "
                               f"{idx}")
                open_offsets.append(idx)
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    line, column = _line_col(sql, idx)
                    raise _err(f"unbalanced ')' at offset {idx} "
                               f"(line {line}, column {column})")
                open_offsets.pop()
        if open_offsets:
            idx = open_offsets[0]
            line, column = _line_col(sql, idx)
            raise _err(f"unbalanced '(' (unclosed) at offset {idx} "
                       f"(line {line}, column {column})")

        tokens = _tokenize(code, literals)

        semis = [i for i, t in enumerate(tokens) if t["text"] == ";"]
        if semis:
            if semis[-1] != len(tokens) - 1 or len(semis) > 1:
                idx = tokens[semis[0]]["offset"]
                line, column = _line_col(sql, idx)
                raise _err(
                    f"multiple statements are not supported "
                    f"(single-statement contract); statement separator "
                    f"';' at offset {idx} (line {line}, column {column})"
                )
            tokens = tokens[:-1]
        if not tokens:
            raise _err("sql is empty after comment stripping")

        stmt_type, type_index = _statement_type(tokens)
        regions = _regions(tokens)

        if mode == "lint":
            return self._lint(sql, tokens, regions, stmt_type, type_index,
                              disabled, require_limit, in_list_max,
                              or_chain_min)
        if mode == "explain_structure":
            return {
                "mode": "explain_structure",
                **_structure(tokens, regions, stmt_type),
            }
        formatted = _format(tokens, uppercase_keywords)
        return {
            "mode": "format",
            "result": formatted,
            "statement_type": stmt_type,
            "line_count": formatted.count("\n") + 1 if formatted else 0,
        }

    def _lint(self, sql, tokens, regions, stmt_type, type_index, disabled,
              require_limit, in_list_max, or_chain_min) -> dict:
        found: list = []
        found.extend(_rule_select_star(tokens))
        found.extend(_rule_no_where(tokens, regions, stmt_type,
                                    type_index))
        found.extend(_rule_missing_limit(tokens, regions, stmt_type,
                                         type_index, require_limit))
        found.extend(_rule_cartesian(tokens, regions))
        found.extend(_rule_like_prefix(tokens))
        found.extend(_rule_distinct_order(tokens, regions))
        found.extend(_rule_groupby_shape(tokens, regions))
        found.extend(_rule_in_list_size(tokens, in_list_max))
        found.extend(_rule_or_chain(tokens, regions, or_chain_min))
        found.extend(_rule_mixed_lit_types(tokens, regions))

        found = [(o, f) for (o, f) in found if f["code"] not in disabled]
        found.sort(key=lambda pair: (pair[0], pair[1]["code"]))

        findings: list = []
        for offset, finding in found:
            line, column = _line_col(sql, offset)
            findings.append({
                "code": finding["code"],
                "severity": finding["severity"],
                "message": finding["message"],
                "position": {"offset": offset, "line": line,
                             "column": column},
                "hint": finding["hint"],
            })
        ok = not any(f["severity"] in ("error", "warning")
                     for f in findings)
        return {
            "mode": "lint",
            "ok": ok,
            "statement_type": stmt_type,
            "finding_count": len(findings),
            "findings": findings,
            "rules_disabled": sorted(disabled),
        }


def _line_col(sql: str, offset: int) -> tuple:
    """1-based (line, column) for a character offset."""
    line_starts = [0]
    for i, ch in enumerate(sql):
        if ch == "\n":
            line_starts.append(i + 1)
    line = bisect_right(line_starts, offset)
    return line, offset - line_starts[line - 1] + 1
