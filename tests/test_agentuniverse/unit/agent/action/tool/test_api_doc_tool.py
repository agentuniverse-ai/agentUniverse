#!/usr/bin/env python3
# -*- coding:utf-8 -*-

r"""Offline unit tests for the ApiDocTool (issue #252, other tools).

No network access, no fixtures on disk — every OpenAPI document is
inline. Ground truths were derived by hand from the OpenAPI 3.1
machinery the tool models and recorded here as explicit expectations:

* the MASTER fixture deliberately breaks every lint rule exactly
  once (or the documented number of times); the (code, severity,
  path) multiset of its findings is asserted in full;
* the CLEAN control is the same API written correctly and must lint
  to zero findings;
* MASTER is rendered once as JSON and once as YAML from the SAME
  Python dict, and both spellings must produce identical inventory
  and lint output — the input-parity ground truth (YAML quoting of
  string status keys keeps '204' a string, so both loaders agree);
* YAML-specific shape (unquoted ``200:`` parsing to an int key) is
  covered separately: response handling goes through str(status);
* the diff breaking matrix separates removed endpoints, removed
  params and removed responses (each breaking on its own) from
  pure additions (never breaking).

Distinction under test: this tool inspects spec documents; it never
sends a request (the merged APITool does that from a parsed spec).
"""

import json
import os

import pytest
import yaml

from agentuniverse.agent.action.tool.common_tool import ApiDocTool
from agentuniverse.agent.action.tool.common_tool.api_doc_tool import (
    _resolve_local_pointer,
    _template_param_names,
)

TOOL = ApiDocTool()

FINDING_KEYS = {"code", "severity", "path", "message"}
_SEVERITY_RANK = {"error": 0, "warning": 1, "info": 2}


def inventory(text):
    return TOOL.execute(mode="inventory", document=text)


def lint(text):
    return TOOL.execute(mode="lint", document=text)


def diff(new_text, old_text):
    return TOOL.execute(mode="diff", document=new_text, document_old=old_text)


def as_json(spec):
    return json.dumps(spec, indent=1)


def as_yaml(spec):
    return yaml.safe_dump(spec, sort_keys=False)


def codes(result):
    return [f["code"] for f in result["findings"]]


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

# One realistic but deliberately flawed 3.1 spec touching EVERY rule:
# info lacks title+version; no servers; root security names an
# undefined scheme; POST /users repeats the X-Request-Id header param
# (one array, duplicate (name, in)); GET /users has no operationId and
# no error response; GET /users/{id} never declares {id} and its 204
# response has no description; DELETE /users/{id} is deprecated with
# no description and shows only 2xx responses; GET /status declares
# an in:path param its template never uses and op-level security on
# another undefined scheme; GET /legacy reuses the getUser
# operationId; components hold a dangling $ref and a legal User<->Pet
# cycle the walk must survive.
MASTER = {
    "openapi": "3.1.0",
    "info": {"description": "Flawed user API exercising every lint rule"},
    "security": [{"apiKeyMissing": []}],
    "paths": {
        "/users": {
            "post": {
                "operationId": "createUser",
                "summary": "Create a user",
                "tags": ["users"],
                "parameters": [
                    {"name": "X-Request-Id", "in": "header", "schema": {"type": "string"}},
                    {"name": "X-Request-Id", "in": "header", "schema": {"type": "string"}},
                ],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
                },
                "responses": {
                    "201": {"description": "Created"},
                    "400": {"description": "Invalid body"},
                },
            },
            "get": {
                "summary": "List users",
                "parameters": [
                    {"name": "limit", "in": "query", "schema": {"type": "integer"}},
                    {"name": "format", "in": "query", "schema": {"type": "string"}},
                ],
                "responses": {"200": {"description": "A page of users"}},
            },
        },
        "/users/{id}": {
            "parameters": [
                {"name": "trace", "in": "query", "schema": {"type": "string"}},
            ],
            "get": {
                "operationId": "getUser",
                "summary": "Fetch one user",
                "responses": {
                    "200": {"description": "The user"},
                    "404": {"description": "No such user"},
                    "204": {},
                },
            },
            "delete": {
                "operationId": "deleteUser",
                "summary": "Delete a user",
                "deprecated": True,
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {"204": {"description": "Deleted"}},
            },
        },
        "/status": {
            "get": {
                "operationId": "getStatus",
                "parameters": [
                    {"name": "zone", "in": "path", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {"200": {"description": "Healthy"}},
                "security": [{"oauthUndefined": ["read"]}],
            },
        },
        "/legacy": {
            "get": {
                "operationId": "getUser",
                "responses": {"200": {"description": "Legacy"}},
            },
        },
    },
    "components": {
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "pet": {"$ref": "#/components/schemas/Pet"},
                },
            },
            "Pet": {
                "type": "object",
                "properties": {"owner": {"$ref": "#/components/schemas/User"}},
            },
            "Broken": {"$ref": "#/components/schemas/Missing"},
        },
        "securitySchemes": {
            "apiKey": {"type": "apiKey", "name": "X-Key", "in": "header"},
        },
    },
}

