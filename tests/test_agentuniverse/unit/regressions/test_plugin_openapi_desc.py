"""Regression tests for plugin OpenAPI description persistence."""

from agentuniverse_product.service.model.plugin_dto import PluginDTO
from agentuniverse_product.service.util.plugin_util import assemble_plugin_product_config_data


def test_openapi_desc_is_persisted_in_product_config():
    dto = PluginDTO(
        id="plugin_id",
        nickname="nick",
        avatar="avatar",
        description="desc",
        openapi_desc="openapi: 3.0.0\ninfo: {}\npaths: {}",
    )
    config = assemble_plugin_product_config_data(dto, tool_id_list=["t1"])
    assert config["openapi_desc"] == dto.openapi_desc


def test_openapi_desc_none_falls_back_to_empty():
    dto = PluginDTO(id="plugin_id", nickname="nick", avatar="avatar", description="desc", openapi_desc=None)
    config = assemble_plugin_product_config_data(dto, tool_id_list=["t1"])
    assert config["openapi_desc"] == ""
