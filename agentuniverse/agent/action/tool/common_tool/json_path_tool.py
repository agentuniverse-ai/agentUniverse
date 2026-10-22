#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: json_path_tool.py

"""JSON path query tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency JSON query helper
agents can call to pull values out of nested JSON documents — model
outputs, API response snapshots, configuration blobs — without shipping
a third-party JSONPath package.

The tool is a strictly-validated façade over the standard library
``json`` module and supports two modes:

* ``query`` — take a JSON document (as text or an already-decoded
  ``dict`` / ``list``) and a path, and return every value the path
  selects. Each match carries its concrete rendered path (for example
  ``$.store.book[0].title``) and its value, plus ``found`` / ``count``
  / ``truncated`` status.
* ``validate`` — parse a path without any data and report the parsed
  segments, so an agent can verify a path before using it.

Supported path syntax (a practical JSONPath subset):

* an optional leading ``$`` root; ``$`` alone selects the whole
  document;
* dot keys for objects (``$.store.bicycle.color``), where a bare key
  matches ``[A-Za-z_][A-Za-z0-9_-]*``;
* quoted bracket keys for objects (``$['a b']``, ``$["0"]``) with ``\\``
  and quote escapes, for keys that are not bare identifiers;
* integer indexes for lists, negative allowed (``$.items[0]``,
  ``$.items[-1]``);
* ``start:end`` slices with either side optional and no step
  (``$.items[1:3]``, ``$.items[2:]``, ``$.items[:2]``);
* wildcards — ``[*]`` or ``.*`` — that iterate the elements of a list
  or the values of an object;
* simple filters of the form ``[?(@.price < 10)]`` comparing the
  element itself (``@``) or a sub-path (``@.price``,
  ``@['unit price']``, ``@.tags[0]``) against a literal — a number, a
  quoted string, ``true``, ``false`` or ``null`` — using ``==``,
  ``!=``, ``<``, ``<=``, ``>`` or ``>=``.

Filter semantics are strictly typed and deterministic: equality only
holds between values of the same JSON kind (numbers compare numerically
across int/float, booleans only match booleans, strings only strings,
``null`` only ``null``); ordering comparisons apply to numbers only;
and a filter sub-path that is missing or type-mismatched simply
excludes the element instead of raising. A path that selects nothing is
a normal empty result (``found: false``), not an error.

Input validation is strict and happens before any work: malformed
parameters (unknown mode, missing / empty / over-long path, wrong
``data`` type, JSON text over ``max_input_chars``) raise a
``ValueError``, mirroring the other common tools. Errors that depend on
the *content being processed* — JSON text that fails to parse
(including ``NaN`` / ``Infinity`` constants and nesting too deep for
the interpreter stack) and path syntax errors — are returned as a
structured ``error`` payload (``{"type": "invalid_json", ...}`` /
``{"type": "invalid_path", ...}``) so an agent can react without
catching exceptions.

Cost is bounded by caps, not by timeouts: ``max_input_chars`` (default
100,000) bounds the document, which in turn bounds every intermediate
result of the iterative (non-recursive) evaluator — each traversal
state is a concrete path from the root, so states can never outnumber
document nodes — and ``max_matches`` (default 1000) caps the returned
match list with a ``truncated`` flag. The tool never mutates and never
re-serializes the queried document.
"""

import json
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Bare (unquoted) object keys accepted in dot notation.
_BARE_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")
_INT_RE = re.compile(r"-?\d+\Z")
_SLICE_RE = re.compile(r"(-?\d+)?:(-?\d+)?\Z")
_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?\Z")

# Token kinds produced by the path parser.
_ROOT = "root"
_KEY = "key"
_INDEX = "index"
_SLICE = "slice"
_WILDCARD = "wildcard"
_FILTER = "filter"


def _reject_constant(name: str) -> None:
    """Reject NaN / Infinity constants while parsing JSON text."""
    raise ValueError(f"{name} is not a valid JSON constant")


class _PathSyntaxError(ValueError):
    """Internal marker for path syntax problems (never escapes the tool)."""


