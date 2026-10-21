#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: sql_format_tool.py

"""Deterministic, configurable SQL pretty-printer built purely on stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency formatter for agents
that *produce* SQL. The tool never connects to a database and never
executes anything — it rewrites SQL text.

Relationship to SqlLintTool (PR #4003)
--------------------------------------
SqlLintTool ships a *basic* ``format`` mode with fixed rules: a newline
before every major clause, a hard-coded two-space subquery indent,
comments dropped and a single ``uppercase_keywords`` switch. This tool
is the full formatter that mode is not: keyword case (upper / lower /
preserve), identifier case (preserve / lower for unquoted identifiers),
indent width (2 or 4), comma style (trailing / leading), vertical
layout switch (``newline_before_major``), select-list wrapping at a
configurable column (80..120), per-line AND/OR grouping, byte-exact
comment preservation (SqlLintTool's format mode drops comments), a
``check`` mode for CI (is this file already formatted? where does it
diverge?) and named style presets. Both tools share the same scanning
discipline (see below); they are siblings, not duplicates.

Scanner consistency
-------------------
The scanner is the PR #4003-family scanner, implemented standalone in
this module (that PR is not merged yet, so there is nothing to import
without taking a dependency). Behaviour kept identical, rule for rule:

* comments — ``--`` line, MySQL ``#`` line and ``/* ... */`` block —
  are located and their bodies masked to same-length spaces (newlines
  preserved), so every offset maps 1:1 onto the original statement;
  unterminated literals and block comments raise ``ValueError``;
* string-literal and quoted-identifier contents are masked the same
  way, with doubled-quote escapes handled identically;
* tokenization produces word / num / str / qid / punct tokens carrying
  parenthesis depth, with two-character operators (``<= >= <> != ||
  ->``) fused and paren pairs sharing the depth of their opener;
* the keyword vocabulary, clause-starter detection (GROUP BY / ORDER
  BY pairs, UNION ALL / UNION DISTINCT, the six JOIN families with
  optional OUTER) and the two-character punctuation set are copied
  verbatim.

The formatter then goes beyond the family's fixed rules with the
option table below. All layout decisions are functions of the token
stream only — never of the input's whitespace — which is what makes
formatting deterministic and idempotent:
``format(format(x)) == format(x)`` for every statement and option
combination (asserted in the test suite over a 100-statement corpus
per preset).

Single-statement contract
-------------------------
Exactly one SQL statement per call (same as SqlLintTool). Comments are
ignored for parsing; one *trailing* semicolon is tolerated and
preserved in the output (absent input semicolons stay absent); any
other semicolon, an empty statement, unbalanced or over-deeply-nested
parentheses, unterminated literals or comments, NUL bytes and
statements over the size cap all raise ``ValueError`` before any
formatting.

Modes
-----
``format``
    Pretty-print ``sql`` under the resolved options and return the
    text. Layout majors (SELECT / FROM / WHERE / GROUP BY / HAVING /
    ORDER BY / LIMIT / OFFSET / FETCH / UNION [ALL|DISTINCT] / EXCEPT /
    INTERSECT / every JOIN family / WITH) each start on a fresh line at
    the clause's indent when ``newline_before_major`` is on (the
    default); with it off the statement collapses to one line, except
    where a vertical option (leading commas, AND/OR grouping, line
    comments — which must end their line by definition) forces breaks.
    Parenthesized ``SELECT``/``WITH`` bodies (derived tables, CTE
    bodies, scalar and IN subqueries) become indented blocks whose
    closing parenthesis returns to its opener's indent. All other
    spacing follows the family rules: single spaces, no space before
    ``,``/``)``/``.``/``;`` or around ``.``/function-call ``(``,
    keyword-adjacent parens keep their space (``IN (1, 2)``,
    ``count(*)``), unary minus attaches to its number.

``check``
    The CI mode: return whether ``sql`` already equals its own
    formatted form (trailing newlines on the input are tolerated and
    ignored). The result carries ``clean``, a unified-diff-style line
    summary (capped, stdlib ``difflib``) and the first divergence as
    ``{line, col, expected, actual}`` with 1-based coordinates.

``styles``
    List the built-in style presets with their resolved options and a
    rendered sample of the same demonstration statement, so callers
    can pick a style without guessing.

Options
-------
keyword_case (upper|lower|preserve, default upper)
    Letter case for recognized keywords. Never applied inside string
    literals, quoted identifiers or comments — those are emitted
    byte-for-byte as written.
identifier_case (preserve|lower, default preserve)
    Letter case for unquoted identifiers (including function names,
    which are not keywords). Quoted identifiers and string literals
    are always verbatim.
indent (2|4, default 2)
    Indentation width per nesting level.
comma_style (trailing|leading, default trailing)
    Trailing: ``a, b``. Leading: every clause-level list comma (select
    list, FROM table list, GROUP BY / ORDER BY entries, CTE list)
    starts its own line at one indent unit, comma-first — commas
    inside parentheses (function arguments, IN lists, VALUES tuples)
    always stay inline. Leading commas force per-item newlines even
    when ``newline_before_major`` is off; that is inherent to the
    style.
newline_before_major (bool, default true)
    Vertical layout switch described under ``format``.
select_wrap (none|at_width, default none)
    With at_width, a select list whose *single-line* rendering (a
    layout-independent token measure, comments excluded) exceeds
    ``wrap_column`` is broken one item per line at one indent unit.
    Individual items are never split. The decision is a pure function
    of tokens, so it survives re-formatting.
wrap_column (int 80..120, default 100)
    The at_width threshold.
and_newline_group (bool, default false)
    Each AND / OR connector at clause level inside WHERE / HAVING /
    JOIN-ON starts its own line at one indent unit. The AND of
    ``BETWEEN x AND y`` never breaks.

Presets: ``default`` (upper keywords, trailing commas, 2-space,
vertical), ``compact`` (same, single-line) and ``pythonic`` (lower
keywords and identifiers, 4-space, leading commas, AND/OR grouped,
select lists wrapped at 88).
"""

