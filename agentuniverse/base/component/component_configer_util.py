# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 14:00
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_configer_util.py
import importlib
from typing import Type, Callable

from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.action.toolkit.toolkit_manager import ToolkitManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.memory.memory_compressor.memory_compressor_manager import MemoryCompressorManager
from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.agent.memory.memory_storage.memory_storage_manager import MemoryStorageManager
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.agent_serve.service_manager import ServiceManager
from agentuniverse.agent_serve.service_configer import ServiceConfiger
from agentuniverse.base.config.component_configer.configers.work_pattern_configer import WorkPatternConfiger
from agentuniverse.base.config.component_configer.configers.workflow_configer import WorkflowConfiger
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.config.component_configer.configers.knowledge_configer import KnowledgeConfiger
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.base.config.component_configer.configers.planner_configer import PlannerConfiger
from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.component_configer.configers.sqldb_wrapper_config import SQLDBWrapperConfiger
from agentuniverse.base.config.config_type_enum import ConfigTypeEnum
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.llm.llm_channel.llm_channel_manager import LLMChannelManager
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.workflow.workflow_manager import WorkflowManager
from agentuniverse.base.util.logging.log_sink.log_sink_manager import LogSinkManager
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser_manager import QueryParaphraserManager
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager


class ComponentConfigerUtil(object):
    """The ComponentConfigerUtil class, which is used to load and manage the component configuration."""

    __COMPONENT_CONFIGER_CLZ_MAP = {
        ComponentEnum.AGENT: AgentConfiger,
        ComponentEnum.KNOWLEDGE: KnowledgeConfiger,
        ComponentEnum.LLM: LLMConfiger,
        ComponentEnum.PLANNER: PlannerConfiger,
        ComponentEnum.TOOL: ToolConfiger,
        ComponentEnum.TOOLKIT: ComponentConfiger,
        ComponentEnum.MEMORY: MemoryConfiger,
        ComponentEnum.SERVICE: ServiceConfiger,
        ComponentEnum.PROMPT: PromptConfiger,
        ComponentEnum.SQLDB_WRAPPER: SQLDBWrapperConfiger,
        ComponentEnum.WORKFLOW: WorkflowConfiger,
        ComponentEnum.EMBEDDING: ComponentConfiger,
        ComponentEnum.DOC_PROCESSOR: ComponentConfiger,
        ComponentEnum.READER: ComponentConfiger,
        ComponentEnum.STORE: ComponentConfiger,
        ComponentEnum.RAG_ROUTER: ComponentConfiger,
        ComponentEnum.QUERY_PARAPHRASER: ComponentConfiger,
        ComponentEnum.MEMORY_COMPRESSOR: ComponentConfiger,
        ComponentEnum.MEMORY_STORAGE: ComponentConfiger,
        ComponentEnum.WORK_PATTERN: WorkPatternConfiger,
        ComponentEnum.LOG_SINK: ComponentConfiger,
        ComponentEnum.DEFAULT: ComponentConfiger,
        ComponentEnum.LLM_CHANNEL: ComponentConfiger
    }

    __COMPONENT_MANAGER_CLZ_MAP = {
        ComponentEnum.AGENT: AgentManager,
        ComponentEnum.KNOWLEDGE: KnowledgeManager,
        ComponentEnum.LLM: LLMManager,
        ComponentEnum.PLANNER: PlannerManager,
        ComponentEnum.TOOL: ToolManager,
        ComponentEnum.TOOLKIT: ToolkitManager,
        ComponentEnum.MEMORY: MemoryManager,
        ComponentEnum.SERVICE: ServiceManager,
        ComponentEnum.SQLDB_WRAPPER: SQLDBWrapperManager,
        ComponentEnum.PROMPT: PromptManager,
        ComponentEnum.WORKFLOW: WorkflowManager,
        ComponentEnum.EMBEDDING: EmbeddingManager,
        ComponentEnum.DOC_PROCESSOR: DocProcessorManager,
        ComponentEnum.READER: ReaderManager,
        ComponentEnum.STORE: StoreManager,
        ComponentEnum.RAG_ROUTER: RagRouterManager,
        ComponentEnum.QUERY_PARAPHRASER: QueryParaphraserManager,
        ComponentEnum.MEMORY_COMPRESSOR: MemoryCompressorManager,
        ComponentEnum.MEMORY_STORAGE: MemoryStorageManager,
        ComponentEnum.WORK_PATTERN: WorkPatternManager,
        ComponentEnum.LOG_SINK: LogSinkManager,
        ComponentEnum.LLM_CHANNEL: LLMChannelManager,
    }

    @classmethod
    def get_component_config_clz_by_type(cls, component_type_enum: ComponentEnum) -> \
            Type[ComponentConfiger | LLMConfiger]:
        """Get the ComponentConfiger object by the component type.
        Args:
            component_type_enum(ConfigTypeEnum): the component type
        Returns:
            ComponentConfiger: the sub object of ComponentConfiger
        """
        component_config_clz = cls.__COMPONENT_CONFIGER_CLZ_MAP.get(component_type_enum)
        if component_config_clz is None:
            raise Exception(f"Failed to get the ComponentConfiger class by the component type: {component_type_enum}")
        return component_config_clz

    @classmethod
    def get_component_object_clz_by_component_configer(cls, component_configer: ComponentConfiger) -> Callable:
        """Get the component object by the ComponentConfiger object.
        Args:
            component_configer(ComponentConfiger): the ComponentConfiger object
        Returns:
            object: the component object
        """
        if component_configer.meta_class:
            try:
                metadata_module = '.'.join(component_configer.meta_class.split('.')[:-1])
                metadata_class = component_configer.meta_class.split('.')[-1]
                module = importlib.import_module(metadata_module)
                clz = getattr(module, metadata_class)
                return clz
            except Exception as ex:
                LOGGER.error(f"Please check your config file, load configer module error! module name: {metadata_class},error info: {ex} ")
                raise ex
        else:
            try:
                module = importlib.import_module(component_configer.metadata_module)
                clz = getattr(module, component_configer.metadata_class)
                return clz
            except Exception as ex:
                LOGGER.error(f"Please check your config file, load configer module error! module name: {component_configer.metadata_module},error info: {ex} ")
                raise ex

    @classmethod
    def get_component_manager_clz_by_type(cls, component_type_enum: ComponentEnum) -> Callable:
        """Get the ComponentManager object by the component type.
        Args:
            component_type_enum(ConfigTypeEnum): the component type
        Returns:
            object: the ComponentManager object
        """
        return cls.__COMPONENT_MANAGER_CLZ_MAP.get(component_type_enum)
