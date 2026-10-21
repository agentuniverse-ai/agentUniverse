#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: url_query_tool.py

"""URL query-parameter editing tool on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency editor for the
query string of a URL. Where ``URLParserTool`` inspects and
normalizes whole URLs, this tool MUTATES the query: parameters are
added / updated / deleted / renamed, the whole query is cleared or
stably sorted, and boolean flags are toggled — everything else of
the URL (scheme, authority, path, fragment) is passed through
byte-for-byte. Six modes are supported:

* ``set`` — add-or-update parameters from a ``{key: value}`` dict.
  Values are coerced with a documented rule (``bool`` first, since
  ``bool`` is an ``int`` subclass: ``True`` → ``"true"`` /
  ``False`` → ``"false"``; ``int`` / ``float`` via ``str()``;
  ``str`` verbatim — never re-decoded). Updating an existing key
  rewrites its FIRST occurrence in place; a key that appears
  several times keeps its later repeats untouched (parameters are
  never silently collapsed); unknown keys are appended in dict
  order.
* ``delete`` — drop every occurrence of the given keys and report
  which keys were missing.
* ``rename`` — rename keys in place (order kept) against the
  ORIGINAL key set simultaneously (``a→b`` plus ``b→c`` does not
  cascade); renaming onto an existing key creates additional
  occurrences rather than merging them.
* ``clear`` — remove the entire query, dropping a dangling ``?``;
  the fragment is preserved untouched.
* ``sort`` — stable-sort the parameters by key — the ordering
  convention used to prepare OAuth signature base strings (this
  tool does not sign or verify anything itself).
* ``toggle_bool`` — flip ``&k=true`` ↔ ``&k=false``: an absent key
  is added as ``k=true`` (absent reads as false), values are
  matched case-insensitively, only the first occurrence of a
  repeated key is flipped, and any other value is rejected.

Encoding is round-trip safe: existing parameters are decoded with
``urllib.parse`` semantics (``unquote_plus`` per pair, ``&`` the
only separator, blank values and bare keys kept) and, with the
default ``encode=True``, re-encoded through ``quote_plus`` with
``safe=''`` — spaces become ``+`` and ``&`` / ``=`` / non-ASCII
are percent-encoded, so what comes out decodes back to exactly the
same pairs. With ``encode=False`` untouched parameters keep their
original bytes verbatim and new keys / values are inserted raw
(for pre-encoded input); raw segments may not contain ``&`` /
``#`` / whitespace (raw keys additionally not ``=`` / ``?``).

Any string is accepted as url-shaped by default (scheme-relative
references and non-http schemes such as ``ftp`` included); the
``strict=True`` option additionally requires a scheme.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode, missing ``url``,
empty ``params`` / ``keys`` / ``mapping``, a rename mapping a key
to itself, non-boolean ``encode`` / ``strict``) raise a
``ValueError``, mirroring the other common tools. Errors that
depend on the URL or value *content* — whitespace or control
characters inside the URL, URLs ``urllib.parse`` itself rejects, a
missing scheme under ``strict=True``, non-``true``/``false``
toggle values, and forbidden characters in raw segments — are
returned as a structured ``error`` payload so an agent can react
without catching exceptions.
"""

import re
import urllib.parse
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Characters that may never appear unescaped anywhere in a URL.
_FORBIDDEN_URL_CHARS = re.compile(r"[\x00-\x20\x7f]")
# Characters that break raw (encode=False) query segments. Keys are
# stricter than values: '=' / '?' inside a raw key would be reparsed
# as separators, while both round-trip safely inside a raw value.
_RAW_FORBIDDEN_KEY_CHARS = ("&", "#", "=", "?")
_RAW_FORBIDDEN_VALUE_CHARS = ("&", "#")

# Internal pair layout indices.
_K = 0  # decoded key
_V = 1  # decoded value
_RAW = 2  # original raw segment (None once modified)
_OUT_KEY = 3  # raw-insertion key (encode=False, modified pairs only)
_OUT_VAL = 4  # raw-insertion value (encode=False, modified pairs only)