class _PathParser:
    """Strict, iterative parser for the supported JSON-path subset.

    Produces a flat token list; each token is a tuple whose first item
    is one of ``root`` / ``key`` / ``index`` / ``slice`` / ``wildcard``
    / ``filter``. Raises :class:`_PathSyntaxError` on any syntax
    problem.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._pos = 0
        self._len = len(path)

    # -- helpers ------------------------------------------------------- #

    def _fail(self, message: str) -> None:
        raise _PathSyntaxError(
            f"{message} (at position {self._pos} in {self._path[:64]!r})"
        )

    # -- grammar ------------------------------------------------------- #

    def parse(self) -> List[Tuple[Any, ...]]:
        """Parse the whole path into tokens."""
        tokens: List[Tuple[Any, ...]] = []
        if self._path[0] == "$":
            tokens.append((_ROOT,))
            self._pos = 1
        while self._pos < self._len:
            char = self._path[self._pos]
            if char == ".":
                self._pos += 1
                if self._pos < self._len and self._path[self._pos] == "*":
                    self._pos += 1
                    tokens.append((_WILDCARD,))
                else:
                    tokens.append((_KEY, self._bare_key()))
            elif char == "[":
                tokens.append(self._bracket())
            elif not tokens:
                # A leading bare key without a dot is accepted.
                tokens.append((_KEY, self._bare_key()))
            else:
                self._fail(
                    f"expected '.' or '[' after a path segment (got {char!r})"
                )
        return tokens

    def _bare_key(self) -> str:
        match = _BARE_KEY_RE.match(self._path, self._pos)
        if match is None:
            got = (
                self._path[self._pos]
                if self._pos < self._len
                else "end of path"
            )
            self._fail(
                f"expected a bare key ([A-Za-z_][A-Za-z0-9_-]*) after '.' "
                f"(got {got!r}); quote unusual keys instead, e.g. ['0'] "
                "or ['a b']"
            )
        self._pos = match.end()
        return match.group(0)

    def _bracket(self) -> Tuple[Any, ...]:
        """Parse one ``[...]`` segment: filter, wildcard, key, index or slice."""
        if self._path.startswith("[?(", self._pos):
            return self._filter()
        content_end, content = self._scan_bracket_content()
        self._pos = content_end + 1
        stripped = content.strip()
        if not stripped:
            self._fail("empty '[' segment")
        if stripped == "*":
            return (_WILDCARD,)
        if stripped[0] in ("'", '"'):
            return (_KEY, self._quoted_key(stripped))
        if _INT_RE.match(stripped):
            return (_INDEX, int(stripped))
        slice_match = _SLICE_RE.match(stripped)
        if slice_match is not None:
            raw_start, raw_end = slice_match.group(1), slice_match.group(2)
            start = int(raw_start) if raw_start is not None else None
            end = int(raw_end) if raw_end is not None else None
            return (_SLICE, start, end)
        if ":" in stripped:
            self._fail(
                "unsupported slice — only start:end with either side "
                "optional and no step is supported"
            )
        self._fail(
            "unsupported '[' segment — expected a quoted key, an integer "
            "index, a start:end slice, '*' or a [?( ... )] filter"
        )

    def _scan_bracket_content(self) -> Tuple[int, str]:
        """Scan to the closing ``]``, honouring quoted strings."""
        index = self._pos + 1
        quote: Optional[str] = None
        escaped = False
        while index < self._len:
            char = self._path[index]
            if escaped:
                escaped = False
            elif quote is not None:
                if char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in ("'", '"'):
                quote = char
            elif char == "]":
                return index, self._path[self._pos + 1 : index]
            index += 1
        self._fail("unterminated '[' segment — missing ']'")

    def _filter(self) -> Tuple[Any, ...]:
        """Parse a ``[?( ... )]`` filter segment."""
        open_end = self._pos + 3  # just past "[?("
        index = open_end
        quote: Optional[str] = None
        escaped = False
        while index < self._len:
            char = self._path[index]
            if escaped:
                escaped = False
            elif quote is not None:
                if char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in ("'", '"'):
                quote = char
            elif char == ")" and self._path.startswith(")]", index):
                break
            index += 1
        if index >= self._len:
            self._fail("unterminated filter — missing ')]'")
        expression = self._path[open_end:index]
        self._pos = index + 2
        left_tokens, operator, literal = self._filter_expression(expression)
        return (_FILTER, left_tokens, operator, literal)

    def _filter_expression(
        self, expression: str
    ) -> Tuple[List[Tuple[Any, ...]], str, Tuple[str, Any]]:
        """Parse ``@<sub-path> <op> <literal>`` inside a filter."""
        text = expression.strip()
        if not text:
            self._fail("empty filter expression")
        if text[0] != "@":
            self._fail("filter expression must start with '@'")
        pos = 1
        left_tokens: List[Tuple[Any, ...]] = []
        while pos < len(text) and text[pos] in ".[":
            if text[pos] == ".":
                match = _BARE_KEY_RE.match(text, pos + 1)
                if match is None:
                    self._fail(
                        "expected a bare key after '.' inside the filter "
                        "'@' path"
                    )
                left_tokens.append((_KEY, match.group(0)))
                pos = match.end()
            else:
                close = text.find("]", pos)
                if close == -1:
                    self._fail(
                        "unterminated '[' inside the filter '@' path"
                    )
                inner = text[pos + 1 : close].strip()
                if inner[:1] in ("'", '"'):
                    left_tokens.append((_KEY, self._quoted_key(inner)))
                elif _INT_RE.match(inner):
                    left_tokens.append((_INDEX, int(inner)))
                else:
                    self._fail(
                        "the filter '@' path only supports quoted keys and "
                        "integer indexes"
                    )
                pos = close + 1
        while pos < len(text) and text[pos].isspace():
            pos += 1
        operator: Optional[str] = None
        for candidate in ("==", "!=", "<=", ">=", "<", ">"):
            if text.startswith(candidate, pos):
                operator = candidate
                pos += len(candidate)
                break
        if operator is None:
            self._fail(
                "filter is missing a comparator (one of ==, !=, <, <=, "
                ">, >=)"
            )
        while pos < len(text) and text[pos].isspace():
            pos += 1
        return left_tokens, operator, self._literal(text[pos:])

    def _literal(self, raw: str) -> Tuple[str, Any]:
        """Parse a filter literal: number, quoted string, true, false, null."""
        if raw in ("true", "false"):
            return ("bool", raw == "true")
        if raw == "null":
            return ("null", None)
        if raw[:1] in ("'", '"'):
            return ("string", self._quoted_key(raw))
        if _NUMBER_RE.match(raw):
            if "." in raw:
                return ("number", float(raw))
            return ("number", int(raw))
        self._fail(
            "filter literal must be a number, a quoted string, true, "
            f"false or null (got {raw[:32]!r})"
        )

    @staticmethod
    def _quoted_key(text: str) -> str:
        """Unescape a quoted string including its surrounding quotes."""
        quote = text[0]
        if len(text) < 2 or text[-1] != quote:
            raise _PathSyntaxError(f"unterminated quoted key in {text!r}")
        body = text[1:-1]
        out: List[str] = []
        index = 0
        while index < len(body):
            char = body[index]
            if char == "\\":
                if index + 1 >= len(body):
                    raise _PathSyntaxError(
                        f"dangling escape in quoted key {text!r}"
                    )
                nxt = body[index + 1]
                if nxt not in ("\\", "'", '"'):
                    raise _PathSyntaxError(
                        f"unsupported escape '\\{nxt}' in quoted key {text!r}"
                    )
                out.append(nxt)
                index += 2
            else:
                out.append(char)
                index += 1
        return "".join(out)


def _render_key(parent: str, key: str) -> str:
    """Render an object-key step, quoted when it is not a bare identifier."""
    if _BARE_KEY_RE.fullmatch(key):
        return f"{parent}.{key}"
    escaped = key.replace("\\", "\\\\").replace("'", "\\'")
    return f"{parent}['{escaped}']"


def _is_number(value: Any) -> bool:
    """True for JSON numbers (bool is a JSON boolean, not a number)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _resolve_left(
    element: Any, left_tokens: List[Tuple[Any, ...]]
) -> Tuple[bool, Any]:
    """Resolve a filter's ``@`` sub-path against one element.

    Returns ``(found, value)``; ``found`` is False when any step is
    missing or type-mismatched, which excludes the element from the
    filter result instead of raising.
    """
    current = element
    for token in left_tokens:
        if token[0] == _KEY:
            if not isinstance(current, dict) or token[1] not in current:
                return False, None
            current = current[token[1]]
        else:  # _INDEX
            if not isinstance(current, list):
                return False, None
            index = token[1]
            if not -len(current) <= index < len(current):
                return False, None
            current = current[index]
    return True, current