# The same API written correctly — the clean control.
CLEAN = {
    "openapi": "3.1.0",
    "info": {"title": "Clean user API", "version": "2.0.0"},
    "servers": [{"url": "https://api.example.com"}],
    "paths": {
        "/users": {
            "get": {
                "operationId": "listUsers",
                "summary": "List users",
                "tags": ["users"],
                "parameters": [
                    {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
                ],
                "responses": {
                    "200": {"description": "A page of users"},
                    "default": {"description": "Unexpected error"},
                },
            },
            "post": {
                "operationId": "createUser",
                "summary": "Create a user",
                "tags": ["users"],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
                },
                "responses": {
                    "201": {"description": "Created"},
                    "400": {"description": "Invalid body"},
                },
            },
        },
        "/users/{id}": {
            "get": {
                "operationId": "getUser",
                "summary": "Fetch one user",
                "tags": ["users"],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {
                    "200": {"description": "The user"},
                    "404": {"description": "No such user"},
                },
            },
            "delete": {
                "operationId": "deleteUser",
                "summary": "Delete a user",
                "tags": ["users"],
                "deprecated": True,
                "description": "Deprecated: use POST /users/{id}/archive instead.",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {
                    "204": {"description": "Deleted"},
                    "404": {"description": "No such user"},
                },
            },
        },
    },
    "components": {
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "pet": {"$ref": "#/components/schemas/Pet"},
                },
            },
            "Pet": {
                "type": "object",
                "properties": {"owner": {"$ref": "#/components/schemas/User"}},
            },
            "Error": {"type": "object", "properties": {"message": {"type": "string"}}},
        },
    },
}


# ------------------------------------------------------------------ #
# Registration and shape
# ------------------------------------------------------------------ #

def test_registration_and_metadata():
    assert TOOL.name == "api_doc_tool"
    assert TOOL.MODES == ("inventory", "lint", "diff")
    assert "OpenAPI" in TOOL.description
    assert "never sent" in TOOL.description or "no request" in TOOL.description
    yaml_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "..", "..",
        "agentuniverse", "agent", "action", "tool", "common_tool",
        "api_doc_tool.yaml",
    )
    with open(os.path.abspath(yaml_path), "r", encoding="utf-8") as fh:
        meta = yaml.safe_load(fh)
    assert meta["name"] == "api_doc_tool"
    assert meta["metadata"]["class"] == "ApiDocTool"
    assert meta["metadata"]["module"].endswith("api_doc_tool")
    assert set(meta["args_model_schema"]["properties"]["mode"]["enum"]) \
        == {"inventory", "lint", "diff"}


def test_finding_shape():
    result = lint(as_json(MASTER))
    assert set(result) == {"findings", "summary"}
    for finding in result["findings"]:
        assert set(finding) == FINDING_KEYS
        assert finding["severity"] in ("error", "warning", "info")
        assert finding["path"] is None or isinstance(finding["path"], str)


# ------------------------------------------------------------------ #
# lint — the MASTER ground truth (every rule, exact multiset)
# ------------------------------------------------------------------ #

def test_master_lint_ground_truth():
    result = lint(as_json(MASTER))
    actual = sorted(
        (f["code"], f["severity"], f["path"]) for f in result["findings"]
    )
    expected = sorted([
        ("missing_info_title", "error", "info.title"),
        ("missing_info_version", "error", "info.version"),
        ("servers_missing", "info", "servers"),
        ("security_scheme_referenced_undefined", "error", "security"),
        ("security_scheme_referenced_undefined", "error", "paths./status.get.security"),
        ("duplicate_parameter_names", "error", "paths./users.post.parameters"),
        ("operation_id_missing", "warning", "paths./users.get.operationId"),
        ("missing_error_responses", "warning", "paths./users.get.responses"),
        ("path_param_undeclared", "error", "paths./users/{id}"),
        ("response_without_description", "error", "paths./users/{id}.get.responses.204"),
        ("missing_error_responses", "warning", "paths./users/{id}.delete.responses"),
        ("deprecated_without_description", "info", "paths./users/{id}.delete.description"),
        ("path_param_defined_but_unused", "error", "paths./status.get.parameters.zone"),
        ("missing_error_responses", "warning", "paths./status.get.responses"),
        ("operation_id_duplicate", "error", "paths./users/{id}.get.operationId"),
        ("missing_error_responses", "warning", "paths./legacy.get.responses"),
        ("schema_ref_dangling", "error", "components.schemas.Broken.$ref"),
    ])
    assert actual == expected
    assert result["summary"] == {
        "error": 10,
        "warning": 5,
        "info": 2,
        "by_code": {
            "deprecated_without_description": 1,
            "duplicate_parameter_names": 1,
            "missing_error_responses": 4,
            "missing_info_title": 1,
            "missing_info_version": 1,
            "operation_id_duplicate": 1,
            "operation_id_missing": 1,
            "path_param_defined_but_unused": 1,
            "path_param_undeclared": 1,
            "response_without_description": 1,
            "schema_ref_dangling": 1,
            "security_scheme_referenced_undefined": 2,
            "servers_missing": 1,
        },
    }


def test_master_lint_sorted_and_deterministic():
    r1 = lint(as_json(MASTER))
    r2 = lint(as_json(MASTER))
    assert r1 == r2
    keys = [
        (_SEVERITY_RANK[f["severity"]], f["code"], f["path"], f["message"])
        for f in r1["findings"]
    ]
    assert keys == sorted(keys)


def test_clean_control_lints_to_zero():
    result = lint(as_json(CLEAN))
    assert result["findings"] == []
    assert result["summary"]["error"] == 0
    assert result["summary"]["by_code"] == {}


# ------------------------------------------------------------------ #
# lint — per-rule minimal documents
# ------------------------------------------------------------------ #

def _mini(**overrides):
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1.0.0"},
        "servers": [{"url": "https://x.example.com"}],
        "paths": {
            "/a": {
                "get": {
                    "operationId": "getA",
                    "responses": {
                        "200": {"description": "ok"},
                        "404": {"description": "no"},
                    },
                }
            }
        },
    }
    spec.update(overrides)
    return spec


def test_rule_missing_info_title_and_version():
    spec = _mini(info={"description": "neither field"})
    got = codes(lint(as_json(spec)))
    assert "missing_info_title" in got
    assert "missing_info_version" in got
    # An empty string is as missing as an absent key.
    spec = _mini(info={"title": "   ", "version": ""})
    got = codes(lint(as_json(spec)))
    assert "missing_info_title" in got
    assert "missing_info_version" in got


