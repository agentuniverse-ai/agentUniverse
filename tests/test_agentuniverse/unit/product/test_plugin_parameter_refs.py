import pytest

from agentuniverse_product.service.util.plugin_util import parse_openapi_yaml_to_tool_bundle
from agentuniverse_product.service.util.tool_util import parse_tool_input


def test_operation_parameter_references_are_resolved():
    bundles = parse_openapi_yaml_to_tool_bundle(
        """
openapi: 3.0.0
servers: [{url: https://example.com}]
components:
  parameters:
    UserId:
      in: path
      name: user_id
      required: true
      schema: {type: string}
paths:
  /users/{user_id}:
    get:
      parameters:
        - $ref: '#/components/parameters/UserId'
      responses: {'200': {description: ok}}
"""
    )

    assert bundles[0]["operation"]["parameters"] == [
        {
            "in": "path",
            "name": "user_id",
            "required": True,
            "schema": {"type": "string"},
        }
    ]
    assert parse_tool_input(bundles[0]) == ["user_id"]


def test_invalid_local_parameter_reference_has_clear_error():
    with pytest.raises(ValueError, match="Invalid local OpenAPI reference"):
        parse_openapi_yaml_to_tool_bundle(
            """
openapi: 3.0.0
servers: [{url: https://example.com}]
paths:
  /users:
    get:
      parameters:
        - $ref: '#/components/parameters/Missing'
      responses: {'200': {description: ok}}
"""
        )
