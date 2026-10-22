#!/usr/bin/env python3
"""JqLiteTool: a documented, safe subset of jq path queries over JSON text.

The tool implements a strict subset of the jq query language (behaviour
verified against the real jq binary, 1.6 and later) with four modes:
``validate`` (parse a query and decompose it into steps), ``execute`` (run a
query against JSON text and return every output of the jq result stream),
``explain`` (an English walkthrough of the query) and ``transpile_check``
(parse, re-serialize the parse tree, re-parse and compare semantics).

Supported subset (anything outside this list is rejected with a clear
"not in subset" error instead of being silently mis-evaluated):

* identity ``.``
* field access ``.a``, chains ``.a.b``, quoted ``."key"``, ``.["key"]``
* optional access ``.a?`` (``?`` may follow any single field / index /
  slice / iteration step and suppresses only that step's errors;
  ``(...)?`` wraps a whole parenthesised expression and keeps the outputs
  produced before an error, like jq's ``try``)
* iteration ``.[]``, ``.[]?``, ``.a[]``
* element index ``.a[0]`` (integer literals; negatives index from the end)
* slices ``.[2:5]``, ``.[start:]``, ``.[:end]`` (integer-literal endpoints,
  clamped like jq)
* pipe ``|`` and comma ``,`` with full multi-output stream semantics
* parentheses
* array construction ``[...]`` and object construction ``{a: .b, "k": .v}``
  (including ``{a}`` shorthand; multi-output values build the cartesian
  product in jq's order)
* literals: numbers (jq 1.7 preserves the original literal, e.g. ``1.0``
  stays ``1.0`` and ``1e2`` is printed ``1E+2``), strings, ``true`` /
  ``false`` / ``null``
* the alternative operator ``//`` with jq semantics: only ``null`` and
  ``false`` are falsy (so ``false // 5`` is ``5`` and ``0 // 5`` is ``0``);
  an error on the left side still propagates
* comparisons ``==  !=  <  <=  >  >=`` using jq's total ordering
  (null < false < true < numbers < strings < arrays < objects)
* boolean ``and`` / ``or`` / ``not`` with jq's per-output stream semantics
* builtin filters applied to the piped input: ``length``, ``keys``,
  ``keys_unsorted``, ``has("k")``, ``type``, ``empty``, ``add``, ``first``,
  ``last``, ``reverse``, ``sort``, ``sort_by(.f)``, ``map(.f)``, ``unique``,
  ``min``, ``max``, ``join(",")``, ``select(.f)``

Explicitly excluded (rejected as "not in the subset"): arithmetic operators,
string interpolation ``"\\(...)"``, recursive descent ``..``, ``if/then/else``,
``try``/``catch``, ``reduce``/``foreach``, ``def``, variables ``$x`` and ``as``
bindings, ``limit``, regex helpers (``test``, ``match``, ``capture``, ...),
format strings (``@base64`` and friends), ``env``/``$ENV``, ``input``/
``inputs``, slice steps ``.[::2]``, comments ``#`` and every other jq builtin
outside the list above.

The runtime is standard-library only (``json`` plus a hand-written parser).
Outputs and traces are capped, evaluation is deterministic, object key order
is preserved exactly like jq, and numbers round-trip with jq's formatting.
Only ``execute`` reads a JSON document; no shell commands, filesystem paths
or network access are involved.
"""

# Long jq-style error strings are raised directly, mirroring jq's messages.
# ruff: noqa: TRY003

from __future__ import annotations

import json
from collections.abc import Generator
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------


class JqLiteError(ValueError):
    """Base error for JqLiteTool problems."""


class NotInSubsetError(JqLiteError):
    """A construct real jq supports but this subset deliberately rejects."""

    def __init__(self, construct: str, message: str, position: int = 0):
        super().__init__(message)
        self.construct = construct
        self.message = message
        self.position = position


class JqParseError(JqLiteError):
    """The query is not syntactically valid inside the subset."""

    def __init__(self, message: str, position: int = 0):
        super().__init__(message)
        self.message = message
        self.position = position


class JqRuntimeError(JqLiteError):
    """A jq evaluation error; the message mirrors the real jq error text."""


class JqResourceError(JqLiteError):
    """A configured resource cap was exceeded."""


# --------------------------------------------------------------------------
# Numbers: jq 1.7 preserves the original literal for untouched numbers.
# --------------------------------------------------------------------------


class JInt(int):
    """int that remembers the exact literal it was parsed from."""

    lexeme: str

    def __new__(cls, value: int, lexeme: str):
        obj = super().__new__(cls, value)
        obj.lexeme = lexeme
        return obj


class JFloat(float):
    """float that remembers the exact literal it was parsed from."""

    lexeme: str

    def __new__(cls, value: float, lexeme: str):
        obj = super().__new__(cls, value)
        obj.lexeme = lexeme
        return obj


def _split_exponent(text: str) -> tuple[str, str]:
    """Split a number literal into (mantissa, exponent text) at e/E."""
    for index, char in enumerate(text):
        if char in "eE":
            return text[:index], text[index + 1 :]
    return text, ""


def _normalize_exponent_lexeme(lexeme: str) -> str:
    """Canonicalize an exponent-bearing literal the way jq 1.7 (decNumber) does.

    jq keeps plain decimal literals verbatim but rewrites exponent literals:
    ``1e2`` -> ``1E+2``, ``1e-4`` -> ``0.0001``, ``1.50e1`` -> ``15.0``,
    ``1e17`` -> ``1E+17``.  The rule is decNumber's: plain notation when the
    decimal exponent is <= 0 and the adjusted exponent is >= -6, otherwise
    scientific notation with a signed exponent.
    """
    sign = ""
    body = lexeme
    if body.startswith("-"):
        sign, body = "-", body[1:]
    mantissa, exponent_text = _split_exponent(body)
    exponent = int(exponent_text)
    if "." in mantissa:
        int_part, frac_part = mantissa.split(".", 1)
        digits = int_part + frac_part
        exponent -= len(frac_part)
    else:
        digits = mantissa
    digits = digits.lstrip("0")
    if not digits:
        return sign + "0"
    count = len(digits)
    adjusted = exponent + count - 1
    if exponent <= 0 and adjusted >= -6:
        if exponent == 0:
            return sign + digits
        point = count + exponent
        if point <= 0:
            return sign + "0." + "0" * (-point) + digits
        return sign + digits[:point] + "." + digits[point:]
    adjusted_text = f"+{adjusted}" if adjusted >= 0 else str(adjusted)
    if count == 1:
        return sign + digits + "E" + adjusted_text
    return sign + digits[0] + "." + digits[1:] + "E" + adjusted_text


def _dump_number(value: Any) -> str:
    """Serialize a number exactly like ``jq -c`` would print it."""
    lexeme = getattr(value, "lexeme", None)
    if isinstance(lexeme, str):
        if "e" in lexeme or "E" in lexeme:
            return _normalize_exponent_lexeme(lexeme)
        return lexeme
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    # Computed float: jq prints integral doubles without a fraction part and
    # uses uppercase-E scientific notation otherwise.
    number = float(value)
    if number.is_integer() and abs(number) < 1e17:
        return str(int(number))
    lexeme = repr(number)
    if "e" in lexeme or "E" in lexeme:
        return _normalize_exponent_lexeme(lexeme)
    return lexeme


# --------------------------------------------------------------------------
# jq value helpers
# --------------------------------------------------------------------------

_TYPE_ORDER = {"null": 0, "boolean": 1, "number": 2, "string": 3, "array": 4, "object": 5}


