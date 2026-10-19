# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: test_knowledge_util.py
"""Unit tests for the knowledge_util helpers in agentuniverse_product."""

from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO
from agentuniverse_product.service.util.knowledge_util import (
    assemble_knowledge_config,
    assemble_knowledge_product_config_data,
)


def sample_knowledge_dto(**overrides):
    data = dict(id='demo_knowledge', nickname='Demo knowledge',
                description='A demo knowledge base', avatar='avatar.png')
    data.update(overrides)
    return KnowledgeDTO(**data)


def test_assemble_knowledge_product_config_data():
    config = assemble_knowledge_product_config_data(sample_knowledge_dto())
    assert config['id'] == 'demo_knowledge'
    assert config['nickname'] == 'Demo knowledge'
    assert config['avatar'] == 'avatar.png'
    assert config['type'] == 'KNOWLEDGE'
    assert config['metadata'] == {'class': 'AgentProduct',
                                  'module': 'agentuniverse_product.base.agent_product',
                                  'type': 'PRODUCT'}


def test_assemble_knowledge_product_config_data_with_empty_dto():
    config = assemble_knowledge_product_config_data(KnowledgeDTO())
    assert config['id'] == ''
    assert config['nickname'] == ''
    assert config['type'] == 'KNOWLEDGE'


def test_assemble_knowledge_config():
    config = assemble_knowledge_config(sample_knowledge_dto())
    assert config['name'] == 'demo_knowledge'
    assert config['description'] == 'A demo knowledge base'
    assert config['stores'] == []
    assert config['insert_processors'] == ['recursive_character_text_splitter']
    assert config['readers'] == {'pdf': 'default_pdf_reader', 'docx': 'default_docx_reader',
                                 'pptx': 'default_pptx_reader', 'txt': 'default_txt_reader'}
    assert config['metadata'] == {'type': 'KNOWLEDGE',
                                  'module': 'agentuniverse.agent.action.knowledge.knowledge',
                                  'class': 'Knowledge'}


def test_assemble_knowledge_config_defaults_for_missing_fields():
    config = assemble_knowledge_config(KnowledgeDTO(id='knowledge_a'))
    assert config['name'] == 'knowledge_a'
    assert config['description'] == ''
    assert config['stores'] == []