class _QueryProblem(Exception):
    """Internal carrier for content-level query failures.

    Carries the structured ``error_type`` plus a human-readable
    message; the mode runners convert it into a structured
    ``error`` payload.
    """

    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message


class UrlQueryTool(Tool):
    """URL query-parameter editing tool (set / delete / rename /
    clear / sort / toggle_bool).

    Attributes:
        max_url_chars (int): Upper bound on the ``url`` input and on
            every parameter key / value / mapping entry; longer
            inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "url_query_tool"
    description: str = (
        "URL query tool — pure Python stdlib, no network required. "
        "Edit the query string of a URL while everything else stays "
        "byte-identical — add or update parameters from a dict with "
        "bool/int/float/str coercion, first-occurrence updates and "
        "appended new keys (mode='set'); delete every occurrence of "
        "keys with missing-key reporting (mode='delete'); rename "
        "keys in place (mode='rename'); drop the whole query "
        "including a dangling '?' (mode='clear'); stable-sort "
        "parameters by key, the OAuth signature-prep convention "
        "(mode='sort'); and flip &k=true/&k=false flags "
        "(mode='toggle_bool'). Repeated keys are never collapsed, "
        "empty values and bare keys are preserved, and encoding "
        "round-trips through quote_plus(safe='') — or is passed "
        "through raw with encode=False."
    )

    MODES: ClassVar[tuple] = (
        "set",
        "delete",
        "rename",
        "clear",
        "sort",
        "toggle_bool",
    )

    max_url_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        url: Any = None,
        params: Any = None,
        keys: Any = None,
        mapping: Any = None,
        key: Any = None,
        encode: Any = None,
        strict: Any = None,
    ) -> Dict[str, Any]:
        """Run one query-parameter edit.

        Args:
            mode (str): One of ``set`` / ``delete`` / ``rename`` /
                ``clear`` / ``sort`` / ``toggle_bool``.
            url (str): The URL to edit. Everything outside the query
                (scheme, authority, path, fragment) is preserved
                byte-for-byte; only the query string is rewritten.
            params (dict): ``set`` mode — a non-empty ``{key: value}``
                dict; values are coerced (``True``/``False`` →
                ``"true"``/``"false"``, ``int``/``float`` via
                ``str()``, ``str`` verbatim).
            keys (list): ``delete`` mode — a non-empty list of
                parameter names; every occurrence of each is removed.
            mapping (dict): ``rename`` mode — a non-empty
                ``{old: new}`` dict applied against the original key
                set simultaneously; ``old`` must differ from ``new``.
            key (str): ``toggle_bool`` mode — the flag to flip.
            encode (bool): Re-encode parameters with
                ``quote_plus(safe='')`` on rebuild (default). With
                ``False``, untouched parameters keep their original
                bytes and new keys / values are inserted raw.
            strict (bool): Require the URL to carry a scheme
                (default ``False``: any url-shaped string —
                scheme-relative or non-http included — is accepted).

        Returns:
            Dict[str, Any]: The edited ``url``, the final decoded
            ``params`` pair list, per-mode bookkeeping (added /
            updated / deleted / missing / renamed / sorted / toggle
            transition), or a structured ``error`` payload for
            content-level failures.

        Raises:
            ValueError: If any parameter is malformed (before any
            computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                "mode must be one of: "
                f"{', '.join(self.MODES)} (got {mode!r})"
            )
        clean_url = self._validate_url(url)
        do_encode = self._validate_flag("encode", encode, default=True)
        is_strict = self._validate_flag("strict", strict, default=False)

        if mode == "set":
            return self._run_set(clean_url, params, do_encode, is_strict)
        if mode == "delete":
            return self._run_delete(clean_url, keys, do_encode, is_strict)
        if mode == "rename":
            return self._run_rename(
                clean_url, mapping, do_encode, is_strict
            )
        if mode == "clear":
            return self._run_clear(clean_url, is_strict)
        if mode == "sort":
            return self._run_sort(clean_url, do_encode, is_strict)
        return self._run_toggle_bool(clean_url, key, do_encode, is_strict)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"url_query_tool: {message}")

    @classmethod
    def _validate_url(cls, url: Any) -> str:
        """Validate the ``url`` parameter (type / emptiness / length)."""
        if url is None or isinstance(url, bool) or not isinstance(url, str):
            cls._invalid(f"url must be a non-empty string (got {url!r})")
        if not url:
            cls._invalid("url must be a non-empty string (got '')")
        if len(url) > 100_000:
            cls._invalid(
                f"url exceeds the {100_000:,}-character limit "
                f"(got {len(url):,} characters)"
            )
        return url

    @classmethod
    def _validate_flag(cls, name: str, value: Any, default: bool) -> bool:
        """Validate a boolean option such as ``encode`` / ``strict``."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        cls._invalid(
            f"{name} must be a boolean or omitted (got {value!r})"
        )

    @classmethod
    def _validate_key_str(cls, name: str, value: Any) -> str:
        """Validate a single parameter-name string."""
        if isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{name} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{name} must be a non-empty string (got '')")
        if len(value) > 100_000:
            cls._invalid(
                f"{name} exceeds the {100_000:,}-character limit "
                f"(got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _coerce_value(cls, key: str, value: Any) -> str:
        """Coerce a ``set`` value per the documented rule.

        ``bool`` is checked before ``int`` because ``bool`` is an
        ``int`` subclass; floats render via ``str()`` (``1.5`` →
        ``"1.5"``, ``2.0`` → ``"2.0"``); strings pass through
        verbatim and are never re-decoded.
        """
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            return value
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return str(value)
        cls._invalid(
            f"params[{key!r}] must be a string, integer, float or "
            f"boolean (got {value!r})"
        )

    @classmethod
    def _validate_params(cls, params: Any) -> List[Tuple[str, str]]:
        """Validate the ``set``-mode ``params`` dict, coercing values."""
        if not isinstance(params, dict) or not params:
            cls._invalid(
                f"params must be a non-empty dict (got {params!r})"
            )
        clean: List[Tuple[str, str]] = []
        for raw_key, raw_value in params.items():
            clean_key = cls._validate_key_str("params keys", raw_key)
            clean.append((clean_key, cls._coerce_value(clean_key, raw_value)))
        return clean

    @classmethod
    def _validate_keys(cls, keys: Any) -> List[str]:
        """Validate the ``delete``-mode ``keys`` list."""
        if not isinstance(keys, list) or not keys:
            cls._invalid(
                f"keys must be a non-empty list of strings (got {keys!r})"
            )
        clean: List[str] = []
        for item in keys:
            clean.append(cls._validate_key_str("keys items", item))
        return clean

    @classmethod
    def _validate_mapping(cls, mapping: Any) -> List[Tuple[str, str]]:
        """Validate the ``rename``-mode ``{old: new}`` mapping."""
        if not isinstance(mapping, dict) or not mapping:
            cls._invalid(
                "mapping must be a non-empty dict of {old: new} "
                f"strings (got {mapping!r})"
            )
        clean: List[Tuple[str, str]] = []
        for old, new in mapping.items():
            clean_old = cls._validate_key_str("mapping keys", old)
            clean_new = cls._validate_key_str("mapping values", new)
            if clean_old == clean_new:
                cls._invalid(
                    f"mapping must not map a key to itself ({clean_old!r})"
                )
            clean.append((clean_old, clean_new))
        return clean

    # ------------------------------------------------------------------ #
    # Shared splitting / content validation
    # ------------------------------------------------------------------ #

    @classmethod
    def _split(cls, url: str, strict: bool) -> Tuple[str, str, str, List[list]]:
        """Split a URL into prefix / raw query / fragment + pairs.

        The query span is located by string surgery (fragment cut
        first, then the first ``?``) so every byte outside the query
        survives the edit untouched. Returns
        ``(prefix, raw_query, fragment, pairs)`` where each pair is
        ``[decoded_key, decoded_value, raw_segment, out_key, out_val]``
        and the render fields are ``None`` for untouched pairs.
        Content problems (whitespace / control characters, URLs
        ``urlsplit`` rejects, a missing scheme under ``strict``)
        raise the internal ``_QueryProblem``.
        """
        if _FORBIDDEN_URL_CHARS.search(url):
            raise _QueryProblem(
                "malformed_url",
                "url must not contain whitespace or control characters "
                f"(got {url[:64]!r})",
            )
        try:
            parts = urllib.parse.urlsplit(url)
        except ValueError as exc:  # e.g. 'Invalid IPv6 URL'
            raise _QueryProblem(
                "malformed_url",
                f"url could not be parsed: {exc} (got {url[:64]!r})",
            ) from exc
        if strict and not parts.scheme:
            raise _QueryProblem(
                "missing_scheme",
                "url has no scheme; strict=True requires one — pass "
                "strict=False to edit scheme-relative or scheme-less "
                f"url-shaped strings (got {url[:64]!r})",
            )
        frag_pos = url.find("#")
        head, fragment = (
            (url[:frag_pos], url[frag_pos:]) if frag_pos != -1 else (url, "")
        )
        query_pos = head.find("?")
        if query_pos == -1:
            return head, "", fragment, []
        prefix, raw_query = head[:query_pos], head[query_pos + 1 :]
        pairs: List[list] = []
        for segment in raw_query.split("&"):
            if not segment:
                # Empty segments ('&&') carry no parameter; drop them.
                continue
            raw_key, sep, raw_value = segment.partition("=")
            if sep:
                decoded_key = urllib.parse.unquote_plus(raw_key)
                decoded_value = urllib.parse.unquote_plus(raw_value)
            else:
                # Bare key without '=' — decodes to an empty value.
                decoded_key = urllib.parse.unquote_plus(raw_key)
                decoded_value = ""
            pairs.append(
                [decoded_key, decoded_value, segment, None, None]
            )
        return prefix, raw_query, fragment, pairs

    @staticmethod
    def _render_pair(pair: list, encode: bool) -> str:
        """Render one pair back into a raw query segment."""
        if encode:
            return (
                urllib.parse.quote_plus(pair[_K], safe="")
                + "="
                + urllib.parse.quote_plus(pair[_V], safe="")
            )
        if pair[_RAW] is not None:
            return pair[_RAW]
        return f"{pair[_OUT_KEY]}={pair[_OUT_VAL]}"

    @classmethod
    def _rebuild(
        cls,
        prefix: str,
        pairs: List[list],
        fragment: str,
        encode: bool,
    ) -> str:
        """Rebuild the URL; an empty query drops the ``?`` marker."""
        new_query = "&".join(
            cls._render_pair(pair, encode) for pair in pairs
        )
        return (
            prefix + ("?" + new_query if new_query else "") + fragment
        )

    @classmethod
    def _decode_pairs(cls, pairs: List[list]) -> List[List[str]]:
        """Project the internal pairs into plain ``[key, value]`` lists."""
        return [[pair[_K], pair[_V]] for pair in pairs]

    @classmethod
    def _pairs_of_url(cls, url: str) -> List[List[str]]:
        """Decode the pairs of a *result* URL for reporting.

        The report always reflects what the produced URL actually
        decodes to — in ``encode=False`` mode inserted raw bytes are
        therefore reported post-decode, matching ``parse_qsl`` on the
        output exactly. The input is already content-validated, so the
        split cannot fail here.
        """
        _prefix, _raw, _frag, pairs = cls._split(url, strict=False)
        return cls._decode_pairs(pairs)

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }

    @classmethod
    def _check_raw_part(cls, kind: str, text: str) -> None:
        """Reject characters that break raw (encode=False) segments."""
        forbidden = (
            _RAW_FORBIDDEN_KEY_CHARS
            if kind == "key"
            else _RAW_FORBIDDEN_VALUE_CHARS
        )
        if _FORBIDDEN_URL_CHARS.search(text) or any(
            char in text for char in forbidden
        ):
            raise _QueryProblem(
                "invalid_value",
                f"raw {kind} must not contain whitespace, control "
                f"characters or any of '{''.join(forbidden)}' — pass "
                f"encode=True to encode arbitrary data "
                f"(got {text[:64]!r})",
            )

    # ------------------------------------------------------------------ #
    # set mode
    # ------------------------------------------------------------------ #

    def _run_set(
        self, url: str, params: Any, encode: bool, strict: bool
    ) -> Dict[str, Any]:
        """Add or update parameters; order preserved, new keys appended."""
        clean_params = self._validate_params(params)
        context: Dict[str, Any] = {"mode": "set"}
        try:
            if not encode:
                for name, value in clean_params:
                    self._check_raw_part("key", name)
                    self._check_raw_part("value", value)
            prefix, _raw_query, fragment, pairs = self._split(url, strict)
        except _QueryProblem as exc:
            return self._error_result(context, exc.error_type, exc.message)

        added: List[str] = []
        updated: List[str] = []
        first_index: Dict[str, int] = {
            pair[_K]: index for index, pair in reversed(list(enumerate(pairs)))
        }
        for name, value in clean_params:
            index = first_index.get(name)
            if index is None:
                pairs.append([name, value, None, name, value])
                added.append(name)
            else:
                # Rewrite the first occurrence in place; later repeats
                # of the same key are intentionally left untouched.
                pairs[index] = [name, value, None, name, value]
                updated.append(name)
        new_url = self._rebuild(prefix, pairs, fragment, encode)
        return {
            **context,
            "url": new_url,
            "params": self._pairs_of_url(new_url),
            "added": added,
            "updated": updated,
        }

    # ------------------------------------------------------------------ #
    # delete mode
    # ------------------------------------------------------------------ #

    def _run_delete(
        self, url: str, keys: Any, encode: bool, strict: bool
    ) -> Dict[str, Any]:
        """Remove every occurrence of the given keys."""
        clean_keys = self._validate_keys(keys)
        context: Dict[str, Any] = {"mode": "delete"}
        try:
            prefix, _raw_query, fragment, pairs = self._split(url, strict)
        except _QueryProblem as exc:
            return self._error_result(context, exc.error_type, exc.message)

        wanted = set(clean_keys)
        remaining = [pair for pair in pairs if pair[_K] not in wanted]
        present = {pair[_K] for pair in pairs}
        deleted = [name for name in dict.fromkeys(clean_keys) if name in present]
        missing = [name for name in dict.fromkeys(clean_keys) if name not in present]
        new_url = self._rebuild(prefix, remaining, fragment, encode)
        return {
            **context,
            "url": new_url,
            "params": self._pairs_of_url(new_url),
            "deleted": deleted,
            "missing": missing,
            "removed": len(pairs) - len(remaining),
        }

    # ------------------------------------------------------------------ #
    # rename mode
    # ------------------------------------------------------------------ #

    def _run_rename(
        self, url: str, mapping: Any, encode: bool, strict: bool
    ) -> Dict[str, Any]:
        """Rename keys in place against the original key set."""
        clean_mapping = self._validate_mapping(mapping)
        context: Dict[str, Any] = {"mode": "rename"}
        try:
            if not encode:
                for _old, new in clean_mapping:
                    self._check_raw_part("key", new)
            prefix, _raw_query, fragment, pairs = self._split(url, strict)
        except _QueryProblem as exc:
            return self._error_result(context, exc.error_type, exc.message)

        # Snapshot the original occurrences before any mutation so the
        # bookkeeping below reports the pre-rename key set.
        occurrences: Dict[str, int] = {}
        for pair in pairs:
            occurrences[pair[_K]] = occurrences.get(pair[_K], 0) + 1
        rename_map = dict(clean_mapping)
        for pair in pairs:
            new_name = rename_map.get(pair[_K])
            if new_name is None:
                continue
            # Renamed in place: the raw value bytes survive verbatim for
            # encode=False rebuilds, and a collision with an existing key
            # simply coexists as an additional occurrence (never merged).
            _raw_key, sep, raw_value = (pair[_RAW] or "").partition("=")
            pair[_K] = new_name
            pair[_RAW] = None
            pair[_OUT_KEY] = new_name
            pair[_OUT_VAL] = raw_value if sep else ""
        renamed: Dict[str, str] = {}
        missing: List[str] = []
        renamed_count = 0
        for old, new in clean_mapping:
            count = occurrences.get(old, 0)
            if count:
                renamed[old] = new
                renamed_count += count
            else:
                missing.append(old)
        new_url = self._rebuild(prefix, pairs, fragment, encode)
        return {
            **context,
            "url": new_url,
            "params": self._pairs_of_url(new_url),
            "renamed": renamed,
            "missing": missing,
            "renamed_count": renamed_count,
        }

    # ------------------------------------------------------------------ #
    # clear mode
    # ------------------------------------------------------------------ #

    def _run_clear(self, url: str, strict: bool) -> Dict[str, Any]:
        """Remove the whole query; the fragment is kept untouched."""
        context: Dict[str, Any] = {"mode": "clear"}
        try:
            prefix, _raw_query, fragment, pairs = self._split(url, strict)
        except _QueryProblem as exc:
            return self._error_result(context, exc.error_type, exc.message)
        head = url.split("#", 1)[0]
        return {
            **context,
            "url": prefix + fragment,  # '' query drops the '?' marker
            "params": [],
            "removed_params": len(pairs),
            "had_query": "?" in head,
        }

    # ------------------------------------------------------------------ #
    # sort mode
    # ------------------------------------------------------------------ #

    def _run_sort(
        self, url: str, encode: bool, strict: bool
    ) -> Dict[str, Any]:
        """Stable-sort parameters by key (OAuth signature prep)."""
        context: Dict[str, Any] = {"mode": "sort"}
        try:
            prefix, _raw_query, fragment, pairs = self._split(url, strict)
        except _QueryProblem as exc:
            return self._error_result(context, exc.error_type, exc.message)
        sorted_pairs = sorted(pairs, key=lambda pair: pair[_K])
        new_url = self._rebuild(prefix, sorted_pairs, fragment, encode)
        return {
            **context,
            "url": new_url,
            "params": self._pairs_of_url(new_url),
            "sorted": sorted_pairs != pairs,
        }

    # ------------------------------------------------------------------ #
    # toggle_bool mode
    # ------------------------------------------------------------------ #

    def _run_toggle_bool(
        self, url: str, key: Any, encode: bool, strict: bool
    ) -> Dict[str, Any]:
        """Flip a true/false flag; absent keys are added as true."""
        clean_key = self._validate_key_str("key", key)
        context: Dict[str, Any] = {"mode": "toggle_bool", "key": clean_key}
        try:
            prefix, _raw_query, fragment, pairs = self._split(url, strict)
        except _QueryProblem as exc:
            return self._error_result(context, exc.error_type, exc.message)

        for pair in pairs:
            if pair[_K] != clean_key:
                continue
            current = pair[_V].lower()
            if current not in ("true", "false"):
                return self._error_result(
                    context,
                    "invalid_value",
                    "toggle_bool values must be 'true' or 'false' "
                    "(case-insensitive) — key "
                    f"{clean_key!r} has {pair[_V]!r}; use mode='set' to "
                    "assign arbitrary values",
                )
            flipped = "false" if current == "true" else "true"
            raw_key, _sep, _raw_value = (pair[_RAW] or "").partition("=")
            pair[_V] = flipped
            pair[_RAW] = None
            pair[_OUT_KEY] = raw_key or clean_key
            pair[_OUT_VAL] = flipped
            new_url = self._rebuild(prefix, pairs, fragment, encode)
            return {
                **context,
                "url": new_url,
                "params": self._pairs_of_url(new_url),
                "action": "flipped",
                "from": current,
                "to": flipped,
            }
        # Absent key: absence reads as false, so the toggle adds true.
        pairs.append([clean_key, "true", None, clean_key, "true"])
        new_url = self._rebuild(prefix, pairs, fragment, encode)
        return {
            **context,
            "url": new_url,
            "params": self._pairs_of_url(new_url),
            "action": "added",
            "from": None,
            "to": "true",
        }