def jq_type(value: Any) -> str:
    """Return jq's name for a value's type."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


def jq_truthy(value: Any) -> bool:
    """jq treats only null and false as falsy (so ``0 // 5`` is ``0``)."""
    return value is not None and value is not False


def dump_compact(value: Any) -> str:
    """Serialize one JSON value exactly like one line of ``jq -c`` output."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return _dump_number(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(dump_compact(item) for item in value) + "]"
    return (
        "{"
        + ",".join(json.dumps(key, ensure_ascii=False) + ":" + dump_compact(item) for key, item in value.items())
        + "}"
    )


def jq_cmp(left: Any, right: Any) -> int:  # noqa: C901
    """jq's total ordering: null < false < true < numbers < strings < arrays < objects."""
    left_type, right_type = jq_type(left), jq_type(right)
    left_order, right_order = _TYPE_ORDER[left_type], _TYPE_ORDER[right_type]
    if left_order != right_order:
        return -1 if left_order < right_order else 1
    if left_type == "null":
        return 0
    if left_type == "boolean":
        return (1 if left else 0) - (1 if right else 0)
    if left_type == "number":
        if left < right:
            return -1
        return 1 if left > right else 0
    if left_type == "string":
        if left < right:
            return -1
        return 1 if left > right else 0
    if left_type == "array":
        for item_left, item_right in zip(left, right, strict=False):
            order = jq_cmp(item_left, item_right)
            if order:
                return order
        return (len(left) > len(right)) - (len(left) < len(right))
    left_keys, right_keys = sorted(left.keys()), sorted(right.keys())
    key_order = jq_cmp(left_keys, right_keys)
    if key_order:
        return key_order
    for key in left_keys:
        order = jq_cmp(left[key], right[key])
        if order:
            return order
    return 0


class _SortKey:
    """cmp_to_key-style wrapper using jq's total ordering."""

    __slots__ = ("value",)

    def __init__(self, value: Any):
        self.value = value

    def __lt__(self, other: _SortKey) -> bool:
        return jq_cmp(self.value, other.value) < 0

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _SortKey) and jq_cmp(self.value, other.value) == 0


def _sorted(elements: list) -> list:
    return sorted(elements, key=_SortKey)


def _err_dump(value: Any) -> str:
    """Dump a value for an error message with jq's byte-based truncation.

    jq keeps dumps of at most 14 bytes intact and otherwise shows the first
    11 bytes followed by ``...`` (the cut can even split a UTF-8 character,
    mirrored here with a replacement character).
    """
    text = dump_compact(value)
    encoded = text.encode("utf-8")
    if len(encoded) <= 14:
        return text
    return encoded[:11].decode("utf-8", errors="replace") + "..."


def _cannot_iterate(value: Any) -> JqRuntimeError:
    return JqRuntimeError(f"Cannot iterate over {jq_type(value)} ({_err_dump(value)})")


def _string_key_desc(name: str) -> str:
    """Render a string key for an index error like jq: keys of at most 29
    bytes are shown quoted, longer ones degrade to just the type name."""
    if len(name.encode("utf-8")) <= 29:
        return f'string "{name}"'
    return "string"


def _cannot_index(value: Any, key_desc: str) -> JqRuntimeError:
    return JqRuntimeError(f"Cannot index {jq_type(value)} with {key_desc}")


# --------------------------------------------------------------------------
# Lexer
# --------------------------------------------------------------------------

# Keywords of jq constructs outside this subset; seeing one is a precise
# "not in subset" rejection rather than a generic syntax error.
_EXCLUDED_KEYWORDS = {
    "if": "if/then/elif/else/end conditionals",
    "then": "if/then/elif/else/end conditionals",
    "elif": "if/then/elif/else/end conditionals",
    "else": "if/then/else/end conditionals",
    "end": "if/then/else/end conditionals",
    "def": "function definitions (def)",
    "as": "as-bindings (E as $x | ...)",
    "reduce": "reduce aggregations",
    "foreach": "foreach iterations",
    "try": "try/catch error handling",
    "catch": "try/catch error handling",
    "label": "label/break control flow",
    "import": "module imports",
    "include": "module includes",
    "__loc__": "__loc__ location literals",
}

_IDENT_START = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_IDENT_CHARS = _IDENT_START | set("0123456789")
_DIGITS = set("0123456789")

# Token kinds that end a term; used to tell binary minus from a negative
# number literal.
_TERM_END_KINDS = {"NUMBER", "STRING", "RPAREN", "RBRACKET", "RBRACE", "QUESTION", "IDENT"}

_SIMPLE_TOKENS = {
    "|": "PIPE",
    ",": "COMMA",
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "{": "LBRACE",
    "}": "RBRACE",
    ";": "SEMI",
    "?": "QUESTION",
    ":": "COLON",
}


class Token:
    __slots__ = ("kind", "position", "value")

    def __init__(self, kind: str, value: Any, position: int):
        self.kind = kind
        self.value = value
        self.position = position

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Token({self.kind}, {self.value!r})"


def lex(query: str) -> list[Token]:  # noqa: C901
    """Tokenize a query, raising NotInSubsetError for excluded constructs."""
    tokens: list[Token] = []
    index, length = 0, len(query)
    while index < length:
        char = query[index]
        if char in " \t\r\n":
            index += 1
            continue
        if char == "#":
            raise NotInSubsetError("comments", "jq comments (# ...) are not in the subset", index)
        if char == "$":
            raise NotInSubsetError("variables", "variables ($name, $ENV) are not in the subset", index)
        if char == "@":
            raise NotInSubsetError(
                "format strings", "format strings (@base64, @text, @csv, ...) are not in the subset", index
            )
        if char == ".":
            if index + 1 < length and query[index + 1] == ".":
                raise NotInSubsetError("recursive descent", "recursive descent (..) is not in the subset", index)
            if index + 1 < length and query[index + 1] in _DIGITS:
                raise JqParseError(f"unexpected digit after '.' at position {index}", index)
            tokens.append(Token("DOT", ".", index))
            index += 1
            continue
        if char in _IDENT_START:
            start = index
            while index < length and query[index] in _IDENT_CHARS:
                index += 1
            word = query[start:index]
            if word in _EXCLUDED_KEYWORDS:
                raise NotInSubsetError(word, f"'{word}' ({_EXCLUDED_KEYWORDS[word]}) is not in the subset", start)
            if word in ("and", "or"):
                tokens.append(Token("LOGIC", word, start))
            elif word in ("true", "false", "null"):
                tokens.append(Token("KEYWORD", word, start))
            else:
                tokens.append(Token("IDENT", word, start))
            continue
        is_negative_literal = char == "-" and index + 1 < length and query[index + 1] in _DIGITS
        if char in _DIGITS or is_negative_literal:
            if is_negative_literal and tokens and tokens[-1].kind in _TERM_END_KINDS:
                # "x - 1" style: binary minus, i.e. excluded arithmetic.
                tokens.append(Token("OP_ARITH", "-", index))
                index += 1
                continue
            start = index
            if is_negative_literal:
                index += 1
            while index < length and query[index] in _DIGITS:
                index += 1
            saw_dot = False
            if index + 1 < length and query[index] == "." and query[index + 1] in _DIGITS:
                saw_dot = True
                index += 1
                while index < length and query[index] in _DIGITS:
                    index += 1
            saw_exponent = False
            if index < length and query[index] in "eE":
                lookahead = index + 1
                if lookahead < length and query[lookahead] in "+-":
                    lookahead += 1
                if lookahead < length and query[lookahead] in _DIGITS:
                    saw_exponent = True
                    index = lookahead
                    while index < length and query[index] in _DIGITS:
                        index += 1
            lexeme = query[start:index]
            tokens.append(Token("NUMBER", (lexeme, saw_dot or saw_exponent), start))
            continue
        if char == '"':
            start = index
            text, index = _lex_string(query, index)
            tokens.append(Token("STRING", text, start))
            continue
        if char in _SIMPLE_TOKENS:
            tokens.append(Token(_SIMPLE_TOKENS[char], char, index))
            index += 1
            continue
        if char == "/" and index + 1 < length and query[index + 1] == "/":
            tokens.append(Token("ALT", "//", index))
            index += 2
            continue
        if char in "+-*/%":
            tokens.append(Token("OP_ARITH", char, index))
            index += 1
            continue
        if char in "=<>!":
            two = query[index : index + 2]
            if two in ("==", "!=", "<=", ">="):
                tokens.append(Token("CMP", two, index))
                index += 2
                continue
            if char == "=":
                raise NotInSubsetError(
                    "assignment", "assignment operators (=, |=, +=, ...) are not in the subset", index
                )
            if char == "!":
                raise JqParseError(f"unexpected '!' at position {index}", index)
            tokens.append(Token("CMP", char, index))
            index += 1
            continue
        raise JqParseError(f"unexpected character {char!r} at position {index}", index)
    tokens.append(Token("EOF", None, length))
    return tokens


