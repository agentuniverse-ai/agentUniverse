#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: url_parser_tool.py

"""URL parsing / inspection / building / normalization tool on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency URL utility agents can
call whenever they need to look at, edit or rebuild the addresses they
work with — everything is a thin, strictly-validated façade over
``urllib.parse``. Four modes are supported:

* ``parse`` — split a URL into scheme / netloc / hostname / path /
  query / fragment, with the query decoded into an ordered list of
  ``[key, value]`` pairs (multi-value aware, blanks kept), the port
  resolved against the per-scheme defaults (http 80, https 443, ws 80,
  wss 443, ftp 21), embedded userinfo flagged (raw ``username`` /
  ``password``) and bracketed IPv6 hosts handled. Non-http(s) schemes
  such as ``ftp`` or ``urn`` are flagged via ``is_http_scheme`` but not
  rejected.
* ``query`` — get / set / delete query parameters on a URL. ``get``
  returns every value of a key (or every pair when no key is given);
  ``set`` replaces the first occurrence of a key with one or more new
  values (a list sets multiple occurrences) and appends the key when it
  does not exist yet; ``delete`` drops every occurrence. Order of the
  untouched parameters is always preserved and percent-encoding is
  round-tripped through ``parse_qsl`` / ``urlencode``.
* ``build`` — construct a URL from parts (``scheme``, ``host`` or raw
  ``netloc``, ``port``, ``path``, ``query``, ``fragment``, optional
  ``username`` / ``password``) with strict per-part validation.
* ``normalize`` — canonicalize a URL: lowercase the scheme and host,
  strip trailing-dot hosts (fully-qualified-domain root), remove the
  port when it equals the scheme default, sort the query by key
  (stable, preserving the relative order of equal keys) and drop empty
  ``?`` / ``#`` markers. The transformation is idempotent.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode / operation, missing
``url``, missing ``key`` for query set/delete, conflicting ``host`` and
``netloc`` in build mode) raise a ``ValueError``, mirroring the other
common tools. Errors that depend on the *URL content* — control
characters or whitespace inside the URL, unmatched IPv6 brackets,
missing scheme (unless ``allow_scheme_relative`` is set), ports that
are not integers or out of the 1-65535 range, and invalid build parts
(scheme grammar, host characters, path/query/fragment shape) — are
returned as a structured ``error`` payload so an agent can react
without catching exceptions.
"""

import re
import urllib.parse
from operator import itemgetter
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_SCHEME_RE = re.compile(r"\A[A-Za-z][A-Za-z0-9+.\-]*\Z")
# Characters that may never appear unescaped anywhere in a URL.
_FORBIDDEN_URL_CHARS = re.compile(r"[\x00-\x20\x7f]")


class _URLProblem(Exception):
    """Internal carrier for content-level URL failures.

    Carries the structured ``error_type`` plus a human-readable message;
    the mode runners convert it into a structured ``error`` payload.
    """

    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message


