"""Regression tests for actionable plugin OpenAPI parsing errors."""

import re

import pytest
from yaml import YAMLError, safe_dump

from agentuniverse_product.service.util.plugin_util import parse_openapi_yaml_to_tool_bundle


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


def test_malformed_yaml_preserves_the_parser_cause_and_location():
    with pytest.raises(ValueError, match="Invalid OpenAPI YAML syntax") as raised:
        parse_openapi_yaml_to_tool_bundle("servers:\n  - url: [\n")

    cause = raised.value.__cause__
    assert isinstance(cause, YAMLError)
    assert str(cause) in str(raised.value)
    assert "line" in str(raised.value)
    assert "column" in str(raised.value)


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
def test_valid_openapi_preserves_tool_generation(server_url):
    document = {
        "servers": [{"url": server_url}],
        "paths": {
            "/pets": {
                "get": {"operationId": "listPets"},
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Pet"},
                            }
                        }
                    }
                },
            },
        },
        "components": {"schemas": {"Pet": {"type": "object"}}},
    }

    tools = parse_openapi_yaml_to_tool_bundle(safe_dump(document))

    assert len(tools) == 2
    assert tools[0] == {
        "path": "/pets",
        "method": "get",
        "operation": {"operationId": "listPets"},
        "url": server_url + "/pets",
    }
    assert tools[1]["operation"]["operationId"] == "pets_post"
    assert tools[1]["operation"]["requestBody"]["content"]["application/json"]["schema"] == {"type": "object"}