_STRING_ESCAPES = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}


def _lex_string(query: str, start: int) -> tuple[str, int]:
    """Lex a double-quoted string literal beginning at ``start``.

    Returns the decoded text and the index just past the closing quote.
    """
    chunks: list[str] = []
    index = start + 1
    length = len(query)
    while index < length:
        char = query[index]
        if char == '"':
            return "".join(chunks), index + 1
        if char == "\\":
            index += 1
            if index >= length:
                break
            esc = query[index]
            if esc == "(":
                raise NotInSubsetError(
                    "string interpolation", 'string interpolation ("\\(expr)") is not in the subset', start
                )
            if esc in _STRING_ESCAPES:
                chunks.append(_STRING_ESCAPES[esc])
                index += 1
                continue
            if esc == "u":
                hex_text = query[index + 1 : index + 5]
                if len(hex_text) == 4 and all(c in "0123456789abcdefABCDEF" for c in hex_text):
                    chunks.append(chr(int(hex_text, 16)))
                    index += 5
                    continue
            raise JqParseError(f"invalid escape sequence at position {index - 1}", index - 1)
        chunks.append(char)
        index += 1
    raise JqParseError("unterminated string literal", start)


# --------------------------------------------------------------------------
# Parser -> AST tuples
# --------------------------------------------------------------------------

# Builtins allowed by the subset: name -> (min_args, max_args).
_BUILTINS: dict[str, tuple[int, int]] = {
    "length": (0, 0),
    "keys": (0, 0),
    "keys_unsorted": (0, 0),
    "has": (1, 1),
    "type": (0, 0),
    "empty": (0, 0),
    "add": (0, 0),
    "first": (0, 0),
    "last": (0, 0),
    "reverse": (0, 0),
    "sort": (0, 0),
    "sort_by": (1, 1),
    "map": (1, 1),
    "unique": (0, 0),
    "min": (0, 0),
    "max": (0, 0),
    "join": (1, 1),
    "select": (1, 1),
    "not": (0, 0),
}


class _Parser:
    """Recursive-descent parser for the jq subset."""

    def __init__(self, tokens: list[Token], max_depth: int):
        self.tokens = tokens
        self.index = 0
        self.max_depth = max_depth
        self.depth = 0

    # -- token helpers ----------------------------------------------------
    def peek(self, offset: int = 0) -> Token:
        return self.tokens[min(self.index + offset, len(self.tokens) - 1)]

    def advance(self) -> Token:
        token = self.tokens[self.index]
        if token.kind != "EOF":
            self.index += 1
        return token

    def expect(self, kind: str, what: str) -> Token:
        token = self.peek()
        if token.kind != kind:
            raise JqParseError(f"expected {what} at position {token.position}", token.position)
        return self.advance()

    # -- grammar (lowest precedence first) ---------------------------------
    def parse_query(self):
        node = self.parse_pipe()
        token = self.peek()
        if token.kind != "EOF":
            if token.kind == "OP_ARITH":
                raise NotInSubsetError(
                    "arithmetic operators",
                    f"arithmetic operator '{token.value}' is not in the subset",
                    token.position,
                )
            raise JqParseError(f"unexpected {token.value!r} at position {token.position}", token.position)
        return node

    def parse_pipe(self):
        self.depth += 1
        try:
            if self.depth > self.max_depth:
                raise JqParseError(f"query nesting exceeds max_depth ({self.max_depth})", self.peek().position)
            node = self.parse_comma()
            while self.peek().kind == "PIPE":
                self.advance()
                node = ("pipe", node, self.parse_comma())
            return node
        finally:
            self.depth -= 1

    def parse_comma(self):
        node = self.parse_alt()
        while self.peek().kind == "COMMA":
            self.advance()
            node = ("comma", node, self.parse_alt())
        return node

    def parse_alt(self):
        node = self.parse_or()
        if self.peek().kind == "ALT":
            self.advance()
            return ("alt", node, self.parse_alt())
        return node

    def parse_or(self):
        node = self.parse_and()
        while self.peek().kind == "LOGIC" and self.peek().value == "or":
            self.advance()
            node = ("or", node, self.parse_and())
        return node

    def parse_and(self):
        node = self.parse_cmp()
        while self.peek().kind == "LOGIC" and self.peek().value == "and":
            self.advance()
            node = ("and", node, self.parse_cmp())
        return node

    def parse_cmp(self):
        node = self.parse_postfix()
        if self.peek().kind == "CMP":
            op = self.advance().value
            return ("cmp", op, node, self.parse_postfix())
        return node

    def parse_postfix(self):
        node = self.parse_primary()
        while True:
            token = self.peek()
            if token.kind == "DOT" and self.peek(1).kind in ("IDENT", "STRING"):
                self.advance()
                name = self.advance().value
                node = ("field", node, name, self._opt())
            elif token.kind == "LBRACKET":
                node = self._parse_brackets(node)
            else:
                break
        return node

    def _opt(self) -> bool:
        if self.peek().kind == "QUESTION":
            self.advance()
            return True
        return False

    def _parse_brackets(self, base):  # noqa: C901
        self.expect("LBRACKET", "'['")
        if self.peek().kind == "RBRACKET":
            self.advance()
            return ("iterate", base, self._opt())
        if self.peek().kind == "COLON":
            self.advance()
            if self.peek().kind == "COLON":
                raise NotInSubsetError(
                    "slice step", "slice steps (.[start:end:step]) are not in the subset", self.peek().position
                )
            end = self._int_literal("slice end")
            if self.peek().kind == "COLON":
                raise NotInSubsetError(
                    "slice step", "slice steps (.[start:end:step]) are not in the subset", self.peek().position
                )
            self.expect("RBRACKET", "']'")
            return ("slice", base, None, end, self._opt())
        if self.peek().kind == "STRING":
            key = self.advance().value
            self.expect("RBRACKET", "']'")
            return ("field", base, key, self._opt())
        start = self._int_literal("index or slice start")
        token = self.peek()
        if token.kind == "RBRACKET":
            self.advance()
            return ("index", base, start, self._opt())
        if token.kind == "COLON":
            self.advance()
            if self.peek().kind == "COLON":
                raise NotInSubsetError(
                    "slice step", "slice steps (.[start:end:step]) are not in the subset", token.position
                )
            if self.peek().kind == "RBRACKET":
                self.advance()
                return ("slice", base, start, None, self._opt())
            end = self._int_literal("slice end")
            if self.peek().kind == "COLON":
                raise NotInSubsetError(
                    "slice step", "slice steps (.[start:end:step]) are not in the subset", self.peek().position
                )
            self.expect("RBRACKET", "']'")
            return ("slice", base, start, end, self._opt())
        raise JqParseError(f"expected ']' or ':' at position {token.position}", token.position)

    def _int_literal(self, what: str) -> JInt:
        token = self.peek()
        if token.kind != "NUMBER" or token.value[1]:
            position = token.position
            raise JqParseError(f"{what} must be an integer literal in this subset (position {position})", position)
        self.advance()
        lexeme = token.value[0]
        return JInt(int(lexeme), lexeme)

    def parse_primary(self):  # noqa: C901
        token = self.peek()
        if token.kind == "DOT":
            nxt = self.peek(1)
            if nxt.kind in ("IDENT", "STRING"):
                self.advance()
                name = self.advance().value
                return ("field", ("id",), name, self._opt())
            self.advance()
            return ("id",)
        if token.kind == "NUMBER":
            lexeme, is_float = token.value
            self.advance()
            value = JFloat(float(lexeme), lexeme) if is_float else JInt(int(lexeme), lexeme)
            return ("lit", value)
        if token.kind == "STRING":
            self.advance()
            return ("lit", token.value)
        if token.kind == "KEYWORD":
            self.advance()
            return ("lit", {"true": True, "false": False, "null": None}[token.value])
        if token.kind == "IDENT":
            return self._parse_call()
        if token.kind == "LPAREN":
            self.advance()
            inner = self.parse_pipe()
            self.expect("RPAREN", "')'")
            if self.peek().kind == "QUESTION":
                self.advance()
                return ("try", inner)
            return ("paren", inner)
        if token.kind == "LBRACKET":
            self.advance()
            if self.peek().kind == "RBRACKET":
                self.advance()
                return ("array", None)
            inner = self.parse_pipe()
            self.expect("RBRACKET", "']'")
            return ("array", inner)
        if token.kind == "LBRACE":
            return self._parse_object()
        if token.kind == "OP_ARITH":
            raise NotInSubsetError(
                "arithmetic operators", f"arithmetic operator '{token.value}' is not in the subset", token.position
            )
        raise JqParseError(f"unexpected {token.value!r} at position {token.position} (expected a term)", token.position)

    def _parse_call(self):
        token = self.advance()
        name = token.value
        if name not in _BUILTINS:
            raise NotInSubsetError(
                "function call",
                f"function '{name}' is not in the jq subset (supported builtins: {', '.join(sorted(_BUILTINS))})",
                token.position,
            )
        min_args, max_args = _BUILTINS[name]
        args: tuple = ()
        if self.peek().kind == "LPAREN":
            if max_args == 0:
                position = self.peek().position
                raise NotInSubsetError(
                    "function call",
                    f"builtin '{name}' takes no arguments in this subset; {name}(...) is not in the jq subset",
                    position,
                )
            self.advance()
            parsed = [self.parse_pipe()]
            while self.peek().kind == "SEMI":
                self.advance()
                parsed.append(self.parse_pipe())
            self.expect("RPAREN", "')'")
            if not (min_args <= len(parsed) <= max_args):
                raise JqParseError(
                    f"builtin '{name}' expects {min_args} argument(s), got {len(parsed)}", token.position
                )
            args = tuple(parsed)
        elif min_args > 0:
            raise JqParseError(f"builtin '{name}' expects an argument: {name}(...)", token.position)
        return ("call", name, args)

    def _parse_object(self):
        self.expect("LBRACE", "'{'")
        entries: list[tuple[str, Any]] = []
        if self.peek().kind == "RBRACE":
            self.advance()
            return ("object", tuple(entries))
        while True:
            token = self.peek()
            if token.kind in ("IDENT", "STRING", "KEYWORD"):
                key = token.value
                self.advance()
                if self.peek().kind == "COLON":
                    self.advance()
                    entries.append((key, self.parse_object_value()))
                elif token.kind == "IDENT":
                    entries.append((key, ("field", ("id",), key, False)))
                else:
                    position = token.position
                    raise JqParseError(f"expected ':' after object key at position {position}", position)
            else:
                position = token.position
                raise JqParseError(f"expected an object key at position {position}", position)
            if self.peek().kind == "COMMA":
                self.advance()
                continue
            self.expect("RBRACE", "'}'")
            return ("object", tuple(entries))

    def parse_object_value(self):
        """Parse an object value with jq's restricted grammar: a term chain
        optionally piped into further term chains (jq's ExpD).  Comma, //,
        and/or and comparisons need parentheses, exactly like real jq."""
        node = self.parse_postfix()
        while self.peek().kind == "PIPE":
            self.advance()
            node = ("pipe", node, self.parse_postfix())
        return node


