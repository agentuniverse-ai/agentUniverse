#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: toml_tool.py

"""Read-only TOML inspection tool built on the stdlib ``tomllib`` module.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency TOML reader agents can
call when reasoning about configuration files. Together with
``JsonYamlTool`` (#3579) and ``IniConfigTool`` (#3725) it completes the
configuration-format trio for the config formats agents meet in the
wild — JSON / YAML, INI and now TOML.

``tomllib`` is the TOML 1.0 parser shipped with Python 3.11+, so the
tool requires nothing beyond the standard library. It is **read-only by
design**: parsing is a solved, dependency-free problem, while *writing*
TOML round-trip-safe needs the third-party ``tomli-w`` package, which is
not a core dependency of agentUniverse — so no ``set`` / ``serialize``
mode is offered rather than shipping a lossy home-grown serializer.

Four modes are supported:

* ``parse`` — parse TOML text into a nested, JSON-safe dict. Values that
  have no native JSON representation are converted with documented
  rules: ``datetime`` / ``date`` / ``time`` objects (offset datetimes,
  local datetimes, local dates, local times — all legal TOML value
  types) are ISO 8601-stringified via ``isoformat()`` (e.g.
  ``1979-05-27T07:32:00+00:00``), and non-finite floats (TOML ``inf`` /
  ``nan``) become the strings ``"inf"`` / ``"-inf"`` / ``"nan"`` so the
  result can always be embedded in strict JSON.
* ``validate`` — attempt a parse and report success (root-level key
  count plus the list of every table path, arrays of tables included as
  ``name[i]`` entries) or failure with the parse error message and the
  line / column position extracted from the ``tomllib.TOMLDecodeError``
  message (``None`` / ``None`` when tomllib reports the end of the
  document instead of a position).
* ``get`` — resolve a dotted path like ``server.auth.user`` against the
  parsed document and return the value plus its TOML type name. Each
  segment is key-aware: bare keys (``[0-9A-Za-z_-]+``), double-quoted
  keys with ``\\"`` / ``\\\\`` escapes for keys containing dots or
  special characters (``a."b.c"``), single-quoted literal keys
  (``a.'b.c'``) and ``[N]`` array-index segments (``items[0].name``).
  Path syntax problems are reported with the 0-based position of the
  offending character.
* ``paths`` — list every leaf path in the document in document order
  with its TOML type name (``integer`` / ``float`` / ``boolean`` /
  ``string`` / ``datetime`` / ``date`` / ``time``; empty arrays and
  empty tables are listed as leaves of type ``array`` / ``table``). Keys
  that are not bare are rendered quoted. The listing is capped at 500
  leaves; when truncated the total leaf count is still reported.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text — except for ``validate``,
where the empty document is valid TOML with zero keys — oversized text
above the 1 MiB cap, missing / empty / oversized or syntactically
invalid paths) raise a ``ValueError``, mirroring the other common tools.
Errors that depend on the *content being processed* — invalid TOML in
``parse`` / ``get`` / ``paths``, and a path that cannot be resolved in
``get`` (missing key, index out of range, or a segment that tries to
descend into a scalar) — are returned as a structured ``error`` payload
so an agent can react without catching exceptions.
"""

import datetime
import math
import re
import tomllib
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# tomllib embeds the error position in the message as "(at line 3, column 5)"
# — the exception object itself carries no lineno / col attributes.
_TOML_POSITION = re.compile(r"\(at line (\d+), column (\d+)\)")
# Keys that match this pattern are rendered unquoted in path listings.
_BARE_KEY = re.compile(r"\A[0-9A-Za-z_-]+\Z")
_BARE_KEY_CHARS = frozenset(
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-"
)
# Escapes accepted inside double-quoted path segments.
_KEY_ESCAPES = {'"': '"', "\\": "\\", "n": "\n", "t": "\t", "r": "\r"}


