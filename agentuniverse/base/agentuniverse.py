# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 15:27
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: agentuniverse.py
import importlib
import sys
from pathlib import Path
from typing import List

from agentuniverse.agent_serve.web.mcp.mcp_server_manager import \
    MCPServerManager
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.application_component_manager import ApplicationComponentManager
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.config.config_type_enum import ConfigTypeEnum
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.custom_configer.default_llm_configer import DefaultLLMConfiger
from agentuniverse.base.config.custom_configer.custom_key_configer import CustomKeyConfiger
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.storage.config_storage import ConfigStorage
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.base.util.system_util import get_project_root_path, is_api_key_missing, \
    is_system_builtin, find_default_llm_config
from agentuniverse.base.util.logging.logging_util import init_loggers
from agentuniverse.agent_serve.web.request_task import RequestLibrary
from agentuniverse.agent_serve.web.rpc.grpc.grpc_server_booster import set_grpc_config
from agentuniverse.agent_serve.web.web_booster import ACTIVATE_OPTIONS
from agentuniverse.agent_serve.web.post_fork_queue import POST_FORK_QUEUE
from agentuniverse.agent_serve.web.web_util import FlaskServerManager
from agentuniverse.base.tracing.otel.telemetry_manager import TelemetryManager

@singleton
class AgentUniverse(object):
    """AgentUniverse framework object, responsible for the framework initialization,
       system variables management, etc."""

    def __init__(self):
        self.__application_container = ApplicationComponentManager()
        self.__config_container: ApplicationConfigManager = ApplicationConfigManager()
        self.__system_default_agent_package = ['agentuniverse.agent.default']
        self.__system_default_llm_package = ['agentuniverse.llm.default']
        self.__system_default_tool_package = ['agentuniverse.agent.action.tool']
        self.__system_default_toolkit_package = ['agentuniverse.agent.action.toolkit']
        self.__system_default_planner_package = ['agentuniverse.agent.plan.planner']
        self.__system_default_memory_package = ['agentuniverse.agent.memory.default']
        self.__system_default_prompt_package = ['agentuniverse.agent', 'agentuniverse.base.util']
        self.__system_default_embedding_package = ['agentuniverse.agent.action.knowledge.embedding']
        self.__system_default_doc_processor_package = ['agentuniverse.agent.action.knowledge.doc_processor']
        self.__system_default_reader_package = ['agentuniverse.agent.action.knowledge.reader.file']
        self.__system_default_rag_router_package = ['agentuniverse.agent.action.knowledge.rag_router']
        self.__system_default_query_paraphraser_package = ['agentuniverse.agent.action.knowledge.query_paraphraser']
        self.__system_default_memory_compressor_package = ['agentuniverse.agent.memory.memory_compressor']
        self.__system_default_memory_storage_package = ['agentuniverse.agent.memory.memory_storage']
        self.__system_default_work_pattern_package = ['agentuniverse.agent.work_pattern']
        self.__system_default_log_sink_package = ['agentuniverse.base.util.logging.log_sink.log_sink']

    def start(self, config_path: str = None, core_mode: bool = False):
        """Start the agentUniverse framework.

        """
        # get default config path
        project_root_path = get_project_root_path()
        sys.path.append(str(project_root_path.parent))
        self._add_to_sys_path(project_root_path, ['intelligence', 'app'])

        if not config_path:
            config_path = project_root_path / 'config' / 'config.toml'
            config_path = str(config_path)

        # load the configuration file
        configer = Configer(path=config_path).load()

        # try to load custom key first
        custom_key_configer_path = self.__parse_sub_config_path(
            configer.value.get('SUB_CONFIG_PATH', {}).get('custom_key_path'),
            config_path)
        CustomKeyConfiger(custom_key_configer_path)

        # then reload config
        configer = Configer(path=config_path).load()
        app_configer = AppConfiger().load_by_configer(configer)
        self.__config_container.app_configer = app_configer

        # init loguru loggers
        log_config_path = self.__parse_sub_config_path(
            configer.value.get('SUB_CONFIG_PATH', {}).get('log_config_path'),
            config_path)
        init_loggers(log_config_path)

        # Init OTEL configs
        TelemetryManager().init_from_config(configer.value.get('OTEL', {}))

        # init web request task database
        RequestLibrary(configer=configer)

        # Edit grpc config.
        grpc_activate = configer.value.get('GRPC', {}).get('activate')
        if grpc_activate and grpc_activate.lower() == 'true':
            ACTIVATE_OPTIONS["grpc"] = True
            set_grpc_config(configer)

        # Init gunicorn web server with config file.
        sync_service_timeout = configer.value.get('HTTP_SERVER', {}).get('sync_service_timeout')
        if sync_service_timeout:
            FlaskServerManager().sync_service_timeout = sync_service_timeout
        gunicorn_activate = configer.value.get('GUNICORN', {}).get('activate')
        if gunicorn_activate and gunicorn_activate.lower() == 'true':
            ACTIVATE_OPTIONS["gunicorn"] = True
            gunicorn_config_path = self.__parse_sub_config_path(
                configer.value.get('GUNICORN', {})
                .get('gunicorn_config_path'), config_path
            )
            from ..agent_serve.web.gunicorn_server import \
                GunicornApplication
            GunicornApplication(config_path=gunicorn_config_path)

        # init all extension module
        ext_classes = configer.value.get('EXTENSION_MODULES', {}).get('class_list')
        if isinstance(ext_classes, list):
            for ext_class in ext_classes:
                if "YamlFuncExtension" in ext_class:
                    self.__config_container.app_configer.yaml_func_instance = self.__dynamic_import_and_init(ext_class)
                else:
                    self.__dynamic_import_and_init(ext_class, configer)

        # init monitor module
        Monitor(configer=configer)
        # init config storage
        ConfigStorage(configer=configer)

        # scan and register the components
        self.__scan_and_register(self.__config_container.app_configer)
        if core_mode:
            for _func, args, kwargs in POST_FORK_QUEUE:
                _func(*args, **kwargs)

    def __scan_and_register(self, app_configer: AppConfiger):
        """Scan the component directory and register the components.

        Args:
            app_configer(AppConfiger): the AppConfiger object
        """
        core_agent_package_list = ((app_configer.core_agent_package_list or app_configer.core_default_package_list)
                                   + self.__system_default_agent_package)
        core_knowledge_package_list = app_configer.core_knowledge_package_list or app_configer.core_default_package_list
        core_llm_package_list = ((app_configer.core_llm_package_list or app_configer.core_default_package_list)
                                 + self.__system_default_llm_package)
        core_planner_package_list = ((app_configer.core_planner_package_list or app_configer.core_default_package_list)
                                     + self.__system_default_planner_package)
        core_tool_package_list = ((app_configer.core_tool_package_list or app_configer.core_default_package_list)
                                    + self.__system_default_tool_package)
        core_toolkit_package_list = ((app_configer.core_toolkit_package_list or app_configer.core_tool_package_list or app_configer.core_default_package_list)
                                  + self.__system_default_tool_package)
        core_service_package_list = app_configer.core_service_package_list or app_configer.core_default_package_list
        core_sqldb_wrapper_package_list = app_configer.core_sqldb_wrapper_package_list or app_configer.core_default_package_list
        core_memory_package_list = ((app_configer.core_memory_package_list or app_configer.core_default_package_list)
                                    + self.__system_default_memory_package)
        core_prompt_package_list = ((app_configer.core_prompt_package_list or app_configer.core_default_package_list)
                                    + self.__system_default_prompt_package)
        core_workflow_package_list = app_configer.core_workflow_package_list or app_configer.core_default_package_list
        core_embedding_package_list = ((app_configer.core_embedding_package_list or app_configer.core_default_package_list)
                                       + self.__system_default_embedding_package)
        core_doc_processor_package_list = ((app_configer.core_doc_processor_package_list or app_configer.core_default_package_list)
                                           + self.__system_default_doc_processor_package)
        core_reader_package_list = ((app_configer.core_reader_package_list or app_configer.core_default_package_list)
                                    + self.__system_default_reader_package)
        core_store_package_list = app_configer.core_store_package_list or app_configer.core_default_package_list
        core_rag_router_package_list = ((app_configer.core_rag_router_package_list or app_configer.core_default_package_list)
                                        + self.__system_default_rag_router_package)
        core_query_paraphraser_package_list = ((app_configer.core_query_paraphraser_package_list or app_configer.core_default_package_list)
                                               + self.__system_default_query_paraphraser_package)
        core_memory_compressor_package_list = ((app_configer.core_memory_compressor_package_list or app_configer.core_default_package_list)
                                               + self.__system_default_memory_compressor_package)
        core_memory_storage_package_list = ((app_configer.core_memory_storage_package_list or app_configer.core_default_package_list)
                                            + self.__system_default_memory_storage_package)
        core_work_pattern_package_list = ((app_configer.core_work_pattern_package_list or app_configer.core_default_package_list)
                                            + self.__system_default_work_pattern_package)
        core_log_sink_package_list = ((app_configer.core_log_sink_package_list or app_configer.core_default_package_list)
                                          + self.__system_default_log_sink_package)

        core_llm_channel_package_list = app_configer.core_llm_channel_package_list or app_configer.core_default_package_list


        component_package_map = {
            ComponentEnum.AGENT: core_agent_package_list,
            ComponentEnum.KNOWLEDGE: core_knowledge_package_list,
            ComponentEnum.LLM: core_llm_package_list,
            ComponentEnum.PLANNER: core_planner_package_list,
            ComponentEnum.TOOL: core_tool_package_list,
            ComponentEnum.TOOLKIT: core_toolkit_package_list,
            ComponentEnum.SERVICE: core_service_package_list,
            ComponentEnum.SQLDB_WRAPPER: core_sqldb_wrapper_package_list,
            ComponentEnum.MEMORY: core_memory_package_list,
            ComponentEnum.PROMPT: core_prompt_package_list,
            ComponentEnum.WORKFLOW: core_workflow_package_list,
            ComponentEnum.EMBEDDING: core_embedding_package_list,
            ComponentEnum.DOC_PROCESSOR: core_doc_processor_package_list,
            ComponentEnum.READER: core_reader_package_list,
            ComponentEnum.STORE: core_store_package_list,
            ComponentEnum.RAG_ROUTER: core_rag_router_package_list,
            ComponentEnum.QUERY_PARAPHRASER: core_query_paraphraser_package_list,
            ComponentEnum.MEMORY_COMPRESSOR: core_memory_compressor_package_list,
            ComponentEnum.MEMORY_STORAGE: core_memory_storage_package_list,
            ComponentEnum.WORK_PATTERN: core_work_pattern_package_list,
            ComponentEnum.LOG_SINK: core_log_sink_package_list,
            ComponentEnum.LLM_CHANNEL: core_llm_channel_package_list
        }

        component_configer_list_map = {}
        for component_enum, package_list in component_package_map.items():
            if not package_list:
                continue
            component_configer_list = self.scan(package_list, ConfigTypeEnum.YAML, component_enum)
            component_configer_list_map[component_enum] = component_configer_list

        for component_enum, component_configer_list in component_configer_list_map.items():
            self.__register(component_enum, component_configer_list)

    def scan(self,
             package_list: [str],
             config_type_enum: ConfigTypeEnum,
             component_enum: ComponentEnum) -> list:
        """Scan the component directory and return certain component configer list.

        Args:
            package_list(list): the package list
            config_type_enum(ConfigTypeEnum): the configuration file type enumeration
            component_enum(ComponentEnum): the component enumeration

        Returns:
            list: the component configer list
        """
        component_configer_list = []
        if component_enum.value == ComponentEnum.LLM.value:
            # Find the default LLM configuration file path from the provided package list
            default_llm_config_path = find_default_llm_config(package_list)
            if default_llm_config_path:
                # Create a DefaultLLMConfiger object using the found configuration path
                # This object will be responsible for managing the default LLM configuration
                default_llm_configer = DefaultLLMConfiger(default_llm_config_path)
                self.__config_container.app_configer.default_llm_configer = default_llm_configer
                # If a default LLM configuration exists and specifies a default LLM, add its name to the agent LLM set
                if default_llm_configer and default_llm_configer.default_llm:
                    self.__config_container.app_configer.agent_llm_set.add(default_llm_configer.default_llm)

        for package_name in package_list:
            package_path = self.__package_name_to_path(package_name)
            path = Path(package_path)
            config_files = path.rglob(f'*.{config_type_enum.value}')
            for config_file in config_files:
                config_file_str = str(config_file)
                configer = ConfigStorage().sync_configer(config_file_str, component_enum)
                component_configer = ComponentConfiger().load_by_configer(configer)
                component_config_type = component_configer.get_component_config_type()
                if component_config_type == component_enum.value:
                    component_configer_list.append(component_configer)
        return component_configer_list

    def __register(self, component_enum: ComponentEnum, component_configer_list: list[ComponentConfiger]):
        """Register the components.

        Args:
            component_enum(ComponentEnum): the component enumeration
            component_configer_list(list): the component configer list
        """
        component_manager_clz = ComponentConfigerUtil.get_component_manager_clz_by_type(component_enum)
        default_llm_configer: DefaultLLMConfiger = self.__config_container.app_configer.default_llm_configer
        yaml_func_instance = self.__config_container.app_configer.yaml_func_instance

        for component_configer in component_configer_list:
            configer_clz = ComponentConfigerUtil.get_component_config_clz_by_type(component_enum)
            configer_instance: ComponentConfiger = configer_clz().load_by_configer(component_configer.configer)
            configer_instance.yaml_func_instance = yaml_func_instance
            configer_instance.default_llm_configer = default_llm_configer
            if component_enum.value == ComponentEnum.AGENT.value:
                # Extract LLM names and tool names from the agent's profile and action attributes
                if (hasattr(configer_instance, 'profile') and configer_instance.profile
                        and isinstance(configer_instance.profile, dict)):
                    llm_model = configer_instance.profile.get('llm_model', {})
                    if isinstance(llm_model, dict):
                        llm_name = llm_model.get('name')
                        if llm_name and isinstance(llm_name, str):
                            self.__config_container.app_configer.agent_llm_set.add(llm_name)
                if (hasattr(configer_instance, 'action') and configer_instance.action
                        and isinstance(configer_instance.action, dict)):
                    tool_name_list = configer_instance.action.get('tool')
                    if tool_name_list and isinstance(tool_name_list, list):
                        self.__config_container.app_configer.agent_tool_set.update(tool_name_list)
                    toolkit_name_list = configer_instance.action.get('toolkit')
                    if toolkit_name_list and isinstance(toolkit_name_list, list):
                        self.__config_container.app_configer.agent_toolkit_set.update(
                            toolkit_name_list)
            elif component_enum.value == ComponentEnum.LLM.value:
                # Register LLM components only if llm names are already in the agent LLM set
                if hasattr(configer_instance, 'name') and configer_instance.name:
                    if configer_instance.name not in self.__config_container.app_configer.agent_llm_set:
                        self.__config_container.app_configer.llm_configer_map[
                            configer_instance.name] = configer_instance
                        continue
            elif component_enum.value == ComponentEnum.TOOL.value:
                # Register TOOL components only if tool names are already in the agent tool set
                if hasattr(configer_instance, 'name') and configer_instance.name:
                    if hasattr(configer_instance, 'as_mcp_tool'):
                        MCPServerManager().register_mcp_tool(configer_instance, component_enum.value)
                    if configer_instance.name not in self.__config_container.app_configer.agent_tool_set:
                        self.__config_container.app_configer.tool_configer_map[
                            configer_instance.name] = configer_instance
                        continue
            elif component_enum.value == ComponentEnum.TOOLKIT.value:
                # Register TOOL components only if tool names are already in the agent tool set
                if hasattr(configer_instance, 'name') and configer_instance.name:
                    if hasattr(configer_instance, 'as_mcp_tool'):
                        MCPServerManager().register_mcp_tool(configer_instance, component_enum.value)
                    if configer_instance.name not in self.__config_container.app_configer.agent_toolkit_set:
                        self.__config_container.app_configer.toolkit_configer_map[
                            configer_instance.name] = configer_instance
                        continue
            component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(configer_instance)
            component_instance: ComponentBase = component_clz().initialize_by_component_configer(configer_instance)
            if component_instance is None:
                continue
            component_instance.component_config_path = component_configer.configer.path
            component_manager_clz().register(component_instance.get_instance_code(), component_instance)

    def __package_name_to_path(self, package_name: str) -> str:
        """Convert the package name to the package path.

        Args:
            package_name(str): the package name

        Returns:
            str: the package path
        """
        # get the package spec
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            raise ImportError(f"Can not find {package_name}")
        # get the package path
        package_path = spec.submodule_search_locations[0] if spec.submodule_search_locations else spec.origin
        return package_path

    def __parse_sub_config_path(self, input_path: str,
                                reference_file_path: str) -> str | None:
        """Resolve a sub config file path according to main config file.

            Args:
                input_path(str): Absolute or relative path of sub config file.
                reference_file_path(str): Main config file path.
            Returns:
                str or None: A file path or none when no such file.
        """
        if not input_path:
            return None

        input_path_obj = Path(input_path)
        if input_path_obj.is_absolute():
            combined_path = input_path_obj
        else:
            reference_file_path_obj = Path(reference_file_path)
            combined_path = reference_file_path_obj.parent / input_path_obj

        return str(combined_path)

    def __dynamic_import_and_init(self, class_path: str, configer: Configer = None):
        """Resolve a sub config file path according to main config file.

            Args:
                class_path(str): Full class path like package_name.class_name.
                Auto read from config file.
        """

        module_path, _, class_name = class_path.rpartition('.')
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls(configer) if configer else cls()

    def _add_to_sys_path(self, root_path, sub_dirs):
        for sub_dir in sub_dirs:
            app_path = root_path / sub_dir
            if app_path.exists():
                sys.path.append(str(app_path))