def parse_query(query: str, max_depth: int = 120):
    """Parse a query into an AST, rejecting outside-subset constructs."""
    try:
        return _Parser(lex(query), max_depth).parse_query()
    except RecursionError:
        raise JqParseError(f"query nesting exceeds max_nesting_depth ({max_depth})") from None


def _iter_children(node):
    """Yield every AST node nested inside ``node`` (conservatively)."""
    for child in node[1:]:
        if isinstance(child, tuple):
            if child and isinstance(child[0], str) and child[0] in _NODE_KINDS:
                yield child
            else:
                # A tuple of nodes (call arguments / object entries).
                for item in child:
                    if isinstance(item, tuple):
                        if item and isinstance(item[0], str) and item[0] in _NODE_KINDS:
                            yield item
                        elif len(item) == 2:
                            key, value_expr = item
                            if not isinstance(key, tuple) and isinstance(value_expr, tuple):
                                yield value_expr


_NODE_KINDS = {
    "id",
    "field",
    "index",
    "iterate",
    "slice",
    "pipe",
    "comma",
    "alt",
    "and",
    "or",
    "cmp",
    "lit",
    "array",
    "object",
    "try",
    "paren",
    "call",
}


def count_ast_nodes(node) -> int:
    """Count AST nodes (iteratively) so overly long query chains get capped."""
    total = 0
    stack = [node]
    while stack:
        current = stack.pop()
        total += 1
        stack.extend(_iter_children(current))
    return total


# --------------------------------------------------------------------------
# Evaluator: eval(node, value) yields the jq output stream.
# --------------------------------------------------------------------------


def _eval(node, value: Any, limit: int | None = None) -> Generator[Any, None, None]:  # noqa: C901
    """Evaluate ``node`` against ``value`` yielding jq's output stream.

    ``limit`` caps how many values a single collector (array construction,
    map, object cartesian product) may gather, mirroring jq's lazy streams
    while bounding memory.
    """
    kind = node[0]
    if kind == "id":
        yield value
    elif kind == "lit":
        yield node[1]
    elif kind == "paren":
        yield from _eval(node[1], value, limit)
    elif kind == "try":
        # jq's try semantics: outputs already produced are kept, an error
        # ends the stream silently.
        stream = _eval(node[1], value, limit)
        while True:
            try:
                item = next(stream)
            except StopIteration:
                return
            except JqRuntimeError:
                return
            yield item
    elif kind == "field":
        _, base, name, opt = node
        for item in _eval(base, value, limit):
            try:
                yield _field(item, name)
            except JqRuntimeError:
                if not opt:
                    raise
    elif kind == "index":
        _, base, idx, opt = node
        for item in _eval(base, value, limit):
            try:
                yield _index(item, idx)
            except JqRuntimeError:
                if not opt:
                    raise
    elif kind == "iterate":
        _, base, opt = node
        for item in _eval(base, value, limit):
            try:
                if isinstance(item, list):
                    yield from item
                elif isinstance(item, dict):
                    yield from item.values()
                else:
                    raise _cannot_iterate(item)
            except JqRuntimeError:
                if not opt:
                    raise
    elif kind == "slice":
        _, base, start, end, opt = node
        for item in _eval(base, value, limit):
            try:
                yield _slice(item, start, end)
            except JqRuntimeError:
                if not opt:
                    raise
    elif kind == "pipe":
        for left_value in _eval(node[1], value, limit):
            yield from _eval(node[2], left_value, limit)
    elif kind == "comma":
        yield from _eval(node[1], value, limit)
        yield from _eval(node[2], value, limit)
    elif kind == "alt":
        produced = False
        for candidate in _eval(node[1], value, limit):
            if jq_truthy(candidate):
                produced = True
                yield candidate
        if not produced:
            yield from _eval(node[2], value, limit)
    elif kind == "and":
        for left_value in _eval(node[1], value, limit):
            if not jq_truthy(left_value):
                yield False
            else:
                for right_value in _eval(node[2], value, limit):
                    yield jq_truthy(right_value)
    elif kind == "or":
        for left_value in _eval(node[1], value, limit):
            if jq_truthy(left_value):
                yield True
            else:
                for right_value in _eval(node[2], value, limit):
                    yield jq_truthy(right_value)
    elif kind == "cmp":
        op = node[1]
        for left_value in _eval(node[2], value, limit):
            for right_value in _eval(node[3], value, limit):
                order = jq_cmp(left_value, right_value)
                yield {
                    "==": order == 0,
                    "!=": order != 0,
                    "<": order < 0,
                    "<=": order <= 0,
                    ">": order > 0,
                    ">=": order >= 0,
                }[op]
    elif kind == "array":
        if node[1] is None:
            yield []
        else:
            yield _collect(_eval(node[1], value, limit), limit)
    elif kind == "object":
        yield from _object(node[1], value, limit)
    elif kind == "call":
        yield from _call(node[1], node[2], value, limit)
    else:  # pragma: no cover - every node kind is handled above
        raise JqRuntimeError(f"internal error: unknown node {kind!r}")