class URLParserTool(Tool):
    """URL parsing / inspection / building / normalization tool.

    Attributes:
        max_url_chars (int): Upper bound on the ``url`` input and on any
            single string part in build mode; longer inputs are rejected
            before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "url_parser_tool"
    description: str = (
        "URL parser tool — pure Python stdlib urllib.parse, no network "
        "required. Parse a URL into scheme/host/port (scheme defaults "
        "resolved)/path/ordered query parameter list/fragment with "
        "userinfo and IPv6 support (mode='parse'); get/set/delete query "
        "parameters, multi-value aware and order preserving "
        "(mode='query'); build a URL from validated parts "
        "(mode='build'); and canonicalize URLs — lowercase scheme/host, "
        "remove default ports, sort query keys, resolve trailing-dot "
        "hosts, drop empty fragments — idempotently (mode='normalize')."
    )

    MODES: ClassVar[tuple] = ("parse", "query", "build", "normalize")
    QUERY_OPERATIONS: ClassVar[tuple] = ("get", "set", "delete")
    # Well-known default ports; used to resolve parse-mode ports and to
    # strip redundant ports in normalize mode.
    DEFAULT_PORTS: ClassVar[Dict[str, int]] = {
        "http": 80,
        "https": 443,
        "ws": 80,
        "wss": 443,
        "ftp": 21,
    }

    max_url_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        url: Any = None,
        allow_scheme_relative: Any = None,
        operation: Any = None,
        key: Any = None,
        value: Any = None,
        scheme: Any = None,
        host: Any = None,
        netloc: Any = None,
        port: Any = None,
        path: Any = None,
        query: Any = None,
        fragment: Any = None,
        username: Any = None,
        password: Any = None,
    ) -> Dict[str, Any]:
        """Run one URL operation.

        Args:
            mode (str): One of ``parse`` / ``query`` / ``build`` /
                ``normalize``.
            url (str): The URL to work on — required for the ``parse``,
                ``query`` and ``normalize`` modes; not used by ``build``.
            allow_scheme_relative (bool): Allow URLs / builds without a
                scheme (relative references such as ``//host/path``).
                Defaults to ``False`` for ``parse`` and ``build``; the
                ``query`` and ``normalize`` modes always accept
                scheme-less URLs.
            operation (str): ``get`` / ``set`` / ``delete`` — required
                for the ``query`` mode; not used elsewhere.
            key (str): Query mode — the parameter name. Required for
                ``set`` / ``delete``; optional for ``get`` (without it,
                every pair is returned).
            value (str | list[str]): Query ``set`` only — the new value
                (or list of values, which sets multiple occurrences).
            scheme (str): Build mode — the URL scheme, e.g. ``https``.
            host (str): Build mode — the host, IPv6 literal included in
                brackets; mutually exclusive with ``netloc``.
            netloc (str): Build mode — a raw authority block
                (``user:pass@host:port``); mutually exclusive with
                ``host`` / ``port`` / ``username`` / ``password``.
            port (int): Build mode — an explicit port, 1-65535.
            path (str): Build mode — the path, empty or starting with
                ``/``.
            query (str | list | dict): Build mode — the query as a raw
                string (no leading ``?``) or a list of ``[key, value]``
                pairs / dict (values may be lists for multi-value).
            fragment (str): Build mode — the fragment, no leading ``#``.
            username (str): Build mode — percent-encoded into the
                authority userinfo block.
            password (str): Build mode — percent-encoded into the
                authority userinfo block.

        Returns:
            Dict[str, Any]: The operation result (the parsed components,
            the rebuilt URL, ...) plus the call context, or a structured
            ``error`` payload for content-level failures (malformed
            URLs, missing scheme, bad ports, invalid build parts).

        Raises:
            ValueError: If any parameter is malformed (before any
            computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        allow_relative = self._validate_allow_scheme_relative(
            allow_scheme_relative
        )
        if mode == "parse":
            return self._run_parse(url, allow_relative)
        if mode == "query":
            return self._run_query(url, operation, key, value)
        if mode == "build":
            return self._run_build(
                allow_relative,
                scheme,
                host,
                netloc,
                port,
                path,
                query,
                fragment,
                username,
                password,
            )
        return self._run_normalize(url)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"url_parser_tool: {message}")

    @classmethod
    def _validate_allow_scheme_relative(cls, value: Any) -> bool:
        """Validate the ``allow_scheme_relative`` flag."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        cls._invalid(
            "allow_scheme_relative must be a boolean or omitted "
            f"(got {value!r})"
        )

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
    def _validate_part_str(
        cls, name: str, value: Any, allow_empty: bool = True
    ) -> str:
        """Validate a single build-mode string part."""
        if value is None:
            return ""
        if isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{name} must be a string (got {value!r})")
        if not value and not allow_empty:
            cls._invalid(f"{name} must be a non-empty string (got '')")
        if len(value) > 100_000:
            cls._invalid(
                f"{name} exceeds the {100_000:,}-character limit "
                f"(got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _validate_query_key(cls, key: Any, required: bool) -> Optional[str]:
        """Validate the query-mode ``key`` parameter."""
        if key is None:
            if required:
                cls._invalid("key is required for this operation (got None)")
            return None
        if isinstance(key, bool) or not isinstance(key, str):
            cls._invalid(f"key must be a non-empty string (got {key!r})")
        if not key:
            cls._invalid("key must be a non-empty string (got '')")
        if len(key) > 100_000:
            cls._invalid(
                f"key exceeds the {100_000:,}-character limit "
                f"(got {len(key):,} characters)"
            )
        return key

    # ------------------------------------------------------------------ #
    # Shared splitting / content validation
    # ------------------------------------------------------------------ #

    @classmethod
    def _split(
        cls, url: str, *, require_scheme: bool, allow_scheme_relative: bool
    ) -> Tuple[urllib.parse.SplitResult, Optional[int]]:
        """Split a URL with strict content validation.

        Returns the ``SplitResult`` and the explicit port (``None`` when
        absent). Content problems (whitespace / control characters,
        unmatched IPv6 brackets, bad ports, missing scheme) raise the
        internal ``_URLProblem`` carrying the structured error type.
        """
        if _FORBIDDEN_URL_CHARS.search(url):
            raise _URLProblem(
                "malformed_url",
                "url must not contain whitespace or control characters "
                f"(got {url[:64]!r})",
            )
        try:
            parts = urllib.parse.urlsplit(url)
        except ValueError as exc:  # e.g. 'Invalid IPv6 URL'
            raise _URLProblem(
                "malformed_url",
                f"url could not be parsed: {exc} (got {url[:64]!r})",
            ) from exc
        try:
            explicit_port = parts.port
        except ValueError as exc:  # non-integer or out-of-range port
            raise _URLProblem(
                "invalid_port",
                f"netloc contains an invalid port: {exc}",
            ) from exc
        if explicit_port is not None and not 1 <= explicit_port <= 65535:
            raise _URLProblem(
                "invalid_port",
                f"port must be within 1-65535 (got {explicit_port})",
            )
        if require_scheme and not allow_scheme_relative and not parts.scheme:
            raise _URLProblem(
                "missing_scheme",
                "url has no scheme; pass allow_scheme_relative=True to "
                "parse or build scheme-less relative references "
                f"(got {url[:64]!r})",
            )
        return parts, explicit_port

    @staticmethod
    def _params_of(query: str) -> List[List[str]]:
        """Decode a raw query string into ordered ``[key, value]`` pairs."""
        if not query:
            return []
        return [
            list(pair)
            for pair in urllib.parse.parse_qsl(query, keep_blank_values=True)
        ]

    @staticmethod
    def _userinfo_of(netloc: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract the raw (still percent-encoded) username / password."""
        if "@" not in netloc:
            return None, None
        userinfo = netloc.rsplit("@", 1)[0]
        username, sep, password = userinfo.partition(":")
        return username if username or sep else None, (
            password if sep else None
        )

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

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _run_parse(
        self, url: Any, allow_scheme_relative: bool
    ) -> Dict[str, Any]:
        """Split a URL into strictly-validated components."""
        clean_url = self._validate_url(url)
        context: Dict[str, Any] = {"mode": "parse"}
        try:
            parts, explicit_port = self._split(
                clean_url,
                require_scheme=True,
                allow_scheme_relative=allow_scheme_relative,
            )
        except _URLProblem as exc:
            return self._error_result(context, exc.error_type, exc.message)
        username, password = self._userinfo_of(parts.netloc)
        scheme = parts.scheme
        default_port = self.DEFAULT_PORTS.get(scheme)
        return {
            **context,
            "url": clean_url,
            "scheme": scheme,
            "netloc": parts.netloc,
            "hostname": parts.hostname or None,
            "port": (
                explicit_port
                if explicit_port is not None
                else default_port
            ),
            "explicit_port": explicit_port,
            "default_port": default_port,
            "path": parts.path,
            "query": parts.query,
            "params": self._params_of(parts.query),
            "fragment": parts.fragment,
            "has_user_info": username is not None,
            "username": username,
            "password": password,
            "is_http_scheme": scheme in ("http", "https"),
        }

    # ------------------------------------------------------------------ #
    # query mode
    # ------------------------------------------------------------------ #

    def _run_query(
        self, url: Any, operation: Any, key: Any, value: Any
    ) -> Dict[str, Any]:
        """Get / set / delete query parameters, order preserving."""
        clean_url = self._validate_url(url)
        if operation not in self.QUERY_OPERATIONS:
            self._invalid(
                "operation must be one of: "
                f"{', '.join(self.QUERY_OPERATIONS)} for query mode "
                f"(got {operation!r})"
            )
        context: Dict[str, Any] = {"mode": "query", "operation": operation}
        try:
            parts, _ = self._split(
                clean_url, require_scheme=False, allow_scheme_relative=True
            )
        except _URLProblem as exc:
            return self._error_result(context, exc.error_type, exc.message)
        params = self._params_of(parts.query)

        if operation == "get":
            clean_key = self._validate_query_key(key, required=False)
            if clean_key is None:
                return {**context, "url": clean_url, "params": params}
            values = [v for k, v in params if k == clean_key]
            return {
                **context,
                "url": clean_url,
                "key": clean_key,
                "values": values,
                "count": len(values),
            }

        clean_key = self._validate_query_key(key, required=True)
        if operation == "set":
            new_values = self._validate_set_value(value)
            replaced = False
            new_params: List[List[str]] = []
            for pair_key, pair_value in params:
                if pair_key == clean_key:
                    if not replaced:
                        new_params.extend(
                            [clean_key, item] for item in new_values
                        )
                        replaced = True
                else:
                    new_params.append([pair_key, pair_value])
            if not replaced:
                new_params.extend([clean_key, item] for item in new_values)
            new_url = self._rebuild(parts, new_params)
            return {
                **context,
                "url": new_url,
                "key": clean_key,
                "params": new_params,
                "replaced": replaced,
            }

        # operation == "delete"
        new_params = [pair for pair in params if pair[0] != clean_key]
        removed = len(params) - len(new_params)
        new_url = self._rebuild(parts, new_params)
        return {
            **context,
            "url": new_url,
            "key": clean_key,
            "params": new_params,
            "removed": removed,
        }

    @classmethod
    def _validate_set_value(cls, value: Any) -> List[str]:
        """Validate the query ``set`` value (string or list of strings)."""
        if isinstance(value, str):
            return [value]
        if isinstance(value, list) and value and all(
            isinstance(item, str) for item in value
        ):
            return list(value)
        cls._invalid(
            "value must be a string or a non-empty list of strings for "
            f"query set (got {value!r})"
        )

    @staticmethod
    def _rebuild(
        parts: urllib.parse.SplitResult, params: List[List[str]]
    ) -> str:
        """Rebuild a URL from its parts with new query pairs."""
        new_query = (
            urllib.parse.urlencode([tuple(pair) for pair in params])
            if params
            else ""
        )
        return urllib.parse.urlunsplit(
            (parts.scheme, parts.netloc, parts.path, new_query, parts.fragment)
        )

    # ------------------------------------------------------------------ #
    # build mode
    # ------------------------------------------------------------------ #

    def _run_build(
        self,
        allow_scheme_relative: bool,
        scheme: Any,
        host: Any,
        netloc: Any,
        port: Any,
        path: Any,
        query: Any,
        fragment: Any,
        username: Any,
        password: Any,
    ) -> Dict[str, Any]:
        """Construct a URL from strictly-validated parts."""
        context: Dict[str, Any] = {"mode": "build"}
        problem = self._validate_build_parts(
            allow_scheme_relative,
            scheme,
            host,
            netloc,
            port,
            path,
            query,
            fragment,
            username,
            password,
        )
        if problem is not None:
            return self._error_result(
                context, problem.error_type, problem.message
            )
        clean_scheme = "" if scheme is None else scheme
        # Compose the authority: either the raw netloc or the parts.
        if netloc is not None:
            authority = netloc
        else:
            authority = host or ""
            if username is not None:
                userinfo = urllib.parse.quote(username, safe="")
                if password is not None:
                    userinfo += ":" + urllib.parse.quote(password, safe="")
                authority = userinfo + "@" + authority
            if port is not None:
                authority = f"{authority}:{port}"
        clean_path = path or ""
        clean_query = self._build_query_string(query)
        clean_fragment = fragment or ""
        url = urllib.parse.urlunsplit(
            (clean_scheme, authority, clean_path, clean_query, clean_fragment)
        )
        return {
            **context,
            "url": url,
            "scheme": clean_scheme,
            "netloc": authority,
            "path": clean_path,
            "query": clean_query,
            "fragment": clean_fragment,
        }

    @classmethod
    def _validate_build_parts(
        cls,
        allow_scheme_relative: bool,
        scheme: Any,
        host: Any,
        netloc: Any,
        port: Any,
        path: Any,
        query: Any,
        fragment: Any,
        username: Any,
        password: Any,
    ) -> Optional[_URLProblem]:
        """Validate every build part; return a problem or ``None``.

        Type / shape problems raise ``ValueError`` directly (they are
        parameter-level); value problems that depend on the part content
        are returned as a ``_URLProblem`` for the structured payload.
        """

        def problem(error_type: str, message: str) -> _URLProblem:
            return _URLProblem(error_type, message)

        if scheme is None:
            if not allow_scheme_relative:
                return problem(
                    "missing_scheme",
                    "scheme is required to build a URL; pass "
                    "allow_scheme_relative=True to build scheme-less "
                    "relative references (got None)",
                )
        else:
            if isinstance(scheme, bool) or not isinstance(scheme, str):
                cls._invalid(f"scheme must be a string (got {scheme!r})")
            if not scheme or not _SCHEME_RE.match(scheme):
                return problem(
                    "invalid_scheme",
                    "scheme must match [A-Za-z][A-Za-z0-9+.-]* "
                    f"(got {scheme[:64]!r})",
                )
            if len(scheme) > 100_000:
                cls._invalid(
                    f"scheme exceeds the {100_000:,}-character limit"
                )

        if netloc is not None and host is not None:
            cls._invalid("pass either netloc or host, not both")
        if netloc is not None and (
            port is not None or username is not None or password is not None
        ):
            cls._invalid(
                "pass either netloc or host/port/username/password, not both"
            )
        if netloc is None and host is None:
            if port is not None or username is not None or password is not None:
                cls._invalid(
                    "port/username/password require host (netloc and host "
                    "are both absent)"
                )

        authority: Optional[str] = None
        if netloc is not None:
            authority = cls._validate_part_str("netloc", netloc)
            if _FORBIDDEN_URL_CHARS.search(authority) or any(
                char in authority for char in "/#"
            ):
                return problem(
                    "invalid_netloc",
                    "netloc must not contain whitespace, control "
                    "characters, '/' or '#' "
                    f"(got {authority[:64]!r})",
                )
            if not authority:
                return problem(
                    "invalid_netloc",
                    "netloc must be a non-empty authority string "
                    "(use host='' semantics by omitting it instead)",
                )
        else:
            clean_host = cls._validate_part_str("host", host or "")
            if clean_host:
                if _FORBIDDEN_URL_CHARS.search(clean_host) or any(
                    char in clean_host for char in "/?#@"
                ):
                    return problem(
                        "invalid_host",
                        "host must not contain whitespace, control "
                        "characters or any of '/?#@' "
                        f"(got {clean_host[:64]!r})",
                    )
                if ":" in clean_host and not (
                    clean_host.startswith("[") and clean_host.endswith("]")
                ):
                    return problem(
                        "invalid_host",
                        "IPv6 literal hosts must be wrapped in brackets, "
                        f"e.g. '[2001:db8::1]' (got {clean_host[:64]!r})",
                    )
                if clean_host.startswith("[") and not clean_host.endswith("]"):
                    return problem(
                        "invalid_host",
                        "host starts with '[' but has no closing ']' "
                        f"(got {clean_host[:64]!r})",
                    )
            if port is not None:
                if isinstance(port, bool) or not isinstance(port, int):
                    cls._invalid(f"port must be an integer (got {port!r})")
                if not 1 <= port <= 65535:
                    return problem(
                        "invalid_port",
                        f"port must be within 1-65535 (got {port})",
                    )
            if username is not None:
                cls._validate_part_str(
                    "username", username, allow_empty=False
                )
                if password is not None:
                    cls._validate_part_str("password", password)
            elif password is not None:
                cls._invalid("password requires username to be set as well")

        clean_path = cls._validate_part_str("path", path)
        if clean_path:
            if not clean_path.startswith("/"):
                return problem(
                    "invalid_path",
                    "path must be empty or start with '/' "
                    f"(got {clean_path[:64]!r})",
                )
            if not authority and clean_path.startswith("//"):
                return problem(
                    "invalid_path",
                    "path must not start with '//' when the URL has no "
                    "authority — it would be reparsed as one "
                    f"(got {clean_path[:64]!r})",
                )

        if query is not None and not isinstance(query, (str, list, dict)):
            cls._invalid(
                "query must be a string, a list of [key, value] pairs or "
                f"a dict (got {query!r})"
            )
        if isinstance(query, str):
            clean_query_str = cls._validate_part_str("query", query)
            if "#" in clean_query_str:
                return problem(
                    "invalid_query",
                    "query must not contain '#' (fragments are passed "
                    f"separately) (got {clean_query_str[:64]!r})",
                )
            if clean_query_str.startswith("?"):
                return problem(
                    "invalid_query",
                    "query must not start with '?' "
                    f"(got {clean_query_str[:64]!r})",
                )
        elif isinstance(query, list):
            for index, item in enumerate(query):
                if (
                    isinstance(item, (list, tuple))
                    and len(item) == 2
                    and isinstance(item[0], str)
                    and isinstance(item[1], str)
                ):
                    continue
                cls._invalid(
                    "query list items must be [key, value] string pairs "
                    f"(item {index}: {item!r})"
                )
        elif isinstance(query, dict):
            for dict_key, dict_value in query.items():
                if not isinstance(dict_key, str):
                    cls._invalid(f"query dict keys must be strings (got {dict_key!r})")
                if isinstance(dict_value, str):
                    continue
                if isinstance(dict_value, list) and all(
                    isinstance(entry, str) for entry in dict_value
                ):
                    continue
                cls._invalid(
                    "query dict values must be strings or lists of strings "
                    f"(key {dict_key!r}: {dict_value!r})"
                )

        clean_fragment = cls._validate_part_str("fragment", fragment)
        if "#" in clean_fragment:
            return problem(
                "invalid_fragment",
                "fragment must not contain '#' "
                f"(got {clean_fragment[:64]!r})",
            )
        if clean_fragment.startswith("#"):
            return problem(
                "invalid_fragment",
                f"fragment must not start with '#' (got {clean_fragment[:64]!r})",
            )
        return None

    @classmethod
    def _build_query_string(cls, query: Any) -> str:
        """Render the build-mode ``query`` part as a string."""
        if query is None:
            return ""
        if isinstance(query, str):
            return query
        if isinstance(query, dict):
            pairs: List[List[str]] = []
            for dict_key, dict_value in query.items():
                values = (
                    dict_value
                    if isinstance(dict_value, list)
                    else [dict_value]
                )
                pairs.extend([dict_key, entry] for entry in values)
            return (
                urllib.parse.urlencode([tuple(pair) for pair in pairs])
                if pairs
                else ""
            )
        return (
            urllib.parse.urlencode([tuple(pair) for pair in query])
            if query
            else ""
        )

    # ------------------------------------------------------------------ #
    # normalize mode
    # ------------------------------------------------------------------ #

    def _run_normalize(self, url: Any) -> Dict[str, Any]:
        """Canonicalize a URL; the transformation is idempotent."""
        clean_url = self._validate_url(url)
        context: Dict[str, Any] = {"mode": "normalize"}
        try:
            parts, explicit_port = self._split(
                clean_url, require_scheme=False, allow_scheme_relative=True
            )
        except _URLProblem as exc:
            return self._error_result(context, exc.error_type, exc.message)

        changes: List[str] = []

        # 1. Lowercase the scheme (urlsplit lowercases already; detect the
        #    original spelling to report the change).
        raw_scheme_match = re.match(
            r"\A([A-Za-z][A-Za-z0-9+.\-]*):", clean_url
        )
        if raw_scheme_match and raw_scheme_match.group(1) != parts.scheme:
            changes.append("lowercased_scheme")

        # 2. Authority surgery: lowercase the host, strip trailing dots,
        #    drop default / empty ports. Userinfo stays byte-identical.
        netloc = parts.netloc
        new_netloc = netloc
        if netloc:
            userinfo, sep, hostport = netloc.rpartition("@")
            if sep:
                userinfo += "@"
            else:
                userinfo, hostport = "", netloc
            if hostport.startswith("["):
                closing = hostport.find("]")
                host_raw = hostport[: closing + 1]
                rest = hostport[closing + 1 :]
                port_str: Optional[str] = (
                    rest[1:] if rest.startswith(":") else None
                )
            elif ":" in hostport:
                # Safe: _split already rejected non-integer suffixes via
                # parts.port, so everything after the last ':' is the port.
                host_raw, port_str = hostport.rsplit(":", 1)
            else:
                host_raw, port_str = hostport, None
            lowered_host = host_raw.lower()
            if lowered_host != host_raw:
                changes.append("lowercased_host")
            stripped_host = lowered_host.rstrip(".")
            if stripped_host != lowered_host:
                changes.append("resolved_trailing_dot_host")
            kept_port = ""
            if port_str:
                # A non-empty explicit port: drop it only when it equals
                # the scheme's well-known default.
                if (
                    parts.scheme in self.DEFAULT_PORTS
                    and int(port_str) == self.DEFAULT_PORTS[parts.scheme]
                ):
                    changes.append("removed_default_port")
                else:
                    kept_port = ":" + port_str
            elif port_str == "":
                # Present but empty, e.g. 'http://host:/path'.
                changes.append("removed_empty_port")
            new_netloc = userinfo + stripped_host + kept_port

        # 3. Query: stable-sort the pairs by key; keep the original bytes
        #    when the order already matches so repeated runs converge.
        new_query = parts.query
        if parts.query:
            params = self._params_of(parts.query)
            sorted_params = sorted(params, key=itemgetter(0))
            if sorted_params != params:
                changes.append("sorted_query_keys")
                new_query = urllib.parse.urlencode(
                    [tuple(pair) for pair in sorted_params]
                )

        # 4. Drop empty '?' / '#' markers (urlunsplit omits them when the
        #    corresponding component is empty).
        head = clean_url.split("#", 1)[0]
        if parts.query == "" and "?" in head:
            changes.append("removed_empty_query")
        if parts.fragment == "" and "#" in clean_url:
            changes.append("removed_empty_fragment")

        normalized = urllib.parse.urlunsplit(
            (parts.scheme, new_netloc, parts.path, new_query, parts.fragment)
        )
        return {
            **context,
            "url": normalized,
            "changed": changes,
            "changed_count": len(changes),
        }