def _typed_equal(left: Any, literal_kind: str, literal_value: Any) -> bool:
    """Strictly typed JSON equality (numbers, strings, bools, null)."""
    if literal_kind == "number":
        return _is_number(left) and left == literal_value
    if literal_kind == "string":
        return isinstance(left, str) and left == literal_value
    if literal_kind == "bool":
        return isinstance(left, bool) and left == literal_value
    return left is None  # null


def _filter_match(
    element: Any,
    left_tokens: List[Tuple[Any, ...]],
    operator: str,
    literal: Tuple[str, Any],
) -> bool:
    """Apply one filter expression to one candidate element."""
    found, left = _resolve_left(element, left_tokens)
    if not found:
        return False
    literal_kind, literal_value = literal
    if operator == "==":
        return _typed_equal(left, literal_kind, literal_value)
    if operator == "!=":
        return not _typed_equal(left, literal_kind, literal_value)
    # Ordering comparisons are defined for numbers only.
    if literal_kind != "number" or not _is_number(left):
        return False
    if operator == "<":
        return left < literal_value
    if operator == "<=":
        return left <= literal_value
    if operator == ">":
        return left > literal_value
    return left >= literal_value  # ">="


def _apply_tokens(
    tokens: List[Tuple[Any, ...]], data: Any
) -> List[Tuple[str, Any]]:
    """Evaluate tokens against the document, carrying concrete paths.

    Each state is a ``(rendered_path, value)`` pair. Because every
    state corresponds to a distinct concrete path from the document
    root, the number of states can never exceed the number of document
    nodes, which ``max_input_chars`` bounds.
    """
    states: List[Tuple[str, Any]] = [("$", data)]
    for token in tokens:
        kind = token[0]
        if kind == _ROOT:
            continue
        nxt: List[Tuple[str, Any]] = []
        for parent, value in states:
            if kind == _KEY:
                if isinstance(value, dict) and token[1] in value:
                    nxt.append((_render_key(parent, token[1]), value[token[1]]))
            elif kind == _INDEX:
                if isinstance(value, list):
                    index = token[1]
                    if -len(value) <= index < len(value):
                        if index < 0:
                            index += len(value)
                        nxt.append((f"{parent}[{index}]", value[index]))
            elif kind == _SLICE:
                if isinstance(value, list):
                    for index in range(
                        *slice(token[1], token[2]).indices(len(value))
                    ):
                        nxt.append((f"{parent}[{index}]", value[index]))
            elif kind == _WILDCARD:
                if isinstance(value, list):
                    for index, item in enumerate(value):
                        nxt.append((f"{parent}[{index}]", item))
                elif isinstance(value, dict):
                    for key, item in value.items():
                        nxt.append((_render_key(parent, key), item))
            else:  # _FILTER
                if isinstance(value, list):
                    candidates = enumerate(value)
                elif isinstance(value, dict):
                    candidates = ((key, item) for key, item in value.items())
                else:
                    candidates = ()
                for key_or_index, item in candidates:
                    if _filter_match(item, token[1], token[2], token[3]):
                        if isinstance(key_or_index, int):
                            nxt.append(
                                (f"{parent}[{key_or_index}]", item)
                            )
                        else:
                            nxt.append(
                                (_render_key(parent, key_or_index), item)
                            )
        states = nxt
        if not states:
            break
    return states