class TomlTool(Tool):
    """Read-only TOML inspection tool built on the stdlib ``tomllib``.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length
            (1 MiB); longer inputs are rejected before any work.
        max_paths (int): Upper bound on the number of leaf paths the
            ``paths`` mode returns; the total is still reported when the
            listing is truncated.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "toml_tool"
    description: str = (
        "Read-only TOML inspection tool — pure Python stdlib (tomllib, "
        "Python 3.11+), no network required. Parse TOML text into a "
        "nested JSON-safe dict with datetime/date/time values "
        "ISO-stringified (mode='parse'), check validity with root key "
        "count, table list and error line/column (mode='validate'), "
        "resolve a dotted path with quoted-key and array-index segments "
        "(mode='get'), or list every leaf path with its type, capped at "
        "500 entries (mode='paths'). Read-only by design: writing TOML "
        "round-trip-safe needs the non-core tomli-w package."
    )

    MODES: ClassVar[tuple] = ("parse", "validate", "get", "paths")

    max_text_chars: int = 1_048_576
    max_paths: int = 500

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self, mode: Any, text: Any = None, path: Any = None
    ) -> dict[str, Any]:
        """Run one TOML inspection operation.

        Args:
            mode (str): One of ``parse`` / ``validate`` / ``get`` /
                ``paths``.
            text (str): The TOML document to inspect. Required and
                non-empty for ``parse`` / ``get`` / ``paths``; the
                ``validate`` mode also accepts the empty string (a valid
                TOML document with zero keys).
            path (str): ``get`` mode only — the dotted path to resolve,
                e.g. ``server.auth.user``, ``a."b.c"`` (double-quoted
                key with escapes), ``a.'b.c'`` (literal single-quoted
                key) or ``items[0].name`` (array index). Ignored by the
                other modes.

        Returns:
            Dict[str, Any]: The operation result plus the call context,
                or a structured ``error`` payload for content-level
                failures (invalid TOML; unresolvable path in ``get``
                mode).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        # validate's whole job is checking validity — the empty document
        # is valid TOML with zero keys, so it accepts the empty string.
        clean_text = self._validate_text(text, allow_empty=(mode == "validate"))
        if mode == "get":
            segments = self._validate_path(path)
            data = self._parse_or_error(clean_text)
            if "error" in data:
                return {"mode": "get", "path": path, **data}
            return self._run_get(path, data["data"], segments)
        if mode == "parse":
            data = self._parse_or_error(clean_text)
            if "error" in data:
                return {"mode": "parse", **data}
            return {"mode": "parse", "data": _to_json_safe(data["data"])}
        if mode == "validate":
            return {"mode": "validate", **self._run_validate(clean_text)}
        data = self._parse_or_error(clean_text)
        if "error" in data:
            return {"mode": "paths", **data}
        return self._run_paths(data["data"])

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"toml_tool: {message}")

    def _validate_text(self, text: Any, allow_empty: bool = False) -> str:
        """Validate the ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a string containing TOML (got {text!r})")
        if not text and not allow_empty:
            self._invalid("text must be a non-empty string (got '')")
        if len(text) > self.max_text_chars:
            self._invalid(
                f"text exceeds the {self.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    def _validate_path(self, path: Any) -> list[tuple[str, Any]]:
        """Validate the ``path`` input and parse it into segments.

        Returns the list of ``("key", str)`` / ``("index", int)``
        segments; syntax errors are reported with the 0-based position
        of the offending character.
        """
        if path is None or isinstance(path, bool) or not isinstance(path, str):
            self._invalid(
                f"path must be a non-empty dotted path string (got {path!r})"
            )
        if not path:
            self._invalid("path must be a non-empty dotted path string (got '')")
        if len(path) > 2000:
            self._invalid(
                f"path exceeds the 2,000-character limit (got {len(path):,} "
                "characters)"
            )
        return _parse_path(path)

    # ------------------------------------------------------------------ #
    # Parsing shared by all modes
    # ------------------------------------------------------------------ #

    def _parse_or_error(self, text: str) -> dict[str, Any]:
        """Parse TOML text, returning ``{"data": ...}`` or ``{"error": ...}``."""
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            message = str(exc)
            line, col = _extract_position(message)
            return {
                "error": {
                    "type": "invalid_toml",
                    "message": message,
                    "line": line,
                    "col": col,
                }
            }
        return {"data": data}

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(self, text: str) -> dict[str, Any]:
        """Parse and report ok (key / table inventory) or the exact error."""
        parsed = self._parse_or_error(text)
        if "error" in parsed:
            return {"valid": False, "error": parsed["error"]}
        data = parsed["data"]
        return {
            "valid": True,
            "root_key_count": len(data),
            "tables": list(_iter_tables(data, [])),
        }

    # ------------------------------------------------------------------ #
    # get mode
    # ------------------------------------------------------------------ #

    def _run_get(
        self,
        path: str,
        data: dict[str, Any],
        segments: list[tuple[str, Any]],
    ) -> dict[str, Any]:
        """Resolve pre-parsed path segments against the parsed document."""
        current: Any = data
        for position, (kind, ref) in enumerate(segments):
            rendered = _render_segment(kind, ref)
            if kind == "key":
                if not isinstance(current, dict):
                    return self._error_result(
                        path,
                        error_type="path_type_mismatch",
                        message=(
                            f"segment {position + 1} ({rendered}) addresses a "
                            f"key, but the value at that point is of type "
                            f"{_toml_type(current)}, not a table"
                        ),
                    )
                if ref not in current:
                    return self._error_result(
                        path,
                        error_type="path_not_found",
                        message=(
                            f"key {rendered} (segment {position + 1}) not "
                            "found in the document"
                        ),
                    )
                current = current[ref]
            else:
                if not isinstance(current, list):
                    return self._error_result(
                        path,
                        error_type="path_type_mismatch",
                        message=(
                            f"segment {position + 1} ({rendered}) addresses "
                            f"an array element, but the value at that point "
                            f"is of type {_toml_type(current)}, not an array"
                        ),
                    )
                if ref >= len(current):
                    return self._error_result(
                        path,
                        error_type="path_not_found",
                        message=(
                            f"index {ref} (segment {position + 1}) is out of "
                            f"range for an array of {len(current)} element(s)"
                        ),
                    )
                current = current[ref]
        return {
            "mode": "get",
            "path": path,
            "value": _to_json_safe(current),
            "type": _toml_type(current),
        }

    # ------------------------------------------------------------------ #
    # paths mode
    # ------------------------------------------------------------------ #

    def _run_paths(self, data: dict[str, Any]) -> dict[str, Any]:
        """List leaf paths with types, capped, in document order."""
        leaves = list(_iter_leaves(data, []))
        listed = leaves[: self.max_paths]
        return {
            "mode": "paths",
            "count": len(listed),
            "total": len(leaves),
            "truncated": len(leaves) > self.max_paths,
            "limit": self.max_paths,
            "paths": [{"path": p, "type": t} for p, t in listed],
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        path: str, error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload for the get mode."""
        return {
            "mode": "get",
            "path": path,
            "error": {"type": error_type, "message": str(message)[:500]},
        }


