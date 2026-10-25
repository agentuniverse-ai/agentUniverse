#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: envsubst_tool.py

r"""Shell-style ``${VAR}`` *parameter expansion* tool built purely on the
stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the expansion layer between "a template with shell
variable references" and "the text a shell would produce": templates
are expanded against a caller-supplied ``env`` mapping using the
bash/POSIX parameter-expansion dialect — never by running a shell.
Every rule below was verified against real ``bash`` behaviour and is
pinned byte-for-byte by the test suite (the tests run the actual bash
binary as an oracle; this module itself never spawns a process).

Expansion dialect (documented exact subset)
-------------------------------------------

Variables are named ``[A-Za-z_][A-Za-z0-9_]*``.  ``$NAME`` and
``${NAME}`` expand to the mapping value (empty when the name is
absent).  On top of the basic form the tool implements, with POSIX
semantics exactly as bash applies them:

* ``${NAME:-word}`` / ``${NAME-word}`` — default when unset.  The
  classic distinction: the colon form triggers when the variable is
  unset **or empty**, the plain form only when **unset**.
* ``${NAME:=word}`` / ``${NAME=word}`` — like the default forms, but
  the default is also **assigned** back into the working env mapping;
  every assignment is reported in the ``assignments`` output list.
* ``${NAME:?word}`` / ``${NAME?word}`` — when unset (colon form: unset
  or empty) the whole operation fails with a structured
  ``required_variable_missing`` error whose message is the expanded
  ``word`` or bash's own default text (``parameter null or not set``
  for ``:?``, ``parameter not set`` for ``?``).
* ``${NAME:+word}`` / ``${NAME+word}`` — alternate value when the
  variable is set and non-empty (colon) or merely set (plain).
* ``${#NAME}`` — length in characters.
* ``${NAME%pattern}`` / ``${NAME%%pattern}`` — strip the shortest /
  longest suffix matching a glob ``pattern``.
* ``${NAME#pattern}`` / ``${NAME##pattern}`` — strip the shortest /
  longest matching prefix.
* ``${NAME:offset}`` / ``${NAME:offset:length}`` — substring.
  Whitespace around the integer literals is allowed (so the classic
  ``${NAME: -3}`` spelling works: space, then a negative offset
  counted from the end).  A negative offset that runs past the start
  yields the empty string; a negative *length* (bash >= 4.2) means
  "stop that many characters before the end", and an end position
  before the offset is the structured error ``substring expression
  < 0`` — the same failure bash reports, and like bash the whole
  expression is skipped (yielding the empty string, never the error)
  when the variable is unset.  Arithmetic expressions are **not**
  evaluated (``${V:2-3}`` is rejected; bash would compute).
* ``${NAME^pattern}`` / ``${NAME^^pattern}`` / ``${NAME,pattern}`` /
  ``${NAME,,pattern}`` — case modification; an empty pattern defaults
  to ``?`` (any single character), and only characters matching the
  pattern are converted.

Word / pattern operands follow bash's rules for an expansion that
appears inside double quotes (the context the test oracle uses, and
the only context in which the whole dialect is verifiable
byte-for-byte):

* Nested expansions — ``$NAME`` and full ``${...}`` forms — are
  expanded recursively inside operands (bash does this too), to a
  maximum nesting depth of 8.
* Single quotes are *literal characters*: they group for the purpose
  of finding the closing ``}`` (and are emitted verbatim), but they do
  not suppress ``$`` expansion of their content.
* Double quotes group and are removed; a ``}`` inside either quote
  style does not close the expansion.
* In **value** operands (default / assign / guard / alternate) a
  backslash escapes the next character for scanning purposes and
  disappears before ``$ ` " \`` and ``}``; before a single quote both
  characters survive in every region; before any other character both
  characters survive (``${V:-\\x}`` is a literal backslash and x).  In
  **pattern** operands (strip / case forms) the backslash is dropped
  before *every* following character except a single quote, making it
  literal — bash's pathname-pattern escaping (``${V%\\*}`` strips a
  literal asterisk, ``${V%\\x}`` strips a literal x).
* Glob patterns support ``*``, ``?`` and ``[...]`` classes with
  ranges, ``!``/``^`` negation, a leading ``]`` as a literal, a
  trailing/leading ``-`` as a literal and an unmatched ``[`` as a
  literal — matching bash's pathname-style pattern matching, minus
  ``extglob`` operators.  Characters that arrive quoted or
  backslash-escaped are never metacharacters.

Rejected constructs (structured ``not_supported`` errors — the tool
**never evaluates anything**; there is no ``eval``, no subprocess, no
filesystem access at runtime): command substitution ``$(...)`` and
```...` `` anywhere in the template (including inside operands),
arithmetic expansion ``$((...))``, process substitution ``<(...)`` /
``>(...)`` anywhere, positional and special parameters (``$0``-``$9``,
``$?``, ``$$``, ``$!``, ``$@``, ``$*``, ``$#``) in either bare or
braced form, ``${!NAME}`` indirection, ``${NAME[...]}`` array
subscripts, ``${NAME@op}`` expansion operators and the
``${NAME/pat/rep}`` replacement family.  Structured
``invalid_template`` errors mirror bash's *bad substitution* family
(unterminated ``${``, empty or invalid names, malformed substring
specifications such as ``${V:}`` or ``${V:2-3}``, nesting deeper than
the cap).

Modes
-----

* ``expand`` — ``template`` + ``env`` mapping → ``{text, expanded,
  unresolved, assignments, errors}``.  ``expanded`` lists the names
  that resolved from the mapping; ``unresolved`` lists referenced
  names that had no mapping value, each with the default that applied
  (if any); ``assignments`` reports every ``:=`` / ``=`` assignment
  performed on the working copy of the mapping.
* ``analyze`` — ``template`` alone → static analysis: ``variables``
  (each name with ``forms_used`` and ``occurrences``), ``required``
  (used at the top level without a default operator),
  ``optional_with_default`` (name → default operand as written),
  ``conditionally_required`` (``:?`` / ``?`` guard forms) and
  ``referenced_in_defaults`` (names that only ever appear nested
  inside another operand), plus ``expansion_forms_exercised``.
* ``check_env`` — ``template`` + ``env`` → the mapping audit:
  ``missing_required``, ``triggered_error_forms`` (the ``:?`` guards
  that would abort, distinguishing unset from empty),
  ``unused`` (mapping entries the template never references) and
  ``shadowing`` notes (``:=``/``=`` assignments that would overwrite a
  mapping value the caller already provided, and mapping names that
  collide with shell-reserved variables such as ``IFS`` or ``PATH``).
* ``quote`` — ``template`` + ``env`` → expand, then render the result
  as a safely single-quoted shell literal (embedded single quotes
  spelled ``'\\''``) that reproduces the text byte-for-byte when
  handed to a POSIX shell — verified against real ``bash`` by the
  test suite.

Malformed *parameters* (unknown mode, non-string template, NUL
characters, non-dict ``env``, non-string values, invalid variable
names as mapping keys, inputs over the documented caps) raise
``ValueError`` **before** any computation.  Content-level failures
(not-supported constructs, invalid templates, triggered ``:?``
guards) are structured ``error`` payloads so an agent can react
without catching exceptions.  The process environment is never read;
the tool is deterministic (no clock, no randomness, no network).
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# grammar primitives
# --------------------------------------------------------------------- #

_NAME_START = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
)
_NAME_CHARS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_0123456789"
)
_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_SPECIAL_PARAMS = frozenset("?!@*#$")

# Literals advance the template scan in bulk runs up to the next
# character that can open (or forbid) an expansion.
_NEXT_SPECIAL_RE = re.compile(r"[$`]|\>\(|<\(")

# Sequences rejected anywhere in the template; `$(subsumes `$((`.
_FORBIDDEN_SEQUENCES = (
    ("$((", "arithmetic expansion $((...))"),
    ("$(", "command substitution $(...)"),
    ("`", "command substitution `...`"),
    ("<(", "process substitution <(...)"),
    (">(", "process substitution >(...)"),
)

# Value operands: backslash before these characters disappears and the
# character is emitted literally, losing all grouping meaning.  A
# backslash before a single quote keeps BOTH characters in every
# region (verified against bash) — handled separately in the scanner.
_ESCAPE_CHARS = frozenset("$`\"\\}")

# Documented caps.
MAX_TEMPLATE_CHARS = 2_000_000
MAX_ENV_VARS = 10_000
MAX_VALUE_CHARS = 100_000
MAX_TOTAL_ENV_CHARS = 2_000_000
MAX_NESTING_DEPTH = 8

# Forms that use a fallback operand (the variable itself is optional).
_DEFAULT_FORMS = frozenset(
    ("default_colon", "default_plain", "assign_colon", "assign_plain")
)
# Guard forms (conditionally required variables).
_GUARD_FORMS = frozenset(("error_colon", "error_plain"))
# Forms with no fallback: a top-level use makes the variable required.
_REQUIRED_FORMS = frozenset(
    (
        "basic",
        "length",
        "strip_prefix_shortest",
        "strip_prefix_longest",
        "strip_suffix_shortest",
        "strip_suffix_longest",
        "substring",
        "upper_first",
        "upper_all",
        "lower_first",
        "lower_all",
    )
)

# Shell-reserved names worth a shadowing note in check_env mode.
_RESERVED_NAMES = frozenset(
    (
        "IFS",
        "PATH",
        "HOME",
        "SHELL",
        "USER",
        "PWD",
        "TMPDIR",
        "PS1",
        "PS2",
        "LANG",
        "LC_ALL",
        "LD_PRELOAD",
        "LD_LIBRARY_PATH",
    )
)


class _TemplateError(Exception):
    """Content-level failure (becomes a structured error payload)."""

    def __init__(self, kind: str, position: int, message: str) -> None:
        super().__init__(message)
        self.kind = kind  # "not_supported" | "invalid"
        self.position = position
        self.message = message


class _GuardError(Exception):
    """A ``:?`` / ``?`` guard fired (required variable missing)."""

    def __init__(self, var: str, message: str) -> None:
        super().__init__(message)
        self.var = var
        self.message = message


# --------------------------------------------------------------------- #
# parser
# --------------------------------------------------------------------- #
#
# Nodes:
#   ("lit", text)
#   ("ref", dict) with keys:
#     form     form label (basic / length / default_colon / ... )
#     name     variable name
#     colon    bool (default/assign/guard/alternate forms)
#     word     operand parts (default/assign/guard/alternate forms)
#     pattern  operand parts (strip / case forms)
#     greedy   bool (strip forms; longest match when true)
#     side     "prefix" | "suffix" (strip forms)
#     offset   int (substring form)
#     length   int | None (substring form)
#     op       "^" | "^^" | "," | ",," (case forms)
#     start    template position of the "$" that opens the form
#     source   raw template text of the whole expansion token
#     operand_source  raw operand text (default/assign/guard forms)
#   Operand part:
#     ("lit", text, quoted_bool)
#     ("ref", node-dict, quoted_bool)


class _Parser:
    """Single-template parser (pure, position-tracking)."""

    def __init__(self, template: str) -> None:
        self.s = template
        self.n = len(template)

    # -- helpers ------------------------------------------------------ #

    def _fail(self, kind: str, pos: int, message: str) -> None:
        raise _TemplateError(kind, pos, message)

    def _read_name(self, i: int) -> tuple:
        """Read [A-Za-z_][A-Za-z0-9_]* at i; return (name, end)."""
        j = i
        while j < self.n and self.s[j] in _NAME_CHARS:
            j += 1
        return self.s[i:j], j

    def _node(self, form: str, start: int, end: int, **kw) -> dict:
        node = {"form": form, "start": start, "source": self.s[start:end]}
        node.update(kw)
        return node

    # -- entry -------------------------------------------------------- #

    def parse(self) -> list:
        s, n = self.s, self.n
        nodes = []
        lit_start = 0
        i = 0
        while i < n:
            m = _NEXT_SPECIAL_RE.search(s, i)
            if m is None:
                break
            i = m.start()
            c = s[i]
            if c == "`":
                self._fail(
                    "not_supported",
                    i,
                    "command substitution `...` is not supported; the "
                    "tool never evaluates anything (position %d)" % i,
                )
            if c in "<>" and s[i + 1 : i + 2] == "(":
                self._fail(
                    "not_supported",
                    i,
                    "process substitution %s(...) is not supported; the "
                    "tool never evaluates anything (position %d)"
                    % (c, i),
                )
            # c == "$"
            nxt = s[i + 1] if i + 1 < n else ""
            if nxt in _NAME_START or nxt == "{":
                if lit_start < i:
                    nodes.append(("lit", s[lit_start:i]))
                node, end = self._parse_expansion(i, depth=1)
                nodes.append(("ref", node))
                i = lit_start = end
                continue
            if nxt.isdigit():
                self._fail(
                    "not_supported",
                    i,
                    "positional parameters such as $%s have no value in "
                    "a template (position %d)" % (nxt, i),
                )
            if nxt in _SPECIAL_PARAMS:
                self._fail(
                    "not_supported",
                    i,
                    "special parameter $%s has no value in a template "
                    "(position %d)" % (nxt, i),
                )
            # A lone dollar sign (or `$` at end of input) is literal.
            i += 1
        if lit_start < n:
            nodes.append(("lit", s[lit_start:n]))
        return nodes

    # -- expansions --------------------------------------------------- #

    def _parse_expansion(self, i: int, depth: int) -> tuple:
        """Parse one $NAME / ${...} at position i. Returns (node, end)."""
        if depth > MAX_NESTING_DEPTH:
            self._fail(
                "not_supported",
                i,
                "expansion nesting deeper than %d levels is not "
                "supported (position %d)" % (MAX_NESTING_DEPTH, i),
            )
        s, n = self.s, self.n
        nxt = s[i + 1] if i + 1 < n else ""
        if nxt == "{":
            return self._parse_braced(i, depth)
        # $NAME bare form (nxt is a name start — guaranteed by caller).
        name, end = self._read_name(i + 1)
        if not name:  # pragma: no cover - callers guarantee a name
            self._fail("invalid", i, "expected a variable name (position %d)" % i)
        return self._node("basic", i, end, name=name), end

    def _parse_braced(self, i: int, depth: int) -> tuple:
        s, n = self.s, self.n
        start = i  # position of "$"
        j = i + 2  # first char after "${"
        c = s[j] if j < n else ""
        if c == "":
            self._fail(
                "invalid",
                start,
                "unterminated ${{ (position %d)" % start,
            )
        if c == "!":
            self._fail(
                "not_supported",
                j,
                "${!NAME} indirection is not supported (position %d)"
                % j,
            )
        if c == "#":
            k = j + 1
            if k < n and s[k] in _NAME_START:
                name, end = self._read_name(k)
                if end < n and s[end] == "}":
                    return self._node("length", start, end + 1, name=name), end + 1
                self._fail(
                    "invalid",
                    start,
                    "${#%s...}: bad substitution (position %d)"
                    % (name, start),
                )
            if k < n and s[k] == "}":
                self._fail(
                    "not_supported",
                    j,
                    "special parameter $# has no value in a template "
                    "(position %d)" % j,
                )
            if k < n and (s[k].isdigit() or s[k] in _SPECIAL_PARAMS):
                self._fail(
                    "not_supported",
                    j,
                    "special parameters cannot be used with ${#...} "
                    "in a template (position %d)" % j,
                )
            self._fail(
                "invalid",
                start,
                "${#...}: bad substitution (position %d)" % start,
            )
        if c in _NAME_START:
            name, j = self._read_name(j)
        elif c == "}":
            self._fail(
                "invalid",
                start,
                "${}: empty variable name (position %d)" % start,
            )
        elif c.isdigit():
            _, j = self._read_digits(j)
            if j < n and s[j] == "}":
                self._fail(
                    "not_supported",
                    start,
                    "positional parameters such as ${%s} have no value "
                    "in a template (position %d)" % (c, start),
                )
            self._fail(
                "invalid",
                start,
                "${%s...}: bad substitution (position %d)" % (c, start),
            )
        elif c in _SPECIAL_PARAMS:
            if j + 1 < n and s[j + 1] == "}":
                self._fail(
                    "not_supported",
                    start,
                    "special parameter ${%s} has no value in a "
                    "template (position %d)" % (c, start),
                )
            self._fail(
                "invalid",
                start,
                "${%s...}: bad substitution (position %d)" % (c, start),
            )
        else:
            self._fail(
                "invalid",
                start,
                "${%s...}: bad substitution (position %d)" % (c, start),
            )
        # `name` consumed; j points at the first post-name character.
        if j >= n:
            self._fail(
                "invalid",
                start,
                "unterminated ${{%s (position %d)" % (name, start),
            )
        op = s[j]
        if op == "}":
            return self._node("basic", start, j + 1, name=name), j + 1
        if op == ":":
            nxt = s[j + 1] if j + 1 < n else ""
            if nxt in "-=?+":
                form = {"-": "default", "=": "assign", "?": "error", "+": "alt"}[nxt]
                parts, end = self._scan_word(j + 2, depth, is_pattern=False, err_pos=start)
                return (
                    self._node(
                        form + "_colon",
                        start,
                        end,
                        name=name,
                        colon=True,
                        word=parts,
                        operand_source=s[j + 2 : end - 1],
                    ),
                    end,
                )
            return self._parse_substring(start, name, j)
        if op in "-=?+":  # plain (colon-less) operator forms
            form = {"-": "default", "=": "assign", "?": "error", "+": "alt"}[op]
            parts, end = self._scan_word(j + 1, depth, is_pattern=False, err_pos=start)
            return (
                self._node(
                    form + "_plain",
                    start,
                    end,
                    name=name,
                    colon=False,
                    word=parts,
                    operand_source=s[j + 1 : end - 1],
                ),
                end,
            )
        if op in "#%":
            greedy = j + 1 < n and s[j + 1] == op
            pat_start = j + 2 if greedy else j + 1
            parts, end = self._scan_word(pat_start, depth, is_pattern=True, err_pos=start)
            side = "prefix" if op == "#" else "suffix"
            form = "strip_%s_%s" % (side, "longest" if greedy else "shortest")
            return (
                self._node(
                    form,
                    start,
                    end,
                    name=name,
                    greedy=greedy,
                    side=side,
                    pattern=parts,
                ),
                end,
            )
        if op in "^,":
            doubled = j + 1 < n and s[j + 1] == op
            pat_start = j + 2 if doubled else j + 1
            parts, end = self._scan_word(pat_start, depth, is_pattern=True, err_pos=start)
            base = "upper" if op == "^" else "lower"
            form = "%s_%s" % (base, "all" if doubled else "first")
            return (
                self._node(
                    form,
                    start,
                    end,
                    name=name,
                    op=op * 2 if doubled else op,
                    pattern=parts,
                ),
                end,
            )
        if op == "/":
            self._fail(
                "not_supported",
                j,
                "${%s/pattern/replacement} substitution is not "
                "supported (position %d)" % (name, j),
            )
        if op == "[":
            self._fail(
                "not_supported",
                j,
                "array subscript ${%s[...]} is not supported "
                "(position %d)" % (name, j),
            )
        if op == "@":
            self._fail(
                "not_supported",
                j,
                "expansion operator ${%s@...} is not supported "
                "(position %d)" % (name, j),
            )
        self._fail(
            "invalid",
            start,
            "${%s%s...}: bad substitution (position %d)" % (name, op, start),
        )

    def _read_digits(self, i: int) -> tuple:
        j = i
        while j < self.n and self.s[j].isdigit():
            j += 1
        return self.s[i:j], j

    def _parse_substring(self, start: int, name: str, j: int) -> tuple:
        """j points at the ':' that opens a substring spec."""
        s, n = self.s, self.n
        end = s.find("}", j + 1)
        if end == -1:
            self._fail(
                "invalid",
                start,
                "unterminated ${{%s (position %d)" % (name, start),
            )
        spec = s[j + 1 : end]
        if "$" in spec:
            self._fail(
                "not_supported",
                s.find("$", j + 1, end),
                "substring offsets support integer literals only; "
                "arithmetic or nested expansions such as ${%s:%s} are "
                "not supported (position %d)" % (name, spec.strip(), start),
            )
        parts = spec.split(":", 1)
        labels = ["offset", "length"]
        values = []
        for idx, raw in enumerate(parts):
            stripped = raw.strip(" \t\r\n")
            if stripped == "":
                if len(parts) == 1:
                    self._fail(
                        "invalid",
                        start,
                        "${%s:}: bad substitution (position %d)"
                        % (name, start),
                    )
                values.append(0)  # bash: an omitted side reads as 0
                continue
            if not re.fullmatch(r"[+-]?[0-9]+", stripped):
                kind = "not_supported" if re.fullmatch(
                    r"[0-9+\-*/%() \t]+", stripped
                ) else "invalid"
                self._fail(
                    kind,
                    start,
                    "${%s:%s}: %s must be an integer literal; arithmetic "
                    "expressions are not evaluated (position %d)"
                    % (name, spec.strip(), labels[idx], start),
                )
            values.append(int(stripped))
        offset = values[0]
        length = values[1] if len(values) == 2 else None
        return (
            self._node(
                "substring",
                start,
                end + 1,
                name=name,
                offset=offset,
                length=length,
            ),
            end + 1,
        )

    # -- operand scanning ---------------------------------------------- #

    def _scan_word(self, j: int, depth: int, is_pattern: bool, err_pos: int = 0) -> tuple:
        """Scan a word/pattern operand up to the closing '}'.

        Returns (parts, end_index_after_brace).  Mirrors bash's rules
        for an expansion inside double quotes: single quotes are
        literal characters (but group for brace matching and do not
        stop $ expansion), double quotes group and vanish, and nested
        expansions are parsed wherever a ``$`` starts one — in every
        region.  Backslash handling differs per operand kind exactly
        as bash applies it: value operands keep ``\\x`` for ordinary
        characters, pattern operands drop the backslash before every
        character (pathname-style escaping).
        """
        s, n = self.s, self.n
        state = "plain"  # plain | sq | dq
        parts = []
        buf = []  # list of (char, quoted)

        def flush() -> None:
            run_flag = None
            run = []
            for ch, quoted in buf:
                if run and quoted != run_flag:
                    parts.append(("lit", "".join(run), run_flag))
                    run = []
                run.append(ch)
                run_flag = quoted
            if run:
                parts.append(("lit", "".join(run), run_flag))
            del buf[:]

        i = j
        while i < n:
            c = s[i]
            if c == "\\" and i + 1 < n:
                nxt = s[i + 1]
                if nxt == "'":
                    # Both characters survive in every region (bash
                    # keeps the backslash before a single quote), and
                    # the quote neither opens nor closes a region.
                    buf.append(("\\", True))
                    buf.append(("'", True))
                elif nxt in _ESCAPE_CHARS or is_pattern:
                    # Backslash disappears; the character is literal
                    # (quoted, so pattern metachars stay inert) and has
                    # no grouping effect.
                    buf.append((nxt, True))
                else:
                    buf.append(("\\", False))
                    buf.append((nxt, False))
                i += 2
                continue
            if c == "'":
                if state == "dq":
                    buf.append((c, True))
                else:
                    flush()
                    state = "plain" if state == "sq" else "sq"
                    buf.append((c, True))  # single quotes stay in text
                i += 1
                continue
            if c == '"':
                if state == "sq":
                    buf.append((c, True))
                else:
                    flush()
                    state = "plain" if state == "dq" else "dq"
                    # the double quote itself is removed (quote removal)
                i += 1
                continue
            if c == "}" and state == "plain":
                flush()
                return parts, i + 1
            if c == "$" and i + 1 < n:
                nxt = s[i + 1]
                if nxt == "{":
                    flush()
                    node, end = self._parse_expansion(i, depth + 1)
                    parts.append(("ref", node, state != "plain"))
                    i = end
                    continue
                if nxt in _NAME_START:
                    flush()
                    nm_end = i + 1
                    while nm_end < n and s[nm_end] in _NAME_CHARS:
                        nm_end += 1
                    node = self._node(
                        "basic", i, nm_end, name=s[i + 1 : nm_end]
                    )
                    parts.append(("ref", node, state != "plain"))
                    i = nm_end
                    continue
                if nxt.isdigit() or nxt in _SPECIAL_PARAMS:
                    kind = (
                        "positional parameter"
                        if nxt.isdigit()
                        else "special parameter"
                    )
                    self._fail(
                        "not_supported",
                        i,
                        "%s $%s inside an operand has no value in a "
                        "template (position %d)" % (kind, nxt, i),
                    )
                if nxt == "(":
                    self._fail(
                        "not_supported",
                        i,
                        "command/arithmetic substitution $(...) is not "
                        "supported; the tool never evaluates anything "
                        "(position %d)" % i,
                    )
                # lone dollar: literal
                buf.append(("$", state != "plain"))
                i += 1
                continue
            # '}' inside quotes, and every ordinary character
            buf.append((c, state != "plain"))
            i += 1
        flush()
        self._fail(
            "invalid", err_pos, "unterminated ${{ operand (position %d)" % err_pos
        )


# --------------------------------------------------------------------- #
# glob matcher (bash pathname-style patterns, no extglob)
# --------------------------------------------------------------------- #


def _compile_pattern(chars: list) -> list:
    """Turn [(char, quoted)] into matcher tokens.

    Tokens: ("lit", char) | ("any1",) | ("star",) | ("class", set, negated)
    """
    tokens = []
    i = 0
    n = len(chars)
    while i < n:
        ch, quoted = chars[i]
        if not quoted and ch == "*":
            tokens.append(("star",))
            i += 1
            continue
        if not quoted and ch == "?":
            tokens.append(("any1",))
            i += 1
            continue
        if not quoted and ch == "[":
            bracket, new_i = _compile_bracket(chars, i)
            if bracket is not None:
                tokens.append(bracket)
                i = new_i
                continue
            tokens.append(("lit", ch))  # unmatched '[' is a literal
            i += 1
            continue
        tokens.append(("lit", ch))
        i += 1
    return tokens


def _compile_bracket(chars: list, i: int) -> tuple:
    """Compile a [...] class starting at chars[i] (an unquoted '[')."""
    n = len(chars)
    j = i + 1
    negated = False
    if j < n and chars[j][0] in "!^" and not chars[j][1]:
        negated = True
        j += 1
    members = set()
    first = True
    while j < n:
        ch, quoted = chars[j]
        if ch == "]" and first:
            members.add("]")
            j += 1
            first = False
            continue
        first = False
        if ch == "]" and not quoted:
            return ("class", members, negated), j + 1
        if (
            j + 2 < n
            and chars[j + 1][0] == "-"
            and chars[j + 2][0] != "]"
            and not chars[j + 1][1]
        ):
            lo, hi = ord(ch), ord(chars[j + 2][0])
            if lo > hi:
                lo, hi = hi, lo
            for code in range(lo, hi + 1):
                members.add(chr(code))
            j += 3
            continue
        members.add(ch)
        j += 1
    return None, i  # unterminated: caller treats '[' as literal


def _prefix_match_length(tokens: list, value: str, longest: bool):
    """Length of the shortest/longest prefix of value matching tokens.

    Classic wildcard DP over reachable consumed-lengths; returns None
    when no prefix matches.
    """
    reachable = {0}
    size = len(value)
    for token in tokens:
        if token[0] == "star":
            floor = min(reachable)
            reachable = set(range(floor, size + 1))
        else:
            nxt = set()
            for pos in reachable:
                if pos >= size:
                    continue
                ch = value[pos]
                if token[0] == "any1":
                    nxt.add(pos + 1)
                elif token[0] == "lit":
                    if ch == token[1]:
                        nxt.add(pos + 1)
                else:  # class
                    if (ch in token[1]) != token[2]:
                        nxt.add(pos + 1)
            reachable = nxt
        if not reachable:
            return None
    return max(reachable) if longest else min(reachable)


def _suffix_match_length(tokens: list, value: str, longest: bool):
    """Shortest/longest suffix length: match reversed value against the
    reversed token list (star is symmetric; per-character tokens are
    direction-independent)."""
    return _prefix_match_length(list(reversed(tokens)), value[::-1], longest)


def _pattern_matches_one(tokens: list, ch: str) -> bool:
    """Does the pattern match exactly the single character ch?"""
    return _prefix_match_length(tokens, ch, longest=True) == 1


# --------------------------------------------------------------------- #
# evaluator
# --------------------------------------------------------------------- #


class _Usage:
    """Per-name usage bookkeeping across one operation."""

    def __init__(self) -> None:
        self.forms = {}  # name -> {form: count}
        self.top_level = {}  # name -> seen outside any operand
        self.order = []  # first-appearance order
        self.resolved = {}  # name -> resolved from env at least once
        self.defaults = {}  # name -> first default text that applied
        self.assignments = []  # [{name, value}] in application order
        self.guards = []  # [{name, colon, unset_or_empty, message}]

    def record(self, name: str, form: str, top: bool) -> None:
        if name not in self.forms:
            self.forms[name] = {}
            self.order.append(name)
            self.top_level[name] = False
            self.resolved[name] = False
            self.defaults[name] = None
        self.forms[name][form] = self.forms[name].get(form, 0) + 1
        if top:
            self.top_level[name] = True

    def mark_resolved(self, name: str) -> None:
        self.resolved[name] = True

    def note_default(self, name: str, default_text: str) -> None:
        """Record the default that applied for an unresolved name."""
        if self.defaults[name] is None:
            self.defaults[name] = default_text


class _Evaluator:
    """Expands parsed nodes against an env mapping (pure strings)."""

    def __init__(self, env: dict, usage: _Usage, stop_on_guard: bool) -> None:
        self.env = env  # working copy (:= may mutate it)
        self.usage = usage
        self.stop_on_guard = stop_on_guard

    # -- operands ------------------------------------------------------- #

    def eval_word(self, parts: list, depth: int) -> str:
        out = []
        for part in parts:
            if part[0] == "lit":
                out.append(part[1])
            else:
                out.append(self.eval_ref(part[1], top=False, depth=depth))
        return "".join(out)

    def eval_pattern_chars(self, parts: list, depth: int) -> list:
        chars = []
        for part in parts:
            if part[0] == "lit":
                for ch in part[1]:
                    chars.append((ch, part[2]))
            else:
                for ch in self.eval_ref(part[1], top=False, depth=depth):
                    chars.append((ch, part[2]))
        return chars

    # -- one expansion -------------------------------------------------- #

    def eval_ref(self, node: dict, top: bool, depth: int) -> str:
        name = node["name"]
        form = node["form"]
        present = name in self.env
        value = self.env.get(name, "")
        self.usage.record(name, form, top)
        if form == "basic":
            if present:
                self.usage.mark_resolved(name)
            return value
        if form == "length":
            if present:
                self.usage.mark_resolved(name)
            return str(len(value))
        if form in ("default_colon", "default_plain"):
            colon = form.endswith("colon")
            if not present or (colon and value == ""):
                text = self.eval_word(node["word"], depth + 1)
                self.usage.note_default(name, text)
                return text
            self.usage.mark_resolved(name)
            return value
        if form in ("assign_colon", "assign_plain"):
            colon = form.endswith("colon")
            if not present or (colon and value == ""):
                text = self.eval_word(node["word"], depth + 1)
                self.env[name] = text
                self.usage.note_default(name, text)
                self.usage.assignments.append({"name": name, "value": text})
                return text
            self.usage.mark_resolved(name)
            return value
        if form in ("alt_colon", "alt_plain"):
            colon = form.endswith("colon")
            if present and (value != "" or not colon):
                self.usage.mark_resolved(name)
                return self.eval_word(node["word"], depth + 1)
            return ""
        if form in ("error_colon", "error_plain"):
            colon = form.endswith("colon")
            if not present or (colon and value == ""):
                word = self.eval_word(node["word"], depth + 1)
                message = (
                    word
                    if word != ""
                    else (
                        "parameter null or not set"
                        if colon
                        else "parameter not set"
                    )
                )
                self.usage.guards.append(
                    {
                        "name": name,
                        "colon": colon,
                        "unset_or_empty": "unset" if not present else "empty",
                        "message": message,
                    }
                )
                if self.stop_on_guard:
                    raise _GuardError(name, message)
                return ""
            self.usage.mark_resolved(name)
            return value
        if form.startswith("strip_"):
            if present:
                self.usage.mark_resolved(name)
            tokens = _compile_pattern(
                self.eval_pattern_chars(node["pattern"], depth + 1)
            )
            greedy = node["greedy"]
            if node["side"] == "prefix":
                got = _prefix_match_length(tokens, value, greedy)
            else:
                got = _suffix_match_length(tokens, value, greedy)
            if not got:  # None (no match) or 0 (empty match)
                return value
            if node["side"] == "prefix":
                return value[got:]
            return value[: len(value) - got]
        if form == "substring":
            if not present:
                # bash short-circuits unset variables: the substring
                # expression is never evaluated, so no error can fire.
                return ""
            self.usage.mark_resolved(name)
            return self._substring(node, name, value)
        # case forms
        if present:
            self.usage.mark_resolved(name)
        pattern = node["pattern"]
        tokens = (
            _compile_pattern(self.eval_pattern_chars(pattern, depth + 1))
            if pattern
            else [("any1",)]  # empty pattern defaults to '?'
        )
        op = node["op"]
        out = []
        for idx, ch in enumerate(value):
            if op in ("^", ",") and idx != 0:
                out.append(ch)
                continue
            if _pattern_matches_one(tokens, ch):
                out.append(ch.upper() if op[0] == "^" else ch.lower())
            else:
                out.append(ch)
        return "".join(out)

    @staticmethod
    def _substring(node: dict, name: str, value: str) -> str:
        offset = node["offset"]
        length = node["length"]
        size = len(value)
        start = offset if offset >= 0 else size + offset
        if start < 0 or start > size:
            return ""
        if length is None:
            return value[start:]
        if length >= 0:
            return value[start : start + length]
        end = size + length  # negative length: stop before the tail
        if end < start:
            raise _TemplateError(
                "invalid",
                node["start"],
                "%s: substring expression < 0 (position %d)"
                % (name, node["start"]),
            )
        return value[start:end]


# --------------------------------------------------------------------- #
# tool
# --------------------------------------------------------------------- #


class EnvsubstTool(Tool):
    """Shell-style ``${VAR}`` template expansion and analysis tool.

    Implements the bash/POSIX parameter-expansion subset (basic forms,
    ``:-``/``-`` defaults with the unset-vs-empty distinction, ``:=``
    assignment, ``:?`` guards, ``:+`` alternates, ``${#VAR}`` length,
    ``%``/``#`` glob-pattern stripping, ``:offset:length`` substrings
    and ``^ ^^ , ,,`` case modifiers, with recursive operands) as pure
    string operations — nothing is ever evaluated. Four modes:
    ``expand``, ``analyze``, ``check_env`` and ``quote``.

    Attributes:
        max_template_chars (int): Upper bound on template size.
        max_env_vars (int): Upper bound on the env mapping entry count.
        max_value_chars (int): Upper bound on a single env value.
        max_total_env_chars (int): Upper bound on total env value size.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "envsubst_tool"
    description: str = (
        "Envsubst tool — expand and analyze shell-style ${VAR} templates "
        "with the bash parameter-expansion dialect (basic $VAR/${VAR}, "
        "${VAR:-default} with the unset-vs-empty colon distinction, "
        "${VAR:=default} assignment reported back, ${VAR:?err} guards, "
        "${VAR:+alt}, ${#VAR} length, ${VAR%pat}/${VAR#pat} glob stripping, "
        "${VAR:offset:length} substrings, ${VAR^^pat} case modifiers, "
        "recursive operands), purely on the Python stdlib — nothing is "
        "ever evaluated; $(...), backticks, $((...)) and process "
        "substitution are rejected with structured errors. expand mode "
        "returns the expanded text plus which variables resolved, which "
        "are unresolved (with the default that applied) and any "
        "assignments (mode='expand'); analyze statically reports the "
        "variables a template needs, per-variable forms and defaults "
        "(mode='analyze'); check_env audits a mapping against a template "
        "(missing required variables, triggered :? guards, unused entries, "
        "assignment-overwrite and reserved-name shadowing notes) "
        "(mode='check_env'); quote renders the expansion as a safely "
        "single-quoted shell literal (mode='quote')."
    )

    MODES: ClassVar[tuple] = ("expand", "analyze", "check_env", "quote")

    max_template_chars: int = MAX_TEMPLATE_CHARS
    max_env_vars: int = MAX_ENV_VARS
    max_value_chars: int = MAX_VALUE_CHARS
    max_total_env_chars: int = MAX_TOTAL_ENV_CHARS

    # ------------------------------------------------------------------ #
    # entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        template: Any = None,
        env: Any = None,
    ) -> dict[str, Any]:
        """Run one envsubst operation.

        Args:
            mode (str): One of ``expand`` / ``analyze`` / ``check_env`` /
                ``quote``.
            template (str): The template text (required for every mode;
                may be empty).
            env (dict): Mapping of variable name -> string value.
                Required for ``expand`` / ``check_env`` / ``quote``;
                ignored by ``analyze``. A copy is used: ``:=``
                assignments mutate the copy and are reported, never the
                caller's dict.

        Returns:
            Dict[str, Any]: The operation result (``mode`` and ``result``
                plus mode-specific fields) or a structured ``error``
                payload for content-level failures (not-supported
                constructs, invalid templates, triggered ``:?`` guards).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                "mode must be one of: %s (got %r)"
                % (", ".join(self.MODES), mode)
            )
        clean_template = self._validate_template(template)
        if mode == "analyze":
            return self._run_analyze(clean_template)
        clean_env = self._validate_env(env)
        if mode == "expand":
            return self._run_expand(clean_template, clean_env)
        if mode == "check_env":
            return self._run_check_env(clean_template, clean_env)
        return self._run_quote(clean_template, clean_env)

    # ------------------------------------------------------------------ #
    # input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        raise ValueError("envsubst_tool: %s" % message)

    @classmethod
    def _validate_template(cls, template: Any) -> str:
        if template is None or isinstance(template, bool) or not isinstance(
            template, str
        ):
            cls._invalid("template must be a string (got %r)" % (template,))
        if "\x00" in template:
            cls._invalid(
                "template must not contain NUL characters (position %d)"
                % template.index("\x00")
            )
        if len(template) > MAX_TEMPLATE_CHARS:
            cls._invalid(
                "template exceeds the %s-character limit (got %s characters)"
                % ("{:,}".format(MAX_TEMPLATE_CHARS), "{:,}".format(len(template)))
            )
        return template

    @classmethod
    def _validate_env(cls, env: Any) -> dict:
        if env is None or isinstance(env, bool) or not isinstance(env, dict):
            cls._invalid(
                "env must be a dict of name -> string value (got %r)" % (env,)
            )
        if len(env) > MAX_ENV_VARS:
            cls._invalid(
                "env exceeds the %s-variable limit (got %s variables)"
                % ("{:,}".format(MAX_ENV_VARS), "{:,}".format(len(env)))
            )
        total = 0
        for key, value in env.items():
            if key is None or isinstance(key, bool) or not isinstance(key, str):
                cls._invalid(
                    "env keys must be variable name strings (got %r)" % (key,)
                )
            if not _NAME_RE.match(key):
                cls._invalid(
                    "env keys must match [A-Za-z_][A-Za-z0-9_]* (got %r)" % (key,)
                )
            if value is None or isinstance(value, bool) or not isinstance(
                value, str
            ):
                cls._invalid(
                    "env value for %r must be a string (got %r — convert "
                    "it with str() first)" % (key, value)
                )
            if "\x00" in value:
                cls._invalid(
                    "env value for %r must not contain NUL characters" % key
                )
            if len(value) > MAX_VALUE_CHARS:
                cls._invalid(
                    "env value for %r exceeds the %s-character limit "
                    "(got %s characters)"
                    % (key, "{:,}".format(MAX_VALUE_CHARS), "{:,}".format(len(value)))
                )
            total += len(value)
        if total > MAX_TOTAL_ENV_CHARS:
            cls._invalid(
                "env values exceed the %s-character total limit (got %s)"
                % ("{:,}".format(MAX_TOTAL_ENV_CHARS), "{:,}".format(total))
            )
        return dict(env)

    # ------------------------------------------------------------------ #
    # shared machinery
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse(cls, template: str) -> tuple:
        """Parse a template; convert content errors to error payloads.

        Safety pre-scan first: execution-flavored constructs are
        rejected anywhere in the template, before any parsing
        decisions, with the earliest occurrence winning.
        """
        best = None
        for needle, construct in _FORBIDDEN_SEQUENCES:
            pos = template.find(needle)
            if pos != -1 and (best is None or pos < best[0]):
                best = (pos, construct)
        if best is not None:
            pos, construct = best
            return None, {
                "type": "not_supported",
                "construct": construct.split(" ", 1)[0],
                "position": pos,
                "message": "%s is not supported; the tool never "
                "evaluates anything (position %d)" % (construct, pos),
            }
        try:
            return _Parser(template).parse(), None
        except _TemplateError as exc:
            kind = (
                "not_supported" if exc.kind == "not_supported"
                else "invalid_template"
            )
            return None, {
                "type": kind,
                "position": exc.position,
                "message": exc.message,
            }

    @staticmethod
    def _result(mode: str, **fields) -> dict:
        payload = {"mode": mode, "result": "ok"}
        payload.update(fields)
        return payload

    @staticmethod
    def _error_payload(exc: Exception) -> dict:
        if isinstance(exc, _GuardError):
            return {
                "type": "required_variable_missing",
                "var": exc.var,
                "message": exc.message,
            }
        if isinstance(exc, _TemplateError):
            kind = (
                "not_supported" if exc.kind == "not_supported"
                else "invalid_template"
            )
            return {
                "type": kind,
                "position": exc.position,
                "message": exc.message,
            }
        raise exc  # pragma: no cover - defensive

    @staticmethod
    def _expand_nodes(evaluator: _Evaluator, nodes: list) -> str:
        out = []
        for kind, payload in nodes:
            if kind == "lit":
                out.append(payload)
            else:
                out.append(evaluator.eval_ref(payload, top=True, depth=1))
        return "".join(out)

    # ------------------------------------------------------------------ #
    # modes
    # ------------------------------------------------------------------ #

    def _run_expand(self, template: str, env: dict) -> dict:
        nodes, error = self._parse(template)
        if error is not None:
            return {"error": error}
        usage = _Usage()
        evaluator = _Evaluator(env, usage, stop_on_guard=True)
        try:
            text = self._expand_nodes(evaluator, nodes)
        except (_GuardError, _TemplateError) as exc:
            return {"error": self._error_payload(exc)}
        return self._result(
            "expand",
            text=text,
            expanded=[
                name for name in usage.order if usage.resolved[name]
            ],
            unresolved=[
                {
                    "name": name,
                    "default": usage.defaults[name],
                    "forms": sorted(usage.forms[name]),
                }
                for name in usage.order
                if not usage.resolved[name]
            ],
            assignments=usage.assignments,
            errors=[],
        )

    def _run_analyze(self, template: str) -> dict:
        nodes, error = self._parse(template)
        if error is not None:
            return {"error": error}
        usage = _Usage()

        def walk(usage_list, nodes, top):
            for kind, payload in nodes:
                if kind != "ref":
                    continue
                usage_list.record(payload["name"], payload["form"], top)
                if "word" in payload:
                    for part in payload["word"]:
                        if part[0] == "ref":
                            walk(usage_list, [("ref", part[1])], False)

        walk(usage, nodes, True)
        defaults_raw = {}

        def collect_defaults(nodes):
            for kind, payload in nodes:
                if kind != "ref":
                    continue
                if payload["form"] in _DEFAULT_FORMS and payload["name"] not in defaults_raw:
                    defaults_raw[payload["name"]] = payload["operand_source"]
                for key in ("word", "pattern"):
                    for part in payload.get(key) or []:
                        if part[0] == "ref":
                            collect_defaults([("ref", part[1])])

        collect_defaults(nodes)

        variables = []
        required = []
        optional_with_default = {}
        conditionally_required = []
        for name in usage.order:
            forms_used = sorted(usage.forms[name])
            variables.append(
                {
                    "name": name,
                    "forms_used": forms_used,
                    "occurrences": sum(usage.forms[name].values()),
                }
            )
            if usage.top_level[name] and _REQUIRED_FORMS.intersection(forms_used):
                required.append(name)
            if _DEFAULT_FORMS.intersection(forms_used):
                optional_with_default[name] = defaults_raw.get(name, "")
            if _GUARD_FORMS.intersection(forms_used):
                conditionally_required.append(name)
        exercised = set()
        for forms in usage.forms.values():
            exercised.update(forms)
        return self._result(
            "analyze",
            variables=variables,
            required=required,
            optional_with_default=optional_with_default,
            conditionally_required=conditionally_required,
            referenced_in_defaults=[
                name for name in usage.order if not usage.top_level[name]
            ],
            expansion_forms_exercised=sorted(exercised),
        )

    def _run_check_env(self, template: str, env: dict) -> dict:
        nodes, error = self._parse(template)
        if error is not None:
            return {"error": error}
        usage = _Usage()
        evaluator = _Evaluator(env, usage, stop_on_guard=False)
        try:
            self._expand_nodes(evaluator, nodes)
        except _TemplateError as exc:
            return {"error": self._error_payload(exc)}
        referenced = set(usage.order)
        missing_required = []
        for name in usage.order:
            forms = _REQUIRED_FORMS.intersection(usage.forms[name])
            if name not in env and usage.top_level[name] and forms:
                missing_required.append(
                    {"name": name, "forms": sorted(forms)}
                )
        triggered_dedup = []
        seen_guards = set()
        for guard in usage.guards:
            if guard["name"] not in seen_guards:
                seen_guards.add(guard["name"])
                triggered_dedup.append(
                    {
                        "name": guard["name"],
                        "unset_or_empty": guard["unset_or_empty"],
                        "message": guard["message"],
                    }
                )
        unused = [name for name in env if name not in referenced]
        shadowing = []
        seen_shadow = set()
        for assignment in usage.assignments:
            if (
                assignment["name"] in env
                and assignment["name"] not in seen_shadow
            ):
                seen_shadow.add(assignment["name"])
                shadowing.append(
                    {
                        "kind": "assignment_overwrites",
                        "name": assignment["name"],
                        "note": "the template assigns this variable with "
                        ":= / =; the mapping already provides a value "
                        "for it, which the assignment overwrites",
                    }
                )
        for name in env:
            if name in _RESERVED_NAMES:
                shadowing.append(
                    {
                        "kind": "reserved_name",
                        "name": name,
                        "note": "%s collides with a shell-reserved "
                        "variable name; if the expanded text is later "
                        "used in a shell this value may take effect "
                        "unexpectedly" % name,
                    }
                )
        return self._result(
            "check_env",
            ok=not missing_required and not triggered_dedup,
            missing_required=missing_required,
            triggered_error_forms=triggered_dedup,
            unused=unused,
            shadowing=shadowing,
        )

    def _run_quote(self, template: str, env: dict) -> dict:
        result = self._run_expand(template, env)
        if "error" in result:
            return result
        text = result["text"]
        quoted = "'" + text.replace("'", "'\\''") + "'"
        return self._result(
            "quote",
            text=text,
            quoted=quoted,
            expanded=result["expanded"],
            unresolved=result["unresolved"],
            assignments=result["assignments"],
            errors=[],
        )
