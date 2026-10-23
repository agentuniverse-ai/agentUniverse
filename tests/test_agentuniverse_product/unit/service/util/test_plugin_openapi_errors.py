"""Regression tests for actionable plugin OpenAPI parsing errors."""

import re

import pytest
from yaml import YAMLError, safe_dump

from agentuniverse_product.service.util.plugin_util import OpenAPIParseError, parse_openapi_yaml_to_tool_bundle


@pytest.mark.parametrize(
    ("document", "message"),
    [
        ([], "OpenAPI YAML root must be a mapping."),
        (42, "OpenAPI YAML root must be a mapping."),
        ("text", "OpenAPI YAML root must be a mapping."),
        ({"paths": {}}, "OpenAPI field 'servers' is required; add a server entry with a 'url'."),
        ({"servers": None}, "OpenAPI field 'servers' must be a list of server mappings."),
        ({"servers": {}}, "OpenAPI field 'servers' must be a list of server mappings."),
        ({"servers": "https://example.com"}, "OpenAPI field 'servers' must be a list of server mappings."),
        ({"servers": [None]}, "OpenAPI field 'servers[0]' must be a mapping containing a 'url'."),
        ({"servers": ["https://example.com"]}, "OpenAPI field 'servers[0]' must be a mapping containing a 'url'."),
        ({"servers": [{}]}, "OpenAPI field 'servers[0].url' is required; add a server URL."),
        ({"servers": [{"url": None}]}, "OpenAPI field 'servers[0].url' must be a non-empty string."),
        ({"servers": [{"url": 123}]}, "OpenAPI field 'servers[0].url' must be a non-empty string."),
        ({"servers": [{"url": ""}]}, "OpenAPI field 'servers[0].url' must be a non-empty string."),
        ({"servers": [{"url": "  "}]}, "OpenAPI field 'servers[0].url' must be a non-empty string."),
        ({"servers": [{"url": "/api"}]}, "OpenAPI field 'paths' is required; use a mapping of endpoint paths."),
        (
            {"servers": [{"url": "/api"}], "paths": None},
            "OpenAPI field 'paths' must be a mapping of endpoint paths.",
        ),
        (
            {"servers": [{"url": "/api"}], "paths": []},
            "OpenAPI field 'paths' must be a mapping of endpoint paths.",
        ),
    ],
    ids=[
        "root-list",
        "root-number",
        "root-string",
        "servers-missing",
        "servers-null",
        "servers-mapping",
        "servers-string",
        "server-null",
        "server-string",
        "url-missing",
        "url-null",
        "url-number",
        "url-empty",
        "url-whitespace",
        "paths-missing",
        "paths-null",
        "paths-list",
    ],
)
def test_invalid_openapi_structure_reports_the_field(document, message):
    with pytest.raises(ValueError, match=re.escape(message)):
        parse_openapi_yaml_to_tool_bundle(safe_dump(document))


@pytest.mark.parametrize(
    ("document", "line", "column"),
    [
        ("servers:\n  - url: ]\n", 2, 10),
        ("servers:\n  - url: [\n", 3, 1),
        ("servers:\n\t- url: https://example.com\n", 2, 1),
    ],
    ids=["unexpected-token", "unexpected-end", "invalid-indentation"],
)
def test_malformed_yaml_preserves_the_parser_cause_and_location(document, line, column):
    with pytest.raises(OpenAPIParseError, match="Invalid OpenAPI YAML syntax") as raised:
        parse_openapi_yaml_to_tool_bundle(document)

    cause = raised.value.__cause__
    assert isinstance(cause, YAMLError)
    assert str(cause) in str(raised.value)
    assert str(raised.value).startswith(f"Invalid OpenAPI YAML syntax at line {line}, column {column}:")


def test_yaml_error_without_a_location_preserves_the_parser_cause(monkeypatch):
    cause = YAMLError("synthetic parser failure")

    def fail_to_load(_document):
        raise cause

    monkeypatch.setattr("agentuniverse_product.service.util.plugin_util.safe_load", fail_to_load)

    with pytest.raises(OpenAPIParseError) as raised:
        parse_openapi_yaml_to_tool_bundle("servers: [{url: /api}]\npaths: {}\n")

    assert str(raised.value) == "Invalid OpenAPI YAML syntax: synthetic parser failure"
    assert raised.value.__cause__ is cause


@pytest.mark.parametrize("document", ["", "# Empty document\n"])
def test_empty_yaml_preserves_the_existing_message(document):
    with pytest.raises(Exception, match=re.escape("Invalid openapi yaml.")):
        parse_openapi_yaml_to_tool_bundle(document)


def test_empty_servers_preserves_the_existing_message():
    with pytest.raises(Exception, match=re.escape("No server found in the openapi yaml.")):
        parse_openapi_yaml_to_tool_bundle("servers: []\npaths: {}\n")


def test_empty_paths_still_returns_no_tools():
    assert parse_openapi_yaml_to_tool_bundle("servers: [{url: /api}]\npaths: {}\n") == []


@pytest.mark.parametrize("server_url", ["https://api.example.com", "/api", "https://{tenant}.example.com"])
def test_valid_openapi_round_trip_assembles_complete_tool_bundles(server_url):
    """Parse a valid OpenAPI document into complete GET and POST tool bundles."""
    server = {"url": server_url}
    if "{tenant}" in server_url:
        server["variables"] = {"tenant": {"default": "demo"}}

    document = {
        "openapi": "3.0.3",
        "info": {"title": "Pet API", "version": "1.0.0"},
        "servers": [server],
        "paths": {
            "/pets": {
                "get": {
                    "operationId": "listPets",
                    "parameters": [
                        {"name": "limit", "in": "query", "schema": {"type": "integer"}},
                    ],
                    "responses": {"200": {"description": "A list of pets"}},
                },
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Pet"},
                            }
                        }
                    },
                    "responses": {"201": {"description": "Pet created"}},
                },
            },
        },
        "components": {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {"name": {"type": "string"}},
                },
            },
        },
    }

    tools = parse_openapi_yaml_to_tool_bundle(safe_dump(document))

    assert tools == [
        {
            "path": "/pets",
            "method": "get",
            "operation": {
                "operationId": "listPets",
                "parameters": [
                    {"name": "limit", "in": "query", "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "A list of pets"}},
            },
            "url": server_url + "/pets",
        },
        {
            "path": "/pets",
            "method": "post",
            "operation": {
                "operationId": "pets_post",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {"name": {"type": "string"}},
                            },
                        },
                    },
                },
                "responses": {"201": {"description": "Pet created"}},
            },
            "url": server_url + "/pets",
        },
    ]