def _collect(stream, limit: int | None) -> list:
    collected: list[Any] = []
    for item in stream:
        collected.append(item)
        if limit is not None and len(collected) > limit:
            raise JqResourceError(f"collected values exceed the cap ({limit})")
    return collected


def _object(entries, value: Any, limit: int | None) -> Generator[dict, None, None]:
    results: list[dict] = [{}]
    for key, value_expr in entries:
        next_results: list[dict] = []
        for partial in results:
            for entry_value in _eval(value_expr, value, limit):
                combined = dict(partial)
                combined[key] = entry_value
                next_results.append(combined)
                if limit is not None and len(next_results) > limit:
                    raise JqResourceError(f"object construction exceeds the cap ({limit})")
        results = next_results
    yield from results


def _field(value: Any, name: str) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(name)
    raise _cannot_index(value, _string_key_desc(name))


def _index(value: Any, idx: int) -> Any:
    if value is None:
        return None
    if isinstance(value, list):
        position = idx + len(value) if idx < 0 else idx
        if 0 <= position < len(value):
            return value[position]
        return None
    raise _cannot_index(value, "number")


def _slice(value: Any, start: int | None, end: int | None) -> Any:
    if value is None:
        return None
    if isinstance(value, (list, str)):
        return value[start:end]
    raise _cannot_index(value, "object")


def _jq_plus(left: Any, right: Any) -> Any:
    """jq's ``+`` (used internally by add/join); the query-level operator stays excluded."""
    if left is None:
        return right
    if right is None:
        return left
    left_type, right_type = jq_type(left), jq_type(right)
    if left_type == right_type:
        if left_type in ("number", "string", "array"):
            return left + right
        if left_type == "object":
            merged = dict(left)
            merged.update(right)
            return merged
    raise JqRuntimeError(f"{left_type} ({_err_dump(left)}) and {right_type} ({_err_dump(right)}) cannot be added")


def _elements(value: Any) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    raise _cannot_iterate(value)


def _join_part(base: str, element: Any) -> str:
    """Convert one join element, raising jq's exact '+' error message otherwise."""
    if element is None:
        return ""
    if isinstance(element, bool):
        return "true" if element else "false"
    if isinstance(element, (int, float)):
        return _dump_number(element)
    if isinstance(element, str):
        return element
    raise JqRuntimeError(f"string ({_err_dump(base)}) and {jq_type(element)} ({_err_dump(element)}) cannot be added")


def _call(name: str, args: tuple, value: Any, limit: int | None) -> Generator[Any, None, None]:  # noqa: C901
    if name == "empty":
        return
    if name == "length":
        if value is None:
            yield 0
        elif isinstance(value, bool):
            raise JqRuntimeError(f"boolean ({_err_dump(value)}) has no length")
        elif isinstance(value, (int, float)):
            # jq numbers are doubles: compute abs on the double value and
            # print the computed double canonically (literal is not kept).
            magnitude = abs(float(value))
            yield magnitude
        else:
            yield len(value)
        return
    if name == "type":
        yield jq_type(value)
        return
    if name == "not":
        yield not jq_truthy(value)
        return
    if name in ("keys", "keys_unsorted"):
        if isinstance(value, dict):
            yield sorted(value.keys()) if name == "keys" else list(value.keys())
        elif isinstance(value, list):
            yield list(range(len(value)))
        else:
            raise JqRuntimeError(f"{jq_type(value)} ({_err_dump(value)}) has no keys")
        return
    if name == "has":
        for key in _eval(args[0], value, limit):
            kind = jq_type(key)
            if isinstance(value, dict):
                if kind != "string":
                    raise JqRuntimeError(f"Cannot check whether object has a {kind} key")
                yield key in value
            elif isinstance(value, list):
                if isinstance(key, bool):
                    raise JqRuntimeError("Cannot check whether array has a boolean key")
                if kind == "number":
                    position = int(key)
                    yield 0 <= position < len(value)
                else:
                    raise JqRuntimeError(f"Cannot check whether array has a {kind} key")
            else:
                raise JqRuntimeError(f"Cannot check whether {jq_type(value)} has a {kind} key")
        return
    if name == "select":
        for check in _eval(args[0], value, limit):
            if jq_truthy(check):
                yield value
        return
    if name == "map":
        yield _collect((item for element in _elements(value) for item in _eval(args[0], element, limit)), limit)
        return
    if name == "add":
        elements = _elements(value)
        if not elements:
            yield None
            return
        accumulator = elements[0]
        for element in elements[1:]:
            accumulator = _jq_plus(accumulator, element)
        yield accumulator
        return
    if name == "first":
        yield _index(value, 0)
        return
    if name == "last":
        yield _index(value, -1)
        return
    if name == "reverse":
        if value is None:
            yield []
        elif isinstance(value, list):
            yield list(reversed(value))
        else:
            raise _cannot_index(value, "number")
        return
    if name == "sort":
        if not isinstance(value, list):
            raise JqRuntimeError(f"{jq_type(value)} ({_err_dump(value)}) cannot be sorted, as it is not an array")
        yield _sorted(value)
        return
    if name == "sort_by":
        decorated = [(_collect(_eval(args[0], element, limit), limit), element) for element in _elements(value)]
        decorated.sort(key=lambda pair: _SortKey(pair[0]))
        yield [element for _, element in decorated]
        return
    if name == "unique":
        output: list[Any] = []
        for element in _sorted(_elements(value)):
            if not output or jq_cmp(output[-1], element) != 0:
                output.append(element)
        yield output
        return
    if name in ("min", "max"):
        if not isinstance(value, (list, dict)):
            # jq's min/max go through its internal reduce, whose non-array
            # error reads like this (value shown twice, truncated like jq).
            kind, shown = jq_type(value), _err_dump(value)
            raise JqRuntimeError(f"{kind} ({shown}) and {kind} ({shown}) cannot be iterated over")
        elements = _elements(value)
        if not elements:
            yield None
            return
        best = elements[0]
        for element in elements[1:]:
            order = jq_cmp(element, best)
            if (name == "min" and order < 0) or (name == "max" and order > 0):
                best = element
        yield best
        return
    if name == "join":
        for separator in _eval(args[0], value, limit):
            elements = _elements(value)
            if not elements:
                yield ""
                continue
            # jq evaluates the separator only from the second element on, so
            # single-element arrays never fail on a non-string separator.
            accumulator = _join_part("", elements[0])
            for element in elements[1:]:
                if not isinstance(separator, str):
                    raise JqRuntimeError(
                        f"string ({_err_dump(accumulator)}) and {jq_type(separator)} "
                        f"({_err_dump(separator)}) cannot be added"
                    )
                accumulator = accumulator + separator
                accumulator = accumulator + _join_part(accumulator, element)
            yield accumulator
        return
    raise JqRuntimeError(f"internal error: unknown builtin {name!r}")  # pragma: no cover


