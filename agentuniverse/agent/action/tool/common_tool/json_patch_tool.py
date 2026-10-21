#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: json_patch_tool.py

"""RFC 6902 JSON *Patch* tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the document-mutation layer on top of JSON: given
a JSON document and an RFC 6902 patch — the array of
``{"op": ..., "path": ..., "value"?: ..., "from"?: ...}`` operation
objects — apply it, generate one from two documents, or check a
patch for well-formedness, with no network access and no
third-party dependencies.

Where a JSON *query* tool reads values out of a document (the
counterpart layers of this collection address path querying and
string escaping), this tool is the write side: the six RFC 6902
operations — ``add`` (array index insertion including the ``-``
append marker and object member upsert), ``remove`` (target must
exist), ``replace`` (target must exist), ``move`` (from must exist,
and a value can never be moved into its own descendant — verified
by a token-sequence cycle check), ``copy`` (deep copy, the source
is never aliased) and ``test`` (equality per JSON semantics:
numbers compare numerically so ``1 == 1.0``, but ``true != 1`` and
``"1" != 1``; object member order is irrelevant, array order is
significant) — all addressing their targets through RFC 6901 JSON
Pointers.

Three modes:

* ``apply`` — a JSON document (text or already-parsed value) plus a
  patch (list of op objects, or a JSON text of such a list) → the
  resulting ``document``, the list of ``applied`` op summaries and
  the list of ``failed`` operations ``{index, op, path, reason}``.
  Lenient by default: operations are applied sequentially, a
  failing operation is recorded and skipped, and the rest of the
  patch still runs against the document state reached so far. With
  ``atomic: true`` the run aborts on the very first failure and the
  original document is returned completely untouched
  (all-or-nothing, mirroring the spec's intent that a patch either
  applies as a whole or not at all).
* ``diff`` — two documents → the patch that transforms ``a`` into
  ``b``: objects key-by-key recursion (sorted keys, deterministic),
  arrays via a longest-common-subsequence alignment on deep
  equality emitting descending removes then ascending inserts. A
  *heuristic*: it is correct (the round-trip property
  ``apply(diff(a, b), a) == b`` holds, which the tests verify over
  hundreds of seeded document pairs) but documented as **not
  guaranteed minimal** — no move detection, no key renames.
* ``validate_patch`` — patch well-formedness without a document:
  op whitelist, per-op required members (``add``/``replace``/
  ``test`` require ``value``; ``move``/``copy`` require ``from``)
  and RFC 6901 pointer syntax for ``path`` and ``from``; every
  violation is collected, not just the first.

JSON-Pointer (RFC 6901) handling is complete: ``~1`` → ``/`` and
``~0`` → ``~`` unescaping in the RFC-mandated order, any other
``~`` escape rejected, the empty pointer addressing the whole
document, array indices as plain digits without leading zeros
(``01`` is not an index — against an object it is a legitimate
member name, the container decides), ``-`` accepted only as the
*final* token of an ``add`` path (an append marker can never be
navigated through), and pointers missing the leading ``/`` —
including the common URI-fragment mistake ``#/foo/bar`` — rejected
with an explicit message. Members of an op object the spec does
not define are ignored, exactly as RFC 6902 §4 requires.

Semantics notes. ``move`` is implemented as literally "a remove on
``from`` followed immediately by an add at ``path`` with the value
just removed" (spec §4.4), so array target indices are evaluated
*after* the removal — and ``move`` with ``from == path`` is
therefore a successful no-op. ``replace``/``remove`` on the empty
pointer are rejected (``add``/``replace``/``test``/``move``/
``copy`` on the root are fine — the result must remain a document,
and deleting the root has no JSON meaning).

Input validation is strict and happens before any computation:
malformed parameters (wrong types, missing required arguments,
oversized inputs — documents and patch texts are capped at
1,000,000 characters, patches at 1,000 operations) raise a
``ValueError``, mirroring the other common tools. Errors that
depend on the *content being processed* — a document text that is
not valid JSON, a patch text that does not decode to a list — are
returned as a structured ``error`` payload so an agent can react
without catching exceptions; per-operation failures (unknown op,
malformed pointer, missing target) flow into the ``failed`` list
instead. The tool is deterministic — output is a pure function of
the input — and the caller's data is never mutated: the document
and every patch value are deep-copied before any operation touches
them (asserted by the tests), so applying a patch can never
corrupt the input document or the patch itself.
"""

