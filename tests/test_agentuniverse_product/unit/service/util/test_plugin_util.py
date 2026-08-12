from agentuniverse_product.service.model.plugin_dto import PluginDTO
from agentuniverse_product.service.util.plugin_util import (
    assemble_plugin_product_config_data,
)


def test_plugin_product_config_preserves_openapi_description():
    openapi_desc = """openapi: 3.0.0
servers:
  - url: https://example.com
paths: {}
"""
    plugin = PluginDTO(
        id="example_plugin",
        nickname="Example",
        openapi_desc=openapi_desc,
    )

    config = assemble_plugin_product_config_data(plugin, ["example_tool"])

    assert config["openapi_desc"] == openapi_desc
