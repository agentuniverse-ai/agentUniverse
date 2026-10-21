#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: api_doc_tool.py

"""Offline OpenAPI document inspection and linting tool built purely
on the stdlib (JSON) plus PyYAML, which is a core dependency of
agentUniverse — no network access, no new third-party dependency.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the quality-assurance layer that sits **under** the
existing request-executing tools: the merged ``APITool``
(``agentuniverse/agent/action/tool/api_tool.py``) *consumes* a parsed
OpenAPI spec at runtime to build and execute HTTP requests; this tool
never sends a request — it inspects the spec **document itself**
(endpoint inventory, rule-based lint findings, two-version diff) so a
broken contract is caught before any request runs.

Three modes, all deterministic (output is a pure function of the
input, every list sorted):

``inventory`` — a structured endpoint summary of one spec:
``{openapi_version, title, endpoints, counts}`` with each endpoint
``{method, path, operation_id?, summary?, tags?, params_count,
has_request_body, responses_count}`` (keys with ``?`` present only
when the spec carries them) sorted by ``(path, method)``. ``method``
is the upper-case verb, ``params_count`` is the *effective* merged
parameter count (operation parameters plus path-item parameters the
operation does not override — the OpenAPI override rule), and
``has_request_body`` honours both the 3.x ``requestBody`` object and
the 2.0 ``in: body`` parameter. Both JSON and YAML document bodies
are accepted (``json.loads`` first for precise errors, then
``yaml.safe_load`` — the same document in either spelling produces
the same inventory).

``lint`` — findings ``{code, severity, path, message}`` sorted by
(severity, code, path) with severities ``error`` / ``warning`` /
``info``:

* ``missing_info_title`` / ``missing_info_version`` (error) — the
  required ``info.title`` / ``info.version`` are absent or empty.
* ``paths_empty`` (error) — no ``paths`` at all (an API document
  without endpoints).
* ``operation_id_missing`` (warning) — an operation without an
  ``operationId`` (clients and code generators rely on it).
* ``operation_id_duplicate`` (error) — one ``operationId`` on two or
  more operations (the OpenAPI spec demands uniqueness); every
  occurrence after the first is reported.
* ``path_param_undeclared`` (error) — the path template uses
  ``{name}`` but no effective ``in: path`` parameter declares it (the
  exact defect that makes request building crash at runtime).
* ``path_param_defined_but_unused`` (warning) — an ``in: path``
  parameter whose name never appears in the path template (dead
  metadata; harmless but confusing).
* ``response_without_description`` (error) — a response entry whose
  ``description`` is missing or empty (``description`` is REQUIRED on
  the Response Object in every OpenAPI version).
* ``duplicate_parameter_names`` (error) — the same (name, in) pair
  twice within one parameter array (operation level or path-item
  level; uniqueness per in-type is what the spec demands. An
  operation parameter *overriding* a path-item parameter is legal and
  is not flagged).
* ``security_scheme_referenced_undefined`` (error) — ``security``
  (root or operation; operation overrides root) names a scheme that
  ``components.securitySchemes`` / 2.0 ``securityDefinitions`` does
  not define.
* ``deprecated_without_description`` (info) — an operation marked
  ``deprecated: true`` without a ``description`` telling consumers
  why, and what to use instead.
* ``missing_error_responses`` (warning) — responses contain neither a
  4xx/5xx status nor ``default`` (callers cannot learn failure
  shapes).
* ``servers_missing`` (info) — no 3.x ``servers`` (2.0: neither
  ``host`` nor ``basePath``); where should requests go?
* ``schema_ref_dangling`` (error) — a local ``$ref``
  (``#/components/schemas/X``, 2.0 ``#/definitions/X`` — any ``#/…``
  JSON pointer) that resolves nowhere in the document. The ref walk
  is **cycle-guarded** (self-referencing schemas are legal and do not
  hang the walk); refs to other documents (``http://…``, ``file.yaml``)
  cannot be verified offline and are skipped by design.

``diff`` — the version-drift mode over two spec texts (``document`` =
the NEW version, ``document_old`` = the previous one): endpoints
(method+path) ``added`` / ``removed`` / ``changed``, where each
changed endpoint carries the params and responses it gained or lost
(by ``(name, in)`` and by status code), and ``breaking`` is true iff
endpoints were removed OR params/responses were removed — with
``breaking_reasons`` naming each one, so a release review can see at
a glance what will break existing clients.

**Swagger 2.0 best-effort note.** The tool focuses on OpenAPI 3.x.
For 2.0-shaped documents it works on the equivalent fields where they
exist — ``swagger`` reported as the version, ``securityDefinitions``
read like ``components.securitySchemes``, ``#/definitions/`` pointers
checked like any other local ref, ``in: body`` parameters counted as
request bodies, and ``host``/``basePath`` accepted in place of
``servers`` — but no full 2.0-to-3.x translation is attempted; that
is the documented best-effort boundary.

Input validation is strict and happens before any computation:
``mode`` must be one of the three, the document(s) must be the spec
**text** (str; JSON or YAML spelling) of at most 1,000,000
characters each, must parse, and must parse to an object at the root
— violations raise a ``ValueError`` with a clear message, mirroring
the other common tools. The tool is read-only: inputs are never
modified, no filesystem or network access happens.
"""

