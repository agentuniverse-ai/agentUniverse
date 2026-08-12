import json
from unittest.mock import patch

from agentuniverse.agent.action.tool.api_tool import APITool
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse_product.service.util.plugin_util import parse_openapi_yaml_to_tool_bundle
from agentuniverse_product.service.util.tool_util import parse_tool_input


OPENAPI_DOCUMENT = """
openapi: 3.0.0
servers:
  - url: https://example.com
paths:
  /items:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [name]
              properties:
                name:
                  type: string
                count:
                  type: integer
      responses:
        '200':
          description: ok
"""


class _Response:
    text = "ok"


def test_product_plugin_exposes_required_request_body_properties():
    tool_bundle = parse_openapi_yaml_to_tool_bundle(OPENAPI_DOCUMENT)[0]

    assert parse_tool_input(tool_bundle) == ["name"]


def test_api_tool_sends_operation_request_body():
    tool_bundle = parse_openapi_yaml_to_tool_bundle(OPENAPI_DOCUMENT)[0]
    tool = APITool(name="create_item", openapi_spec=tool_bundle, input_keys=["name"])

    with patch(
        "agentuniverse.agent.action.tool.api_tool.ssrf_proxy.post",
        return_value=_Response(),
    ) as request:
        tool.execute(ToolInput(params={"name": "demo", "count": "2"}))

    assert request.call_args.kwargs["headers"] == {"Content-Type": "application/json"}
    assert json.loads(request.call_args.kwargs["data"]) == {"name": "demo", "count": 2}
