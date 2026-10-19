# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/11/01 10:00
# @Author  : Yue Wang
# @FileName: test_plugin_util.py
"""Unit tests for the plugin_util module."""

import pytest

from agentuniverse_product.service.model.plugin_dto import PluginDTO
from agentuniverse_product.service.util.plugin_util import (
    assemble_plugin_product_config_data,
    parse_openapi_yaml_to_tool_bundle,
)

SERVERS = "openapi: 3.0.0\nservers:\n  - url: https://api.example.com\n"


class TestPluginUtil:
    """Tests for plugin_util helpers."""

    def test_assemble_plugin_product_config_data(self):
        """The assembled config dict mirrors the plugin dto fields."""
        plugin_dto = PluginDTO(id="plugin_001", nickname="demo", avatar="/a.png", description="a demo plugin")
        config = assemble_plugin_product_config_data(plugin_dto, tool_id_list=["tool_1", "tool_2"])

        assert config["id"] == "plugin_001"
        assert config["nickname"] == "demo"
        assert config["avatar"] == "/a.png"
        assert config["description"] == "a demo plugin"
        assert config["type"] == "PLUGIN"
        assert config["toolset"] == ["tool_1", "tool_2"]
        assert config["metadata"] == {
            "class": "PluginProduct",
            "module": "agentuniverse_product.base.plugin_product",
            "type": "PRODUCT",
        }
        assert config["openapi_desc"] == ""

    def test_invalid_openapi_yaml_raises(self):
        """A yaml document that evaluates to None raises an exception."""
        with pytest.raises(Exception, match="Invalid openapi yaml."):
            parse_openapi_yaml_to_tool_bundle("   \n")

    def test_openapi_without_servers_raises(self):
        """An openapi spec with an empty server list raises an exception."""
        with pytest.raises(Exception, match="No server found in the openapi yaml."):
            parse_openapi_yaml_to_tool_bundle("openapi: 3.0.0\nservers: []\npaths: {}\n")

    def test_empty_paths_return_no_bundles(self):
        """An openapi spec without paths yields no tool bundles."""
        assert parse_openapi_yaml_to_tool_bundle(SERVERS + "paths: {}\n") == []

    def test_interfaces_built_from_paths_and_methods(self):
        """Each http method of a path produces one bundle with url and method."""
        yaml_text = SERVERS + "paths:\n  /pets:\n    get:\n      operationId: listPets\n      responses:\n        '200':\n          description: OK\n    post:\n      responses:\n        '200':\n          description: OK\n"
        bundles = parse_openapi_yaml_to_tool_bundle(yaml_text)

        assert len(bundles) == 2
        assert [bundle["method"] for bundle in bundles] == ["get", "post"]
        assert all(bundle["url"] == "https://api.example.com/pets" for bundle in bundles)
        assert bundles[0]["operation"]["operationId"] == "listPets"

    def test_operation_id_generated_when_missing(self):
        """A missing operationId is derived from the cleaned path and method."""
        yaml_text = SERVERS + "paths:\n  /hello-world:\n    delete:\n      responses:\n        '204':\n          description: OK\n"
        bundles = parse_openapi_yaml_to_tool_bundle(yaml_text)

        assert bundles[0]["operation"]["operationId"] == "hello-world_delete"

    def test_special_char_path_falls_back_to_uuid(self):
        """A path made only of special characters gets a uuid based operation id."""
        yaml_text = SERVERS + "paths:\n  '/@#$%':\n    get:\n      responses:\n        '200':\n          description: OK\n"
        operation_id = parse_openapi_yaml_to_tool_bundle(yaml_text)[0]["operation"]["operationId"]

        assert operation_id.endswith("_get")
        assert len(operation_id) > 4

    def test_request_body_ref_is_resolved(self):
        """A $ref inside a request body schema is resolved from the spec root."""
        yaml_text = SERVERS + "paths:\n  /pets:\n    post:\n      requestBody:\n        content:\n          application/json:\n            schema:\n              $ref: '#/components/schemas/Pet'\n      responses:\n        '200':\n          description: OK\ncomponents:\n  schemas:\n    Pet:\n      type: object\n      properties:\n        name:\n          type: string\n"
        schema = parse_openapi_yaml_to_tool_bundle(yaml_text)[0]["operation"]["requestBody"]["content"]["application/json"]["schema"]

        assert schema["type"] == "object"
        assert schema["properties"]["name"]["type"] == "string"