import json
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple

from pydantic import ConfigDict

try:  # PyYAML is a core agentUniverse dependency, not a new one.
    import yaml
except ImportError:  # pragma: no cover - environment guard only
    yaml = None

from agentuniverse.agent.action.tool.tool import Tool

# Input size limit (bounded purely to reject pathological inputs
# early; far above real specs).
_MAX_TEXT = 1_000_000

# Path Item Object operations in canonical order (OpenAPI 3.x).
_HTTP_METHODS: Tuple[str, ...] = (
    "get", "put", "post", "delete", "options", "head", "patch", "trace",
)

# Finding sort order: errors first, then warnings, then infos.
_SEVERITY_RANK = {"error": 0, "warning": 1, "info": 2}

# Guard for the cycle-safe $ref walk and parameter dereferencing.
_MAX_DEREF_DEPTH = 8


# ------------------------------------------------------------------ #
# Parsing helpers (shared by every mode)
# ------------------------------------------------------------------ #

def _load_spec(text: str, label: str) -> Dict[str, Any]:
    """Parse one OpenAPI document text (JSON or YAML) to an object.

    ``json.loads`` is tried first because it gives precise errors for
    the JSON spelling; any text that is not JSON falls through to
    ``yaml.safe_load`` (JSON is a subset of YAML, so trying JSON
    first only makes failures more precise, never less correct).

    Raises:
        ValueError: the text parses as neither JSON nor YAML (both
            parser messages are quoted), or parses to a non-object
            root (an OpenAPI document is an object; a bare scalar,
            list or empty text cannot be one).
    """
    value: Any = None
    json_error: Optional[Exception] = None
    try:
        value = json.loads(text)
    except ValueError as exc:
        json_error = exc

    if json_error is not None:
        if yaml is None:  # pragma: no cover - environment guard only
            raise ValueError(
                f"{label} is not valid JSON ({json_error}) and PyYAML "
                "is unavailable to try the YAML spelling"
            )
        try:
            value = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ValueError(
                f"{label} is neither valid JSON nor valid YAML — "
                f"JSON: {json_error}; YAML: {exc}"
            ) from exc

    if not isinstance(value, dict):
        got = "nothing (empty or whitespace-only text)" if value is None else (
            f"a {type(value).__name__} value"
        )
        raise ValueError(
            f"{label} must parse to an object at the root — an OpenAPI "
            f"document is a mapping of fields like openapi/info/paths, "
            f"but the text parses to {got}"
        )
    return value


