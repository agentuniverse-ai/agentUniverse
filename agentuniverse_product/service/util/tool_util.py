# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/27 23:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool_util.py
import os
from typing import Dict

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse_product.service.model.tool_dto import ToolDTO
from agentuniverse_product.service.util.common_util import validate_component_id


def validate_create_api_tool_parameters(tool_dto: ToolDTO) -> None:
    """Validate the parameters for creating an api tool instance.

    Args :
        tool_dto (ToolDTO): The tool DTO object containing the tool parameters.
    """
    validate_component_id(tool_dto.id)
    tool = ToolManager().get_instance_obj(tool_dto.id)
    if tool:
        raise ValueError(f"Tool instance corresponding to the tool id already exists. {tool_dto.id}")
    if tool_dto.openapi_schema is None:
        raise ValueError("The openapi_schema in tool cannot be None.")


def assemble_tool_product_config_data(tool_dto: ToolDTO) -> Dict:
    """Assemble the tool product configuration data.

    Args :
        tool_dto (ToolDTO): The tool DTO object containing the tool parameters.
    """
    return {
        'id': tool_dto.id,
        'nickname': tool_dto.nickname,
        'avatar': tool_dto.avatar,
        'type': 'TOOL',
        'metadata': {
            'class': 'Product',
            'module': 'agentuniverse_product.base.product',
            'type': 'PRODUCT'
        },
    }


def assemble_api_tool_config_data(tool_dto: ToolDTO) -> Dict:
    """Assemble the api tool configuration data.

    Args :
        tool_dto (ToolDTO): The tool DTO object containing the tool parameters.

    Returns:
        Dict: The assembled api tool configuration data.
    """
    tool_config_data = {
        'name': tool_dto.id,
        'description': tool_dto.description,
        'tool_type': 'api',
        'input_keys': tool_dto.parameters,
        'openapi_spec': tool_dto.openapi_schema
    }
    metadata_class = 'APITool'
    metadata_api_tool_path = 'api_tool'

    tool_config_data['metadata'] = {
        'class': metadata_class,
        'module': f'agentuniverse.agent.action.tool.{metadata_api_tool_path}',
        'type': 'TOOL'
    }
    return tool_config_data


def register_tool(file_path: str):
    """Register a tool instance to the tool manager.

    Args :
        file_path (str): The path to the tool configuration file.
    """
    absolute_file_path = os.path.abspath(file_path)
    configer = Configer(path=absolute_file_path).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    tool_configer: ToolConfiger = ToolConfiger().load_by_configer(component_configer.configer)
    component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(tool_configer)
    component_instance: Tool = component_clz().initialize_by_component_configer(tool_configer)
    component_instance.component_config_path = component_configer.configer.path
    ToolManager().register(component_instance.get_instance_code(), component_instance)


def parse_tool_input(openapi: dict) -> list[str]:
    """Parse the tool input from the openapi schema.

    Args:
        openapi (dict): The openapi schema dictionary.

    Returns:
        list[str]: The list of tool input.
    """
    # convert parameters
    parameters = []
    operation = openapi['operation']
    for parameter in operation.get('parameters', []):
        if parameter.get('required'):
            parameters.append(parameter['name'])

    request_body = operation.get('requestBody', {})
    for content in request_body.get('content', {}).values():
        schema = content.get('schema', {})
        parameters.extend(schema.get('required', []))
        break
    return parameters