# --------------------------------------------------------------------------
# validate steps / explain / transpile
# --------------------------------------------------------------------------


def decompose_steps(node) -> list[dict[str, Any]]:
    """Flatten the AST into a human-readable pipeline decomposition."""
    steps: list[dict[str, Any]] = []
    _walk_steps(node, steps)
    for index, step in enumerate(steps, start=1):
        step["step"] = index
    return steps


def _walk_steps(node, steps: list[dict[str, Any]]) -> None:  # noqa: C901
    kind = node[0]
    optional_note = " (optional: errors on this step are suppressed)"
    if kind == "id":
        steps.append({"op": "identity", "detail": "emit the input value unchanged"})
    elif kind == "paren":
        steps.append({"op": "group", "detail": "group a sub-expression (no semantic effect)"})
        _walk_steps(node[1], steps)
    elif kind == "field":
        _walk_steps(node[1], steps)
        suffix = optional_note if node[3] else ""
        steps.append({"op": "field_access", "detail": f'access field "{node[2]}"{suffix}'})
    elif kind == "index":
        _walk_steps(node[1], steps)
        suffix = optional_note if node[3] else ""
        direction = " (negative counts from the end)" if node[2] < 0 else ""
        steps.append({"op": "element_index", "detail": f"access index {node[2]}{direction}{suffix}"})
    elif kind == "iterate":
        _walk_steps(node[1], steps)
        suffix = optional_note if node[2] else ""
        steps.append(
            {"op": "iterate", "detail": "emit every element of the array / every value of the object" + suffix}
        )
    elif kind == "slice":
        _walk_steps(node[1], steps)
        suffix = optional_note if node[4] else ""
        start_text = "start" if node[2] is None else str(node[2])
        end_text = "end" if node[3] is None else str(node[3])
        steps.append({"op": "slice", "detail": f"keep positions {start_text} up to {end_text} (end exclusive){suffix}"})
    elif kind == "pipe":
        _walk_steps(node[1], steps)
        steps.append({"op": "pipe", "detail": "feed each output of the left side into the right side"})
        _walk_steps(node[2], steps)
    elif kind == "comma":
        _walk_steps(node[1], steps)
        steps.append({"op": "comma", "detail": "also run the next branch and append its outputs in order"})
        _walk_steps(node[2], steps)
    elif kind == "alt":
        _walk_steps(node[1], steps)
        steps.append(
            {
                "op": "alternative",
                "detail": "emit left outputs that are not null/false; if there are none, emit the right side",
            }
        )
        _walk_steps(node[2], steps)
    elif kind in ("and", "or"):
        _walk_steps(node[1], steps)
        _walk_steps(node[2], steps)
        steps.append({"op": kind, "detail": f"jq boolean '{kind}' over every pair of outputs (null/false are falsy)"})
    elif kind == "cmp":
        _walk_steps(node[2], steps)
        _walk_steps(node[3], steps)
        steps.append(
            {
                "op": "compare",
                "detail": f"compare both sides with '{node[1]}' using jq's total ordering "
                "(null < false < true < numbers < strings < arrays < objects)",
            }
        )
    elif kind == "lit":
        steps.append({"op": "literal", "detail": f"constant value {dump_compact(node[1])}"})
    elif kind == "array":
        steps.append({"op": "array_construction", "detail": "collect all outputs of the inner query into one array"})
        if node[1] is not None:
            _walk_steps(node[1], steps)
    elif kind == "object":
        keys = ", ".join(f'"{key}"' for key, _ in node[1]) or "(none)"
        steps.append(
            {
                "op": "object_construction",
                "detail": f"build an object from the key/value pairs [{keys}] "
                "(multi-output values build the cartesian product in jq's order)",
            }
        )
        for _, value_expr in node[1]:
            _walk_steps(value_expr, steps)
    elif kind == "try":
        steps.append({"op": "try", "detail": "suppress errors of the wrapped expression (empty output instead)"})
        _walk_steps(node[1], steps)
    elif kind == "call":
        name, args = node[1], node[2]
        if args:
            rendered = f"apply builtin filter {name}({', '.join(to_source(arg) for arg in args)})"
        else:
            rendered = f"apply builtin filter {name}"
        steps.append({"op": "builtin", "detail": rendered})
        for arg in args:
            _walk_steps(arg, steps)
    else:  # pragma: no cover - every node kind is handled above
        raise JqRuntimeError(f"internal error: unknown node {kind!r}")


def explain(node) -> str:
    """Render an English walkthrough of the query."""
    return _explain(node, "the input value")


def _lower_first(text: str) -> str:
    return text[0].lower() + text[1:] if text else text


def _explain(node, subject: str) -> str:  # noqa: C901
    kind = node[0]
    if kind == "id":
        return f"Return {subject} unchanged."
    if kind == "paren":
        return _explain(node[1], subject)
    if kind == "field":
        optional = "; if this step errors it produces no output instead" if node[3] else ""
        return f'{_explain(node[1], subject)} Then read field "{node[2]}" (missing fields give null){optional}.'
    if kind == "index":
        optional = "; if this step errors it produces no output instead" if node[3] else ""
        tail = "counting from the end" if node[2] < 0 else ""
        return f"{_explain(node[1], subject)} Then take element {node[2]}{tail} (out of range gives null){optional}."
    if kind == "iterate":
        optional = " (errors suppressed)" if node[2] else ""
        return (
            f"{_explain(node[1], subject)} Then, for each element or value it produced, "
            f"emit it as its own output{optional}."
        )
    if kind == "slice":
        optional = " (errors suppressed)" if node[4] else ""
        start_text = "the start" if node[2] is None else str(node[2])
        end_text = "the end" if node[3] is None else str(node[3])
        return (
            f"{_explain(node[1], subject)} Then keep the part from position {start_text} "
            f"up to {end_text} (end exclusive){optional}."
        )
    if kind == "pipe":
        left = _explain(node[1], subject)
        right = _explain(node[2], "each value produced so far")
        return f"{left} The results then flow into the next stage: {_lower_first(right)}"
    if kind == "comma":
        left = _explain(node[1], subject)
        right = _explain(node[2], subject)
        return f"{left} Separately, on the same input: {_lower_first(right)}"
    if kind == "alt":
        left = _explain(node[1], subject)
        right = _explain(node[2], subject)
        return (
            f"{left} Only outputs that are neither null nor false are kept (jq treats false as falsy "
            f"for '//'); if nothing remains, use the alternative instead: {_lower_first(right)}"
        )
    if kind == "and":
        return (
            f"Compute '{to_source(node[1])}' and '{to_source(node[2])}' with jq's boolean 'and': each "
            f"null/false left output yields false directly, every other left output is combined with "
            f"the truthiness of each right output."
        )
    if kind == "or":
        return (
            f"Compute '{to_source(node[1])}' or '{to_source(node[2])}' with jq's boolean 'or': each "
            f"truthy left output yields true directly, every other left output is combined with the "
            f"truthiness of each right output."
        )
    if kind == "cmp":
        return (
            f"Compare '{to_source(node[2])}' {node[1]} '{to_source(node[3])}' using jq's total ordering "
            "(null < false < true < numbers < strings < arrays < objects) and emit one boolean per pair."
        )
    if kind == "lit":
        return f"Emit the constant value {dump_compact(node[1])}."
    if kind == "array":
        if node[1] is None:
            return "Emit an empty array."
        return f"{_explain(node[1], 'the input value')} All outputs are collected into a single array."
    if kind == "object":
        pairs = ", ".join(f'"{key}": {to_source(value_expr)}' for key, value_expr in node[1])
        return (
            f"Build an object with the pairs {pairs}; values may produce several outputs, in which "
            f"case one object per combination is emitted in jq's order."
        )
    if kind == "try":
        return f"{_explain(node[1], subject)} Any error from this wrapped expression is suppressed to empty output."
    if kind == "call":
        name, args = node[1], node[2]
        rendered = name if not args else f"{name}({', '.join(to_source(arg) for arg in args)})"
        specifics = {
            "select": "keep the current input only when the condition output is not null/false",
            "length": "measure it (array/object element count, string length, number absolute value, null gives 0)",
            "keys": "list its key names in sorted order (arrays give the index range)",
            "keys_unsorted": "list its key names in original order (arrays give the index range)",
            "has": "check whether that key/index exists",
            "type": "report its jq type",
            "empty": "produce no output at all",
            "add": "fold its elements with jq's '+' rules (numbers sum, strings/arrays concatenate, objects merge)",
            "first": "take its first element (like .[0], so null when absent)",
            "last": "take its last element (like .[-1], so null when absent)",
            "reverse": "reverse an array (null gives [])",
            "sort": "sort an array with jq's total ordering",
            "sort_by": "sort an array by the array of all outputs of the key expression",
            "map": "apply the inner query to every element and collect the outputs into one array",
            "unique": "sort and drop duplicates",
            "min": "take the smallest element under jq's ordering (null when empty)",
            "max": "take the largest element under jq's ordering (null when empty)",
            "join": "concatenate its stringifiable elements with the separator",
            "not": "emit true when the input is null/false, otherwise false",
        }
        return f"Apply {rendered} to {subject}: {specifics.get(name, f'apply the builtin filter {name}')}."
    raise JqRuntimeError(f"internal error: unknown node {kind!r}")  # pragma: no cover