def test_rule_paths_empty():
    for paths in ({}, None):
        spec = _mini(paths=paths)
        findings = [
            f for f in lint(as_json(spec))["findings"]
            if f["code"] == "paths_empty"
        ]
        assert len(findings) == 1
        # The OpenAPI schema permits an empty paths object — advice,
        # not a violation.
        assert findings[0]["severity"] == "warning"
    assert "paths_empty" not in codes(lint(as_json(_mini())))

    # 3.1 webhooks alone carry the API — no empty-paths finding.
    spec = _mini(paths={}, webhooks={"newUser": {"post": {
        "operationId": "hookNewUser",
        "responses": {"200": {"description": "ok"}, "default": {"description": "e"}},
    }}})
    assert "paths_empty" not in codes(lint(as_json(spec)))


def test_rule_operation_id_duplicate_reports_once_with_both_paths():
    spec = _mini(paths={
        "/a": {"get": {"operationId": "dup", "responses": {"200": {"description": "ok"}, "404": {"description": "no"}}}},
        "/b": {"get": {"operationId": "dup", "responses": {"200": {"description": "ok"}, "404": {"description": "no"}}}},
    })
    findings = [f for f in lint(as_json(spec))["findings"] if f["code"] == "operation_id_duplicate"]
    assert len(findings) == 1
    assert findings[0]["severity"] == "error"
    assert findings[0]["path"] == "paths./a.get.operationId"
    assert "/a" in findings[0]["message"] and "/b" in findings[0]["message"]


def test_rule_path_param_undeclared_and_override():
    # {id} used but never declared — the runtime request-builder crash.
    spec = _mini(paths={
        "/a/{id}": {"get": {"operationId": "getA", "responses": {"200": {"description": "ok"}, "404": {"description": "no"}}}},
    })
    findings = [f for f in lint(as_json(spec))["findings"] if f["code"] == "path_param_undeclared"]
    assert len(findings) == 1
    assert findings[0]["severity"] == "error"
    assert "{id}" in findings[0]["message"]

    # Declaring id at the PATH-ITEM level covers GET too (effective
    # params merge with the OpenAPI override rule).
    spec["paths"]["/a/{id}"]["parameters"] = [
        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
        {"name": "verbose", "in": "query", "schema": {"type": "boolean"}},
    ]
    assert "path_param_undeclared" not in codes(lint(as_json(spec)))
    assert "path_param_defined_but_unused" not in codes(lint(as_json(spec)))