# ---------------------------------------------------------------------- #
# Module-level helpers (pure functions, no tool state)
# ---------------------------------------------------------------------- #


def _extract_position(message: str) -> tuple[Any, Any]:
    """Extract ``(line, col)`` from a tomllib error message.

    tomllib embeds the position as ``(at line 3, column 7)`` or reports
    ``(at end of document)`` — the latter (and any unexpected format)
    maps to ``(None, None)``.
    """
    match = _TOML_POSITION.search(message)
    if match is None:
        return None, None
    return int(match.group(1)), int(match.group(2))


def _toml_type(value: Any) -> str:
    """Map a parsed TOML value to its TOML 1.0 type name."""
    # bool must be tested before int — bool is an int subclass.
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    # datetime.datetime is a subclass of datetime.date — test it first.
    if isinstance(value, datetime.datetime):
        return "datetime"
    if isinstance(value, datetime.date):
        return "date"
    if isinstance(value, datetime.time):
        return "time"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "table"
    return "unknown"


def _to_json_safe(value: Any) -> Any:
    """Convert a parsed TOML value to strict-JSON-safe data.

    datetime / date / time values are ISO 8601-stringified and
    non-finite floats become the strings ``"inf"`` / ``"-inf"`` /
    ``"nan"`` (the TOML type name in ``get`` / ``paths`` results still
    reports ``float`` — the stringification is a transport detail, same
    as for datetimes).
    """
    if isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, list):
        return [_to_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_json_safe(item) for key, item in value.items()}
    return str(value)


def _render_key(key: str) -> str:
    """Render one key segment, quoted when it is not a bare TOML key."""
    if _BARE_KEY.match(key):
        return key
    escaped = key.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _render_segment(kind: str, ref: Any) -> str:
    """Render one parsed path segment for error messages / listings."""
    return _render_key(ref) if kind == "key" else f"[{ref}]"


def _render_path(parts: list[str]) -> str:
    """Join rendered segments: keys with ``.``, indices attached."""
    out: list[str] = []
    for index, part in enumerate(parts):
        if part.startswith("[") or index == 0:
            out.append(part)
        else:
            out.append(f".{part}")
    return "".join(out)


def _iter_tables(value: Any, prefix: list[str]):
    """Yield the dotted path of every table (dict node), pre-order.

    The root table itself is not listed. Arrays of tables contribute
    one ``name[i]`` entry per element; inline tables are included.
    """
    if isinstance(value, dict):
        if prefix:
            yield _render_path(prefix)
        for key, item in value.items():
            yield from _iter_tables(item, prefix + [_render_key(key)])
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_tables(item, prefix + [f"[{index}]"])


