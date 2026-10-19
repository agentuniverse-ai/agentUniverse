# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/27 23:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: plugin_util.py
import re
from typing import Dict, List
import uuid

from yaml import safe_load
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.plugin_dto import PluginDTO


def validate_create_plugin_parameters(plugin_dto: PluginDTO) -> None:
    """Validate the parameters for creating a plugin instance.

    Args:
        plugin_dto (PluginDTO): The plugin DTO object containing the plugin parameters.
    """
    if plugin_dto.id is None:
        raise ValueError("Plugin id cannot be None.")
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
        'openapi_desc': plugin_dto.openapi_desc or ''
    }


def parse_openapi_yaml_to_tool_bundle(yaml: str) -> list:
    """Parse the openapi schema yaml to tool bundles.

    Args:
        yaml (str): The openapi schema yaml string.

    Returns:
        list: The list of tool bundles.
    """

    openapi: dict = safe_load(yaml)
    if openapi is None:
        raise Exception('Invalid openapi yaml.')

    if len(openapi['servers']) == 0:
        raise Exception('No server found in the openapi yaml.')

    server_url = str(openapi['servers'][0]['url'])

    # list all interfaces
    interfaces = []
    for path, path_item in openapi['paths'].items():
        methods = ['get', 'post', 'put', 'delete',
                   'patch', 'head', 'options', 'trace']
        path_parameters = path_item.get('parameters', [])
        for method in methods:
            if method in path_item:
                operation = dict(path_item[method])
                operation_parameters = operation.get('parameters', [])
                merged = _merge_parameters(path_parameters, operation_parameters)
                operation['parameters'] = _resolve_parameter_refs(openapi, merged)
                interfaces.append({
                    'path': path,
                    'method': method,
                    'operation': operation,
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


def _resolve_ref(openapi: dict, ref: str) -> dict:
    """Resolve a local OpenAPI $ref against the document root.

    Args:
        openapi (dict): The OpenAPI document root.
        ref (str): The $ref string, expected to start with '#/'.

    Returns:
        dict: The referenced object.

    Raises:
        Exception: If the reference is malformed or points to a missing node.
    """
    if not ref.startswith('#/'):
        raise Exception(f'Only local OpenAPI references are supported: {ref}')
    root = openapi
    for part in ref[2:].split('/'):
        if part not in root:
            raise Exception(f'Unresolved OpenAPI reference: {ref}')
        root = root[part]
    return root


def _resolve_parameter_refs(openapi: dict, parameters: list) -> list:
    """Resolve $ref entries inside an OpenAPI parameter list.

    Args:
        openapi (dict): The OpenAPI document root.
        parameters (list): The parameter list.

    Returns:
        list: A new list with references resolved to concrete parameter objects.
    """
    resolved = []
    for parameter in parameters:
        if '$ref' in parameter:
            resolved.append(_resolve_ref(openapi, parameter['$ref']))
        else:
            resolved.append(parameter)
    return resolved


def _merge_parameters(path_parameters: list, operation_parameters: list) -> list:
    """Merge Path Item parameters with operation parameters without mutating inputs.

    Args:
        path_parameters (list): Parameters declared at the Path Item level.
        operation_parameters (list): Parameters declared at the operation level.

    Returns:
        list: The merged parameter list.
    """
    return list(path_parameters) + list(operation_parameters)
