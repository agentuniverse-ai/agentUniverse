# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import importlib
# @Time    : 2024/3/12 16:17
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: app_configer.py
from typing import Optional, Dict, Any

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.custom_configer.default_llm_configer import DefaultLLMConfiger


class AppConfiger(object):
    """The AppConfiger class, which is used to load and manage the application configuration."""

    def __init__(self):
        """Initialize the AppConfiger."""
        self.__configer: Optional[Configer] = None
        self.__base_info_appname: Optional[str] = None
        self.__core_default_package_list: Optional[list[str]] = None
        self.__core_agent_package_list: Optional[list[str]] = None
        self.__core_knowledge_package_list: Optional[list[str]] = None
        self.__core_llm_package_list: Optional[list[str]] = None
        self.__core_planner_package_list: Optional[list[str]] = None
        self.__core_tool_package_list: Optional[list[str]] = None
        self.__core_memory_package_list: Optional[list[str]] = None
        self.__core_service_package_list: Optional[list[str]] = None
        self.__core_sqldb_wrapper_package_list: Optional[list[str]] = None
        self.__core_prompt_package_list: Optional[list[str]] = None
        self.__core_product_package_list: Optional[list[str]] = None
        self.__core_workflow_package_list: Optional[list[str]] = None
        self.__core_embedding_package_list: Optional[list[str]] = None
        self.__core_doc_processor_package_list: Optional[list[str]] = None
        self.__core_reader_package_list: Optional[list[str]] = None
        self.__core_store_package_list: Optional[list[str]] = None
        self.__core_rag_router_package_list: Optional[list[str]] = None
        self.__core_query_paraphraser_package_list: Optional[list[str]] = None
        self.__core_memory_compressor_package_list: Optional[list[str]] = None
        self.__core_memory_storage_package_list: Optional[list[str]] = None
        self.__core_work_pattern_package_list: Optional[list[str]] = None
        self.__core_log_sink_package_list: Optional[list[str]] = None
        self.__core_llm_channel_package_list: Optional[list[str]] = None
        self.__conversation_memory_configer: Optional[dict] = {}
        self.__root_package_name: Optional[str] = None
        self.__yaml_func_instance = None
        self.__default_llm_configer: DefaultLLMConfiger = None
        self.__tool_configer_map: Dict[str, ToolConfiger] = {}
        self.__llm_configer_map: Dict[str, LLMConfiger] = {}
        self.__agent_llm_set: Optional[set[str]] = set()
        self.__agent_tool_set: Optional[set[str]] = set()
        self.__llm_plugins: Optional[Any] = set()

    @property
    def base_info_appname(self) -> Optional[str]:
        """Return the appname of the application."""
        return self.__base_info_appname

    @property
    def core_default_package_list(self) -> Optional[list[str]]:
        """Return the default package list of the core."""
        return self.__core_default_package_list

    @property
    def core_agent_package_list(self) -> Optional[list[str]]:
        """Return the agent package list of the core."""
        return self.__core_agent_package_list

    @property
    def core_knowledge_package_list(self) -> Optional[list[str]]:
        """Return the knowledge package list of the core."""
        return self.__core_knowledge_package_list

    @property
    def core_llm_package_list(self) -> Optional[list[str]]:
        """Return the llm package list of the core."""
        return self.__core_llm_package_list

    @property
    def core_planner_package_list(self) -> Optional[list[str]]:
        """Return the planner package list of the core."""
        return self.__core_planner_package_list

    @property
    def core_tool_package_list(self) -> Optional[list[str]]:
        """Return the tool package list of the core."""
        return self.__core_tool_package_list

    @property
    def core_memory_package_list(self) -> Optional[list[str]]:
        """Return the memory package list of the core."""
        return self.__core_memory_package_list

    @property
    def core_service_package_list(self) -> Optional[list[str]]:
        """Return the service package list of the core."""
        return self.__core_service_package_list

    @property
    def core_sqldb_wrapper_package_list(self) -> Optional[list[str]]:
        """Return the sql db wrapper package list of the core."""
        return self.__core_sqldb_wrapper_package_list

    @property
    def core_prompt_package_list(self) -> Optional[list[str]]:
        return self.__core_prompt_package_list

    @property
    def core_product_package_list(self) -> Optional[list[str]]:
        return self.__core_product_package_list

    @property
    def core_workflow_package_list(self) -> Optional[list[str]]:
        return self.__core_workflow_package_list

    @property
    def core_embedding_package_list(self) -> Optional[list[str]]:
        """Return the embedding package list of the core."""
        return self.__core_embedding_package_list

    @property
    def core_doc_processor_package_list(self) -> Optional[list[str]]:
        """Return the document processor package list of the core."""
        return self.__core_doc_processor_package_list

    @property
    def core_reader_package_list(self) -> Optional[list[str]]:
        """Return the reader package list of the core."""
        return self.__core_reader_package_list

    @property
    def core_store_package_list(self) -> Optional[list[str]]:
        """Return the store package list of the core."""
        return self.__core_store_package_list

    @property
    def core_rag_router_package_list(self) -> Optional[list[str]]:
        """Return the RAG router package list of the core."""
        return self.__core_rag_router_package_list

    @property
    def core_query_paraphraser_package_list(self) -> Optional[list[str]]:
        """Return the query paraphraser package list of the core."""
        return self.__core_query_paraphraser_package_list

    @property
    def core_memory_compressor_package_list(self) -> Optional[list[str]]:
        """Return the memory compressor package list of the core."""
        return self.__core_memory_compressor_package_list

    @property
    def core_memory_storage_package_list(self) -> Optional[list[str]]:
        """Return the memory storage package list of the core."""
        return self.__core_memory_storage_package_list

    @property
    def core_work_pattern_package_list(self) -> Optional[list[str]]:
        """Return the work pattern package list of the core."""
        return self.__core_work_pattern_package_list

    @property
    def core_log_sink_package_list(self) -> Optional[list[str]]:
        """Return the work pattern package list of the core."""
        return self.__core_log_sink_package_list

    @property
    def core_llm_channel_package_list(self) -> Optional[list[str]]:
        """Return the llm channel package list of the core."""
        return self.__core_llm_channel_package_list

    @property
    def conversation_memory_configer(self) -> dict:
        return self.__conversation_memory_configer

    @property
    def root_package_name(self) -> str:
        return self.__root_package_name

    @property
    def yaml_func_instance(self):
        return self.__yaml_func_instance

    @yaml_func_instance.setter
    def yaml_func_instance(self, value):
        self.__yaml_func_instance = value

    @property
    def default_llm_configer(self) -> DefaultLLMConfiger:
        return self.__default_llm_configer

    @default_llm_configer.setter
    def default_llm_configer(self, value: DefaultLLMConfiger):
        self.__default_llm_configer = value

    @property
    def tool_configer_map(self) -> Dict[str, ToolConfiger]:
        return self.__tool_configer_map

    @tool_configer_map.setter
    def tool_configer_map(self, value: Dict[str, ToolConfiger]):
        self.__tool_configer_map = value

    @property
    def llm_configer_map(self) -> Dict[str, LLMConfiger]:
        return self.__llm_configer_map

    @llm_configer_map.setter
    def llm_configer_map(self, value: Dict[str, LLMConfiger]):
        self.__llm_configer_map = value

    @property
    def agent_llm_set(self) -> set:
        return self.__agent_llm_set

    @agent_llm_set.setter
    def agent_llm_set(self, value: set):
        self.__agent_llm_set = value

    @property
    def agent_tool_set(self) -> set:
        return self.__agent_tool_set

    @agent_tool_set.setter
    def agent_tool_set(self, value: set):
        self.__agent_tool_set = value

    @property
    def llm_plugins(self):
        return self.__llm_plugins

    @classmethod
    def load_llm_plugins(cls, plugin_modules):
        funcs = []
        for item in plugin_modules:
            module_name, func_name = item.rsplit('.', 1)
            module = importlib.import_module(module_name)
            funcs.append(getattr(module, func_name))
        return funcs

    def load_by_configer(self, configer: Configer) -> 'AppConfiger':
        """Load the AppConfiger by the given Configer.

        Args:
            configer(Configer): the Configer object
        Returns:
            AppConfiger: the AppConfiger object
        """
        self.__configer = configer
        self.__base_info_appname = configer.value.get('BASE_INFO', {}).get('appname')
        self.__root_package_name = configer.value.get('PACKAGE_PATH_INFO', {}).get('ROOT_PACKAGE')
        self.__core_default_package_list = configer.value.get('CORE_PACKAGE', {}).get('default')
        self.__core_agent_package_list = configer.value.get('CORE_PACKAGE', {}).get('agent')
        self.__core_knowledge_package_list = configer.value.get('CORE_PACKAGE', {}).get('knowledge')
        self.__core_llm_package_list = configer.value.get('CORE_PACKAGE', {}).get('llm')
        self.__core_planner_package_list = configer.value.get('CORE_PACKAGE', {}).get('planner')
        self.__core_tool_package_list = configer.value.get('CORE_PACKAGE', {}).get('tool')
        self.__core_memory_package_list = configer.value.get('CORE_PACKAGE', {}).get('memory')
        self.__core_service_package_list = configer.value.get('CORE_PACKAGE', {}).get('service')
        self.__core_sqldb_wrapper_package_list = configer.value.get('CORE_PACKAGE', {}).get('sqldb_wrapper')
        self.__core_prompt_package_list = configer.value.get('CORE_PACKAGE', {}).get('prompt')
        self.__core_product_package_list = configer.value.get('CORE_PACKAGE', {}).get('product')
        self.__core_workflow_package_list = configer.value.get('CORE_PACKAGE', {}).get('workflow')
        self.__core_embedding_package_list = configer.value.get('CORE_PACKAGE', {}).get('embedding')
        self.__core_doc_processor_package_list = configer.value.get('CORE_PACKAGE', {}).get('doc_processor')
        self.__core_reader_package_list = configer.value.get('CORE_PACKAGE', {}).get('reader')
        self.__core_store_package_list = configer.value.get('CORE_PACKAGE', {}).get('store')
        self.__core_rag_router_package_list = configer.value.get('CORE_PACKAGE', {}).get('rag_router')
        self.__core_query_paraphraser_package_list = configer.value.get('CORE_PACKAGE', {}).get('query_paraphraser')
        self.__core_memory_compressor_package_list = configer.value.get('CORE_PACKAGE', {}).get('memory_compressor')
        self.__core_memory_storage_package_list = configer.value.get('CORE_PACKAGE', {}).get('memory_storage')
        self.__core_work_pattern_package_list = configer.value.get('CORE_PACKAGE', {}).get('work_pattern')
        self.__core_log_sink_package_list = configer.value.get('CORE_PACKAGE', {}).get('log_sink')
        self.__core_llm_channel_package_list = configer.value.get('CORE_PACKAGE', {}).get('llm_channel')
        self.__conversation_memory_configer = configer.value.get('CONVERSATION_MEMORY', {})
        self.__llm_plugins = self.load_llm_plugins(configer.value.get("PLUGINS", {}).get("llm_plugins", []))
        return self