# Precedence levels for minimal parenthesization in to_source.
_PRECEDENCE = {
    "pipe": 1,
    "comma": 2,
    "alt": 3,
    "or": 4,
    "and": 5,
    "cmp": 6,
    "field": 7,
    "index": 7,
    "iterate": 7,
    "slice": 7,
    "try": 7,
    "call": 7,
    "array": 7,
    "object": 7,
    "lit": 8,
    "id": 8,
    "paren": 8,
}

_PATH_BASE_KINDS = {"id", "field", "index", "iterate", "slice", "paren", "try"}


def _is_ident(name: str) -> bool:
    return bool(name) and name[0] in _IDENT_START and all(char in _IDENT_CHARS for char in name)


def _key_text(name: str) -> str:
    return name if _is_ident(name) else json.dumps(name, ensure_ascii=False)


def to_source(node) -> str:  # noqa: C901
    """Serialize the parse tree back to a canonical jq-subset query."""
    kind = node[0]
    if kind == "id":
        return "."
    if kind == "lit":
        return dump_compact(node[1])
    if kind == "paren":
        return "(" + to_source(node[1]) + ")"
    if kind == "try":
        return "(" + to_source(node[1]) + ")?"
    if kind == "field":
        _, base, name, opt = node
        suffix = "?" if opt else ""
        if base[0] == "id":
            return f".{_key_text(name)}{suffix}"
        return f"{_path_base_source(base)}.{_key_text(name)}{suffix}"
    if kind == "index":
        _, base, idx, opt = node
        base_source = _path_base_source(base)
        return f"{base_source}[{idx}]" + ("?" if opt else "")
    if kind == "iterate":
        _, base, opt = node
        base_source = _path_base_source(base)
        return f"{base_source}[]" + ("?" if opt else "")
    if kind == "slice":
        _, base, start, end, opt = node
        base_source = _path_base_source(base)
        start_text = "" if start is None else str(start)
        end_text = "" if end is None else str(end)
        return f"{base_source}[{start_text}:{end_text}]" + ("?" if opt else "")
    if kind == "pipe":
        return f"{_operand(node[1], 1)} | {_operand(node[2], 1)}"
    if kind == "comma":
        return f"{_operand(node[1], 2)}, {_operand(node[2], 2)}"
    if kind == "alt":
        return f"{_operand(node[1], 3)} // {_operand(node[2], 3)}"
    if kind == "or":
        return f"{_operand(node[1], 4)} or {_operand(node[2], 4)}"
    if kind == "and":
        return f"{_operand(node[1], 5)} and {_operand(node[2], 5)}"
    if kind == "cmp":
        return f"{_operand(node[2], 6)} {node[1]} {_operand(node[3], 6)}"
    if kind == "array":
        return "[]" if node[1] is None else "[" + to_source(node[1]) + "]"
    if kind == "object":
        if not node[1]:
            return "{}"
        parts = [f"{_key_text(key)}: {_operand(value_expr, 3)}" for key, value_expr in node[1]]
        return "{" + ", ".join(parts) + "}"
    if kind == "call":
        name, args = node[1], node[2]
        if not args:
            return name
        return name + "(" + "; ".join(to_source(arg) for arg in args) + ")"
    raise JqRuntimeError(f"internal error: unknown node {kind!r}")  # pragma: no cover


def _path_base_source(base) -> str:
    if base[0] in _PATH_BASE_KINDS:
        return to_source(base)
    return "(" + to_source(base) + ")"


def _operand(node, minimum: int) -> str:
    source = to_source(node)
    if _PRECEDENCE.get(node[0], 8) < minimum:
        return "(" + source + ")"
    return source


def ast_equal(left, right) -> bool:
    """Structural equality of two ASTs (numbers by value, bools kept distinct)."""
    if isinstance(left, tuple) and isinstance(right, tuple):
        if len(left) != len(right):
            return False
        return all(ast_equal(a, b) for a, b in zip(left, right, strict=False))
    if isinstance(left, tuple) or isinstance(right, tuple):
        return False
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    return type(left) is type(right) and left == right


# --------------------------------------------------------------------------
# Pipeline execution with stream semantics and stage tracing
# --------------------------------------------------------------------------


def _flatten_pipe(node) -> list:
    """Split a top-level pipe chain into its stages."""
    if node[0] == "pipe":
        return _flatten_pipe(node[1]) + _flatten_pipe(node[2])
    return [node]


def run_pipeline(
    node,
    root: Any,
    max_outputs: int,
    max_intermediates: int,
    max_trace_values: int,
    max_value_chars: int,
    max_trace_steps: int,
) -> dict[str, Any]:
    """Evaluate the query and collect outputs with jq's exact stream semantics.

    Outputs are emitted one per result and serialized like ``jq -c`` lines;
    when jq would abort with an error, whatever was already produced is kept
    (jq prints the partial stream before the error).  The execution trace is
    derived from a stage-wise pass over top-level pipe stages and is capped.
    """
    outputs: list[str] = []
    truncated = False
    error: JqRuntimeError | None = None
    stream = _eval(node, root, max_intermediates)
    try:
        for value in stream:
            outputs.append(dump_compact(value))
            if len(outputs) >= max_outputs:
                truncated = True
                break
    except JqResourceError:
        raise
    except JqRuntimeError as exc:
        error = exc
    trace = _stage_trace(node, root, max_intermediates, max_trace_values, max_value_chars, max_trace_steps)
    result = {
        "outputs": outputs,
        "output_count": len(outputs),
        "truncated": truncated,
        "execution_trace": trace,
    }
    if error is not None:
        result["error"] = str(error)
    return result


