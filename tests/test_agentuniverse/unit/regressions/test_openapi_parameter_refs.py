"""Regression tests for OpenAPI parameter reference resolution."""

import pytest

from agentuniverse_product.service.util.plugin_util import parse_openapi_yaml_to_tool_bundle

OPENAPI_YAML = """
openapi: 3.0.0
servers:
  - url: https://api.example.com
paths:
  /users/{userId}:
    parameters:
      - $ref: '#/components/parameters/UserId'
    get:
      operationId: getUser
      parameters:
        - name: verbose
          in: query
          required: true
          schema:
            type: boolean
components:
  parameters:
    UserId:
      name: userId
      in: path
      required: true
      schema:
        type: string
"""


def test_parameter_refs_are_resolved():
    bundles = parse_openapi_yaml_to_tool_bundle(OPENAPI_YAML)
    assert len(bundles) == 1
    parameters = bundles[0]["operation"]["parameters"]
    names = [p.get("name") for p in parameters]
    assert "userId" in names
    assert "verbose" in names
    user_id = next(p for p in parameters if p.get("name") == "userId")
    assert user_id["in"] == "path"
    assert user_id["required"] is True


def test_malformed_ref_raises_clear_error():
    yaml = """
openapi: 3.0.0
servers:
  - url: https://api.example.com
paths:
  /x:
    get:
      operationId: getX
      parameters:
        - $ref: '#/components/parameters/Missing'
components:
  parameters: {}
"""
    with pytest.raises(Exception, match="Unresolved OpenAPI reference"):
        parse_openapi_yaml_to_tool_bundle(yaml)