import copy
import json
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Array indices are plain ASCII digit runs (no unicode digits, no
# signs, no decimals, no exponents).
_DIGITS = re.compile(r"[0-9]+\Z")

# The six RFC 6902 operations.
_OPS = ("add", "remove", "replace", "move", "copy", "test")

# Input size limits (documents are bounded purely to reject
# pathological inputs early; the limits are far above real payloads).
_MAX_TEXT = 1_000_000
_MAX_OPS = 1_000
# Arrays longer than this on either side fall back from the LCS
# alignment to a single whole-array replace in diff mode.
_MAX_LCS = 512


class _PatchError(Exception):
    """Internal carrier for one failed patch operation / payload."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def _is_number(value: Any) -> bool:
    """Whether the value is a JSON number (bool is NOT a number)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _json_type_name(value: Any) -> str:
    """A human JSON type name for error messages."""
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, (int, float)):
        return "a number"
    if value is None:
        return "null"
    if isinstance(value, str):
        return "a string"
    if isinstance(value, list):
        return "an array"
    if isinstance(value, dict):
        return "an object"
    return type(value).__name__


def _json_equal(a: Any, b: Any) -> bool:
    """JSON-semantics equality (RFC 6902 §4.6 ``test``).

    Literals are equal only to the same literal (``true != 1``,
    ``"1" != 1``, ``null`` only to ``null``); numbers compare
    numerically (``1 == 1.0``); objects are equal with the same
    members regardless of order; arrays are equal element-wise in
    order.
    """
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if _is_number(a) and _is_number(b):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(_json_equal(a[key], b[key]) for key in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(
            _json_equal(x, y) for x, y in zip(a, b)
        )
    return a == b


def _decode_pointer(pointer: Any) -> List[str]:
    """Parse an RFC 6901 pointer into raw reference tokens.

    Returns the token list (``""`` → ``[]`` = the whole document).
    Raises :class:`_PatchError` on syntax violations: a pointer must
    be a string that is empty or starts with ``/`` (rejecting the
    URI-fragment form ``#/...``), and every ``~`` must be followed
    by ``0`` or ``1``.
    """
    if not isinstance(pointer, str):
        raise _PatchError(
            f"a JSON Pointer must be a string (got "
            f"{_json_type_name(pointer)})"
        )
    if pointer.startswith("#"):
        raise _PatchError(
            f"pointer {pointer[:64]!r} must not start with '#' — that is "
            f"the URI-fragment form; strip the '#' and pass '/...'"
        )
    if not pointer:
        return []
    if not pointer.startswith("/"):
        raise _PatchError(
            f"pointer {pointer[:64]!r} must be empty or start with '/'"
        )
    tokens: List[str] = pointer[1:].split("/")
    for index, token in enumerate(tokens):
        position = 0
        while True:
            found = token.find("~", position)
            if found < 0:
                break
            if found + 1 >= len(token) or token[found + 1] not in "01":
                raise _PatchError(
                    f"invalid escape in reference token {index} "
                    f"({token!r}): '~' must be followed by '0' (for '~') "
                    f"or '1' (for '/')"
                )
            position = found + 2
    # RFC 6901 §3: "~1" first, then "~0" (so "~01" decodes to "~1").
    return [t.replace("~1", "/").replace("~0", "~") for t in tokens]


def _pointer_text(tokens: List[str]) -> str:
    """Render tokens back into pointer text (escaping ~ and /)."""
    if not tokens:
        return ""
    return "/" + "/".join(
        t.replace("~", "~0").replace("/", "~1") for t in tokens
    )


def _array_index(token: str, length: int, *, allow_append: bool,
                 allow_end: bool) -> int:
    """Resolve one token as an array index against ``length``.

    ``allow_append`` accepts ``-`` (the RFC 6902 add-append marker,
    valid only as the final token of an add path); ``allow_end``
    accepts ``index == length`` (the insert position of add);
    everything at or beyond the length is out of range.
    """
    if token == "-":
        if allow_append:
            return length
        raise _PatchError(
            "'-' (the append marker) is only valid as the final token "
            "of an 'add' path, not for this operation or position"
        )
    if not _DIGITS.match(token):
        raise _PatchError(
            f"array index {token!r} is not valid — a plain sequence of "
            f"digits 0-9 without a sign, decimal point or leading zeros "
            f"('-' means append for add)"
        )
    if len(token) > 1 and token[0] == "0":
        raise _PatchError(
            f"array index {token!r} must not have leading zeros"
        )
    index = int(token)
    if index > length or (index == length and not allow_end):
        raise _PatchError(
            f"array index {index} is out of range for an array of "
            f"length {length} (valid indices: 0..{length - 1}"
            + (f", {length} to append" if allow_end else "")
            + ")"
        )
    return index


def _navigate(document: Any, tokens: List[str]) -> Tuple[Any, str]:
    """Walk to the parent of the final token of a path.

    Returns ``(parent, final_token)``; the parent is the container
    (dict or list) the final token applies to. Every intermediate
    token must resolve inside the existing document.
    """
    current = document
    for position, token in enumerate(tokens[:-1]):
        walked = _pointer_text(tokens[:position]) or "the document root"
        if isinstance(current, list):
            index = _array_index(token, len(current),
                                 allow_append=False, allow_end=False)
            current = current[index]
        elif isinstance(current, dict):
            if token not in current:
                raise _PatchError(
                    f"object member {token!r} does not exist "
                    f"(at {walked})"
                )
            current = current[token]
        else:
            raise _PatchError(
                f"cannot descend into {_json_type_name(current)} with "
                f"token {token!r} (at {walked}): only arrays and objects "
                f"have members"
            )
    return current, tokens[-1]


def _read_at(document: Any, tokens: List[str]) -> Any:
    """Read the value an existing path points to."""
    if not tokens:
        return document
    parent, final = _navigate(document, tokens)
    if isinstance(parent, list):
        index = _array_index(final, len(parent),
                             allow_append=False, allow_end=False)
        return parent[index]
    if isinstance(parent, dict):
        if final not in parent:
            raise _PatchError(f"object member {final!r} does not exist")
        return parent[final]
    raise _PatchError(
        f"cannot address a member of {_json_type_name(parent)} — only "
        f"arrays and objects have members"
    )


def _do_add(document: Any, tokens: List[str], value: Any) -> Any:
    """Apply one RFC 6902 ``add`` (returns the new document)."""
    if not tokens:
        return copy.deepcopy(value)
    parent, final = _navigate(document, tokens)
    if isinstance(parent, list):
        index = _array_index(final, len(parent),
                             allow_append=True, allow_end=True)
        parent.insert(index, copy.deepcopy(value))
        return document
    if isinstance(parent, dict):
        parent[final] = copy.deepcopy(value)
        return document
    raise _PatchError(
        f"cannot add a member to {_json_type_name(parent)} — only arrays "
        f"and objects have members"
    )


def _do_replace(document: Any, tokens: List[str], value: Any) -> Any:
    """Apply one RFC 6902 ``replace`` (returns the new document)."""
    if not tokens:
        return copy.deepcopy(value)
    _read_at(document, tokens)  # the target location MUST exist
    parent, final = _navigate(document, tokens)
    if isinstance(parent, list):
        index = _array_index(final, len(parent),
                             allow_append=False, allow_end=False)
        parent[index] = copy.deepcopy(value)
    elif isinstance(parent, dict):
        parent[final] = copy.deepcopy(value)
    else:  # pragma: no cover - _read_at already rejected this
        raise _PatchError(
            f"cannot replace a member of {_json_type_name(parent)} — only "
            f"arrays and objects have members"
        )
    return document


def _do_remove(document: Any, tokens: List[str]) -> Tuple[Any, Any]:
    """Apply one RFC 6902 ``remove``.

    Returns ``(new_document, removed_value)``.
    """
    if not tokens:
        raise _PatchError(
            "removing the whole document (the empty path) has no JSON "
            "meaning"
        )
    parent, final = _navigate(document, tokens)
    if isinstance(parent, list):
        index = _array_index(final, len(parent),
                             allow_append=False, allow_end=False)
        return document, parent.pop(index)
    if isinstance(parent, dict):
        if final not in parent:
            raise _PatchError(f"object member {final!r} does not exist")
        return document, parent.pop(final)
    raise _PatchError(
        f"cannot remove a member of {_json_type_name(parent)} — only "
        f"arrays and objects have members"
    )


class JsonPatchTool(Tool):
    """RFC 6902 JSON Patch tool built purely on the stdlib.

    Attributes:
        max_text (int): Upper bound on a document / patch text
            passed as JSON; longer inputs are rejected before any
            work.
        max_ops (int): Upper bound on the number of operations of
            one patch.
        max_lcs (int): Array length up to which the ``diff`` mode
            aligns with longest-common-subsequence; longer arrays
            fall back to a single whole-array replace.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "json_patch_tool"
    description: str = (
        "RFC 6902 JSON Patch tool — pure Python stdlib, no network "
        "required. Apply a JSON Patch (mode='apply') to a document "
        "with add/remove/replace/move/copy/test operations addressed "
        "by RFC 6901 JSON-Pointer paths (~0/~1 escapes, '-' append, "
        "whole-document empty path; lenient or atomic all-or-nothing "
        "application), generate the patch transforming one document "
        "into another (mode='diff', LCS-based and round-trip exact "
        "but not guaranteed minimal), and check a patch's "
        "well-formedness without a document (mode='validate_patch')."
    )

    MODES: ClassVar[tuple] = ("apply", "diff", "validate_patch")

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        document: Any = None,
        document_b: Any = None,
        patch: Any = None,
        atomic: Any = None,
    ) -> Dict[str, Any]:
        """Run one JSON Patch operation.

        Args:
            mode (str): One of ``apply`` / ``diff`` /
                ``validate_patch``.
            document (Any): The JSON document — a JSON text or an
                already-parsed value. Required for ``apply`` (the
                target) and ``diff`` (the source ``a``).
            document_b (Any): The second document — the target
                ``b`` of the ``diff`` mode.
            patch (Any): The JSON Patch — a list of op objects or a
                JSON text of such a list. Required for ``apply``
                and ``validate_patch``.
            atomic (bool): ``apply`` mode only: ``False`` (default)
                applies what is valid and reports the failures;
                ``True`` aborts on the first failure and leaves the
                original document untouched.

        Returns:
            Dict[str, Any]: The operation result — for ``apply``:
            the resulting ``document``, ``applied`` op summaries and
            ``failed`` entries ``{index, op, path, reason}``; for
            ``diff``: the generated ``patch``; for
            ``validate_patch``: ``valid`` plus the collected
            ``errors`` — or a structured ``error`` payload for
            content-level failures (a text that is not valid JSON).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} "
                f"(got {mode!r})"
            )
        if atomic is not None and not isinstance(atomic, bool):
            self._invalid(f"atomic must be a boolean (got {atomic!r})")
        if mode == "apply":
            return self._run_apply(document, patch, bool(atomic))
        if mode == "diff":
            return self._run_diff(document, document_b)
        return self._run_validate_patch(patch)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"json_patch_tool: {message}")

    @classmethod
    def _load_document(cls, value: Any, name: str, mode: str) -> Any:
        """Validate / decode one document parameter.

        A text is decoded (a decode failure raises :class:`_PatchError`
        — the caller turns it into the structured error payload); a
        parsed JSON value is accepted as-is after a type walk.
        """
        if value is None:
            cls._invalid(f"{name} is required for the {mode} mode")
        if isinstance(value, str):
            if len(value) > _MAX_TEXT:
                cls._invalid(
                    f"{name} exceeds the {_MAX_TEXT:,}-character limit "
                    f"(got {len(value):,} characters)"
                )
            if not value.strip():
                cls._invalid(f"{name} must not be an empty text")
            try:
                return json.loads(value)
            except ValueError as exc:
                raise _PatchError(f"{name} is not valid JSON: {exc}") from None
        if isinstance(value, (bool, int, float, dict, list)) or value is None:
            return value
        cls._invalid(
            f"{name} must be a JSON text or a parsed JSON value "
            f"(got {_json_type_name(value)})"
        )

    @classmethod
    def _load_patch(cls, value: Any) -> Any:
        """Validate / decode the ``patch`` parameter.

        Returns the (possibly text-decoded) list. Parameter-level
        problems (missing, wrong container type, oversized) raise
        ``ValueError``; content failures of the text form (not
        valid JSON / does not decode to a list) raise
        :class:`_PatchError` for the structured error payload.
        """
        if value is None:
            cls._invalid("patch is required for this mode")
        decoded_from_text = False
        if isinstance(value, str):
            if len(value) > _MAX_TEXT:
                cls._invalid(
                    f"patch exceeds the {_MAX_TEXT:,}-character limit "
                    f"(got {len(value):,} characters)"
                )
            if not value.strip():
                cls._invalid("patch must not be an empty text")
            try:
                value = json.loads(value)
                decoded_from_text = True
            except ValueError as exc:
                raise _PatchError(
                    f"patch is not valid JSON: {exc}"
                ) from None
        if isinstance(value, (str, bytes)) or not isinstance(
            value, (list, tuple)
        ):
            message = (
                f"patch must decode to a list of operation objects (got "
                f"{_json_type_name(value)})"
                if decoded_from_text
                else f"patch must be a list of operation objects or a "
                     f"JSON text of such a list (got "
                     f"{_json_type_name(value)})"
            )
            if decoded_from_text:
                raise _PatchError(message)
            cls._invalid(message)
        if len(value) > _MAX_OPS:
            cls._invalid(
                f"patch exceeds the {_MAX_OPS:,}-operation limit "
                f"(got {len(value):,} operations)"
            )
        return value

    # ------------------------------------------------------------------ #
    # Per-operation structural validation (shared by apply and
    # validate_patch)
    # ------------------------------------------------------------------ #

    @classmethod
    def _op_structure_error(
        cls, entry: Any
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Structurally validate one patch entry.

        Returns ``(op, path, reason)`` — ``reason`` is ``None`` when
        the entry is well-formed (``op`` / ``path`` stay ``None``
        for malformed entries; extra members are ignored per
        RFC 6902 §4).
        """
        if not isinstance(entry, dict):
            return None, None, (
                f"patch entry must be an object "
                f"(got {_json_type_name(entry)})"
            )
        op = entry.get("op")
        if not isinstance(op, str) or op not in _OPS:
            return op if isinstance(op, str) else None, None, (
                f"'op' must be one of: {', '.join(_OPS)} (got {op!r})"
            )
        path = entry.get("path")
        if not isinstance(path, str):
            return op, None, (
                f"'path' must be a JSON Pointer string (got {path!r})"
            )
        try:
            _decode_pointer(path)
        except _PatchError as exc:
            return op, path, f"'path' {exc.reason}"
        if op in ("add", "replace", "test") and "value" not in entry:
            return op, path, (
                f"a '{op}' operation requires a 'value' member "
                f"(it may be null, but the member must be present)"
            )
        if op in ("move", "copy"):
            if "from" not in entry:
                return op, path, f"a '{op}' operation requires a 'from' member"
            source = entry["from"]
            if not isinstance(source, str):
                return op, path, (
                    f"'from' must be a JSON Pointer string (got {source!r})"
                )
            try:
                _decode_pointer(source)
            except _PatchError as exc:
                return op, path, f"'from' {exc.reason}"
        return op, path, None

    @staticmethod
    def _error_field(op: Optional[str], entry: Any) -> str:
        """The offending member name for a validation error report."""
        if not isinstance(entry, dict):
            return "op"
        raw_op = entry.get("op")
        if not isinstance(raw_op, str) or raw_op not in _OPS:
            return "op"
        if not isinstance(entry.get("path"), str):
            return "path"
        if op in ("add", "replace", "test") and "value" not in entry:
            return "value"
        if op in ("move", "copy"):
            return "from"
        return "path"

    # ------------------------------------------------------------------ #
    # apply mode
    # ------------------------------------------------------------------ #

    def _run_apply(
        self, document: Any, patch: Any, atomic: bool
    ) -> Dict[str, Any]:
        """Apply a patch to a document (lenient or atomic)."""
        try:
            parsed = self._load_document(document, "document", "apply")
        except _PatchError as exc:
            return {"mode": "apply", "error": {"reason": exc.reason}}
        try:
            operations = self._load_patch(patch)
        except _PatchError as exc:
            return {"mode": "apply", "error": {"reason": exc.reason}}

        # Deep-copy isolation: the input document and patch are never
        # touched — every mutation happens on the scratch copy.
        current = copy.deepcopy(parsed)
        applied: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []
        for index, entry in enumerate(operations):
            result = self._apply_one(current, entry)
            if isinstance(result, _PatchError):
                failure: Dict[str, Any] = {
                    "index": index,
                    "op": self._op_name_of(entry),
                    "path": self._path_of(entry),
                    "reason": result.reason,
                }
                if atomic:
                    failure["note"] = (
                        "atomic mode: aborted at the first failing "
                        "operation; the document is unchanged"
                    )
                    failed.append(failure)
                    return {
                        "mode": "apply",
                        "document": copy.deepcopy(parsed),
                        "applied": [],
                        "applied_count": 0,
                        "failed": failed,
                        "failed_count": 1,
                        "atomic": True,
                    }
                failed.append(failure)
                continue
            current, summary = result
            applied.append({
                "index": index,
                "op": summary[0],
                "path": summary[1],
                "summary": summary[2],
            })
        result_payload: Dict[str, Any] = {
            "mode": "apply",
            "document": current,
            "applied": applied,
            "applied_count": len(applied),
            "failed": failed,
            "failed_count": len(failed),
            "atomic": atomic,
        }
        if failed and not atomic:
            result_payload["note"] = (
                "lenient mode: failing operations were skipped and the "
                "remaining patch still ran against the document state "
                "reached so far (pass atomic=true for all-or-nothing)"
            )
        return result_payload

    @staticmethod
    def _op_name_of(entry: Any) -> Optional[str]:
        """Best-effort op name of an entry (for failure reports)."""
        if isinstance(entry, dict) and isinstance(entry.get("op"), str):
            return entry["op"]
        return None

    @staticmethod
    def _path_of(entry: Any) -> Optional[str]:
        """Best-effort path of an entry (for failure reports)."""
        if isinstance(entry, dict) and isinstance(entry.get("path"), str):
            return entry["path"]
        return None

    @classmethod
    def _apply_one(cls, document: Any, entry: Any) -> Any:
        """Apply one operation to ``document``.

        Returns ``(new_document, (op, path, summary))`` on success,
        or a :class:`_PatchError` instance (never raises) on
        failure.
        """
        op, path, reason = cls._op_structure_error(entry)
        if reason is not None:
            return _PatchError(reason)
        tokens = _decode_pointer(path)
        try:
            if op == "add":
                summary = cls._summarize_add(document, tokens, path)
                return _do_add(document, tokens, entry["value"]), (
                    op, path, summary,
                )
            if op == "remove":
                new_document, removed = _do_remove(document, tokens)
                return new_document, (
                    op, path,
                    f"removed {_json_type_name(removed)} at {path!r}",
                )
            if op == "replace":
                return _do_replace(document, tokens, entry["value"]), (
                    op, path,
                    "replaced the whole document"
                    if not tokens
                    else f"replaced the value at {path!r}",
                )
            if op == "move":
                return cls._apply_move(document, entry, path, tokens)
            if op == "copy":
                source = _decode_pointer(entry["from"])
                value = copy.deepcopy(_read_at(document, source))
                return _do_add(document, tokens, value), (
                    op, path,
                    f"copied the value at {entry['from']!r} to {path!r}",
                )
            # test
            actual = _read_at(document, tokens)
            if _json_equal(actual, entry["value"]):
                return document, (op, path, "test passed (values are equal)")
            return _PatchError(
                f"test failed: the value at {path!r} is not equal to the "
                f"expected value (got "
                f"{json.dumps(actual, ensure_ascii=False, default=str)[:120]}"
                f")"
            )
        except _PatchError as exc:
            return exc

    @classmethod
    def _apply_move(
        cls, document: Any, entry: Dict[str, Any], path: str,
        tokens: List[str]
    ) -> Any:
        """Apply one RFC 6902 ``move``.

        Functionally identical to a remove on ``from`` followed
        immediately by an add at ``path`` with the value just
        removed (spec §4.4) — so array target indices are evaluated
        after the removal, and ``from == path`` is a no-op.
        """
        source = _decode_pointer(entry["from"])
        if source == tokens:
            return document, (
                "move", path,
                "no-op: 'from' equals 'path' (the value is removed and "
                "immediately re-added)",
            )
        if len(source) < len(tokens) and tokens[: len(source)] == source:
            return _PatchError(
                f"cannot move {entry['from']!r} into its own descendant "
                f"{path!r}: the 'from' location must not be a proper "
                f"prefix of the 'path' location"
            )
        try:
            new_document, moved = _do_remove(document, source)
            return _do_add(new_document, tokens, moved), (
                "move", path,
                f"moved the value at {entry['from']!r} to {path!r}",
            )
        except _PatchError as exc:
            return exc

    @classmethod
    def _summarize_add(
        cls, document: Any, tokens: List[str], path: str
    ) -> str:
        """Human summary of one add (evaluated before the mutation)."""
        if not tokens:
            return "replaced the whole document"
        try:
            parent, final = _navigate(document, tokens)
        except _PatchError:  # pragma: no cover - add already validated
            return f"added a value at {path!r}"
        if isinstance(parent, list):
            if final == "-":
                return f"appended an element to the array (length becomes {len(parent) + 1})"
            return (
                f"inserted an element at index {final} of the array "
                f"(length becomes {len(parent) + 1})"
            )
        return f"set the object member {final!r}"

    # ------------------------------------------------------------------ #
    # diff mode
    # ------------------------------------------------------------------ #

    def _run_diff(self, document: Any, document_b: Any) -> Dict[str, Any]:
        """Generate the patch transforming a into b."""
        try:
            source = self._load_document(document, "document", "diff")
        except _PatchError as exc:
            return {"mode": "diff", "error": {"reason": exc.reason}}
        try:
            target = self._load_document(document_b, "document_b", "diff")
        except _PatchError as exc:
            return {"mode": "diff", "error": {"reason": exc.reason}}
        operations: List[Dict[str, Any]] = []
        self._diff(source, target, [], operations)
        return {
            "mode": "diff",
            "equal": not operations,
            "patch": operations,
            "op_count": len(operations),
            "note": (
                "heuristic diff: objects key-by-key (sorted, "
                "deterministic), arrays via longest-common-subsequence "
                "on deep equality — the round-trip property "
                "apply(diff(a, b), a) == b holds exactly, but the patch "
                "is not guaranteed minimal (no move or rename detection)"
            ),
        }

    @classmethod
    def _diff(
        cls, a: Any, b: Any, tokens: List[str], out: List[Dict[str, Any]]
    ) -> None:
        """Emit the ops transforming ``a`` into ``b`` at ``tokens``."""
        if _json_equal(a, b):
            return
        if isinstance(a, dict) and isinstance(b, dict):
            for key in sorted(a.keys()):
                if key not in b:
                    out.append({
                        "op": "remove",
                        "path": _pointer_text(tokens + [key]),
                    })
            for key in sorted(b.keys()):
                if key not in a:
                    out.append({
                        "op": "add",
                        "path": _pointer_text(tokens + [key]),
                        "value": copy.deepcopy(b[key]),
                    })
                else:
                    cls._diff(a[key], b[key], tokens + [key], out)
            return
        if (
            isinstance(a, list)
            and isinstance(b, list)
            and len(a) <= _MAX_LCS
            and len(b) <= _MAX_LCS
        ):
            cls._diff_arrays(a, b, tokens, out)
            return
        out.append({
            "op": "replace",
            "path": _pointer_text(tokens),
            "value": copy.deepcopy(b),
        })

    @classmethod
    def _diff_arrays(
        cls, a: List[Any], b: List[Any], tokens: List[str],
        out: List[Dict[str, Any]]
    ) -> None:
        """LCS-align two arrays and emit the gap operations.

        Between two matched elements, the unmatched ``a`` elements
        are removed in descending index order (keeping earlier
        positions stable) and the unmatched ``b`` elements inserted
        at their target positions in ascending order — so the
        emitted patch always round-trips.
        """
        matches = cls._lcs_pairs(a, b)
        prev_i = -1
        prev_j = -1
        for i, j in matches + [(len(a), len(b))]:
            for k in range(i - 1, prev_i, -1):
                out.append({
                    "op": "remove",
                    "path": _pointer_text(
                        tokens + [str(prev_j + (k - prev_i))]
                    ),
                })
            for offset, jdx in enumerate(range(prev_j + 1, j)):
                out.append({
                    "op": "add",
                    "path": _pointer_text(tokens + [str(prev_j + 1 + offset)]),
                    "value": copy.deepcopy(b[jdx]),
                })
            prev_i, prev_j = i, j

    @staticmethod
    def _lcs_pairs(a: List[Any], b: List[Any]) -> List[Tuple[int, int]]:
        """The longest-common-subsequence match pairs of two arrays.

        Elements match by deep equality; the walk breaks DP ties
        deterministically (preferring to consume an ``a`` element),
        so the same inputs always produce the same alignment.
        """
        m, n = len(a), len(b)
        table = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m - 1, -1, -1):
            row = table[i]
            below = table[i + 1]
            for j in range(n - 1, -1, -1):
                if _json_equal(a[i], b[j]):
                    row[j] = below[j + 1] + 1
                else:
                    row[j] = max(below[j], row[j + 1])
        pairs: List[Tuple[int, int]] = []
        i = j = 0
        while i < m and j < n:
            if _json_equal(a[i], b[j]):
                pairs.append((i, j))
                i += 1
                j += 1
            elif table[i + 1][j] >= table[i][j + 1]:
                i += 1
            else:
                j += 1
        return pairs

    # ------------------------------------------------------------------ #
    # validate_patch mode
    # ------------------------------------------------------------------ #

    def _run_validate_patch(self, patch: Any) -> Dict[str, Any]:
        """Check a patch for well-formedness (no document needed)."""
        try:
            operations = self._load_patch(patch)
        except _PatchError as exc:
            return {
                "mode": "validate_patch", "error": {"reason": exc.reason},
            }
        errors: List[Dict[str, Any]] = []
        ops: List[Dict[str, Any]] = []
        for index, entry in enumerate(operations):
            op, path, reason = self._op_structure_error(entry)
            ops.append({"index": index, "op": op, "path": path})
            if reason is not None:
                errors.append({
                    "index": index,
                    "field": self._error_field(op, entry),
                    "reason": reason,
                })
        return {
            "mode": "validate_patch",
            "valid": not errors,
            "op_count": len(operations),
            "ops": ops,
            "errors": errors,
        }