def _stage_trace(
    node, root: Any, max_intermediates: int, max_trace_values: int, max_value_chars: int, max_trace_steps: int
) -> list[dict[str, Any]]:
    """Informational per-stage intermediate values of the top-level pipe chain."""
    trace: list[dict[str, Any]] = []
    current: list[Any] = [root]
    for stage in _flatten_pipe(node):
        if len(trace) >= max_trace_steps:
            break
        produced: list[Any] = []
        failed = False
        for value in current:
            try:
                produced.extend(_eval(stage, value, max_intermediates))
            except (JqRuntimeError, JqResourceError):
                failed = True
                break
        sampled = [dump_compact(item)[:max_value_chars] for item in produced[:max_trace_values]]
        trace.append(
            {
                "stage": len(trace) + 1,
                "query": to_source(stage)[:max_value_chars],
                "value_count": len(produced),
                "values": sampled,
                "values_truncated": len(produced) > max_trace_values,
            }
        )
        if failed:
            break
        current = produced
    return trace


def _load_json(text: str) -> Any:
    """Parse JSON text keeping exact number literals (jq 1.7 behaviour)."""
    return json.loads(
        text,
        parse_int=lambda lexeme: JInt(int(lexeme), lexeme),
        parse_float=lambda lexeme: JFloat(float(lexeme), lexeme),
    )


# --------------------------------------------------------------------------
# The tool
# --------------------------------------------------------------------------


class JqLiteTool(Tool):
    """Validate, execute, explain and round-trip a documented subset of jq queries."""

    max_query_length: int = 10_000
    max_input_bytes: int = 1_000_000
    max_ast_nodes: int = 5_000
    max_nesting_depth: int = 120
    max_outputs: int = 1_000
    max_intermediates: int = 1_000_000
    max_trace_values: int = 50
    max_trace_steps: int = 100
    max_value_chars: int = 200

    _MODES: ClassVar[tuple[str, ...]] = ("validate", "execute", "explain", "transpile_check")

    def execute(self, mode: str, query: str, json_text: str | None = None) -> dict[str, Any]:  # noqa: C901
        """Run one of the four tool modes.

        Args:
            mode: ``validate``, ``execute``, ``explain`` or ``transpile_check``.
            query: The jq-subset query string.
            json_text: The JSON document (required for ``execute``).

        Returns:
            A structured result dict; input problems become structured errors
            instead of exceptions.
        """
        try:
            self._validate_config()
            mode = self._checked_mode(mode)
            query = self._checked_query(query)
            try:
                ast = parse_query(query, self.max_nesting_depth)
            except NotInSubsetError as exc:
                if mode in ("validate", "transpile_check"):
                    return self._validate_failure(exc, mode)
                return self._subset_error(exc)
            except JqParseError as exc:
                if mode in ("validate", "transpile_check"):
                    return self._validate_failure(exc, mode)
                return self._error("parse_error", exc.message)
            node_count = count_ast_nodes(ast)
            if node_count > self.max_ast_nodes:
                detail = f"query has {node_count} AST nodes, exceeding max_ast_nodes ({self.max_ast_nodes})"
                if mode in ("validate", "transpile_check"):
                    return self._validate_failure(JqParseError(detail), mode)
                return self._error("validation_error", detail)
            if mode == "validate":
                return {
                    "status": "success",
                    "mode": mode,
                    "valid": True,
                    "steps": decompose_steps(ast),
                    "unsupported_constructs": [],
                    "canonical_query": to_source(ast),
                }
            if mode == "explain":
                return {
                    "status": "success",
                    "mode": mode,
                    "explanation": explain(ast),
                    "steps": decompose_steps(ast),
                }
            if mode == "transpile_check":
                return self._transpile_check(ast)
            return self._execute_mode(ast, json_text)
        except (TypeError, ValueError, JqLiteError) as exc:
            return self._error("validation_error", str(exc))
        except RecursionError:
            detail = f"query nesting exceeds max_nesting_depth ({self.max_nesting_depth})"
            if mode in ("validate", "transpile_check"):
                return self._validate_failure(JqParseError(detail), mode)
            return self._error("validation_error", detail)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error("operation_error", f"jq-lite execution failed: {exc}")

    def _checked_mode(self, mode: Any) -> str:
        if not isinstance(mode, str) or mode not in self._MODES:
            raise ValueError(f"mode must be one of {', '.join(self._MODES)}")
        return mode

    def _checked_query(self, query: Any) -> str:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if len(query) > self.max_query_length:
            raise ValueError(f"query exceeds max_query_length ({self.max_query_length})")
        return query

    async def async_execute(self, mode: str, query: str, json_text: str | None = None) -> dict[str, Any]:
        """Asynchronously run the same modes as :meth:`execute`."""
        return self.execute(mode=mode, query=query, json_text=json_text)

    # -- helpers ------------------------------------------------------------
    def _validate_config(self) -> None:
        for name in (
            "max_query_length",
            "max_input_bytes",
            "max_ast_nodes",
            "max_nesting_depth",
            "max_outputs",
            "max_intermediates",
            "max_trace_values",
            "max_trace_steps",
            "max_value_chars",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    def _transpile_check(self, ast) -> dict[str, Any]:
        canonical = to_source(ast)
        try:
            reparsed = parse_query(canonical, self.max_nesting_depth)
        except (JqParseError, NotInSubsetError) as exc:
            return {
                "status": "success",
                "mode": "transpile_check",
                "valid": True,
                "round_trip": False,
                "canonical_query": canonical,
                "reparse_error": str(exc),
            }
        return {
            "status": "success",
            "mode": "transpile_check",
            "valid": True,
            "round_trip": ast_equal(ast, reparsed) and to_source(reparsed) == canonical,
            "canonical_query": canonical,
            "reparsed_query": to_source(reparsed),
        }

    def _execute_mode(self, ast, json_text: Any) -> dict[str, Any]:
        if not isinstance(json_text, str) or not json_text.strip():
            raise ValueError("json_text is required for execute mode")
        if len(json_text.encode("utf-8")) > self.max_input_bytes:
            raise ValueError(f"json_text exceeds max_input_bytes ({self.max_input_bytes})")
        try:
            root = _load_json(json_text)
        except json.JSONDecodeError as exc:
            return self._error("json_error", f"invalid JSON input: {exc.msg} (line {exc.lineno}, column {exc.colno})")
        try:
            result = run_pipeline(
                ast,
                root,
                max_outputs=self.max_outputs,
                max_intermediates=self.max_intermediates,
                max_trace_values=self.max_trace_values,
                max_value_chars=self.max_value_chars,
                max_trace_steps=self.max_trace_steps,
            )
        except JqResourceError as exc:
            return self._error("resource_limit", str(exc))
        if "error" in result:
            return {
                "status": "error",
                "mode": "execute",
                "error_type": "jq_error",
                "message": result.pop("error"),
                "outputs": result["outputs"],
                "output_count": result["output_count"],
                "truncated": result["truncated"],
                "execution_trace": result["execution_trace"],
            }
        result["status"] = "success"
        result["mode"] = "execute"
        return result

    def _subset_error(self, exc: NotInSubsetError) -> dict[str, Any]:
        payload = self._error("not_in_subset", exc.message)
        payload["unsupported_constructs"] = [
            {"construct": exc.construct, "message": exc.message, "position": exc.position}
        ]
        return payload

    def _validate_failure(self, exc: JqLiteError, mode: str = "validate") -> dict[str, Any]:
        if isinstance(exc, NotInSubsetError):
            return {
                "status": "success",
                "mode": mode,
                "valid": False,
                "steps": [],
                "unsupported_constructs": [
                    {"construct": exc.construct, "message": exc.message, "position": exc.position}
                ],
            }
        return {
            "status": "success",
            "mode": mode,
            "valid": False,
            "steps": [],
            "unsupported_constructs": [],
            "parse_error": {"message": exc.message, "position": getattr(exc, "position", 0)},
        }

    @staticmethod
    def _error(kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "message": message}