def test_rule_path_param_defined_but_unused():
    spec = _mini(paths={
        "/a": {
            "get": {
                "operationId": "getA",
                "parameters": [
                    {"name": "ghost", "in": "path", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {"200": {"description": "ok"}, "404": {"description": "no"}},
            }
        },
    })
    findings = [
        f for f in lint(as_json(spec))["findings"]
        if f["code"] == "path_param_defined_but_unused"
    ]
    assert len(findings) == 1
    # The spec's MUST: an in: path name corresponds to a template
    # expression — error, not cosmetic advice.
    assert findings[0]["severity"] == "error"
    assert findings[0]["path"] == "paths./a.get.parameters.ghost"


def test_rule_response_without_description_including_empty_string():
    spec = _mini(paths={
        "/a": {
            "get": {
                "operationId": "getA",
                "responses": {
                    "200": {"description": "ok"},
                    "418": {},          # absent
                    "500": {"description": "   "},  # whitespace-only
                },
            }
        },
    })
    findings = [
        f for f in lint(as_json(spec))["findings"]
        if f["code"] == "response_without_description"
    ]
    # Ground truth: the absent (418) and whitespace-only (500)
    # descriptions are flagged; the described 200 is not.
    assert {f["path"] for f in findings} == {
        "paths./a.get.responses.418",
        "paths./a.get.responses.500",
    }
    assert all(f["severity"] == "error" for f in findings)


def test_rule_duplicate_parameter_names_same_in_only():
    # Same name, different in: legal per in-type — NOT flagged.
    spec = _mini(paths={
        "/a": {
            "get": {
                "operationId": "getA",
                "parameters": [
                    {"name": "q", "in": "query", "schema": {"type": "string"}},
                    {"name": "q", "in": "header", "schema": {"type": "string"}},
                ],
                "responses": {"200": {"description": "ok"}, "404": {"description": "no"}},
            }
        },
    })
    assert "duplicate_parameter_names" not in codes(lint(as_json(spec)))

    # Same (name, in) twice in ONE array: the error.
    spec["paths"]["/a"]["get"]["parameters"].append(
        {"name": "q", "in": "query", "schema": {"type": "string"}},
    )
    findings = [
        f for f in lint(as_json(spec))["findings"]
        if f["code"] == "duplicate_parameter_names"
    ]
    assert len(findings) == 1
    assert findings[0]["severity"] == "error"
    assert findings[0]["path"] == "paths./a.get.parameters"


def test_parameter_override_between_levels_is_legal():
    # Operation parameter overriding a path-item parameter of the
    # same (name, in) is OpenAPI's documented merge rule, not a
    # duplicate; effective params count it once (with the override's
    # schema winning is a lint-invisible detail, the count is the
    # observable ground truth here).
    spec = _mini(paths={
        "/a/{id}": {
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "get": {
                "operationId": "getA",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {"200": {"description": "ok"}, "404": {"description": "no"}},
            },
        },
    })
    result = lint(as_json(spec))
    assert "duplicate_parameter_names" not in codes(result)
    assert "path_param_undeclared" not in codes(result)
    inv = inventory(as_json(spec))
    assert inv["endpoints"][0]["params_count"] == 1


def test_rule_security_referenced_undefined_and_override():
    # Root security names only defined schemes; an operation may
    # override the root entry — its own list is what gets checked.
    spec = _mini(security=[{"key": []}])
    spec["components"] = {
        "securitySchemes": {"key": {"type": "apiKey", "name": "k", "in": "header"}},
    }
    assert "security_scheme_referenced_undefined" not in codes(lint(as_json(spec)))

    # An operation with security: [] opts out — a bad root scheme is
    # still reported at the root (and only there).
    spec["paths"]["/a"]["get"]["security"] = []
    findings = [
        f for f in lint(as_json(spec))["findings"]
        if f["code"] == "security_scheme_referenced_undefined"
    ]
    # Root security: [{"key": []}] is defined → no finding at all.
    assert findings == []

    spec["security"] = [{"nope": []}]
    findings = [
        f for f in lint(as_json(spec))["findings"]
        if f["code"] == "security_scheme_referenced_undefined"
    ]
    assert len(findings) == 1
    assert findings[0]["path"] == "security"
    assert findings[0]["severity"] == "error"


def test_rule_deprecated_without_description():
    spec = _mini(paths={
        "/a": {
            "get": {
                "operationId": "getA",
                "deprecated": True,
                "responses": {"200": {"description": "ok"}, "404": {"description": "no"}},
            }
        },
    })
    findings = [
        f for f in lint(as_json(spec))["findings"]
        if f["code"] == "deprecated_without_description"
    ]
    assert len(findings) == 1
    assert findings[0]["severity"] == "info"


def test_rule_missing_error_responses_default_counts():
    spec = _mini(paths={
        "/a": {
            "get": {
                "operationId": "getA",
                "responses": {"default": {"description": "anything"}},
            }
        },
    })
    assert "missing_error_responses" not in codes(lint(as_json(spec)))


def test_rule_servers_missing_and_2x_host():
    spec = dict(_mini())
    del spec["servers"]
    assert "servers_missing" in codes(lint(as_json(spec)))

    spec = _mini()
    del spec["servers"]
    spec["host"] = "api.example.com"  # 2.0 best-effort
    assert "servers_missing" not in codes(lint(as_json(spec)))


def test_rule_schema_ref_dangling_and_pointer_edges():
    spec = _mini()
    spec["components"] = {"schemas": {"A": {"type": "object"}}}
    spec["paths"]["/a"]["get"]["responses"]["200"] = {
        "description": "ok",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/A"}}},
    }
    assert "schema_ref_dangling" not in codes(lint(as_json(spec)))

    # Dangling — includes non-schema targets and pointer escaping:
    # '~1' decodes to '/', '~0' to '~' (RFC 6901).
    spec["paths"]["/a"]["get"]["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/paths/~1a/get/responses/200",
    }
    assert "schema_ref_dangling" not in codes(lint(as_json(spec)))

    spec["paths"]["/a"]["get"]["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/A/~0tilde",
    }
    findings = [
        f for f in lint(as_json(spec))["findings"]
        if f["code"] == "schema_ref_dangling"
    ]
    assert len(findings) == 1
    assert findings[0]["severity"] == "error"

    # Non-local refs cannot be verified offline — skipped by design.
    spec["paths"]["/a"]["get"]["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "https://cdn.example.com/schemas/common.yaml#/X",
    }
    assert "schema_ref_dangling" not in codes(lint(as_json(spec)))

    # Direct helper ground truths for the pointer resolver.
    doc = {"paths": {"/a": {"get": 7}}, "l": [1, {"x": 2}]}
    assert _resolve_local_pointer(doc, "#")
    assert _resolve_local_pointer(doc, "#/paths/~1a/get") is True
    assert _resolve_local_pointer(doc, "#/l/1/x")
    assert not _resolve_local_pointer(doc, "#/paths/~1a/put")
    assert not _resolve_local_pointer(doc, "#/l/9")
    assert not _resolve_local_pointer(doc, "#foo")
    assert _resolve_local_pointer(doc, "other.yaml#/x")  # non-local skipped


def test_ref_cycle_walk_terminates():
    # Self-referencing schemas are legal; the walk must terminate.
    spec = _mini()
    spec["components"] = {
        "schemas": {
            "Node": {
                "type": "object",
                "properties": {"next": {"$ref": "#/components/schemas/Node"}},
            },
        },
    }
    result = lint(as_json(spec))
    assert "schema_ref_dangling" not in codes(result)


def test_template_param_names_edges():
    assert _template_param_names("/users/{id}/orders/{oid}") == ["id", "oid"]
    assert _template_param_names("/plain") == []
    assert _template_param_names("/a/{}") == []          # empty name ignored
    assert _template_param_names("/a/{unclosed") == []   # never closed


# ------------------------------------------------------------------ #
# $ref resolution semantics (regressions)
# ------------------------------------------------------------------ #

def _op_ok(oid, **extra):
    op = {"operationId": oid, "responses": {"200": {"description": "ok"}, "default": {"description": "e"}}}
    op.update(extra)
    return op


def test_response_ref_description_resolved():
    # A Response Object written as a local $ref whose target carries
    # the (required) description is LEGAL — no false positive.
    spec = _mini()
    spec["components"] = {"responses": {"OK": {"description": "created"}}}
    spec["paths"]["/a"]["post"] = _op_ok(
        "createA",
        requestBody={"content": {"application/json": {"schema": {"type": "object"}}}},
    )
    spec["paths"]["/a"]["post"]["responses"]["201"] = {"$ref": "#/components/responses/OK"}
    assert "response_without_description" not in codes(lint(as_json(spec)))

    # A $ref whose target lacks the description is still flagged.
    spec["components"]["responses"]["BAD"] = {}
    spec["paths"]["/a"]["post"]["responses"]["201"] = {"$ref": "#/components/responses/BAD"}
    findings = [f for f in lint(as_json(spec))["findings"] if f["code"] == "response_without_description"]
    assert len(findings) == 1 and findings[0]["path"] == "paths./a.post.responses.201"


def test_path_item_ref_resolved():
    # A path item that IS a local $ref (e.g. 3.1 components/pathItems)
    # carries real operations — they must be inventoried and linted.
    spec = _mini()
    spec["components"] = {"pathItems": {"A": {"get": _op_ok("getA"), "post": _op_ok("postA")}}}
    spec["paths"] = {"/a": {"$ref": "#/components/pathItems/A"}}
    result = inventory(as_json(spec))
    assert [(e["method"], e["path"]) for e in result["endpoints"]] == [("GET", "/a"), ("POST", "/a")]

    # Rules fire inside the referenced item (POST here lacks nothing,
    # so break one: remove its default error response).
    broken = json.loads(as_json(spec))
    broken["components"]["pathItems"]["A"]["post"]["responses"] = {"200": {"description": "ok"}}
    assert "missing_error_responses" in codes(lint(as_json(broken)))

    # 3.1 semantics: siblings of the referencing item merge over the
    # target — the local PUT wins over the referenced PUT.
    spec["paths"]["/a"]["put"] = _op_ok("putALocal")
    spec["components"]["pathItems"]["A"]["put"] = _op_ok("putARef")
    result = inventory(as_json(spec))
    by_method = {e["method"]: e for e in result["endpoints"]}
    assert by_method["PUT"]["operation_id"] == "putALocal"

    # Cycles between path items terminate instead of hanging.
    cyc = _mini()
    cyc["components"] = {"pathItems": {
        "A": {"$ref": "#/components/pathItems/B"},
        "B": {"$ref": "#/components/pathItems/A"},
    }}
    cyc["paths"] = {"/a": {"$ref": "#/components/pathItems/A"}}
    assert inventory(as_json(cyc))["counts"]["endpoints"] == 0


def test_webhooks_inventory_and_lint():
    spec = {
        "openapi": "3.1.0",
        "info": {"title": "Hooks", "version": "1.0.0"},
        "webhooks": {
            "newUser": {"post": _op_ok("hookNewUser")},
            "orderShipped": {
                "post": {"operationId": "hookShipped", "responses": {"200": {"description": "ok"}}},
            },
        },
    }
    result = inventory(as_json(spec))
    assert result["counts"]["webhooks"] == 2
    assert [(e["method"], e["path"]) for e in result["endpoints"]] == [
        ("POST", "newUser"), ("POST", "orderShipped"),
    ]
    findings = {f["code"]: f for f in lint(as_json(spec))["findings"]}
    assert "paths_empty" not in findings            # webhooks carry the API
    assert "spec_version_invalid" not in findings
    assert findings["missing_error_responses"]["path"] == "webhooks.orderShipped.post.responses"

    # diff sees webhook endpoints like any other.
    old = json.loads(as_json(spec))
    new = json.loads(as_json(spec))
    del new["webhooks"]["newUser"]
    result = diff(as_json(new), as_json(old))
    assert result["removed"] == [{"method": "POST", "path": "newUser"}]
    assert result["breaking"] is True


def test_rule_spec_version_invalid():
    cases = [
        ("3.1", "two-part version"),          # openapi wants X.Y.Z
        ("v3", "garbage"),
        (3.1, "YAML float spelling"),
        ("", "blank"),
    ]
    for bad, why in cases:
        spec = _mini()
        spec["openapi"] = bad
        findings = [f for f in lint(as_json(spec))["findings"] if f["code"] == "spec_version_invalid"]
        assert len(findings) == 1, why
        assert findings[0]["severity"] == "error"
        assert findings[0]["path"] == "openapi"

    # Missing entirely: neither openapi nor swagger.
    spec = _mini()
    del spec["openapi"]
    findings = [f for f in lint(as_json(spec))["findings"] if f["code"] == "spec_version_invalid"]
    assert len(findings) == 1

    # Well-formed versions pass (pre-release suffix included).
    for good in ("3.0.0", "3.0.3", "3.1.0", "3.1.0-beta1"):
        assert "spec_version_invalid" not in codes(lint(as_json(_mini(openapi=good))))
    assert "spec_version_invalid" not in codes(lint(as_json({"swagger": "2.0", "info": {"title": "t", "version": "1"}, "host": "h", "paths": {}})))


def test_rule_responses_missing():
    spec = _mini()
    del spec["paths"]["/a"]["get"]["responses"]
    findings = [f for f in lint(as_json(spec))["findings"] if f["code"] == "responses_missing"]
    assert len(findings) == 1
    assert findings[0]["severity"] == "error"
    assert findings[0]["path"] == "paths./a.get.responses"
    # Missing responses is the error itself — no redundant warning.
    assert "missing_error_responses" not in codes(lint(as_json(spec)))

    # An empty responses object is equally broken (minProperties 1).
    spec = _mini()
    spec["paths"]["/a"]["get"]["responses"] = {}
    assert "responses_missing" in codes(lint(as_json(spec)))


def test_deep_param_ref_chain_resolves():
    # A legal chain of parameter $refs far beyond the old depth cap
    # resolves exactly: id stays an effective path parameter.
    spec = _mini()
    chain = 12
    params = {}
    for i in range(chain):
        if i == 0:
            params["P0"] = {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
        else:
            params[f"P{i}"] = {"$ref": f"#/components/parameters/P{i - 1}"}
    spec["components"] = {"parameters": params}
    spec["paths"] = {"/a/{id}": {"get": _op_ok("getId", parameters=[{"$ref": f"#/components/parameters/P{chain - 1}"}])}}
    result = lint(as_json(spec))
    assert "path_param_undeclared" not in codes(result)
    inv = inventory(as_json(spec))
    assert inv["endpoints"][0]["params_count"] == 1


def test_param_override_semantics():
    # Same (name, in) at both levels: the OPERATION parameter wins;
    # same name different in: both survive. Verified on the merged
    # content, not just the count.
    from agentuniverse.agent.action.tool.common_tool.api_doc_tool import _effective_params
    path_item = {"parameters": [
        {"name": "limit", "in": "query", "schema": {"type": "integer"}},
        {"name": "token", "in": "query", "schema": {"type": "string"}},
    ]}
    operation = {"parameters": [
        {"name": "limit", "in": "query", "schema": {"type": "string", "maxLength": 5}},
        {"name": "limit", "in": "header", "schema": {"type": "string"}},
    ]}
    merged, order = _effective_params(path_item, operation)
    assert order == [("limit", "query"), ("token", "query"), ("limit", "header")]
    assert merged[("limit", "query")]["schema"] == {"type": "string", "maxLength": 5}
    assert merged[("token", "query")]["schema"] == {"type": "string"}

    # And through inventory: the override counts once per (name, in).
    spec = _mini()
    spec["paths"]["/a"]["get"]["parameters"] = operation["parameters"]
    spec["paths"]["/a"]["parameters"] = path_item["parameters"]
    inv = inventory(as_json(spec))
    assert inv["endpoints"][0]["params_count"] == 3


def test_pointer_lookup_into_arrays():
    # Pointers must follow array indices and ~0/~1 escapes exactly.
    doc = {
        "components": {"schemas": {"A": {"allOf": [
            {"type": "object"},
            {"$ref": "#/components/schemas/B"},
        ]}}},
    }
    assert _resolve_local_pointer(doc, "#/components/schemas/A/allOf/0")
    assert _resolve_local_pointer(doc, "#/components/schemas/A/allOf/0/type")
    assert not _resolve_local_pointer(doc, "#/components/schemas/A/allOf/2")
    assert not _resolve_local_pointer(doc, "#/components/schemas/A/anyOf/0")

    # Escaped tokens: a schema literally named "a/b" and "m~n".
    doc2 = {"components": {"schemas": {"a/b": {"m~n": 1}}}}
    assert _resolve_local_pointer(doc2, "#/components/schemas/a~1b/m~0n")
    assert not _resolve_local_pointer(doc2, "#/components/schemas/a/b")


# ------------------------------------------------------------------ #
# inventory — ground truth
# ------------------------------------------------------------------ #

def test_master_inventory_ground_truth():
    result = inventory(as_json(MASTER))
    assert result["openapi_version"] == "3.1.0"
    assert result["title"] is None
    order = [(e["method"], e["path"]) for e in result["endpoints"]]
    assert order == [
        ("GET", "/legacy"),
        ("GET", "/status"),
        ("GET", "/users"),
        ("POST", "/users"),
        ("DELETE", "/users/{id}"),
        ("GET", "/users/{id}"),
    ]
    by_key = {(e["method"], e["path"]): e for e in result["endpoints"]}

    post_users = by_key[("POST", "/users")]
    assert post_users == {
        "method": "POST",
        "path": "/users",
        "operation_id": "createUser",
        "summary": "Create a user",
        "tags": ["users"],
        # Effective (name, in) merge: the duplicated X-Request-Id
        # header counts once (the duplicate is the lint finding).
        "params_count": 1,
        "has_request_body": True,
        "responses_count": 2,
    }

    get_users = by_key[("GET", "/users")]
    assert "operation_id" not in get_users        # absent, not None
    assert get_users["params_count"] == 2
    assert get_users["has_request_body"] is False
    assert get_users["responses_count"] == 1

    delete_user = by_key[("DELETE", "/users/{id}")]
    # path-item 'trace' + own 'id' — the merge rule at work.
    assert delete_user["params_count"] == 2

    get_user = by_key[("GET", "/users/{id}")]
    assert get_user["params_count"] == 1          # only path-item 'trace'
    assert get_user["responses_count"] == 3

    assert result["counts"] == {
        "paths": 4,
        "webhooks": 0,
        "endpoints": 6,
        "methods": {"DELETE": 1, "GET": 4, "POST": 1},
        # per-endpoint effective params: 0+1+2+1+2+1 (see above)
        "parameters": 7,
        "request_bodies": 1,
        "schemas": 3,
        "security_schemes": 1,
    }


def test_clean_inventory_ground_truth():
    result = inventory(as_json(CLEAN))
    assert result["openapi_version"] == "3.1.0"
    assert result["title"] == "Clean user API"
    assert [(e["method"], e["path"]) for e in result["endpoints"]] == [
        ("GET", "/users"),
        ("POST", "/users"),
        ("DELETE", "/users/{id}"),
        ("GET", "/users/{id}"),
    ]
    assert result["counts"] == {
        "paths": 2,
        "webhooks": 0,
        "endpoints": 4,
        "methods": {"DELETE": 1, "GET": 2, "POST": 1},
        "parameters": 3,
        "request_bodies": 1,
        "schemas": 3,
        "security_schemes": 0,
    }
    # Deterministic: same input, byte-identical output.
    assert inventory(as_json(CLEAN)) == result


def test_inventory_without_openapi_or_swagger_key():
    result = inventory(as_json({"info": {"title": "x"}, "paths": {}}))
    assert result["openapi_version"] is None


# ------------------------------------------------------------------ #
# JSON / YAML input parity
# ------------------------------------------------------------------ #

def test_json_yaml_parity_inventory_and_lint():
    j = as_json(MASTER)
    y = as_yaml(MASTER)
    assert inventory(y) == inventory(j)
    assert lint(y) == lint(j)

    j = as_json(CLEAN)
    y = as_yaml(CLEAN)
    assert inventory(y) == inventory(j)
    assert lint(y) == lint(j)


def test_yaml_specific_shapes():
    # Unquoted 200/404 parse to INT keys under YAML — response
    # handling must go through str(status) like the JSON spelling.
    text = (
        "openapi: 3.0.0\n"
        "info:\n"
        "  title: T\n"
        "  version: 1.0.0\n"
        "servers:\n"
        "  - url: https://x.example.com\n"
        "paths:\n"
        "  /a:\n"
        "    get:\n"
        "      operationId: getA\n"
        "      responses:\n"
        "        200:\n"
        "          description: ok\n"
        "        404:\n"
        "          description: \"not found\"  # quoted: bare 'no' is a YAML 1.1 boolean\n"
    )
    result = lint(text)
    assert result["findings"] == []
    inv = inventory(text)
    assert inv["endpoints"][0]["responses_count"] == 2


# ------------------------------------------------------------------ #
# Swagger 2.0 best-effort
# ------------------------------------------------------------------ #

SWAGGER_20 = {
    "swagger": "2.0",
    "info": {"title": "Legacy pets", "version": "1.0"},
    "host": "api.example.com",
    "basePath": "/v1",
    "schemes": ["https"],
    "securityDefinitions": {"key": {"type": "apiKey", "name": "k", "in": "query"}},
    "paths": {
        "/pets/{petId}": {
            "get": {
                "operationId": "getPet",
                "parameters": [
                    {"name": "petId", "in": "path", "required": True, "type": "string"},
                ],
                "responses": {
                    "200": {"description": "ok", "schema": {"$ref": "#/definitions/Pet"}},
                    "404": {"description": "no"},
                },
            },
            "post": {
                "operationId": "addPet",
                "parameters": [
                    {"name": "petId", "in": "path", "required": True, "type": "string"},
                    {"name": "body", "in": "body", "schema": {"$ref": "#/definitions/Pet"}},
                ],
                "responses": {"201": {"description": "made"}, "400": {"description": "bad"}},
            },
        },
    },
    "definitions": {"Pet": {"type": "object", "properties": {"name": {"type": "string"}}}},
}


def test_swagger_20_inventory_best_effort():
    result = inventory(as_json(SWAGGER_20))
    assert result["openapi_version"] == "2.0"
    assert result["counts"]["schemas"] == 1          # definitions counted
    assert result["counts"]["security_schemes"] == 1  # securityDefinitions
    by_key = {(e["method"], e["path"]): e for e in result["endpoints"]}
    assert by_key[("POST", "/pets/{petId}")]["has_request_body"] is True  # in: body
    assert by_key[("GET", "/pets/{petId}")]["has_request_body"] is False


def test_swagger_20_lint_best_effort():
    result = lint(as_json(SWAGGER_20))
    assert result["findings"] == []  # host/basePath accepted for servers; refs resolve

    # 2.0 dangling ref into #/definitions/ is still caught.
    broken = json.loads(as_json(SWAGGER_20))
    broken["definitions"]["Pet"]["properties"]["friend"] = {"$ref": "#/definitions/Ghost"}
    findings = [
        f for f in lint(as_json(broken))["findings"]
        if f["code"] == "schema_ref_dangling"
    ]
    assert len(findings) == 1
    assert findings[0]["path"] == "definitions.Pet.properties.friend.$ref"


# ------------------------------------------------------------------ #
# diff — the version-drift mode
# ------------------------------------------------------------------ #

def _old_spec():
    return {
        "openapi": "3.0.0",
        "info": {"title": "API", "version": "1.0.0"},
        "servers": [{"url": "https://x"}],
        "paths": {
            "/a": {
                "get": {
                    "operationId": "getA",
                    "summary": "Same",
                    "parameters": [
                        {"name": "p1", "in": "query", "schema": {"type": "string"}},
                        {"name": "p2", "in": "query", "schema": {"type": "string"}},
                    ],
                    "responses": {"200": {"description": "ok"}, "404": {"description": "no"}},
                }
            },
            "/b": {
                "post": {
                    "operationId": "postB",
                    "parameters": [{"name": "q", "in": "query", "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "ok"}, "422": {"description": "bad"}},
                }
            },
            "/c": {
                "get": {
                    "operationId": "getC",
                    "responses": {"200": {"description": "ok"}, "500": {"description": "boom"}},
                }
            },
        },
    }


def test_diff_breaking_matrix():
    old = _old_spec()
    new = json.loads(as_json(old))
    # /a: p2 removed, p3 added, 404 removed, 422 added, summary changed.
    new["paths"]["/a"]["get"]["parameters"] = [
        {"name": "p1", "in": "query", "schema": {"type": "string"}},
        {"name": "p3", "in": "query", "schema": {"type": "string"}},
    ]
    new["paths"]["/a"]["get"]["responses"] = {"200": {"description": "ok"}, "422": {"description": "bad"}}
    new["paths"]["/a"]["get"]["summary"] = "Changed"
    # /b: method replaced (POST removed, DELETE added).
    new["paths"]["/b"] = {
        "delete": {
            "operationId": "deleteB",
            "parameters": [{"name": "q", "in": "query", "schema": {"type": "string"}}],
            "responses": {"200": {"description": "ok"}, "422": {"description": "bad"}},
        }
    }
    # /c removed, /d added.
    del new["paths"]["/c"]
    new["paths"]["/d"] = {
        "get": {
            "operationId": "getD",
            "responses": {"200": {"description": "ok"}, "404": {"description": "no"}},
        }
    }

    result = diff(as_json(new), as_json(old))
    assert result["added"] == [
        {"method": "DELETE", "path": "/b"},
        {"method": "GET", "path": "/d"},
    ]
    assert result["removed"] == [
        {"method": "POST", "path": "/b"},
        {"method": "GET", "path": "/c"},
    ]
    assert len(result["changed"]) == 1
    changed = result["changed"][0]
    assert (changed["method"], changed["path"]) == ("GET", "/a")
    assert changed["params"] == {"added": ["p3 (in: query)"], "removed": ["p2 (in: query)"]}
    assert changed["responses"] == {"added": ["422"], "removed": ["404"]}
    assert changed["changes"] == [
        "params.added", "params.removed",
        "responses.added", "responses.removed",
        "summary",
    ]
    assert result["summary"] == {"added": 2, "removed": 2, "changed": 1}
    assert result["breaking"] is True
    assert result["breaking_reasons"] == [
        "GET /a removed param 'p2' (in: query)",
        "GET /a removed response '404'",
        "removed endpoint GET /c",
        "removed endpoint POST /b",
    ]


def test_diff_pure_additions_are_not_breaking():
    old = _old_spec()
    new = json.loads(as_json(old))
    new["paths"]["/a"]["get"]["parameters"].append(
        {"name": "extra", "in": "header", "schema": {"type": "string"}},
    )
    new["paths"]["/a"]["get"]["responses"]["418"] = {"description": "teapot"}
    new["paths"]["/e"] = {
        "put": {"operationId": "putE", "responses": {"200": {"description": "ok"}, "404": {"description": "no"}}},
    }
    result = diff(as_json(new), as_json(old))
    assert result["breaking"] is False
    assert result["breaking_reasons"] == []
    assert result["removed"] == []
    assert result["added"] == [{"method": "PUT", "path": "/e"}]
    changed = result["changed"][0]
    assert changed["params"] == {"added": ["extra (in: header)"], "removed": []}
    assert changed["responses"] == {"added": ["418"], "removed": []}
    assert changed["changes"] == ["params.added", "responses.added"]


def test_diff_removed_param_alone_breaks():
    old = _old_spec()
    new = json.loads(as_json(old))
    new["paths"]["/b"]["post"]["parameters"] = []
    result = diff(as_json(new), as_json(old))
    assert result["breaking"] is True
    assert result["breaking_reasons"] == ["POST /b removed param 'q' (in: query)"]
    assert result["removed"] == []


def test_diff_removed_response_alone_breaks():
    old = _old_spec()
    new = json.loads(as_json(old))
    del new["paths"]["/c"]["get"]["responses"]["500"]
    result = diff(as_json(new), as_json(old))
    assert result["breaking"] is True
    assert result["breaking_reasons"] == ["GET /c removed response '500'"]


def test_diff_identical_and_metadata_only():
    old = _old_spec()
    same = json.loads(as_json(old))
    result = diff(as_json(same), as_json(old))
    assert result == {
        "added": [], "removed": [], "changed": [],
        "breaking": False, "breaking_reasons": [],
        "summary": {"added": 0, "removed": 0, "changed": 0},
    }

    # operationId/summary changes are visible but never breaking.
    new = json.loads(as_json(old))
    new["paths"]["/a"]["get"]["summary"] = "Renamed"
    new["paths"]["/a"]["get"]["operationId"] = "getARenamed"
    result = diff(as_json(new), as_json(old))
    assert result["breaking"] is False
    assert result["changed"][0]["changes"] == ["operation_id", "summary"]


def test_diff_across_formats():
    # Old in JSON spelling, new in YAML spelling — one drift surface.
    new_yaml = yaml.safe_dump(_old_spec(), sort_keys=False)
    result = diff(new_yaml, as_json(_old_spec()))
    assert result["summary"] == {"added": 0, "removed": 0, "changed": 0}
    assert result["breaking"] is False


# ------------------------------------------------------------------ #
# Strict validation — the error matrix
# ------------------------------------------------------------------ #

def test_error_invalid_mode():
    with pytest.raises(ValueError, match="mode must be one of"):
        TOOL.execute(mode="frobnicate", document=as_json(_mini()))
    with pytest.raises(ValueError, match="mode must be one of"):
        TOOL.execute(mode=None, document=as_json(_mini()))


def test_error_document_must_be_text():
    with pytest.raises(ValueError, match="must be the OpenAPI document text"):
        TOOL.execute(mode="lint", document=_mini())          # dict, not text
    with pytest.raises(ValueError, match="must be the OpenAPI document text"):
        TOOL.execute(mode="lint", document=None)


def test_error_document_too_long():
    with pytest.raises(ValueError, match="exceeds the .*-character cap"):
        TOOL.execute(mode="lint", document="x" * (TOOL.max_text + 1))
    with pytest.raises(ValueError, match="document_old exceeds"):
        TOOL.execute(
            mode="diff",
            document=as_json(_mini()),
            document_old="x" * (TOOL.max_text + 1),
        )


def test_error_diff_requires_document_old():
    with pytest.raises(ValueError, match="requires document_old"):
        TOOL.execute(mode="diff", document=as_json(_mini()))
    with pytest.raises(ValueError, match="requires document_old"):
        TOOL.execute(mode="diff", document=as_json(_mini()), document_old=42)


def test_error_unparseable_text():
    bad = '{"broken": [1, 2'   # invalid JSON AND invalid YAML (flow error)
    with pytest.raises(ValueError, match="neither valid JSON nor valid YAML"):
        TOOL.execute(mode="lint", document=bad)
    with pytest.raises(ValueError, match="document_old"):
        TOOL.execute(
            mode="diff",
            document=as_json(_mini()),
            document_old="key: [unclosed",
        )


def test_error_non_object_root():
    for bad in ("[1, 2, 3]", "42", '"a bare string"', "true", "", "   \n"):
        with pytest.raises(ValueError, match="must parse to an object"):
            TOOL.execute(mode="inventory", document=bad)
    with pytest.raises(ValueError, match="document_old must parse to an object"):
        TOOL.execute(mode="diff", document=as_json(_mini()), document_old="[1]")