import difflib
import re
from bisect import bisect_right
from typing import Any, ClassVar, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Static vocabulary (kept consistent with the SqlLintTool #4003 family)
# ---------------------------------------------------------------------------

_WORD = re.compile(r"[^\W\d][\w$]*")
_NUM = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")

# Keywords recognized (case-insensitively) by the case options.
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

# One-word clause starters (formatting majors).
_SIMPLE_STARTERS = frozenset({
    "SELECT", "FROM", "WHERE", "HAVING", "LIMIT", "OFFSET", "FETCH",
    "UNION", "EXCEPT", "INTERSECT", "JOIN",
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

_TWO_CHAR_PUNCT = ("<=", ">=", "<>", "!=", "||", "->")

# Regions whose clause-level AND/OR connectors can be grouped per line.
_AND_OR_REGIONS = frozenset({"WHERE", "HAVING", "JOIN"})

# Built-in style presets (resolved option tables).
STYLE_PRESETS = {
    "default": {
        "keyword_case": "upper", "identifier_case": "preserve",
        "indent": 2, "comma_style": "trailing",
        "newline_before_major": True, "select_wrap": "none",
        "wrap_column": 100, "and_newline_group": False,
    },
    "compact": {
        "keyword_case": "upper", "identifier_case": "preserve",
        "indent": 2, "comma_style": "trailing",
        "newline_before_major": False, "select_wrap": "none",
        "wrap_column": 100, "and_newline_group": False,
    },
    "pythonic": {
        "keyword_case": "lower", "identifier_case": "lower",
        "indent": 4, "comma_style": "leading",
        "newline_before_major": True, "select_wrap": "at_width",
        "wrap_column": 88, "and_newline_group": True,
    },
}

# Demonstration statement rendered by the styles mode.
SAMPLE_STATEMENT = (
    "select u.id, u.name, count(o.id) as orders -- pick columns\n"
    "from users u join orders o on u.id = o.user_id "
    "where u.status = 'active' and o.total > 100 "
    "group by u.id, u.name having count(o.id) > 5 "
    "order by orders desc limit 10;"
)


def _err(message: str) -> ValueError:
    return ValueError(f"sql_format_tool: {message}")


# ---------------------------------------------------------------------------
# Scanning: #4003-family discipline (comments stripped with positions
# preserved, string-literal contents masked, offsets 1:1)
# ---------------------------------------------------------------------------

def _scan(sql: str) -> tuple:
    """Return ``(code, literals, comments)`` for ``sql``.

    ``code`` has the same length as ``sql``: comment bodies (and
    markers) and literal contents are replaced by spaces, newlines
    preserved, so any offset in ``code`` maps 1:1 onto ``sql``.
    ``literals`` maps each opening-quote offset to
    ``{end, raw, quote}``. ``comments`` maps each comment's opening
    offset to ``{end, raw, line}`` where ``raw`` is the byte-exact
    comment text (markers included) and ``line`` marks ``--`` / ``#``
    line comments.

    Raises:
        ValueError: On unterminated literals or block comments.
    """
    buf = list(sql)
    literals: dict = {}
    comments: dict = {}
    i, n = 0, len(sql)

    def _masked_span(start: int, end: int) -> None:
        for k in range(start, end):
            if buf[k] != "\n":
                buf[k] = " "

    def _scan_quoted(quote: str) -> dict:
        nonlocal i
        j = i + 1
        while True:
            if j >= n:
                kind = "string literal" if quote == "'" \
                    else "quoted identifier"
                raise _err(
                    f"unterminated {kind} starting at offset {i}"
                )
            if sql[j] == quote:
                if j + 1 < n and sql[j + 1] == quote:  # doubled escape
                    j += 2
                    continue
                break
            j += 1
        end = j + 1
        _masked_span(i + 1, j)
        info = {"end": end, "raw": sql[i:end], "quote": quote}
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
            comments[i] = {"end": j, "raw": sql[i:j], "line": True}
            i = j  # keep the newline itself
        elif ch == "#":
            j = i
            while j < n and sql[j] != "\n":
                buf[j] = " "
                j += 1
            comments[i] = {"end": j, "raw": sql[i:j], "line": True}
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
            comments[i] = {
                "end": j + 2, "raw": sql[i:j + 2], "line": False,
            }
            i = j + 2
        else:
            i += 1
    return "".join(buf), literals, comments


# ---------------------------------------------------------------------------
# Tokenization (#4003 family: kinds, depths, fused two-char operators)
# ---------------------------------------------------------------------------

def _tokenize(code: str, literals: dict, comments: dict) -> list:
    """Tokenize ``code`` into ``{kind, text, offset, depth}`` tokens.

    Kinds: ``word``, ``num``, ``str`` / ``qid`` (raw quoted text from
    the literal registry), ``punct``, ``comment`` (raw byte-exact
    text). Parentheses of a pair carry the same depth; enclosed tokens
    are one deeper. Comment tokens carry the paren depth open at their
    offset.
    """
    depth_at = [0] * len(code)
    running = 0
    for idx, ch in enumerate(code):
        depth_at[idx] = running
        if ch == "(":
            running += 1
        elif ch == ")":
            running -= 1

    tokens: list = []
    depth = 0
    i, n = 0, len(code)
    while i < n:
        ch = code[i]
        # comments come first: their masked bodies are whitespace, so
        # the whitespace branch below would otherwise swallow them
        if i in comments:
            com = comments[i]
            tokens.append({
                "kind": "comment", "text": com["raw"], "offset": i,
                "depth": depth_at[i], "line": com["line"],
            })
            i = com["end"]
            continue
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


def _line_col(sql: str, offset: int) -> tuple:
    """1-based (line, column) for a character offset."""
    line_starts = [0]
    for i, ch in enumerate(sql):
        if ch == "\n":
            line_starts.append(i + 1)
    line = bisect_right(line_starts, offset)
    return line, offset - line_starts[line - 1] + 1


def _statement_type(tokens: list) -> str:
    """Resolve the statement type (a WITH prefix resolves to its
    operative SELECT / INSERT / ... via the last depth-0 closer)."""
    if not tokens or tokens[0]["kind"] != "word":
        return "unknown"
    first = tokens[0]["text"].upper()
    if first != "WITH":
        return _TYPE_WORDS.get(first, first.lower())
    last_top_close = -1
    for idx, tok in enumerate(tokens):
        if tok["kind"] == "punct" and tok["text"] == ")" \
                and tok["depth"] == 0:
            last_top_close = idx
    for tok in tokens[last_top_close + 1:]:
        if tok["kind"] == "word" and tok["depth"] == 0:
            resolved = _OPERATIVE_WORDS.get(tok["text"].upper())
            if resolved:
                return resolved
            break
    return "with"


# ---------------------------------------------------------------------------
# Clause starter detection (family rules; WITH added as a formatting
# major, UNION ALL / UNION DISTINCT and JOIN families fused)
# ---------------------------------------------------------------------------

def _starter_at(tokens: list, i: int):
    """Return ``(name, raw, length)`` if a formatting major begins at
    token index ``i`` (same detection rules as the #4003 format mode,
    plus WITH as a major)."""
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
    if w == "WITH":
        return ("WITH", orig, 1)
    return None


def _starter_map(tokens: list) -> dict:
    return {
        i: _starter_at(tokens, i)
        for i in range(len(tokens))
        if _starter_at(tokens, i) is not None
    }


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _cased_text(text: str, kind: str, opts: dict) -> str:
    """Case one token text per the case options (never comments /
    literals / quoted identifiers — callers pass those verbatim)."""
    if kind != "word":
        return text
    upper = text.upper()
    if upper in KEYWORDS:
        if opts["keyword_case"] == "upper":
            return upper
        if opts["keyword_case"] == "lower":
            return text.lower()
        return text
    if opts["identifier_case"] == "lower":
        return text.lower()
    return text


def _case_starter_raw(raw: str, opts: dict) -> str:
    """Case each whitespace-separated word of a starter keyword run."""
    return " ".join(
        _cased_text(word, "word", opts) for word in raw.split(" ")
    )


def _needs_space(prev: Optional[dict], text: str,
                 pending_no_space: bool) -> bool:
    """Family spacing rule: whether a space precedes ``text``."""
    if pending_no_space:
        return False
    if text in (",", ")", ".", ";"):
        return False
    if text == "(":
        if prev is None:
            return True  # fresh clause lead keeps its space: WHERE (…)
        if prev["kind"] in ("num", "str", "qid", "comment"):
            return False
        if prev["kind"] == "punct" and prev["text"] == ")":
            return False
        if prev["kind"] == "word" and prev["text"].upper() not in KEYWORDS:
            return False
        return True
    return True


def _select_region_wrap_starts(tokens: list, starters: dict,
                               opts: dict) -> set:
    """Token indices of SELECT starters whose select list should be
    wrapped: the single-line rendering of the region (comments
    excluded — they never influence layout decisions) exceeds
    ``wrap_column`` and the list has at least one clause-level comma.
    Pure function of the token stream, hence idempotence-safe."""
    wrap_column = opts["wrap_column"]
    starts: set = set()
    if opts["select_wrap"] != "at_width" \
            or opts["comma_style"] != "trailing":
        return starts
    n = len(tokens)
    for i, (name, raw, length) in starters.items():
        if name != "SELECT":
            continue
        depth = tokens[i]["depth"]
        end = i + length
        while end < n:
            if tokens[end]["depth"] < depth:
                break
            if tokens[end]["depth"] == depth and end in starters:
                break
            end += 1
        region = [t for t in tokens[i:end]
                  if t["kind"] != "comment"]
        body = [t for t in region[length:] if t["depth"] == depth]
        commas = sum(1 for t in body
                     if t["kind"] == "punct" and t["text"] == ",")
        if commas < 1:
            continue
        width = len(_case_starter_raw(raw, opts))
        prev: Optional[dict] = None
        pending = False
        for t in region[length:]:
            if t["kind"] == "comment":
                continue
            text = _cased_text(t["text"], t["kind"], opts)
            if prev is not None and _needs_space(prev, text, pending):
                width += 1
            width += len(text)
            pending = text in ("(", ".")
            prev = t
        if width > wrap_column:
            starts.add(i)
    return starts


def _format(tokens: list, opts: dict) -> str:
    """Deterministic pretty-print of the token stream (see module
    docstring). Layout is a pure function of tokens — never of the
    input's whitespace — so ``format(format(x)) == format(x)``."""
    indent_unit = opts["indent"]
    leading = opts["comma_style"] == "leading"
    nlm = opts["newline_before_major"]
    and_nl = opts["and_newline_group"]

    starters = _starter_map(tokens)
    wrap_starts = _select_region_wrap_starts(tokens, starters, opts)

    # Subquery parens: '(' whose first significant follower is a
    # SELECT/WITH word (comments skipped when peeking), with the
    # matching close index.
    sub_close: dict = {}
    open_stack: list = []
    for idx, tok in enumerate(tokens):
        if tok["kind"] == "punct" and tok["text"] == "(":
            open_stack.append(idx)
        elif tok["kind"] == "punct" and tok["text"] == ")" and open_stack:
            sub_close[open_stack.pop()] = idx

    def _is_sub_open(idx: int) -> bool:
        if idx not in sub_close:
            return False
        j = idx + 1
        while j < len(tokens) and tokens[j]["kind"] == "comment":
            j += 1
        return (
            j < len(tokens)
            and tokens[j]["kind"] == "word"
            and tokens[j]["text"].upper() in ("SELECT", "WITH")
        )

    lines: list = []
    cur: list = []

    def flush(keep_empty: bool = False) -> None:
        text = "".join(cur)
        if text or keep_empty:
            lines.append(text)
        cur.clear()

    def has_content() -> bool:
        """True when the current line already has visible text (an
        indent-only prefix does not count — tokens glue to it)."""
        return any(part.strip() for part in cur)

    def indent_str(levels: int) -> str:
        return " " * (indent_unit * levels)

    depth_stack: list = []      # open indices of active subquery parens
    region: Optional[str] = None
    region_stack: list = []     # (region, select_start) per subquery
    select_start: Optional[int] = None
    pending_no_space = False
    prev_sig: Optional[dict] = None
    between_active = False  # a BETWEEN whose AND has not been consumed
    leading_comma_pending = False  # current line starts with ', item'

    i, n = 0, len(tokens)
    while i < n:
        tok = tokens[i]
        body_depth = len(depth_stack)

        # --- comments: byte-exact, own placement in the token stream
        if tok["kind"] == "comment":
            if has_content():
                cur.append(" ")
            segments = tok["text"].split("\n")
            for k, seg in enumerate(segments):
                if k:
                    flush(keep_empty=True)
                cur.append(seg)
            if tok["line"]:
                flush()  # a line comment must end its line
            pending_no_space = False
            i += 1
            continue

        # --- formatting majors
        starter = starters.get(i)
        if starter is not None and tok["depth"] == body_depth:
            name, raw, length = starter
            if nlm or leading_comma_pending:
                flush()
                cur.append(indent_str(body_depth))
            elif has_content() and not cur[-1].endswith("("):
                cur.append(" ")
            cur.append(_case_starter_raw(raw, opts))
            region = name
            select_start = i if name == "SELECT" else None
            pending_no_space = False
            prev_sig = None
            between_active = False
            leading_comma_pending = False
            i += length
            continue

        # --- subquery blocks
        if _is_sub_open(i):
            if has_content() and not cur[-1].endswith(" "):
                cur.append(" ")
            cur.append("(")
            if nlm:
                # keep a directly following comment on the '(' line
                j = i + 1
                while j < n and tokens[j]["kind"] == "comment":
                    c = tokens[j]
                    cur.append(" ")
                    for k, seg in enumerate(c["text"].split("\n")):
                        if k:
                            flush(keep_empty=True)
                        cur.append(seg)
                    j += 1
                i = j - 1  # the loop's i += 1 advances past the last
                flush()
            depth_stack.append(i)
            region_stack.append((region, select_start))
            region = None
            select_start = None
            pending_no_space = False
            prev_sig = tok
            between_active = False
            i += 1
            continue

        # --- subquery closers (indent back to the opener's body): a
        # ')' whose depth equals the token depth of the innermost
        # open subquery parenthesis
        if tok["kind"] == "punct" and tok["text"] == ")" \
                and depth_stack \
                and tok["depth"] == tokens[depth_stack[-1]]["depth"]:
            if nlm:
                flush()
                cur.append(indent_str(body_depth - 1))
                cur.append(")")
            else:
                cur.append(")")  # no space before ')' (family rule)
            depth_stack.pop()
            region, select_start = region_stack.pop()
            pending_no_space = False
            prev_sig = tok
            between_active = False
            i += 1
            continue

        # --- clause-level commas
        if tok["kind"] == "punct" and tok["text"] == "," \
                and tok["depth"] == body_depth:
            if leading:
                flush()
                cur.append(indent_str(body_depth + 1))
                cur.append(",")
                pending_no_space = False
                prev_sig = tok
                between_active = False
                leading_comma_pending = True
                i += 1
                continue
            cur.append(",")
            if select_start is not None and select_start in wrap_starts:
                flush()
                cur.append(indent_str(body_depth + 1))
            pending_no_space = False
            prev_sig = tok
            between_active = False
            i += 1
            continue

        # --- AND/OR grouping (never the AND of BETWEEN)
        if tok["kind"] == "word" \
                and tok["text"].upper() in ("AND", "OR") \
                and tok["depth"] == body_depth and and_nl \
                and region in _AND_OR_REGIONS \
                and not between_active:
            flush()
            cur.append(indent_str(body_depth + 1))
            cur.append(_cased_text(tok["text"], "word", opts))
            pending_no_space = False
            prev_sig = tok
            i += 1
            continue

        # --- default emission with the family spacing rules
        text = _cased_text(tok["text"], tok["kind"], opts)
        space = True
        minus_glue = False
        if text in (",", ")", ".", ";"):
            space = False
        elif text == "(":
            space = _needs_space(prev_sig, "(", False)
        elif text == "-" and i + 1 < n and tokens[i + 1]["kind"] == "num":
            minus_glue = True
            space = not pending_no_space and (
                prev_sig is None or prev_sig["text"] != "(")
        if pending_no_space:
            space = False
        if has_content() and space:
            cur.append(" ")
        cur.append(text)
        pending_no_space = text in ("(", ".") or minus_glue
        if tok["kind"] == "word":
            upper_word = text.upper()
            if upper_word == "BETWEEN":
                between_active = True
            elif upper_word in ("AND", "OR"):
                between_active = False
        prev_sig = tok
        i += 1

    # Keep every produced line: the layout never emits blank lines, so
    # blank lines can only originate *inside* multi-line block comment
    # text, which is preserved byte-for-byte.
    flush()
    return "\n".join(lines)


def _format_sql(sql: str, opts: dict) -> tuple:
    """Validate + scan + tokenize + format; returns (formatted, type)."""
    code, literals, comments = _scan(sql)

    depth = 0
    open_offsets: list = []
    for idx, ch in enumerate(code):
        if ch == "(":
            depth += 1
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

    tokens = _tokenize(code, literals, comments)

    semis = [i for i, t in enumerate(tokens)
             if t["kind"] == "punct" and t["text"] == ";"]
    if semis:
        if semis[-1] != len(tokens) - 1 or len(semis) > 1:
            idx = tokens[semis[0]]["offset"]
            line, column = _line_col(sql, idx)
            raise _err(
                "multiple statements are not supported "
                "(single-statement contract); statement separator "
                f"';' at offset {idx} (line {line}, column {column})"
            )
    if not [t for t in tokens
            if t["kind"] != "comment" and t["text"] != ";"]:
        raise _err("sql is empty after comment stripping")

    stmt_type = _statement_type(
        [t for t in tokens if t["kind"] != "comment"])
    formatted = _format(tokens, opts)
    return formatted, stmt_type


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class SqlFormatTool(Tool):
    """Deterministic, configurable SQL pretty-printer for single
    statements, built purely on the stdlib.

    The tool never connects to a database and never executes SQL — it
    rewrites SQL *text*: format it under a full option table
    (keyword / identifier case, indent width, comma style, vertical
    layout, select-list wrapping, AND/OR grouping), check whether a
    file already matches its formatted form (CI mode with a first-
    difference locator), or list the built-in style presets with
    rendered samples. See the module docstring for the scanner
    consistency notes and the exact option semantics.

    Class attributes:
        MAX_SQL_CHARS (int): Upper bound on the statement length.
        MAX_PAREN_DEPTH (int): Upper bound on parenthesis nesting.
        MAX_DIFF_LINES (int): Cap on the check-mode diff summary.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "sql_format_tool"
    description: str = (
        "Deterministic configurable SQL pretty-printing tool — pure "
        "Python stdlib, no database, no execution. Formats a single "
        "SQL statement (mode='format') under a full option table: "
        "keyword case upper/lower/preserve (never inside strings, "
        "quoted identifiers or comments — those are byte-preserved), "
        "identifier case preserve/lower, indent 2/4, trailing or "
        "leading comma style, newline-before-major-clause switch, "
        "select-list wrapping at a column of 80..120 and per-line "
        "AND/OR grouping in WHERE/HAVING/JOIN-ON; subqueries and CTE "
        "bodies indent as blocks. Check mode returns whether the text "
        "already matches its formatted form plus a unified-diff-style "
        "summary and the first divergence (line/col/expected/actual) "
        "for CI. Styles mode lists the default/compact/pythonic "
        "presets with rendered samples. Idempotent: "
        "format(format(x)) == format(x); single-statement contract "
        "enforced strictly."
    )

    MODES: ClassVar[tuple] = ("format", "check", "styles")
    PRESET_NAMES: ClassVar[tuple] = ("default", "compact", "pythonic")
    KEYWORD_CASES: ClassVar[tuple] = ("upper", "lower", "preserve")
    IDENTIFIER_CASES: ClassVar[tuple] = ("preserve", "lower")
    INDENTS: ClassVar[tuple] = (2, 4)
    COMMA_STYLES: ClassVar[tuple] = ("trailing", "leading")
    SELECT_WRAPS: ClassVar[tuple] = ("none", "at_width")
    MAX_SQL_CHARS: ClassVar[int] = 20_000
    MAX_PAREN_DEPTH: ClassVar[int] = 64
    MAX_DIFF_LINES: ClassVar[int] = 40
    DEFAULT_WRAP_COLUMN: ClassVar[int] = 100

    def execute(
        self,
        mode: Any = None,
        sql: Any = None,
        style: Any = None,
        keyword_case: Any = None,
        identifier_case: Any = None,
        indent: Any = None,
        comma_style: Any = None,
        newline_before_major: Any = None,
        select_wrap: Any = None,
        wrap_column: Any = None,
        and_newline_group: Any = None,
    ) -> dict:
        """Format, check or list styles for a single SQL statement.

        Args:
            mode (str): One of ``format``, ``check`` or ``styles``.
            sql (str): The single SQL statement (required for format
                and check; must be absent for styles). Comments are
                allowed and preserved byte-exactly; one trailing
                semicolon is tolerated and preserved.
            style (str): Optional preset name (default, compact,
                pythonic). Any option not explicitly supplied resolves
                to this preset's value.
            keyword_case (str): upper | lower | preserve for keywords.
            identifier_case (str): preserve | lower for unquoted
                identifiers.
            indent (int): 2 or 4 spaces per nesting level.
            comma_style (str): trailing | leading clause-level commas.
            newline_before_major (bool): Major clauses / subquery
                blocks on their own lines (true) or one single line
                (false).
            select_wrap (str): none | at_width select-list wrapping.
            wrap_column (int): at_width threshold, 80..120.
            and_newline_group (bool): One AND/OR connector per line in
                WHERE / HAVING / JOIN-ON.

        Returns:
            dict: ``format`` → ``{mode, result, statement_type,
            line_count, style, options}``; ``check`` → ``{mode, clean,
            statement_type, first_difference, diff_lines,
            diff_truncated}``; ``styles`` → ``{mode, styles}`` with
            each preset's options and rendered sample.

        Raises:
            ValueError: If any argument is malformed or the statement
                violates the single-statement contract (multiple
                statements, unbalanced / over-nested parens, unterminated
                literals or comments, size cap).
        """
        if mode not in self.MODES:
            raise _err(f"mode must be one of {self.MODES}, got {mode!r}")

        if mode == "styles":
            if sql is not None:
                raise _err("styles mode takes no sql argument")
            if style is not None:
                self._validate_style(style)
            return {"mode": "styles", "styles": self._style_catalog()}

        opts, style_name = self._resolve_options(
            style=style,
            keyword_case=keyword_case,
            identifier_case=identifier_case,
            indent=indent,
            comma_style=comma_style,
            newline_before_major=newline_before_major,
            select_wrap=select_wrap,
            wrap_column=wrap_column,
            and_newline_group=and_newline_group,
        )

        if not isinstance(sql, str) or not sql.strip():
            raise _err("sql must be a non-empty string")
        if len(sql) > self.MAX_SQL_CHARS:
            raise _err(f"sql exceeds MAX_SQL_CHARS "
                       f"({len(sql)} > {self.MAX_SQL_CHARS})")
        if "\x00" in sql:
            raise _err("sql must not contain NUL characters")

        depth = 0
        for ch in _scan(sql)[0]:
            if ch == "(":
                depth += 1
                if depth > self.MAX_PAREN_DEPTH:
                    raise _err("nesting depth exceeds MAX_PAREN_DEPTH "
                               f"({self.MAX_PAREN_DEPTH})")
            elif ch == ")":
                depth -= 1

        formatted, stmt_type = _format_sql(sql, opts)

        if mode == "format":
            return {
                "mode": "format",
                "result": formatted,
                "statement_type": stmt_type,
                "line_count": formatted.count("\n") + 1 if formatted else 0,
                "style": style_name,
                "options": dict(opts),
            }
        return self._check(sql, formatted, stmt_type)

    # -- option handling --------------------------------------------------

    def _validate_style(self, style: Any) -> str:
        if not isinstance(style, str) or style not in STYLE_PRESETS:
            raise _err(
                f"style must be one of {self.PRESET_NAMES}, got {style!r}"
            )
        return style

    def _resolve_options(self, **given: Any) -> tuple:
        """Validate raw arguments and resolve them against the preset."""
        style_name = "custom"
        base = STYLE_PRESETS["default"]
        if given.get("style") is not None:
            style_name = self._validate_style(given["style"])
            base = STYLE_PRESETS[style_name]
        elif not any(
            given.get(key) is not None for key in (
                "keyword_case", "identifier_case", "indent",
                "comma_style", "newline_before_major", "select_wrap",
                "wrap_column", "and_newline_group",
            )
        ):
            style_name = "default"

        def _pick(key: str) -> Any:
            value = given.get(key)
            return base[key] if value is None else value

        keyword_case = _pick("keyword_case")
        if keyword_case not in self.KEYWORD_CASES:
            raise _err("keyword_case must be one of "
                       f"{self.KEYWORD_CASES}, got {keyword_case!r}")
        identifier_case = _pick("identifier_case")
        if identifier_case not in self.IDENTIFIER_CASES:
            raise _err("identifier_case must be one of "
                       f"{self.IDENTIFIER_CASES}, got "
                       f"{identifier_case!r}")
        indent = _pick("indent")
        if not isinstance(indent, int) or isinstance(indent, bool) \
                or indent not in self.INDENTS:
            raise _err(f"indent must be one of {self.INDENTS} (int), "
                       f"got {indent!r}")
        comma_style = _pick("comma_style")
        if comma_style not in self.COMMA_STYLES:
            raise _err("comma_style must be one of "
                       f"{self.COMMA_STYLES}, got {comma_style!r}")
        newline_before_major = _pick("newline_before_major")
        if not isinstance(newline_before_major, bool):
            raise _err("newline_before_major must be a bool, got "
                       f"{type(newline_before_major).__name__}")
        select_wrap = _pick("select_wrap")
        if select_wrap not in self.SELECT_WRAPS:
            raise _err("select_wrap must be one of "
                       f"{self.SELECT_WRAPS}, got {select_wrap!r}")
        wrap_column = _pick("wrap_column")
        if not isinstance(wrap_column, int) or isinstance(wrap_column, \
                                                          bool) or \
                not 80 <= wrap_column <= 120:
            raise _err(f"wrap_column must be an int in 80..120, got "
                       f"{wrap_column!r}")
        and_newline_group = _pick("and_newline_group")
        if not isinstance(and_newline_group, bool):
            raise _err("and_newline_group must be a bool, got "
                       f"{type(and_newline_group).__name__}")

        return ({
            "keyword_case": keyword_case,
            "identifier_case": identifier_case,
            "indent": indent,
            "comma_style": comma_style,
            "newline_before_major": newline_before_major,
            "select_wrap": select_wrap,
            "wrap_column": wrap_column,
            "and_newline_group": and_newline_group,
        }, style_name)

    def _style_catalog(self) -> list:
        catalog = []
        for name in self.PRESET_NAMES:
            opts = dict(STYLE_PRESETS[name])
            formatted, stmt_type = _format_sql(SAMPLE_STATEMENT, opts)
            catalog.append({
                "name": name,
                "options": opts,
                "sample": formatted,
                "sample_statement_type": stmt_type,
            })
        return catalog

    # -- check mode --------------------------------------------------------

    def _check(self, sql: str, formatted: str, stmt_type: str) -> dict:
        actual = sql.rstrip("\n")
        expected_lines = formatted.split("\n")
        actual_lines = actual.split("\n")
        clean = expected_lines == actual_lines
        if clean:
            return {
                "mode": "check",
                "clean": True,
                "statement_type": stmt_type,
                "first_difference": None,
                "diff_lines": [],
                "diff_truncated": False,
            }

        first_difference = None
        for idx in range(max(len(expected_lines), len(actual_lines))):
            expected_line = (expected_lines[idx]
                             if idx < len(expected_lines) else None)
            actual_line = (actual_lines[idx]
                           if idx < len(actual_lines) else None)
            if expected_line == actual_line:
                continue
            if expected_line is None:
                column = len(actual_line) + 1
            elif actual_line is None:
                column = len(expected_line) + 1
            else:
                column = next(
                    (pos + 1 for pos, (exp_char, act_char)
                     in enumerate(zip(expected_line, actual_line))
                     if exp_char != act_char),
                    min(len(expected_line), len(actual_line)) + 1,
                )
            first_difference = {
                "line": idx + 1,
                "col": column,
                "expected": expected_line if expected_line is not None
                else "",
                "actual": actual_line if actual_line is not None else "",
            }
            break

        diff = list(difflib.unified_diff(
            expected_lines, actual_lines, lineterm="", n=1))[2:]
        truncated = len(diff) > self.MAX_DIFF_LINES
        if truncated:
            diff = diff[:self.MAX_DIFF_LINES]
        return {
            "mode": "check",
            "clean": False,
            "statement_type": stmt_type,
            "first_difference": first_difference,
            "diff_lines": diff,
            "diff_truncated": truncated,
        }