def _spec_flavor(spec: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """(flavor, version string) — 'openapi' or 'swagger' (2.0), or (None, None)."""
    version = spec.get("openapi")
    if isinstance(version, str) and version.strip():
        return "openapi", version.strip()
    version = spec.get("swagger")
    if isinstance(version, str) and version.strip():
        return "swagger", version.strip()
    return None, None


def _info_field(spec: Dict[str, Any], field: str) -> Optional[str]:
    """A non-empty info.<field> string, or None."""
    info = spec.get("info")
    if isinstance(info, dict):
        value = info.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _path_items(spec: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    """(path, path-item) pairs in deterministic document order."""
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return []
    items: List[Tuple[str, Dict[str, Any]]] = []
    for path, item in paths.items():
        if isinstance(path, str) and isinstance(item, dict):
            items.append((path, item))
    return items


def _operations(path_item: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    """(method, operation) pairs present on one path item."""
    ops: List[Tuple[str, Dict[str, Any]]] = []
    for method in _HTTP_METHODS:
        op = path_item.get(method)
        if isinstance(op, dict):
            ops.append((method, op))
    return ops


def _template_param_names(path: str) -> List[str]:
    """The {name} placeholders of a path template, in order (duplicates kept)."""
    names: List[str] = []
    current: Optional[List[str]] = None
    for ch in path:
        if ch == "{":
            if current is None:
                current = []
        elif ch == "}" and current is not None:
            name = "".join(current).strip()
            if name:
                names.append(name)
            current = None
        elif current is not None:
            current.append(ch)
    return names


def _deref_param(param: Any, spec: Dict[str, Any], depth: int = 0) -> Any:
    """Resolve a Parameter Object ``$ref`` into ``components/parameters``.

    Local (``#/…``) refs only, depth-capped so a parameters cycle
    cannot recurse forever; an unresolvable ref is returned as-is and
    left to the dangling-ref lint rule to report.
    """
    if depth >= _MAX_DEREF_DEPTH or not isinstance(param, dict):
        return param
    ref = param.get("$ref")
    if not (isinstance(ref, str) and ref.startswith("#/")):
        return param
    target: Any = spec
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(target, dict) and part in target:
            target = target[part]
        else:
            return param
    return _deref_param(target, spec, depth + 1)


# The spec currently being inspected; set by execute below. Kept
# module-global (single-threaded linting) so parameter dereferencing
# can resolve local $refs without threading the spec through every
# helper signature.
_SPEC_CONTEXT: List[Dict[str, Any]] = [{}]


def _param_lists(
    path_item: Dict[str, Any], operation: Dict[str, Any]
) -> Tuple[List[Any], List[Any]]:
    """The path-item and operation parameter arrays, entries dereferenced."""
    def _deref_list(raw: Any) -> List[Any]:
        if not isinstance(raw, list):
            return []
        return [_deref_param(entry, _SPEC_CONTEXT[0]) for entry in raw]

    return _deref_list(path_item.get("parameters")), _deref_list(operation.get("parameters"))


def _effective_params(
    path_item: Dict[str, Any], operation: Dict[str, Any]
) -> Tuple[Dict[Tuple[str, str], Dict[str, Any]], List[Tuple[str, str]]]:
    """Merged effective parameters of one operation.

    Returns ((name, in) → parameter, keys in first-seen order) with
    the OpenAPI override rule applied: an operation parameter with
    the same (name, in) replaces the path-item parameter.
    """
    merged: Dict[Tuple[str, str], Dict[str, Any]] = {}
    order: List[Tuple[str, str]] = []
    item_params, op_params = _param_lists(path_item, operation)
    for param in item_params + op_params:
        if not isinstance(param, dict):
            continue
        name, loc = param.get("name"), param.get("in")
        if not (isinstance(name, str) and name and isinstance(loc, str) and loc):
            continue
        key = (name, loc)
        if key not in merged:
            order.append(key)
        merged[key] = param
    return merged, order


def _has_request_body(operation: Dict[str, Any]) -> bool:
    """3.x ``requestBody`` present, or a 2.0 ``in: body`` parameter."""
    if operation.get("requestBody") is not None:
        return True
    for param in operation.get("parameters") or []:
        if isinstance(param, dict) and param.get("in") == "body":
            return True
    return False


def _security_schemes(spec: Dict[str, Any]) -> Set[str]:
    """Defined scheme names — 3.x ``components.securitySchemes`` or 2.0 ``securityDefinitions``."""
    components = spec.get("components")
    if isinstance(components, dict):
        schemes = components.get("securitySchemes")
        if isinstance(schemes, dict):
            return {str(name) for name in schemes}
    definitions = spec.get("securityDefinitions")
    if isinstance(definitions, dict):
        return {str(name) for name in definitions}
    return set()


def _resolve_local_pointer(spec: Dict[str, Any], ref: str) -> bool:
    """Whether a ``#/…`` JSON pointer resolves inside the document.

    Non-local refs (other files/URLs) cannot be verified offline and
    return True by design (skipped, not assumed dangling). Pointer
    tokens are RFC 6901-unescaped (~1 → /, ~0 → ~).
    """
    if not ref.startswith("#"):
        return True
    remainder = ref[1:]
    if remainder and not remainder.startswith("/"):
        return False  # '#foo' is not a JSON pointer
    node: Any = spec
    tokens = remainder[1:].split("/") if remainder else []
    for token in tokens:
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and token in node:
            node = node[token]
        elif isinstance(node, list) and token.isdigit() and int(token) < len(node):
            node = node[int(token)]
        else:
            return False
    return True


def _walk_dangling_refs(
    node: Any, spec: Dict[str, Any], path: str,
    out: List[Tuple[str, str]], seen: Set[int],
) -> None:
    """Collect every local ``$ref`` that resolves nowhere.

    Cycle-guarded by container identity (``id``) so self-referencing
    schemas — legal and common — terminate the walk instead of
    recursing forever.
    """
    if isinstance(node, (dict, list)):
        if id(node) in seen:
            return
        seen.add(id(node))
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#") and not _resolve_local_pointer(spec, ref):
            out.append((path + ".$ref" if path else "$ref", ref))
        for key in sorted(node, key=str):
            _walk_dangling_refs(node[key], spec, f"{path}.{key}" if path else str(key), out, seen)
    elif isinstance(node, list):
        for index, entry in enumerate(node):
            _walk_dangling_refs(entry, spec, f"{path}.{index}", out, seen)


def _endpoint_key(method: str, path: str) -> Tuple[str, str]:
    """Sort key of an endpoint — (path, method); the design's order."""
    return (path, method.upper())


# ------------------------------------------------------------------ #
# The tool
# ------------------------------------------------------------------ #

class ApiDocTool(Tool):
    """Offline OpenAPI document inspection and linting tool.

    The QA layer under the request-executing ``APITool``: inventory
    (endpoint summary), lint (rule findings) and diff (version drift)
    over one or two OpenAPI document texts — never sending a request.

    Attributes:
        max_text (int): Upper bound on each accepted document text;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "api_doc_tool"
    description: str = (
        "Offline OpenAPI document inspection and linting tool — pure "
        "Python stdlib plus core PyYAML, no network required, no "
        "request is ever sent. Summarize a spec's endpoints "
        "(mode='inventory': openapi_version, title, endpoints with "
        "method/path/operation_id/summary/tags/params_count/"
        "has_request_body/responses_count sorted by path+method, plus "
        "counts). Lint a spec (mode='lint') for rule findings "
        "{code, severity, path, message}: missing info title/version, "
        "empty paths, missing or duplicate operationIds, path "
        "template params undeclared or declared-but-unused, responses "
        "without description, duplicate parameter names per in-type, "
        "security referencing undefined schemes, deprecated "
        "operations without description, operations without error "
        "responses, missing servers and dangling schema $refs "
        "(cycle-guarded walk). Diff two spec versions "
        "(mode='diff', document = new, document_old = previous): "
        "added/removed/changed endpoints with param and response "
        "deltas and a breaking flag true when endpoints, params or "
        "responses were removed. Accepts JSON and YAML document "
        "bodies; OpenAPI 3.x focus with a documented best-effort "
        "handling of 2.0 (swagger) shapes."
    )

    MODES: ClassVar[tuple] = ("inventory", "lint", "diff")

    max_text: int = _MAX_TEXT

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        document: Any = None,
        document_old: Any = None,
    ) -> Dict[str, Any]:
        """Run one OpenAPI document inspection.

        Args:
            mode (str): One of ``inventory`` / ``lint`` / ``diff``.
            document (str): The OpenAPI document text to inspect —
                the NEW version in ``diff`` mode. JSON or YAML
                spelling; capped at ``max_text`` characters.
            document_old (str): The PREVIOUS spec text; required in
                ``diff`` mode, ignored otherwise.

        Returns:
            Dict[str, Any]: ``inventory`` — the endpoint summary;
            ``lint`` — findings plus a per-severity/per-code summary;
            ``diff`` — added/removed/changed endpoints, param and
            response deltas, and the ``breaking`` verdict with
            reasons.

        Raises:
            ValueError: invalid mode, non-text or oversized input,
                unparseable text, or a root that is not an object.
        """
        if not isinstance(mode, str) or mode not in self.MODES:
            raise ValueError(
                "mode must be one of "
                f"{', '.join(self.MODES)} (got {mode!r})"
            )
        if not isinstance(document, str):
            raise ValueError(
                "document must be the OpenAPI document text to "
                "inspect (a str, JSON or YAML spelling — not a "
                f"pre-parsed value; got {type(document).__name__})"
            )
        if len(document) > self.max_text:
            raise ValueError(
                f"document exceeds the {self.max_text}-character cap "
                f"({len(document)} characters)"
            )
        if mode == "diff":
            if not isinstance(document_old, str):
                raise ValueError(
                    "diff mode requires document_old — the previous "
                    "spec text (a str); got "
                    f"{type(document_old).__name__}"
                )
            if len(document_old) > self.max_text:
                raise ValueError(
                    f"document_old exceeds the {self.max_text}-character "
                    f"cap ({len(document_old)} characters)"
                )

        spec = _load_spec(document, "document")

        _SPEC_CONTEXT[0] = spec
        try:
            if mode == "inventory":
                return self._inventory(spec)
            if mode == "lint":
                return self._lint(spec)
            old_spec = _load_spec(document_old, "document_old")
            _SPEC_CONTEXT[0] = spec  # diff reads the NEW spec context
            return self._diff(old_spec, spec)
        finally:
            _SPEC_CONTEXT[0] = {}

    # ------------------------------------------------------------------ #
    # inventory
    # ------------------------------------------------------------------ #

    def _inventory(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        _, version = _spec_flavor(spec)
        endpoints: List[Dict[str, Any]] = []
        method_counts: Dict[str, int] = {}
        params_total = 0
        bodies_total = 0
        schema_count = 0
        components = spec.get("components")
        if isinstance(components, dict) and isinstance(components.get("schemas"), dict):
            schema_count = len(components["schemas"])
        definitions = spec.get("definitions")
        if isinstance(definitions, dict):  # 2.0 best-effort
            schema_count += len(definitions)

        for path, path_item in _path_items(spec):
            for method, operation in _operations(path_item):
                _, order = _effective_params(path_item, operation)
                responses = operation.get("responses")
                responses_count = len(responses) if isinstance(responses, dict) else 0
                entry: Dict[str, Any] = {
                    "method": method.upper(),
                    "path": path,
                    "params_count": len(order),
                    "has_request_body": _has_request_body(operation),
                    "responses_count": responses_count,
                }
                operation_id = operation.get("operationId")
                if isinstance(operation_id, str) and operation_id:
                    entry["operation_id"] = operation_id
                summary = operation.get("summary")
                if isinstance(summary, str) and summary:
                    entry["summary"] = summary
                tags = operation.get("tags")
                if isinstance(tags, list) and tags and all(isinstance(t, str) for t in tags):
                    entry["tags"] = list(tags)
                endpoints.append(entry)
                method_counts[method.upper()] = method_counts.get(method.upper(), 0) + 1
                params_total += len(order)
                bodies_total += 1 if entry["has_request_body"] else 0

        endpoints.sort(key=lambda e: _endpoint_key(e["method"], e["path"]))
        return {
            "openapi_version": version,
            "title": _info_field(spec, "title"),
            "endpoints": endpoints,
            "counts": {
                "paths": len(_path_items(spec)),
                "endpoints": len(endpoints),
                "methods": {m: method_counts[m] for m in sorted(method_counts)},
                "parameters": params_total,
                "request_bodies": bodies_total,
                "schemas": schema_count,
                "security_schemes": len(_security_schemes(spec)),
            },
        }

    # ------------------------------------------------------------------ #
    # lint
    # ------------------------------------------------------------------ #

    @staticmethod
    def _finding(
        code: str, severity: str, path: Optional[str], message: str
    ) -> Dict[str, Any]:
        """Build one ordered finding dict."""
        return {
            "code": code,
            "severity": severity,
            "path": path,
            "message": message,
        }

    def _lint(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []

        # Rules: info.title / info.version (required fields).
        if _info_field(spec, "title") is None:
            findings.append(self._finding(
                "missing_info_title", "error", "info.title",
                "info.title is missing or empty — required by the "
                "OpenAPI specification; every document must name its API",
            ))
        if _info_field(spec, "version") is None:
            findings.append(self._finding(
                "missing_info_version", "error", "info.version",
                "info.version is missing or empty — required by the "
                "OpenAPI specification; clients version against it",
            ))

        # Rule: paths must exist and be non-empty.
        path_items = _path_items(spec)
        if not path_items:
            findings.append(self._finding(
                "paths_empty", "error", "paths",
                "paths is missing, empty or malformed — an API "
                "document without endpoints describes nothing",
            ))

        # Rule: servers (3.x) / host+basePath (2.0 best-effort).
        servers = spec.get("servers")
        has_servers = isinstance(servers, list) and bool(servers)
        has_2x_base = spec.get("host") is not None or spec.get("basePath") is not None
        if not has_servers and not has_2x_base:
            findings.append(self._finding(
                "servers_missing", "info", "servers",
                "no servers entry (Swagger 2.0: neither host nor "
                "basePath) — consumers cannot know where to send "
                "requests",
            ))

        # Rule: security schemes referenced but undefined (root level).
        schemes = _security_schemes(spec)
        self._lint_security(spec.get("security"), schemes, "security", findings)

        seen_operation_ids: Dict[str, str] = {}
        duplicate_ids: Set[str] = set()

        for path, path_item in path_items:
            template_names = set(_template_param_names(path))

            # Duplicate parameter names at the path-item level.
            self._lint_duplicate_params(
                path_item.get("parameters"),
                f"paths.{path}", findings,
            )

            for method, operation in _operations(path_item):
                op_path = f"paths.{path}.{method}"
                self._lint_duplicate_params(
                    operation.get("parameters"), op_path, findings,
                )

                # Rule: operationId missing (warning).
                operation_id = operation.get("operationId")
                if not (isinstance(operation_id, str) and operation_id):
                    findings.append(self._finding(
                        "operation_id_missing", "warning",
                        f"{op_path}.operationId",
                        f"{method.upper()} {path} has no operationId — "
                        "clients and code generators rely on it to "
                        "name the call",
                    ))
                else:
                    # Rule: operationId duplicated across operations (error).
                    first_seen = seen_operation_ids.get(operation_id)
                    if first_seen is None:
                        seen_operation_ids[operation_id] = op_path
                    else:
                        if operation_id not in duplicate_ids:
                            duplicate_ids.add(operation_id)
                            findings.append(self._finding(
                                "operation_id_duplicate", "error",
                                f"{first_seen}.operationId",
                                f"operationId '{operation_id}' is used "
                                f"by more than one operation (first at "
                                f"{first_seen}, again at {op_path}) — "
                                "the spec demands uniqueness",
                            ))
                        else:
                            findings.append(self._finding(
                                "operation_id_duplicate", "error",
                                f"{op_path}.operationId",
                                f"operationId '{operation_id}' is used "
                                f"by more than one operation (already "
                                f"seen at {first_seen}) — the spec "
                                "demands uniqueness",
                            ))

                # Rules around effective parameters and the path template.
                effective, _ = _effective_params(path_item, operation)
                path_params = {name for (name, loc) in effective if loc == "path"}
                for name in sorted(template_names - path_params):
                    findings.append(self._finding(
                        "path_param_undeclared", "error", f"paths.{path}",
                        f"path template uses {{{name}}} but no effective "
                        f"in: path parameter declares it — request "
                        f"building for {method.upper()} {path} cannot "
                        "fill the placeholder",
                    ))
                for name in sorted(path_params - template_names):
                    findings.append(self._finding(
                        "path_param_defined_but_unused", "warning",
                        f"{op_path}.parameters.{name}",
                        f"in: path parameter '{name}' is defined but "
                        f"the path template never uses {{{name}}} — "
                        "dead metadata",
                    ))

                # Rules around responses.
                responses = operation.get("responses")
                has_error_response = False
                if isinstance(responses, dict) and responses:
                    for status, response in sorted(responses.items(), key=lambda kv: str(kv[0])):
                        status_str = str(status)
                        if status_str.startswith(("4", "5")) or status_str == "default":
                            has_error_response = True
                        if not (isinstance(response, dict)
                                and isinstance(response.get("description"), str)
                                and response["description"].strip()):
                            findings.append(self._finding(
                                "response_without_description", "error",
                                f"{op_path}.responses.{status_str}",
                                f"response '{status_str}' of {method.upper()} "
                                f"{path} has no description — REQUIRED "
                                "on the Response Object in every "
                                "OpenAPI version",
                            ))
                if not has_error_response:
                    findings.append(self._finding(
                        "missing_error_responses", "warning",
                        f"{op_path}.responses",
                        f"{method.upper()} {path} documents no 4xx/5xx "
                        "or default response — callers cannot learn "
                        "the failure shapes",
                    ))

                # Rule: deprecated without a description saying why.
                if operation.get("deprecated") is True:
                    description = operation.get("description")
                    if not (isinstance(description, str) and description.strip()):
                        findings.append(self._finding(
                            "deprecated_without_description", "info",
                            f"{op_path}.description",
                            f"{method.upper()} {path} is marked "
                            "deprecated but has no description — "
                            "consumers cannot learn why, or what to "
                            "use instead",
                        ))

                # Rule: operation security referencing undefined schemes
                # (operation security overrides the root entry).
                if "security" in operation:
                    self._lint_security(
                        operation.get("security"), schemes,
                        f"{op_path}.security", findings,
                    )

        # Rule: dangling local $refs anywhere in the document.
        dangling: List[Tuple[str, str]] = []
        _walk_dangling_refs(spec, spec, "", dangling, set())
        for where, ref in sorted(dangling):
            findings.append(self._finding(
                "schema_ref_dangling", "error", where,
                f"$ref '{ref}' resolves nowhere in the document — "
                "the referenced component is missing",
            ))

        findings.sort(key=lambda f: (
            _SEVERITY_RANK[f["severity"]], f["code"], str(f["path"]), f["message"],
        ))
        by_severity = {"error": 0, "warning": 0, "info": 0}
        by_code: Dict[str, int] = {}
        for finding in findings:
            by_severity[finding["severity"]] += 1
            by_code[finding["code"]] = by_code.get(finding["code"], 0) + 1
        return {
            "findings": findings,
            "summary": {
                "error": by_severity["error"],
                "warning": by_severity["warning"],
                "info": by_severity["info"],
                "by_code": dict(sorted(by_code.items())),
            },
        }

    def _lint_duplicate_params(
        self, raw_params: Any, location: str,
        findings: List[Dict[str, Any]],
    ) -> None:
        """Rule: the same (name, in) twice within ONE parameter array.

        An operation parameter overriding a path-item parameter is
        legal OpenAPI and intentionally not flagged — uniqueness is
        demanded per in-type within one array.
        """
        if not isinstance(raw_params, list):
            return
        seen: Set[Tuple[str, str]] = set()
        reported: Set[Tuple[str, str]] = set()
        for param in raw_params:
            param = _deref_param(param, _SPEC_CONTEXT[0])
            if not isinstance(param, dict):
                continue
            name, loc = param.get("name"), param.get("in")
            if not (isinstance(name, str) and name and isinstance(loc, str) and loc):
                continue
            key = (name, loc)
            if key in seen and key not in reported:
                reported.add(key)
                findings.append(self._finding(
                    "duplicate_parameter_names", "error",
                    f"{location}.parameters",
                    f"parameter name '{name}' appears more than once "
                    f"with in: {loc} in {location} — parameter "
                    "uniqueness is per in-type",
                ))
            seen.add(key)

    def _lint_security(
        self, raw_security: Any, schemes: Set[str],
        location: str, findings: List[Dict[str, Any]],
    ) -> None:
        """Rule: a security requirement naming an undefined scheme."""
        if not isinstance(raw_security, list):
            return
        for requirement in raw_security:
            if not isinstance(requirement, dict):
                continue
            for name in sorted(requirement, key=str):
                if str(name) not in schemes:
                    findings.append(self._finding(
                        "security_scheme_referenced_undefined", "error",
                        location,
                        f"security requirement '{name}' references a "
                        "scheme that components.securitySchemes "
                        "(2.0: securityDefinitions) does not define",
                    ))

    # ------------------------------------------------------------------ #
    # diff
    # ------------------------------------------------------------------ #

    @staticmethod
    def _endpoint_records(spec: Dict[str, Any]) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """(METHOD, path) → the per-endpoint facts the diff compares."""
        records: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for path, path_item in _path_items(spec):
            for method, operation in _operations(path_item):
                effective, _ = _effective_params(path_item, operation)
                responses = operation.get("responses")
                response_keys = (
                    {str(status) for status in responses}
                    if isinstance(responses, dict) else set()
                )
                records[(method.upper(), path)] = {
                    "params": set(effective.keys()),
                    "responses": response_keys,
                    "has_request_body": _has_request_body(operation),
                    "operation_id": operation.get("operationId"),
                    "summary": operation.get("summary"),
                }
        return records

    def _diff(
        self, old_spec: Dict[str, Any], new_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        _SPEC_CONTEXT[0] = old_spec
        old_records = self._endpoint_records(old_spec)
        _SPEC_CONTEXT[0] = new_spec
        new_records = self._endpoint_records(new_spec)

        old_keys, new_keys = set(old_records), set(new_records)

        def _endpoint_list(keys: Set[Tuple[str, str]]) -> List[Dict[str, str]]:
            return [
                {"method": method, "path": path}
                for method, path in sorted(keys, key=lambda k: _endpoint_key(k[0], k[1]))
            ]

        added = _endpoint_list(new_keys - old_keys)
        removed = _endpoint_list(old_keys - new_keys)

        changed: List[Dict[str, Any]] = []
        breaking_reasons: List[str] = []
        for method, path in sorted(old_keys & new_keys, key=lambda k: _endpoint_key(k[0], k[1])):
            old_rec, new_rec = old_records[(method, path)], new_records[(method, path)]
            params_added = sorted(new_rec["params"] - old_rec["params"])
            params_removed = sorted(old_rec["params"] - new_rec["params"])
            responses_added = sorted(new_rec["responses"] - old_rec["responses"])
            responses_removed = sorted(old_rec["responses"] - new_rec["responses"])
            changes: List[str] = []
            if params_added:
                changes.append("params.added")
            if params_removed:
                changes.append("params.removed")
            if responses_added:
                changes.append("responses.added")
            if responses_removed:
                changes.append("responses.removed")
            if old_rec["has_request_body"] != new_rec["has_request_body"]:
                changes.append("request_body")
            if old_rec["operation_id"] != new_rec["operation_id"]:
                changes.append("operation_id")
            if old_rec["summary"] != new_rec["summary"]:
                changes.append("summary")
            if not changes:
                continue
            changed.append({
                "method": method,
                "path": path,
                "params": {
                    "added": [f"{name} (in: {loc})" for name, loc in params_added],
                    "removed": [f"{name} (in: {loc})" for name, loc in params_removed],
                },
                "responses": {
                    "added": responses_added,
                    "removed": responses_removed,
                },
                "changes": changes,
            })
            for name, loc in params_removed:
                breaking_reasons.append(
                    f"{method} {path} removed param '{name}' (in: {loc})"
                )
            for status in responses_removed:
                breaking_reasons.append(
                    f"{method} {path} removed response '{status}'"
                )

        for endpoint in removed:
            breaking_reasons.append(
                f"removed endpoint {endpoint['method']} {endpoint['path']}"
            )

        breaking = bool(removed) or any(
            "params.removed" in entry["changes"]
            or "responses.removed" in entry["changes"]
            for entry in changed
        )
        # breaking_reasons already holds exactly the removed endpoints,
        # params and responses; keep it even when non-breaking (empty).
        return {
            "added": added,
            "removed": removed,
            "changed": changed,
            "breaking": breaking,
            "breaking_reasons": sorted(breaking_reasons),
            "summary": {
                "added": len(added),
                "removed": len(removed),
                "changed": len(changed),
            },
        }
