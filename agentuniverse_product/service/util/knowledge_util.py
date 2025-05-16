# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/30 10:25
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge_util.py
import os

from typing import Dict

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent_serve.web.post_fork_queue import POST_FORK_QUEUE
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.knowledge_configer import KnowledgeConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO


def assemble_knowledge_product_config_data(knowledge_dto: KnowledgeDTO) -> Dict:
    """Assemble the knowledge product configuration data.

    Args:
        knowledge_dto (KnowledgeDTO): The knowledge DTO.

    Returns:
        Dict: The assembled knowledge product configuration data.
    """
    return {
        'id': knowledge_dto.id,
        'nickname': knowledge_dto.nickname,
        'avatar': knowledge_dto.avatar,
        'type': 'KNOWLEDGE',
        'metadata': {
            'class': 'AgentProduct',
            'module': 'agentuniverse_product.base.agent_product',
            'type': 'PRODUCT'
        }
    }


def assemble_knowledge_config(knowledge_dto: KnowledgeDTO) -> Dict:
    """Assemble the knowledge configuration data.

    Args:
        knowledge_dto (KnowledgeDTO): The knowledge DTO object containing the knowledge parameters.

    Returns:
        Dict: The assembled knowledge configuration data.
    """
    return {
        'name': knowledge_dto.id,
        'description': knowledge_dto.description,
        'stores': [],
        'insert_processors': ["recursive_character_text_splitter"],
        'readers': {
            'pdf': "default_pdf_reader",
            'docx': "default_docx_reader",
            'pptx': "default_pptx_reader",
            'txt': "default_txt_reader",
        },
        'metadata': {
            'type': 'KNOWLEDGE',
            'module': 'agentuniverse.agent.action.knowledge.knowledge',
            'class': 'Knowledge',
        }
    }


def register_knowledge(file_path: str):
    """Register the knowledge instance to the knowledge manager.

    Args:
        file_path (str): The path to the knowledge configuration file.
    """
    absolute_file_path = os.path.abspath(file_path)
    configer = Configer(path=absolute_file_path).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    knowledge_configer: KnowledgeConfiger = KnowledgeConfiger().load_by_configer(component_configer.configer)
    component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(knowledge_configer)
    component_instance: Knowledge = component_clz().initialize_by_component_configer(knowledge_configer)
    component_instance.component_config_path = component_configer.configer.path
    KnowledgeManager().register(component_instance.get_instance_code(), component_instance)


def unregister_knowledge(file_path: str):
    """Unregister the knowledge instance from the knowledge manager.

    Args:
        file_path (str): The path to the knowledge configuration file.
    """
    absolute_file_path = os.path.abspath(file_path)
    configer = Configer(path=absolute_file_path).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    knowledge_configer: KnowledgeConfiger = KnowledgeConfiger().load_by_configer(component_configer.configer)
    component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(knowledge_configer)
    component_instance: Knowledge = component_clz().initialize_by_component_configer(knowledge_configer)
    KnowledgeManager().unregister(component_instance.get_instance_code())


def register_store(file_path: str):
    """Register the store instance to the store manager.

    Args:
        file_path (str): The path to the store configuration file.
    """
    absolute_file_path = os.path.abspath(file_path)
    configer = Configer(path=absolute_file_path).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(component_configer)
    component_instance = component_clz().initialize_by_component_configer(component_configer)
    component_instance.component_config_path = component_configer.configer.path
    StoreManager().register(component_instance.get_instance_code(), component_instance)
    for _func, args, kwargs in POST_FORK_QUEUE[-2:]:
        _func(*args, **kwargs)
