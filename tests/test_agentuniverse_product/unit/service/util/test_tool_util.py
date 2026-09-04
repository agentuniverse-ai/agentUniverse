# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: test_tool_util.py
"""Unit tests for the tool_util helpers in agentuniverse_product."""

from unittest.mock import patch

import pytest

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse_product.service.model.tool_dto import ToolDTO
from agentuniverse_product.service.util.tool_util import (
    assemble_api_tool_config_data,
    assemble_tool_product_config_data,
    parse_tool_input,
    validate_create_api_tool_parameters,
)


def sample_tool_dto(**overrides):
    data = dict(id='demo_tool', nickname='Demo tool', avatar='avatar.png',
                description='A demo tool', parameters=['query', 'page'],
                openapi_schema={'openapi': '3.0.0'})
    data.update(overrides)
    return ToolDTO(**data)


def patch_tool_lookup(result):
    return patch.object(ToolManager(), 'get_instance_obj', return_value=result)


def test_assemble_tool_product_config_data():
    config = assemble_tool_product_config_data(sample_tool_dto())
    assert config['id'] == 'demo_tool'
    assert config['nickname'] == 'Demo tool'
    assert config['avatar'] == 'avatar.png'
    assert config['type'] == 'TOOL'
    assert config['metadata'] == {'class': 'Product',
                                  'module': 'agentuniverse_product.base.product',
                                  'type': 'PRODUCT'}


def test_assemble_api_tool_config_data():
    config = assemble_api_tool_config_data(sample_tool_dto())
    assert config['name'] == 'demo_tool'
    assert config['description'] == 'A demo tool'
    assert config['tool_type'] == 'api'
    assert config['input_keys'] == ['query', 'page']
    assert config['openapi_spec'] == {'openapi': '3.0.0'}
    assert config['metadata'] == {'class': 'APITool',
                                  'module': 'agentuniverse.agent.action.tool.api_tool',
                                  'type': 'TOOL'}


def test_validate_ok_when_no_existing_tool():
    with patch_tool_lookup(None):
        validate_create_api_tool_parameters(sample_tool_dto())


def test_validate_raises_when_tool_exists():
    with patch_tool_lookup(object()):
        with pytest.raises(ValueError, match='already exists'):
            validate_create_api_tool_parameters(sample_tool_dto())


def test_validate_raises_when_openapi_missing():
    tool_dto = sample_tool_dto(openapi_schema=None)
    with patch_tool_lookup(None):
        with pytest.raises(ValueError, match='openapi_schema'):
            validate_create_api_tool_parameters(tool_dto)


def test_parse_tool_input_keeps_required_parameters():
    openapi = {'operation': {'parameters': [
        {'name': 'query', 'required': True},
        {'name': 'page', 'required': False},
    ]}}
    assert parse_tool_input(openapi) == ['query']


def test_parse_tool_input_empty_without_parameters():
    assert parse_tool_input({'operation': {}}) == []