def _token_summary(token: Tuple[Any, ...]) -> str:
    """Human-readable one-line summary of one parsed token."""
    kind = token[0]
    if kind == _ROOT:
        return "root"
    if kind == _KEY:
        return f"key:{token[1]}"
    if kind == _INDEX:
        return f"index:{token[1]}"
    if kind == _SLICE:
        return f"slice:{token[1]}:{token[2]}"
    if kind == _WILDCARD:
        return "wildcard"
    left = "".join(
        f".{step[1]}" if step[0] == _KEY else f"[{step[1]}]"
        for step in token[1]
    )
    return f"filter:@{left} {token[2]} {json.dumps(token[3][1])}"


class JsonPathTool(Tool):
    """JSON path query tool built purely on the stdlib.

    Attributes:
        max_input_chars (int): Upper bound on the JSON text length
            accepted in ``data``; longer inputs are rejected before any
            work, which also bounds evaluation cost.
        max_matches (int): Upper bound on the number of matches
            returned by ``query`` mode; further matches are dropped and
            ``truncated`` is set to True.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "json_path_tool"
    description: str = (
        "JSON path query tool — pure Python stdlib, no network required. "
        "Query nested JSON documents with a practical JSONPath subset "
        "(mode='query'): dot and quoted bracket keys, integer indexes "
        "(negative allowed), start:end slices, wildcards ([*] or .*) and "
        "simple filters like [?(@.price < 10)] comparing a sub-path to a "
        "number, string, true, false or null with ==, !=, <, <=, >, >=. "
        "Each match carries its concrete path and value. Validate a path "
        "without data (mode='validate'). Invalid JSON text and invalid "
        "paths return structured error payloads instead of raising."
    )

    MODES: ClassVar[tuple] = ("query", "validate")
    MAX_PATH_CHARS: ClassVar[int] = 10_000

    max_input_chars: int = 100_000
    max_matches: int = 1000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        path: Any = None,
        data: Any = None,
    ) -> Dict[str, Any]:
        """Run one JSON path operation.

        Args:
            mode (str): ``query`` or ``validate``.
            path (str): The JSON path, e.g. ``$.store.book[0].title`` or
                ``$.items[?(@.price < 10)]``. A leading ``$`` is
                optional and ``$`` alone selects the whole document.
            data (str | dict | list): The document to query — a JSON
                string or an already-decoded ``dict`` / ``list``.
                Required for ``query`` mode; not used by ``validate``
                mode.

        Returns:
            Dict[str, Any]: For ``query`` mode a dict with ``path``,
                ``found``, ``count``, ``truncated`` and a ``matches``
                list of ``{"path": ..., "value": ...}`` entries, or a
                structured ``error`` payload (``invalid_json`` /
                ``invalid_path``) for content-level failures. For
                ``validate`` mode a dict with ``valid`` and either the
                parsed ``tokens`` or an ``invalid_path`` error payload.

        Raises:
            ValueError: If any parameter is malformed (before any work
                happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_path = self._validate_path(path)
        if mode == "validate":
            return self._run_validate(clean_path)
        clean_data = self._validate_data(data)
        return self._run_query(clean_path, clean_data)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"json_path_tool: {message}")

    @classmethod
    def _validate_path(cls, path: Any) -> str:
        """Validate the ``path`` input (structure only, not syntax)."""
        if path is None or isinstance(path, bool) or not isinstance(path, str):
            cls._invalid(f"path must be a non-empty string (got {path!r})")
        if not path:
            cls._invalid("path must be a non-empty string (got '')")
        if not path.strip():
            cls._invalid("path must contain more than whitespace")
        if len(path) > cls.MAX_PATH_CHARS:
            cls._invalid(
                f"path exceeds the {cls.MAX_PATH_CHARS:,}-character limit "
                f"(got {len(path):,} characters)"
            )
        return path

    def _validate_data(self, data: Any) -> Any:
        """Validate the ``data`` input (JSON text or decoded container)."""
        if (
            data is None
            or isinstance(data, bool)
            or not isinstance(data, (str, dict, list))
        ):
            self._invalid(
                f"data must be a JSON string, dict or list (got {data!r})"
            )
        if isinstance(data, str):
            if not data:
                self._invalid(
                    "data must be a non-empty JSON string, dict or list "
                    "(got '')"
                )
            if len(data) > self.max_input_chars:
                self._invalid(
                    f"data exceeds the {self.max_input_chars:,}-character "
                    f"limit (got {len(data):,} characters)"
                )
        return data

    # ------------------------------------------------------------------ #
    # query mode
    # ------------------------------------------------------------------ #

    def _run_query(self, path: str, data: Any) -> Dict[str, Any]:
        """Parse the document and the path, then evaluate the path."""
        context: Dict[str, Any] = {"mode": "query", "path": path}
        if isinstance(data, str):
            try:
                document = json.loads(data, parse_constant=_reject_constant)
            except (ValueError, RecursionError) as exc:
                return self._error_result(
                    context,
                    error_type="invalid_json",
                    message=(
                        "data is not valid JSON text: expected a JSON "
                        "document without NaN/Infinity constants and with "
                        f"nesting the interpreter can parse ({str(exc)[:120]})"
                    ),
                )
        else:
            document = data
        try:
            tokens = _PathParser(path).parse()
        except _PathSyntaxError as exc:
            return self._error_result(
                context, error_type="invalid_path", message=str(exc)
            )
        states = _apply_tokens(tokens, document)
        truncated = len(states) > self.max_matches
        matches = [
            {"path": state_path, "value": value}
            for state_path, value in states[: self.max_matches]
        ]
        return {
            **context,
            "found": bool(matches),
            "count": len(matches),
            "truncated": truncated,
            "matches": matches,
        }

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(self, path: str) -> Dict[str, Any]:
        """Parse the path alone and report its segments."""
        context: Dict[str, Any] = {"mode": "validate", "path": path}
        try:
            tokens = _PathParser(path).parse()
        except _PathSyntaxError as exc:
            return {
                **context,
                "valid": False,
                "error": {"type": "invalid_path", "message": str(exc)[:500]},
            }
        return {
            **context,
            "valid": True,
            "tokens": [_token_summary(token) for token in tokens],
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