def _iter_leaves(value: Any, prefix: list[str]):
    """Yield ``(dotted_path, toml_type)`` for every leaf, document order.

    A leaf is any scalar value, plus empty arrays / empty tables (a
    container with no elements has nothing to descend into).
    """
    if isinstance(value, dict):
        if not value:
            yield _render_path(prefix), "table"
            return
        for key, item in value.items():
            yield from _iter_leaves(item, prefix + [_render_key(key)])
    elif isinstance(value, list):
        if not value:
            yield _render_path(prefix), "array"
            return
        for index, item in enumerate(value):
            yield from _iter_leaves(item, prefix + [f"[{index}]"])
    else:
        yield _render_path(prefix), _toml_type(value)


def _path_error(path: str, pos: int, message: str) -> None:
    """Raise the standard path-syntax error (0-based ``pos``)."""
    raise ValueError(
        f"toml_tool: invalid path {path!r} at position {pos}: {message}"
    )


def _read_key(path: str, pos: int) -> tuple[str, int]:
    """Read one bare / double-quoted / single-quoted key at ``pos``."""
    if pos >= len(path):
        _path_error(path, pos, "expected a key")
    char = path[pos]
    if char == '"':
        return _read_quoted_key(path, pos, '"')
    if char == "'":
        return _read_quoted_key(path, pos, "'")
    end = pos
    while end < len(path) and path[end] in _BARE_KEY_CHARS:
        end += 1
    if end == pos:
        _path_error(
            path,
            pos,
            "expected a bare key ([0-9A-Za-z_-]+), a double-quoted key or "
            f"a single-quoted key (got {char!r})",
        )
    return path[pos:end], end


def _read_quoted_key(path: str, pos: int, quote: str) -> tuple[str, int]:
    """Read a quoted key starting at the opening ``quote`` at ``pos``.

    Double-quoted keys support the escapes ``\\"`` ``\\\\`` ``\\n``
    ``\\t`` ``\\r``; single-quoted keys are literal (no escapes).
    """
    out: list[str] = []
    end = pos + 1
    while end < len(path):
        char = path[end]
        if quote == '"' and char == "\\":
            if end + 1 >= len(path):
                _path_error(path, end, "dangling escape '\\' at the end of the path")
            escape = path[end + 1]
            if escape not in _KEY_ESCAPES:
                _path_error(
                    path,
                    end,
                    f"unsupported escape '\\{escape}' in a double-quoted key "
                    "(supported: \\\" \\\\ \\n \\t \\r)",
                )
            out.append(_KEY_ESCAPES[escape])
            end += 2
            continue
        if char == quote:
            if end == pos + 1:
                _path_error(path, pos, "empty quoted key")
            return "".join(out), end + 1
        out.append(char)
        end += 1
    _path_error(path, pos, f"unterminated {quote}-quoted key")


def _read_index(path: str, pos: int) -> tuple[int, int]:
    """Read an ``[N]`` array-index segment starting at ``[`` at ``pos``."""
    length = len(path)
    start = pos + 1
    end = start
    while end < length and path[end] in "0123456789":
        end += 1
    digits = path[start:end]
    if not digits:
        _path_error(
            path,
            start,
            "expected a non-negative integer array index inside '[...]'",
        )
    if len(digits) > 1 and digits.startswith("0"):
        _path_error(path, start, "array index must not have leading zeros")
    if end >= length or path[end] != "]":
        _path_error(path, min(end, length - 1), "expected ']' to close the array index")
    return int(digits), end + 1


def _parse_path(path: str) -> list[tuple[str, Any]]:
    """Parse a dotted path into ``("key", str)`` / ``("index", int)``.

    Grammar (whitespace is not allowed around separators)::

        path    := key (('.' key) | index)*
        key     := bare | '"' ... '"' | "'" ... "'"
        index   := '[' digits ']'

    Syntax errors raise ``ValueError`` with the 0-based position of the
    offending character, before any document parsing happens.
    """
    segments: list[tuple[str, Any]] = []
    key, pos = _read_key(path, 0)
    segments.append(("key", key))
    while pos < len(path):
        char = path[pos]
        if char == ".":
            dot = pos
            pos += 1
            if pos >= len(path):
                _path_error(path, dot, "dangling '.' — a key must follow the separator")
            key, pos = _read_key(path, pos)
            segments.append(("key", key))
        elif char == "[":
            index, pos = _read_index(path, pos)
            segments.append(("index", index))
        else:
            _path_error(
                path, pos, f"unexpected character {char!r} — expected '.' or '['"
            )
    return segments
