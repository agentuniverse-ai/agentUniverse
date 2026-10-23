# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/27 23:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: plugin_util.py
import re
from collections.abc import Mapping
from typing import Dict, List
import uuid

from yaml import YAMLError, safe_load

from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.plugin_dto import PluginDTO
from agentuniverse_product.service.util.common_util import validate_component_id


class OpenAPIParseError(ValueError):
    """Raised when a plugin OpenAPI YAML document cannot be parsed."""


_OPENAPI_ERROR_MESSAGES = {
    'empty': 'Invalid openapi yaml.',
    'root': 'OpenAPI YAML root must be a mapping.',
    'servers_missing': "OpenAPI field 'servers' is required; add a server entry with a 'url'.",
    'servers_type': "OpenAPI field 'servers' must be a list of server mappings.",
    'servers_empty': 'No server found in the openapi yaml.',
    'server_type': "OpenAPI field 'servers[0]' must be a mapping containing a 'url'.",
    'url_missing': "OpenAPI field 'servers[0].url' is required; add a server URL.",
    'url_type': "OpenAPI field 'servers[0].url' must be a non-empty string.",
    'paths_missing': "OpenAPI field 'paths' is required; use a mapping of endpoint paths.",
    'paths_type': "OpenAPI field 'paths' must be a mapping of endpoint paths.",
}


def validate_create_plugin_parameters(plugin_dto: PluginDTO) -> None:
    """Validate the parameters for creating a plugin instance.

    Args:
        plugin_dto (PluginDTO): The plugin DTO object containing the plugin parameters.
    """
    validate_component_id(plugin_dto.id)
    plugin = ProductManager().get_instance_obj(plugin_dto.id, new_instance=False)
    if plugin:
        raise ValueError("Plugin instance corresponding to the plugin id already exists.")
    if plugin_dto.openapi_desc is None:
        raise ValueError("The openapi_desc in plugin cannot be None.")


def assemble_plugin_product_config_data(plugin_dto: PluginDTO, tool_id_list: List[str]) -> Dict:
    """Assemble the plugin product configuration data.

    Args:
        plugin_dto (PluginDTO): The plugin DTO object containing the plugin parameters.
        tool_id_list (List[str]): The list of tool IDs associated with the plugin.

    Returns:
        Dict: The assembled plugin product configuration data.
    """
    return {
        'id': plugin_dto.id,
        'nickname': plugin_dto.nickname,
        'avatar': plugin_dto.avatar,
        'description': plugin_dto.description,
        'type': 'PLUGIN',
        'toolset': tool_id_list,
        'metadata': {
            'class': 'PluginProduct',
            'module': 'agentuniverse_product.base.plugin_product',
            'type': 'PRODUCT'
        },
        'openapi_desc': ''
    }


def _load_openapi_yaml(yaml: str) -> Mapping:
    """Load an OpenAPI YAML document and validate its root value."""
    try:
        openapi = safe_load(yaml)
    except YAMLError as error:
        location = ''
        problem_mark = getattr(error, 'problem_mark', None)
        if problem_mark is not None:
            # YAML marks are zero-based; show the user one-based line and column numbers.
            location = f' at line {problem_mark.line + 1}, column {problem_mark.column + 1}'
        message = f'Invalid OpenAPI YAML syntax{location}: {error}'
        raise OpenAPIParseError(message) from error

    if openapi is None:
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['empty'])
    if not isinstance(openapi, Mapping):
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['root'])
    return openapi


def _get_openapi_server_url(openapi: Mapping) -> str:
    """Return the first OpenAPI server URL after validating its structure."""
    if 'servers' not in openapi:
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['servers_missing'])

    servers = openapi['servers']
    if not isinstance(servers, list):
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['servers_type'])
    if not servers:
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['servers_empty'])
    if not isinstance(servers[0], Mapping):
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['server_type'])
    if 'url' not in servers[0]:
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['url_missing'])

    server_url = servers[0]['url']
    if not isinstance(server_url, str) or not server_url.strip():
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['url_type'])
    return server_url


def _get_openapi_paths(openapi: Mapping) -> Mapping:
    """Return the OpenAPI paths mapping after validating its structure."""
    if 'paths' not in openapi:
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['paths_missing'])

    paths = openapi['paths']
    if not isinstance(paths, Mapping):
        raise OpenAPIParseError(_OPENAPI_ERROR_MESSAGES['paths_type'])
    return paths


def parse_openapi_yaml_to_tool_bundle(yaml: str) -> list:
    """Parse the openapi schema yaml to tool bundles.

    Args:
        yaml (str): The openapi schema yaml string.

    Returns:
        list: The list of tool bundles.
    """

    openapi = _load_openapi_yaml(yaml)
    server_url = _get_openapi_server_url(openapi)
    paths = _get_openapi_paths(openapi)

    # list all interfaces
    interfaces = []
    for path, path_item in paths.items():
        methods = ['get', 'post', 'put', 'delete',
                   'patch', 'head', 'options', 'trace']
        for method in methods:
            if method in path_item:
                interfaces.append({
                    'path': path,
                    'method': method,
                    'operation': path_item[method],
                    'url': server_url + path,
                })
    # create tool bundle
    for interface in interfaces:
        # check if there is a request body
        if 'requestBody' in interface['operation']:
            request_body = interface['operation']['requestBody']
            if 'content' in request_body:
                for content_type, content in request_body['content'].items():
                    # if there is a reference, get the reference and overwrite the content
                    if 'schema' not in content:
                        continue

                    if '$ref' in content['schema']:
                        # get the reference
                        root = openapi
                        reference = content['schema']['$ref'].split(
                            '/')[1:]
                        for ref in reference:
                            root = root[ref]
                        # overwrite the content
                        interface['operation']['requestBody']['content'][content_type]['schema'] = root

        if 'operationId' not in interface['operation']:
            # remove special characters like / to ensure the operation id is valid ^[a-zA-Z0-9_-]{1,64}$
            path = interface['path']
            if interface['path'].startswith('/'):
                path = interface['path'][1:]
            path = re.sub(r'[^a-zA-Z0-9_-]', '', path)
            if not path:
                path = str(uuid.uuid4())

            interface['operation']['operationId'] = f'{path}_{interface["method"]}'

    return interfaces
