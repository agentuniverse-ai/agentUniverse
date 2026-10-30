from agentuniverse_product.service.util.plugin_util import parse_openapi_yaml_to_tool_bundle
from agentuniverse_product.service.util.tool_util import parse_tool_input


def test_path_item_parameters_are_inherited_by_operations():
    bundles = parse_openapi_yaml_to_tool_bundle(
        """
openapi: 3.0.0
servers: [{url: https://example.com}]
paths:
  /users/{user_id}:
    parameters:
      - in: path
        name: user_id
        required: true
        schema: {type: string}
    get:
      responses: {'200': {description: ok}}
"""
    )

    assert parse_tool_input(bundles[0]) == ["user_id"]
    assert bundles[0]["operation"]["parameters"][0]["in"] == "path"


def test_operation_parameters_override_matching_path_item_parameters():
    bundles = parse_openapi_yaml_to_tool_bundle(
        """
openapi: 3.0.0
servers: [{url: https://example.com}]
paths:
  /search:
    parameters:
      - in: query
        name: locale
        required: false
        schema: {type: string, default: en}
      - in: header
        name: X-Tenant
        required: true
        schema: {type: string}
    get:
      parameters:
        - in: query
          name: locale
          required: true
          schema: {type: string}
      responses: {'200': {description: ok}}
"""
    )

    parameters = bundles[0]["operation"]["parameters"]

    assert [(item["name"], item["in"]) for item in parameters] == [
        ("X-Tenant", "header"),
        ("locale", "query"),
    ]
    assert parse_tool_input(bundles[0]) == ["X-Tenant", "locale"]
